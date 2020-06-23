""" usrs/models.py """
from app import db
from app.utils.base_mixin import BaseMixin


class BlackList(db.Model, BaseMixin):

    __tablename__ = "BLACKLIST"

    jti = db.Column(db.String, nullable=False, primary_key=True)

    @staticmethod
    def create(token):
        """ Create new blacklisted token

        Parameters
        ----------
        token(decoded token) : token to be blacklisted
        """

        try:
            black = BlackList()
            black.jti = token["jti"]
            db.session.add(black)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise
