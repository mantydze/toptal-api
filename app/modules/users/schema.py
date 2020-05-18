schema_create_user = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "minLength": 4, "maxLength": 20},
        "password": {"type": "string", "minLength": 4, "maxLength": 20}
    },
    "required": ["username", "password"],
    "additionalProperties": False
}

schema_update_user = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "minLength": 4, "maxLength": 20},
        "password": {"type": "string", "minLength": 4, "maxLength": 20}
    },
    "additionalProperties": False
}
