import os

clientTypes = {"Base": "0", "Standing Order": "1"}
clientAttributeOrder = ["id", "clientType", "name", "phone", "address", "hash", "mondaySalads", "thursdaySalads", "weeklySoups", "weeklyHotplates",
                        "allergies", "saladLikes", "saladDislikes", "saladLoves", "hotplateLikes", "hotplateDislikes", "hotplateLoves",
                        "generalNotes", "saladNotes", "generalNotes", "hotplateNotes"]
clientTypeOrder = ["Base", "Standing Order"]
clientAttributes = {}
clientAttributes["0"] = ["name", "phone",
                         "address", "allergies", "generalNotes"]
clientAttributes["1"] = sorted(clientAttributes["0"] + ["mondaySalads", "thursdaySalads", "saladLikes", "saladDislikes", "saladLoves", "saladNotes",
                                                        "hotplateLikes", "hotplateDislikes", "hotplateLoves", "hotplateNotes", "weeklyHotplates", "weeklySoups"],
                               key=lambda x: clientAttributeOrder.index(x))
inputTypes = {
    "defaultText": ["name", "phone", "address", "mondaySalads", "thursdaySalads", "weeklyHotplates", "weeklySoups"],
    "opinionText": ["saladLikes", "saladDislikes", "saladLoves", "hotplateLikes", "hotplateDislikes", "hotplateLoves", "allergies"],
    "noteText": ["generalNotes", "saladNotes", "hotplateNotes"]
}
try:
    dbConfig = "mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(username=os.environ["RDS_USERNAME"],
                                                                                   password=os.environ["RDS_PASSWORD"],
                                                                                   server=os.environ["RDS_HOSTNAME"],
                                                                                   port=os.environ["RDS_PORT"],
                                                                                   db=os.environ["RDS_DB_NAME"])
except:
    dbConfig = "mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(
        username="admin", password="y94D6NDeTColiQDZAEWp", server="aa13t6f8mueycaj.cy9bm4pmzdu7.us-east-1.rds.amazonaws.com", port="3306", db="ebdb")
