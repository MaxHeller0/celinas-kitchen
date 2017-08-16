from helpers import apology
from databaseHelpers import clientAttributes
from formattingHelpers import removeExcess

def clientInputCheck(request, clientType):
    # make sure client type was provided (client exists)
    if clientType == None:
        return (True, ["Client doesn't exist in database or retrieval failed", ''])
    try:
        # make sure the client has a name
        if request.form.get("name") == '':
            return (True, ["All clients must have a name", ''])

        # make sure the phone numyber in a 10 digit number
        phoneStr = request.form.get("phone")
        try:
            int(removeExcess(phoneStr))
        except:
            return (True, ["Phone number must be number", ''])
        if len(removeExcess(phoneStr)) == 7:
            return (True, ["Must include area code for phone number", ''])
        elif len(removeExcess(phoneStr)) != 10:
            return (True, ["Not a valid phone number", ''])

        #TODO address checking

        #salad service form checking
        if clientType == "1":
            if request.form.get("mondaySalads") != "" and request.form.get("thursdaySalads") != "":
                try:
                    int(request.form.get("mondaySalads"))
                    int(request.form.get("thursdaySalads"))
                except:
                    return (True, ["The number of monday salads or thursday salads is invalid", "they must be numbers"])
            for attribute in clientAttributes["1"][3:6]:
                if any(c in ".\'\"!@#$%^&*()_+" for c in request.form.get(attribute)):
                    return (True, [("you entered an invalid character for " + attribute), ''])
    except:
        # meta error checking
        return (True, ["Ironically enough there is an error in the error checking code", ("for client operations")])
    return (False, None) # there's no reason to return All clear but it doesn't anything
