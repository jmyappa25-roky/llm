from fastapi import APIRouter

from app.modules.metrics.metrics_schemas import MetricsSummaryResponse
from app.modules.metrics.metrics_service import metrics_service

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary() -> MetricsSummaryResponse:
    return metrics_service.summary()
