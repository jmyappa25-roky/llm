from datetime import datetime, timezone

from app.core.ids import new_id
from app.config.env import settings
from app.modules.ai.ai_schemas import AIInvocationLogRecord
from app.modules.database.database import SessionLocal, init_db
from app.modules.database.models import AIInvocationLogModel


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class AIInvocationLogStore:
    def __init__(self) -> None:
        init_db()

    def create_log(
        self,
        operation: str,
        provider: str,
        success: bool,
        latency_ms: int,
        request_id: str | None = None,
        customer_id: str | None = None,
        channel: str | None = None,
        used_fallback: bool = False,
        fallback_provider: str | None = None,
        error_type: str | None = None,
        error_message: str | None = None,
    ) -> AIInvocationLogRecord:
        with SessionLocal() as session:
            row = AIInvocationLogModel(
                id=new_id("ailog"),
                request_id=request_id,
                customer_id=customer_id,
                channel=channel,
                operation=operation,
                provider=provider,
                model=settings.OPENAI_MODEL,
                success=success,
                used_fallback=used_fallback,
                fallback_provider=fallback_provider,
                error_type=error_type,
                error_message=error_message,
                latency_ms=latency_ms,
                created_at=utc_now_iso(),
            )

            session.add(row)
            session.commit()
            session.refresh(row)

            return self._to_record(row)

    def list_logs(self, limit: int = 100) -> list[AIInvocationLogRecord]:
        with SessionLocal() as session:
            rows = (
                session.query(AIInvocationLogModel)
                .order_by(AIInvocationLogModel.created_at.desc())
                .limit(limit)
                .all()
            )

            return [self._to_record(row) for row in rows]

    def reset_logs(self) -> None:
        with SessionLocal() as session:
            session.query(AIInvocationLogModel).delete()
            session.commit()

    def _to_record(self, row: AIInvocationLogModel) -> AIInvocationLogRecord:
        return AIInvocationLogRecord(
            id=row.id,
            request_id=row.request_id,
            customer_id=row.customer_id,
            channel=row.channel,
            operation=row.operation,
            provider=row.provider,
            model=row.model,
            success=bool(row.success),
            used_fallback=bool(row.used_fallback),
            fallback_provider=row.fallback_provider,
            error_type=row.error_type,
            error_message=row.error_message,
            latency_ms=row.latency_ms,
            created_at=row.created_at,
        )


ai_invocation_log_store = AIInvocationLogStore()
