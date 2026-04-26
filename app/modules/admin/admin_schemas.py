from typing import Any, Literal

from pydantic import BaseModel, Field

from app.modules.metrics.metrics_schemas import MetricsSummaryResponse
from app.modules.tools.tool_schemas import (
    ConversationRecord,
    LeadRecord,
    MessageRecord,
    QuoteDraftRecord,
    TicketRecord,
)


TicketStatus = Literal[
    "open",
    "in_progress",
    "waiting_customer",
    "closed",
    "cancelled",
]

LeadStatus = Literal[
    "new",
    "collecting_data",
    "qualified",
    "contacted",
    "won",
    "lost",
]

QuoteDraftStatus = Literal[
    "draft",
    "pending_review",
    "approved",
    "rejected",
    "sent",
    "cancelled",
]


class AdminDashboardResponse(BaseModel):
    ok: bool = True
    metrics: MetricsSummaryResponse
    recent_conversations: list[ConversationRecord] = Field(default_factory=list)
    recent_leads: list[LeadRecord] = Field(default_factory=list)
    open_tickets: list[TicketRecord] = Field(default_factory=list)
    recent_quote_drafts: list[QuoteDraftRecord] = Field(default_factory=list)


class AdminTimelineItem(BaseModel):
    type: str
    id: str
    title: str
    summary: str
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdminStatusUpdateResponse(BaseModel):
    ok: bool = True
    entity_type: str
    entity_id: str
    old_status: str
    new_status: str
    message: str


class TicketStatusUpdateRequest(BaseModel):
    status: TicketStatus


class LeadStatusUpdateRequest(BaseModel):
    status: LeadStatus


class QuoteDraftStatusUpdateRequest(BaseModel):
    status: QuoteDraftStatus
