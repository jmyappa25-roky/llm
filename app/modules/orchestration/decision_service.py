from app.modules.chat.chat_schemas import ChatAnalysis, ChatDecision


class DecisionOrchestrator:
    def decide(self, analysis: ChatAnalysis) -> ChatDecision:
        if analysis.blocked:
            return ChatDecision(
                action="rechazar_solicitud",
                reason="La solicitud esta bloqueada por una regla de seguridad.",
                created_lead=False,
                created_ticket=False,
                priority=analysis.urgency,
            )

        if analysis.needs_human:
            return ChatDecision(
                action="escalar_humano",
                reason="El caso requiere revision humana por regla de negocio.",
                created_lead=self._should_create_lead(analysis),
                created_ticket=self._should_create_ticket(analysis),
                priority=analysis.urgency,
            )

        if analysis.missing_data:
            return ChatDecision(
                action="pedir_datos",
                reason="Faltan datos para continuar correctamente.",
                created_lead=self._should_create_lead(analysis),
                created_ticket=False,
                priority=analysis.urgency,
            )

        if analysis.intent == "cotizacion_mayoreo":
            return ChatDecision(
                action="crear_borrador_cotizacion",
                reason="Ya existen datos suficientes para preparar un borrador de cotizacion.",
                created_lead=True,
                created_ticket=False,
                priority=analysis.urgency,
            )

        return ChatDecision(
            action="responder_directo",
            reason="La consulta puede responderse con informacion basica.",
            created_lead=False,
            created_ticket=False,
            priority=analysis.urgency,
        )

    def _should_create_lead(self, analysis: ChatAnalysis) -> bool:
        return analysis.intent == "cotizacion_mayoreo"

    def _should_create_ticket(self, analysis: ChatAnalysis) -> bool:
        ticket_intents = ["reclamo", "reembolso", "humano"]

        if analysis.intent in ticket_intents:
            return True

        if "tema_legal" in analysis.safety_flags:
            return True

        return False


decision_orchestrator = DecisionOrchestrator()
