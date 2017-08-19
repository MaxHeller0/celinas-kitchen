from flask import Flask, redirect, render_template, request, url_for

from databaseHelpers import (db, getClient, getClientNames, getClientType,
                             initDict)
from errorHandling import clientInputCheck
from formattingHelpers import (capitalize, cssClass, formatKey, formatName,
                               formatValue, title, viewFormatValue)
from hardcodedShit import clientAttributes, clientTypes, dbConfig
from helpers import apology

# configure application
application = Flask(__name__)
app = application

app.config["SQLALCHEMY_DATABASE_URI"] = dbConfig
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# set up filters for use in displaying text
app.jinja_env.filters["title"] = title
app.jinja_env.filters["capitalize"] = capitalize
app.jinja_env.filters["formatValue"] = formatValue
app.jinja_env.filters["viewFormatValue"] = viewFormatValue
app.jinja_env.filters["formatKey"] = formatKey

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


@app.context_processor
def injectNavbarData():
    try:
        return dict(clientTypes=clientTypes, clientNameList=getClientNames())
    except:
        db.init_app(app)


@app.route("/")
def index():
    """
    Renders home page
    pass in clientTypes dictionary to enable radio buttons for client creation
    pass in clientNameList dictionary to enable datalist containing all clients
    """
    return render_template("index.html")


@app.route("/newClient", methods=["GET", "POST"])
def newClient():
    """
    Renders client creation page
    pass in list of required attributes for the client type from the clientAttributes dictionary
    """
    if request.method == "GET":
        return redirect(url_for("index"))
    global clientType
    clientType = request.form.get("clientType")
    if not clientType:
        return redirect("/")
    return render_template("newClient.html", clientType=clientType, attributes=clientAttributes[clientType], cssClass=cssClass)


@app.route("/client/", methods=["GET", "POST"])
@app.route("/client/<name>", methods=["GET"])
def client(name=None):
    """
    Renders a page to edit or view client details
    pass in existing details so that users can build off of them
    """
    if name is None:
        try:
            name = formatName(request.form.get("name"))
            assert len(name) > 0
        except:
            return redirect(url_for("index"))
        source = request.form.get("source")
    else:
        source = "GET"
    message = ''
    destination = "viewClient.html"

    if source in ["viewButton", "GET"]:
        message = "Client details"
    elif source in ["newClient", "editClient"]:
        if source == "newClient":
            message = "Client added to the database"
            global clientType
        elif source == "editClient":
            message = "Client details updated"
            clientType = getClientType(name)
        inputCheckResults = clientInputCheck(request, clientType, source)
        if inputCheckResults[0]:
            return apology(inputCheckResults[1][0], inputCheckResults[1][1])
        initDict[clientType](request)
    else:
        destination = "editClient.html"

    # refresh client data in case changes were made
    clientData = getClient(name)
    if clientData is None:
        return apology("Could not retrieve client with name {}".format(name), '')
    return render_template(destination, clientData=clientData, message=message, cssClass=cssClass)


if __name__ == "__main__":
    # initialize database
    db.init_app(app)
    app.run()
