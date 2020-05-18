""" init.py
"""

import time
import traceback
import sqlalchemy
import flask_login

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import InternalServerError, HTTPException
from app.utils.config_loader import load_config

db = SQLAlchemy()
toolbar = DebugToolbarExtension()
login_manager = flask_login.LoginManager()


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

    # Login Manager
    login_manager.init_app(app)

    # Index page
    @app.route("/")
    def index():
        """ Index page """
        return jsonify({"hello": "world"})

    @app.errorhandler(sqlalchemy.exc.OperationalError)
    def handle_validation_error(e):
        """ Database Error """
        traceback.print_exc()
        e.code = 400
        e.description = "Database Error"
        return handle_error(e)

    @app.errorhandler(Exception)
    def handle_exception(e):
        """ Any unhandled exceptions """
        traceback.print_exc()
        e = InternalServerError
        return handle_error(e)

    from app.modules.auth.controllers import auth_route
    from app.modules.users.controllers import users_route
    from app.modules.runs.controllers import runs_route

    app.register_blueprint(auth_route)
    app.register_blueprint(users_route)
    app.register_blueprint(runs_route)

    return app
