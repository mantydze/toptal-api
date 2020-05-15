from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.utils.base_mixin import BaseMixin


class User(db.Model, BaseMixin):

    __tablename__ = "USER"

    # List of attributes to serialize to JSON
    attrs = ["user_id", "username", "role", "links"]

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

    @hybrid_property
    def links(self):
        """ Links """

        links = {}
        links["self"] = url_for("users_route.get_user",
                                user_id=self.user_id,
                                _external=True)
        return links
