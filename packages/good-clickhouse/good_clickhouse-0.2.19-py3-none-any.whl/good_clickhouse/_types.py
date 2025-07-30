from pydantic_core import CoreSchema, core_schema
from pydantic import GetCoreSchemaHandler
from typing import Any


class JsonDict(dict):
    """
    A dictionary that can be serialized to JSON.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"JsonDict({super().__repr__()})"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(dict))
