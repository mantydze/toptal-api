""" init.py
"""

import os
import sys
import json
import time
import argparse
import traceback
import sqlalchemy

from flask import g, Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import InternalServerError, HTTPException


db = SQLAlchemy()
toolbar = DebugToolbarExtension()


def load_config():
    """ Load config from given config_path

        Returns
        -------
        config (dict) - parsed config JSON

        Raise Exception if file not found or not valid JSON
    """

    # Initialize argument parser
    parser = argparse.ArgumentParser()
    # Expect one argumument
    parser.add_argument("--config_path", required=True, type=str,
                        default=None, help="path to configuration json file")
    args = parser.parse_args()

    # Value of argument
    config_path = args.config_path

    # Check if configuration file exists
    if not os.path.isfile(config_path):
        sys.exit("Configuration file [%s] does not exist" % config_path)

    # Load JSON from file
    try:
        with open(config_path, "r") as fh:
            return json.load(fh)
    except Exception:
        sys.exit("Configuration file is not a valid json")


def handle_error(error):
    """ JSONAPI envelope for processing errors
    """

    detail = ""
    code = error.code if hasattr(error, "code") else 500

    # In some cases error may have both 'message' and 'description'
    # One of them is empty and other contains actual description
    if hasattr(error, "description"):
        detail = error.description

    elif not detail and hasattr(error, "message"):
        detail = error.message

    else:
        detail = "Unknown"

    e = {
        "status": code,
        "title": error.__class__.__name__,
        "detail": detail.replace("\n", " ").replace("  ", "")
    }

    ret = {"errors": [e]}

    return jsonify(ret), code


def create_app():

    app = Flask(__name__)

    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, handle_error)

    app.url_map.strict_slashes = False

    # oms-crud-api config
    app.config.from_mapping(load_config())

    # Debug Toolbar (Only for development)
    toolbar.init_app(app)

    # SQLAlchemy
    db.init_app(app)

    # Index page
    @app.route("/")
    def index():
        """ Index page """

        return jsonify({"hello": "world"})

    @app.before_request
    def app_before_request():
        """ """

        # Create a method to measure time taken for a request
        g.req_start = time.time()
        g.request_time = lambda: round((time.time() - g.req_start) * 1000.0, 2)

        # Print request payload of every request which is manipulating data
        if request.method in ["PUT", "POST", "DELETE"]:
            print(request.data)

    @app.errorhandler(sqlalchemy.exc.OperationalError)
    def handle_validation_error(e):
        """ Database Error """
        traceback.print_exc()
        e.code = 400
        e.description = "Action is not supported for this database dialect."
        return handle_error(e)

    @app.errorhandler(Exception)
    def handle_exception(e):
        """ Any unhandled exceptions """
        traceback.print_exc()
        e = InternalServerError
        return handle_error(e)

    from app.modules.users.controllers import users_route
    from app.modules.records.controllers import records_route

    app.register_blueprint(users_route)
    app.register_blueprint(records_route)

    return app
