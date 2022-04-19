"""Methods for Recipe collection"""

import json
from sqlite3 import IntegrityError
from flask import url_for, Response, request
from flask_restful import Resource
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter
from jsonschema import validate, ValidationError, draft7_format_checker
from ..models import Recipe, Ingredient, Recipeingredient, Unit
from .. import DB
from ..utils import (
    IngredientBuilder,
    RecipeBuilder,
    create_error_response,
    search_models,
)
from ..constants import MASON, DIFFICULTIES


class RecipeCollection(Resource):
    """Methods for Recipecollection"""
    def get(self, user):
        """Get method functionality for Recipecollection"""
        build = RecipeBuilder(items=[])
        inventory = DB.session.query(Recipe).filter_by(user_id=user.id).all()
        for item in inventory:
            data = RecipeBuilder(
                name=item.name,
                description=item.description,
                difficulty=item.difficulty,
                owner=user.name,
                user_id=item.user_id,
            )
            data.add_control(
                "self", url_for("api.recipeitem", user=user.name, recipe=item.name)
            )
            build["items"].append(data)
        build.add_control("self", href=url_for("api.recipecollection", user=user.name))
        build.add_control_add_recipe(user.name)

        return Response(
            status=200,
            response=json.dumps(
                build, indent=4, separators=(",", ": "), sort_keys=True
            ),
            mimetype=MASON,
        )

    def post(self, user):
        """Post method functionality for Recipecollection"""

        if request.json is None:
            return create_error_response(415, "BAD CONTENT", "MUST BE JSON")
        try:
            validate(
                request.json["recipe"],
                Recipe.json_schema(),
                format_checker=draft7_format_checker,
            )
            for ingredient in request.json["ingredients"]:
                validate(
                    ingredient,
                    Recipeingredient.json_schema(),
                    format_checker=draft7_format_checker,
                )
        except ValidationError as e_msg:
            return create_error_response(400, "Invalid JSON", str(e_msg))
        try:
            p_name = request.json["recipe"]["name"]
            recipe_name = Recipe.query.filter_by(name=p_name).first()
            if recipe_name:
                return create_error_response(409, "ON JO", "Duplicate 🥝")
            p_desc = request.json["recipe"]["description"]
            if not isinstance(p_desc, str):
                return create_error_response(400, "Invalid values")
            p_diff = request.json["recipe"].get("difficulty", "undefined")
            if p_diff not in DIFFICULTIES:
                p_diff = "undefined"
        except KeyError:
            return create_error_response(400, "KeyError", "SOS")

        try:
            new_recipe = Recipe(
                name=p_name, description=p_desc, difficulty=p_diff, user_id=user.id
            )
            DB.session.add(new_recipe)
            DB.session.commit()
        except IntegrityError:
            return create_error_response(409, "Duplicate", "Database error")

        recipe = DB.session.query(Recipe).filter_by(name=p_name).first()

        for ingredient in request.json["ingredients"]:
            recipe_id = recipe.id
            ing_id = search_models(ingredient["name"], Ingredient)
            ing_unit = search_models(ingredient["unit"], Unit)
            ing_amount = ingredient["amount"]
            try:
                new_ingredient = Recipeingredient(
                    id=recipe_id,
                    ingredient_id=ing_id,
                    amount=ing_amount,
                    unit_id=ing_unit,
                )
                DB.session.add(new_ingredient)
                DB.session.commit()
            except IntegrityError:
                DB.session.rollback()
                return create_error_response(409, "Duplicate", "Database error")

        return Response(
            status=201,
            mimetype=MASON,
            headers={
                "Location": url_for("api.recipeitem", user=user.name, recipe=p_name)
            },
        )


class RecipeItem(Resource):
    """Methods for Recipeitems"""
    def get(self, recipe, user):
        """Get method functionality for Recipeitem"""
        recipe_item = DB.session.query(Recipe).filter_by(name=recipe.name).first()
        recipe_ingredient = (
            DB.session.query(Ingredient.name, Recipeingredient.amount, Unit.name)
            .filter(Recipeingredient.ingredient_id == Ingredient.id)
            .filter(Recipeingredient.id == recipe.id)
            .filter(Unit.id == Recipeingredient.unit_id)
            .all()
        )
        if recipe_item is None:
            return create_error_response(404, "Ei oo", "No recipe_item")
        #        ingredients = []
        build = IngredientBuilder(items=[])
        for row in recipe_ingredient:
            #            ingredients.append(list(row))
            dataa = IngredientBuilder(name=row[0], amount=row[1], unit=row[2])

            dataa.add_control("self", url_for("api.ingredientitem", ingredient=row[0]))
            build["items"].append(dataa)
        data = RecipeBuilder(
            name=recipe_item.name,
            description=recipe_item.description,
            difficulty=recipe_item.difficulty,
            ingredients=build,
        )
        data.add_control(
            "self", url_for("api.recipeitem", user=user.name, recipe=recipe.name)
        )
        data.add_control("collection", url_for("api.recipecollection", user=user.name))
        data.add_control("user", url_for("api.useritem", user=user.name))
        data.add_control_edit_recipe(recipe, user)
        data.add_control_delete_recipe(recipe, user)

        return Response(json.dumps(data), status=200, mimetype=MASON)

    def put(self, recipe):
        """Put method functionality for Recipeitem"""
        recipe_item = DB.session.query(Recipe).filter_by(name=recipe.name).first()
        if not recipe_item:
            return create_error_response(404, "recipe not found")
        try:
            recipe_item.name = request.json["name"]
            recipe_item.description = request.json["description"]
        except TypeError:
            return create_error_response(415, "Wrong content", "Should be JSON")
        except KeyError:
            return create_error_response(400, "Invalid content", "Validation fails")

        try:
            DB.session.commit()
        except IntegrityError:
            DB.session.rollback()
            return create_error_response(status_code=409, title="Taken")
        return Response(status=204, mimetype=MASON)

    def delete(self, recipe):
        """Delete method functionality for Recipeitem"""
        recipe_h = DB.session.query(Recipe).filter_by(name=recipe.name).first()
        if not recipe_h:
            return create_error_response(404, "Not Found", "recipe not found")

        DB.session.delete(recipe_h)
        DB.session.commit()
        return Response(status=204, mimetype=MASON)


class RecipeConverter(BaseConverter):
    """Converts the Recipe for suitable mode"""
    def to_python(self, recipe):
        """Converts recipe from url to python object"""
        db_recipe = DB.session.query(Recipe).filter_by(name=recipe).first()
        if db_recipe is None:
            raise NotFound
        return db_recipe

    def to_url(self, db_recipe):
        """Converts object to URL"""
        return str(db_recipe)
