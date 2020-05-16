
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
    username = db.Column(db.String, nullable=False, unique=True, index=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    authenticated = db.Column(db.Boolean, default=False)

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
    def encrypt_str(s):
        """ Encrypts given string into sha256 hex hash """
        return hashlib.sha256(s.encode('utf-8')).hexdigest()

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
            input_json["password"] = User.encrypt_str(input_json["password"])

            user = User(**input_json)

            db.session.add(user)
            db.session.commit()

            return user
        except:
            db.session.rollback()
            raise

    # Login Manager

    def is_active(self):
        """ Returns always True. Assume that all users are active """
        print("kviecia is_active ")
        return True

    def get_id(self):
        """ Returns unique identifier """
        print("kviecia get_id ")
        return self.username

    def is_authenticated(self):
        """ Returns True if the user is authenticated """
        print("kviecia is_auth")
        return self.authenticated

    def is_anonymous(self):
        """ Anonymous usage of this API is not supported """
        print("kviecia is_anon ")
        return False
