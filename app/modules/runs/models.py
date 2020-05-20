from datetime import datetime
from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property
from app import db
from app.utils.base_mixin import BaseMixin
from app.utils.json_column import JsonColumn
from app.utils.weather_api import get_weather


class Run(db.Model, BaseMixin):

    __tablename__ = "RUN"

    # List of attributes to serialize to JSON
    public = ["run_id", "date", "distance", "duration", "latitude",
              "longitude", "weather", "user_id", "isoweek"]  # , "links"]

    run_id = db.Column(db.Integer, nullable=False, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    isoweek = db.Column(db.Integer, nullable=False)     # for building repors
    duration = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    weather = db.Column(JsonColumn)
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

    @staticmethod
    def create(input_json, save=True, commit=True):
        """ Create new Run. Fetch weather

            Parameters
            ----------
            input_json(dict): dictionary containing username and password
            save(bool): should model be saved or not
            commit(bool): should model be commited or not

            Returns
            -------
            user (SAModel): newly created instance of Run
        """

        input_json["weather"] = None

        try:
            input_json["date"] = datetime.strptime(
                input_json["date"], "%Y-%m-%d")

            input_json["isoweek"] = input_json["date"].isocalendar()[1]

            # Get weather condition from Weather API. Returns JSON or None
            input_json["weather"] = get_weather(input_json["latitude"],
                                                input_json["longitude"])

            run = Run(**input_json)

            if save:
                db.session.add(run)

            if commit:
                db.session.commit()

            return run
        except Exception:
            db.session.rollback()
            raise

    def update(self, input_json, commit=True):
        """ Update Run. Fetch weather if coordinates are updated

            Parameters
            ----------
            input_json(dict): dictionary containing attributes to update
            commit(bool): should model be commited or not
        """

        try:
            if "date" in input_json:
                self.date = datetime.strptime(input_json["date"], "%Y-%m-%d")
                self.isoweek = self.date.isocalendar()[1]

            if "distance" in input_json:
                self.distance = input_json["distance"]

            if "duration" in input_json:
                self.duration = input_json["duration"]

            coords_changed = False
            if "latitude" in input_json:
                self.latitude = input_json["latitude"]
                coords_changed = True

            if "longitude" in input_json:
                self.longitude = input_json["longitude"]
                coords_changed = True

            if coords_changed or self.weather is None:
                self.weather = get_weather(self.latitude, self.longitude)

            if commit:
                db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    def delete(self):
        """ Delete current Run """

        try:
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
