import os

clientTypes = {"Base": 0, "Standing Order": 1}
clientAttributeOrder = ["id", "clientType", "name", "phone", "address", "delivery", "hash",
                        "mondaySalads", "thursdaySalads", "saladDressings", "mondayHotplates", "tuesdayHotplates", "thursdayHotplates",
                        "allergies", "dietaryPreferences", "protein", "saladDislikes", "saladLoves", "hotplateLikes", "hotplateDislikes", "hotplateLoves",
                        "generalNotes", "saladNotes", "generalNotes", "hotplateNotes"]
clientTypeOrder = ["Base", "Standing Order"]
clientAttributes = {}
clientAttributes[0] = ["name", "phone",
                       "address", "delivery", "allergies", "generalNotes", "dietaryPreferences"]
clientAttributes[1] = sorted(clientAttributes[0] + ["mondaySalads", "thursdaySalads", "saladDressings", "protein", "saladDislikes", "saladLoves", "saladNotes",
                                                    "hotplateLikes", "hotplateDislikes", "hotplateLoves", "hotplateNotes",
                                                    "mondayHotplates", "tuesdayHotplates", "thursdayHotplates"],
                             key=lambda x: clientAttributeOrder.index(x))
inputTypes = {
    "defaultText": ["name", "phone", "address", "mondaySalads", "thursdaySalads", "mondayHotplates", "tuesdayHotplates", "thursdayHotplates"],
    "opinionText": ["protein", "saladDislikes", "saladLoves", "hotplateLikes", "hotplateDislikes", "hotplateLoves", "allergies"],
    "noteText": ["generalNotes", "saladNotes", "hotplateNotes"],
    "boolean": ["saladDressings", "delivery"]
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
