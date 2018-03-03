from datetime import datetime, timedelta

from flask import Flask, redirect, render_template, request, session, url_for

from clients import Admin, BaseClient, delete_client, get_client, init_dict
from db_config import db
from error_handling import client_input_check
from formatting_helpers import (capitalize, css_class, format_bool,
                                format_date_time, format_key, format_value,
                                title, usd, view_format_value)
from hardcoded_shit import client_attributes, client_types, db_config
from helpers import apology, login_required, root_login_required
from orders import Order, OrderItem, filter_orders
from recipes import Recipe, new_recipe

# configure application
application = Flask(__name__)
app = application

app.config["DEBUG"] = True

# configure database
app.config["SQLALCHEMY_DATABASE_URI"] = db_config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# configure session
app.secret_key = "XL94IAlZqcRbt5BJF2J3mM4Gz8LaAi"
app.config["SESSION_TYPE"] = "filesystem"

# set up filters for use in displaying text
app.jinja_env.filters["title"] = title
app.jinja_env.filters["capitalize"] = capitalize
app.jinja_env.filters["format_value"] = format_value
app.jinja_env.filters["view_format_value"] = view_format_value
app.jinja_env.filters["format_key"] = format_key
app.jinja_env.filters["format_bool"] = format_bool
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
def inject_navbar_data():
    return dict(client_types=client_types,
                client_name_list=BaseClient.query.order_by(
                    BaseClient.name).all(),
                recipes=Recipe.query.order_by(Recipe.name).all())


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
        if name is None:
            name = request.form.get("name")

        try:
            recipe = Recipe.query.filter_by(name=name).first()
            source = request.form.get("source")

            if request.method == "GET":
                return render_template("view_recipe.html", recipe=recipe)

            elif source in ["save_button", "view_button"]:
                if source == "save_button":
                    if not name:
                        # trying to create new recipe without a name
                        return apology("Recipes must have a name")
                    recipe = new_recipe(request)
                return redirect("/recipe/{name}".format(name=name))

            elif source == "delete_button":
                Recipe.delete(name)
                return redirect(url_for("index"))

            else:
                # source must have been an edit button
                return render_template("edit_recipe.html", recipe=recipe)

        except:
            return redirect(url_for("index"))
    else:
        return render_template("edit_recipe.html", recipe=None)


@app.route("/new_client", methods=["GET", "POST"])
@login_required
def new_client():
    """
    Renders client creation page
    pass in list of required attributes for the client type from the client_attributes dictionary
    """
    # block people from trying to GET new_client
    if request.method == "GET":
        return redirect(url_for("index"))
    global client_type
    client_type = int(request.form.get("client_type"))
    if client_type in [None, ""]:
        return redirect("/")
    return render_template("new_client.html", client_type=client_type, attributes=client_attributes[client_type], css_class=css_class)


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
            name = request.form.get("name")
            assert len(name) > 0
        except:
            return apology('Client must have a name', '')
        source = request.form.get("source")

    if source in ["view_button", "GET"]:
        destination = "view_client.html"
        message = "Client details"

    elif source in ["new_client", "edit_client"]:
        destination = "view_client.html"
        message = ''

        if source == "new_client":
            # get client_type defined earlier in /new_client
            global client_type
            message = "Client added to the database"

        elif source == "edit_client":
            old_name = request.form.get("old_name")
            client_type = BaseClient.query.filter_by(
                name=old_name).first().client_type
            message = "Client details updated"

        # check for errors
        input_check_results = client_input_check(request, client_type, source)
        if input_check_results[0]:
            return apology(input_check_results[1][0], input_check_results[1][1])

        # add client to db using appropriate function
        init_dict[client_type](request)

    elif source == "delete_button":
        delete_client(name)
        return redirect(url_for("index"))

    else:
        # source must have been an edit button
        message = ''
        destination = "edit_client.html"

    client_data = get_client(name)
    if client_data is None:
        return apology("Could not retrieve client with name {}".format(name), '')

    # return either edit_client or view_client passing in all the clients data
    return render_template(destination, client_data=client_data, message=message, css_class=css_class)


@app.route("/salad_service_card/<name>", methods=["GET"])
@login_required
def salad_service_card(name=None):
    try:
        # attempt to get client
        client_data = get_client(name)

        # make sure they're a salad service client
        assert client_data["client_type"] == 1
    except:
        return redirect(url_for('index'))
    return render_template("salad_service_card.html", client_data=client_data)


@app.route("/new_order", methods=["GET"])
@login_required
def new_order():
    return render_template("new_order.html")


@app.route("/order/", methods=["GET", "POST"])
@app.route("/order/<order_id>", methods=["GET", "POST"])
@login_required
def order(order_id=None):
    if order_id:
        order = Order.query.get(order_id)
    else:
        try:
            name = request.form.get("name")
            order = Order(name)
        except:
            return redirect(url_for("new_order"))
    if request.method == "POST":
        to_delete = request.form.get("delete")
        if to_delete:
            OrderItem.query.get(to_delete).delete()
        else:
            dish_name = request.form.get("name")
            dish = Recipe.query.filter_by(name=dish_name).first()
            quantity = request.form.get("quantity")
            price = request.form.get("price")
            if dish:
                if not price:
                    price = dish.price
                order_item = OrderItem(order_id, quantity, dish.id, price)
        return redirect(url_for("order") + str(order.id))
    # try:
    return render_template("order.html", id=order_id, order_details=order.list())
# except:
    # return redirect(url_for("index"))


@app.route("/order/<order_id>/delete", methods=["GET"])
@login_required
def delete_order(order_id=None):
    if order_id:
        order = Order.query.get(order_id)
        order.delete()
        return redirect(url_for("view_orders"))
    return redirect(url_for("index"))


@app.route("/orders/", methods=["GET", "POST"])
@login_required
def view_orders():
    if request.method == "GET":
        orders = Order.query.order_by(Order.date.desc()).all()
    else:
        orders = filter_orders(request)

    formatted_orders = []
    for order in orders:
        client_name = BaseClient.query.get(order.client_id).name
        total = usd(order.total())
        date = format_date_time(order.date)
        order_id = order.id
        formatted_orders.append([date, client_name, total, order_id])

    return render_template("view_orders.html", orders=formatted_orders)


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

        admin_id = Admin.check(request)

        # ensure username exists and password is correct
        if admin_id is None:
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["admin_id"] = admin_id

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

        admin = Admin.query.get(session["admin_id"])

        if not admin.update(request):
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

        Admin(request)

        return redirect(url_for("index"))
    else:
        return render_template("register.html")


with app.app_context():
    db.init_app(app)
    db.create_all()

# run the program
if __name__ == "__main__":
    app.run()
