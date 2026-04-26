from fastapi import APIRouter

from app.modules.chat.chat_schemas import ChatRequest, ChatResponse
from app.modules.chat.chat_service import chat_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    return chat_service.handle_message(payload)
