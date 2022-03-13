from flask import current_app as app, request
from flask_restful import Resource

from ..models import db, Recipe
from ..db_creator_V2 import populate_db, get_db

class Populate(Resource):

    def __init__(self) -> None:
        super().__init__()

    def get(self):
        get_db()

    def post(self):
        db_exists = db.session.query(Recipe).first()
        if db_exists:
            return "Database is already populated", 409
        populate_db()
        return " ", 201