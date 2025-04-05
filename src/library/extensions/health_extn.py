import os
import threading

from quart import Quart
from quart_schema import hide


def configure_heath_checkup(app: Quart) -> None:
    @app.route("/health")
    @hide
    async def get_health_info() -> tuple[dict[str, str], int]:
        resonse_ = {
            "pid": os.getpid(),
            "status": "ok",
            "version": app.config.get("API_VERSION"),
            "app_name": app.config.get("APPLICATION_NAME"),
        }
        return resonse_, 201


def configure_thread_checkup(app: Quart) -> None:
    @app.route("/threads")
    @hide
    async def get_threads_info() -> tuple[dict[str, str], int]:
        num_threads = threading.active_count()
        threads = threading.enumerate()

        thread_list = []
        for thread in threads:
            thread_name = thread.name
            thread_id = thread.ident
            is_alive = thread.is_alive()

            thread_list.append({
                "name": thread_name,
                "id": thread_id,
                "is_alive": is_alive,
            })

        reponse_ = {"pid": os.getpid(), "thread_num": num_threads, "threads": thread_list}
        return reponse_, 201


def configure_db_checkup(app: Quart) -> None:
    @app.route("/db-pool-info")
    @hide
    def get_dbpool_info() -> tuple[dict[str, str], int]:
        from database import db

        reponse_ = {
            "pid": os.getpid(),
            "pool_size": db.engine.pool.size(),
            "checked_in_connections": db.engine.pool.checkedin(),
            "checked_out_connections": db.engine.pool.checkedout(),
            "overflow_connections": db.engine.pool.overflow(),
            "connection_timeout": db.engine.pool.timeout(),
            "recycle_time": db.engine.pool._recycle,  # noqa: SLF001
        }
        return reponse_, 201
