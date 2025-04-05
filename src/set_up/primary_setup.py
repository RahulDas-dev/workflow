from dotenv import load_dotenv
from quart import Quart

from library.extensions import configure_logger, configure_timezone, configure_warning


def register_app(app: Quart) -> None:
    configure_timezone(app)
    configure_logger(app)
    configure_warning(app)
    load_dotenv()
