""" utils/base_mixin.py """

import datetime
from werkzeug.exceptions import NotFound


class BaseMixin(object):
    """ BaseMixin class provides basic GETs and simple serialization """

    def to_dict(self):
        """ Convert SA Model into a dictionary. Does not serialize relationships

            Returns
            -------
            result (dict) - SA Model serialized into JSON
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

            Parameters
            ----------
            primary_key - primary key of an instance

            Returns
            -------
            obj (SAModel)

            Retursn None if instance is not found  """

        return cls.query.get(primary_key)

    @classmethod
    def get_or_404(cls, primary_key):
        """ Return an instance based on the given primary key identifier

            Parameters
            ----------
            primary_key - primary key of an instance

            Returns
            -------
            obj (SAModel)

            Raises NotFound(404) if instance is not found  """

        obj = cls.get(primary_key)
        if obj is None:
            raise NotFound("{} not found".format(cls.__name__))

        return obj
