from cs50 import SQL
import os
from application import db2

from formattingHelpers import sortDict, removeExcess, invertDict

# configure CS50 Library to use Amazon RDS MySQL Database
try:
    db = SQL("mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(username=os.environ["RDS_USERNAME"],
                                                                            password=os.environ["RDS_PASSWORD"],
                                                                            server=os.environ["RDS_HOSTNAME"],
                                                                            port=os.environ["RDS_PORT"],
                                                                            db=os.environ["RDS_DB_NAME"]))
except:
    db = SQL("mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(username="admin", password="y94D6NDeTColiQDZAEWp", server="aa13t6f8mueycaj.cy9bm4pmzdu7.us-east-1.rds.amazonaws.com", port="3306", db="ebdb"))

class BaseClient(db2.Model):
    __tablename__ = "clients"
    id = db2.Column(db2.Integer, primary_key=True)
    name = db2.Column(db2.String(100), unique=True)
    phone = db2.Column(db2.String(10), unique=True)
    clientType = db2.Column(db2.Integer)
    address = db2.Column(db2.String())
    generalNotes = db2.Column(db2.String())
    allergies = db2.Column(db2.String())

    def __init__(self, request, clientType = 0):
        self.name = removeExcess(request.form.get("name").lower(), "-'")
        self.phone = removeExcess(request.form.get("phone"))
        self.address = request.form.get("address").lower()
        self.allergies = request.form.get("allergies").lower()
        self.generalNotes = request.form.get("generalNotes")
        self.clientType = clientType

def baseClient(request, clientType = 0):
    name = removeExcess(request.form.get("name").lower(), "-'")
    if getClient(name):
        client = BaseClient.query.filter_by(name=name).first()
        client.__init__(request, clientType)
    else:
        client = BaseClient(request, clientType)
        db2.session.add(client)
    db2.session.commit()

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
        self.mondaySalads = request.form.get("mondaySalads")
        self.thursdaySalads = request.form.get("thursdaySalads")
        self.weeklyHotplates = request.form.get("weeklyHotplates")
        self.weeklySoups = request.form.get("weeklySoups")
        self.saladNotes = request.form.get("saladNotes")
        self.hotplateNotes = request.form.get("hotplateNotes")

def standingOrderClient(request):
    name = removeExcess(request.form.get("name").lower(), "-'")
    baseClient(request, 1)
    clientId = getClientId(name)
    if getClient(name):
        client = StandingOrderClient.query.get(clientId)
        client.__init__(request, clientId)
    else:
        client = StandingOrderClient(request, clientId)
        db2.session.add(client)
    db2.session.commit()

def getClient(name):
    """Takes a name and returns the associated client details as a sorted dictionary, or None if no client exists"""
    try:
        name = removeExcess(name.lower(), "-'")
        client = db.execute("SELECT * FROM clients WHERE name LIKE :name", name=name)
        if client[0]["clientType"] != "0":
            client = db.execute("SELECT * FROM {table} JOIN clients ON {table}.id = clients.id WHERE name LIKE :name".format(table=tableNames[client[0]["clientType"]]), name=name)
        return sortDict(client[0], "clientAttributes")
    except:
        return None

def getClientNames():
    """Returns a list of client names from the database as a list of dicts of form {"name":name}"""
    return db.execute("SELECT name FROM clients")

def getClientId(name):
    """Returns a client's id given a name"""
    try:
        return db.execute("SELECT id FROM clients WHERE name LIKE :name", name=name.lower())[0]["id"]
    except:
        return None

def getClientType(name):
    """Returns a client's clientType given a name"""
    try:
        return db.execute("SELECT clientType FROM clients WHERE name LIKE :name", name=name.lower())[0]["clientType"]
    except:
        return None

initDict = {"0": baseClient, "1": standingOrderClient}
tableNames = {"0": "clients", "1": "standingOrder"}
clientTypes = sortDict({"Base": "0", "Standing Order": "1"}, "clientTypes")
clientAttributes = {}
clientAttributes["0"] = ["name", "phone", "address", "allergies", "generalNotes"]
clientAttributes["1"] = clientAttributes["0"] + ["mondaySalads", "thursdaySalads", "saladLikes", "saladDislikes", "saladLoves", "saladNotes", "hotplateLikes", "hotplateDislikes", "hotplateLoves", "hotplateNotes", "weeklyHotplates", "weeklySoups"]
inputTypes = {
            "defaultText": ["name", "phone", "address", "mondaySalads", "thursdaySalads", "weeklyHotplates", "weeklySoups"],
            "opinionText": ["saladLikes", "saladDislikes", "saladLoves", "hotplateLikes", "hotplateDislikes", "hotplateLoves", "allergies"],
            "noteText": ["generalNotes", "saladNotes", "hotplateNotes"]
            }
cssClass = invertDict(inputTypes)
