# ruff: noqa: LOG015
import logging
import time

from application import LLMOrchaX
from configs import app_config


def _register_extensions(app: LLMOrchaX, bebug: bool = False) -> None:
    from src.set_up import primary_setup, secondary_setup

    extensions = [
        primary_setup,
        secondary_setup,
    ]
    for extension in extensions:
        logging.info(f"Registering {extension.__name__} ...")
        start_time = time.perf_counter()
        extension.register_app(app)
        if bebug:
            logging.info(
                f"{extension.__name__} registered , latency: {round((time.perf_counter() - start_time) * 1000, 3)}ms"
            )


def _register_services(app: LLMOrchaX) -> None:
    logging.info("Service registration complete...")


def _register_blueprints(app: LLMOrchaX) -> None:
    from blueprints import bp

    app.register_blueprint(bp)
    logging.info("Blueprints registration complete...")


def create_application() -> LLMOrchaX:
    start_time = time.perf_counter()
    app = LLMOrchaX(__name__)
    app.config.from_mapping(app_config.model_dump())
    debug_ = app.config.get("DEBUG", False)
    _register_extensions(app, debug_)
    _register_services(app)
    _register_blueprints(app)
    if debug_:
        latency = round((time.perf_counter() - start_time) * 1000, 3)
        logging.info(f"Application created in {latency} seconds")
    return app
