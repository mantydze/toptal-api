""" utils/base_mixin.py
"""

import datetime
from werkzeug.exceptions import NotFound


class BaseMixin(object):
    """ BaseMixin class provides basic GETs and simple serialization """

    def to_dict(self):
        """ Convert SA Model into a dictionary. Does not serialize relationships
        """

        # List public attributes to export. Use all available if not specified
        attrs = getattr(self.__class__, "public", self.__mapper__.c.keys())

        result = {}

        for attr in attrs:
            if hasattr(self, attr):

                value = getattr(self, attr)

                if isinstance(value, datetime.date):
                    # Convert Timestamp into ISO format for better readability
                    value = value.isoformat()

                result[attr] = value

        return result

    @classmethod
    def get(cls, primary_key):
        """ Return an instance based on the given primary key identifier
            or None if not found.
        """
        return cls.query.get(primary_key)

    @classmethod
    def get_or_404(cls, primary_key):
        """ Return an instance based on the given primary key identifier
            or raises 404 if not found.
        """

        obj = cls.get(primary_key)
        if obj is None:
            error_msg = "{} not found".format(cls.__name__)

            raise NotFound(error_msg)

        return obj

    @classmethod
    def get_all(cls):
        """ Return all instances of a given class

            Parameters
            ----------
            cls (sqlachemy.Model)

            Returns
            -------
            data (dict): Result set exported into a valid JSON
            fiedsl (list): projection, list of fields to export
        """

        # Parse request query string (URL)
        # qs = QueryString(request.query_string.decode("utf-8"), cls.fields)
        # qs.parse()

        # Build SA query and apply parsed QueryString
        # qb = QueryBuilder(qs, cls)
        # qb.build_query()

        # Build Response object (JSON) using QueryBuilder (resultset is list)
        # return jsonapify_set(qb)

        return [obj.to_dict() for obj in cls.query.all()]
