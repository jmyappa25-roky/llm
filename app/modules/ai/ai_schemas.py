from typing import Literal

from pydantic import BaseModel, Field


AIIntent = Literal[
    "saludo",
    "informacion_producto",
    "precio",
    "cotizacion_mayoreo",
    "venta_menudeo",
    "envio",
    "disponibilidad",
    "reclamo",
    "soporte_pedido",
    "reembolso",
    "facturacion",
    "humano",
    "otro",
]

AICustomerType = Literal[
    "desconocido",
    "menudeo",
    "mayoreo",
    "distribuidor",
    "restaurante",
    "cafeteria",
    "evento",
    "cliente_molesto",
]

AIUrgency = Literal["baja", "media", "alta"]

AIProduct = Literal[
    "none",
    "miel_maguey",
    "aguamiel",
    "pulque",
    "penca_maguey",
]


class AIAnalysisRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    channel: str = Field(default="web")
    customer_id: str = Field(default="demo_customer")
    request_id: str | None = None
    local_product: str | None = None
    local_quantity: int | None = None


class AIAnalysisResult(BaseModel):
    intent: AIIntent
    customer_type: AICustomerType
    product: AIProduct = "none"
    quantity: int = Field(default=0, ge=0)
    urgency: AIUrgency = "baja"
    needs_human: bool = False
    missing_data: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    reply_suggestion: str = ""
    confidence: float = Field(default=0.0, ge=0, le=1)
    provider: str = "mock"


class AIStatusResponse(BaseModel):
    ok: bool = True
    ai_mode: str
    openai_enabled: bool
    model: str
    use_openai_analysis: bool
    use_openai_reply: bool
    max_output_tokens: int
    timeout_seconds: int


class AIInvocationLogRecord(BaseModel):
    id: str
    request_id: str | None = None
    customer_id: str | None = None
    channel: str | None = None
    operation: str
    provider: str
    model: str
    success: bool
    used_fallback: bool = False
    fallback_provider: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    latency_ms: int = 0
    created_at: str


class AIResetLogsResponse(BaseModel):
    ok: bool = True
    message: str
