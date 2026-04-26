from datetime import datetime, timezone

from app.core.errors import AppError
from app.core.ids import new_id
from app.modules.audit.audit_service import audit_service
from app.modules.database.database import SessionLocal, init_db
from app.modules.database.models import (
    InventoryItemModel,
    InventoryMovementModel,
    QuoteModel,
)
from app.modules.inventory.inventory_schemas import (
    InventoryAdjustmentResponse,
    InventoryItemRecord,
    InventoryMovementRecord,
    InventoryReservationResponse,
)


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class InventoryService:
    def __init__(self) -> None:
        init_db()

    def list_items(self) -> list[InventoryItemRecord]:
        with SessionLocal() as session:
            rows = (
                session.query(InventoryItemModel)
                .order_by(InventoryItemModel.product_id.asc())
                .all()
            )

            return [self._item_to_record(row) for row in rows]

    def get_item(self, product_id: str) -> InventoryItemRecord:
        with SessionLocal() as session:
            row = self._get_item_row(session=session, product_id=product_id)

            if row is None:
                raise AppError(
                    message="Producto sin registro de inventario.",
                    status_code=404,
                    code="INVENTORY_ITEM_NOT_FOUND",
                )

            return self._item_to_record(row)

    def adjust_stock(
        self,
        product_id: str,
        quantity_delta: int,
        unit: str,
        notes: str,
    ) -> InventoryAdjustmentResponse:
        if quantity_delta == 0:
            raise AppError(
                message="El ajuste no puede ser cero.",
                status_code=400,
                code="INVALID_INVENTORY_ADJUSTMENT",
            )

        with SessionLocal() as session:
            item = self._get_or_create_item_row(
                session=session,
                product_id=product_id,
                unit=unit,
            )

            before_available = int(item.available_quantity)
            before_reserved = int(item.reserved_quantity)
            after_available = before_available + quantity_delta

            if after_available < 0:
                raise AppError(
                    message="El ajuste dejaria inventario disponible negativo.",
                    status_code=409,
                    code="NEGATIVE_AVAILABLE_INVENTORY",
                )

            item.available_quantity = after_available
            item.unit = unit
            item.updated_at = utc_now_iso()

            movement = InventoryMovementModel(
                id=new_id("inv_move"),
                product_id=product_id,
                movement_type="adjustment",
                quantity=quantity_delta,
                before_available=before_available,
                after_available=after_available,
                before_reserved=before_reserved,
                after_reserved=before_reserved,
                reference_type=None,
                reference_id=None,
                notes=notes,
                created_at=utc_now_iso(),
            )

            session.add(movement)
            session.commit()
            session.refresh(item)
            session.refresh(movement)

            audit_service.safe_record_event(
                event_type="inventory_adjusted",
                actor_type="admin",
                entity_type="inventory_item",
                entity_id=item.id,
                summary="Inventario ajustado manualmente.",
                metadata={
                    "product_id": product_id,
                    "quantity_delta": quantity_delta,
                    "before_available": before_available,
                    "after_available": after_available,
                },
            )

            return InventoryAdjustmentResponse(
                ok=True,
                item=self._item_to_record(item),
                movement=self._movement_to_record(movement),
                message="Inventario ajustado correctamente.",
            )

    def reserve_from_quote(self, quote_id: str) -> InventoryReservationResponse:
        with SessionLocal() as session:
            quote = (
                session.query(QuoteModel)
                .filter(QuoteModel.id == quote_id)
                .first()
            )

            if quote is None:
                raise AppError(
                    message="Cotizacion no encontrada.",
                    status_code=404,
                    code="QUOTE_NOT_FOUND",
                )

            existing_movement = (
                session.query(InventoryMovementModel)
                .filter(
                    InventoryMovementModel.reference_type == "quote",
                    InventoryMovementModel.reference_id == quote_id,
                    InventoryMovementModel.movement_type == "reservation",
                )
                .first()
            )

            item = self._get_item_row(
                session=session,
                product_id=quote.product_id,
            )

            if item is None:
                raise AppError(
                    message="No existe inventario para el producto de la cotizacion.",
                    status_code=404,
                    code="INVENTORY_ITEM_NOT_FOUND",
                )

            if existing_movement is not None:
                return InventoryReservationResponse(
                    ok=True,
                    item=self._item_to_record(item),
                    movement=self._movement_to_record(existing_movement),
                    quote_id=quote_id,
                    message="La cotizacion ya tenia inventario reservado.",
                )

            before_available = int(item.available_quantity)
            before_reserved = int(item.reserved_quantity)
            quantity = int(quote.quantity)

            if before_available < quantity:
                raise AppError(
                    message="Inventario insuficiente para reservar esta cotizacion.",
                    status_code=409,
                    code="INSUFFICIENT_INVENTORY",
                )

            after_available = before_available - quantity
            after_reserved = before_reserved + quantity

            item.available_quantity = after_available
            item.reserved_quantity = after_reserved
            item.updated_at = utc_now_iso()

            movement = InventoryMovementModel(
                id=new_id("inv_move"),
                product_id=quote.product_id,
                movement_type="reservation",
                quantity=quantity,
                before_available=before_available,
                after_available=after_available,
                before_reserved=before_reserved,
                after_reserved=after_reserved,
                reference_type="quote",
                reference_id=quote_id,
                notes="Reserva de inventario desde cotizacion.",
                created_at=utc_now_iso(),
            )

            session.add(movement)
            session.commit()
            session.refresh(item)
            session.refresh(movement)

            audit_service.safe_record_event(
                event_type="inventory_reserved",
                actor_type="system",
                customer_id=quote.customer_id,
                entity_type="quote",
                entity_id=quote.id,
                summary="Inventario reservado desde cotizacion.",
                metadata={
                    "product_id": quote.product_id,
                    "quantity": quantity,
                    "before_available": before_available,
                    "after_available": after_available,
                    "before_reserved": before_reserved,
                    "after_reserved": after_reserved,
                },
            )

            return InventoryReservationResponse(
                ok=True,
                item=self._item_to_record(item),
                movement=self._movement_to_record(movement),
                quote_id=quote_id,
                message="Inventario reservado correctamente.",
            )

    def list_movements(
        self,
        product_id: str | None = None,
        limit: int = 100,
    ) -> list[InventoryMovementRecord]:
        with SessionLocal() as session:
            query = session.query(InventoryMovementModel)

            if product_id is not None:
                query = query.filter(InventoryMovementModel.product_id == product_id)

            rows = (
                query
                .order_by(InventoryMovementModel.created_at.desc())
                .limit(limit)
                .all()
            )

            return [self._movement_to_record(row) for row in rows]

    def _get_item_row(
        self,
        session,
        product_id: str,
    ) -> InventoryItemModel | None:
        return (
            session.query(InventoryItemModel)
            .filter(InventoryItemModel.product_id == product_id)
            .first()
        )

    def _get_or_create_item_row(
        self,
        session,
        product_id: str,
        unit: str,
    ) -> InventoryItemModel:
        row = self._get_item_row(
            session=session,
            product_id=product_id,
        )

        if row is not None:
            return row

        now = utc_now_iso()

        row = InventoryItemModel(
            id=new_id("inv"),
            product_id=product_id,
            available_quantity=0,
            reserved_quantity=0,
            unit=unit,
            created_at=now,
            updated_at=now,
        )

        session.add(row)
        session.flush()

        return row

    def _item_to_record(self, row: InventoryItemModel) -> InventoryItemRecord:
        return InventoryItemRecord(
            id=row.id,
            product_id=row.product_id,
            available_quantity=int(row.available_quantity),
            reserved_quantity=int(row.reserved_quantity),
            unit=row.unit,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def _movement_to_record(self, row: InventoryMovementModel) -> InventoryMovementRecord:
        return InventoryMovementRecord(
            id=row.id,
            product_id=row.product_id,
            movement_type=row.movement_type,
            quantity=int(row.quantity),
            before_available=int(row.before_available),
            after_available=int(row.after_available),
            before_reserved=int(row.before_reserved),
            after_reserved=int(row.after_reserved),
            reference_type=row.reference_type,
            reference_id=row.reference_id,
            notes=row.notes,
            created_at=row.created_at,
        )


inventory_service = InventoryService()
