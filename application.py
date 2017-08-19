from flask import Flask, redirect, render_template, request, session, url_for

from clients import (adminCheck, db, getAdmin, getClient, getClientNames,
                     getClientType, initDict, newAdmin, updateAdmin)
from errorHandling import clientInputCheck
from formattingHelpers import (capitalize, cssClass, formatKey, formatName,
                               formatValue, title, usd, viewFormatValue)
from hardcodedShit import clientAttributes, clientTypes, dbConfig
from helpers import apology, login_required, root_login_required
from recipes import Recipe

# configure application
application = Flask(__name__)
app = application

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
    return dict(clientTypes=clientTypes, clientNameList=getClientNames(), recipes=Recipe.query.order_by(Recipe.name).all())


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
    if request.method == "POST" or name is not None:
        if name is None:
            name = request.form.get("name")
        try:
            name = formatName(name)
            if name in [None, ""]:
                return apology("Recipes must have a name")
            recipe = Recipe.query.filter_by(name=name).first()
            source = request.form.get("source")
            if source == "viewButton":
                destination = "viewRecipe.html"
            elif source == "newButton":
                destination = "viewRecipe.html"
                if recipe:
                    recipe.update(request)
                else:
                    recipe = Recipe(request)
                    db.session.add(recipe)
                db.session.commit()
            elif source == "editButton" or (source is None and name is not None and request.method == "POST"):
                destination = "editRecipe.html"
            return render_template(destination, recipe=recipe)
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
    if request.method == "GET":
        return redirect(url_for("index"))
    global clientType
    clientType = request.form.get("clientType")
    if not clientType:
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


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("name"):
            return apology("must provide name")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        adminId = adminCheck(request)

        # ensure username exists and password is correct
        if adminId is None:
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["adminId"] = adminId

        # redirect user to home page
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

        if not (request.form.get("password") and request.form.get("password") == request.form.get("password_retype")):
            return apology("must enter the same new password twice")

        # query database for admin
        admin = getAdmin(session["adminId"])

        # change password
        if not updateAdmin(admin, request):
            return apology("old password invalid")

        logout()

        # redirect user to login page
        return redirect(url_for("login"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_pwd.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
@root_login_required
def register():
    """Register user."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("name"):
            return apology("must provide name")

        # ensure passwords were entered and match
        elif not (request.form.get("password") and request.form.get("password") == request.form.get("password_retype")):
            return apology("must enter the same password twice")

        # insert the user into the database
        newAdmin(request)

        # redirect user to login page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


with app.app_context():
    db.init_app(app)
    db.create_all()

if __name__ == "__main__":
    app.run()
