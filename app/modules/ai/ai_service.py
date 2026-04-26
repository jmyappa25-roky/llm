import os
import time

from app.config.env import settings
from app.modules.ai.ai_log_store import ai_invocation_log_store
from app.modules.ai.ai_schemas import (
    AIAnalysisRequest,
    AIAnalysisResult,
    AIStatusResponse,
)
from app.modules.ai.mock_provider import mock_ai_provider
from app.modules.ai.openai_provider import create_openai_provider


class AIService:
    def status(self) -> AIStatusResponse:
        return AIStatusResponse(
            ok=True,
            ai_mode=settings.AI_MODE,
            openai_enabled=settings.is_openai_enabled,
            model=settings.OPENAI_MODEL,
            use_openai_analysis=settings.AI_USE_OPENAI_ANALYSIS,
            use_openai_reply=settings.AI_USE_OPENAI_REPLY,
            max_output_tokens=settings.OPENAI_MAX_OUTPUT_TOKENS,
            timeout_seconds=settings.OPENAI_TIMEOUT_SECONDS,
        )

    def analyze(
        self,
        request: AIAnalysisRequest,
        operation: str = "analysis",
    ) -> AIAnalysisResult:
        if self._should_use_openai() is False:
            return self._analyze_with_mock(
                request=request,
                operation=operation,
                provider_name="mock",
            )

        started_at = time.perf_counter()

        try:
            provider = create_openai_provider()
            result = provider.analyze(request)
            latency_ms = self._latency_ms(started_at)

            ai_invocation_log_store.create_log(
                operation=operation,
                provider="openai",
                success=True,
                latency_ms=latency_ms,
                request_id=request.request_id,
                customer_id=request.customer_id,
                channel=request.channel,
                used_fallback=False,
            )

            return result

        except Exception as exc:
            latency_ms = self._latency_ms(started_at)
            error_type = self._classify_error(exc)

            ai_invocation_log_store.create_log(
                operation=operation,
                provider="openai",
                success=False,
                latency_ms=latency_ms,
                request_id=request.request_id,
                customer_id=request.customer_id,
                channel=request.channel,
                used_fallback=True,
                fallback_provider="local_fallback",
                error_type=error_type,
                error_message=str(exc),
            )

            fallback_result = mock_ai_provider.analyze(request)
            fallback_result.provider = "local_fallback"

            return fallback_result

    def smoke_test(self) -> AIAnalysisResult:
        request = AIAnalysisRequest(
            message="Hola quiero comprar 50 frascos de miel de maguey para una cafeteria en CDMX",
            channel="smoke_test",
            customer_id="smoke_test_customer",
            request_id="smoke_test_request",
            local_product="miel_maguey",
            local_quantity=50,
        )

        return self.analyze(
            request=request,
            operation="smoke_test",
        )

    def _analyze_with_mock(
        self,
        request: AIAnalysisRequest,
        operation: str,
        provider_name: str,
    ) -> AIAnalysisResult:
        started_at = time.perf_counter()

        result = mock_ai_provider.analyze(request)
        result.provider = provider_name

        ai_invocation_log_store.create_log(
            operation=operation,
            provider=provider_name,
            success=True,
            latency_ms=self._latency_ms(started_at),
            request_id=request.request_id,
            customer_id=request.customer_id,
            channel=request.channel,
            used_fallback=False,
        )

        return result

    def _should_use_openai(self) -> bool:
        if self._is_running_pytest():
            return False

        if not settings.should_use_openai_analysis:
            return False

        return True

    def _is_running_pytest(self) -> bool:
        return "PYTEST_CURRENT_TEST" in os.environ

    def _latency_ms(self, started_at: float) -> int:
        return int((time.perf_counter() - started_at) * 1000)

    def _classify_error(self, exc: Exception) -> str:
        message = str(exc).lower()

        if "quota" in message or "insufficient_quota" in message:
            return "quota_exceeded"

        if "429" in message or "rate limit" in message:
            return "rate_limit"

        if "timeout" in message or "timed out" in message:
            return "timeout"

        if "api key" in message or "authentication" in message or "401" in message:
            return "auth_error"

        if "json" in message:
            return "invalid_json"

        if "model" in message:
            return "model_error"

        return "openai_error"


ai_service = AIService()
