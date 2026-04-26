from app.core.errors import AppError
from app.modules.admin.admin_schemas import (
    AdminDashboardResponse,
    AdminStatusUpdateResponse,
    AdminTimelineItem,
)
from app.modules.audit.audit_service import audit_service
from app.modules.database.database import SessionLocal
from app.modules.database.models import (
    AuditEventModel,
    ConversationModel,
    LeadModel,
    MessageModel,
    QuoteDraftModel,
    TicketModel,
)
from app.modules.metrics.metrics_service import metrics_service
from app.modules.tools.tool_schemas import (
    ConversationRecord,
    LeadRecord,
    MessageRecord,
    QuoteDraftRecord,
    TicketRecord,
)


class AdminService:
    def dashboard(self) -> AdminDashboardResponse:
        return AdminDashboardResponse(
            ok=True,
            metrics=metrics_service.summary(),
            recent_conversations=self.list_conversations(limit=10),
            recent_leads=self.list_leads(limit=10),
            open_tickets=self.list_tickets(status="open", limit=10),
            recent_quote_drafts=self.list_quote_drafts(limit=10),
        )

    def list_conversations(
        self,
        customer_id: str | None = None,
        limit: int = 100,
    ) -> list[ConversationRecord]:
        with SessionLocal() as session:
            query = session.query(ConversationModel)

            if customer_id is not None:
                query = query.filter(ConversationModel.customer_id == customer_id)

            rows = (
                query
                .order_by(ConversationModel.updated_at.desc())
                .limit(limit)
                .all()
            )

            return [self._conversation_to_record(row) for row in rows]

    def list_messages(
        self,
        conversation_id: str | None = None,
        customer_id: str | None = None,
        limit: int = 200,
    ) -> list[MessageRecord]:
        with SessionLocal() as session:
            query = session.query(MessageModel)

            if customer_id is not None:
                query = (
                    query
                    .join(
                        ConversationModel,
                        MessageModel.conversation_id == ConversationModel.id,
                    )
                    .filter(ConversationModel.customer_id == customer_id)
                )

            if conversation_id is not None:
                query = query.filter(MessageModel.conversation_id == conversation_id)

            rows = (
                query
                .order_by(MessageModel.created_at.desc())
                .limit(limit)
                .all()
            )

            return [self._message_to_record(row) for row in rows]

    def list_leads(
        self,
        customer_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[LeadRecord]:
        with SessionLocal() as session:
            query = session.query(LeadModel)

            if customer_id is not None:
                query = query.filter(LeadModel.customer_id == customer_id)

            if status is not None:
                query = query.filter(LeadModel.status == status)

            rows = (
                query
                .order_by(LeadModel.created_at.desc())
                .limit(limit)
                .all()
            )

            return [self._lead_to_record(row) for row in rows]

    def list_tickets(
        self,
        customer_id: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        limit: int = 100,
    ) -> list[TicketRecord]:
        with SessionLocal() as session:
            query = session.query(TicketModel)

            if customer_id is not None:
                query = query.filter(TicketModel.customer_id == customer_id)

            if status is not None:
                query = query.filter(TicketModel.status == status)

            if priority is not None:
                query = query.filter(TicketModel.priority == priority)

            rows = (
                query
                .order_by(TicketModel.created_at.desc())
                .limit(limit)
                .all()
            )

            return [self._ticket_to_record(row) for row in rows]

    def list_quote_drafts(
        self,
        customer_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[QuoteDraftRecord]:
        with SessionLocal() as session:
            query = session.query(QuoteDraftModel)

            if customer_id is not None:
                query = query.filter(QuoteDraftModel.customer_id == customer_id)

            if status is not None:
                query = query.filter(QuoteDraftModel.status == status)

            rows = (
                query
                .order_by(QuoteDraftModel.created_at.desc())
                .limit(limit)
                .all()
            )

            return [self._quote_draft_to_record(row) for row in rows]

    def customer_timeline(
        self,
        customer_id: str,
        limit: int = 100,
    ) -> list[AdminTimelineItem]:
        items: list[AdminTimelineItem] = []

        with SessionLocal() as session:
            conversations = (
                session.query(ConversationModel)
                .filter(ConversationModel.customer_id == customer_id)
                .all()
            )

            conversation_ids = [conversation.id for conversation in conversations]

            messages = []
            if conversation_ids:
                messages = (
                    session.query(MessageModel)
                    .filter(MessageModel.conversation_id.in_(conversation_ids))
                    .all()
                )

            leads = (
                session.query(LeadModel)
                .filter(LeadModel.customer_id == customer_id)
                .all()
            )

            tickets = (
                session.query(TicketModel)
                .filter(TicketModel.customer_id == customer_id)
                .all()
            )

            quote_drafts = (
                session.query(QuoteDraftModel)
                .filter(QuoteDraftModel.customer_id == customer_id)
                .all()
            )

            audit_events = (
                session.query(AuditEventModel)
                .filter(AuditEventModel.customer_id == customer_id)
                .all()
            )

            for message in messages:
                title = "Mensaje del cliente"
                if message.role == "assistant":
                    title = "Respuesta del asistente"

                items.append(
                    AdminTimelineItem(
                        type="message",
                        id=message.id,
                        title=title,
                        summary=self._shorten(message.content),
                        created_at=message.created_at,
                        metadata={
                            "conversation_id": message.conversation_id,
                            "role": message.role,
                        },
                    )
                )

            for lead in leads:
                items.append(
                    AdminTimelineItem(
                        type="lead",
                        id=lead.id,
                        title="Lead comercial",
                        summary=(
                            f"Lead {lead.status} para producto {lead.product_id} "
                            f"con cantidad {lead.quantity}."
                        ),
                        created_at=lead.created_at,
                        metadata={
                            "conversation_id": lead.conversation_id,
                            "product_id": lead.product_id,
                            "quantity": lead.quantity,
                            "status": lead.status,
                            "priority": lead.priority,
                        },
                    )
                )

            for ticket in tickets:
                items.append(
                    AdminTimelineItem(
                        type="ticket",
                        id=ticket.id,
                        title="Ticket interno",
                        summary=f"Ticket {ticket.status}: {ticket.reason}.",
                        created_at=ticket.created_at,
                        metadata={
                            "conversation_id": ticket.conversation_id,
                            "reason": ticket.reason,
                            "priority": ticket.priority,
                            "status": ticket.status,
                        },
                    )
                )

            for quote_draft in quote_drafts:
                items.append(
                    AdminTimelineItem(
                        type="quote_draft",
                        id=quote_draft.id,
                        title="Borrador de cotizacion",
                        summary=(
                            f"Borrador {quote_draft.status} para producto "
                            f"{quote_draft.product_id} con cantidad {quote_draft.quantity}."
                        ),
                        created_at=quote_draft.created_at,
                        metadata={
                            "conversation_id": quote_draft.conversation_id,
                            "lead_id": quote_draft.lead_id,
                            "product_id": quote_draft.product_id,
                            "quantity": quote_draft.quantity,
                            "status": quote_draft.status,
                        },
                    )
                )

            for event in audit_events:
                items.append(
                    AdminTimelineItem(
                        type="audit_event",
                        id=event.id,
                        title=event.event_type,
                        summary=self._shorten(event.summary),
                        created_at=event.created_at,
                        metadata={
                            "entity_type": event.entity_type,
                            "entity_id": event.entity_id,
                            "actor_type": event.actor_type,
                        },
                    )
                )

        items.sort(key=lambda item: item.created_at, reverse=True)

        return items[:limit]

    def update_ticket_status(
        self,
        ticket_id: str,
        new_status: str,
    ) -> AdminStatusUpdateResponse:
        with SessionLocal() as session:
            row = (
                session.query(TicketModel)
                .filter(TicketModel.id == ticket_id)
                .first()
            )

            if row is None:
                raise AppError(
                    message="Ticket no encontrado.",
                    status_code=404,
                    code="TICKET_NOT_FOUND",
                )

            old_status = row.status
            row.status = new_status
            session.commit()
            session.refresh(row)

            audit_service.safe_record_event(
                event_type="ticket_status_updated",
                actor_type="admin",
                customer_id=row.customer_id,
                entity_type="ticket",
                entity_id=row.id,
                summary=f"Ticket actualizado de {old_status} a {new_status}.",
                metadata={
                    "old_status": old_status,
                    "new_status": new_status,
                },
            )

            return AdminStatusUpdateResponse(
                ok=True,
                entity_type="ticket",
                entity_id=row.id,
                old_status=old_status,
                new_status=new_status,
                message="Estado de ticket actualizado correctamente.",
            )

    def update_lead_status(
        self,
        lead_id: str,
        new_status: str,
    ) -> AdminStatusUpdateResponse:
        with SessionLocal() as session:
            row = (
                session.query(LeadModel)
                .filter(LeadModel.id == lead_id)
                .first()
            )

            if row is None:
                raise AppError(
                    message="Lead no encontrado.",
                    status_code=404,
                    code="LEAD_NOT_FOUND",
                )

            old_status = row.status
            row.status = new_status
            session.commit()
            session.refresh(row)

            audit_service.safe_record_event(
                event_type="lead_status_updated",
                actor_type="admin",
                customer_id=row.customer_id,
                entity_type="lead",
                entity_id=row.id,
                summary=f"Lead actualizado de {old_status} a {new_status}.",
                metadata={
                    "old_status": old_status,
                    "new_status": new_status,
                },
            )

            return AdminStatusUpdateResponse(
                ok=True,
                entity_type="lead",
                entity_id=row.id,
                old_status=old_status,
                new_status=new_status,
                message="Estado de lead actualizado correctamente.",
            )

    def update_quote_draft_status(
        self,
        quote_id: str,
        new_status: str,
    ) -> AdminStatusUpdateResponse:
        with SessionLocal() as session:
            row = (
                session.query(QuoteDraftModel)
                .filter(QuoteDraftModel.id == quote_id)
                .first()
            )

            if row is None:
                raise AppError(
                    message="Borrador de cotizacion no encontrado.",
                    status_code=404,
                    code="QUOTE_DRAFT_NOT_FOUND",
                )

            old_status = row.status
            row.status = new_status
            session.commit()
            session.refresh(row)

            audit_service.safe_record_event(
                event_type="quote_draft_status_updated",
                actor_type="admin",
                customer_id=row.customer_id,
                entity_type="quote_draft",
                entity_id=row.id,
                summary=f"Borrador actualizado de {old_status} a {new_status}.",
                metadata={
                    "old_status": old_status,
                    "new_status": new_status,
                },
            )

            return AdminStatusUpdateResponse(
                ok=True,
                entity_type="quote_draft",
                entity_id=row.id,
                old_status=old_status,
                new_status=new_status,
                message="Estado de borrador actualizado correctamente.",
            )

    def _conversation_to_record(self, row: ConversationModel) -> ConversationRecord:
        return ConversationRecord(
            id=row.id,
            customer_id=row.customer_id,
            channel=row.channel,
            status=row.status,
            last_intent=row.last_intent,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _message_to_record(self, row: MessageModel) -> MessageRecord:
        return MessageRecord(
            id=row.id,
            conversation_id=row.conversation_id,
            role=row.role,
            content=row.content,
            created_at=row.created_at,
        )

    def _lead_to_record(self, row: LeadModel) -> LeadRecord:
        return LeadRecord(
            id=row.id,
            conversation_id=row.conversation_id,
            customer_id=row.customer_id,
            product_id=row.product_id,
            quantity=row.quantity,
            customer_type=row.customer_type,
            status=row.status,
            priority=row.priority,
            missing_data=self._decode_missing_data(row.missing_data),
            created_at=row.created_at,
        )

    def _ticket_to_record(self, row: TicketModel) -> TicketRecord:
        return TicketRecord(
            id=row.id,
            conversation_id=row.conversation_id,
            customer_id=row.customer_id,
            reason=row.reason,
            summary=row.summary,
            priority=row.priority,
            status=row.status,
            created_at=row.created_at,
        )

    def _quote_draft_to_record(self, row: QuoteDraftModel) -> QuoteDraftRecord:
        return QuoteDraftRecord(
            id=row.id,
            conversation_id=row.conversation_id,
            lead_id=row.lead_id,
            customer_id=row.customer_id,
            product_id=row.product_id,
            quantity=row.quantity,
            status=row.status,
            requires_human_approval=bool(row.requires_human_approval),
            created_at=row.created_at,
        )

    def _decode_missing_data(self, value: str | None) -> list[str]:
        if value is None or value == "":
            return []

        return [item for item in value.split("|") if item]

    def _shorten(self, value: str, max_length: int = 140) -> str:
        if len(value) <= max_length:
            return value

        return value[: max_length - 3] + "..."


admin_service = AdminService()
