import json
from flask import request, Response, url_for
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
from jsonschema import validate, ValidationError, draft7_format_checker
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter

from ..utils import IngredientBuilder, create_error_response
from .. import db
from ..models import Ingredient
from ..constants import *

class IngredientCollection(Resource):
    def get(self):
        build = IngredientBuilder(items=[])
        inventory = db.session.query(Ingredient).all()
        for item in inventory:
            data = IngredientBuilder(
                name=item.name,
            )
            
            data.add_control(
                "self", url_for("api.ingredientitem",
                        ingredient=item.name)
                        )
        build.add_control("self", href=url_for("api.ingredientcollection",
                        ingredient=item)
                        )
        build.add_control_add_ingredient(item.name)
        
        return Response(
            status=200,
            response=json.dumps(
                build, indent=4, separators=(",", ": "), sort_keys=True
            ),
            mimetype=MASON,
        )

    def post(self):

        if request.json == None:
            return create_error_response(415, "BAD CONTENT", "MUST BE JSON")
        try:
            for ingredient in request.json["ingredients"]:
                validate(
                    ingredient, Ingredient.json_schema(), format_checker=draft7_format_checker
                )
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON", str(e))
        try:
            for i in request.json["ingredients"]:
                p_name = i["name"]
                ing_name = Ingredient.query.filter_by(name=p_name).first()
                if ing_name:
                    continue

                try:
                    new_ingredient = Ingredient(
                    name=p_name,
                    )
                    db.session.add(new_ingredient)
                    db.session.commit()
                except IntegrityError:
                    return create_error_response(409, "Duplicate", "Database error")

        except KeyError:
            return create_error_response(400, "KeyError", "Check the JSON keys")

        return Response(
            status=201,
            mimetype=MASON,
            headers={
                "Location": url_for("api.ingredientitem", ingredient=ingredient, recipe=p_name)
            },
        )

class IngredientItem(Resource):
    def get(self, ingredient):
        ing = db.session.query(Ingredient).filter_by(name=ingredient.name).first()
        if not ing:
            return create_error_response(404, "Ingredient not found")

        data = IngredientBuilder(
            name=ing.name,
        )
        data.add_namespace("storage", LINK_RELATIONS_URL)
        data.add_control("self", url_for("api.ingredientitem", ingredient=ing.name))
        data.add_control("collection", url_for("api.ingredientcollection"))

        return Response(
            json.dumps(data, indent=4, separators=(",", ": ")),
            status=200,
            mimetype=MASON,
        )

    def put(self, ingredient):
        ing = db.session.query(Ingredient).filter_by(name=ingredient.name).first()
        if not ing:
            return create_error_response(404, "Ingredient not found")
        if not request.json:
            return create_error_response(415, "Wrong content", "Should be JSON")
        try:
            validate(request.json, Ingredient.json_schema())
        except ValidationError:
            return create_error_response(400, "Invalid content", "Validation fails")
        ing.name = request.json["name"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return create_error_response(status_code=409, title="Taken")
        return Response(status=204, mimetype=MASON)

    def delete(self, ingredient):
        ing = db.session.query(Ingredient).filter_by(name=ingredient.name).first()
        if not ing:
            return create_error_response(404, "Not Found", "Ingredient: {ingredient.name} not found")

        db.session.delete(ing)
        db.session.commit()
        return Response(status=204, mimetype=MASON)

class IngredientConverter(BaseConverter):
    def to_python(self, ingredient):
        db_ingredient = db.session.query(Ingredient).filter_by(name=ingredient).first()
        if db_ingredient is None:
            raise NotFound
        return db_ingredient

    def to_url(self, db_ingredient):
        return str(db_ingredient)
