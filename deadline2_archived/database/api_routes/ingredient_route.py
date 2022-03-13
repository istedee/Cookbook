from flask import current_app as app, request
from flask_restful import Resource

from ..models import db, Ingredient

class Ingredients(Resource):

    def __init__(self) -> None:
        super().__init__()
    
    def get(self):
        if request.method != "GET":
            return "GET method required", 405
        inventory = db.session.query(Ingredient)
        emt = [
        {
            "name": item.name,
        } for item in inventory]
        if emt == []:
            emt = "EI VITTU LÖYDY MITÄÄN!!!"
        return emt

    def post(self):
        if request.method != "POST":
            return "POST method required", 405
        if request.json == None:
            return "Request content type must be JSON", 415
        try:
            name_ingredient = request.json["name"]
            recipe_exists = db.session.query(Ingredient).filter_by(name=name_ingredient).first()
            if recipe_exists:
                return "Ingredient already exists", 409
        except KeyError:
            return "Incomplete request - missing fields", 400
        new_recipe = Ingredient(
            name=name_ingredient
        )
        db.session.add(new_recipe)
        db.session.commit()
        return " ", 201
