"""This file imports the API configuration
    for routing"""

from flask import Blueprint
from flask_restful import Api

from .resources.user import UserCollection, UserItem
from .resources.recipe import RecipeCollection, RecipeItem
from .resources.ingredient import (
    IngredientCollection,
    IngredientItem,
)

API_BP = Blueprint("api", __name__, url_prefix="/api")
API = Api(API_BP)

API.add_resource(UserCollection, "/users/")
API.add_resource(UserItem, "/users/<user:user>/")
API.add_resource(RecipeCollection, "/users/<user:user>/recipes/")
API.add_resource(RecipeItem, "/users/<user:user>/recipes/<recipe:recipe>/")
API.add_resource(IngredientCollection, "/ingredients/")
API.add_resource(IngredientItem, "/ingredients/<ingredient:ingredient>/")
