import json
from typing import Any, Dict, List, Union

from pydantic import ValidationError
from pydantic.json import pydantic_encoder


class ExclusiveFieldError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class RequestValidationError(Exception):
    def __init__(self, validation_error: ValidationError) -> None:
        self.validation_error = validation_error

    def errors(self) -> List[Dict[str, Any]]:
        return self.validation_error.errors()

    def json(self, *, indent: Union[None, int, str] = 2) -> str:
        return json.dumps(self.errors(), indent=indent, default=pydantic_encoder)

    @staticmethod
    def schema() -> dict:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "loc": {
                        "title": "Loc",
                        "description": "error field",
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "type": {
                        "title": "Type",
                        "description": "error type",
                        "type": "string",
                    },
                    "msg": {
                        "title": "Msg",
                        "description": "error message",
                        "type": "string",
                    },
                },
                "required": ["loc", "type", "msg"],
            },
        }
