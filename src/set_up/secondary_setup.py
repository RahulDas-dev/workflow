from quart import Quart
from quart_schema import Info, QuartSchema
from quart_uploads import configure_uploads

from database.base import db
from library.extensions import (
    configure_db_checkup,
    configure_heath_checkup,
    configure_lifespan,
    configure_thread_checkup,
    pdf_loader,
)


def register_app(app: Quart) -> None:
    title_ = app.config.get("APPLICATION_NAME", "")
    version_ = app.config.get("API_VERSION", "1.0.0")
    api_schema = QuartSchema(
        info=Info(title=title_, version=version_),
        # conversion_preference="pydantic",
    )

    api_schema.init_app(app)
    db.init_app(app)
    configure_heath_checkup(app)
    configure_thread_checkup(app)
    configure_db_checkup(app)
    configure_lifespan(app)
    configure_uploads(app, pdf_loader)
    register_commands(app)


def register_commands(app: Quart) -> None:
    from commands import create_user, init_db

    app.cli.add_command(init_db)
    app.cli.add_command(create_user)
