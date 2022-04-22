import json
import os
from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from cookbook.constants import *


db = SQLAlchemy()

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///"
        + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from . import models

    """Imports API configuration"""
    from . import api
    from .resources.user import UserConverter
    from .resources.recipe import RecipeConverter
    from .resources.ingredient import IngredientConverter

    app.url_map.converters["recipe"] = RecipeConverter
    app.url_map.converters["user"] = UserConverter
    app.url_map.converters["ingredient"] = IngredientConverter
    from .models import User

    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.generate_test_data)
    app.register_blueprint(api.api_bp)

    @app.route(LINK_RELATIONS_URL)
    def send_link_relations():
        return "link relations"

    @app.route("/profiles/<profile>/")
    def send_profile(profile):
        return "you requests {} profile".format(profile)

    @app.route("/api/")
    def view():
        """Return api entrypoint."""
        body = {
            "@namespaces": {
                "cookbook": {
                    "name": "/cookbook/link-relations/"
                }
            },
            "@controls": {
                "cookbook:users-all": {
                    "href": "/api/users/"
                }
            }
        }
        return Response(status=200, response=json.dumps(body, indent=2), mimetype=MASON)

    return app
