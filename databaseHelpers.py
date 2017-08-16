from cs50 import SQL
import os

from formattingHelpers import sortDict, removeExcess, invertDict

# configure CS50 Library to use Amazon RDS MySQL Database
db = SQL("mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(username=os.environ["RDS_USERNAME"],
                                                                            password=os.environ["RDS_PASSWORD"],
                                                                            server=os.environ["RDS_HOSTNAME"],
                                                                            port=os.environ["RDS_PORT"],
                                                                            db=os.environ["RDS_DB_NAME"]))

def baseClient(request, clientType = 0):
    """
    Adds or edits base level client information
    Inputs: request from HTTP POST form, clientType (int) to save in database
    """
    name = removeExcess(request.form.get("name").lower(), "-'")
    phone = removeExcess(request.form.get("phone"))
    address = request.form.get("address").lower()
    deliveryNotes = request.form.get("deliveryNotes")
    if getClient(name):
        user_id = getClientId(request.form.get("name"))
        db.execute("UPDATE clients SET phone=:phone, address=:address, name=:name, deliveryNotes=:deliveryNotes WHERE id=:user_id",
                                        phone=phone, address=address, name=name, user_id=user_id, deliveryNotes=deliveryNotes)
    else:
        db.execute("INSERT INTO clients (phone, name, clientType, address, deliveryNotes) VALUES (:phone, :name, :clientType, :address, :deliveryNotes)",
                                        phone=phone, name=name, clientType=clientType, address=address, deliveryNotes=deliveryNotes)

def saladService(request):
    """
    Adds or edits salad service level client information
    Inputs: request from HTTP POST form
    """
    baseClient(request, 1)
    name = removeExcess(request.form.get("name").lower(), "-'")
    user_id = getClientId(name)
    likes, dislikes, allergies = request.form.get("likes").lower(), request.form.get("dislikes").lower(), request.form.get("allergies").lower()
    loves, mp, tp = request.form.get("loves").lower(), request.form.get("mp"), request.form.get("tp")
    saladNotes = request.form.get("saladNotes")
    if getClient(name):
        db.execute("UPDATE saladService SET likes=:likes, dislikes=:dislikes, allergies=:allergies, loves=:loves, mp=:mp, tp=:tp, saladNotes=:saladNotes WHERE id=:user_id",
                                        likes=likes, dislikes=dislikes, allergies=allergies, loves=loves, mp=mp, tp=tp, saladNotes=saladNotes, user_id=user_id)
    else:
        db.execute("INSERT INTO saladService (id, likes, dislikes, allergies, loves, mp, tp, saladNotes) VALUES (:user_id, :likes, :dislikes, :allergies, :loves, :mp, :tp, :saladNotes)",
                                        user_id=user_id, likes=likes, dislikes=dislikes, allergies=allergies, loves=loves, mp=mp, tp=tp, saladNotes=saladNotes)

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

initDict = {"0": baseClient, "1": saladService}
tableNames = {"0": "clients", "1": "saladService"}
clientTypes = sortDict({"Base": "0", "Salad service": "1"}, "clientTypes")
clientAttributes = {
                    "0": ["name", "phone", "address", "deliveryNotes"],
                    "1": ["name", "phone", "address", "mp", "tp", "likes", "dislikes", "loves", "allergies", "deliveryNotes", "saladNotes"]
                    }
inputTypes = {
            "defaultText": ["name", "phone", "address", "mp", "tp"],
            "opinionText": ["likes", "dislikes", "loves", "allergies"],
            "noteText": ["deliveryNotes", "saladNotes"]
            }
cssClass = invertDict(inputTypes)
