from fastapi import APIRouter, Query

from app.modules.audit.audit_schemas import AuditEventRecord, AuditResetResponse
from app.modules.audit.audit_store import audit_event_store

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/events", response_model=list[AuditEventRecord])
async def list_audit_events(
    limit: int = Query(default=100, ge=1, le=500),
) -> list[AuditEventRecord]:
    return audit_event_store.list_events(limit=limit)


@router.post("/reset", response_model=AuditResetResponse)
async def reset_audit_events() -> AuditResetResponse:
    audit_event_store.reset_events()

    return AuditResetResponse(
        ok=True,
        message="Eventos de auditoria reiniciados correctamente.",
    )
