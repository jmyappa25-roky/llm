from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, UniqueConstraint

from app.modules.database.database import Base


class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True, index=True)
    email = Column(String(200), nullable=True, index=True)
    main_channel = Column(String(50), nullable=False, default="web")
    customer_type = Column(String(100), nullable=False, default="desconocido")
    status = Column(String(50), nullable=False, default="active")
    notes = Column(Text, nullable=False, default="")
    last_intent = Column(String(100), nullable=True)
    last_product_id = Column(String(100), nullable=True)
    last_quantity = Column(Integer, nullable=True)
    last_interaction_at = Column(String(40), nullable=True)
    created_at = Column(String(40), nullable=False)
    updated_at = Column(String(40), nullable=False)


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String(64), primary_key=True)
    customer_id = Column(String(100), nullable=False, index=True)
    channel = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active")
    last_intent = Column(String(100), nullable=True)
    created_at = Column(String(40), nullable=False)
    updated_at = Column(String(40), nullable=False)

    __table_args__ = (
        UniqueConstraint("customer_id", "channel", name="uq_conversation_customer_channel"),
    )


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(String(40), nullable=False)


class LeadModel(Base):
    __tablename__ = "leads"

    id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=False, index=True)
    customer_id = Column(String(100), nullable=False, index=True)
    product_id = Column(String(100), nullable=True, index=True)
    quantity = Column(Integer, nullable=True)
    customer_type = Column(String(100), nullable=False, default="desconocido")
    status = Column(String(50), nullable=False, default="new")
    priority = Column(String(50), nullable=False, default="baja")
    missing_data = Column(Text, nullable=False, default="")
    created_at = Column(String(40), nullable=False)


class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=False, index=True)
    customer_id = Column(String(100), nullable=False, index=True)
    reason = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False, default="media")
    status = Column(String(50), nullable=False, default="open")
    created_at = Column(String(40), nullable=False)


class QuoteDraftModel(Base):
    __tablename__ = "quote_drafts"

    id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=False, index=True)
    lead_id = Column(String(64), ForeignKey("leads.id"), nullable=True, index=True)
    customer_id = Column(String(100), nullable=False, index=True)
    product_id = Column(String(100), nullable=True, index=True)
    quantity = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    requires_human_approval = Column(Boolean, nullable=False, default=False)
    created_at = Column(String(40), nullable=False)


class QuoteModel(Base):
    __tablename__ = "quotes"

    id = Column(String(64), primary_key=True)
    quote_draft_id = Column(String(64), ForeignKey("quote_drafts.id"), nullable=False, index=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=False, index=True)
    customer_id = Column(String(100), nullable=False, index=True)
    product_id = Column(String(100), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price_mxn = Column(Float, nullable=False)
    subtotal_mxn = Column(Float, nullable=False)
    discount_percent = Column(Float, nullable=False, default=0)
    discount_mxn = Column(Float, nullable=False, default=0)
    shipping_mxn = Column(Float, nullable=False, default=0)
    total_mxn = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    requires_human_approval = Column(Boolean, nullable=False, default=False)
    valid_until = Column(String(40), nullable=False)
    notes = Column(Text, nullable=False, default="")
    created_at = Column(String(40), nullable=False)
    updated_at = Column(String(40), nullable=False)

    __table_args__ = (
        UniqueConstraint("quote_draft_id", name="uq_quote_quote_draft"),
    )


class InventoryItemModel(Base):
    __tablename__ = "inventory_items"

    id = Column(String(64), primary_key=True)
    product_id = Column(String(100), nullable=False, unique=True, index=True)
    available_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    unit = Column(String(50), nullable=False, default="unidad")
    created_at = Column(String(40), nullable=False)
    updated_at = Column(String(40), nullable=False)


class InventoryMovementModel(Base):
    __tablename__ = "inventory_movements"

    id = Column(String(64), primary_key=True)
    product_id = Column(String(100), nullable=False, index=True)
    movement_type = Column(String(100), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    before_available = Column(Integer, nullable=False)
    after_available = Column(Integer, nullable=False)
    before_reserved = Column(Integer, nullable=False)
    after_reserved = Column(Integer, nullable=False)
    reference_type = Column(String(100), nullable=True, index=True)
    reference_id = Column(String(100), nullable=True, index=True)
    notes = Column(Text, nullable=False, default="")
    created_at = Column(String(40), nullable=False)


class AIInvocationLogModel(Base):
    __tablename__ = "ai_invocation_logs"

    id = Column(String(64), primary_key=True)
    request_id = Column(String(100), nullable=True, index=True)
    customer_id = Column(String(100), nullable=True, index=True)
    channel = Column(String(50), nullable=True, index=True)
    operation = Column(String(100), nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    success = Column(Boolean, nullable=False, default=False)
    used_fallback = Column(Boolean, nullable=False, default=False)
    fallback_provider = Column(String(100), nullable=True)
    error_type = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=False, default=0)
    created_at = Column(String(40), nullable=False)


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(String(64), primary_key=True)
    event_type = Column(String(100), nullable=False, index=True)
    actor_type = Column(String(100), nullable=False, index=True)
    customer_id = Column(String(100), nullable=True, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(100), nullable=True, index=True)
    summary = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(String(40), nullable=False)
