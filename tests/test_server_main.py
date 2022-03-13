# test main server API

from flask import request
import json
from matplotlib import use
import pytest
import sys
import os

#Solution for importing the needed create_app
#with telling the tests their folder first
#Found from below link
#https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from database import create_app

#Pytest init from
#https://flask.palletsprojects.com/en/2.0.x/testing/

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_new_app():
    """
    Tests to create a new Flask application
    """
    test_app = create_app()

    with test_app.test_client() as test_flask:
        response = test_flask.get("/api/")
        assert response.status_code == 200

def test_recipe_json(client):
    """
    Tests to fetch populated recipe from API
    """
    client.post("/api/populate/", json={

    })
    response = client.get("/api/recipes/")
    assert response.json["items"][0]["name"] == "Cake-Recipe"

def test_recipe_faulty(client):
    """
    Tests to fetch non existent recipe
    """

    client.post("/api/populate/", json={

    })
    response = client.get("/api/recipes/")
    with pytest.raises(AssertionError):
        assert response.json["items"][0]["name"] == "Ville Vallaton"

def test_edit_recipe(client):
    """
    Tests to edit recipe
    """

    edit_msg = "Tata on muokattu"

    client.post("/api/populate/", json={

    })
    client.put("/api/recipes/Water-Recipe", data={
        "name": "Water-Recipe",
        "description": edit_msg
    })
    response = client.get("/api/recipes/Water-Recipe/")
    assert response.json["description"] == edit_msg

def test_edit_non_existent_recipe(client):
    """
    Tests to edit recipe which does not exist in the db
    """

    edit_msg = "Tata on muokattu"

    client.post("/api/populate/", json={

    })
    response = client.put("/api/recipes/Ei-ole-resepti/", data={
        "name": "Water-Recipe",
        "description": edit_msg
    })
    #Test returns 404 since this recipe does not exist
    assert response.status_code == 404

def test_edit_recipe_faulty_key(client):

    edit_msg = "Tata on muokattu"

    client.post("/api/populate/", json={

    })
    response = client.put("/api/recipes/Water-Recipe/", data={
        "name": "Water-Recipe",
        "faulty_key": edit_msg
    })
    #Test returns 415 since this key is faulty
    assert response.status_code == 415

def test_get_user_recipe(client):

    user = "Taneli-Testiukko"
    recipe = "Water-Recipe"

    client.post("/api/populate/", json={

    })
    response = client.get("/api/" + user + "/" + recipe + "/")
    assert response.status_code == 200
    assert response.json["name"] == recipe
    assert response.json["owner"] == user

def test_get_nonexistent_user_recipe(client):

    user = "Eioletallaista"
    recipe = "Water-Recipe"

    client.post("/api/populate/", json={

    })
    response = client.get("/api/" + user + "/" + recipe + "/")
    #Test returns 404 since the user does not exist in the db
    assert response.status_code == 404

def test_get_recipeingredients(client):

    client.post("/api/populate/", json={

    })
    response = client.get("/api/recipeingredients/")
    assert response.status_code == 200

