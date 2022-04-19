import click
from flask.cli import with_appcontext
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from . import db


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=False, nullable=False)
    address = Column(String(100), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    def __repr__(self):
        return "<User {}\n,email={}\n>".format(self.name, self.email)

    @staticmethod
    def json_schema():
        """Returns the schema for User"""
        schema = {"type": "object", "required": ["name", "email", "password"]}
        props = schema["properties"] = {}
        props["name"] = {"description": "username", "type": "string"}
        props["email"] = {"description": "email", "type": "string"}
        props["password"] = {"description": "password", "type": "string"}
        return schema


class Recipeingredient(db.Model):
    __tablename__ = "recipeingredient"
    id = Column(Integer, ForeignKey("recipe.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredient.id"), primary_key=True)
    amount = Column(Integer)
    unit_id = Column(Integer, ForeignKey("unit.id"), primary_key=True)

    recipe_rel = relationship(
        "Recipe", backref=backref("recipeingredients", cascade="all, delete-orphan")
    )
    ingredient = relationship(
        "Ingredient", backref=backref("recipeingredients", cascade="all, delete-orphan")
    )
    unit = relationship(
        "Unit", backref=backref("recipeingredients", cascade="all, delete-orphan")
    )

    @staticmethod
    def json_schema():
        schema = {"type": "object", "required": ["name", "amount", "unit"]}
        props = schema["properties"] = {}
        props["name"] = {"description": "Ingredients ID", "type": "string"}
        props["amount"] = {"description": "Amount of ingredient", "type": "number"}
        props["unit"] = {"description": "Ingredients unit", "type": "string"}
        return schema


class Recipe(db.Model):
    __tablename__ = "recipe"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    name = Column(String(64), unique=True, nullable=False)
    difficulty = Column(String(20), nullable=True)
    description = Column(String(2000), nullable=False)

    user = relationship("User", backref=backref("user", cascade="all, delete-orphan"))

    @staticmethod
    def json_schema():
        schema = {"type": "object", "required": ["name", "description"]}
        props = schema["properties"] = {}
        props["name"] = {"description": "Name of the recipe", "type": "string"}
        props["description"] = {
            "description": "Description of the recipe",
            "type": "string",
        }
        return schema


class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    @staticmethod
    def json_schema():
        """Returns the schema for Ingredient"""
        schema = {"type": "object", "required": ["name"]}
        props = schema["properties"] = {}
        props["name"] = {"description": "Name of ingredient", "type": "string"}
        return schema


class Unit(db.Model):
    __tablename__ = "unit"
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)

    @staticmethod
    def json_schema():
        """Returns the schema for Unit"""
        schema = {"type": "object", "required": ["name"]}
        props = schema["properties"] = {}
        props["name"] = {"description": "unit of measurement", "type": "string"}
        return schema


@click.command("init-db")
@with_appcontext
def init_db_command():
    """
    Makes 'flask init-db' possible from command line. Initializes DB by
    creating the tables. Example from https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/models.py
    """
    db.create_all()


@click.command("testgen")
@with_appcontext
def generate_test_data():
    p = User(name="test", address="boboboaaa", email="boba", password="bob34")
    db.session.add(p)
    db.session.commit()
    p1 = User(name="user", address="boboboccc", email="bobc", password="bob21")
    db.session.add(p)
    db.session.commit()
    p2 = User(name="bobi", address="bobobobbbb", email="bobb", password="bob12")
    db.session.add(p)
    db.session.add(p1)
    db.session.add(p2)
    db.session.commit()
    print("bob")
