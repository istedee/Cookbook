from flask import current_app as app, request
from flask_restful import Resource

from ..models import Recipe, db, Ingredient, Recipeingredient

class Recipeingredients(Resource):

    def __init__(self) -> None:
        super().__init__()

    def get(self):
        if request.method != "GET":
            return "GET method required", 405
        inventory = db.session.query(Recipe).all()
        emt = [
        {
            "name": item.name,
            "Ingredients": [
                [
                    ingredient.name,
#                    recipe.amount_id,
#                    recipe.unit_id
                ] for ingredient in db.session.query(Ingredient).filter(Recipeingredient.ingredient_id==Ingredient.id).order_by(Recipeingredient.id).all()]
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
            user_mail = request.json["id"]
            user_name = request.json["ingredient_id"]
        except KeyError:
            return "Incomplete request - missing fields", 400
        new_user = Recipeingredient(
            id=user_name,
            ingredient_id=user_mail,
        )
        db.session.add(new_user)
        db.session.commit()
        return " ", 201