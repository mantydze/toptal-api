
import hashlib

from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property

from app import db
from app.utils.base_mixin import BaseMixin


class User(db.Model, BaseMixin):

    __tablename__ = "USER"

    # List of attributes to serialize to JSON
    attrs = ["user_id", "username", "role", "links"]

    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

    runs = db.relationship("Run", backref="user", lazy="dynamic")

    @hybrid_property
    def links(self):
        """ Links """

        links = {}
        links["self"] = url_for("users_route.get_user",
                                user_id=self.user_id,
                                _external=True)
        links["runs"] = url_for("users_route.get_user_runs",
                                user_id=self.user_id,
                                _external=True)

        return links

    @hybrid_property
    def base_url(self):
        """ URL to a route which returns list of objects """
        return url_for("users_route.get_users", _external=True)

    @staticmethod
    def create(input_json):
        """ Create new User. Set default role to user and encode password

            Parameters
            ----------
            input_json(dict): dictionary containing username and password

            Returns
            -------
            user (SAModel): newly created instance of User
        """

        try:
            # Default Role is user
            input_json["role"] = "user"

            # Do not store passwords in plaintext, encode with sha256
            phash = hashlib.sha256(input_json["password"].encode('utf-8'))
            input_json["password"] = phash.hexdigest()

            user = User(**input_json)

            db.session.add(user)
            db.session.commit()

            return user
        except:
            db.session.rollback()
            raise
