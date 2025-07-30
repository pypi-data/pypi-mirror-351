import asyncio

# from good_common.utilities.io import download_url_to_file, download_url_to_temp_file, decompress_tempfile
import typing
from typing import Any, ClassVar
from fast_depends import inject
import orjson
from good_common.modeling import TypeInfo
from good_common.types import UUIDField
from good_common.utilities import sort_object_keys
from loguru import logger
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

# from good_clickhouse import ClickhouseAsync
from good_clickhouse.query import (
    ClickhouseColumn,
)

from ._client import ClickhouseAsync, ClickhouseAsyncProvider

# from goodintel_core.models.entities import PersonName, OrganizationName, EntityName
# from goodintel_core.models.data import DataTable


class DataTable(BaseModel):
    uid: UUIDField
    _table_name_: ClassVar[str]

    @classmethod
    def model_all_fields(cls) -> dict[str, TypeInfo]:
        fields = cls.model_fields
        computed_fields: dict[str, Any] = cls.model_computed_fields

        all_fields = {}

        for key, field in fields.items():
            type_info = TypeInfo.annotation_extract_primary_type(field.annotation)
            all_fields[key] = type_info

        for key, field in computed_fields.items():
            type_info = TypeInfo.annotation_extract_primary_type(field.return_type)
            all_fields[key] = type_info

        return sort_object_keys(all_fields)

    def object_all_fields(self) -> dict[str, TypeInfo]:
        extra_fields: dict[str, Any] = {
            k: type(v) for k, v in (self.model_extra or {}).items()
        }

        all_fields = self.model_all_fields()

        for key, field in extra_fields.items():
            type_info = TypeInfo.annotation_extract_primary_type(field)
            all_fields[key] = type_info

        return sort_object_keys(all_fields)


T = typing.TypeVar("T", bound=DataTable)


def columns_from_model(
    model: T,
    exclude_columns: set | None = None,
    sort_order: list[str] | None = None,
    **kwargs,
) -> list[ClickhouseColumn]:
    if hasattr(model, "__exclude_columns__"):
        exclude_columns = exclude_columns or set()
        exclude_columns.update(model.__exclude_columns__)

    if hasattr(model, "__table_column_order__"):
        sort_order = sort_order or set()
        sort_order = model.__table_column_order__

    cols = [
        ClickhouseColumn(k, v, **kwargs)
        for k, v in (
            model.model_all_fields()
            if hasattr(model, "model_all_fields")
            else model.model_fields
        ).items()
        if not exclude_columns or k not in exclude_columns
    ]
    if sort_order:
        cols = sorted(
            cols,
            key=lambda x: sort_order.index(x.name) if x.name in sort_order else 999,
        )

    return cols


class PydanticCollection(typing.Generic[T]):
    def __init__(
        self,
        records: list[T],
        type: T,
        serializer: typing.Callable[[T], dict] = None,
        exclude_columns: set | None = None,
        **kwargs,
    ):
        self._type = type
        self._records = records
        self._kwargs = kwargs
        self._serializer = serializer
        self._exclude_columns = (exclude_columns or set()) | getattr(
            type, "__exclude_columns__", set()
        )
        # self._position = 0
        self._columns = None

    def __len__(self):
        return len(self._records)

    def __getitem__(self, key):
        return self.serialize_to_columns(self._records[key])

    @property
    def select(self):
        return ", ".join([col.name for col in self.columns])

    @property
    def columns(self):
        if not self._columns:
            _columns = columns_from_model(self._type, **self._kwargs)
            for col in _columns:
                if self._exclude_columns and col.name in self._exclude_columns:
                    _columns.remove(col)
            self._columns = _columns
        return self._columns

    def serialize_to_columns(self, obj: T) -> dict:
        if self._serializer:
            obj = self._serializer(obj)
            for key in self._exclude_columns:
                obj.pop(key, None)
        else:
            obj = (
                obj.model_export() if hasattr(obj, "model_export") else obj.model_dump()
            )
        for key in self._exclude_columns:
            obj.pop(key, None)
        for col in self.columns:
            if col.json_serialize:
                obj[col.name] = orjson.dumps(obj[col.name]).decode("utf-8")

        return obj

    def __iter__(self):
        for record in self._records:
            yield self.serialize_to_columns(record)

    def __next__(self):
        raise NotImplementedError


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
@inject
async def insert_into_clickhouse(
    database: str,
    table: str,
    records: PydanticCollection,
    client: ClickhouseAsync = ClickhouseAsyncProvider(),
):
    logger.info(f"inserting {len(records)} into {database}.{table}")
    async with client as cursor:
        try:
            await cursor.execute(
                f"insert into `{database}`.`{table}`({records.select}) settings async_insert=1, wait_for_async_insert=1 values ",
                list(records),
            )

            logger.info(f"inserted {len(records)} records")
            return len(records)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(e)

            return False
