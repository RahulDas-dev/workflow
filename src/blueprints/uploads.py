import logging

from pydantic import BaseModel, Field
from quart import Blueprint
from quart_schema import DataSource, validate_request, validate_response
from quart_schema.pydantic import File

bp = Blueprint("uploads", __name__, url_prefix="/uploads")

logger = logging.getLogger(__name__)


class UploadItem(BaseModel):
    name: str = Field(description="Name of the file")
    size: int = Field(description="Size of the file in bytes")
    type: str = Field(description="Type of the file")
    password: str = Field(description="Password for the file")


class UploadReqst(BaseModel):
    documents: list[File] = Field(default_factory=list, description="List of files to upload")
    items: list[UploadItem] = Field(default_factory=list, description="List of items to upload", max_items=10)


class InvoiceData(BaseModel):
    message: str


@bp.route("/", methods=["POST"])
@validate_request(UploadReqst, source=DataSource.FORM_MULTIPART)
@validate_response(InvoiceData, 201)
async def post(data: UploadReqst) -> tuple:
    logger.info(f"Total No of documents uploaded {len(data.documents)} items {len(data.items)}")
    invoices = InvoiceData(message="Hi there , How r u")
    return invoices, 201
