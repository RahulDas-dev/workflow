import uuid
from datetime import datetime
from typing import Any, ClassVar, Dict, List

from sqlalchemy import JSON, UUID, Index, PrimaryKeyConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String, Text

from database.base import db


class Dataset(db.Model):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    provider: Mapped[str] = mapped_column(String(255), nullable=False, default=text("'vendor'"))
    data_source_type: Mapped[str] = mapped_column(String(255))
    indexing_technique: Mapped[str] = mapped_column(String(255), nullable=True)
    index_struct: Mapped[str] = mapped_column(Text(), nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())
    updated_by: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())
    embedding_model: Mapped[str] = mapped_column(String(255), nullable=True)
    embedding_model_provider: Mapped[str] = mapped_column(String(255), nullable=True)
    collection_binding_id: Mapped[str] = mapped_column(UUID(as_uuid=True), nullable=True)
    retrieval_model: Mapped[Dict[str, Any]] = mapped_column(type_=JSON, server_default=text("'{}'"), nullable=True)

    INDEXING_TECHNIQUE_LIST: ClassVar[List[str | None]] = ["high_quality", "economy", None]
    PROVIDER_LIST: ClassVar[List[str | None]] = ["vendor", "external", None]

    __table_args__ = (PrimaryKeyConstraint(id, name="dataset_pkey"), Index("dataset_tenant_idx", tenant_id))
