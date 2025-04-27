import uuid
from datetime import datetime
from typing import Any, ClassVar, Dict, List

from sqlalchemy import JSON, UUID, Boolean, Float, Index, Integer, PrimaryKeyConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String, Text

from database.base import db


class Document(db.Model):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    position: Mapped[int] = mapped_column(Integer(), nullable=False)
    data_source_type: Mapped[str] = mapped_column(String(255), nullable=False)
    data_source_info: Mapped[str] = mapped_column(Text(), nullable=True)
    dataset_process_rule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    batch: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())

    # start processing
    processing_started_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    # parsing
    file_id: Mapped[str] = mapped_column(Text(), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer(), nullable=True)
    parsing_completed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    cleaning_completed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    splitting_completed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    tokens: Mapped[int] = mapped_column(Integer(), nullable=True)
    indexing_latency: Mapped[float] = mapped_column(Float(), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    # pause
    is_paused: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=text("false"))
    paused_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    paused_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    # error
    error: Mapped[uuid.UUID] = mapped_column(Text(), nullable=True)
    stopped_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    # basic fields
    indexing_status: Mapped[str] = mapped_column(
        String(255), nullable=False, default=text("'waiting'::character varying")
    )
    enabled: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=text("true"))
    disabled_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    disabled_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    archived: Mapped[uuid.UUID] = mapped_column(Boolean(), nullable=False, server_default=text("false"))
    archived_reason: Mapped[uuid.UUID] = mapped_column(String(255), nullable=True)
    archived_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    archived_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())
    doc_type: Mapped[uuid.UUID] = mapped_column(String(40), nullable=True)
    doc_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    doc_form: Mapped[str] = mapped_column(String(255), nullable=False, default=text("'text_model'::character varying"))
    doc_language: Mapped[str] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint(id, name="document_pkey"),
        Index("document_dataset_id_idx", dataset_id),
        Index("document_is_paused_idx", is_paused),
        Index("document_tenant_idx", tenant_id),
    )

    DATA_SOURCES: ClassVar[List[str]] = ["upload_file", "notion_import", "website_crawl"]
