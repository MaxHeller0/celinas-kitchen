from cs50 import SQL
import os

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

def baseClient(request, clientType = 0):
    """
    Adds or edits base level client information
    Inputs: request from HTTP POST form, clientType (int) to save in database
    """
    name = removeExcess(request.form.get("name").lower(), "-'")
    phone = removeExcess(request.form.get("phone"))
    address = request.form.get("address").lower()
    generalNotes = request.form.get("generalNotes")
    if getClient(name):
        user_id = getClientId(request.form.get("name"))
        db.execute("UPDATE clients SET phone=:phone, address=:address, name=:name, generalNotes=:generalNotes WHERE id=:user_id",
                                        phone=phone, address=address, name=name, user_id=user_id, generalNotes=generalNotes)
    else:
        db.execute("INSERT INTO clients (phone, name, clientType, address, generalNotes) VALUES (:phone, :name, :clientType, :address, :generalNotes)",
                                        phone=phone, name=name, clientType=clientType, address=address, generalNotes=generalNotes)

def standingOrder(request):
    """
    Adds or edits salad service level client information
    Inputs: request from HTTP POST form
    """
    baseClient(request, 1)
    name = removeExcess(request.form.get("name").lower(), "-'")
    user_id = getClientId(name)
    saladLikes, saladDislikes = request.form.get("saladLikes").lower(), request.form.get("saladDislikes").lower()
    saladLoves, mondaySalads, thursdaySalads = request.form.get("saladLoves").lower(), request.form.get("mondaySalads"), request.form.get("thursdaySalads")
    saladNotes = request.form.get("saladNotes")
    hotplateLikes, hotplateDislikes = request.form.get("hotplateLikes").lower(), request.form.get("hotplateDislikes").lower()
    hotplateLoves, weeklyHotplates, weeklySoups = request.form.get("hotplateLoves").lower(), request.form.get("weeklyHotplates"), request.form.get("weeklySoups")
    hotplateNotes = request.form.get("hotplateNotes")
    if getClient(name):
        db.execute("UPDATE standingOrder SET saladLikes=:saladLikes, saladDislikes=:saladDislikes, saladLoves=:saladLoves, mondaySalads=:mondaySalads, thursdaySalads=:thursdaySalads, saladNotes=:saladNotes, hotplateLikes=:hotplateLikes, hotplateDislikes=:hotplateDislikes, hotplateLoves=:hotplateLoves, hotplateNotes=:hotplateNotes, weeklyHotplates=:weeklyHotplates, weeklySoups=:weeklySoups WHERE id=:user_id",
                                                saladLikes=saladLikes, saladDislikes=saladDislikes, saladLoves=saladLoves, mondaySalads=mondaySalads, thursdaySalads=thursdaySalads, saladNotes=saladNotes, hotplateLikes=hotplateLikes, hotplateDislikes=hotplateDislikes, hotplateLoves=hotplateLoves, hotplateNotes=hotplateNotes, weeklyHotplates=weeklyHotplates, weeklySoups=weeklySoups, user_id=user_id)
    else:
        db.execute("INSERT INTO standingOrder (id, saladLikes, saladDislikes, saladLoves, mondaySalads, thursdaySalads, saladNotes, hotplateLikes, hotplateDislikes, hotplateLoves, hotplateNotes, weeklyHotplates, weeklySoups) VALUES (:user_id, :saladLikes, :saladDislikes, :saladLoves, :mondaySalads, :thursdaySalads, :saladNotes, :hotplateLikes, :hotplateDislikes, :hotplateLoves, :hotplateNotes, :weeklyHotplates, :weeklySoups)",
                                        user_id=user_id, saladLikes=saladLikes, saladDislikes=saladDislikes, saladLoves=saladLoves, mondaySalads=mondaySalads, thursdaySalads=thursdaySalads, saladNotes=saladNotes, hotplateLikes=hotplateLikes, hotplateDislikes=hotplateDislikes, hotplateLoves=hotplateLoves, hotplateNotes=hotplateNotes, weeklyHotplates=weeklyHotplates, weeklySoups=weeklySoups)

def getClient(name):
    """Takes a name and returns the associated client details as a sorted dictionary, or None if no client exists"""
    try:
        name = removeExcess(name.lower())
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

initDict = {"0": baseClient, "1": standingOrder}
tableNames = {"0": "clients", "1": "standingOrder"}
clientTypes = sortDict({"Base": "0", "Standing Order": "1"}, "clientTypes")
clientAttributes = {
                    "0": ["name", "phone", "address", "generalNotes"],
                    "1": ["name", "phone", "address", "mondaySalads", "thursdaySalads", "saladLikes", "saladDislikes", "saladLoves", "generalNotes", "saladNotes", "hotplateLikes", "hotplateDislikes", "hotplateLoves", "hotplateNotes", "weeklyHotplates", "weeklySoups"]
                    }
inputTypes = {
            "defaultText": ["name", "phone", "address", "mondaySalads", "thursdaySalads", "weeklyHotplates", "weeklySoups"],
            "opinionText": ["saladLikes", "saladDislikes", "saladLoves", "hotplateLikes", "hotplateDislikes", "hotplateLoves", "allergies"],
            "noteText": ["generalNotes", "saladNotes", "hotplateNotes"]
            }
cssClass = invertDict(inputTypes)
