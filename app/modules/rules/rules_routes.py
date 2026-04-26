from fastapi import APIRouter

from app.modules.rules.business_rules_service import business_rules_service
from app.modules.rules.rules_schemas import RuleEvaluationRequest, RuleEvaluationResult

router = APIRouter(prefix="/api", tags=["rules"])


@router.post("/rules/evaluate", response_model=RuleEvaluationResult)
async def evaluate_rules(payload: RuleEvaluationRequest) -> RuleEvaluationResult:
    return business_rules_service.evaluate(
        text=payload.text,
        intent=payload.intent,
        product_id=payload.product_id,
        quantity=payload.quantity,
        customer_type=payload.customer_type,
        has_phone=payload.has_phone,
        has_email=payload.has_email,
    )
