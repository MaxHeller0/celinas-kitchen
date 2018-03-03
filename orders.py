import datetime

from sqlalchemy import text

from clients import BaseClient
from db_config import db
from formatting_helpers import format_date_time, usd
from recipes import Recipe


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    dish_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)

    def __init__(self, order_id, count, dish_id, price):
        self.order_id = order_id
        self.count = count
        self.dish_id = dish_id
        self.price = price
        db.session.add(self)
        db.session.commit()

    def list(self):
        dish = Recipe.query.get(self.dish_id)
        return [self.count, dish.name, usd(self.price),
                usd(self.price * self.count), self.id]

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True))

    def delete(self):
        order_items = OrderItem.query.filter_by(order_id=self.id).all()
        for item in order_items:
            db.session.delete(item)
        db.session.delete(self)
        db.session.commit()

    def __init__(self, name):
        self.client_id = BaseClient.query.filter_by(name=name).first().id
        self.date = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def list(self):
        orders = OrderItem.query.filter_by(order_id=self.id).all()
        t = [[], [], []]
        if len(orders) == 0:
            t[0].append("Add the first item below")
        else:
            t[0].append("Order Details: {}, {}".format(BaseClient.query.get(
                self.client_id).name, format_date_time(self.date)))
            total = 0
            for row in orders:
                t[1].append(row.list())
                total += row.count * row.price
            t[2].append(usd(total))
        return t

    def total(self):
        orders = OrderItem.query.filter_by(order_id=self.id).all()
        total = 0
        for row in orders:
            total += row.count * row.price
        return total
