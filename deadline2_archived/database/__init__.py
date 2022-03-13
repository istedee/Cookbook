import json
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask import Flask, request


db = SQLAlchemy()


def create_app():
    """Construct the core application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cookbook.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():

        from . import models
        from .api_routes import recipe_route, populate_route, ingredient_route, user_route, recipe_ingredients
        from database.builders.builders import RecipeBuilder, RecipeConverter, RecipeItem, RecipeCollection, UserConverter, UserRecipe, UserRecipeCollection

        db.create_all()  # Create database tables for our data models

        api = Api(app)

        api.add_resource(populate_route.Populate, "/api/populate")
        api.add_resource(ingredient_route.Ingredients, "/api/ingredients")
        api.add_resource(user_route.UserCollection, "/api/users")
        api.add_resource(recipe_ingredients.Recipeingredients, "/api/recipeingredients")
        api.add_resource(RecipeCollection, "/api/recipes/")
        app.url_map.converters["recipe"] = RecipeConverter
        app.url_map.converters["user"] = UserConverter
        api.add_resource(RecipeItem, "/api/recipes/<recipe:recipe>/")
        api.add_resource(UserRecipeCollection, "/api/<user:user>/")
        api.add_resource(UserRecipe, "/api/<user:user>/<recipe:recipe>/")

        @app.route("/api/")
        def view():
            bob = RecipeBuilder()
            bob.add_control_recipes_all()
            return json.dumps(bob)

        @app.route("/profiles/<profile_name>")
        def redirect_to_profile(profile_name):
            pass

        @app.route("/storage/link-relations/")
        def send_link_relations_html():
            return "here be link relations"

        return app
