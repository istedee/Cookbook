import json
import os
import sys
import pytest
import tempfile
from jsonschema import validate, draft7_format_checker

from sqlalchemy import event
from sqlalchemy.engine import Engine

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from cookbook import create_app, DB
from cookbook.models import Recipe, Ingredient, Recipeingredient, Unit, User


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    config = {"SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname, "TESTING": True}

    # First create_app() for checking deployment without config
    app = create_app()

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
    test_recipe = _create_recipe(
        name="Test-Recipe", description="This is a description"
    )
    test_ingredient = _add_ingredient("Flour")
    test_unit = _add_unit("Cup")

    DB.session.add(test_user)
    DB.session.add(test_recipe)
    DB.session.add(test_ingredient)
    DB.session.add(test_unit)
    DB.session.commit()


def _check_control_get_href(ctrl, client, obj):
    """
    Confirms the response objects item list href to be correct
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200


def _valid_recipe_json(version=0):
    """
    Returns a JSON object for POST and PUT to accept the schema
    """
    return {
        "recipe": {
            "name": f"Cake-Recipe-{version}",
            "description": f"Desc of Cake-Recipe-{version}",
            "difficulty": "hard",
        },
        "ingredients": [{"name": "Ingredient"}],
    }


def _valid_recipe_barebones():
    """
    Returns a JSON object for testing the schema
    """
    return {"name": "Cake", "description": "Normal cake I guess"}


def _invalid_recipe_json(version=0):
    """
    Returns a JSON object for POST and PUT to accept the schema
    """
    return {
        "recipe": {
            "name": f"Cake-Recipe-{version}",
            "description": f"Desc of Cake-Recipe-{version}",
            "difficulty": "hard",
        },
        "ingredients": [{"nameeeee": f"Ingredient-{version}"}],
    }


def _valid_user_json(name="", email="", password=""):
    """
    Returns User json to check schema
    """
    return {"name": f"{name}", "email": f"{email}", "password": f"{password}"}


def _valid_recipe_put(name=""):
    """
    Returns Recipe ingredient to put it to the database
    """
    return {"name": f"{name}", "description": "This is modified"}


def _invalid_recipe_put(name=""):
    """
    Returns Recipe ingredient to put it to the database
    """
    return {"namee": f"{name}", "description": "This is modified"}


def _valid_ingredient_json():
    """Returns valid Recipeingredient JSON for schema validation"""
    return {"name": "Lonkero_Original_Karpalo_5.5%", "unit": "kolpakko", "amount": 1}


def _valid_unit_json():
    """Return valid Unit JSON for schema validation"""
    return {"name": "Tuoppi"}


def test_schema_validation():
    """Test validation for database schemas"""
    validate(
        _valid_user_json("Bob", "bob@bobmail.com", "bobword"),
        User.json_schema(),
        format_checker=draft7_format_checker,
    )

    validate(
        _valid_recipe_barebones(),
        Recipe.json_schema(),
        format_checker=draft7_format_checker,
    )

    validate(
        _valid_ingredient_json(),
        Recipeingredient.json_schema(),
        format_checker=draft7_format_checker,
    )

    validate(
        _valid_unit_json(),
        Unit.json_schema(),
        format_checker=draft7_format_checker,
    )


def test_start_page(db_handle):
    """Tests first page"""
    RESOURCE_URL = "/api/"
    resp = db_handle.get(RESOURCE_URL)
    assert resp.status_code == 200


def test_link_relations(db_handle):
    """
    Test link_relations_page
    """
    RESOURCE_URL = "cookbook/link-relations/"
    resp = db_handle.get(RESOURCE_URL)
    assert resp.status_code == 200


def test_profile(db_handle):
    """
    Test profile page
    """
    RESOURCE_URL = "profiles/Bob/"
    resp = db_handle.get(RESOURCE_URL)
    assert resp.status_code == 200
    assert "Bob" in str(resp.data)


class TestIngredientCollection(object):
    """
    Test IngredientCollection methods and return values
    """

    RESOURCE_URL = "/api/ingredients/"

    def test_get_ingredient_collection(self, db_handle):
        """
        Test GET from ingredients and validate href from recipe list
        """
        resp = db_handle.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body["items"]) == 1
        for recipe in body["items"]:
            _check_control_get_href("self", db_handle, recipe)

    def test_post_ingredient_collection(self, db_handle):
        """
        Test posting valid recipe to app
        and validating correctly with invalid JSON
        """

        valid_data = _valid_recipe_json()
        invalid_data = _invalid_recipe_json()

        resp = db_handle.post(self.RESOURCE_URL, json=valid_data)
        assert resp.status_code == 201

        "Run it again to test existing Ingredient being handled correctly"
        resp = db_handle.post(self.RESOURCE_URL, json=valid_data)
        assert resp.status_code == 201

        resp = db_handle.post(self.RESOURCE_URL, data=valid_data)
        assert resp.status_code == 415

        resp = db_handle.post(self.RESOURCE_URL, json=invalid_data)
        assert resp.status_code == 400


class TestIngredientItem(object):
    """
    Test IngredientItem methods and return values
    """

    RESOURCE_URL = "/api/ingredients/Flour/"
    INVALID_RESOURCE_URL = "/api/ingredients/NotFound/"

    def test_get_ingredient(self, db_handle):
        """
        Test GET for single ingredient
        """
        resp = db_handle.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Flour"

    def test_get_nonexist_ingredient(self, db_handle):
        """
        Test GET for single non-existent ingredient
        """
        resp = db_handle.get(self.INVALID_RESOURCE_URL)
        assert resp.status_code == 404

    def test_put_ingredient(self, db_handle):
        """
        Test PUT for ingredient
        """

        valid_recipe = _valid_recipe_put("Flour")
        valid_recipe_ing = _valid_recipe_put("Ingredient")
        invalid_recipe = _valid_recipe_put("ThisIsNotFound")
        invalid_schema = _invalid_recipe_put("Flour")
        valid_data = _valid_recipe_json()

        resp = db_handle.put(self.RESOURCE_URL, json=valid_recipe)
        assert resp.status_code == 204

        resp = db_handle.post(self.RESOURCE_URL, json=valid_data)
        assert resp.status_code == 405

        resp = db_handle.put(self.INVALID_RESOURCE_URL, json=invalid_recipe)
        assert resp.status_code == 404

        resp = db_handle.put(self.RESOURCE_URL, data=valid_recipe)
        assert resp.status_code == 415

        resp = db_handle.put(self.RESOURCE_URL, json=invalid_schema)
        assert resp.status_code == 400

        # Used for inserting existing Ingredient to the database
        # And trying to change Flour to this Ingredient return 409 code
        valid_data = _valid_recipe_json()
        RESOURCE_URL_RECIPE = "/api/ingredients/"

        resp = db_handle.post(RESOURCE_URL_RECIPE, json=valid_data)
        assert resp.status_code == 201

        # Validate the existing Ingredient and return 409 status code
        # Since Flour cannot override existing Ingredient
        resp = db_handle.put(self.RESOURCE_URL, json=valid_recipe_ing)
        assert resp.status_code == 409

    def test_delete_ingredient(self, db_handle):
        """
        Test DELETE for ingredient
        """

        valid_recipe = _valid_recipe_put("Flour")
        invalid_recipe = _valid_recipe_put("ThisIsNotFound")

        resp = db_handle.delete(self.RESOURCE_URL, json=valid_recipe)
        assert resp.status_code == 204

        resp = db_handle.put(self.RESOURCE_URL, json=invalid_recipe)
        assert resp.status_code == 404
