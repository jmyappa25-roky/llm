from datetime import datetime, timezone

from app.core.ids import new_id
from app.modules.database.database import SessionLocal, init_db, reset_db
from app.modules.database.models import (
    ConversationModel,
    LeadModel,
    MessageModel,
    QuoteDraftModel,
    TicketModel,
)
from app.modules.tools.tool_schemas import (
    ConversationRecord,
    LeadRecord,
    MessageRecord,
    QuoteDraftRecord,
    TicketRecord,
)


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def encode_missing_data(values: list[str]) -> str:
    return "|".join(values)


def decode_missing_data(value: str | None) -> list[str]:
    if value is None or value == "":
        return []

    return [item for item in value.split("|") if item]


class InternalPersistentStore:
    def __init__(self) -> None:
        init_db()

    def reset(self) -> None:
        reset_db()

    def upsert_conversation(
        self,
        customer_id: str,
        channel: str,
        last_intent: str | None,
    ) -> ConversationRecord:
        now = utc_now_iso()

        with SessionLocal() as session:
            row = (
                session.query(ConversationModel)
                .filter(
                    ConversationModel.customer_id == customer_id,
                    ConversationModel.channel == channel,
                )
                .first()
            )

            if row is not None:
                row.last_intent = last_intent
                row.updated_at = now

                session.commit()
                session.refresh(row)

                return self._conversation_to_record(row)

            row = ConversationModel(
                id=new_id("conv"),
                customer_id=customer_id,
                channel=channel,
                status="active",
                last_intent=last_intent,
                created_at=now,
                updated_at=now,
            )

            session.add(row)
            session.commit()
            session.refresh(row)

            return self._conversation_to_record(row)

    def create_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> MessageRecord:
        with SessionLocal() as session:
            row = MessageModel(
                id=new_id("msg"),
                conversation_id=conversation_id,
                role=role,
                content=content,
                created_at=utc_now_iso(),
            )

            session.add(row)
            session.commit()
            session.refresh(row)

            return self._message_to_record(row)

    def create_lead(
        self,
        conversation_id: str,
        customer_id: str,
        product_id: str | None,
        quantity: int | None,
        customer_type: str,
        priority: str,
        missing_data: list[str],
    ) -> LeadRecord:
        status = "qualified" if not missing_data else "collecting_data"

        with SessionLocal() as session:
            row = LeadModel(
                id=new_id("lead"),
                conversation_id=conversation_id,
                customer_id=customer_id,
                product_id=product_id,
                quantity=quantity,
                customer_type=customer_type,
                status=status,
                priority=priority,
                missing_data=encode_missing_data(missing_data),
                created_at=utc_now_iso(),
            )

            session.add(row)
            session.commit()
            session.refresh(row)

            return self._lead_to_record(row)

    def create_ticket(
        self,
        conversation_id: str,
        customer_id: str,
        reason: str,
        summary: str,
        priority: str,
    ) -> TicketRecord:
        with SessionLocal() as session:
            row = TicketModel(
                id=new_id("ticket"),
                conversation_id=conversation_id,
                customer_id=customer_id,
                reason=reason,
                summary=summary,
                priority=priority,
                status="open",
                created_at=utc_now_iso(),
            )

            session.add(row)
            session.commit()
            session.refresh(row)

            return self._ticket_to_record(row)

    def create_quote_draft(
        self,
        conversation_id: str,
        customer_id: str,
        lead_id: str | None,
        product_id: str | None,
        quantity: int | None,
        requires_human_approval: bool,
    ) -> QuoteDraftRecord:
        with SessionLocal() as session:
            row = QuoteDraftModel(
                id=new_id("quote"),
                conversation_id=conversation_id,
                lead_id=lead_id,
                customer_id=customer_id,
                product_id=product_id,
                quantity=quantity,
                status="draft",
                requires_human_approval=requires_human_approval,
                created_at=utc_now_iso(),
            )

            session.add(row)
            session.commit()
            session.refresh(row)

            return self._quote_draft_to_record(row)

    def list_conversations(self) -> list[ConversationRecord]:
        with SessionLocal() as session:
            rows = (
                session.query(ConversationModel)
                .order_by(ConversationModel.created_at.asc())
                .all()
            )

            return [self._conversation_to_record(row) for row in rows]

    def list_messages(self) -> list[MessageRecord]:
        with SessionLocal() as session:
            rows = (
                session.query(MessageModel)
                .order_by(MessageModel.created_at.asc())
                .all()
            )

            return [self._message_to_record(row) for row in rows]

    def list_leads(self) -> list[LeadRecord]:
        with SessionLocal() as session:
            rows = (
                session.query(LeadModel)
                .order_by(LeadModel.created_at.asc())
                .all()
            )

            return [self._lead_to_record(row) for row in rows]

    def list_tickets(self) -> list[TicketRecord]:
        with SessionLocal() as session:
            rows = (
                session.query(TicketModel)
                .order_by(TicketModel.created_at.asc())
                .all()
            )

            return [self._ticket_to_record(row) for row in rows]

    def list_quote_drafts(self) -> list[QuoteDraftRecord]:
        with SessionLocal() as session:
            rows = (
                session.query(QuoteDraftModel)
                .order_by(QuoteDraftModel.created_at.asc())
                .all()
            )

            return [self._quote_draft_to_record(row) for row in rows]

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
            missing_data=decode_missing_data(row.missing_data),
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


internal_store = InternalPersistentStore()
