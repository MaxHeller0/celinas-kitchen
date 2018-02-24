from collections import OrderedDict

from hardcodedShit import clientAttributeOrder, clientTypeOrder, inputTypes


def title(val):
    if type(val) == str:
        return val.title()
    return val


def capitalize(val):
    if type(val) == str:
        return val.capitalize()
    return val


def formatKey(key):
    formatDict = {"mondaySalads": "# of Monday Salads", "thursdaySalads": "# of Thursday Salads",
                  "saladDressings": "Salad Dressings", "dietaryPreferences": "Dietary Preferences",
                  "mondayHotplates": "# of Monday Hotplates", "tuesdayHotplates": "# of Tuesday Hotplates",
                  "thursdayHotplates": "# of Thursday Hotplates", "saladNotes": "Salad Notes",
                  "generalNotes": "General Notes", "hotplateNotes": "Hotplate Notes",
                  "saladDislikes": "Salad Dislikes", "saladLoves": "Salad Loves",
                  "hotplateLikes": "Hotplate Likes", "hotplateDislikes": "Hotplate Dislikes", "hotplateLoves": "Hotplate Loves"}
    if key in formatDict:
        return formatDict[key]
    return key.title()


def formatValue(val, prettyPhone=False):
    try:
        int(val)
        if len(val) == 10 and prettyPhone:
            return "({}) {}-{}".format(val[0:3], val[3:6], val[6:10])
        return val
    except:
        if type(val) == str:
            return val.title()
        return val

def formatBool(val):
    if val:
        return "Yes"
    else:
        return "No"

def viewFormatValue(val):
    return formatValue(val, prettyPhone=True)


def usd(value):
    """Formats value as USD."""
    return "${:,.2f}".format(value)


def formatName(name):
    return removeExcess(name.lower(), "-'")


def forceNum(string, output="int"):
    """
    Input: string that ideally can be converted to a number
    Returns: converted number or 0 if conversion isn't possible
    """
    convertDict = {"int": int, "float": float}
    try:
        return convertDict[output](string)
    except:
        return 0


def removeExcess(string, keep=""):
    excess = "'-/()!@#$%^&*<>.?\":;|+=_{}[]~"
    result = ""
    for c in keep:
        excess.replace(c, "")
    for c in string:
        if c not in excess:
            result += c
    return result.strip()


def sortDict(unsortedDict, dictName):
    """
    Credit goes to John La Rooy of stackoverflow:
    https://stackoverflow.com/questions/12031482/custom-sorting-python-dictionary
    returns a sorted dictionary
    """
    if dictName == "clientAttributes":
        return OrderedDict(sorted(unsortedDict.items(), key=lambda i: clientAttributeOrder.index(i[0])))
    elif dictName == "clientTypes":
        return OrderedDict(sorted(unsortedDict.items(), key=lambda i: clientTypeOrder.index(i[0])))


def invertDict(dictionary):
    result = {}
    for key in dictionary:
        for value in dictionary[key]:
            result[value] = key
    return result


cssClass = invertDict(inputTypes)
