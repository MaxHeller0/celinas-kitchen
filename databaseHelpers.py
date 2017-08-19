from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import text

from formattingHelpers import forceNum, formatName, removeExcess, sortDict
from hardcodedShit import clientTypes, dbConfig

# prepare database object for connection
db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    hash = db.Column(db.String())

    def __init__(self, request):
        self.name = formatName(request.form.get("name"))
        self.hash = pwd_context.hash(request.form.get("password"))

    def update(self, request):
        self.hash = pwd_context.hash(request.form.get("password"))


def newAdmin(request):
    name = formatName(request.form.get("name"))
    admin = Admin.query.filter_by(name=name).first()
    if not admin:
        admin = Admin(request)
        db.session.add(admin)
        db.session.commit()


def adminCheck(request):
    name = formatName(request.form.get("name"))
    admin = Admin.query.filter_by(name=name).first()
    if admin is None or not pwd_context.verify(request.form.get("password"), admin.hash):
        return None
    return admin.id


def getAdmin(id):
    """
    Input: id number
    Returns: admin object or None
    """
    try:
        return Admin.query.get(id)
    except:
        return None


def updateAdmin(admin, request):
    if not pwd_context.verify(request.form.get("password_old"), admin.hash):
        return False
    admin.update(request)
    db.session.commit()
    return True


class BaseClient(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(10), unique=True)
    clientType = db.Column(db.Integer)
    address = db.Column(db.String())
    generalNotes = db.Column(db.String())
    allergies = db.Column(db.String())

    def __init__(self, request, clientType=0):
        self.name = formatName(request.form.get("name"))
        self.phone = removeExcess(request.form.get("phone"))
        self.address = request.form.get("address").lower()
        self.allergies = request.form.get("allergies").lower()
        self.generalNotes = request.form.get("generalNotes")
        self.clientType = clientType

    def update(self, request):
        self.__init__(request, self.clientType)

    def toDict(self):
        return dict((key, value) for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith('_'))


def baseClient(request, clientType=0):
    name = formatName(request.form.get("name"))
    client = BaseClient.query.filter_by(name=name).first()
    if client:
        client.update(request)
    else:
        client = BaseClient(request, clientType)
        db.session.add(client)
    db.session.commit()
    return client.id


class StandingOrderClient(db.Model):
    __tablename__ = "standingOrder"
    id = db.Column(db.Integer, primary_key=True)
    saladLikes = db.Column(db.String())
    saladDislikes = db.Column(db.String())
    saladLoves = db.Column(db.String())
    hotplateLikes = db.Column(db.String())
    hotplateDislikes = db.Column(db.String())
    hotplateLoves = db.Column(db.String())
    mondaySalads = db.Column(db.Integer)
    thursdaySalads = db.Column(db.Integer)
    weeklyHotplates = db.Column(db.Integer)
    weeklySoups = db.Column(db.Integer)
    saladNotes = db.Column(db.String())
    hotplateNotes = db.Column(db.String())

    def __init__(self, request, clientId):
        self.id = clientId
        self.saladLikes = request.form.get("saladLikes").lower()
        self.saladDislikes = request.form.get("saladDislikes").lower()
        self.saladLoves = request.form.get("saladLoves").lower()
        self.hotplateLikes = request.form.get("hotplateLikes").lower()
        self.hotplateDislikes = request.form.get("hotplateDislikes").lower()
        self.hotplateLoves = request.form.get("hotplateLoves").lower()
        self.mondaySalads = forceNum(request.form.get("mondaySalads"))
        self.thursdaySalads = forceNum(request.form.get("thursdaySalads"))
        self.weeklyHotplates = forceNum(request.form.get("weeklyHotplates"))
        self.weeklySoups = forceNum(request.form.get("weeklySoups"))
        self.saladNotes = request.form.get("saladNotes")
        self.hotplateNotes = request.form.get("hotplateNotes")

    def update(self, request):
        self.__init__(request, self.id)

    def toDict(self):
        return dict((key, value) for key, value in self.__dict__.items()
                    if not callable(value) and not key.startswith('_'))


def standingOrderClient(request):
    clientId = baseClient(request, 1)
    client = StandingOrderClient.query.get(clientId)
    if client:
        client.update(request)
    else:
        client = StandingOrderClient(request, clientId)
        db.session.add(client)
    db.session.commit()


def getClient(name):
    """
    Input: name
    Returns: associated client details as a sorted dictionary, or None if no client exists
    """
    tableNames = {"0": "clients", "1": "standingOrder"}
    try:
        name = formatName(name)
        t = text("SELECT * FROM clients WHERE name LIKE :name")
        client = db.engine.execute(t, name=name).fetchall()[0]
        if client["clientType"] != "0":
            table = tableNames[client["clientType"]]
            t = text(
                "SELECT * FROM {table} JOIN clients ON {table}.id = clients.id WHERE name LIKE :name".format(table=table))
            client = db.engine.execute(t, name=name).fetchall()[0]
        return sortDict(client, "clientAttributes")
    except:
        return None


def getClientNames():
    """Returns a list of client names from the database as a list of dicts of form {"name":name}"""
    return BaseClient.query.order_by(BaseClient.name).all()


def getClientId(name):
    """Returns a client's id given a name"""
    name = formatName(name)
    client = BaseClient.query.filter_by(name=name).first()
    if client:
        return client.id
    return None


def getClientType(name):
    """Returns a client's clientType given a name"""
    name = formatName(name)
    client = BaseClient.query.filter_by(name=name).first()
    if client:
        return client.clientType
    return None


initDict = {"0": baseClient, "1": standingOrderClient}
clientTypes = sortDict(clientTypes, dictName="clientTypes")
