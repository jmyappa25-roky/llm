import re

from app.core.text import normalize_for_matching
from app.modules.knowledge.knowledge_service import knowledge_service
from app.modules.rules.rules_schemas import RuleEvaluationResult


class BusinessRulesService:
    def evaluate(
        self,
        text: str,
        intent: str,
        product_id: str | None,
        quantity: int | None,
        customer_type: str,
        has_phone: bool,
        has_email: bool,
    ) -> RuleEvaluationResult:
        normalized_text = normalize_for_matching(text)
        rules = knowledge_service.get_commercial_rules()

        missing_data = self._detect_missing_data(
            text=normalized_text,
            intent=intent,
            product_id=product_id,
            quantity=quantity,
            has_phone=has_phone,
            has_email=has_email,
        )

        safety_flags = self._detect_safety_flags(
            text=normalized_text,
            intent=intent,
            product_id=product_id,
            quantity=quantity,
        )

        blocked = self._is_blocked(
            text=normalized_text,
            product_id=product_id,
            safety_flags=safety_flags,
        )

        needs_human = self._needs_human(
            text=normalized_text,
            intent=intent,
            quantity=quantity,
            blocked=blocked,
            safety_flags=safety_flags,
        )

        priority = self._detect_priority(
            intent=intent,
            quantity=quantity,
            needs_human=needs_human,
            blocked=blocked,
            safety_flags=safety_flags,
        )

        reasons = self._build_reasons(
            intent=intent,
            product_id=product_id,
            quantity=quantity,
            missing_data=missing_data,
            safety_flags=safety_flags,
            needs_human=needs_human,
            blocked=blocked,
        )

        action_hint = self._detect_action_hint(
            blocked=blocked,
            needs_human=needs_human,
            missing_data=missing_data,
        )

        return RuleEvaluationResult(
            action_hint=action_hint,
            needs_human=needs_human,
            blocked=blocked,
            priority=priority,
            missing_data=missing_data,
            safety_flags=safety_flags,
            reasons=reasons,
        )

    def _detect_missing_data(
        self,
        text: str,
        intent: str,
        product_id: str | None,
        quantity: int | None,
        has_phone: bool,
        has_email: bool,
    ) -> list[str]:
        missing_data: list[str] = []

        if intent in ["precio", "cotizacion_mayoreo", "envio", "disponibilidad"]:
            if product_id is None:
                missing_data.append("producto")

            if quantity is None:
                missing_data.append("cantidad")

            if not self._has_presentation(text):
                missing_data.append("presentacion")

            if not self._has_delivery_zone(text):
                missing_data.append("zona_entrega")

        if intent == "cotizacion_mayoreo":
            if not self._has_required_date(text):
                missing_data.append("fecha_requerida")

            if "factura" not in text and "facturacion" not in text and "cfdi" not in text:
                missing_data.append("requiere_factura")

            if not has_phone:
                missing_data.append("telefono_contacto")

        if intent in ["reclamo", "soporte_pedido", "reembolso"]:
            if "pedido" not in text and "orden" not in text and "folio" not in text:
                missing_data.append("numero_pedido")

            if not has_phone and not has_email:
                missing_data.append("medio_contacto")

        return missing_data

    def _detect_safety_flags(
        self,
        text: str,
        intent: str,
        product_id: str | None,
        quantity: int | None,
    ) -> list[str]:
        flags: list[str] = []

        if any(word in text for word in ["diabetes", "cura", "curar", "medicina", "tratamiento", "salud"]):
            flags.append("tema_medico")

        if any(word in text for word in ["demanda", "legal", "abogado", "profeco"]):
            flags.append("tema_legal")

        if any(word in text for word in ["descuento especial", "precio especial", "rebajame", "mas barato"]):
            flags.append("descuento_especial")

        if intent in ["reclamo", "reembolso"]:
            flags.append("caso_postventa_delicado")

        if quantity is not None and quantity >= knowledge_service.get_commercial_rules().human_approval_quantity:
            flags.append("alto_volumen")

        if product_id == "pulque" or "pulque" in text:
            if self._mentions_minor_age(text):
                flags.append("pulque_menor_edad")

        return self._unique(flags)

    def _is_blocked(
        self,
        text: str,
        product_id: str | None,
        safety_flags: list[str],
    ) -> bool:
        if "pulque_menor_edad" in safety_flags:
            return True

        return False

    def _needs_human(
        self,
        text: str,
        intent: str,
        quantity: int | None,
        blocked: bool,
        safety_flags: list[str],
    ) -> bool:
        if blocked:
            return True

        if intent in ["reclamo", "reembolso", "humano"]:
            return True

        human_flags = [
            "tema_medico",
            "tema_legal",
            "descuento_especial",
            "caso_postventa_delicado",
            "alto_volumen",
        ]

        if any(flag in safety_flags for flag in human_flags):
            return True

        return False

    def _detect_priority(
        self,
        intent: str,
        quantity: int | None,
        needs_human: bool,
        blocked: bool,
        safety_flags: list[str],
    ) -> str:
        if blocked:
            return "alta"

        if any(flag in safety_flags for flag in ["tema_legal", "caso_postventa_delicado"]):
            return "alta"

        if intent in ["reclamo", "reembolso", "humano"]:
            return "alta"

        if quantity is not None and quantity >= knowledge_service.get_commercial_rules().human_approval_quantity:
            return "alta"

        if needs_human:
            return "media"

        if intent in ["cotizacion_mayoreo", "facturacion"]:
            return "media"

        return "baja"

    def _detect_action_hint(
        self,
        blocked: bool,
        needs_human: bool,
        missing_data: list[str],
    ) -> str:
        if blocked:
            return "rechazar_solicitud"

        if needs_human:
            return "escalar_humano"

        if missing_data:
            return "pedir_datos"

        return "responder_directo"

    def _build_reasons(
        self,
        intent: str,
        product_id: str | None,
        quantity: int | None,
        missing_data: list[str],
        safety_flags: list[str],
        needs_human: bool,
        blocked: bool,
    ) -> list[str]:
        reasons: list[str] = []

        if missing_data:
            reasons.append("Faltan datos obligatorios para continuar.")

        if blocked:
            reasons.append("La solicitud esta bloqueada por regla de seguridad.")

        if needs_human:
            reasons.append("El caso requiere revision humana.")

        if product_id is None and intent in ["precio", "cotizacion_mayoreo", "envio"]:
            reasons.append("No se detecto producto especifico.")

        if quantity is not None and quantity >= knowledge_service.get_commercial_rules().human_approval_quantity:
            reasons.append("El volumen solicitado requiere aprobacion humana.")

        if "tema_medico" in safety_flags:
            reasons.append("Se detecto tema medico; no se deben prometer curas ni tratamientos.")

        if "tema_legal" in safety_flags:
            reasons.append("Se detecto tema legal; debe revisarlo una persona.")

        if "pulque_menor_edad" in safety_flags:
            reasons.append("No se permite venta de pulque a menores de edad.")

        return self._unique(reasons)

    def _has_presentation(self, text: str) -> bool:
        presentation_keywords = [
            "250 ml",
            "250ml",
            "500 ml",
            "500ml",
            "1 l",
            "1l",
            "1 litro",
            "litro",
            "frasco",
            "presentacion",
        ]

        return any(keyword in text for keyword in presentation_keywords)

    def _has_delivery_zone(self, text: str) -> bool:
        zones = [
            "cdmx",
            "ciudad de mexico",
            "teotihuacan",
            "san martin",
            "edomex",
            "estado de mexico",
            "puebla",
            "hidalgo",
            "veracruz",
            "queretaro",
            "toluca",
            "ecatepec",
            "texcoco",
            "acolman",
        ]

        return any(zone in text for zone in zones)

    def _has_required_date(self, text: str) -> bool:
        date_words = [
            "hoy",
            "manana",
            "semana",
            "lunes",
            "martes",
            "miercoles",
            "jueves",
            "viernes",
            "sabado",
            "domingo",
            "fecha",
        ]

        return any(word in text for word in date_words)

    def _mentions_minor_age(self, text: str) -> bool:
        minor_patterns = [
            r"\bmenor\b",
            r"\bmenor de edad\b",
            r"\btengo\s+(1[0-7])\b",
            r"\bsoy\s+menor\b",
            r"\b(1[0-7])\s+anos\b",
            r"\b(1[0-7])\s+anios\b",
            r"\b(1[0-7])\s+a?os\b",
        ]

        return any(re.search(pattern, text) is not None for pattern in minor_patterns)

    def _unique(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        unique_values: list[str] = []

        for value in values:
            if value not in seen:
                seen.add(value)
                unique_values.append(value)

        return unique_values


business_rules_service = BusinessRulesService()
