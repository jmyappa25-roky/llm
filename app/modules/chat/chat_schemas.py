from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config.env import settings
from app.modules.tools.tool_schemas import ToolOperationResult


Channel = Literal[
    "web",
    "whatsapp",
    "facebook",
    "instagram",
    "email",
    "panel",
    "voice",
]

Intent = Literal[
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

CustomerType = Literal[
    "desconocido",
    "menudeo",
    "mayoreo",
    "distribuidor",
    "restaurante",
    "cafeteria",
    "evento",
    "cliente_molesto",
]

Urgency = Literal["baja", "media", "alta"]


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    channel: Channel = Field(default="web")
    customer_id: str = Field(default="demo_customer", min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=settings.MAX_INPUT_CHARS)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        clean_value = value.strip()

        if not clean_value:
            raise ValueError("El mensaje no puede estar vacio.")

        return clean_value


class NormalizedMessage(BaseModel):
    request_id: str
    channel: Channel
    customer_id: str
    text: str
    possible_quantity: int | None = None
    has_phone: bool = False
    has_email: bool = False


class ChatAnalysis(BaseModel):
    intent: Intent
    customer_type: CustomerType
    product: str | None = None
    quantity: int | None = None
    urgency: Urgency
    needs_human: bool
    blocked: bool = False
    missing_data: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    rule_reasons: list[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0, le=1)


class ChatDecision(BaseModel):
    action: str
    reason: str
    created_lead: bool = False
    created_ticket: bool = False
    priority: Urgency = "baja"


class ChatResponse(BaseModel):
    ok: bool = True
    mode: str
    reply: str
    normalized: NormalizedMessage
    analysis: ChatAnalysis
    decision: ChatDecision
    operations: list[ToolOperationResult] = Field(default_factory=list)
