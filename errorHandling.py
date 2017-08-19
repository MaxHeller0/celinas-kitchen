from databaseHelpers import BaseClient
from formattingHelpers import formatName, removeExcess
from hardcodedShit import clientAttributes


def clientInputCheck(request, source):
    name = formatName(request.form.get("name"))
    client = BaseClient.query.filter_by(name=name).first()

    # check if client already exists so details aren't overwritten from newClient
    if client and source == "newClient":
        return (True, ["Client already exists in database", ""])

    clientType = client.clientType
    # make sure client type was provided (client exists)
    if clientType is None:
        return (True, ["Client doesn't exist in database or retrieval failed", ''])
    try:
        # make sure the client has a name
        if name == '':
            message = ["All clients must have a name", '']
            raise ValueError

        # make sure the phone numyber in a 10 digit number
        phoneStr = request.form.get("phone")
        try:
            int(removeExcess(phoneStr))
        except:
            message = ["Phone number must be number", '']
            raise ValueError
        if len(removeExcess(phoneStr)) == 7:
            message = ["Must include area code for phone number", '']
            raise ValueError
        elif len(removeExcess(phoneStr)) != 10:
            message = ["Not a valid phone number", '']
            raise ValueError

        # TODO address checking

        # standing order client form checking
        if clientType == "1":
            for attribute in clientAttributes["1"][3:6]:
                if any(c in ".\'\"!@#$%^&*()_+" for c in request.form.get(attribute)):
                    return (True, [("you entered an invalid character for " + attribute), ''])
    except ValueError:
        return (True, message)
    except:
        # meta error checking
        return (True, ["Ironically enough there is an error in the error checking code", "for client operations"])
    return (False, None)
