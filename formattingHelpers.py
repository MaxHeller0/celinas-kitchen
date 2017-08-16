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
    if key == "mp":
        return "# of Monday Plates"
    elif key == "tp":
        return "# of Thursday Plates"
    elif key == "saladNotes":
        return "Salad Notes"
    elif key == "deliveryNotes":
        return "Delivery Notes"
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
        clientAttributeOrder = ["id", "clientType", "name", "phone", "address", "hash", "mp", "tp", "likes", "dislikes", "loves", "allergies", "deliveryNotes", "saladNotes"]
        return OrderedDict(sorted(unsortedDict.items(), key=lambda i:clientAttributeOrder.index(i[0])))
    elif dictType == "clientTypes":
        clientTypeOrder = ["Base", "Salad service"]
        return OrderedDict(sorted(unsortedDict.items(), key=lambda i:clientTypeOrder.index(i[0])))
        
def invertDict(dictionary):
    result = {}
    for key in dictionary:
        for value in dictionary[key]:
            result[value] = key
    return result