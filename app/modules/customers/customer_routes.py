from fastapi import APIRouter, Query

from app.modules.customers.customer_schemas import (
    CustomerCommercialSummary,
    CustomerRecord,
    CustomerUpdateRequest,
    CustomerUpdateResponse,
)
from app.modules.customers.customer_service import customer_service

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerRecord])
async def list_customers(
    customer_type: str | None = None,
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[CustomerRecord]:
    return customer_service.list_customers(
        customer_type=customer_type,
        status=status,
        limit=limit,
    )


@router.get("/{customer_id}", response_model=CustomerRecord)
async def get_customer(customer_id: str) -> CustomerRecord:
    return customer_service.get_customer(customer_id=customer_id)


@router.patch("/{customer_id}", response_model=CustomerUpdateResponse)
async def update_customer(
    customer_id: str,
    payload: CustomerUpdateRequest,
) -> CustomerUpdateResponse:
    return customer_service.update_customer(
        customer_id=customer_id,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        customer_type=payload.customer_type,
        status=payload.status,
        notes=payload.notes,
    )


@router.get("/{customer_id}/commercial-summary", response_model=CustomerCommercialSummary)
async def get_customer_commercial_summary(
    customer_id: str,
) -> CustomerCommercialSummary:
    return customer_service.commercial_summary(customer_id=customer_id)
