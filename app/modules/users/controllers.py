""" users/controllers.py
"""

from flask import jsonify, request
from flask.blueprints import Blueprint
from app.modules.users.models import User
from app.utils.query_string import QueryString
from app.utils.query_builder import QueryBuilder
from werkzeug.exceptions import BadRequest


users_route = Blueprint("users_route", __name__)


@users_route.route("/users")
def get_users():
    """ Return list of Users """

    qs = QueryString(request.query_string.decode("utf-8"))
    qs.parse()

    qb = QueryBuilder(qs, User)
    qb.build_query()

    models = qb.q.all()
    users = [model.to_dict() for model in models]    # Serialize JSON

    return jsonify(data=users, links=qb.links)


@users_route.route("/users/<int:user_id>")
def get_user(user_id):
    """ Return User by ID """

    return jsonify(data=User.get_or_404(user_id).to_dict())


@users_route.route("/users/<int:user_id>/runs")
def get_user_runs(user_id):
    """ Return Runs by User ID """

    user = User.get_or_404(user_id)

    models = user.runs.all()                        # Query SA Models
    runs = [model.to_dict() for model in models]    # Serialize JSON

    return jsonify(data=runs)


@users_route.route("/users", methods=["POST"])
def create_user():
    pass


@users_route.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):

    user = User.get_or_404(user_id)

    input_data = request.get_json(force=True)

    if not isinstance(input_data, dict):
        raise BadRequest("Request data must be a valid JSON")

    # Validate against schema

    # user.update(input_data)

    return jsonify(data=user.to_dict())
