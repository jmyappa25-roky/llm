import json
from typing import Any

from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from app.config.env import settings
from app.modules.ai.ai_schemas import AIAnalysisRequest, AIAnalysisResult
from app.modules.ai.prompts.analysis_prompt import build_analysis_prompt
from app.modules.ai.prompts.system_prompt import build_system_prompt


ANALYSIS_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
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
            ],
        },
        "customer_type": {
            "type": "string",
            "enum": [
                "desconocido",
                "menudeo",
                "mayoreo",
                "distribuidor",
                "restaurante",
                "cafeteria",
                "evento",
                "cliente_molesto",
            ],
        },
        "product": {
            "type": "string",
            "enum": [
                "none",
                "miel_maguey",
                "aguamiel",
                "pulque",
                "penca_maguey",
            ],
        },
        "quantity": {
            "type": "integer",
            "minimum": 0,
        },
        "urgency": {
            "type": "string",
            "enum": ["baja", "media", "alta"],
        },
        "needs_human": {
            "type": "boolean",
        },
        "missing_data": {
            "type": "array",
            "items": {"type": "string"},
        },
        "safety_flags": {
            "type": "array",
            "items": {"type": "string"},
        },
        "reply_suggestion": {
            "type": "string",
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
    },
    "required": [
        "intent",
        "customer_type",
        "product",
        "quantity",
        "urgency",
        "needs_human",
        "missing_data",
        "safety_flags",
        "reply_suggestion",
        "confidence",
    ],
}


class OpenAIProvider:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_TIMEOUT_SECONDS,
        )

    def analyze(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY no esta configurada en .env")

        prompt = build_analysis_prompt(
            message=request.message,
            local_product=request.local_product,
            local_quantity=request.local_quantity,
        )

        try:
            response = self.client.responses.create(
                model=settings.OPENAI_MODEL,
                instructions=build_system_prompt(),
                input=prompt,
                max_output_tokens=settings.OPENAI_MAX_OUTPUT_TOKENS,
                store=False,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "agroavis_customer_analysis",
                        "schema": ANALYSIS_JSON_SCHEMA,
                        "strict": True,
                    }
                },
            )

            raw_text = response.output_text.strip()
            parsed = json.loads(raw_text)

            result = AIAnalysisResult(**parsed)
            result.provider = "openai"

            return result

        except json.JSONDecodeError as exc:
            raise RuntimeError(f"OpenAI no devolvio JSON valido: {exc}") from exc

        except ValidationError as exc:
            raise RuntimeError(f"OpenAI devolvio JSON con estructura invalida: {exc}") from exc

        except OpenAIError as exc:
            raise RuntimeError(f"Error de OpenAI API: {exc}") from exc


def create_openai_provider() -> OpenAIProvider:
    return OpenAIProvider()
