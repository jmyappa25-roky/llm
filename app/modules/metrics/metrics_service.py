from sqlalchemy import func

from app.modules.database.database import SessionLocal
from app.modules.database.models import (
    AIInvocationLogModel,
    AuditEventModel,
    ConversationModel,
    CustomerModel,
    InventoryItemModel,
    InventoryMovementModel,
    LeadModel,
    MessageModel,
    QuoteDraftModel,
    QuoteModel,
    TicketModel,
)
from app.modules.metrics.metrics_schemas import (
    AIMetrics,
    MetricsSummaryResponse,
    OperationalMetrics,
)


class MetricsService:
    def summary(self) -> MetricsSummaryResponse:
        return MetricsSummaryResponse(
            ok=True,
            operational=self._operational_metrics(),
            ai=self._ai_metrics(),
        )

    def _operational_metrics(self) -> OperationalMetrics:
        with SessionLocal() as session:
            return OperationalMetrics(
                customers=session.query(CustomerModel).count(),
                conversations=session.query(ConversationModel).count(),
                messages=session.query(MessageModel).count(),
                leads=session.query(LeadModel).count(),
                tickets=session.query(TicketModel).count(),
                quote_drafts=session.query(QuoteDraftModel).count(),
                quotes=session.query(QuoteModel).count(),
                inventory_items=session.query(InventoryItemModel).count(),
                inventory_movements=session.query(InventoryMovementModel).count(),
                audit_events=session.query(AuditEventModel).count(),
            )

    def _ai_metrics(self) -> AIMetrics:
        with SessionLocal() as session:
            total = session.query(AIInvocationLogModel).count()
            successful = (
                session.query(AIInvocationLogModel)
                .filter(AIInvocationLogModel.success.is_(True))
                .count()
            )
            failed = (
                session.query(AIInvocationLogModel)
                .filter(AIInvocationLogModel.success.is_(False))
                .count()
            )
            fallback = (
                session.query(AIInvocationLogModel)
                .filter(AIInvocationLogModel.used_fallback.is_(True))
                .count()
            )

            average_latency = session.query(func.avg(AIInvocationLogModel.latency_ms)).scalar()
            if average_latency is None:
                average_latency = 0.0

            provider_rows = (
                session.query(AIInvocationLogModel.provider, func.count(AIInvocationLogModel.id))
                .group_by(AIInvocationLogModel.provider)
                .all()
            )

            operation_rows = (
                session.query(AIInvocationLogModel.operation, func.count(AIInvocationLogModel.id))
                .group_by(AIInvocationLogModel.operation)
                .all()
            )

            provider_counts = {
                str(provider): int(count)
                for provider, count in provider_rows
            }

            operation_counts = {
                str(operation): int(count)
                for operation, count in operation_rows
            }

            return AIMetrics(
                total_invocations=total,
                successful_invocations=successful,
                failed_invocations=failed,
                fallback_invocations=fallback,
                average_latency_ms=round(float(average_latency), 2),
                provider_counts=provider_counts,
                operation_counts=operation_counts,
            )


metrics_service = MetricsService()
