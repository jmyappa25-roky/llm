from fastapi import APIRouter, Query

from app.modules.admin.admin_schemas import (
    AdminDashboardResponse,
    AdminStatusUpdateResponse,
    AdminTimelineItem,
    LeadStatusUpdateRequest,
    QuoteDraftStatusUpdateRequest,
    TicketStatusUpdateRequest,
)
from app.modules.admin.admin_service import admin_service
from app.modules.tools.tool_schemas import (
    ConversationRecord,
    LeadRecord,
    MessageRecord,
    QuoteDraftRecord,
    TicketRecord,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_dashboard() -> AdminDashboardResponse:
    return admin_service.dashboard()


@router.get("/conversations", response_model=list[ConversationRecord])
async def get_conversations(
    customer_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[ConversationRecord]:
    return admin_service.list_conversations(
        customer_id=customer_id,
        limit=limit,
    )


@router.get("/messages", response_model=list[MessageRecord])
async def get_messages(
    conversation_id: str | None = None,
    customer_id: str | None = None,
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[MessageRecord]:
    return admin_service.list_messages(
        conversation_id=conversation_id,
        customer_id=customer_id,
        limit=limit,
    )


@router.get("/leads", response_model=list[LeadRecord])
async def get_leads(
    customer_id: str | None = None,
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[LeadRecord]:
    return admin_service.list_leads(
        customer_id=customer_id,
        status=status,
        limit=limit,
    )


@router.get("/tickets", response_model=list[TicketRecord])
async def get_tickets(
    customer_id: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[TicketRecord]:
    return admin_service.list_tickets(
        customer_id=customer_id,
        status=status,
        priority=priority,
        limit=limit,
    )


@router.get("/quote-drafts", response_model=list[QuoteDraftRecord])
async def get_quote_drafts(
    customer_id: str | None = None,
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[QuoteDraftRecord]:
    return admin_service.list_quote_drafts(
        customer_id=customer_id,
        status=status,
        limit=limit,
    )


@router.get("/customers/{customer_id}/timeline", response_model=list[AdminTimelineItem])
async def get_customer_timeline(
    customer_id: str,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[AdminTimelineItem]:
    return admin_service.customer_timeline(
        customer_id=customer_id,
        limit=limit,
    )


@router.patch("/tickets/{ticket_id}/status", response_model=AdminStatusUpdateResponse)
async def update_ticket_status(
    ticket_id: str,
    payload: TicketStatusUpdateRequest,
) -> AdminStatusUpdateResponse:
    return admin_service.update_ticket_status(
        ticket_id=ticket_id,
        new_status=payload.status,
    )


@router.patch("/leads/{lead_id}/status", response_model=AdminStatusUpdateResponse)
async def update_lead_status(
    lead_id: str,
    payload: LeadStatusUpdateRequest,
) -> AdminStatusUpdateResponse:
    return admin_service.update_lead_status(
        lead_id=lead_id,
        new_status=payload.status,
    )


@router.patch("/quote-drafts/{quote_id}/status", response_model=AdminStatusUpdateResponse)
async def update_quote_draft_status(
    quote_id: str,
    payload: QuoteDraftStatusUpdateRequest,
) -> AdminStatusUpdateResponse:
    return admin_service.update_quote_draft_status(
        quote_id=quote_id,
        new_status=payload.status,
    )
