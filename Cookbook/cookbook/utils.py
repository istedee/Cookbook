"""
Utility methods for Flask application
"""

import json
from sqlite3 import IntegrityError
from flask import Response, request, url_for
from .constants import ERROR_PROFILE, MASON
from .models import Recipe, User, Ingredient
from . import DB


class MasonBuilder(dict):
    """
    Defines Masonbuilder used for schema control
    """

    DELETE_RELATION = ""

    def add_error(self, title, details):

        """
        Error definition
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, n_s, uri):
        """
        Namespace addition definition
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][n_s] = {"name": uri}

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Controls when to add a control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

    def add_control_post(self, ctrl_name, title, href, schema):
        """
        Method to add a control POST
        """

        self.add_control(
            ctrl_name, href, method="POST", encoding="json", title=title, schema=schema
        )

    def add_control_put(self, title, href, schema):
        """
        Method to add a control PUT
        """

        self.add_control(
            "edit", href, method="PUT", encoding="json", title=title, schema=schema
        )

    def add_control_delete(self, title, href):
        """
        Method to add a control DELETE
        """

        self.add_control(
            "storage:delete",
            href,
            method="DELETE",
            title=title,
        )


class RecipeBuilder(MasonBuilder):
    """
    Recipebuilder controls the routes for recipes
    """
    def add_control_recipes_all(self, user):
        """
        Method to add a all recipes control
        """
        self.add_control(
            ctrl_name="cookbook:recipes-all",
            href=url_for("api.recipecollection", user=user),
            title="All recipes",
            method="GET",
            encoding="JSON",
        )

    def add_control_add_recipe(self, user):
        """
        Method to add a recipe
        """
        self.add_control_post(
            ctrl_name="cookbook:add-recipe",
            title="Add a new prod",
            href=url_for("api.recipecollection", user=user),
            schema=Recipe.json_schema(),
        )

    def add_control_delete_recipe(self, recipe_name, user):
        """
        Method to delete a recipe
        """
        self.add_control_delete(
            "cookbook:delete",
            url_for("api.recipeitem", user=user.name, recipe=recipe_name.name),
        )

    def add_control_edit_recipe(self, recipe_name, user):
        """
        Method to edit a recipe
        """
        self.add_control_put(
            "Edit this recipe",
            url_for("api.recipeitem", user=user.name, recipe=recipe_name.name),
            Recipe.json_schema(),
        )

    def add_control_all_users(self):
        """
        Method to add all users method
        """
        self.add_control(
            "cookbook:users-all",
            url_for("usercollection"),
            title="All users",
            method="GET",
            encoding="JSON",
        )

    def add_control_add_user(self):
        """
        Method to add an user
        """
        self.add_control_post(
            "cookbook:add-user",
            href=url_for("api.usercollection"),
            title="Add user",
            schema=User.json_schema(),
        )

    def add_control_edit_user(self, user):
        """
        Method to edit an user
        """
        self.add_control_put(
            "edit", href=url_for("api.useritem", user=user), schema=User.json_schema()
        )

    def add_control_delete_user(self, user):
        """
        Method to delete an user
        """
        self.add_control(
            "cookbook:delete",
            href=url_for("api.useritem", user=user),
            method="DELETE",
            title="Delete this user",
        )


class IngredientBuilder(MasonBuilder):
    """Builder for Ingredients routes"""
    def add_control_ingredients_all(self, ingredient):
        """Route for all ingredients"""
        self.add_control(
            ctrl_name="cookbook:ingredients-all",
            href=url_for("api.ingredientcollection", ingredient=ingredient),
            title="All ingredients",
            method="GET",
            encoding="JSON",
        )

    def add_control_add_ingredient(self, ingredient):
        """Route for a single ingredient"""
        self.add_control_post(
            ctrl_name="cookbook:add-ingredient",
            title="Add a new ingredient",
            href=url_for("api.ingredientcollection", ingredient=ingredient),
            schema=Ingredient.json_schema(),
        )

    def add_control_delete_ingredient(self, ingredient):
        """Route for deleting an ingredient"""
        self.add_control_delete(
            "cookbook:delete", url_for("api.ingredientitem", ingredient=ingredient)
        )

    def add_control_edit_ingredient(self, ingredient):
        """Route for editing an ingredient"""
        self.add_control_put(
            "Edit this ingredient",
            url_for("api.ingredientitem", ingredient=ingredient),
            Ingredient.json_schema(),
        )


def create_error_response(status_code, title, message=None):
    """Returns an error response"""
    resource_url = request.path
    data = MasonBuilder(resource_url=resource_url)
    data.add_error(title, message)
    data.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(data), status_code, mimetype=MASON)


def search_models(param, dbmodel):
    """Searches database models and returns a hit if found"""
    result = DB.session.query(dbmodel).filter_by(name=param).first()
    if not result:
        try:
            ing_bob = dbmodel(name=param)
            DB.session.add(ing_bob)
            DB.session.commit()
        except IntegrityError:
            DB.session.rollback()
    result = DB.session.query(dbmodel).filter_by(name=param).first()
    return result.id
