""" users/controllers.py
"""

from flask import jsonify, request
from flask.blueprints import Blueprint
from app.modules.runs.models import Run
from app.utils.query_string import QueryString
from app.utils.query_builder import QueryBuilder

runs_route = Blueprint("runs_route", __name__)


@runs_route.route("/runs")
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
def get_run(run_id=None):
    """ Return Run by ID """

    return jsonify(data=Run.get_or_404(run_id).to_dict())
