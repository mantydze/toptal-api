""" init.py
"""

import traceback
import sqlalchemy
from flask_jwt_extended import (
    JWTManager, jwt_required, current_user, get_jwt_identity, jwt_optional)
from flask import Flask, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import InternalServerError, HTTPException
from app.utils.config_loader import load_config

db = SQLAlchemy()
toolbar = DebugToolbarExtension()
jwt = JWTManager()


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
    jwt.init_app(app)

    @app.before_first_request
    def create_db_schema():
        from flask import current_app
        with current_app.app_context():
            db.create_all()

    # Index page
    @app.route("/")
    @jwt_optional
    def index():
        """ Index page """
        if get_jwt_identity() is None:
            ret = {"message": "Hello anonymous, please register or login"}
        else:
            ret = {"message": "Hello {}".format(current_user.username)}
            ret["links"] = {
                "whoami": url_for("whoami", _external=True),
                "users": url_for("users_route.get_users", _external=True),
                "runs": url_for("runs_route.get_runs", _external=True)
            }

        return jsonify(ret)

    @app.route("/whoami")
    @jwt_required
    def whoami():
        """Little bit redundant endpoint, but still nice to have"""
        return jsonify(current_user.to_dict())

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
