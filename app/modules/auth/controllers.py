""" auth/controllers.py
"""

from flask import jsonify, request
from flask.blueprints import Blueprint

from flask_jwt_extended import jwt_required, create_access_token, get_raw_jwt

from app import jwt
from app.modules.auth.models import BlackList
from app.modules.users.models import User
from app.modules.auth.schema import schema_login_user
from app.utils.jsonschema_validator import validate

from werkzeug.exceptions import BadRequest

auth_route = Blueprint("auth_route", __name__)


@jwt.user_loader_callback_loader
def user_loader(identity):
    """ Load User by given username
        Returns
        ------
        User (SAModel) if found. Otherwise None as Flask-Login requires """
    return User.query.filter_by(username=identity).one_or_none()


@jwt.token_in_blacklist_loader
def in_blacklist(token):
    """ Check if token is not revoked """
    return BlackList.get(token["jti"]) is not None


@auth_route.route("/login", methods=["POST"])
def login():
    """ Login User with given credentials """

    # Get input JSON or raise BadRequest
    input_json = request.get_json(force=True)

    # Validate input JSON or raise ValidationError
    validate(input_json, schema_login_user)

    user = User.query.filter_by(username=input_json["username"]).one_or_none()

    if user and (user.password == User.encrypt_str(input_json["password"])):
        pass
    else:
        # Do not tell user what was wrong exactly to prevent password guessing
        raise BadRequest("Invalid login credentials")

    data = user.to_dict()
    data["access_token"] = create_access_token(identity=user.username)

    return jsonify(data=data)


@auth_route.route("/logout")
@jwt_required
def logout():
    """ Logout current user, revoke and blacklist active token """
    BlackList.create(get_raw_jwt())
    return '', 204
