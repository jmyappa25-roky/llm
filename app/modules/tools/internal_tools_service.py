from app.modules.audit.audit_service import audit_service
from app.modules.chat.chat_schemas import ChatAnalysis, ChatDecision, NormalizedMessage
from app.modules.customers.customer_service import customer_service
from app.modules.knowledge.knowledge_service import knowledge_service
from app.modules.tools.internal_store import internal_store
from app.modules.tools.tool_schemas import ToolOperationResult


class InternalToolsService:
    def execute_after_chat(
        self,
        normalized: NormalizedMessage,
        analysis: ChatAnalysis,
        decision: ChatDecision,
        reply: str,
    ) -> list[ToolOperationResult]:
        operations: list[ToolOperationResult] = []

        customer = customer_service.upsert_from_chat(
            normalized=normalized,
            analysis=analysis,
        )

        operations.append(
            ToolOperationResult(
                name="upsert_customer",
                status="saved",
                record_id=customer.id,
                message="Perfil de cliente registrado o actualizado.",
                data={
                    "customer_type": customer.customer_type,
                    "phone": customer.phone,
                    "email": customer.email,
                    "last_intent": customer.last_intent,
                },
            )
        )

        conversation = internal_store.upsert_conversation(
            customer_id=normalized.customer_id,
            channel=normalized.channel,
            last_intent=analysis.intent,
        )

        audit_service.safe_record_event(
            event_type="conversation_saved",
            actor_type="system",
            customer_id=normalized.customer_id,
            entity_type="conversation",
            entity_id=conversation.id,
            summary="Conversacion registrada o actualizada.",
            metadata={
                "channel": normalized.channel,
                "last_intent": analysis.intent,
            },
        )

        operations.append(
            ToolOperationResult(
                name="save_conversation",
                status="saved",
                record_id=conversation.id,
                message="Conversacion registrada o actualizada.",
            )
        )

        user_message = internal_store.create_message(
            conversation_id=conversation.id,
            role="user",
            content=normalized.text,
        )

        audit_service.safe_record_event(
            event_type="message_saved",
            actor_type="customer",
            customer_id=normalized.customer_id,
            entity_type="message",
            entity_id=user_message.id,
            summary="Mensaje del cliente guardado.",
            metadata={
                "conversation_id": conversation.id,
                "role": "user",
            },
        )

        operations.append(
            ToolOperationResult(
                name="save_user_message",
                status="created",
                record_id=user_message.id,
                message="Mensaje del cliente guardado.",
            )
        )

        assistant_message = internal_store.create_message(
            conversation_id=conversation.id,
            role="assistant",
            content=reply,
        )

        audit_service.safe_record_event(
            event_type="message_saved",
            actor_type="assistant",
            customer_id=normalized.customer_id,
            entity_type="message",
            entity_id=assistant_message.id,
            summary="Respuesta del asistente guardada.",
            metadata={
                "conversation_id": conversation.id,
                "role": "assistant",
            },
        )

        operations.append(
            ToolOperationResult(
                name="save_assistant_message",
                status="created",
                record_id=assistant_message.id,
                message="Respuesta del asistente guardada.",
            )
        )

        lead_id: str | None = None

        if decision.created_lead:
            lead = internal_store.create_lead(
                conversation_id=conversation.id,
                customer_id=normalized.customer_id,
                product_id=analysis.product,
                quantity=analysis.quantity,
                customer_type=analysis.customer_type,
                priority=analysis.urgency,
                missing_data=analysis.missing_data,
            )
            lead_id = lead.id

            audit_service.safe_record_event(
                event_type="lead_created",
                actor_type="system",
                customer_id=normalized.customer_id,
                entity_type="lead",
                entity_id=lead.id,
                summary="Lead comercial creado.",
                metadata={
                    "conversation_id": conversation.id,
                    "product_id": lead.product_id,
                    "quantity": lead.quantity,
                    "status": lead.status,
                    "priority": lead.priority,
                },
            )

            operations.append(
                ToolOperationResult(
                    name="create_lead",
                    status="created",
                    record_id=lead.id,
                    message="Lead comercial creado.",
                    data={
                        "status": lead.status,
                        "product_id": lead.product_id,
                        "quantity": lead.quantity,
                    },
                )
            )

        if decision.created_ticket:
            ticket = internal_store.create_ticket(
                conversation_id=conversation.id,
                customer_id=normalized.customer_id,
                reason=self._build_ticket_reason(analysis),
                summary=self._build_ticket_summary(analysis, normalized.text),
                priority=analysis.urgency,
            )

            audit_service.safe_record_event(
                event_type="ticket_created",
                actor_type="system",
                customer_id=normalized.customer_id,
                entity_type="ticket",
                entity_id=ticket.id,
                summary="Ticket interno creado.",
                metadata={
                    "conversation_id": conversation.id,
                    "reason": ticket.reason,
                    "priority": ticket.priority,
                    "status": ticket.status,
                },
            )

            operations.append(
                ToolOperationResult(
                    name="create_ticket",
                    status="created",
                    record_id=ticket.id,
                    message="Ticket interno creado.",
                    data={
                        "reason": ticket.reason,
                        "priority": ticket.priority,
                        "status": ticket.status,
                    },
                )
            )

        if decision.action == "crear_borrador_cotizacion":
            quote_draft = internal_store.create_quote_draft(
                conversation_id=conversation.id,
                customer_id=normalized.customer_id,
                lead_id=lead_id,
                product_id=analysis.product,
                quantity=analysis.quantity,
                requires_human_approval=self._requires_human_approval(analysis),
            )

            audit_service.safe_record_event(
                event_type="quote_draft_created",
                actor_type="system",
                customer_id=normalized.customer_id,
                entity_type="quote_draft",
                entity_id=quote_draft.id,
                summary="Borrador de cotizacion creado.",
                metadata={
                    "conversation_id": conversation.id,
                    "lead_id": quote_draft.lead_id,
                    "product_id": quote_draft.product_id,
                    "quantity": quote_draft.quantity,
                    "requires_human_approval": quote_draft.requires_human_approval,
                },
            )

            operations.append(
                ToolOperationResult(
                    name="create_quote_draft",
                    status="created",
                    record_id=quote_draft.id,
                    message="Borrador de cotizacion creado.",
                    data={
                        "lead_id": quote_draft.lead_id,
                        "product_id": quote_draft.product_id,
                        "quantity": quote_draft.quantity,
                        "requires_human_approval": quote_draft.requires_human_approval,
                    },
                )
            )

        return operations

    def _requires_human_approval(self, analysis: ChatAnalysis) -> bool:
        rules = knowledge_service.get_commercial_rules()

        if analysis.quantity is not None and analysis.quantity >= rules.human_approval_quantity:
            return True

        if analysis.needs_human:
            return True

        return False

    def _build_ticket_reason(self, analysis: ChatAnalysis) -> str:
        if analysis.intent in ["reclamo", "reembolso", "humano"]:
            return analysis.intent

        if analysis.safety_flags:
            return ",".join(analysis.safety_flags)

        return "revision_humana"

    def _build_ticket_summary(self, analysis: ChatAnalysis, text: str) -> str:
        return (
            f"Intent: {analysis.intent}. "
            f"Product: {analysis.product}. "
            f"Quantity: {analysis.quantity}. "
            f"Customer type: {analysis.customer_type}. "
            f"Message: {text}"
        )


internal_tools_service = InternalToolsService()
