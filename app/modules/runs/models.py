from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.utils.base_mixin import BaseMixin


class Run(db.Model, BaseMixin):

    __tablename__ = "RUN"

    # List of attributes to serialize to JSON
    attrs = ["run_id", "create_time", "distance", "latitude", "longitude",
             "user_id", "links"]

    run_id = db.Column(db.Integer, nullable=False, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.String, nullable=False)
    longitude = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("USER.user_id"),
                        nullable=False)

    @hybrid_property
    def links(self):
        """ Links """

        links = {}
        links["self"] = url_for("runs_route.get_run", run_id=self.run_id,
                                _external=True)

        links["user"] = url_for("users_route.get_user", user_id=self.user_id,
                                _external=True)

        return links

    @hybrid_property
    def base_url(self):
        """ URL to a route which returns list of objects """
        return url_for("runs_route.get_runs", _external=True)
