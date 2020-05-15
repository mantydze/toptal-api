""" downtimes/controllers.py
"""

from flask import jsonify
from flask.blueprints import Blueprint
from app.modules.runs.models import Run

runs_route = Blueprint("runs_route", __name__)


@runs_route.route("/runs")
def get_records():
    """ Return list of Runs """

    return jsonify(runs=Run.get_all())


@runs_route.route("/runs/<int:run_id>")
def get_run(run_id=None):
    """ Return Run by ID """

    return jsonify(run=Run.get_or_404(run_id).to_dict())
