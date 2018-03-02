import datetime

from dbconfig import db
from formattingHelpers import usd, formatDateTime
from recipes import getRecipeById
from sqlalchemy import text
from clients import BaseClient


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

    def list(self):
        dish = getRecipeById(self.dishId)
        return [self.count, dish.name.title(), usd(self.price), usd(self.price * self.count), self.id]

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientId = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True))

    def delete(self):
        orderItems = OrderItem.query.filter_by(orderId=self.id).all()
        for item in orderItems:
            db.session.delete(item)
        db.session.delete(self)
        db.session.commit()

    def __init__(self, name):
        self.clientId = BaseClient.query.filter_by(name=name).first().id
        self.date = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def list(self):
        orders = OrderItem.query.filter_by(orderId=self.id).all()
        t = [[], [], []]
        if len(orders) == 0:
            t[0].append("Add the first item below")
        else:
            t[0].append("Order Details: {}, {}".format(BaseClient.query.get(self.clientId).name.title(), formatDateTime(self.date)))
            total = 0
            for row in orders:
                t[1].append(row.list())
                total += row.count * row.price
            t[2].append(usd(total))
        return t

    def total(self):
        orders = OrderItem.query.filter_by(orderId=self.id).all()
        total = 0
        for row in orders:
            total += row.count * row.price
        return total
