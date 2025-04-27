import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import db


class Uploads(db.Model):
    __tablename__ = "uploads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
