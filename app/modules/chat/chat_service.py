from app.config.env import settings
from app.core.ids import new_id
from app.core.text import (
    extract_possible_quantity,
    has_email,
    has_phone,
    normalize_for_matching,
    normalize_whitespace,
)
from app.modules.ai.ai_schemas import AIAnalysisRequest
from app.modules.ai.ai_service import ai_service
from app.modules.chat.chat_schemas import (
    ChatAnalysis,
    ChatRequest,
    ChatResponse,
    NormalizedMessage,
)
from app.modules.knowledge.knowledge_service import knowledge_service
from app.modules.orchestration.decision_service import decision_orchestrator
from app.modules.replies.reply_service import reply_service
from app.modules.rules.business_rules_service import business_rules_service
from app.modules.tools.internal_tools_service import internal_tools_service


class ChatService:
    def handle_message(self, request: ChatRequest) -> ChatResponse:
        normalized = self._normalize_request(request)
        analysis = self._analyze_message(normalized)
        decision = decision_orchestrator.decide(analysis)
        reply = reply_service.build_reply(analysis, decision)

        operations = internal_tools_service.execute_after_chat(
            normalized=normalized,
            analysis=analysis,
            decision=decision,
            reply=reply,
        )

        return ChatResponse(
            ok=True,
            mode=settings.AI_MODE,
            reply=reply,
            normalized=normalized,
            analysis=analysis,
            decision=decision,
            operations=operations,
        )

    def _normalize_request(self, request: ChatRequest) -> NormalizedMessage:
        clean_text = normalize_whitespace(request.message)

        return NormalizedMessage(
            request_id=new_id("req"),
            channel=request.channel,
            customer_id=request.customer_id,
            text=clean_text,
            possible_quantity=extract_possible_quantity(clean_text),
            has_phone=has_phone(clean_text),
            has_email=has_email(clean_text),
        )

    def _analyze_message(self, normalized: NormalizedMessage) -> ChatAnalysis:
        local_analysis = self._analyze_message_locally(normalized)

        if not settings.should_use_openai_analysis:
            return local_analysis

        ai_result = ai_service.analyze(
            AIAnalysisRequest(
                message=normalized.text,
                channel=normalized.channel,
                customer_id=normalized.customer_id,
                request_id=normalized.request_id,
                local_product=local_analysis.product,
                local_quantity=local_analysis.quantity,
            ),
            operation="chat_analysis",
        )

        ai_product = None if ai_result.product == "none" else ai_result.product
        ai_quantity = None if ai_result.quantity == 0 else ai_result.quantity

        merged_intent = ai_result.intent
        merged_customer_type = ai_result.customer_type
        merged_product = ai_product or local_analysis.product
        merged_quantity = ai_quantity or local_analysis.quantity
        merged_confidence = ai_result.confidence

        if self._local_analysis_is_stronger(local_analysis):
            merged_intent = local_analysis.intent
            merged_customer_type = local_analysis.customer_type
            merged_product = local_analysis.product
            merged_quantity = local_analysis.quantity
            merged_confidence = max(local_analysis.confidence, ai_result.confidence)

        rule_evaluation = business_rules_service.evaluate(
            text=normalized.text,
            intent=merged_intent,
            product_id=merged_product,
            quantity=merged_quantity,
            customer_type=merged_customer_type,
            has_phone=normalized.has_phone,
            has_email=normalized.has_email,
        )

        merged_safety_flags = self._merge_unique(
            local_analysis.safety_flags,
            ai_result.safety_flags,
            rule_evaluation.safety_flags,
        )

        return ChatAnalysis(
            intent=merged_intent,
            customer_type=merged_customer_type,
            product=merged_product,
            quantity=merged_quantity,
            urgency=rule_evaluation.priority,
            needs_human=rule_evaluation.needs_human,
            blocked=rule_evaluation.blocked,
            missing_data=rule_evaluation.missing_data,
            safety_flags=merged_safety_flags,
            rule_reasons=rule_evaluation.reasons,
            confidence=merged_confidence,
        )

    def _local_analysis_is_stronger(self, local_analysis: ChatAnalysis) -> bool:
        if (
            local_analysis.intent == "cotizacion_mayoreo"
            and local_analysis.product is not None
            and local_analysis.quantity is not None
            and local_analysis.quantity >= knowledge_service.get_commercial_rules().wholesale_min_quantity
        ):
            return True

        if local_analysis.blocked:
            return True

        if "tema_medico" in local_analysis.safety_flags:
            return True

        if "pulque_menor_edad" in local_analysis.safety_flags:
            return True

        if local_analysis.intent in ["reclamo", "reembolso", "humano"]:
            return True

        return False

    def _merge_unique(self, *lists: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []

        for values in lists:
            for value in values:
                if value not in seen:
                    seen.add(value)
                    result.append(value)

        return result

    def _analyze_message_locally(self, normalized: NormalizedMessage) -> ChatAnalysis:
        text_for_matching = normalize_for_matching(normalized.text)

        detected_product = knowledge_service.detect_product(normalized.text)
        product_id = detected_product.id if detected_product is not None else None

        intent = self._detect_intent(text_for_matching, normalized.possible_quantity)
        customer_type = self._detect_customer_type(text_for_matching, intent)

        rule_evaluation = business_rules_service.evaluate(
            text=normalized.text,
            intent=intent,
            product_id=product_id,
            quantity=normalized.possible_quantity,
            customer_type=customer_type,
            has_phone=normalized.has_phone,
            has_email=normalized.has_email,
        )

        return ChatAnalysis(
            intent=intent,
            customer_type=customer_type,
            product=product_id,
            quantity=normalized.possible_quantity,
            urgency=rule_evaluation.priority,
            needs_human=rule_evaluation.needs_human,
            blocked=rule_evaluation.blocked,
            missing_data=rule_evaluation.missing_data,
            safety_flags=rule_evaluation.safety_flags,
            rule_reasons=rule_evaluation.reasons,
            confidence=0.89,
        )

    def _detect_intent(self, text: str, quantity: int | None) -> str:
        rules = knowledge_service.get_commercial_rules()

        if any(keyword in text for keyword in rules.escalation_keywords):
            if any(word in text for word in ["reembolso", "devolucion"]):
                return "reembolso"

            if any(word in text for word in ["reclamo", "queja", "molesto", "enojado"]):
                return "reclamo"

            if any(word in text for word in ["humano", "asesor"]):
                return "humano"

        if any(word in text for word in ["mayoreo", "distribuidor", "cafeteria", "restaurante"]):
            return "cotizacion_mayoreo"

        if quantity is not None and quantity >= rules.wholesale_min_quantity:
            return "cotizacion_mayoreo"

        if any(word in text for word in ["factura", "facturacion", "cfdi"]):
            return "facturacion"

        if any(word in text for word in ["precio", "cuanto cuesta", "cuanto vale", "costo"]):
            return "precio"

        if any(word in text for word in ["envio", "entrega", "mandan", "domicilio"]):
            return "envio"

        if any(word in text for word in ["hay", "tienen", "disponible", "stock"]):
            return "disponibilidad"

        if any(word in text for word in ["sirve", "uso", "beneficio", "que es", "para que", "cura", "curar"]):
            return "informacion_producto"

        if any(word in text for word in ["hola", "buen dia", "buenas", "buenas tardes"]):
            return "saludo"

        return "otro"

    def _detect_customer_type(self, text: str, intent: str) -> str:
        if "cafeteria" in text:
            return "cafeteria"

        if "restaurante" in text:
            return "restaurante"

        if "distribuidor" in text:
            return "distribuidor"

        if "evento" in text or "fiesta" in text:
            return "evento"

        if any(word in text for word in ["molesto", "enojado", "queja", "reclamo"]):
            return "cliente_molesto"

        if intent == "cotizacion_mayoreo":
            return "mayoreo"

        if intent in ["precio", "venta_menudeo"]:
            return "menudeo"

        return "desconocido"


chat_service = ChatService()
