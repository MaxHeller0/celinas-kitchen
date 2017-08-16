from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *
from errorHandling import *
from databaseHelpers import *
from formattingHelpers import *

# configure application
application = Flask(__name__)
app = application

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
    return dict(clientTypes=clientTypes, clientNameList=getClientNames())

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
        return(redirect(url_for("index")))
    global clientType
    clientType = request.form.get("clientType")
    return render_template("newClient.html", clientType=clientType, attributes=clientAttributes[clientType], cssClass=cssClass)

@app.route("/client", methods=["GET", "POST"])
def client():
    """
    Renders a page to edit or view client details
    pass in existing details so that users can build off of them
    """
    if request.method == "GET":
        return(redirect(url_for("index")))
    source = request.form.get("source")
    name = removeExcess(request.form.get("name"), "-'")
    destination = str
    message = ''
    destination = "viewClient.html"

    if source == "viewButton":
        message = "Client details"
    elif source in ["newClient", "editClient"]:
        if source == "newClient":
            message = "Client added to the database"
            operation = "new"
            global clientType
        elif source == "editClient":
            message = "Client details updated"
            operation = "edit"
            clientType = getClientType(name)
        inputCheckResults = clientInputCheck(request, clientType)
        if inputCheckResults[0]:
            return apology(inputCheckResults[1][0], inputCheckResults[1][1])
        initDict[clientType](request)
    else:
        destination = "editClient.html"

    # refresh client data in case changes were made
    clientData = getClient(name)
    if clientData == None:
        return apology("Could not retrieve client with name {}".format(name), '')
    return render_template(destination, clientData=clientData, message=message, cssClass=cssClass)

if __name__ == "__main__":
    app.run()
