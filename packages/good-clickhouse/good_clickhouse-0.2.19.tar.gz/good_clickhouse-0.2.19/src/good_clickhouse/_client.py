import os
import typing
import asyncio
from aioch import Client as AsyncClient
from clickhouse_driver import connect
from clickhouse_driver.dbapi.connection import Connection
from clickhouse_driver.dbapi.extras import NamedTupleCursor
from fast_depends import inject
from good_common.dependencies import AsyncBaseProvider, BaseProvider
from loguru import logger
from pydantic import Field, SecretStr, field_serializer
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConnectionProfile(BaseSettings):
    host: str = "localhost"
    port: int = 9000
    database: str = "default"
    user: str = "default"
    password: SecretStr | None = None
    secure: bool = False
    compression: bool = False

    @field_serializer("password", when_used="json")
    def dump_secret(self, v: SecretStr | None) -> str | None:
        if v is None:
            return None
        return v.get_secret_value()

    @classmethod
    def load_by_prefix(cls, prefix: str, config: typing.MutableMapping) -> typing.Self:
        config = {
            "host": config.get(f"{prefix}_HOST", "localhost"),
            "port": config.get(f"{prefix}_PORT", 9000),
            "database": config.get(f"{prefix}_DATABASE", "default"),
            "user": config.get(f"{prefix}_USER", "default"),
            "password": config.get(f"{prefix}_PASSWORD", None),
            "secure": config.get(f"{prefix}_SECURE", False)
            in (True, "True", "true", "yes", "1"),
            "compression": config.get(f"{prefix}_COMPRESSION", False)
            in (True, "True", "true", "yes", "1"),
        }
        return cls(**config)


class Clickhouse:
    def __init__(
        self,
        connection: Connection,
        wake: bool = False,
    ):
        self.connection = connection

        if wake:
            logger.info("Ensuring service is awake...")
            with self as cursor:
                cursor.execute("select 1")

    def __enter__(self) -> NamedTupleCursor:
        self.cursor = self.connection.cursor(cursor_factory=NamedTupleCursor)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        # self.connection.close()


class ClickhouseProvider(BaseProvider[Clickhouse], Clickhouse):
    def __init__(
        self,
        profile: str | None = None,
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
        secure: bool | None = None,
        compression: bool | None = None,
        # _debug: bool = False,
        wake: bool = False,
    ):
        super().__init__(
            profile=profile,
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            secure=secure,
            compression=compression,
            wake=wake,
        )

    def initializer(self, cls_args, cls_kwargs, fn_kwargs):
        # mode = {**cls_kwargs, **fn_kwargs}.get("profile", "cloud").upper()

        _allowable_args = {
            "dsn",
            "host",
            "port",
            "database",
            "user",
            "password",
            "secure",
            "compression",
        }

        kwargs = {**cls_kwargs, **fn_kwargs}

        profile_name = kwargs.pop("profile", None)

        if profile_name:
            profile = (
                "CLICKHOUSE_" + profile_name.upper()
                if "clickhouse" not in profile_name.lower()
                else profile_name
            )
            _overwrite_settings = {}
            for arg in kwargs.keys():
                if (
                    arg not in ("profile", "host", "port", "user", "password")
                    and kwargs.get(arg) is not None
                ):
                    _overwrite_settings[arg] = kwargs[arg]

            profile_args = ConnectionProfile.load_by_prefix(
                profile, os.environ
            ).model_dump(
                mode="json",
                exclude_none=True,
            )

            kwargs = {
                **profile_args,
                **_overwrite_settings,
            }
        # logger.info({k for k,v in kwargs.items() if k not in _allowable_args})
        kwargs = {
            k: v for k, v in kwargs.items() if k in _allowable_args and v is not None
        }

        return cls_args, kwargs

    @classmethod
    def provide(cls, *args, **kwargs) -> Clickhouse:
        wake = kwargs.pop("wake", False)
        return Clickhouse(connection=connect(**kwargs), wake=wake)


class ClickhouseAsync:
    @inject
    def __init__(
        self,
        sync_client: Clickhouse = ClickhouseProvider(),
        profile: str | None = None,
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
        secure: bool | None = None,
        compression: bool | None = None,
        wake: bool = False,
    ):
        self.connection = AsyncClient(_client=sync_client.connection._make_client())

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # await self.connection.disconnect()
        pass
        # await self.cursor.close()
        # await self.connection.close()


class ClickhouseAsyncProvider(AsyncBaseProvider[ClickhouseAsync], ClickhouseAsync):
    async def on_initialize(self, client, wake: bool = False, **kwargs):
        if wake:
            try:
                logger.info("Attempting to wake service...")
                async with asyncio.timeout(15):
                    async with client as cursor:
                        await cursor.execute("select 1")
            except asyncio.TimeoutError:
                logger.debug("Unable to wake service in less than 15 seconds...")
