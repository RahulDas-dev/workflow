import asyncio
import logging
from typing import List, Self

from pydantic import BaseModel, model_validator
from pydantic.dataclasses import dataclass
from quart import Blueprint, current_app, request
from quart_schema import DataSource, validate_request, validate_response
from quart_schema.pydantic import File

from library.extensions import pdf_loader

bp = Blueprint("uploads", __name__, url_prefix="/uploads")

logger = logging.getLogger(__name__)


class UploadReqst(BaseModel):
    passwords: list[str]
    documents: list[File]


class UploadResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str


# Kept for Deubing purpose only
@bp.before_request
async def log_request():
    if request.method == "POST":
        form_data = await request.form
        logger.debug(f"Received form data: {form_data}")
        # Don't use this in production, just for debugging
        files = await request.files
        logger.debug(f"Received files: {files}")


@bp.route("/", methods=["POST"])
@validate_request(UploadReqst, source=DataSource.FORM_MULTIPART)
@validate_response(UploadResponse, 201)
async def post(data: UploadReqst) -> tuple:
    logger.info(f"Total No of documents uploaded {len(data.documents)} ")
    uploads_list = []
    for data_item in data.documents:
        logger.info(f"File name: {data_item.filename}")
        uploads_list.append(pdf_loader.save(data_item, name=data_item.filename))
    saved_list = await asyncio.gather(*uploads_list)
    logger.info(f"Saved list: {len(saved_list)}")
    return UploadResponse(message=f"Saved list: {len(saved_list)}"), 201


@bp.errorhandler(413)
async def request_entity_too_large(e):
    logger.error(f"Request entity too large {e}")
    return ErrorResponse(error="The uploaded file is too large. Please reduce the file size."), 413
