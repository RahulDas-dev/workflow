import enum
import uuid
from datetime import datetime

from sqlalchemy import UUID, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String

from database.base import db


class AccountStatusEnum(enum.StrEnum):
    """Enum for account status."""

    PENDING = "pending"
    UNINTIALIZED = "uninitialized"
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class Account(db.Model):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_salt: Mapped[str] = mapped_column(String(255), nullable=True)
    interface_language: Mapped[str] = mapped_column(String(16))
    interface_theme: Mapped[str] = mapped_column(String(16))
    timezone: Mapped[str] = mapped_column(String(16))
    last_login_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    last_login_ip: Mapped[str] = mapped_column(String(32))
    last_active_at: Mapped[str] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default=text("'active'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())

    __table_args__ = (UniqueConstraint(email, name="account_email_idx"),)

    @property
    def is_password_set(self) -> bool:
        return self.password is not None
