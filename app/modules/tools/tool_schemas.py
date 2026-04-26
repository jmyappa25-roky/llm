from typing import Any

from pydantic import BaseModel, Field


class ConversationRecord(BaseModel):
    id: str
    customer_id: str
    channel: str
    status: str = "active"
    last_intent: str | None = None
    created_at: str
    updated_at: str


class MessageRecord(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str


class LeadRecord(BaseModel):
    id: str
    conversation_id: str
    customer_id: str
    product_id: str | None = None
    quantity: int | None = None
    customer_type: str = "desconocido"
    status: str = "new"
    priority: str = "baja"
    missing_data: list[str] = Field(default_factory=list)
    created_at: str


class TicketRecord(BaseModel):
    id: str
    conversation_id: str
    customer_id: str
    reason: str
    summary: str
    priority: str = "media"
    status: str = "open"
    created_at: str


class QuoteDraftRecord(BaseModel):
    id: str
    conversation_id: str
    lead_id: str | None = None
    customer_id: str
    product_id: str | None = None
    quantity: int | None = None
    status: str = "draft"
    requires_human_approval: bool = False
    created_at: str


class ToolOperationResult(BaseModel):
    name: str
    status: str
    record_id: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
