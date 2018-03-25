from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import FetchedValue, text

from db_config import db
from formatting_helpers import (force_num, format_datetime, format_phone,
                                sort_dict, usd)
from hardcoded_shit import client_types


class Dish(db.Model):
    __tablename__ = "dishes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float(precision=2))
    order_items = db.relationship("OrderItem", backref="dish")

    def __init__(self, request):
        self.name = request.form.get("name")
        self.description = request.form.get("description")
        self.price = force_num(request.form.get("price"), "float")

    def __repr__(self):
        return "{name}: {description}".format(name=self.name,
                                              description=self.description)

    def update(self, request):
        self.__init__(request)


def new_dish(request):
    name = request.form.get("name")
    old_name = request.form.get("old_name")

    dish = Dish.query.filter_by(name=old_name).first()
    if dish:
        dish.update(request)
    else:
        dish = Dish(request)
        db.session.add(dish)
    db.session.commit()
    return dish


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        "orders.id"), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey("dishes.id"), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float(precision=2), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False,
                      server_default=FetchedValue())

    def __init__(self, order_id, count, dish_id, unit_price):
        self.order_id = order_id
        self.count = count
        self.dish_id = dish_id
        self.unit_price = unit_price
        db.session.add(self)
        db.session.commit()


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey(
        "clients.id"), nullable=False)
    date = db.Column(db.DateTime(timezone=True))
    tax_rate = db.Column(db.Float, default=.08)
    subtotal = db.Column(db.Float(precision=2), default=0)
    tax = db.Column(db.Float(precision=2), server_default=FetchedValue())
    total = db.Column(db.Float(precision=2), server_default=FetchedValue())
    paid = db.Column(db.Float(precision=2), default=0)
    owed = db.Column(db.Float(precision=2), server_default=FetchedValue())
    order_items = db.relationship("OrderItem", backref="order")

    def __init__(self, name):
        client = BaseClient.query.filter_by(name=name).first()
        self.client_id = client.id
        if client.client_type == 2:
            if client.tax_exempt:
                self.tax_rate = 0
        self.date = datetime.now()
        db.session.add(self)
        db.session.commit()

    def contains(self, dish_id):
        order_items = OrderItem.query.filter_by(order_id=self.id)
        matching_order_items = order_items.filter_by(dish_id=dish_id).all()
        return sum(item.count for item in matching_order_items)


def filter_orders(request):
    filter = request.args.get('filter', default="client")
    query = request.args.get('query', default="")
    payment = request.args.get('payment', default="all")
    time = request.args.get('time', default="all_time")
    now = datetime.now().date()
    time_dict = {"past_day": now, "past_week": now - timedelta(weeks=1),
                 "past_month": now - timedelta(weeks=4), "all_time": 0}
    past_time = time_dict[time]

    if filter == "client":
        orders = Order.query.filter(Order.date > past_time).order_by(Order.date.desc())

        client = BaseClient.query.filter_by(name=query).first()
        if client:
            orders = orders.with_parent(client)

        if payment == "full":
            orders = orders.filter(Order.owed == 0)
        elif payment == "unpaid":
            orders = orders.filter(Order.owed != 0)

        return orders.all()
    elif filter == "dish":
        if query:
            dish = Dish.query.filter_by(name=query).first()
            if dish:
                items = OrderItem.query.join(OrderItem.order).filter(
                    Order.date > past_time).with_parent(dish).order_by(
                    Order.date.desc()).all()
                total = sum(item.count for item in items)
                return {'items': items, 'total': total}
        else:
            return None


class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    hash = db.Column(db.Text)

    def __init__(self, request):
        self.name = request.form.get("name")
        self.hash = pwd_context.hash(request.form.get("password"))

        # make sure admin with same name doesn't already exist
        if not Admin.query.filter_by(name=self.name).first():
            db.session.add(self)
            db.session.commit()

    def update(self, request):
        if not pwd_context.verify(request.form.get("password_old"), self.hash):
            return False
        self.hash = pwd_context.hash(request.form.get("password"))
        db.session.commit()
        return True

    def check(request):
        name = request.form.get("name")
        admin = Admin.query.filter_by(name=name).first()
        if admin is None or not pwd_context.verify(request.form.get("password"), admin.hash):
            return None
        return admin.id


class BaseClient(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    client_type = db.Column(db.Integer)
    general_notes = db.Column(db.Text)
    orders = db.relationship("Order", backref="client")

    def __init__(self, request, client_type=0):
        self.name = request.form.get("name")
        self.client_type = client_type
        self.general_notes = request.form.get("general_notes")

    def update(self, request):
        self.__init__(request, self.client_type)

    def to_dict(self):
        return dict((key, value) for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith('_'))


def base_client(request, client_type=0):
    if request.form.get("source") == "edit_client":
        name = request.form.get("old_name")
    else:
        name = request.form.get("name")
    client = BaseClient.query.filter_by(name=name).first()
    if client:
        client.update(request)
    else:
        client = BaseClient(request, client_type)
        db.session.add(client)
    db.session.commit()
    return client.id


class ALaCarteClient(db.Model):
    __tablename__ = "a_la_carte"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10))
    address = db.Column(db.Text)
    delivery = db.Column(db.Boolean, default=False)
    allergies = db.Column(db.Text)
    dietary_preferences = db.Column(db.Text)

    def __init__(self, request, client_id):
        self.id = client_id
        self.phone = format_phone(request.form.get("phone"))
        self.address = request.form.get("address").lower()
        self.delivery = force_num(request.form.get("delivery"))
        self.allergies = request.form.get("allergies").lower()
        self.dietary_preferences = request.form.get("dietary_preferences")

    def update(self, request):
        self.__init__(request, self.id)

    def to_dict(self):
        return dict((key, value) for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith('_'))


