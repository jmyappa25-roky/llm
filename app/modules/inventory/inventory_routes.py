from fastapi import APIRouter, Query

from app.modules.inventory.inventory_schemas import (
    InventoryAdjustmentRequest,
    InventoryAdjustmentResponse,
    InventoryItemRecord,
    InventoryMovementRecord,
    InventoryReservationResponse,
)
from app.modules.inventory.inventory_service import inventory_service

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryItemRecord])
async def list_inventory_items() -> list[InventoryItemRecord]:
    return inventory_service.list_items()


@router.get("/movements", response_model=list[InventoryMovementRecord])
async def list_inventory_movements(
    product_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[InventoryMovementRecord]:
    return inventory_service.list_movements(
        product_id=product_id,
        limit=limit,
    )


@router.post("/adjust", response_model=InventoryAdjustmentResponse)
async def adjust_inventory(
    payload: InventoryAdjustmentRequest,
) -> InventoryAdjustmentResponse:
    return inventory_service.adjust_stock(
        product_id=payload.product_id,
        quantity_delta=payload.quantity_delta,
        unit=payload.unit,
        notes=payload.notes,
    )


@router.post("/reserve-from-quote/{quote_id}", response_model=InventoryReservationResponse)
async def reserve_inventory_from_quote(quote_id: str) -> InventoryReservationResponse:
    return inventory_service.reserve_from_quote(quote_id=quote_id)


@router.get("/{product_id}", response_model=InventoryItemRecord)
async def get_inventory_item(product_id: str) -> InventoryItemRecord:
    return inventory_service.get_item(product_id=product_id)
