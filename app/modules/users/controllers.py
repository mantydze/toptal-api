""" users/controllers.py """

from app.modules.users.models import User
from app.utils.query_string import QueryString
from app.utils.query_builder import QueryBuilder
from app.utils.roles import Role

from flask import jsonify, request, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from sqlalchemy import or_
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden


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

    # Simple user can only see own profile
    if current_user.role == Role.USER and current_user.user_id != user_id:
        raise Forbidden()

    user = User.get_or_404(user_id)

    # Manager can only see own profile and other simple users
    if current_user.role == Role.MANAGER and current_user.user_id != user_id:
        if user.role != Role.USER:
            raise Forbidden()

    return jsonify(data=User.get_or_404(user_id).to_dict())


@users_route.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):

    user = User.get_or_404(user_id)

    # Get input JSON or raise BadRequest
    input_data = request.get_json(force=True)

    # Validate against schema

    # user.update(input_data)

    return jsonify(data=user.to_dict())
