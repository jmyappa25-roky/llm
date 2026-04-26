from pydantic import BaseModel, Field


class RuleEvaluationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    intent: str = Field(default="otro")
    product_id: str | None = None
    quantity: int | None = None
    customer_type: str = Field(default="desconocido")
    has_phone: bool = False
    has_email: bool = False


class RuleEvaluationResult(BaseModel):
    action_hint: str
    needs_human: bool
    blocked: bool = False
    priority: str
    missing_data: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
