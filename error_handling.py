from clients import BaseClient
from formatting_helpers import remove_excess
from hardcoded_shit import client_attributes


def client_input_check(request, client_type, source):
    name = request.form.get("name")
    client = BaseClient.query.filter_by(name=name).first()

    # check if client already exists so details aren't overwritten from new_client
    if client and source == "new_client":
        return (True, ["Client already exists in database", ""])

    # make sure client type was provided (client exists)
    if client_type is None:
        return (True, ["Client doesn't exist in database or retrieval failed", ''])
    try:
        # make sure the client has a name
        if name == '':
            message = ["All clients must have a name", '']
            raise ValueError

        # make sure that, if entered, the phone numyber in a 10 digit number
        phone_str = remove_excess(request.form.get("phone"))
        if phone_str:
            try:
                int(phone_str)
            except:
                message = ["Phone number must be number", '']
                raise ValueError
            if len(phone_str) == 7:
                message = ["Must include area code for phone number", '']
                raise ValueError
            elif len(phone_str) != 10:
                message = ["Not a valid phone number", '']
                raise ValueError

        # standing order client form checking
        # TODO BROKEN
        if client_type == 1:
            for attribute in client_attributes[1][3:6]:
                if any(c in ".\'\"!@#$%^&*()_+" for c in request.form.get(attribute)):
                    return (True, [("you entered an invalid character for " + attribute), ''])
    except ValueError:
        return (True, message)
    except:
        # meta error checking
        return (True, ["Ironically enough there is an error in the error checking code", "for client operations"])
    return (False, None)
