import os

client_types = {"Base": 0, "Standing Order": 1}
client_attribute_order = ["id", "client_type", "name", "phone", "address",
                          "delivery", "hash", "weekly_money", "monday_salads",
                          "thursday_salads", "salad_dressings", "monday_hotplates",
                          "tuesday_hotplates", "thursday_hotplates", "allergies",
                          "dietary_preferences", "protein", "salad_dislikes",
                          "salad_loves", "hotplate_likes", "hotplate_dislikes",
                          "hotplate_loves", "general_notes", "salad_notes",
                          "hotplate_notes"]
client_type_order = ["Base", "Standing Order"]
client_attributes = {}
client_attributes[0] = ["name", "phone",
                        "address", "delivery", "allergies", "general_notes",
                        "dietary_preferences"]
client_attributes[1] = sorted(client_attributes[0]
                              + ["weekly_money", "monday_salads", "thursday_salads",
                                 "salad_dressings", "protein", "salad_dislikes",
                                 "salad_loves", "salad_notes", "hotplate_likes",
                                 "hotplate_dislikes", "hotplate_loves",
                                 "hotplate_notes", "monday_hotplates",
                                 "tuesday_hotplates", "thursday_hotplates"],
                              key=lambda x: client_attribute_order.index(x))
input_types = {
    "default_text": ["address", "monday_salads", "thursday_salads",
                    "monday_hotplates", "tuesday_hotplates", "thursday_hotplates"],
    "opinion_text": ["protein", "salad_dislikes", "salad_loves",
                    "hotplate_likes", "hotplate_dislikes", "hotplate_loves",
                    "allergies"],
    "note_text": ["general_notes", "salad_notes", "hotplate_notes"],
    "boolean": ["salad_dressings", "delivery"],
    "money": ["weekly_money"]
}
try:
    db_config = "mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(username=os.environ["RDS_USERNAME"],
                                                                                    password=os.environ["RDS_PASSWORD"],
                                                                                    server=os.environ["RDS_HOSTNAME"],
                                                                                    port=os.environ["RDS_PORT"],
                                                                                    db=os.environ["RDS_DB_NAME"])
except:
    db_config = "mysql+mysqldb://{username}:{password}@{server}:{port}/{db}".format(
        username="admin", password="jOKb7lRRps&smt1bPeW!$",
        server="celinas-kitchen-testing.czfoxvxyu3gn.us-east-2.rds.amazonaws.com",
        port="3306", db="ebdb")
