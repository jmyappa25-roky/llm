from fastapi import APIRouter, Query

from app.modules.ai.ai_log_store import ai_invocation_log_store
from app.modules.ai.ai_schemas import (
    AIAnalysisRequest,
    AIAnalysisResult,
    AIInvocationLogRecord,
    AIResetLogsResponse,
    AIStatusResponse,
)
from app.modules.ai.ai_service import ai_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status() -> AIStatusResponse:
    return ai_service.status()


@router.post("/analyze", response_model=AIAnalysisResult)
async def analyze_with_ai(payload: AIAnalysisRequest) -> AIAnalysisResult:
    return ai_service.analyze(payload)


@router.post("/smoke-test", response_model=AIAnalysisResult)
async def smoke_test_ai() -> AIAnalysisResult:
    return ai_service.smoke_test()


@router.get("/logs", response_model=list[AIInvocationLogRecord])
async def list_ai_logs(
    limit: int = Query(default=100, ge=1, le=500),
) -> list[AIInvocationLogRecord]:
    return ai_invocation_log_store.list_logs(limit=limit)


@router.post("/logs/reset", response_model=AIResetLogsResponse)
async def reset_ai_logs() -> AIResetLogsResponse:
    ai_invocation_log_store.reset_logs()

    return AIResetLogsResponse(
        ok=True,
        message="Logs de IA reiniciados correctamente.",
    )
