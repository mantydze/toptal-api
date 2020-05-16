""" utils/jsonschema_validator.py
"""
import jsonschema
from werkzeug.exceptions import BadRequest, InternalServerError


def validate(input_json, schema):
    """ Validates a parsed JSON document against the provided schema.
        Removes unknown properties (not defined in schema)
        If an error is found a ValidationError is raised.
    """

    try:
        jsonschema.validate(input_json, schema)
    except jsonschema.SchemaError:
        raise InternalServerError("Server Error: Request cannot be fulfilled")
    except jsonschema.ValidationError as ve:
        raise BadRequest("Validation Error: {}".format(ve.message))
