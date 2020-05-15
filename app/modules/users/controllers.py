""" downtimes/controllers.py
"""

from flask import jsonify, request
from flask.blueprints import Blueprint
from app.modules.users.models import User
from app.modules.records.models import Record

from werkzeug.exceptions import BadRequest

users_route = Blueprint("users_route", __name__)


@users_route.route("/users")
def get_users():
    """ Return list of Users """

    return jsonify(users=User.get_all())


@users_route.route("/users/<int:user_id>")
def get_user(user_id):
    """ Return user by ID """
    return jsonify(user=User.get_or_404(user_id).to_dict())


@users_route.route("/users/<int:user_id>/records")
def get_user_records(user_id):
    """ Return Records by User ID """

    models = Record.query.filter_by(user_id=user_id).all()  # Query SA Models
    records = [model.to_dict() for model in models]          # Serialize JSON
    return jsonify(records=records)


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

    return jsonify(user=user.to_dict())
