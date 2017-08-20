from flask_sqlalchemy import SQLAlchemy

from dbconfig import db
from formattingHelpers import forceNum, formatName

# # prepare database object for connection
# db = SQLAlchemy()


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


def newRecipe(request):
    name = formatName(request.form.get("name"))
    recipe = getRecipe(name)
    if recipe:
        recipe.update(request)
    else:
        recipe = Recipe(request)
        db.session.add(recipe)
    db.session.commit()
    return recipe


def deleteRecipe(name):
    recipe = getRecipe(name)
    db.session.delete(recipe)
    db.session.commit()


def getRecipe(name):
    return Recipe.query.filter_by(name=name).first()


def getRecipeList():
    """Returns a list of recipe names from the database"""
    return Recipe.query.order_by(Recipe.name).all()
