""" auth/controllers.py
"""

from flask import jsonify, request
from flask.blueprints import Blueprint

from flask_login import login_required, login_user, logout_user

from app import login_manager
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


@login_manager.user_loader
def user_loader(username):
    """ Find User by given username
        Returns
        ------
        User (SAModel) if found. Otherwise None as Flask-Login requires
    """
    return User.query.filter_by(username=username).one_or_none()


@auth_route.route("/login", methods=["POST"])
def login():

    input_json = request.get_json(force=True)

    if not isinstance(input_json, dict):
        raise BadRequest("Request data must be a valid JSON")

    user = User.query.filter_by(username=input_json["username"]).one_or_none()

    if user and (user.password == User.encrypt_str(input_json["password"])):
        login_user(user)
    else:
        # Do not tell user what was wrong exactly to prevent password guessing
        raise BadRequest("Invalid login credentials")

    return "", 204


@auth_route.route("/logout")
@login_required
def logout():
    logout_user()
    return '', 204
