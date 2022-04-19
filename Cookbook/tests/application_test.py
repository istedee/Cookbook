import json
import os
import sys
import pytest
import tempfile

from sqlalchemy import event
from sqlalchemy.engine import Engine
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cookbook import create_app, DB
from cookbook.models import Recipe, Ingredient, Unit, User


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)

    with app.app_context():
        DB.create_all()
        _fill_db()
        
    yield app.test_client()
    
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


def _fill_db():
    """
    Tests populating database
    """

    test_user = _create_user("Bob", "bob@bobmail.com", "bobword")
    test_recipe = _create_recipe(name="Test-Recipe", description="This is a description")
    test_ingredient = _add_ingredient("Flour")
    test_unit = _add_unit("Cup")

    DB.session.add(test_user)
    DB.session.add(test_recipe)
    DB.session.add(test_ingredient)
    DB.session.add(test_unit)
    DB.session.commit()

def test_start_page(db_handle):
    """Tests first page"""
    RESOURCE_URL = "/api/"
    resp = db_handle.get(RESOURCE_URL)
    assert resp.status_code == 200

class TestIngredientCollection(object):

    RESOURCE_URL = "/api/ingredients/"

    def test_get_ingredient(self, db_handle):
        resp = db_handle.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 1

    def test_post_ingredient(self, db_handle):
        resp = db_handle.post(self.RESOURCE_URL)