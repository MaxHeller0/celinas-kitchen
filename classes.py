from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import FetchedValue, text

from db_config import db
from formatting_helpers import (force_num, format_datetime, format_phone,
                                merge_dicts, sort_dict, to_dict, usd)
from hardcoded_shit import CLIENT_TYPES


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
        client = Client.query.filter_by(name=name).first()
        if client._catering:
            if client._catering.tax_exempt:
                self.tax_rate = 0
        self.date = datetime.now()
        client.orders.append(self)
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

        client = Client.query.filter_by(name=query).first()
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


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)
    general_notes = db.Column(db.Text)
    orders = db.relationship("Order", backref="client")
    _a_la_carte = db.relationship(
        "ALaCarteClient", backref="base", uselist=False, cascade="all, delete-orphan")
    _standing_order = db.relationship(
        "StandingOrderClient", backref="base", uselist=False, cascade="all, delete-orphan")
    _catering = db.relationship(
        "CateringClient", backref="base", uselist=False, cascade="all, delete-orphan")

    def __init__(self, request):
        self.name = request.form.get("name")
        self.general_notes = request.form.get("general_notes")

        client_types = request.form.getlist("client_types")
        for client_type in client_types:
            INIT_DICT[client_type](request=request, base=self)

    def get_sub_clients(self):
        sub_clients = [self._a_la_carte, self._standing_order, self._catering]
        return [sub for sub in sub_clients if sub is not None]

    def update(self, request):
        self.name = request.form.get("name")
        self.general_notes = request.form.get("general_notes")

        for sub_client in self.get_sub_clients():
            sub_client.update(request)

    def data_dict(self):
        client_data = to_dict(self)
        for sub_client in self.get_sub_clients():
            client_data = merge_dicts(client_data, to_dict(sub_client))
        return sort_dict(client_data, "CLIENT_ATTRIBUTES")


class ALaCarteClient(db.Model):
    __tablename__ = "a_la_carte"
    client_id = db.Column(db.Integer, db.ForeignKey(
        "clients.id"), primary_key=True)
    phone = db.Column(db.String(10))
    address = db.Column(db.Text)
    delivery = db.Column(db.Boolean, default=False)
    allergies = db.Column(db.Text)
    dietary_preferences = db.Column(db.Text)

    def __init__(self, request, base):
        self.base = base
        self.phone = format_phone(request.form.get("phone"))
        self.address = request.form.get("address")
        self.delivery = force_num(request.form.get("delivery"))
        self.allergies = request.form.get("allergies")
        self.dietary_preferences = request.form.get("dietary_preferences")

    def update(self, request):
        self.__init__(request, self.base)


class StandingOrderClient(db.Model):
    __tablename__ = "standing_order"
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), primary_key=True)
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

    def __init__(self, request, base):
        self.base = base
        self.phone = format_phone(request.form.get("phone"))
        self.address = request.form.get("address")
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
        self.__init__(request, self.base)


class CateringClient(db.Model):
    __tablename__ = "catering"
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), primary_key=True)
    address = db.Column(db.Text)
    delivery = db.Column(db.Boolean, default=False)
    tax_exempt = db.Column(db.Boolean, default=False)
    contact = db.Column(db.String(100))
    contact_phone = db.Column(db.String(10))
    contact_email = db.Column(db.Text)

    def __init__(self, request, base):
        self.base = base
        self.address = request.form.get("address")
        self.delivery = force_num(request.form.get("delivery"))
        self.tax_exempt = force_num(request.form.get("tax_exempt"))
        self.contact = request.form.get("contact")
        self.contact_phone = format_phone(request.form.get("contact_phone"))
        self.contact_email = request.form.get("contact_email")

    def update(self, request):
        self.__init__(request, self.base)


INIT_DICT = {"a_la_carte": ALaCarteClient, "catering": CateringClient,
             "standing_order": StandingOrderClient}
CLIENT_TYPES = sort_dict(CLIENT_TYPES, dict_name="CLIENT_TYPES")
