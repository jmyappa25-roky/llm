from typing import Literal

from pydantic import BaseModel, Field


InventoryMovementType = Literal[
    "adjustment",
    "reservation",
    "release",
]


class InventoryItemRecord(BaseModel):
    id: str
    product_id: str
    available_quantity: int
    reserved_quantity: int
    unit: str
    created_at: str
    updated_at: str


class InventoryMovementRecord(BaseModel):
    id: str
    product_id: str
    movement_type: InventoryMovementType
    quantity: int
    before_available: int
    after_available: int
    before_reserved: int
    after_reserved: int
    reference_type: str | None = None
    reference_id: str | None = None
    notes: str
    created_at: str


class InventoryAdjustmentRequest(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=100)
    quantity_delta: int
    unit: str = Field(default="unidad", min_length=1, max_length=50)
    notes: str = Field(default="Ajuste manual de inventario.", max_length=500)


class InventoryAdjustmentResponse(BaseModel):
    ok: bool = True
    item: InventoryItemRecord
    movement: InventoryMovementRecord
    message: str


class InventoryReservationResponse(BaseModel):
    ok: bool = True
    item: InventoryItemRecord
    movement: InventoryMovementRecord | None = None
    quote_id: str
    message: str
