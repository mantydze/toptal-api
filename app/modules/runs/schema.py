schema_register_user = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "minLength": 4},
        "password": {"type": "string", "minLength": 8}
    },
    "required": ["username", "password"],
    "additionalProperties": False
}