def a_la_carte_client(request):
    client_id = base_client(request, 1)
    client = ALaCarteClient.query.get(client_id)
    if client:
        client.update(request)
    else:
        client = ALaCarteClient(request, client_id)
        db.session.add(client)
    db.session.commit()


class StandingOrderClient(db.Model):
    __tablename__ = "standing_order"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10))
    address = db.Column(db.Text)
    delivery = db.Column(db.Boolean, default=False)
    allergies = db.Column(db.Text)
    dietary_preferences = db.Column(db.Text)
    protein = db.Column(db.Text)
    salad_dislikes = db.Column(db.Text)
    salad_loves = db.Column(db.Text)
    hotplate_likes = db.Column(db.Text)
    hotplate_dislikes = db.Column(db.Text)
    hotplate_loves = db.Column(db.Text)
    weekly_money = db.Column(db.Integer)
    monday_salads = db.Column(db.Integer)
    thursday_salads = db.Column(db.Integer)
    salad_dressings = db.Column(db.Boolean, default=False)
    monday_hotplates = db.Column(db.Integer)
    tuesday_hotplates = db.Column(db.Integer)
    thursday_hotplates = db.Column(db.Integer)
    salad_notes = db.Column(db.Text)
    hotplate_notes = db.Column(db.Text)

    def __init__(self, request, client_id):
        self.id = client_id
        self.phone = format_phone(request.form.get("phone"))
        self.address = request.form.get("address").lower()
        self.delivery = force_num(request.form.get("delivery"))
        self.allergies = request.form.get("allergies").lower()
        self.dietary_preferences = request.form.get("dietary_preferences")
        self.protein = request.form.get("protein").lower()
        self.salad_dislikes = request.form.get("salad_dislikes").lower()
        self.salad_loves = request.form.get("salad_loves").lower()
        self.salad_dressings = force_num(request.form.get("salad_dressings"))
        self.hotplate_likes = request.form.get("hotplate_likes").lower()
        self.hotplate_dislikes = request.form.get("hotplate_dislikes").lower()
        self.hotplate_loves = request.form.get("hotplate_loves").lower()
        self.weekly_money = force_num(request.form.get("weekly_money"))
        self.monday_salads = force_num(request.form.get("monday_salads"))
        self.thursday_salads = force_num(request.form.get("thursday_salads"))
        self.monday_hotplates = force_num(request.form.get("monday_hotplates"))
        self.tuesday_hotplates = force_num(
            request.form.get("tuesday_hotplates"))
        self.thursday_hotplates = force_num(
            request.form.get("thursday_hotplates"))
        self.salad_notes = request.form.get("salad_notes")
        self.hotplate_notes = request.form.get("hotplate_notes")

    def update(self, request):
        self.__init__(request, self.id)

    def toDict(self):
        return dict((key, value) for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith('_'))


def standing_order_client(request):
    client_id = base_client(request, 2)
    client = StandingOrderClient.query.get(client_id)
    if client:
        client.update(request)
    else:
        client = StandingOrderClient(request, client_id)
        db.session.add(client)
    db.session.commit()


class CateringClient(db.Model):
    __tablename__ = "catering"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.Text)
    delivery = db.Column(db.Boolean, default=False)
    tax_exempt = db.Column(db.Boolean, default=False)
    contact = db.Column(db.String(100))
    contact_phone = db.Column(db.String(10))
    contact_email = db.Column(db.Text)

    def __init__(self, request, client_id):
        self.id = client_id
        self.address = request.form.get("address").lower()
        self.delivery = force_num(request.form.get("delivery"))
        self.tax_exempt = force_num(request.form.get("tax_exempt"))
        self.contact = request.form.get("contact")
        self.contact_phone = format_phone(request.form.get("contact_phone"))
        self.contact_email = request.form.get("contact_email")

    def update(self, request):
        self.__init__(request, self.id)

    def to_dict(self):
        return dict((key, value) for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith('_'))


def catering_client(request):
    client_id = base_client(request, 3)
    client = CateringClient.query.get(client_id)
    if client:
        client.update(request)
    else:
        client = CateringClient(request, client_id)
        db.session.add(client)
    db.session.commit()


def delete_client(name):
    table_names = {0: "clients", 1: "standing_order"}
    client_id = BaseClient.query.filter_by(name=name).first().id
    client_type = BaseClient.query.get(client_id).client_type
    t = text("DELETE FROM clients WHERE id=:client_id")
    db.engine.execute(t, client_id=client_id)
    if client_type != 0:
        table = table_names[client_type]
        t = text("DELETE FROM {table} WHERE id=:client_id".format(table=table))
        db.engine.execute(t, client_id=client_id)
    db.session.commit()


def get_client(name):
    """
    Input: name
    Returns: associated client details as a sorted dictionary, or None
    """
    table_names = {0: "clients", 1: "a_la_carte",
                   2: "standing_order", 3: "catering"}
    try:
        t = text("SELECT * FROM clients WHERE name LIKE :name")
        client = db.engine.execute(t, name=name).first()
        if client["client_type"] != 0:
            table = table_names[client["client_type"]]
            t = text(
                "SELECT * FROM {table} JOIN clients ON {table}.id = clients.id WHERE name LIKE :name".format(table=table))
            client = db.engine.execute(t, name=name).first()
        return sort_dict(client, "client_attributes")
    except:
        return None


init_dict = {0: base_client, 1: a_la_carte_client,
             2: standing_order_client, 3: catering_client}
client_types = sort_dict(client_types, dict_name="client_types")
