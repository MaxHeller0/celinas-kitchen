import datetime

from dbconfig import db
from formattingHelpers import usd
from recipes import getRecipeById
from sqlalchemy import text
from clients import getClientNameById


class OrderItem(db.Model):
    __tablename__ = "orderItems"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderId = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    dishId= db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)

    def __init__(self, orderId, count, dishId, price):
        self.orderId = orderId
        self.count = count
        self.dishId = dishId
        self.price = price

    def __repr__(self):
        dish = getRecipeById(self.dishId)
        return "{} dishes of {} at a price of {}".format(self.count, dish.name, usd(self.price))


def getOrderItems(orderId):
    t = text("SELECT * FROM orderItems WHERE orderId=:orderId")
    return db.engine.execute(t, orderId=orderId).all()


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientId = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime())

    def __init__(self, clientId):
        self.clientId = clientId
        self.date = datetime.datetime.utcnow()

    def __repr__(self):
        orders = getOrderItems(self.id)
        t = "{} placed the following orders on {} : \n ".format(getClientNameById(self.clientId), self.date)
        for row in orders:
            t += str(row) + "\n"
        return t
