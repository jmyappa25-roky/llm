from fastapi import APIRouter

from app.modules.chat.chat_schemas import ChatAnalysis, ChatDecision
from app.modules.orchestration.decision_service import decision_orchestrator
from app.modules.orchestration.orchestration_schemas import DecisionEvaluationRequest

router = APIRouter(prefix="/api", tags=["orchestration"])


@router.post("/decisions/evaluate", response_model=ChatDecision)
async def evaluate_decision(payload: DecisionEvaluationRequest) -> ChatDecision:
    analysis = ChatAnalysis(
        intent=payload.intent,
        customer_type=payload.customer_type,
        product=payload.product,
        quantity=payload.quantity,
        urgency=payload.urgency,
        needs_human=payload.needs_human,
        blocked=payload.blocked,
        missing_data=payload.missing_data,
        safety_flags=payload.safety_flags,
        rule_reasons=payload.rule_reasons,
        confidence=payload.confidence,
    )

    return decision_orchestrator.decide(analysis)
