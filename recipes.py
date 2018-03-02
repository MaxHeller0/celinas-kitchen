from flask_sqlalchemy import SQLAlchemy

from db_config import db
from formatting_helpers import force_num


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float(precision=2))

    def __init__(self, request):
        self.name = request.form.get("name")
        self.description = request.form.get("description")
        self.price = force_num(request.form.get("price"), "float")

    def __repr__(self):
        return "{name}: {description}".format(name=self.name, description=self.description)

    def update(self, request):
        self.__init__(request)


def new_recipe(request):
    name = request.form.get("name")
    recipe = get_recipe(name)
    if recipe:
        recipe.update(request)
    else:
        recipe = Recipe(request)
        db.session.add(recipe)
    db.session.commit()
    return recipe


def delete_recipe(name):
    recipe = get_recipe(name)
    db.session.delete(recipe)
    db.session.commit()


def get_recipe(name):
    return Recipe.query.filter_by(name=name).first()


def get_recipe_by_id(id):
    return Recipe.query.filter_by(id=id).first()


def get_recipe_list():
    """Returns a list of recipe names from the database"""
    return Recipe.query.order_by(Recipe.name).all()
