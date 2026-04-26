from app.core.text import extract_possible_quantity, normalize_for_matching
from app.modules.ai.ai_schemas import AIAnalysisRequest, AIAnalysisResult
from app.modules.knowledge.knowledge_service import knowledge_service


class MockAIProvider:
    def analyze(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        text = normalize_for_matching(request.message)

        detected_product = knowledge_service.detect_product(request.message)
        product_id = detected_product.id if detected_product is not None else "none"

        quantity = request.local_quantity
        if quantity is None:
            quantity = extract_possible_quantity(request.message)

        if quantity is None:
            quantity = 0

        intent = "otro"
        customer_type = "desconocido"
        urgency = "baja"
        needs_human = False
        safety_flags: list[str] = []
        missing_data: list[str] = []

        if any(word in text for word in ["reclamo", "queja", "molesto", "enojado", "no llego"]):
            intent = "reclamo"
            customer_type = "cliente_molesto"
            urgency = "alta"
            needs_human = True
            safety_flags.append("caso_postventa_delicado")

        elif any(word in text for word in ["mayoreo", "cafeteria", "restaurante", "distribuidor"]) or quantity >= 20:
            intent = "cotizacion_mayoreo"
            urgency = "media"
            customer_type = "mayoreo"

            if "cafeteria" in text:
                customer_type = "cafeteria"
            elif "restaurante" in text:
                customer_type = "restaurante"
            elif "distribuidor" in text:
                customer_type = "distribuidor"

        elif any(word in text for word in ["precio", "cuanto cuesta", "costo"]):
            intent = "precio"
            customer_type = "menudeo"

        elif any(word in text for word in ["envio", "entrega", "domicilio"]):
            intent = "envio"

        elif any(word in text for word in ["sirve", "uso", "beneficio", "cura", "curar", "diabetes"]):
            intent = "informacion_producto"

        elif any(word in text for word in ["hola", "buen dia", "buenas"]):
            intent = "saludo"

        if any(word in text for word in ["diabetes", "cura", "curar", "medicina", "tratamiento"]):
            needs_human = True
            safety_flags.append("tema_medico")

        if product_id == "pulque" and any(word in text for word in ["menor", "17 anos", "17 anios", "17 a?os"]):
            needs_human = True
            urgency = "alta"
            safety_flags.append("pulque_menor_edad")

        if intent in ["precio", "cotizacion_mayoreo", "envio"]:
            if product_id == "none":
                missing_data.append("producto")
            if quantity == 0:
                missing_data.append("cantidad")

        return AIAnalysisResult(
            intent=intent,
            customer_type=customer_type,
            product=product_id,
            quantity=quantity,
            urgency=urgency,
            needs_human=needs_human,
            missing_data=missing_data,
            safety_flags=safety_flags,
            reply_suggestion="Respuesta sugerida por proveedor mock.",
            confidence=0.80,
            provider="mock",
        )


mock_ai_provider = MockAIProvider()
