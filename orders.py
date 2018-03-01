import datetime

from dbconfig import db
from formattingHelpers import usd, formatName, formatDateTime
from recipes import getRecipeById
from sqlalchemy import text
from clients import getClientNameById, getClientId


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
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        dish = getRecipeById(self.dishId)
        return "{},{},{},{}".format(self.count, dish.name.title(), usd(self.price), usd(self.price * self.count))

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientId = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True))

    def __init__(self, name):
        self.clientId = getClientId(name)
        self.date = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def list(self):
        orders = OrderItem.query.filter_by(orderId=self.id).all()
        t = [[], [], []]
        if len(orders) == 0:
            t[0].append("Add the first item below")
        else:
            t[0].append("Order Details: {}, {}".format(getClientNameById(self.clientId).title(), formatDateTime(self.date)))
            total = 0
            for row in orders:
                t[1].append(str(row))
                total += row.count * row.price
            t[2].append(usd(total))
        return t

    def total(self):
        orders = OrderItem.query.filter_by(orderId=self.id).all()
        total = 0
        for row in orders:
            total += row.count * row.price
        return total
