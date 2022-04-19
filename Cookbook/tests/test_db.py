import os
import sys
import pytest
import tempfile

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cookbook import create_app, DB
from cookbook.models import Recipe, Ingredient, Unit, User, generate_test_data


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set db engine"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def db_handle():
    """"Setting the db_handle for testing purpose"""
    db_fd, db_fname = tempfile.mkstemp()
    app = create_app
    config = {"SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname, "TESTING": True}

    app = create_app(config)

    with app.app_context():
        DB.create_all()

    yield app

    os.close(db_fd)
    os.unlink(db_fname)


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


def test_fill_db(db_handle):
    """
    Tests populating database
    """

    test_user = _create_user("Bob", "bob@bobmail.com", "bobword")
    test_recipe = _create_recipe()
    test_ingredient = _add_ingredient("Flour")
    test_unit = _add_unit("Cup")

    with db_handle.app_context():

        DB.session.add(test_user)
        DB.session.add(test_recipe)
        DB.session.add(test_ingredient)
        DB.session.add(test_unit)
        DB.session.commit()

        assert User.query.count() == 1
        assert Recipe.query.count() == 1
        assert Ingredient.query.count() == 1
        assert Unit.query.count() == 1

def test_duplicate_recipes(db_handle):
    """
    Tests duplicate recipe addition to the database
    """
    with db_handle.app_context():
        test_recipe_1 = _create_recipe()
        test_recipe_2 = _create_recipe()
        DB.session.add(test_recipe_1)
        DB.session.add(test_recipe_2)
        with pytest.raises(IntegrityError):
            DB.session.commit()
