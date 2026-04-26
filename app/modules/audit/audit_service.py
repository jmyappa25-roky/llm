from typing import Any

from app.modules.audit.audit_schemas import AuditEventRecord
from app.modules.audit.audit_store import audit_event_store


class AuditService:
    def record_event(
        self,
        event_type: str,
        actor_type: str,
        entity_type: str,
        summary: str,
        customer_id: str | None = None,
        entity_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEventRecord:
        return audit_event_store.create_event(
            event_type=event_type,
            actor_type=actor_type,
            customer_id=customer_id,
            entity_type=entity_type,
            entity_id=entity_id,
            summary=summary,
            metadata=metadata,
        )

    def safe_record_event(
        self,
        event_type: str,
        actor_type: str,
        entity_type: str,
        summary: str,
        customer_id: str | None = None,
        entity_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEventRecord | None:
        try:
            return self.record_event(
                event_type=event_type,
                actor_type=actor_type,
                customer_id=customer_id,
                entity_type=entity_type,
                entity_id=entity_id,
                summary=summary,
                metadata=metadata,
            )
        except Exception:
            return None


audit_service = AuditService()
