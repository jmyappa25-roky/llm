from fastapi import APIRouter

from app.modules.tools.internal_store import internal_store
from app.modules.tools.tool_schemas import (
    ConversationRecord,
    LeadRecord,
    MessageRecord,
    QuoteDraftRecord,
    TicketRecord,
)

router = APIRouter(prefix="/api/internal", tags=["internal-tools"])


@router.get("/conversations", response_model=list[ConversationRecord])
async def list_conversations() -> list[ConversationRecord]:
    return internal_store.list_conversations()


@router.get("/messages", response_model=list[MessageRecord])
async def list_messages() -> list[MessageRecord]:
    return internal_store.list_messages()


@router.get("/leads", response_model=list[LeadRecord])
async def list_leads() -> list[LeadRecord]:
    return internal_store.list_leads()


@router.get("/tickets", response_model=list[TicketRecord])
async def list_tickets() -> list[TicketRecord]:
    return internal_store.list_tickets()


@router.get("/quote-drafts", response_model=list[QuoteDraftRecord])
async def list_quote_drafts() -> list[QuoteDraftRecord]:
    return internal_store.list_quote_drafts()


@router.post("/reset")
async def reset_internal_store() -> dict:
    internal_store.reset()

    return {
        "ok": True,
        "message": "Memoria interna reiniciada.",
    }
