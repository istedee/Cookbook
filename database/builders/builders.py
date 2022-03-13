import json
from sqlite3 import IntegrityError
from flask import url_for, Response, request
from flask_restful import Api, Resource
from sqlalchemy import null
from database.models import Recipe, User
from .. import db
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter
from jsonschema import validate, ValidationError, draft7_format_checker


MASON = "application/vnd.mason+json"
ERROR_PROFILE = "/profiles/error-profile/"
LINK_RELATIONS_URL = "/storage/link-relations/"
PRODUCT_PROFILE_URL = "/profiles/product/"
JSON = "application/json"

class RecipeConverter(BaseConverter):
    def to_python(self, recipe):
        db_recipe = db.session.query(Recipe).filter_by(name=recipe).first()
        if db_recipe is None:
            raise NotFound
        return db_recipe
    
    def to_url(self, db_recipe):
        return str(db_recipe)

class MasonBuilder(dict):

    DELETE_RELATION = ""

    def add_error(self, title, details):

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href
        
    def add_control_post(self, ctrl_name, title, href, schema):
    
        self.add_control(
            ctrl_name,
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_put(self, title, href, schema):

        self.add_control(
            "edit",
            href,
            method="PUT",
            encoding="json",
            title=title,
            schema=schema
        )

    def add_control_delete(self, title, href):
        
        self.add_control(
            "storage:delete",
            href,
            method="DELETE",
            title=title,
        )

class RecipeBuilder(MasonBuilder):

    def add_control_recipes_all(self):
        self.add_control(
            ctrl_name="storage:recipes-all",
            href=url_for("recipecollection"),
            title="All recipes",
            method="GET",
            encoding="JSON"
        )

    def add_control_add_recipe(self):
        self.add_control_post(
            ctrl_name="storage:add-recipe",
            title="Add a new recipe",
            href=url_for("recipecollection"),
            schema=Recipe.json_schema()
        )

    def add_control_delete_recipe(self, recipe_name):
        self.add_control_delete(
            "storage:delete",
            url_for("recipeitem", recipe=recipe_name.name)
        )

    def add_control_edit_recipe(self, recipe_name):
        self.add_control_put(
            "Edit this recipe",
            url_for("recipeitem", recipe=recipe_name.name),
            Recipe.json_schema()
        )

class UserBuilder(MasonBuilder):

    def add_control_users_all(self):
        self.add_control(
            ctrl_name="storage:users-all",
            href=url_for("usercollection"),
            title="All users",
            method="GET",
            encoding="JSON"
        )

    def add_control_add_user(self):
        self.add_control_post(
            ctrl_name="storage:add-user",
            title="Add a new user",
            href=url_for("usercollection"),
            schema=User.json_schema()
        )

    def add_control_delete_user(self, user):
        self.add_control_delete(
            "storage:delete",
            url_for("user", user=user.name)
        )

    def add_control_edit_user(self, user):
        self.add_control_put(
            "Edit this user",
            url_for("user", user=user.name),
            User.json_schema()
        )

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    data = MasonBuilder(resource_url=resource_url)
    data.add_error(title, message)
    data.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(data), status_code, mimetype=MASON)

class RecipeCollection(Resource):

    def get(self):
        build = RecipeBuilder(items=[])
        inventory = db.session.query(Recipe).all()
        for item in inventory:
            if item.difficulty == None:
                item.difficulty = 'No difficulty rating'
            data = RecipeBuilder(
                name=item.name,
                description=item.description,
                difficulty=item.difficulty,
                user_id=item.user_id,

            )
            data.add_control("self", url_for("recipeitem", recipe=item.name))
            build["items"].append(data)
        build.add_control("self", href=url_for("recipecollection"))
        build.add_control_add_recipe()

        return Response(
            status=200,
            response=json.dumps(build, indent=4, separators=(',', ': '), sort_keys=True),
            mimetype=MASON)

    def post(self):
        if request.json == None:
            return create_error_response(415, "BAD CONTENT", "MUST BE JSON")
        try:
            validate(
                request.json,
                Recipe.json_schema(),
                format_checker=draft7_format_checker
            )
        except ValidationError as e:
            return create_error_response(
                400,
                "Invalid JSON",
                str(e))
        try:
            p_name = request.json["name"]
            recipe_name = Recipe.query.filter_by(name=p_name).first()
            if recipe_name:
                return create_error_response(409, "ON JO", "Duplicate 🥝")
            p_weight = request.json["description"]
            if not isinstance(p_weight, str):
                return create_error_response(400, "Invalid values")
        except KeyError:
            return create_error_response(400, "KeyError")
        try:
            new_recipe = Recipe(
            name=p_name,
            description=p_weight,
            )
            db.session.add(new_recipe)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Duplicate", "Database error")

        return Response(
            status=201,
            mimetype=MASON,
            headers={"Location": Api.url_for(RecipeItem, recipe=p_name)}
        )

