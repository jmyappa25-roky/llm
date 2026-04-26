from fastapi import APIRouter, Query

from app.modules.quotes.quote_schemas import (
    QuoteCalculationPreview,
    QuoteCreateFromDraftResponse,
    QuoteRecord,
    QuoteStatusUpdateResponse,
)
from app.modules.quotes.quote_service import quote_service

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.get("", response_model=list[QuoteRecord])
async def list_quotes(
    customer_id: str | None = None,
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[QuoteRecord]:
    return quote_service.list_quotes(
        customer_id=customer_id,
        status=status,
        limit=limit,
    )


@router.get("/{quote_id}", response_model=QuoteRecord)
async def get_quote(quote_id: str) -> QuoteRecord:
    return quote_service.get_quote(quote_id)


@router.post("/from-draft/{quote_draft_id}", response_model=QuoteCreateFromDraftResponse)
async def create_quote_from_draft(quote_draft_id: str) -> QuoteCreateFromDraftResponse:
    return quote_service.create_from_draft(quote_draft_id)


@router.get("/preview/{product_id}/{quantity}", response_model=QuoteCalculationPreview)
async def preview_quote(product_id: str, quantity: int) -> QuoteCalculationPreview:
    return quote_service.calculate_quote(
        product_id=product_id,
        quantity=quantity,
    )


@router.patch("/{quote_id}/approve", response_model=QuoteStatusUpdateResponse)
async def approve_quote(quote_id: str) -> QuoteStatusUpdateResponse:
    return quote_service.approve_quote(quote_id)


@router.patch("/{quote_id}/send", response_model=QuoteStatusUpdateResponse)
async def send_quote(quote_id: str) -> QuoteStatusUpdateResponse:
    return quote_service.send_quote(quote_id)
