""" utils/json_column.py """

import json
from sqlalchemy.ext import mutable
import sqlalchemy.types as types


class JsonColumn(types.TypeDecorator):
    """ Custom DataType based on String.
        Enables JSON storage by encoding and decoding on the fly """

    impl = types.String
    python_type = "json_column"

    def process_bind_param(self, value, dialect):
        return None if value is None else json.dumps(value, indent=None,
                                                     separators=(",", ":"))

    def process_result_value(self, value, dialect):
        return None if value is None else json.loads(value, strict=False)


mutable.MutableDict.associate_with(JsonColumn)
