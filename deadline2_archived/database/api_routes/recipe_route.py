from flask import current_app as app, request
from flask_restful import Resource

from ..models import Recipe, db

class Recipes(Resource):

    def __init__(self) -> None:
        super().__init__()
    
    def get(self):
        if request.method != "GET":
            return "GET method required", 405
        inventory = db.session.query(Recipe)
        emt = [
        {
            "name": item.name,
            "description": item.description,
            "difficulty": item.difficulty,
            "id" : item.id
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
            name_recipe = request.json["name"]
            recipe_exists = db.session.query(Recipe).filter_by(name=name_recipe).first()
            if recipe_exists:
                return "Name already exists", 409
            difficulty_rate = request.json["difficulty"]
            description_posted = request.json["description"]
            users_id = request.json["user_id"]
        
        except KeyError:
            return "Incomplete request - missing fields", 400
        new_recipe = Recipe(
#            id=1,
            name=name_recipe,
            difficulty=difficulty_rate,
            description=description_posted,
            user_id=users_id
        )
        db.session.add(new_recipe)
        db.session.commit()
        return " ", 201