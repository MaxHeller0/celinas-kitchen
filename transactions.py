from dbconfig import db
from formattingHelpers import usd


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clientId = db.Column(db.Integer, db.ForeignKey('client.id'))
    clientName = db.Column(db.Text, db.ForeignKey('client.name'))
    clientType = db.Column(db.Integer, nullable=False, index=True)
    amount = db.Column(db.Float(precision=2), nullable=False)
    paid = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        if self.paid:
            return "{client} paid {amount} on {date}".format(client=self.clientName, amount=usd(self.amount), date=self.paid)
        else:
            return "{client} must pay {amount}".format(client=self.clientName, amount=usd(self.amount))
