from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from . import db

class Recipeingredient(db.Model):
    __tablename__ = 'recipeingredient'
    id = Column(Integer, ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredient.id'), primary_key=True)
    amount = Column(Integer)
    unit_id = Column(Integer, ForeignKey('unit.id'), primary_key=True)

    recipe_rel = relationship("Recipe", backref=backref("recipeingredients", cascade="all, delete-orphan" ))
    ingredient = relationship("Ingredient", backref=backref("recipeingredients", cascade="all, delete-orphan" ))
    unit = relationship("Unit", backref=backref("recipeingredients", cascade="all, delete-orphan" ))

class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    name = Column(String(64), unique=True, nullable=False)
    difficulty = Column(String(20), nullable=True)
    description = Column(String(2000), nullable=False)

    user = relationship("User", backref=backref("user", cascade="all, delete-orphan" ))

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name", "description"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "huutis",
            "type": "string"
        }
        props["description"] = {
            "description": "nauris",
            "type": "string"
        }
        return schema

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=False, nullable=False)
    address = Column(String(100), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    def __repr__(self):
        return '<User {}\n,email={}\n>'.format(self.name, self.email)

    @staticmethod
    def json_schema():
        schema = {
            "type": "object",
            "required": ["name", "password", "email"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Name of the user",
            "type": "string"
        }
        props["password"] = {
            "description": "Password of the user",
            "type": "string"
        }
        props["email"] = {
            "description": "Email of the user",
            "type": "string"
        }
        return schema

class Ingredient(db.Model):
    __tablename__ = "ingredient"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    
class Unit(db.Model):
    __tablename__ = "unit"
    id = Column(Integer, primary_key=True)
    unit = Column(String(30), nullable=False)

