# ruff: noqa: S101,  PLR2004
import pytest
from quart import Quart
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_scoped_session

from src.library.extensions.database_extn import SqlAlchemy


@pytest.fixture
def quart_app() -> Quart:
    """Fixture to create and configure a Quart app."""
    app = Quart(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///:memory:"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"echo": True}
    return app


@pytest.fixture
def db(quart_app: Quart) -> SqlAlchemy:
    """Fixture to initialize SqlAlchemy with the Quart app."""
    from sqlalchemy import MetaData
    from sqlalchemy.orm import DeclarativeBase

    meta = MetaData()

    class Base(DeclarativeBase):
        """Base for all DB models."""

        metadata = meta

    db = SqlAlchemy(model_class=Base)
    db.init_app(quart_app)
    return db


@pytest.mark.asyncio
async def test_sqlalchemy_initialization(quart_app: Quart, db: SqlAlchemy) -> None:
    """Test that SqlAlchemy initializes correctly with the Quart app."""
    assert "sqlalchemy" in quart_app.extensions
    assert isinstance(db.session, async_scoped_session)
    assert isinstance(db.engine, AsyncEngine)


@pytest.mark.asyncio
async def test_session_creation(quart_app: Quart, db: SqlAlchemy) -> None:
    """Test session creation and teardown."""
    async with quart_app.app_context():
        async with db.session() as session:
            # Example query
            result = await session.execute(text("SELECT 1+1 AS result"))
            scalar_result = result.scalar()
    assert scalar_result == 2


@pytest.mark.asyncio
async def test_invalid_database_uri() -> None:
    """Test behavior with an invalid database URI."""
    app = Quart(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "invalid_uri"
    db = SqlAlchemy()

    with pytest.raises(Exception):  # Replace `Exception` with the specific exception if known
        db.init_app(app)


@pytest.mark.asyncio
async def test_multiple_sessions(quart_app: Quart, db: SqlAlchemy) -> None:
    """Test that multiple sessions can be created and used."""
    async with quart_app.app_context():
        async with db.session() as session1, db.session() as session2:
            result1 = await session1.execute(text("SELECT 1+1 AS result"))
            result2 = await session2.execute(text("SELECT 2+2 AS result"))
            assert result1.scalar() == 2
            assert result2.scalar() == 4


@pytest.mark.asyncio
async def test_model_creation(quart_app: Quart, db: SqlAlchemy) -> None:
    """Test model creation."""
    from sqlalchemy import Integer, Select, String
    from sqlalchemy.orm import Mapped, mapped_column

    class User(db.Model):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        name: Mapped[str] = mapped_column(String(50))

    async with quart_app.app_context():
        await db.create_all()

        async with db.session() as session:
            new_user = User(name="Test User")
            session.add(new_user)
            await session.commit()

            # result = await session.execute(text("SELECT name FROM users WHERE id = :id"), {"id": new_user.id})
            query_stmt = Select(User).where(User.id == new_user.id)
            result = await session.execute(query_stmt)
            user_ = result.scalar()
            await session.close()
    assert user_ is not None
    assert user_.name == "Test User"


@pytest.mark.asyncio
async def test_transaction_rollback(quart_app: Quart, db: SqlAlchemy) -> None:
    """Test that transactions are rolled back on error."""
    from sqlalchemy import Integer, Select, String
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import Mapped, mapped_column

    class User(db.Model):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        name: Mapped[str] = mapped_column(String(50), unique=True)

    async with quart_app.app_context():
        await db.create_all()

        async with db.session() as session:
            user1 = User(name="Test User")
            session.add(user1)
            await session.commit()

            # Attempt to insert a duplicate user to trigger an IntegrityError
            user2 = User(name="Test User")
            session.add(user2)
            with pytest.raises(IntegrityError):
                await session.commit()

        # Ensure the first user is still in the database
        async with db.session() as session:
            result = await session.execute(Select(User).where(User.name == "Test User"))
            user_ = result.scalar()
            assert user_ is not None


@pytest.mark.asyncio
async def test_query_method(quart_app: Quart, db: SqlAlchemy) -> None:
    """Test querying the database using db.session.query."""
    from sqlalchemy import Integer, String
    from sqlalchemy.orm import Mapped, mapped_column

    class MessageCatalogue(db.Model):
        __tablename__ = "message_catalogue"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        language: Mapped[str] = mapped_column(String(10))
        message: Mapped[str] = mapped_column(String(255))

    async with quart_app.app_context():
        await db.create_all()

        # Insert test data
        async with db.session() as session:
            message1 = MessageCatalogue(language="en", message="Hello")
            message2 = MessageCatalogue(language="fr", message="Bonjour")
            session.add_all([message1, message2])
            await session.commit()

        # Query the database
        async with db.session() as session:
            results = session.query(MessageCatalogue).where(MessageCatalogue.language == "en").all()
            assert len(results) == 1
            assert results[0].message == "Hello"
