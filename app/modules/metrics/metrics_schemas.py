from pydantic import BaseModel, Field


class OperationalMetrics(BaseModel):
    customers: int
    conversations: int
    messages: int
    leads: int
    tickets: int
    quote_drafts: int
    quotes: int
    inventory_items: int
    inventory_movements: int
    audit_events: int


class AIMetrics(BaseModel):
    total_invocations: int
    successful_invocations: int
    failed_invocations: int
    fallback_invocations: int
    average_latency_ms: float
    provider_counts: dict[str, int] = Field(default_factory=dict)
    operation_counts: dict[str, int] = Field(default_factory=dict)


class MetricsSummaryResponse(BaseModel):
    ok: bool = True
    operational: OperationalMetrics
    ai: AIMetrics
