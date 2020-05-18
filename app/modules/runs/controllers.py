""" users/controllers.py """

from flask import jsonify, request
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from app.modules.users.models import User
from app.modules.runs.models import Run
from app.modules.runs.schema import schema_create_run, schema_update_run
from app.utils.jsonschema_validator import validate
from app.utils.query_string import QueryString
from app.utils.query_builder import QueryBuilder
from app.utils.roles import Role
from werkzeug.exceptions import Forbidden

runs_route = Blueprint("runs_route", __name__)


@runs_route.route("/runs")
@login_required
def get_runs():
    """ Return list of Runs """

    qs = QueryString(request.query_string.decode("utf-8"))
    qs.parse()

    qb = QueryBuilder(qs, Run)
    qb.build_query()

    models = qb.q.all()
    runs = [model.to_dict() for model in models]    # Serialize JSON

    return jsonify(data=runs, links=qb.links)


@runs_route.route("/runs/<int:run_id>")
@login_required
def get_run(run_id=None):
    """ Return Run by ID """

    return jsonify(data=Run.get_or_404(run_id).to_dict())


@runs_route.route("/runs", methods=["POST"])
@login_required
def create():
    """ Create new Run """

    # Get input JSON or raise BadRequest
    input_json = request.get_json(force=True)

    # Validate input JSON or raise ValidationError
    validate(input_json, schema_create_run)

    user_id = input_json["user_id"]

    # Both USER and MANAGER can create only self owned Run entries
    # Only ADMIN can create Runs for others
    if (user_id != current_user.user_id) and (current_user.role != Role.ADMIN):
        raise Forbidden()

    # Check if User with given user_id exists at all
    User.get_or_404(user_id)

    input_json["weather"] = None
    run = Run.create(input_json)

    return jsonify(data=run.to_dict())


@runs_route.route("/runs/<int:run_id>", methods=["PUT"])
@login_required
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
    if (run.user_id != current_user.user_id) and \
            (current_user.role != Role.ADMIN):
        raise Forbidden()

    run.update(input_json)

    return jsonify(data=run.to_dict())


@runs_route.route("/runs/<int:run_id>", methods=["DELETE"])
@login_required
def delete(run_id):
    """ Delete existing Run """

    # Check if Run with given run_id exists at all
    run = Run.get_or_404(run_id)

    # Both USER and MANAGER can DELETE only self owned Run entries
    # Only ADMIN can DELETE Runs of others
    if (run.user_id != current_user.user_id) and \
            (current_user.role != Role.ADMIN):
        raise Forbidden()

    run.delete()

    return "", 204
