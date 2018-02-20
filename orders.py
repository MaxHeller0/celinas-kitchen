from dbconfig import db
from formattingHelpers import usd


class OrderItem(db.Model):
    __tablename__ = "orderItems"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderId = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    dishId= db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)

    def __init__(self):
        pass

    def __repr__(self):
        dish = getRecipeById(dishId)
        return "{} dishes of {} at a price of {}".format(count, dish.name, usd(price))

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientId = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime)

    def __init__(self):
        pass
