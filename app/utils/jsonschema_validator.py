""" utils/jsonschema_validator.py """

import jsonschema
from jsonschema import draft7_format_checker
from werkzeug.exceptions import BadRequest, InternalServerError


def validate(input_json, schema):
    """ Validates a parsed JSON document against the provided schema.
        Raises
            InternalServerError if schema is invalid
            BadRequest if input json is not valid against given schema
    """

    try:
        jsonschema.validate(input_json, schema,
                            format_checker=draft7_format_checker)
    except jsonschema.SchemaError:
        raise InternalServerError("Server Error: Request cannot be fulfilled")
    except jsonschema.ValidationError as ve:
        raise BadRequest("Validation Error: {}".format(ve.message))
