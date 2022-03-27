"""This file imports the API configuration
    for routing"""

from flask import Blueprint
from flask_restful import Api

from .resources.user import UserCollection, UserItem, UserConverter
from .resources.recipe import RecipeCollection, RecipeItem, RecipeConverter
from .resources.ingredient import IngredientCollection, IngredientConverter, IngredientItem

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(UserCollection, "/users/" )
api.add_resource(UserItem, "/users/<user:user>/")
api.add_resource(RecipeCollection, "/users/<user:user>/recipes/")
api.add_resource(RecipeItem, "/users/<user:user>/recipes/<recipe:recipe>/")
api.add_resource(IngredientCollection, "/ingredients/")
api.add_resource(IngredientItem, "/ingredients/<ingredient:ingredient>/")