from collections import OrderedDict

def title(val):
    if type(val) == str:
        return val.title()
    return val

def capitalize(val):
    if type(val) == str:
        return val.capitalize()
    return val

def formatKey(key):
    if key == "mondaySalads":
        return "# of Monday Salads"
    elif key == "thursdaySalads":
        return "# of Thursday Salads"
    elif key == "weeklySoups":
        return "# of Weekly Soups"
    elif key == "weeklyHotplates":
        return "# of Weekly Hotplates"
    elif key == "saladNotes":
        return "Salad Notes"
    elif key == "generalNotes":
        return "General Notes"
    elif key == "hotplateNotes":
        return "Hotplate Notes"
    else:
        return key.title()

def formatValue(val, prettyPhone = False):
    try:
        int(val)
        if len(val) == 10 and prettyPhone == True:
            return "({}) {}-{}".format(val[0:3], val[3:6], val[6:10])
        else:
            return val
    except:
        if type(val) == str:
            return val.title()
        else:
            return val

def viewFormatValue(val):
    return formatValue(val, prettyPhone = True)

# def usd(value):
#     """Formats value as USD."""
#     return "${:,.2f}".format(value)

def removeExcess(string, keep = ""):
    excess= "'-/()!@#$%^&*<>.?\":;|+=_{}[]~"
    result = ""
    for c in keep:
        excess.replace(c, "")
    for c in string:
        if c not in excess:
            result += c
    return result.strip()

def sortDict(unsortedDict, dictType):
    """
    Credit goes to John La Rooy of stackoverflow:
    https://stackoverflow.com/questions/12031482/custom-sorting-python-dictionary
    returns a sorted dictionary
    """
    if dictType == "clientAttributes":
        clientAttributeOrder = ["id", "clientType", "name", "phone", "address", "hash", "mondaySalads", "thursdaySalads", "weeklySoups", "weeklyHotplates",
                                "allergies", "saladLikes", "saladDislikes", "saladLoves", "hotplateLikes", "hotplateDislikes", "hotplateLoves",
                                "generalNotes", "saladNotes", "generalNotes", "hotplateNotes"]
        return OrderedDict(sorted(unsortedDict.items(), key=lambda i:clientAttributeOrder.index(i[0])))
    elif dictType == "clientTypes":
        clientTypeOrder = ["Base", "Standing Order"]
        return OrderedDict(sorted(unsortedDict.items(), key=lambda i:clientTypeOrder.index(i[0])))

def invertDict(dictionary):
    result = {}
    for key in dictionary:
        for value in dictionary[key]:
            result[value] = key
    return result
