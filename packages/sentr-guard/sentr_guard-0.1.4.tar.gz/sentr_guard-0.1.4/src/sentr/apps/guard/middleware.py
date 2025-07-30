"""
FastAPI Guard Middleware for fraud detection.

Intercepts incoming requests, extracts payment data, and applies fraud detection verdicts.
"""

import time
from typing import Callable, Optional

import structlog
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from engine.decision_engine import DecisionEngine
from feature_store import PaymentAttempt

logger = structlog.get_logger(__name__)


class PaymentAttemptModel(BaseModel):
    """
    Minimal payment attempt model for middleware.

    Extracts essential fraud detection features from HTTP request.
    """

    ts: float = Field(..., description="Unix timestamp")
    merchant_id: str = Field(..., description="Merchant identifier")
    ip: str = Field(..., description="Client IP address")
    bin: Optional[str] = Field(None, description="Card BIN (first 6 digits)")
    amount: float = Field(..., description="Transaction amount")
    path: str = Field(..., description="Request path")
    headers: dict = Field(default_factory=dict, description="Request headers")

    @classmethod
    def from_request(cls, request: Request) -> "PaymentAttemptModel":
        """
        Extract payment attempt data from FastAPI request.

        Args:
            request: FastAPI request object

        Returns:
            PaymentAttemptModel instance
        """
        # Extract client IP (handle proxies)
        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.headers.get("x-real-ip", "")
        if not client_ip and request.client:
            client_ip = request.client.host
        if not client_ip:
            client_ip = "unknown"

        # Extract merchant ID from path or headers
        merchant_id = request.headers.get("x-merchant-id", "default")

        # Extract amount and BIN from headers (would typically come from request body)
        amount = float(request.headers.get("x-amount", "0"))
        bin_number = request.headers.get("x-card-bin")

        # Convert headers to dict (filter sensitive data)
        safe_headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ["authorization", "x-card-number", "cookie"]
        }

        return cls(
            ts=time.time(),
            merchant_id=merchant_id,
            ip=client_ip,
            bin=bin_number,
            amount=amount,
            path=str(request.url.path),
            headers=safe_headers,
        )

    def to_payment_attempt(self) -> PaymentAttempt:
        """Convert to core PaymentAttempt type."""
        return PaymentAttempt(
            ts=self.ts,
            merchant_id=self.merchant_id,
            ip=self.ip,
            bin=self.bin,
            amount=self.amount,
        )


class GuardMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that applies fraud detection to incoming requests.

    Intercepts requests, evaluates them through the decision engine,
    and applies appropriate actions (allow/block/challenge).
    """

    def __init__(self, app, decision_engine: DecisionEngine):
        """
        Initialize guard middleware.

        Args:
            app: FastAPI application instance
            decision_engine: Decision engine for fraud detection
        """
        super().__init__(app)
        self.decision_engine = decision_engine

        logger.info("Guard middleware initialized")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through fraud detection pipeline.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/route handler

        Returns:
            HTTP response (possibly modified by fraud detection)
        """
        start_time = time.perf_counter()

        # Skip guard for health and metrics endpoints
        if self._should_skip_guard(request):
            return await call_next(request)

        try:
            # Extract payment attempt data
            payment_data = PaymentAttemptModel.from_request(request)
            payment_attempt = payment_data.to_payment_attempt()

            logger.info(
                f"Middleware calling decision engine for {payment_attempt.merchant_id}"
            )
            # Get fraud detection verdict
            verdict = await self.decision_engine.score(payment_attempt)
            logger.info(f"Decision engine returned: {verdict.decision}")

            # Apply verdict
            response = await self._apply_verdict(request, call_next, verdict)

            # Add Sentr headers
            response.headers["X-Sentr-Decision"] = verdict.decision
            response.headers["X-Sentr-RuleRev"] = verdict.revision
            response.headers["X-Sentr-Score"] = str(verdict.score)

            # Log request processing
            processing_time = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Request processed",
                path=request.url.path,
                decision=verdict.decision,
                score=verdict.score,
                processing_time_ms=round(processing_time, 2),
                merchant_id=payment_attempt.merchant_id,
            )

            return response

        except Exception as e:
            # Fail open - allow request if decision engine fails
            logger.error(
                "Guard middleware error, failing open",
                error=str(e),
                path=request.url.path,
            )
            response = await call_next(request)
            response.headers["X-Sentr-Decision"] = "allow"
            response.headers["X-Sentr-Error"] = "engine_error"
            return response

    def _should_skip_guard(self, request: Request) -> bool:
        """
        Determine if guard should be skipped for this request.

        Args:
            request: HTTP request

        Returns:
            True if guard should be skipped
        """
        skip_paths = {"/healthz", "/metrics", "/docs", "/openapi.json"}
        return request.url.path in skip_paths

    async def _apply_verdict(
        self, request: Request, call_next: Callable, verdict
    ) -> Response:
        """
        Apply fraud detection verdict to request.

        Args:
            request: HTTP request
            call_next: Next handler
            verdict: Fraud detection verdict

        Returns:
            HTTP response based on verdict
        """
        if verdict.is_blocking:
            # Block the transaction
            return JSONResponse(
                status_code=402,  # Payment Required
                content={
                    "blocked": True,
                    "reason": "fraud_detected",
                    "reasons": list(verdict.reasons),
                    "score": verdict.score,
                    "revision": verdict.revision,
                },
            )

        elif verdict.is_challenging:
            # Require 3DS challenge - inject into request state
            request.state.sentr_action = "challenge_3ds"
            request.state.sentr_score = verdict.score
            request.state.sentr_reasons = verdict.reasons

            # Continue to next handler
            return await call_next(request)

        else:
            # Allow the transaction
            return await call_next(request)
