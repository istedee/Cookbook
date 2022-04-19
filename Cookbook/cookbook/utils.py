import json
from sqlite3 import IntegrityError
from flask import Response, request, url_for
from .constants import *
from .models import *
from . import db


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

        self["@namespaces"][ns] = {"name": uri}

    def add_control(self, ctrl_name, href, **kwargs):

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

    def add_control_post(self, ctrl_name, title, href, schema):

        self.add_control(
            ctrl_name, href, method="POST", encoding="json", title=title, schema=schema
        )

    def add_control_put(self, title, href, schema):

        self.add_control(
            "edit", href, method="PUT", encoding="json", title=title, schema=schema
        )

    def add_control_delete(self, title, href):

        self.add_control(
            "storage:delete",
            href,
            method="DELETE",
            title=title,
        )


class RecipeBuilder(MasonBuilder):
    def add_control_recipes_all(self, user):
        self.add_control(
            ctrl_name="cookbook:recipes-all",
            href=url_for("api.recipecollection", user=user),
            title="All recipes",
            method="GET",
            encoding="JSON",
        )

    def add_control_add_recipe(self, user):
        self.add_control_post(
            ctrl_name="cookbook:add-recipe",
            title="Add a new prod",
            href=url_for("api.recipecollection", user=user),
            schema=Recipe.json_schema(),
        )

    def add_control_delete_recipe(self, recipe_name, user):
        self.add_control_delete(
            "cookbook:delete",
            url_for("api.recipeitem", user=user.name, recipe=recipe_name.name),
        )

    def add_control_edit_recipe(self, recipe_name, user):
        self.add_control_put(
            "Edit this recipe",
            url_for("api.recipeitem", user=user.name, recipe=recipe_name.name),
            Recipe.json_schema(),
        )

    def add_control_all_users(self):
        self.add_control(
            "cookbook:users-all",
            url_for("usercollection"),
            title="All users",
            method="GET",
            encoding="JSON",
        )

    def add_control_add_user(self):
        self.add_control_post(
            "cookbook:add-user",
            href=url_for("api.usercollection"),
            title="Add user",
            schema=User.json_schema(),
        )

    def add_control_edit_user(self, user):
        self.add_control_put(
            "edit", href=url_for("api.useritem", user=user), schema=User.json_schema()
        )

    def add_control_delete_user(self, user):
        self.add_control(
            "cookbook:delete",
            href=url_for("api.useritem", user=user),
            method="DELETE",
            title="Delete this user",
        )


class IngredientBuilder(MasonBuilder):
    def add_control_ingredients_all(self, ingredient):
        self.add_control(
            ctrl_name="cookbook:ingredients-all",
            href=url_for("api.ingredientcollection", ingredient=ingredient),
            title="All ingredients",
            method="GET",
            encoding="JSON",
        )

    def add_control_add_ingredient(self, ingredient):
        self.add_control_post(
            ctrl_name="cookbook:add-ingredient",
            title="Add a new ingredient",
            href=url_for("api.ingredientcollection", ingredient=ingredient),
            schema=Ingredient.json_schema(),
        )

    def add_control_delete_ingredient(self, ingredient):
        self.add_control_delete(
            "cookbook:delete", url_for("api.ingredientitem", ingredient=ingredient)
        )

    def add_control_edit_ingredient(self, ingredient):
        self.add_control_put(
            "Edit this ingredient",
            url_for("api.ingredientitem", ingredient=ingredient),
            Ingredient.json_schema(),
        )


def create_error_response(status_code, title, message=None):
    resource_url = request.path
    data = MasonBuilder(resource_url=resource_url)
    data.add_error(title, message)
    data.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(data), status_code, mimetype=MASON)


def searchModels(param, dbmodel):
    result = db.session.query(dbmodel).filter_by(name=param).first()
    if not result:
        try:
            ing_bob = dbmodel(name=param)
            db.session.add(ing_bob)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    result = db.session.query(dbmodel).filter_by(name=param).first()
    return result.id
