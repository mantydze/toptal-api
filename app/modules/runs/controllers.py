""" users/controllers.py """

from werkzeug.exceptions import Forbidden
from app.utils.roles import Role
from app.utils.query_builder import QueryBuilder
from app.utils.query_string import QueryString
from app.utils.jsonschema_validator import validate
from flask import jsonify, request
from flask.blueprints import Blueprint
from flask_jwt_extended import jwt_required, current_user
from app.modules.users.models import User
from app.modules.runs.models import Run
from app.modules.runs.schema import schema_create_run, schema_update_run

runs_route = Blueprint("runs_route", __name__)


@runs_route.route("/runs")
@jwt_required
def get_runs():
    """ Return list of Runs """

    qs = QueryString(request.query_string.decode("utf-8"))
    qs.parse()

    qb = QueryBuilder(qs, Run)
    qb.build_query(apply_pagination=False)

    # Both USER and MANAGER can READ only self owned Run entries
    # Only ADMIN can READ Runs of others
    if current_user.role != Role.ADMIN:
        qb.q = qb.q.filter(Run.user_id == current_user.user_id)

    qb._apply_pagination()
    models = qb.q.all()
    runs = [model.to_dict() for model in models]   # Serialize Models into JSON

    return jsonify(data=runs, links=qb.links)


@runs_route.route("/users/<int:user_id>/runs")
@jwt_required
def get_user_runs(user_id):
    """ Return list of User Runs """

    # Check if user exists
    User.get_or_404(user_id)

    # Both USER and MANAGER can READ only self owned Run entries
    # Only ADMIN can READ Runs of others
    if user_id != current_user.user_id and current_user.role != Role.ADMIN:
        raise Forbidden()

    qs = QueryString(request.query_string.decode("utf-8"))
    qs.parse()

    qb = QueryBuilder(qs, Run)
    qb.build_query(apply_pagination=False)

    qb.q = qb.q.filter(Run.user_id == user_id)

    qb._apply_pagination()

    models = qb.q.all()
    runs = [model.to_dict() for model in models]   # Serialize Models into JSON

    return jsonify(data=runs, links=qb.links)


@runs_route.route("/runs/<int:run_id>")
@jwt_required
def get_run(run_id=None):
    """ Return Run by ID """

    run = Run.get_or_404(run_id)

    # Both USER and MANAGER can DELETE only self owned Run entries
    # Only ADMIN can DELETE Runs of others
    if run.user_id != current_user.user_id and current_user.role != Role.ADMIN:
        raise Forbidden()

    return jsonify(data=run.to_dict())


@runs_route.route("/runs", methods=["POST"])
@jwt_required
def create():
    """ Create new Run """

    # Get input JSON or raise BadRequest
    input_json = request.get_json(force=True)

    # Validate input JSON or raise ValidationError
    validate(input_json, schema_create_run)

    user_id = input_json["user_id"]

    # Both USER and MANAGER can CREATE only self owned Run entries
    # Only ADMIN can CREATE Runs for others
    if user_id != current_user.user_id and current_user.role != Role.ADMIN:
        raise Forbidden()

    # Check if User with given user_id exists at all
    User.get_or_404(user_id)

    run = Run.create(input_json)

    return jsonify(data=run.to_dict()), 201


@runs_route.route("/users/<int:user_id>/runs", methods=["POST"])
@jwt_required
def create_user_run(user_id):
    """ Create new Run for a user"""

    # Check if User with given user_id exists at all
    User.get_or_404(user_id)

    # Both USER and MANAGER can CREATE only self owned Run entries
    # Only ADMIN can CREATE Runs for others
    if user_id != current_user.user_id and current_user.role != Role.ADMIN:
        raise Forbidden()

    # Get input JSON or raise BadRequest
    input_json = request.get_json(force=True)

    input_json["user_id"] = user_id

    # Validate input JSON or raise ValidationError
    validate(input_json, schema_create_run)

    run = Run.create(input_json)

    return jsonify(data=run.to_dict()), 201


@runs_route.route("/runs/<int:run_id>", methods=["PUT"])
@jwt_required
def update(run_id):
    """ Update existing Run """

    # Get input JSON or raise BadRequest
    input_json = request.get_json(force=True)

    # Validate input JSON or raise ValidationError
    validate(input_json, schema_update_run)

    # Check if Run with given run_id exists at all
    run = Run.get_or_404(run_id)

    # Both USER and MANAGER can UPDATE only self owned Run entries
    # Only ADMIN can UPDATE Runs of others
    if run.user_id != current_user.user_id and current_user.role != Role.ADMIN:
        raise Forbidden()

    run.update(input_json)

    return jsonify(data=run.to_dict())


@runs_route.route("/runs/<int:run_id>", methods=["DELETE"])
@jwt_required
def delete(run_id):
    """ Delete existing Run """

    # Check if Run with given run_id exists at all
    run = Run.get_or_404(run_id)

    # Both USER and MANAGER can DELETE only self owned Run entries
    # Only ADMIN can DELETE Runs of others
    if run.user_id != current_user.user_id and current_user.role != Role.ADMIN:
        raise Forbidden()

    run.delete()

    return "", 204
