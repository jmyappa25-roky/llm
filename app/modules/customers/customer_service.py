from datetime import datetime, timezone

from sqlalchemy import func

from app.core.errors import AppError
from app.core.text import extract_email, extract_phone
from app.modules.audit.audit_service import audit_service
from app.modules.chat.chat_schemas import ChatAnalysis, NormalizedMessage
from app.modules.database.database import SessionLocal, init_db
from app.modules.database.models import (
    ConversationModel,
    CustomerModel,
    LeadModel,
    MessageModel,
    QuoteModel,
    TicketModel,
)
from app.modules.customers.customer_schemas import (
    CustomerCommercialSummary,
    CustomerRecord,
    CustomerUpdateResponse,
)


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class CustomerService:
    def __init__(self) -> None:
        init_db()

    def upsert_from_chat(
        self,
        normalized: NormalizedMessage,
        analysis: ChatAnalysis,
    ) -> CustomerRecord:
        now = utc_now_iso()
        detected_phone = extract_phone(normalized.text)
        detected_email = extract_email(normalized.text)

        with SessionLocal() as session:
            row = (
                session.query(CustomerModel)
                .filter(CustomerModel.id == normalized.customer_id)
                .first()
            )

            created = False

            if row is None:
                created = True
                row = CustomerModel(
                    id=normalized.customer_id,
                    name=None,
                    phone=detected_phone,
                    email=detected_email,
                    main_channel=normalized.channel,
                    customer_type=analysis.customer_type,
                    status="active",
                    notes="",
                    last_intent=analysis.intent,
                    last_product_id=analysis.product,
                    last_quantity=analysis.quantity,
                    last_interaction_at=now,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
            else:
                if detected_phone is not None:
                    row.phone = detected_phone

                if detected_email is not None:
                    row.email = detected_email

                if analysis.customer_type != "desconocido":
                    row.customer_type = analysis.customer_type

                row.main_channel = normalized.channel
                row.last_intent = analysis.intent
                row.last_product_id = analysis.product
                row.last_quantity = analysis.quantity
                row.last_interaction_at = now
                row.updated_at = now

            session.commit()
            session.refresh(row)

            audit_service.safe_record_event(
                event_type="customer_created" if created else "customer_updated",
                actor_type="system",
                customer_id=row.id,
                entity_type="customer",
                entity_id=row.id,
                summary="Cliente creado desde chat." if created else "Cliente actualizado desde chat.",
                metadata={
                    "main_channel": row.main_channel,
                    "customer_type": row.customer_type,
                    "last_intent": row.last_intent,
                    "last_product_id": row.last_product_id,
                    "last_quantity": row.last_quantity,
                },
            )

            return self._to_record(row)

    def list_customers(
        self,
        customer_type: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[CustomerRecord]:
        with SessionLocal() as session:
            query = session.query(CustomerModel)

            if customer_type is not None:
                query = query.filter(CustomerModel.customer_type == customer_type)

            if status is not None:
                query = query.filter(CustomerModel.status == status)

            rows = (
                query
                .order_by(CustomerModel.updated_at.desc())
                .limit(limit)
                .all()
            )

            return [self._to_record(row) for row in rows]

    def get_customer(self, customer_id: str) -> CustomerRecord:
        with SessionLocal() as session:
            row = self._get_customer_row(session=session, customer_id=customer_id)

            if row is None:
                raise AppError(
                    message="Cliente no encontrado.",
                    status_code=404,
                    code="CUSTOMER_NOT_FOUND",
                )

            return self._to_record(row)

    def update_customer(
        self,
        customer_id: str,
        name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        customer_type: str | None = None,
        status: str | None = None,
        notes: str | None = None,
    ) -> CustomerUpdateResponse:
        with SessionLocal() as session:
            row = self._get_customer_row(session=session, customer_id=customer_id)

            if row is None:
                raise AppError(
                    message="Cliente no encontrado.",
                    status_code=404,
                    code="CUSTOMER_NOT_FOUND",
                )

            if name is not None:
                row.name = name

            if phone is not None:
                row.phone = phone

            if email is not None:
                row.email = email

            if customer_type is not None:
                row.customer_type = customer_type

            if status is not None:
                row.status = status

            if notes is not None:
                row.notes = notes

            row.updated_at = utc_now_iso()

            session.commit()
            session.refresh(row)

            audit_service.safe_record_event(
                event_type="customer_profile_updated",
                actor_type="admin",
                customer_id=row.id,
                entity_type="customer",
                entity_id=row.id,
                summary="Perfil de cliente actualizado.",
                metadata={
                    "name": row.name,
                    "phone": row.phone,
                    "email": row.email,
                    "customer_type": row.customer_type,
                    "status": row.status,
                },
            )

            return CustomerUpdateResponse(
                ok=True,
                customer=self._to_record(row),
                message="Cliente actualizado correctamente.",
            )

    def commercial_summary(self, customer_id: str) -> CustomerCommercialSummary:
        with SessionLocal() as session:
            customer = self._get_customer_row(session=session, customer_id=customer_id)

            if customer is None:
                raise AppError(
                    message="Cliente no encontrado.",
                    status_code=404,
                    code="CUSTOMER_NOT_FOUND",
                )

            conversations_count = (
                session.query(ConversationModel)
                .filter(ConversationModel.customer_id == customer_id)
                .count()
            )

            conversation_ids = [
                row.id
                for row in (
                    session.query(ConversationModel)
                    .filter(ConversationModel.customer_id == customer_id)
                    .all()
                )
            ]

            messages_count = 0
            if conversation_ids:
                messages_count = (
                    session.query(MessageModel)
                    .filter(MessageModel.conversation_id.in_(conversation_ids))
                    .count()
                )

            leads_count = (
                session.query(LeadModel)
                .filter(LeadModel.customer_id == customer_id)
                .count()
            )

            open_tickets_count = (
                session.query(TicketModel)
                .filter(
                    TicketModel.customer_id == customer_id,
                    TicketModel.status != "closed",
                )
                .count()
            )

            quotes_count = (
                session.query(QuoteModel)
                .filter(QuoteModel.customer_id == customer_id)
                .count()
            )

            sent_quotes_count = (
                session.query(QuoteModel)
                .filter(
                    QuoteModel.customer_id == customer_id,
                    QuoteModel.status == "sent",
                )
                .count()
            )

            total_quoted = (
                session.query(func.sum(QuoteModel.total_mxn))
                .filter(QuoteModel.customer_id == customer_id)
                .scalar()
            )

            if total_quoted is None:
                total_quoted = 0.0

            potential_value = float(total_quoted)

            return CustomerCommercialSummary(
                customer_id=customer_id,
                customer=self._to_record(customer),
                conversations_count=conversations_count,
                messages_count=messages_count,
                leads_count=leads_count,
                open_tickets_count=open_tickets_count,
                quotes_count=quotes_count,
                sent_quotes_count=sent_quotes_count,
                total_quoted_mxn=round(float(total_quoted), 2),
                potential_value_mxn=round(potential_value, 2),
                last_interaction_at=customer.last_interaction_at,
            )

    def _get_customer_row(
        self,
        session,
        customer_id: str,
    ) -> CustomerModel | None:
        return (
            session.query(CustomerModel)
            .filter(CustomerModel.id == customer_id)
            .first()
        )

    def _to_record(self, row: CustomerModel) -> CustomerRecord:
        return CustomerRecord(
            id=row.id,
            name=row.name,
            phone=row.phone,
            email=row.email,
            main_channel=row.main_channel,
            customer_type=row.customer_type,
            status=row.status,
            notes=row.notes,
            last_intent=row.last_intent,
            last_product_id=row.last_product_id,
            last_quantity=row.last_quantity,
            last_interaction_at=row.last_interaction_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


customer_service = CustomerService()
