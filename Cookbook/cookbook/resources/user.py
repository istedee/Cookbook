import json
from flask import request, Response, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from jsonschema import validate, ValidationError
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter

from ..utils import create_error_response, RecipeBuilder
from .. import db
from ..models import User
from ..constants import *


class UserCollection(Resource):
    def get(self):
        body = RecipeBuilder(items=[])
        users = db.session.query(User).all()
        for u in users:
            data = RecipeBuilder(
                name=u.name, address=u.address, email=u.email, password=u.password
            )
            data.add_control("self", url_for("api.useritem", user=u.name))
            data.add_control("profile", USER_PROFILE)
            body["items"].append(data)
        body.add_control("self", href=url_for("api.usercollection"))
        body.add_control_add_user()
        body.add_namespace("cookbook", LINK_RELATIONS_URL)

        return Response(
            status=200,
            response=json.dumps(body, indent=4, separators=(",", ": ")),
            mimetype=MASON,
        )

    def post(self):
        if not request.json:
            return create_error_response(
                415, "Not JSON", "Request content type must be JSON"
            )
        try:
            validate(request.json, User.json_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON", str(e))
        try:
            u_name = request.json["name"]
            user_i = User.query.filter_by(name=u_name).first()
            if user_i:
                return create_error_response(409, "ON JO", "Duplicate 🥝")
            u_address = request.json["address"]
            u_email = request.json["email"]
            u_password = request.json["password"]
            if (
                not isinstance(u_address, str)
                or not isinstance(u_email, str)
                or not isinstance(u_password, str)
            ):
                return create_error_response(400, "Invalid values")
        except KeyError:
            return create_error_response(400, "KeyError")
        try:
            new_user = User(
                name=u_name, address=u_address, email=u_email, password=u_password
            )
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Duplicate", "Database error")

        return Response(
            status=201,
            mimetype=MASON,
            headers={"Location": url_for("api.useritem", user=new_user.name)},
        )


class UserItem(Resource):
    def get(self, user):
        user_i = db.session.query(User).filter_by(name=user.name).first()
        if not user_i:
            return create_error_response(404, "User not found")

        data = RecipeBuilder(
            name=user_i.name,
            address=user_i.address,
            email=user_i.email,
            password=user_i.password,
        )
        data.add_namespace("storage", LINK_RELATIONS_URL)
        data.add_control("self", url_for("api.useritem", user=user_i.name))
        data.add_control("profile", href=USER_PROFILE)
        data.add_control("collection", url_for("api.usercollection"))
        data.add_control(
            "user-recipes", url_for("api.recipecollection", user=user_i.name)
        )
        data.add_control_edit_user(user.name)
        data.add_control_delete_user(user.name)

        return Response(
            json.dumps(data, indent=4, separators=(",", ": ")),
            status=200,
            mimetype=MASON,
        )

    def put(self, user):
        user_i = db.session.query(User).filter_by(name=user.name).first()
        if not user_i:
            return create_error_response(404, "User not found")
        if not request.json:
            return create_error_response(415, "Wrong content", "Should be JSON")
        try:
            validate(request.json, User.json_schema())
        except ValidationError:
            return create_error_response(400, "Invalid content", "Validation fails")
        user_i.name = request.json["name"]
        user_i.address = request.json.get("address", "")
        user_i.email = request.json["email"]
        user_i.password = request.json["password"]
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return create_error_response(status_code=409, title="Taken")
        return Response(status=204, mimetype=MASON)

    def delete(self, user):
        user_i = db.session.query(User).filter_by(name=user.name).first()
        if not user_i:
            return create_error_response(404, "Not Found", "User not found")

        db.session.delete(user_i)
        db.session.commit()
        return Response(status=204, mimetype=MASON)


class UserConverter(BaseConverter):
    def to_python(self, user):
        db_user = db.session.query(User).filter_by(name=user).first()
        if db_user is None:
            raise NotFound
        return db_user

    def to_url(self, db_user):
        return str(db_user)
