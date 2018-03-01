from flask import Flask, redirect, render_template, request, session, url_for

from clients import (adminCheck, deleteClient, getAdmin, getClient,
                     getClientNames, getClientType, initDict, newAdmin,
                     updateAdmin)
from dbconfig import db
from errorHandling import clientInputCheck
from formattingHelpers import (capitalize, cssClass, formatKey, formatName,
                               formatValue, title, usd, viewFormatValue, formatBool)
from hardcodedShit import (clientAttributes, clientTypes, dbConfig)
from helpers import apology, login_required, root_login_required
from recipes import deleteRecipe, getRecipe, getRecipeList, newRecipe, Recipe
from orders import Order, OrderItem

# configure application
application = Flask(__name__)
app = application

app.config["DEBUG"] = True

# configure database
app.config["SQLALCHEMY_DATABASE_URI"] = dbConfig
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# configure session
app.secret_key = "XL94IAlZqcRbt5BJF2J3mM4Gz8LaAi"
app.config["SESSION_TYPE"] = "filesystem"

# set up filters for use in displaying text
app.jinja_env.filters["title"] = title
app.jinja_env.filters["capitalize"] = capitalize
app.jinja_env.filters["formatValue"] = formatValue
app.jinja_env.filters["viewFormatValue"] = viewFormatValue
app.jinja_env.filters["formatKey"] = formatKey
app.jinja_env.filters["formatBool"] = formatBool
app.jinja_env.filters["usd"] = usd

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
    return dict(clientTypes=clientTypes, clientNameList=getClientNames(), recipes=getRecipeList())


@app.route("/")
def index():
    """
    Renders home page
    """
    return render_template("index.html")


@app.route("/recipe/", methods=["GET", "POST"])
@app.route("/recipe/<name>", methods=["GET"])
@login_required
def recipe(name=None):
    if request.method == "POST" or name:

        # accessed via post, get name from form
        if name is None:
            name = request.form.get("name")

        try:
            name = formatName(name)
            recipe = getRecipe(name)
            source = request.form.get("source")

            if request.method == "GET":
                return render_template("viewRecipe.html", recipe=recipe)

            elif source in ["newButton", "viewButton"]:
                if source == "newButton":
                    if name in [None, ""]:
                        # trying to create new recipe without a name
                        return apology("Recipes must have a name")
                    recipe = newRecipe(request)
                return redirect("/recipe/{name}".format(name=name))

            elif source == "deleteButton":
                deleteRecipe(name)
                return redirect(url_for("index"))

            else:
                # source must have been an edit button
                return render_template("editRecipe.html", recipe=recipe)

        except:
            return redirect(url_for("index"))
    else:
        return render_template("editRecipe.html", recipe=None)


@app.route("/newClient", methods=["GET", "POST"])
@login_required
def newClient():
    """
    Renders client creation page
    pass in list of required attributes for the client type from the clientAttributes dictionary
    """
    # block people from trying to GET newCLient
    if request.method == "GET":
        return redirect(url_for("index"))
    global clientType
    clientType = int(request.form.get("clientType"))
    if clientType in [None, ""]:
        return redirect("/")
    return render_template("newClient.html", clientType=clientType, attributes=clientAttributes[clientType], cssClass=cssClass)


@app.route("/client/", methods=["GET", "POST"])
@app.route("/client/<name>", methods=["GET"])
@login_required
def client(name=None):
    """
    Renders a page to edit or view client details
    pass in existing details so that users can build off of them
    """
    # check how the user got to the page
    if request.method == "GET":
        source = "GET"
    else:
        try:
            name = formatName(request.form.get("name"))
            assert len(name) > 0

        except:
            return apology('Client must have a name', '')
            # return redirect(url_for("index"))
        source = request.form.get("source")

    if source in ["viewButton", "GET"]:
        destination = "viewClient.html"
        message = "Client details"

    elif source in ["newClient", "editClient"]:
        destination = "viewClient.html"
        message = ''

        if source == "newClient":
            # get clientType defined earlier in /newClient
            global clientType
            message = "Client added to the database"

        elif source == "editClient":
            clientType = getClientType(name)
            message = "Client details updated"

        # check for errors
        inputCheckResults = clientInputCheck(request, clientType, source)
        if inputCheckResults[0]:
            return apology(inputCheckResults[1][0], inputCheckResults[1][1])

        # add client to db using appropriate function
        initDict[clientType](request)

    elif source == "deleteButton":
        deleteClient(name)
        return redirect(url_for("index"))

    else:
        # source must have been an edit button
        message = ''
        destination = "editClient.html"

    clientData = getClient(name)
    if clientData is None:
        return apology("Could not retrieve client with name {}".format(name), '')

    # return either editClient or viewClient passing in all the clients data
    return render_template(destination, clientData=clientData, message=message, cssClass=cssClass)


@app.route("/saladServiceCard/<name>", methods=["GET"])
def saladServiceCard(name=None):
    try:
        # attempt to get client
        clientData = getClient(name)

        # make sure they're a salad service client
        assert clientData["clientType"] == 1
    except:
        return redirect(url_for('index'))
    return render_template("saladServiceCard.html", clientData=clientData)

@app.route("/newOrder", methods=["GET"])
def newOrder():
    return render_template("newOrder.html")

@app.route("/order/", methods=["GET", "POST"])
@app.route("/order/<orderId>", methods=["GET", "POST"])
def order(orderId=None):
    if orderId:
        order = Order.query.filter_by(id=orderId).first()
    else:
        name = formatName(request.form.get("name"))
        try:
            order = Order(name)
        except: return redirect(url_for("newOrder"))
    if request.method == "POST":
        dishName = formatName(request.form.get("name"))
        dish = Recipe.query.filter_by(name=dishName).first()
        quantity = request.form.get("quantity")
        if dish:
            orderItem = OrderItem(orderId, quantity, dish.id, dish.basePrice)
        return redirect(url_for("order") + str(order.id))
    return render_template("order.html", id=orderId, orderDetails=order.list())

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    if request.method == "POST":

        if not request.form.get("name"):
            return apology("must provide name")

        elif not request.form.get("password"):
            return apology("must provide password")

        adminId = adminCheck(request)

        # ensure username exists and password is correct
        if adminId is None:
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["adminId"] = adminId

        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/change_pwd", methods=["GET", "POST"])
@login_required
def change_pwd():
    """Allows admins to change their passwords"""
    if request.method == "POST":

        if not request.form.get("password_old"):
            return apology("must enter old password")

        # make sure passwords match
        if not (request.form.get("password") and request.form.get("password") == request.form.get("password_retype")):
            return apology("must enter the same new password twice")

        admin = getAdmin(session["adminId"])

        try:
            updateAdmin(admin, request)
        except:
            return apology("old password invalid")

        logout()

        return redirect(url_for("login"))

    else:
        return render_template("change_pwd.html")


@app.route("/logout")
def logout():
    """Log user out."""

    session.clear()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
@root_login_required
def register():
    """Register user."""

    if request.method == "POST":

        if not request.form.get("name"):
            return apology("must provide name")

        # ensure passwords were entered and match
        elif not (request.form.get("password") and request.form.get("password") == request.form.get("password_retype")):
            return apology("must enter the same password twice")

        newAdmin(request)

        return redirect(url_for("index"))

    else:

        return render_template("register.html")


with app.app_context():
    db.init_app(app)
    db.create_all()

# run the program
if __name__ == "__main__":
    app.run()
