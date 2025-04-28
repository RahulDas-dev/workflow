from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import JSON, UUID, Boolean, Index, Integer, PrimaryKeyConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String, Text

from database.base import db


class DocumentBatch(db.Model):
    __tablename__ = "document_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    batch_name: Mapped[str] = mapped_column(String(255), nullable=False)
    batch_size: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())

    # start processing
    processing_started_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    # parsing
    parsing_completed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    __table_args__ = (PrimaryKeyConstraint(id, name="batch_pkey"),)

    @classmethod
    async def add_batch(cls, batch_name: str, created_by: uuid.UUID, batch_size: int = 0) -> DocumentBatch:
        """
        Add a new document batch to the database.
        """
        batch = DocumentBatch(
            batch_name=batch_name,
            batch_size=batch_size,
            created_by=created_by,
        )
        async with db.session() as session:
            session.add(batch)
            await session.commit()
        return batch

    @classmethod
    async def get_batch_by_id(cls, batch_id: uuid.UUID) -> DocumentBatch | None:
        """
        Get a document batch by its ID.

        :param batch_id: The unique identifier for the batch.
        :return: The DocumentBatch instance if found, otherwise None.
        """
        async with db.session() as session:
            batch = await session.get(DocumentBatch, batch_id)
            await session.close()
            return batch


class Document(db.Model):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4, primary_key=True)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    process_rule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())
    doc_type: Mapped[uuid.UUID] = mapped_column(String(40), nullable=True)
    doc_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True)
    doc_language: Mapped[str] = mapped_column(String(255), nullable=True)

    # start processing
    processing_started_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    # parsing
    parsing_completed_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    archived: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default=text("false"))
    archived_reason: Mapped[uuid.UUID] = mapped_column(String(255), nullable=True)
    archived_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    archived_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False, server_default=func.current_timestamp())

    __table_args__ = (PrimaryKeyConstraint(id, name="document_pkey"), Index("document_batch_idx", (batch_id, id)))

    @classmethod
    async def add_document(
        cls,
        batch_id: uuid.UUID,
        name: str,
        extension: str,
        password: str,
        process_rule_id: uuid.UUID,
        created_by: uuid.UUID,
        doc_type: str,
        doc_metadata: Dict[str, Any],
        doc_language: str,
    ) -> Document:
        """
        Add a new document to the database.

        :param document_id: The unique identifier for the document.
        :param batch_id: The unique identifier for the batch.
        :param name: The name of the document.
        :param extension: The file extension of the document.
        :return: The created Document instance.
        """
        document = Document(
            batch_id=batch_id,
            name=name,
            extension=extension,
            password=password,
            process_rule_id=process_rule_id,
            created_by=created_by,
            doc_type=doc_type,
            doc_metadata=doc_metadata,
            doc_language=doc_language,
        )
        async with db.session() as session:
            session.add(document)
            await session.commit()
            await session.close()
        return document

    @classmethod
    async def get_document_by_id(cls, document_id: uuid.UUID) -> Document | None:
        """
        Get a document by its ID.

        :param document_id: The unique identifier for the document.
        :return: The Document instance if found, otherwise None.
        """
        async with db.session() as session:
            document = await session.get(Document, document_id)
            await session.close()
            return document

    @classmethod
    async def get_documents_by_batch_id(cls, batch_id: uuid.UUID) -> list[Document]:
        """
        Get all documents by batch ID.

        :param batch_id: The unique identifier for the batch.
        :return: A list of Document instances.
        """
        async with db.session() as session:
            documents = await session.execute(db.select(Document).where(Document.batch_id == batch_id))
            await session.close()
            return documents.scalars().all()
