from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.utils.base_mixin import BaseMixin


class Record(db.Model, BaseMixin):

    __tablename__ = "RECORD"

    # List of attributes to serialize to JSON
    attrs = ["record_id", "create_time", "distance", "latitude", "longitude"]

    record_id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime, nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.String, nullable=False)
    longitude = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("USER.USER_ID"),
                        nullable=False)

    @hybrid_property
    def links(self):
        """ Links """

        links = {}
        links["self"] = url_for("records_route.get_record",
                                record_id=self.record_id,
                                _external=True)
        return links
