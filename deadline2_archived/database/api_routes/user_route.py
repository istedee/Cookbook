from flask import current_app as app, request
from flask_restful import Resource

from ..models import User, Recipe, db

class UserCollection(Resource):

    def __init__(self) -> None:
        super().__init__()

    def get(self):
        if request.method != "GET":
            return "GET method required", 405
        inventory = db.session.query(User).join(Recipe).all()
        emt = [
        {
            "name": item.name,
            "email": item.email,
            "password": item.password,
            "id" : item.id,
            "recipes": [
                [
                    recipe.name
                ] for recipe in Recipe.query.filter_by(user_id=item.id).all()]
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
            user_mail = request.json["email"]
            product_handle = db.session.query(User).filter_by(email=user_mail).first()
            if product_handle:
                return "Name already exists", 409
            user_name = request.json["name"]
            user_password = request.json["password"]
        except KeyError:
            return "Incomplete request - missing fields", 400
        new_user = User(
            name=user_name,
            email=user_mail,
            password=user_password
        )
        db.session.add(new_user)
        db.session.commit()
        return " ", 201