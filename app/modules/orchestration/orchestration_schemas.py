from app.modules.chat.chat_schemas import CustomerType, Intent, Urgency
from pydantic import BaseModel, Field


class DecisionEvaluationRequest(BaseModel):
    intent: Intent = Field(default="otro")
    customer_type: CustomerType = Field(default="desconocido")
    product: str | None = None
    quantity: int | None = None
    urgency: Urgency = Field(default="baja")
    needs_human: bool = False
    blocked: bool = False
    missing_data: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    rule_reasons: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0, le=1)
