from datetime import datetime, timedelta, timezone

from app.core.errors import AppError
from app.core.ids import new_id
from app.modules.audit.audit_service import audit_service
from app.modules.database.database import SessionLocal, init_db
from app.modules.database.models import QuoteDraftModel, QuoteModel
from app.modules.quotes.quote_pricing import get_price_rule
from app.modules.quotes.quote_schemas import (
    QuoteCalculationPreview,
    QuoteCreateFromDraftResponse,
    QuoteRecord,
    QuoteStatusUpdateResponse,
)


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def utc_days_from_now_iso(days: int) -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        + timedelta(days=days)
    ).isoformat().replace("+00:00", "Z")


class QuoteService:
    def __init__(self) -> None:
        init_db()

    def create_from_draft(self, quote_draft_id: str) -> QuoteCreateFromDraftResponse:
        with SessionLocal() as session:
            existing = (
                session.query(QuoteModel)
                .filter(QuoteModel.quote_draft_id == quote_draft_id)
                .first()
            )

            if existing is not None:
                return QuoteCreateFromDraftResponse(
                    ok=True,
                    quote=self._to_record(existing),
                    message="La cotizacion ya existia para este borrador.",
                )

            draft = (
                session.query(QuoteDraftModel)
                .filter(QuoteDraftModel.id == quote_draft_id)
                .first()
            )

            if draft is None:
                raise AppError(
                    message="Borrador de cotizacion no encontrado.",
                    status_code=404,
                    code="QUOTE_DRAFT_NOT_FOUND",
                )

            if draft.product_id is None:
                raise AppError(
                    message="El borrador no tiene producto asociado.",
                    status_code=400,
                    code="QUOTE_DRAFT_WITHOUT_PRODUCT",
                )

            if draft.quantity is None or draft.quantity <= 0:
                raise AppError(
                    message="El borrador no tiene cantidad valida.",
                    status_code=400,
                    code="QUOTE_DRAFT_WITHOUT_QUANTITY",
                )

            calculation = self.calculate_quote(
                product_id=draft.product_id,
                quantity=draft.quantity,
            )

            now = utc_now_iso()
            status = "pending_approval" if draft.requires_human_approval else "draft"

            row = QuoteModel(
                id=new_id("quote_real"),
                quote_draft_id=draft.id,
                conversation_id=draft.conversation_id,
                customer_id=draft.customer_id,
                product_id=draft.product_id,
                quantity=draft.quantity,
                unit_price_mxn=calculation.unit_price_mxn,
                subtotal_mxn=calculation.subtotal_mxn,
                discount_percent=calculation.discount_percent,
                discount_mxn=calculation.discount_mxn,
                shipping_mxn=calculation.shipping_mxn,
                total_mxn=calculation.total_mxn,
                status=status,
                requires_human_approval=draft.requires_human_approval,
                valid_until=utc_days_from_now_iso(7),
                notes=(
                    "Cotizacion estimada generada por el sistema. "
                    "Debe revisarse disponibilidad, logistica y condiciones comerciales antes de confirmar."
                ),
                created_at=now,
                updated_at=now,
            )

            session.add(row)
            session.commit()
            session.refresh(row)

            audit_service.safe_record_event(
                event_type="quote_created",
                actor_type="system",
                customer_id=row.customer_id,
                entity_type="quote",
                entity_id=row.id,
                summary="Cotizacion comercial creada desde borrador.",
                metadata={
                    "quote_draft_id": row.quote_draft_id,
                    "product_id": row.product_id,
                    "quantity": row.quantity,
                    "total_mxn": row.total_mxn,
                    "status": row.status,
                },
            )

            return QuoteCreateFromDraftResponse(
                ok=True,
                quote=self._to_record(row),
                message="Cotizacion creada correctamente desde borrador.",
            )

    def calculate_quote(self, product_id: str, quantity: int) -> QuoteCalculationPreview:
        if quantity <= 0:
            raise AppError(
                message="La cantidad debe ser mayor a cero.",
                status_code=400,
                code="INVALID_QUANTITY",
            )

        rule = get_price_rule(product_id)

        if rule is None:
            raise AppError(
                message="No existe regla de precio para este producto.",
                status_code=400,
                code="PRICE_RULE_NOT_FOUND",
            )

        subtotal = round(rule.unit_price_mxn * quantity, 2)

        discount_percent = 0.0
        if quantity >= rule.wholesale_min_quantity:
            discount_percent = rule.wholesale_discount_percent

        discount_mxn = round(subtotal * (discount_percent / 100), 2)
        shipping_mxn = self._calculate_shipping(quantity=quantity)
        total = round(subtotal - discount_mxn + shipping_mxn, 2)

        notes = [
            "Precios de referencia para MVP local.",
            "No confirmar venta sin revisar disponibilidad.",
            "No confirmar envio sin validar zona y logistica.",
        ]

        return QuoteCalculationPreview(
            product_id=product_id,
            quantity=quantity,
            unit_price_mxn=rule.unit_price_mxn,
            subtotal_mxn=subtotal,
            discount_percent=discount_percent,
            discount_mxn=discount_mxn,
            shipping_mxn=shipping_mxn,
            total_mxn=total,
            notes=notes,
        )

    def list_quotes(
        self,
        customer_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[QuoteRecord]:
        with SessionLocal() as session:
            query = session.query(QuoteModel)

            if customer_id is not None:
                query = query.filter(QuoteModel.customer_id == customer_id)

            if status is not None:
                query = query.filter(QuoteModel.status == status)

            rows = (
                query
                .order_by(QuoteModel.created_at.desc())
                .limit(limit)
                .all()
            )

            return [self._to_record(row) for row in rows]

    def get_quote(self, quote_id: str) -> QuoteRecord:
        with SessionLocal() as session:
            row = (
                session.query(QuoteModel)
                .filter(QuoteModel.id == quote_id)
                .first()
            )

            if row is None:
                raise AppError(
                    message="Cotizacion no encontrada.",
                    status_code=404,
                    code="QUOTE_NOT_FOUND",
                )

            return self._to_record(row)

    def approve_quote(self, quote_id: str) -> QuoteStatusUpdateResponse:
        return self._update_status(
            quote_id=quote_id,
            new_status="approved",
            event_type="quote_approved",
            message="Cotizacion aprobada correctamente.",
        )

    def send_quote(self, quote_id: str) -> QuoteStatusUpdateResponse:
        with SessionLocal() as session:
            row = (
                session.query(QuoteModel)
                .filter(QuoteModel.id == quote_id)
                .first()
            )

            if row is None:
                raise AppError(
                    message="Cotizacion no encontrada.",
                    status_code=404,
                    code="QUOTE_NOT_FOUND",
                )

            if row.requires_human_approval and row.status != "approved":
                raise AppError(
                    message="Esta cotizacion requiere aprobacion humana antes de enviarse.",
                    status_code=409,
                    code="QUOTE_REQUIRES_APPROVAL",
                )

        return self._update_status(
            quote_id=quote_id,
            new_status="sent",
            event_type="quote_sent",
            message="Cotizacion marcada como enviada.",
        )

    def _update_status(
        self,
        quote_id: str,
        new_status: str,
        event_type: str,
        message: str,
    ) -> QuoteStatusUpdateResponse:
        with SessionLocal() as session:
            row = (
                session.query(QuoteModel)
                .filter(QuoteModel.id == quote_id)
                .first()
            )

            if row is None:
                raise AppError(
                    message="Cotizacion no encontrada.",
                    status_code=404,
                    code="QUOTE_NOT_FOUND",
                )

            old_status = row.status
            row.status = new_status
            row.updated_at = utc_now_iso()

            session.commit()
            session.refresh(row)

            audit_service.safe_record_event(
                event_type=event_type,
                actor_type="admin",
                customer_id=row.customer_id,
                entity_type="quote",
                entity_id=row.id,
                summary=f"Cotizacion actualizada de {old_status} a {new_status}.",
                metadata={
                    "old_status": old_status,
                    "new_status": new_status,
                    "total_mxn": row.total_mxn,
                },
            )

            return QuoteStatusUpdateResponse(
                ok=True,
                quote=self._to_record(row),
                old_status=old_status,
                new_status=new_status,
                message=message,
            )

    def _calculate_shipping(self, quantity: int) -> float:
        if quantity >= 50:
            return 0.0

        return 120.0

    def _to_record(self, row: QuoteModel) -> QuoteRecord:
        return QuoteRecord(
            id=row.id,
            quote_draft_id=row.quote_draft_id,
            conversation_id=row.conversation_id,
            customer_id=row.customer_id,
            product_id=row.product_id,
            quantity=row.quantity,
            unit_price_mxn=float(row.unit_price_mxn),
            subtotal_mxn=float(row.subtotal_mxn),
            discount_percent=float(row.discount_percent),
            discount_mxn=float(row.discount_mxn),
            shipping_mxn=float(row.shipping_mxn),
            total_mxn=float(row.total_mxn),
            status=row.status,
            requires_human_approval=bool(row.requires_human_approval),
            valid_until=row.valid_until,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


quote_service = QuoteService()
