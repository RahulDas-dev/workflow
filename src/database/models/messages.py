import re
import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Integer, UniqueConstraint, func, select, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String

from database.base import db


class MessageCatalogue(db.Model):
    __tablename__ = "message_catalogue"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    language: Mapped[str] = mapped_column(String(length=20), nullable=False)
    text: Mapped[str] = mapped_column(String(300), nullable=False, default=text("''"))
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.current_timestamp())
    isactive: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    __table_args__ = (UniqueConstraint(code, language, name="unique_message_code"),)

    def __repr__(self):
        return f"MessageCatalogue[id={self.id}, code={self.code}, text={self.text}]"

    @property
    def has_parameter(self) -> bool:
        parms_patteren = re.compile(r"{[a-z]+}")
        params = parms_patteren.findall(self.text)
        return bool(params)

    @classmethod
    async def featch_all(cls, language: str) -> Sequence["MessageCatalogue"]:
        async with db.session() as session:
            stmt = (
                select(MessageCatalogue)
                .where(MessageCatalogue.language == language and MessageCatalogue.isactive)
                .order_by(MessageCatalogue.updated_at.desc())
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "code": self.code,
            "text": self.text,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "isactive": self.isactive,
        }
