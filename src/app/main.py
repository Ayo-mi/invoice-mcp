from typing import Optional

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings
from app.router import ToolRouter

settings = get_settings()
router = ToolRouter()

mcp = FastMCP(
    name="InvoiceIntelligenceMCP",
    instructions=(
        "Analyze invoices and return decision-ready risk intelligence. "
        "Use analyze_invoice_risk for approval decisions and execute tools for raw data."
    ),
    strict_validation=True,
)


@mcp.custom_route("/health", methods=["GET"])
async def health(_request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "invoice-mcp"})


@mcp.tool
def analyze_invoice_risk(invoice_text: str, user_id: str) -> dict:
    result = router.analyze_invoice_risk({"invoice_text": invoice_text, "user_id": user_id})
    return result.model_dump()


@mcp.tool
def extract_invoice_fields(invoice_text: str, user_id: str) -> dict:
    result = router.extract_invoice_fields({"invoice_text": invoice_text, "user_id": user_id})
    return result.model_dump()


@mcp.tool
def compare_invoice_history(
    vendor: str, user_id: str, current_amount: Optional[float] = None
) -> dict:
    result = router.compare_invoice_history(
        {"vendor": vendor, "user_id": user_id, "current_amount": current_amount}
    )
    return result.model_dump()


def create_http_app():
    return mcp.http_app()


if __name__ == "__main__":
    mcp.run(
        transport=settings.mcp_transport,
        host=settings.mcp_host,
        port=settings.mcp_port,
    )

