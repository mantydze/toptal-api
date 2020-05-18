schema_create_run = {
    "type": "object",
    "properties": {
        "user_id": {"type": "number"},
        "date": {"type": "string", "format": "date"},
        "duration": {"type": "number"},
        "distance": {"type": "number"},
        "latitude": {"type": "number", "minimum": -90, "maximum": 90},
        "longitude": {"type": "number", "minimum": -180, "maximum": 180}
    },
    "required": ["user_id", "date", "duration", "distance",
                 "latitude", "longitude"],
    "additionalProperties": False
}

schema_update_run = {
    "type": "object",
    "properties": {
        "date": {"type": "string", "format": "date"},
        "duration": {"type": "number"},
        "distance": {"type": "number"},
        "latitude": {"type": "number", "minimum": -90, "maximum": 90},
        "longitude": {"type": "number", "minimum": -180, "maximum": 180}
    },
    "additionalProperties": False
}
