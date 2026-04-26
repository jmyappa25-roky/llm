from pydantic import BaseModel, Field


class CustomerRecord(BaseModel):
    id: str
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    main_channel: str
    customer_type: str
    status: str
    notes: str
    last_intent: str | None = None
    last_product_id: str | None = None
    last_quantity: int | None = None
    last_interaction_at: str | None = None
    created_at: str
    updated_at: str


class CustomerUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=200)
    customer_type: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=1000)


class CustomerUpdateResponse(BaseModel):
    ok: bool = True
    customer: CustomerRecord
    message: str


class CustomerCommercialSummary(BaseModel):
    customer_id: str
    customer: CustomerRecord
    conversations_count: int
    messages_count: int
    leads_count: int
    open_tickets_count: int
    quotes_count: int
    sent_quotes_count: int
    total_quoted_mxn: float
    potential_value_mxn: float
    last_interaction_at: str | None = None
