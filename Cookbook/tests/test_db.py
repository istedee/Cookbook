import os
import sys
import pytest
import tempfile

from sqlalchemy import event
from sqlalchemy.engine import Engine

# Solution for importing the needed create_app
# with telling the tests their folder first
# Found from below link
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from cookbook import create_app, DB
from cookbook.models import Recipe, Ingredient, Unit, User, init_db_command


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def app():

    db_fd, db_fname = tempfile.mkstemp()
    config = {"SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname, "TESTING": True}

    app = create_app(config)

    with app.app_context():
        init_db_command()

    yield app

    os.close(db_fd)
    os.unlink(db_fname)


# @pytest.fixture()
# def client(app):
#     return app.test_client()


# @pytest.fixture()
# def runner(app):
#     return app.test_cli_runner()


def test_creation():
    """Test creating the application"""
    flask_app = create_app()

    with flask_app.test_client() as test_client:
        response = test_client.get("/api/")
        assert response.status_code == 200


def _create_recipe(name="Cake-recipe", description="Recipe for Cake"):
    """
    Creates Recipe model
    """
    return Recipe(name=name, description=description)


def _add_ingredient(name=""):
    """
    Creates Ingredient model
    """
    return Ingredient(name=name)


def _add_unit(name=""):
    """
    Creates Unit model
    """
    return Unit(name=name)


def _create_user(name="", email="", password=""):
    """
    Creates User model
    """
    return User(name=name, email=email, password=password)


def test_fill_db(app):
    """
    Tests populating database
    """

    with app.app_context():

        test_user = _create_user("Bob", "bob@bobmail.com", "bobword")
        test_recipe = _create_recipe()
        test_ingredient = _add_ingredient("Flour")
        test_unit = _add_unit("Cup")

        DB.session.add(test_user)
        DB.session.add(test_recipe)
        DB.session.add(test_ingredient)
        DB.session.add(test_unit)
        DB.session.commit()

        assert User.query.count() == 1
        assert Recipe.query.count() == 1
        assert Ingredient.query.count() == 1
        assert Unit.query.count() == 1
