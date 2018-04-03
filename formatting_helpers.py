import re
from collections import OrderedDict

from hardcoded_shit import (client_attribute_order, client_type_order,
                            input_types)


def title(val):
    if type(val) == str:
        return val.title()
    return val


def capitalize(val):
    if type(val) == str:
        return val.capitalize()
    return val


def format_key(key):
    format_dict = {"monday_salads": "# of Monday Salads",
                   "thursday_salads": "# of Thursday Salads",
                   "monday_hotplates": "# of Monday Hotplates",
                   "tuesday_hotplates": "# of Tuesday Hotplates",
                   "thursday_hotplates": "# of Thursday Hotplates"}
    if key in format_dict:
        return format_dict[key]
    else:
        # split underscored keys
        return " ".join(key.split("_")).title()


def format_value(val, pretty_phone=False):
    try:
        int(val)
        if len(val) == 10 and pretty_phone:
            return "({}) {}-{}".format(val[0:3], val[3:6], val[6:10])
        return val
    except:
        if type(val) == str:
            return val.title()
        return val


def format_bool(val):
    if val:
        return "Yes"
    else:
        return "No"


def view_format_value(val):
    return format_value(val, pretty_phone=True)


def usd(value):
    """Formats value as USD."""
    return "${:,.2f}".format(value)


def force_num(string, output="int"):
    """
    Input: string that ideally can be converted to a number
    Returns: converted number or 0 if conversion isn't possible
    """
    convert_dict = {"int": int, "float": float}
    try:
        return convert_dict[output](string)
    except:
        return 0


def format_datetime(datetime):
    t = str(datetime)
    return "{}/{}/{} at {}".format(t[5:7], t[8:10], t[0:4],t[11:16])


def format_phone(string):
    excess = " '-/()!@#$%^&*<>.?\":;|+=_{}[]~"
    result = ""
    for c in string:
        if c not in excess:
            result += c
    return result


def sort_dict(unsorted_dict, dict_name):
    """
    Credit goes to John La Rooy of stackoverflow:
    stackoverflow.com/questions/12031482/custom-sorting-python-dictionary
    returns a sorted dictionary
    """
    if dict_name == "client_attributes":
        return OrderedDict(sorted(unsorted_dict.items(),
                                  key=lambda i: client_attribute_order.index(i[0])))
    elif dict_name == "CLIENT_TYPES":
        return OrderedDict(sorted(unsorted_dict.items(),
                                  key=lambda i: client_type_order.index(i[0])))


def invert_dict(dictionary):
    result = {}
    for key in dictionary:
        for value in dictionary[key]:
            result[value] = key
    return result


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    Credit goes to Aaron Hall of stackoverflow:
    https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


css_class = invert_dict(input_types)
