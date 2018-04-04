from datetime import datetime, timedelta

from flask import Flask, redirect, render_template, request, session, url_for

from classes import (Admin, Client, Dish, Order, OrderItem, filter_orders,
                     new_dish)
from db_config import db
from formatting_helpers import (capitalize, CSS_CLASS, format_bool,
                                format_datetime, format_key,
                                INVERTED_CLIENT_ATTRIBUTES, sort_dict, title,
                                usd, view_format_phone)
from hardcoded_shit import (CLIENT_ATTRIBUTE_ORDER, CLIENT_ATTRIBUTES,
                            CLIENT_TYPES, db_config)
from helpers import apology, login_required, root_login_required

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
app.jinja_env.filters["format_phone"] = view_format_phone
app.jinja_env.filters["format_key"] = format_key
app.jinja_env.filters["format_bool"] = format_bool
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["format_datetime"] = format_datetime

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
    return dict(CLIENT_TYPES=CLIENT_TYPES, CLIENT_NAMES=CLIENT_NAMES,
                DISH_NAMES=DISH_NAMES)


@app.errorhandler(404)
def page_not_found(e):
    return apology("404: Page Not Found"), 404


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new_client/", methods=["GET", "POST"])
@login_required
def new_client():
    name = request.args.get("name", default=request.form.get("name"))
    if request.method == "POST":
        return redirect(url_for("new_client", name=name))
    else:
        return render_template("new_client.html",
                               INVERTED_CLIENT_ATTRIBUTES=INVERTED_CLIENT_ATTRIBUTES,
                               attributes=CLIENT_ATTRIBUTE_ORDER,
                               CSS_CLASS=CSS_CLASS, name=name)


@app.route("/client/", methods=["GET", "POST"])
@login_required
def client(name=None):
    dest_dict = {"view": "view_client.html", "edit": "edit_client.html"}
    destination = dest_dict[request.args.get('dest', default='view')]
    name = request.form.get("name", default=request.args.get("name"))

    if request.method == "POST":
        source = request.form.get("source")

        if destination == "edit_client.html" or source == "edit_button":
            return redirect(url_for('client', name=name, dest="edit"))
        elif source == "view_button":
            return redirect(url_for("client", name=name))
        elif source == "delete_button":
            db.session.delete(Client.query.filter_by(name=name).first())
            db.session.commit()
            CLIENT_NAMES.remove(name)
            return redirect(url_for("index"))
        elif source == "new_client":
            CLIENT_NAMES.append(name)
            CLIENT_NAMES.sort()
            client = Client(request)
            db.session.add(client)
            db.session.commit()
            return redirect(url_for("client", name=name))
        elif source == "edit_client":
            old_name = request.form.get("old_name")
            Client.query.filter_by(name=old_name).first().update(request)
            db.session.commit()
            CLIENT_NAMES.remove(old_name)
            CLIENT_NAMES.append(name)
            CLIENT_NAMES.sort()
            return redirect(url_for("client", name=name))

    client = Client.query.filter_by(name=name).first()

    if not client:
        return apology("Could not retrieve client with name {}".format(name))
    else:
        return render_template(destination, client_data=client.data_dict(), CSS_CLASS=CSS_CLASS)


@app.route("/salad_service_card/", methods=["GET", "POST"])
@login_required
def salad_service_card(name=None):
    # TODO Fix
    if request.method == "POST":
        name = request.form.get("name")
        return redirect(url_for("salad_service_card", name=name))
    else:
        name = request.args.get("name")
        client_data = get_client(name)
        if client_data["client_type"] == 2:
            return render_template("salad_service_card.html", client_data=client_data)
        else:
            return redirect(url_for('index'))


@app.route("/dish/", methods=["GET", "POST"])
@login_required
def dish(name=None):
    dest_dict = {"view": "view_dish.html", "edit": "edit_dish.html"}
    destination = dest_dict[request.args.get('dest', default='view')]
    name = request.args.get("name", default=request.form.get("name"))

    if request.method == "POST":
        source = request.form.get("source")

        if source in ["new_button", "edit_button"]:
            return redirect(url_for('dish', name=name, dest="edit"))
        elif source == "save_button":
            dish = new_dish(request)
            old_name = request.form.get("old_name")
            if old_name:
                DISH_NAMES.remove(old_name)
            DISH_NAMES.append(name)
            DISH_NAMES.sort()
        return redirect(url_for('dish', name=name))
    else:
        dish = Dish.query.filter_by(name=name).first()
        if dish:
            return render_template(destination, dish=dish, name=name)
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
            db.session.delete(item)
            db.session.commit()
        else:
            paid = request.form.get("paid")
            if paid:
                order.paid = paid
                db.session.commit()

            dish_name = request.form.get("name")
            dish = Dish.query.filter_by(name=dish_name).first()
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
        return render_template("order.html", id=order_id, order=order, items=order.order_items)
    except:
        return redirect(url_for("index"))


@app.route("/order/<order_id>/delete", methods=["GET"])
@login_required
def delete_order(order_id=None):
    if order_id:
        db.session.delete(Order.query.get(order_id))
        db.session.commit()
        return redirect(url_for("view_orders"))
    return redirect(url_for("index"))


@app.route("/orders/", methods=["GET", "POST"])
@login_required
def view_orders():
    filter = request.args.get('filter', default='client')
    query = request.args.get('query', default=request.form.get("query"))
    if request.method == "POST":
        filter = request.form.get("filter")
        time = request.form.get("time", default="past_week")
        payment = request.form.get("payment")
        return redirect(url_for('view_orders', filter=filter, query=query, time=time, payment=payment))

    filter_results = filter_orders(request)

    return render_template("view_orders.html", filter_results=filter_results, query=query, filter=filter)


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

    CLIENT_NAMES, DISH_NAMES = [], []
    clients = Client.query.order_by(Client.name).all()
    dishes = Dish.query.order_by(Dish.name).all()
    for client in clients:
        CLIENT_NAMES.append(client.name)
    for dish in dishes:
        DISH_NAMES.append(dish.name)

# run the program
if __name__ == "__main__":
    app.run()
    db.create_all()
