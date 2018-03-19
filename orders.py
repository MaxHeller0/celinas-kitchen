from datetime import datetime, timedelta

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

    def details(self):
        dish = Recipe.query.get(self.dish_id)
        return {'count': self.count, 'name': dish.name, 'unit_price': usd(self.price),
                'price': usd(self.price * self.count), 'id': self.id}

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime(timezone=True))

    def __init__(self, name):
        self.client_id = BaseClient.query.filter_by(name=name).first().id
        self.date = datetime.now()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        order_items = OrderItem.query.filter_by(order_id=self.id).all()
        for item in order_items:
            db.session.delete(item)
        db.session.delete(self)
        db.session.commit()

    def contains(self, dish_id):
        order_items = OrderItem.query.filter_by(order_id=self.id)
        matching_order_items = order_items.filter_by(dish_id=dish_id).all()
        total = 0
        for item in matching_order_items:
            total += item.count
        return total

    def details(self):
        items = OrderItem.query.filter_by(order_id=self.id).all()
        t = {}
        if len(items) == 0:
            t['description'] = "Add the first item below"
        else:
            t['description'] = "Order Details: {}, {}".format(BaseClient.query.get(
                self.client_id).name, format_date_time(self.date))
            t['name'] = BaseClient.query.get(self.client_id).name
            t['date'] = format_date_time(self.date)
            total = 0
            t['items'] = []
            for item in items:
                t['items'].append(item.details())
                total += item.count * item.price
            t['total'] = total
        return t

    def total(self):
        orders = OrderItem.query.filter_by(order_id=self.id).all()
        total = 0
        for row in orders:
            total += row.count * row.price
        return total

    def total_with_tax(self):
        return self.total() * 1.08


def filter_orders(request):
    filter_cat = request.args.get('filter', default="client")
    query = request.args.get('query', default="")
    time = request.args.get('time', default="all_time")
    now = datetime.now().date()
    time_dict = {"past_day": now, "past_week": now - timedelta(weeks=1),
                 "past_month": now - timedelta(weeks=4), "all_time": None}
    past_time = time_dict[time]

    orders = Order.query.order_by(Order.date.desc())
    if past_time:
        orders = orders.filter(Order.date > past_time)

    if filter_cat == "client":
        client = BaseClient.query.filter_by(name=query).first()
        if client:
            orders = orders.filter_by(client_id=client.id)
        return orders.all()
    elif filter_cat == "dish":
        if query:
            dish = Recipe.query.filter_by(name=query).first()
            if dish:
                filtered_orders = {'orders': [], 'total': 0}
                for order in orders:
                    num_dishes = order.contains(dish.id)
                    if num_dishes > 0:
                        filtered_orders['orders'].append(order)
                        filtered_orders['total'] += num_dishes
                return filtered_orders
        return {'orders': orders.all(), 'total': 0}
