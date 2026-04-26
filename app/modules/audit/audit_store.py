import json
from datetime import datetime, timezone
from typing import Any

from app.core.ids import new_id
from app.modules.audit.audit_schemas import AuditEventRecord
from app.modules.database.database import SessionLocal, init_db
from app.modules.database.models import AuditEventModel


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class AuditEventStore:
    def __init__(self) -> None:
        init_db()

    def create_event(
        self,
        event_type: str,
        actor_type: str,
        entity_type: str,
        summary: str,
        customer_id: str | None = None,
        entity_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEventRecord:
        metadata_dict = metadata or {}

        with SessionLocal() as session:
            row = AuditEventModel(
                id=new_id("audit"),
                event_type=event_type,
                actor_type=actor_type,
                customer_id=customer_id,
                entity_type=entity_type,
                entity_id=entity_id,
                summary=summary,
                metadata_json=json.dumps(metadata_dict, ensure_ascii=True),
                created_at=utc_now_iso(),
            )

            session.add(row)
            session.commit()
            session.refresh(row)

            return self._to_record(row)

    def list_events(self, limit: int = 100) -> list[AuditEventRecord]:
        with SessionLocal() as session:
            rows = (
                session.query(AuditEventModel)
                .order_by(AuditEventModel.created_at.desc())
                .limit(limit)
                .all()
            )

            return [self._to_record(row) for row in rows]

    def reset_events(self) -> None:
        with SessionLocal() as session:
            session.query(AuditEventModel).delete()
            session.commit()

    def _to_record(self, row: AuditEventModel) -> AuditEventRecord:
        try:
            metadata = json.loads(row.metadata_json)
        except json.JSONDecodeError:
            metadata = {}

        return AuditEventRecord(
            id=row.id,
            event_type=row.event_type,
            actor_type=row.actor_type,
            customer_id=row.customer_id,
            entity_type=row.entity_type,
            entity_id=row.entity_id,
            summary=row.summary,
            metadata=metadata,
            created_at=row.created_at,
        )


audit_event_store = AuditEventStore()
