from typing import Any

from pydantic import BaseModel, Field


class AuditEventRecord(BaseModel):
    id: str
    event_type: str
    actor_type: str
    customer_id: str | None = None
    entity_type: str
    entity_id: str | None = None
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class AuditResetResponse(BaseModel):
    ok: bool = True
    message: str
