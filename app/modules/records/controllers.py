""" downtimes/controllers.py
"""

from flask import jsonify
from flask.blueprints import Blueprint
from app.modules.records.models import Record

records_route = Blueprint("records_route", __name__)


@records_route.route("/records")
def get_records():
    """ Return list of Records """

    return jsonify(records=Record.get_all())


@records_route.route("/records/<int:record_id>")
def get_record(record_id=None):
    """ Return Record by ID """

    return jsonify(record=Record.get_or_404(record_id))
