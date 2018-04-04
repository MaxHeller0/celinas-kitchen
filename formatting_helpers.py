import re
from collections import OrderedDict

from hardcoded_shit import (CLIENT_ATTRIBUTE_ORDER, CLIENT_ATTRIBUTES,
                            CLIENT_TYPE_ORDER, INPUT_TYPES)


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


def view_format_phone(phone):
    if len(phone) == 10:
        return "({}) {}-{}".format(phone[0:3], phone[3:6], phone[6:10])
    else:
        return phone


def format_bool(val):
    if val:
        return "Yes"
    else:
        return "No"


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
    return "{}/{}/{} at {}".format(t[5:7], t[8:10], t[0:4], t[11:16])


def format_phone(string):
    excess = " '-/()!@#$%^&*<>.?\":;|+=_{}[]~"
    result = ""
    for c in string:
        if c not in excess:
            result += c
    return result


def to_dict(client_obj):
    return dict((key, value) for key, value in client_obj.__dict__.items()
                if not callable(value) and not key.startswith('_'))


def sort_dict(unsorted_dict, dict_name):
    """
    Credit goes to John La Rooy of stackoverflow:
    stackoverflow.com/questions/12031482/custom-sorting-python-dictionary
    returns a sorted dictionary
    """
    if dict_name == "CLIENT_ATTRIBUTES":
        return OrderedDict(sorted(unsorted_dict.items(),
                                  key=lambda i: CLIENT_ATTRIBUTE_ORDER.index(i[0])))
    elif dict_name == "CLIENT_TYPES":
        return OrderedDict(sorted(unsorted_dict.items(),
                                  key=lambda i: CLIENT_TYPE_ORDER.index(i[0])))


def invert_dict(dictionary):
    result = {}
    for key in dictionary:
        for value in dictionary[key]:
            result[value] = key
    return result


def smart_invert_dict(dictionary):
    """
    Handles non-unique values in a way that makes multiple html classes easy
    :param dictionary:
    :return dictionary:
    """
    result = {}
    for key in dictionary:
        for value in dictionary[key]:
            try:
                result[value] += " " + key
            except:
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


CSS_CLASS = invert_dict(INPUT_TYPES)
INVERTED_CLIENT_ATTRIBUTES = smart_invert_dict(CLIENT_ATTRIBUTES)
