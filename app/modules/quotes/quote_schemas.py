from typing import Literal

from pydantic import BaseModel, Field


QuoteStatus = Literal[
    "draft",
    "pending_approval",
    "approved",
    "sent",
    "rejected",
    "cancelled",
]


class QuoteRecord(BaseModel):
    id: str
    quote_draft_id: str
    conversation_id: str
    customer_id: str
    product_id: str
    quantity: int
    unit_price_mxn: float
    subtotal_mxn: float
    discount_percent: float
    discount_mxn: float
    shipping_mxn: float
    total_mxn: float
    status: QuoteStatus
    requires_human_approval: bool
    valid_until: str
    notes: str
    created_at: str
    updated_at: str


class QuoteCreateFromDraftResponse(BaseModel):
    ok: bool = True
    quote: QuoteRecord
    message: str


class QuoteStatusUpdateResponse(BaseModel):
    ok: bool = True
    quote: QuoteRecord
    old_status: str
    new_status: str
    message: str


class QuoteCalculationPreview(BaseModel):
    product_id: str
    quantity: int
    unit_price_mxn: float
    subtotal_mxn: float
    discount_percent: float
    discount_mxn: float
    shipping_mxn: float
    total_mxn: float
    notes: list[str] = Field(default_factory=list)
