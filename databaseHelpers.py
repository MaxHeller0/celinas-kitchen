from cs50 import SQL
from flask_sqlalchemy import SQLAlchemy

from formattingHelpers import forceNum, formatName, removeExcess, sortDict
from hardcodedShit import clientTypes, dbConfig, tableNames

# configure CS50 Library to use Amazon RDS MySQL Database for raw SQL capabilities
db = SQL(dbConfig)

# configure connection for ORM capabilities
db2 = SQLAlchemy()


class BaseClient(db2.Model):
    __tablename__ = "clients"
    id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(100), unique=True)
    phone = db2.Column(db2.String(10), unique=True)
    clientType = db2.Column(db2.Integer)
    address = db2.Column(db2.String())
    generalNotes = db2.Column(db2.String())
    allergies = db2.Column(db2.String())

    def __init__(self, request, clientType=0):
        self.name = formatName(request.form.get("name"))
        self.phone = removeExcess(request.form.get("phone"))
        self.address = request.form.get("address").lower()
        self.allergies = request.form.get("allergies").lower()
        self.generalNotes = request.form.get("generalNotes")
        self.clientType = clientType


def baseClient(request, clientType=0):
    name = formatName(request.form.get("name"))
    client = BaseClient.query.filter_by(name=name).first()
    if client:
        client.__init__(request, clientType)
    else:
        client = BaseClient(request, clientType)
        db2.session.add(client)
    db2.session.commit()
    return client.id


class StandingOrderClient(db2.Model):
    __tablename__ = "standingOrder"
    id = db2.Column(db2.Integer, primary_key=True)
    saladLikes = db2.Column(db2.String())
    saladDislikes = db2.Column(db2.String())
    saladLoves = db2.Column(db2.String())
    hotplateLikes = db2.Column(db2.String())
    hotplateDislikes = db2.Column(db2.String())
    hotplateLoves = db2.Column(db2.String())
    mondaySalads = db2.Column(db2.Integer)
    thursdaySalads = db2.Column(db2.Integer)
    weeklyHotplates = db2.Column(db2.Integer)
    weeklySoups = db2.Column(db2.Integer)
    saladNotes = db2.Column(db2.String())
    hotplateNotes = db2.Column(db2.String())

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


def standingOrderClient(request):
    clientId = baseClient(request, 1)
    client = StandingOrderClient.query.get(clientId)
    if client:
        client.update(request)
    else:
        client = StandingOrderClient(request, clientId)
        db2.session.add(client)
    db2.session.commit()


def getClient(name):
    """
    Input: name
    Returns: associated client details as a sorted dictionary, or None if no client exists
    """
    try:
        name = formatName(name)
        client = db.execute(
            "SELECT * FROM clients WHERE name LIKE :name", name=name)
        if client[0]["clientType"] != "0":
            table = tableNames[client[0]["clientType"]]
            client = db.execute(
                "SELECT * FROM {table} JOIN clients ON {table}.id = clients.id WHERE name LIKE :name".format(table=table), name=name)
        return sortDict(client[0], "clientAttributes")
    except:
        return None


def getClientNames():
    """Returns a list of client names from the database as a list of dicts of form {"name":name}"""
    # orm implementation if we want it
    # return BaseClient.query.order_by(BaseClient.name).all()
    return db.execute("SELECT name FROM clients")


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
