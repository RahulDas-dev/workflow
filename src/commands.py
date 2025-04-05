import asyncio

import click


@click.command("initdb")
def initdb() -> None:
    """Initialize the database."""
    click.echo("Database is migrating")
    from database.base import db

    asyncio.get_event_loop().run_until_complete(db.create_all())
