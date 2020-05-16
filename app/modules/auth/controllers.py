""" auth/controllers.py
"""

from flask import jsonify, request
from flask.blueprints import Blueprint

from app.modules.users.models import User
from app.modules.auth.schema import schema_register_user, schema_login_user
from app.utils.jsonschema_validator import validate

from werkzeug.exceptions import BadRequest

auth_route = Blueprint("auth_route", __name__)


@auth_route.route("/register", methods=["POST"])
def register():
    """ Register new User """

    input_json = request.get_json(force=True)

    if not isinstance(input_json, dict):
        raise BadRequest("Request data must be a valid JSON")

    # Validate input JSON if received data contains required attributes
    validate(input_json, schema_register_user)

    # Check if username is not already taken
    username = input_json["username"]
    user = User.query.filter_by(username=username).first()

    if user:
        raise BadRequest("Username '{}' is already taken".format(username))

    user = User.create(input_json)

    return jsonify(data=user.to_dict())


@auth_route.route("/login", methods=["POST"])
def login():
    """ Login User """

    raise NotImplemented()

@auth_route.route("/logout", methods=["GET"])
def logout():
    """ Logout User """

    raise NotImplemented()
