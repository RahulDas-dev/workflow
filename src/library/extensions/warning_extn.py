from quart import Quart


def configure_warning(app: Quart) -> None:
    if app.config.get("DEBUG", False) is False:
        import warnings

        warnings.simplefilter("ignore", ResourceWarning)
