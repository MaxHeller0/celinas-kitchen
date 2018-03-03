from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import text

from db_config import db
from formatting_helpers import force_num, remove_excess, sort_dict
from hardcoded_shit import client_types


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
    phone = db.Column(db.String(10))
    client_type = db.Column(db.Integer)
    address = db.Column(db.Text)
    delivery = db.Column(db.Boolean, default=False)
    allergies = db.Column(db.Text)
    general_notes = db.Column(db.Text)
    dietary_preferences = db.Column(db.Text)

    def __init__(self, request, client_type=0):
        self.name = request.form.get("name")
        self.phone = remove_excess(request.form.get("phone"))
        self.client_type = client_type
        self.address = request.form.get("address").lower()
        self.delivery = force_num(request.form.get("delivery"))
        self.allergies = request.form.get("allergies").lower()
        self.general_notes = request.form.get("general_notes")
        self.dietary_preferences = request.form.get("dietary_preferences")

    def update(self, request):
        self.__init__(request, self.client_type)

    def toDict(self):
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


class StandingOrderClient(db.Model):
    __tablename__ = "standing_order"
    id = db.Column(db.Integer, primary_key=True)
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
    client_id = base_client(request, 1)
    client = StandingOrderClient.query.get(client_id)
    if client:
        client.update(request)
    else:
        client = StandingOrderClient(request, client_id)
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
    table_names = {0: "clients", 1: "standing_order"}
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


init_dict = {0: base_client, 1: standing_order_client}
client_types = sort_dict(client_types, dict_name="client_types")