class UserRecipeCollection(Resource):

    def get(self, user):
        build = RecipeBuilder(items=[])
        inventory = db.session.query(Recipe
        ).filter_by(user_id=user.id
        ).all()
        for item in inventory:
            if item.difficulty == None:
                item.difficulty = 'No difficulty rating'
            data = RecipeBuilder(
                name=item.name,
                description=item.description,
                difficulty=item.difficulty,
                owner=user.name,
                user_id=item.user_id,

            )
            data.add_control("self", url_for("recipeitem", recipe=item.name))
            build["items"].append(data)
        build.add_control("self", href=url_for("recipecollection"))
        build.add_control_add_recipe()

        return Response(
            status=200,
            response=json.dumps(build, indent=4, separators=(',', ': '), sort_keys=True),
            mimetype=MASON)

    def post(self):
        if request.json == None:
            return create_error_response(415, "BAD CONTENT", "MUST BE JSON")
        try:
            validate(
                request.json,
                Recipe.json_schema(),
                format_checker=draft7_format_checker
            )
        except ValidationError as e:
            return create_error_response(
                400,
                "Invalid JSON",
                str(e))
        try:
            p_name = request.json["name"]
            recipe_name = Recipe.query.filter_by(name=p_name).first()
            if recipe_name:
                return create_error_response(409, "ON JO", "Duplicate 🥝")
            p_weight = request.json["description"]
            if not isinstance(p_weight, str):
                return create_error_response(400, "Invalid values")
        except KeyError:
            return create_error_response(400, "KeyError")
        try:
            new_recipe = Recipe(
            name=p_name,
            description=p_weight,
            )
            db.session.add(new_recipe)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Duplicate", "Database error")

        return Response(
            status=201,
            mimetype=MASON,
            headers={"Location": Api.url_for(RecipeItem, recipe=p_name)}
        )

class RecipeItem(Resource):
    
    def get(self, recipe):
        recipe_item = db.session.query(Recipe).filter_by(name=recipe.name).first()
        if recipe_item == None:
            return create_error_response(404, "Ei oo", "No recipe_item")
        data = RecipeBuilder(
            name=recipe_item.name,
            description=recipe_item.description
        )
        data.add_namespace("storage", LINK_RELATIONS_URL)
        data.add_control("self", url_for("recipeitem", recipe=recipe.name))
        data.add_control("collection", url_for("recipecollection"))
        data.add_control("profile", href=PRODUCT_PROFILE_URL)
        data.add_control_edit_recipe(recipe)
        data.add_control_delete_recipe(recipe)

        return Response(json.dumps(data), status=200, mimetype=JSON)
    
    def put(self, recipe):
        recipe_item = db.session.query(Recipe).filter_by(name=recipe.name).first()
        if not recipe_item:
            return create_error_response(404, "recipe not found")
        try:
            recipe_item.name = request.json["name"]
            recipe_item.description = request.json["description"]
        except TypeError:
            return create_error_response(415, "Wrong content", "Should be JSON")
        except KeyError:
            return create_error_response(400, "Invalid content", "Validation fails")
        except ValueError:
            return create_error_response(400, "Invalid content", "Validation fails")
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return create_error_response(status_code=409, title="Taken")
        return Response(status=204, mimetype=MASON)
    
    def delete(self, recipe):
        recipe_h = db.session.query(Recipe).filter_by(name=recipe.name).first()
        if not recipe_h:
            return create_error_response(404, "Not Found", "recipe not found")
        
        db.session.delete(recipe_h)
        db.session.commit()
        return Response(status=204, mimetype=MASON)

class UserConverter(BaseConverter):
    def to_python(self, name):
        db_user = db.session.query(User).filter_by(name=name).first()
        if db_user is None:
            raise NotFound
        return db_user
    
    def to_url(self, db_user):
        return str(db_user)

class UserRecipe(Resource):
    
    def get(self, user, recipe):
        recipe_item = db.session.query(Recipe
        ).filter_by(user_id=user.id
        ).filter_by(name=recipe.name
        ).first()
        if recipe_item == None:
            return create_error_response(404, "Ei oo tollasta useria", "No such user")
        data = RecipeBuilder(
            name=recipe_item.name,
            description=recipe_item.description,
            owner=user.name,
        )
        data.add_control_edit_recipe(recipe)
        data.add_control_delete_recipe(recipe)

        return Response(json.dumps(data), status=200, mimetype=JSON)
    
    def put(self, recipe):
        recipe_item = db.session.query(Recipe).filter_by(name=recipe.name).first()
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
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return create_error_response(status_code=409, title="Taken")
        return Response(status=204, mimetype=MASON)
    
    def delete(self, recipe):
        recipe_h = db.session.query(Recipe).filter_by(name=recipe.name).first()
        if not recipe_h:
            return create_error_response(404, "Not Found", "recipe not found")
        
        db.session.delete(recipe_h)
        db.session.commit()
        return Response(status=204, mimetype=MASON)