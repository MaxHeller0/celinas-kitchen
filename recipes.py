from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from formattingHelpers import forceNum, formatName

# prepare database object for connection
db = SQLAlchemy()


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    basePrice = db.Column(db.Float(precision=2))
    customPrice = db.Column(db.Float(precision=2))

    def __init__(self, request):
        self.name = formatName(request.form.get("name"))
        self.description = request.form.get("description")
        self.basePrice = forceNum(request.form.get("basePrice"), "float")
        self.customPrice = forceNum(request.form.get("customPrice"), "float")

    def __repr__(self):
        return "{name}: {description}".format(name=self.name, description=self.description)

    def update(self, request):
        self.__init__(request)
