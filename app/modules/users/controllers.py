""" users/controllers.py """

from app.modules.users.models import User
from app.utils.query_string import QueryString
from app.utils.query_builder import QueryBuilder
from app.utils.roles import Role
from app.modules.users.schema import schema_create_user, schema_update_user
from app.utils.jsonschema_validator import validate
from flask import jsonify, request, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from sqlalchemy import or_
from werkzeug.exceptions import BadRequest, Forbidden


users_route = Blueprint("users_route", __name__)


@users_route.route("/users")
@login_required
def get_users():
    """ Return list of Users depending on privileges User has.
        USER is redirected to own profile
        MANAGER sees own profile and other Users
        ADMIN sees all Users """

    # Simple user is redirected to see own profile
    if current_user.role == Role.USER:
        return redirect(url_for("users_route.get_user",
                                user_id=current_user.user_id))

    # Parse Query String and build a query
    qs = QueryString(request.query_string.decode("utf-8"))
    qs.parse()

    qb = QueryBuilder(qs, User)
    qb.build_query(apply_pagination=False)

    # Manager can only see own profile and other simple users
    if current_user.role == Role.MANAGER:
        qb.q = qb.q.filter(or_(User.user_id == current_user.user_id,
                               User.role == Role.USER))

    qb._apply_pagination()

    models = qb.q.all()
    users = [model.to_dict() for model in models]    # Serialize JSON

    return jsonify(data=users, links=qb.links)


@users_route.route("/users/<int:user_id>")
@login_required
def get_user(user_id):
    """ Return User by ID """

    # USER can only READ own profile
    if current_user.role == Role.USER and current_user.user_id != user_id:
        raise Forbidden()

    user = User.get_or_404(user_id)

    # MANAGER can only READ own profile and other simple USERs
    if current_user.role == Role.MANAGER and current_user.user_id != user_id:
        if user.role != Role.USER:
            raise Forbidden()

    return jsonify(data=User.get_or_404(user_id).to_dict())


@users_route.route("/register", methods=["POST"])
@users_route.route("/users", methods=["POST"])
def create():
    """ Register/Create new User """

    # Get input JSON or raise BadRequest
    input_json = request.get_json(force=True)

    # Validate input JSON or raise ValidationError
    validate(input_json, schema_create_user)

    # Check if username is not already taken
    username = input_json["username"]
    user = User.query.filter_by(username=username).one_or_none()

    if user:
        raise BadRequest("Username '{}' is already taken".format(username))

    user = User.create(input_json)

    return jsonify(data=user.to_dict())


@users_route.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    """ Update User """

    # Get input JSON or raise BadRequest
    input_json = request.get_json(force=True)

    # Validate input JSON or raise ValidationError
    validate(input_json, schema_update_user)

    # USER can only UPDATE own profile
    if current_user.role == Role.USER and current_user.user_id != user_id:
        raise Forbidden()

    user = User.get_or_404(user_id)

    # MANAGER can only UPDATE own profile and other simple USERs
    if current_user.role == Role.MANAGER and current_user.user_id != user_id:
        if user.role != Role.USER:
            raise Forbidden()

    if "username" in input_json and user.username != input_json["username"]:
        # Username to be updated. Check if username is not already taken
        username = input_json["username"]
        duplicate = User.query.filter_by(username=username).one_or_none()

        if duplicate:
            raise BadRequest("Username '{}' is already taken".format(username))

    user.update(input_json)

    return jsonify(data=user.to_dict())


@users_route.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete(user_id):
    """ Delete User """

    # USER can only DELETE own profile
    if current_user.role == Role.USER and current_user.user_id != user_id:
        raise Forbidden()

    user = User.get_or_404(user_id)

    # MANAGER can only DELETE own profile and other simple USERs
    if current_user.role == Role.MANAGER and current_user.user_id != user_id:
        if user.role != Role.USER:
            raise Forbidden()

    user.delete()

    return "", 204
