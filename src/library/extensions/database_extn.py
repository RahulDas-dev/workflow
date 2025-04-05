from pathlib import Path
from typing import Any, Type

from quart import Quart
from quart.globals import app_ctx
from sqlalchemy import URL, QueuePool, StaticPool, engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


def _app_ctx_id() -> int:
    """Get the id of the current Flask application context for the session scope."""
    return id(app_ctx)


class SqlAlchemy:
    def __init__(
        self,
        app: Quart | None = None,
        session_options: dict[str, Any] | None = None,
        model_class: Type[DeclarativeBase] | None = None,
    ) -> None:
        self._session_options = {} if session_options is None else session_options
        self._model = model_class if model_class is not None else DeclarativeBase
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Quart) -> None:
        if "sqlalchemy" in app.extensions:
            raise RuntimeError("A 'SqlAlchemy' instance has already been registered on this Quart app.")

        app.extensions["sqlalchemy"] = self
        app.teardown_appcontext(self._teardown_session_with_exception)

        # Default configuration
        basic_uri: str | URL | None = app.config.setdefault("SQLALCHEMY_DATABASE_URI", None)
        if not basic_uri:
            raise RuntimeError("'SQLALCHEMY_DATABASE_URI' must be set.")
        engine_options: dict[str, Any] = app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
        echo: bool = app.config.setdefault("SQLALCHEMY_ECHO", False)
        engine_options.setdefault("echo", echo)
        engine_options.setdefault("echo_pool", echo)
        engine_options["url"] = basic_uri
        self._apply_driver_defaults(engine_options, app)
        url_: str | URL = engine_options.pop("url")
        self._engine = create_async_engine(url_, **engine_options)
        self._session = self._make_scoped_session(self._session_options)

    @property
    def session(self) -> async_scoped_session[AsyncSession]:
        return self._session

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    def _apply_driver_defaults(self, options: dict[str, Any], app: Quart) -> None:
        url = engine.make_url(options["url"])

        if url.drivername in {"sqlite", "sqlite+pysqlite"}:
            if url.database is None or url.database in {"", ":memory:"}:
                options["poolclass"] = StaticPool
                options.setdefault("connect_args", {})
                options["connect_args"]["check_same_thread"] = False
            else:
                is_uri = url.query.get("uri", False)
                db_str = url.database[5:] if is_uri else url.database
                if not Path(db_str).is_absolute():
                    Path(app.instance_path).mkdir(exist_ok=True)
                    db_str = Path(app.instance_path) / Path(db_str)
                    db_str = f"file:{db_str}" if is_uri else str(db_str)

                    options["url"] = url.set(database=db_str)
        elif url.drivername.startswith("mysql"):
            if "pool_class" not in options or options["pool_class"] is QueuePool:
                options.setdefault("pool_recycle", 7200)

            if "charset" not in url.query:
                options["url"] = url.update_query_dict({"charset": "utf8mb4"})

    def _make_scoped_session(self, options: dict[str, Any]) -> async_scoped_session[AsyncSession]:
        scope = options.pop("scopefunc", _app_ctx_id)
        options.setdefault("expire_on_commit", False)
        factory = async_sessionmaker(bind=self._engine, class_=AsyncSession, **options)
        return async_scoped_session(factory, scope)

    async def _teardown_session_with_exception(self, exception: BaseException | None) -> None:
        # self._session.expunge_all()
        await self._session.remove()

    @property
    def Model(self) -> Type[DeclarativeBase]:  # noqa: N802
        return self._model

    async def create_all(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(self._model.metadata.create_all)

    async def drop_all(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(self._model.metadata.drop_all)
