import logging

from pydantic import BaseModel
from quart import Blueprint
from quart_schema import DataSource, validate_request, validate_response
from quart_schema.pydantic import File

bp = Blueprint("process", __name__, url_prefix="/process")

logger = logging.getLogger(__name__)


class Reqst(BaseModel):
    document: File


class InvoiceData(BaseModel):
    message: str


@bp.route("/", methods=["POST"])
@validate_request(Reqst, source=DataSource.FORM_MULTIPART)
@validate_response(InvoiceData, 201)
async def post(data: Reqst) -> tuple:
    logger.info(f"document.filename {data.document.filename}")
    invoices = InvoiceData(message="Hi there , How r u")
    return invoices, 201
