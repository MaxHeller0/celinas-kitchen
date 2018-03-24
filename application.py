from datetime import datetime, timedelta

from flask import Flask, redirect, render_template, request, session, url_for

from clients import Admin, BaseClient, delete_client, get_client, init_dict
from db_config import db
from formatting_helpers import (capitalize, css_class, format_bool,
                                format_date_time, format_key, format_value,
                                title, usd, view_format_value, merge_dicts)
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
@login_required
def recipe(name=None):
    dest_dict = {"view": "view_recipe.html", "edit": "edit_recipe.html"}
    destination = dest_dict[request.args.get('dest', default='view')]
    if request.method == "GET":
        name = request.args.get("name")
        if not name:
            return render_template("edit_recipe.html", recipe=None)
    else:
        name = request.form.get("name")
        source = request.form.get("source")
        if source == "edit_button":
            return redirect(url_for('recipe', name=name, dest="edit"))
        elif source == "save_button" and name:
            recipe = new_recipe(request)
        return redirect(url_for('recipe', name=name))

    recipe = Recipe.query.filter_by(name=name).first()
    if recipe:
        return render_template(destination, recipe=recipe)
    else:
        return redirect(url_for('index'))


@app.route("/new_client/", methods=["GET", "POST"])
@login_required
def new_client():
    """
    Renders client creation page
    pass in list of required attributes for the client type from the client_attributes dictionary
    """
    if request.method == "POST":
        client_type = request.form.get("client_type")
        return redirect(url_for("new_client", client_type=client_type))
    else:
        client_type = request.args.get("client_type", type=int)
    if client_type not in client_types.values():
        return redirect(url_for("index"))
    return render_template("new_client.html", client_type=client_type, attributes=client_attributes[client_type], css_class=css_class)


@app.route("/client/", methods=["GET", "POST"])
@login_required
def client(name=None):
    """
    Renders a page to edit or view client details
    pass in existing details so that users can build off of them
    """
    dest_dict = {"view": "view_client.html", "edit": "edit_client.html"}
    destination = dest_dict[request.args.get('dest', default='view')]
    if request.method == "GET":
        name = request.args.get('name')
    else:
        name = request.form.get("name")
        source = request.form.get("source")

        if destination == "edit_client.html" or source == "edit_button":
            return redirect(url_for('client', name=name, dest="edit"))
        elif source == "view_button":
            return redirect(url_for("client", name=name))
        elif source == "delete_button":
            # delete client's orders
            client_id = BaseClient.query.filter_by(name=name).first().id
            orders = Order.query.filter_by(client_id=client_id).all()
            for order in orders:
                order.delete()

            delete_client(name)
            return redirect(url_for("index"))
        else:
            if source == "new_client":
                client_type = int(request.form.get("client_type"))

            elif source == "edit_client":
                old_name = request.form.get("old_name")
                client_type = BaseClient.query.filter_by(
                    name=old_name).first().client_type

            # add client to db using appropriate function
            init_dict[client_type](request)
            return redirect(url_for("client", name=name))

    client_data = get_client(name)
    if client_data is None:
        return apology("Could not retrieve client with name {}".format(name))

    return render_template(destination, client_data=client_data, css_class=css_class)


@app.route("/salad_service_card/", methods=["GET", "POST"])
@login_required
def salad_service_card(name=None):
    if request.method == "POST":
        name = request.form.get("name")
        return redirect(url_for("salad_service_card", name=name))
    else:
        name = request.args.get("name")
        client_data = get_client(name)
        if client_data["client_type"] == 1:
            return render_template("salad_service_card.html", client_data=client_data)
        else:
            return redirect(url_for('index'))


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
            item = OrderItem.query.get(to_delete)
            order.subtotal -= item.price
            item.delete()
        else:
            paid = request.form.get("paid")
            if paid:
                order.paid = paid
                db.session.commit()

            dish_name = request.form.get("name")
            dish = Recipe.query.filter_by(name=dish_name).first()
            if dish:
                quantity = request.form.get("quantity")
                price = request.form.get("price")
                if not price:
                    price = dish.price
                item = OrderItem(order_id, quantity, dish.id, price)
                order.subtotal += item.price
                db.session.commit()
        return redirect(url_for('order', order_id=order.id))
    try:
        return render_template("order.html", id=order_id, order=merge_dicts(order.details(), order.items()))
    except:
        return redirect(url_for("index"))


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
    filter = request.args.get('filter', default='client')
    query = request.args.get(
        'query', default=request.form.get("query"))
    if request.method == "POST":
        filter = request.form.get("filter")
        time = request.form.get("time")
        payment = request.form.get("payment")
        return redirect(url_for('view_orders', filter=filter, query=query, time=time, payment=payment))

    def get_dropdown_data():
        dropdown_data = {"clients": [], "recipes": []}
        clients= BaseClient.query.order_by(BaseClient.name).all()
        recipes = Recipe.query.all()
        for client in clients:
            dropdown_data["clients"].append(client.name)
        for recipe in recipes:
            dropdown_data["recipes"].append(recipe.name)
        return dropdown_data

    orders = filter_orders(request)
    dropdown_data = get_dropdown_data()

    if filter == "client":
        formatted_orders = []
        for order in orders:
            formatted_orders.append(order.details())
    elif filter == "dish":
        formatted_orders = {'orders': [], 'total': orders['total']}
        for order in orders['orders']:
            formatted_orders['orders'].append(
                merge_dicts(order.details(), order.items()))

    return render_template("view_orders.html", orders=formatted_orders, query=query, filter=filter, dropdown_data=dropdown_data)


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
