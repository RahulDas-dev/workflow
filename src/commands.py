import asyncio

import click


@click.command("init-db")
def init_db() -> None:
    """Initialize the database."""
    click.echo("Database is migrating")
    from database.base import db

    asyncio.get_event_loop().run_until_complete(db.create_all())


@click.command("create-user")
@click.option("--name", prompt=True, help="Name of the User")
@click.option("--email", prompt=True, help="The User email address")
@click.option("--password", prompt=True, help="The User's password")
@click.option("--language", prompt=True, help="Account language, default: en-US.")
@click.option("--timezone", prompt=True, help="Account timezone, default: UTC.")
def create_user(
    email: str,
    password: str | None = None,
    name: str | None = None,
    language: str | None = None,
    timezone: str | None = None,
) -> None:
    """Add a user to the database."""

    if not email:
        click.echo(click.style("Email is required.", fg="red"))
        return
    email = email.strip()
    if not password:
        click.echo(click.style("Email is required.", fg="red"))
        return
    name = name if name else email.split("@")[0]
    language = language.strip() if language is not None else "en-US"
    timezone = timezone.strip() if timezone is not None else "UTC"
    from service.account_service import AccountService

    loop = asyncio.get_event_loop()
    account = loop.run_until_complete(AccountService.create_account(email, password, name, language, timezone))
    click.echo(click.style(f"User created: {account.email}", fg="green"))
