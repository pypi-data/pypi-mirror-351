"""
FastAPI Guard Service - Main application.

Production-ready fraud detection service with middleware, metrics, and health checks.
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from common.enums import ErrorReason
from engine.decision_engine import DecisionEngine, RedisUnavailableError

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global decision engine instance
decision_engine: DecisionEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    global decision_engine

    # Startup
    logger.info("Starting Sentr Guard Service")

    # Get configuration from environment
    redis_url = os.getenv("SENTR_REDIS_URL", "redis://localhost:6379/0")
    rules_path = os.getenv("SENTR_RULES_PATH", "rules/default_card_test.yml")
    enable_graph = os.getenv("SENTR_ENABLE_GRAPH", "false").lower() == "true"

    try:
        # Initialize decision engine
        decision_engine = await DecisionEngine.create(
            redis_url=redis_url, rules_path=rules_path, enable_graph=enable_graph
        )

        logger.info(
            "Decision engine initialized",
            redis_url=redis_url,
            rules_path=rules_path,
            enable_graph=enable_graph,
        )

        yield

    except Exception as e:
        logger.error("Failed to initialize decision engine", error=str(e))
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Sentr Guard Service")
        if decision_engine and decision_engine.redis_client:
            await decision_engine.redis_client.aclose()


# Create FastAPI application
app = FastAPI(
    title="Sentr Guard Service",
    description="Fraud detection guard service",
    version="1.0.0",
    lifespan=lifespan,
)


# Add guard middleware
@app.middleware("http")
async def guard_middleware(request: Request, call_next):
    """Guard middleware wrapper."""
    global decision_engine

    if decision_engine is None:
        # Service not ready
        return JSONResponse(status_code=503, content={"error": "service_not_ready"})

    # Skip guard for health and metrics endpoints
    skip_paths = {"/healthz", "/metrics", "/docs", "/openapi.json", "/"}
    if request.url.path in skip_paths:
        return await call_next(request)

    # Apply guard logic directly
    import time

    from .middleware import PaymentAttemptModel

    print(f"GUARD MIDDLEWARE CALLED: {request.url.path}")
    start_time = time.perf_counter()

    try:
        # Extract payment attempt data
        payment_data = PaymentAttemptModel.from_request(request)
        payment_attempt = payment_data.to_payment_attempt()

        # Quick Redis health check before processing
        try:
            print("MIDDLEWARE: Testing Redis connectivity")
            await decision_engine.redis_client.ping()
            print("MIDDLEWARE: Redis OK")
        except Exception as e:
            print(f"MIDDLEWARE: Redis failed: {e}")
            # Redis is unavailable - return 402 immediately
            return JSONResponse(
                status_code=402,
                content={
                    "blocked": True,
                    "reason": ErrorReason.REDIS_DOWN,
                    "message": "Service temporarily unavailable",
                },
                headers={
                    "X-Sentr-Decision": "block",
                    "X-Sentr-Error": ErrorReason.REDIS_DOWN,
                },
            )

        logger.info(
            f"Middleware calling decision engine for {payment_attempt.merchant_id}"
        )
        # Get fraud detection verdict
        try:
            verdict = await decision_engine.score(payment_attempt)
            logger.info(f"Decision engine returned: {verdict.decision}")
        except RedisUnavailableError as e:
            logger.error("Redis unavailable in middleware", error=str(e))
            # Re-raise to be handled by outer exception handler
            raise
        except Exception as e:
            logger.error(
                "Unexpected error from decision engine",
                error_type=type(e).__name__,
                error=str(e),
            )
            # Re-raise to be handled by outer exception handler
            raise

        # Apply verdict
        if verdict.is_blocking:
            # Block the transaction
            response = JSONResponse(
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
            response = await call_next(request)
        else:
            # Allow the transaction
            response = await call_next(request)

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

    except RedisUnavailableError as e:
        # Redis is specifically unavailable - return 402 Payment Required
        logger.warning(
            "Redis unavailable, blocking transaction",
            error=str(e),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=402,
            content={
                "blocked": True,
                "reason": ErrorReason.REDIS_DOWN,
                "message": "Service temporarily unavailable",
            },
            headers={
                "X-Sentr-Decision": "block",
                "X-Sentr-Error": ErrorReason.REDIS_DOWN,
            },
        )
    except Exception as e:
        # For non-Redis errors, fail open - allow request
        logger.error(
            "Guard middleware error, failing open", error=str(e), path=request.url.path
        )
        response = await call_next(request)
        response.headers["X-Sentr-Decision"] = "allow"
        response.headers["X-Sentr-Error"] = "engine_error"
        return response


@app.get("/healthz")
async def health_check():
    """
    Health check endpoint.

    Returns 200 if Redis is accessible and rules are loaded.
    """
    global decision_engine

    if decision_engine is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "reason": "decision_engine_not_initialized",
            },
        )

    try:
        # Test Redis connectivity
        await decision_engine.redis_client.ping()

        # Check if ruleset is loaded
        rules_count = len(decision_engine.ruleset.rules)

        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "rules_count": rules_count,
                "revision": decision_engine.ruleset.revision_hash,
                "graph_enabled": decision_engine.enable_graph,
            },
        )

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503, content={"status": "unhealthy", "reason": str(e)}
        )


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus format.
    """
    return PlainTextResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/checkout")
async def checkout(request: Request):
    """
    Mock checkout endpoint for testing.

    This would normally be your payment processing endpoint.
    """
    # Check if 3DS challenge is required
    if (
        hasattr(request.state, "sentr_action")
        and request.state.sentr_action == "challenge_3ds"
    ):
        return JSONResponse(
            status_code=200,
            content={
                "status": "challenge_required",
                "action": "3ds_challenge",
                "score": request.state.sentr_score,
                "reasons": list(request.state.sentr_reasons),
            },
        )

    # Normal processing
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "transaction_id": "txn_123456789",
            "message": "Payment processed successfully",
        },
    )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    global decision_engine

    return JSONResponse(
        content={
            "service": "sentr-guard",
            "version": "1.0.0",
            "status": "running" if decision_engine else "initializing",
            "endpoints": {
                "health": "/healthz",
                "metrics": "/metrics",
                "checkout": "/checkout",
            },
        }
    )


def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    return app


def main():
    """Run the FastAPI application."""
    import uvicorn

    # Configuration from environment
    host = os.getenv("SENTR_HOST", "0.0.0.0")
    port = int(os.getenv("SENTR_PORT", "8000"))
    workers = int(os.getenv("SENTR_WORKERS", "1"))
    log_level = os.getenv("SENTR_LOG_LEVEL", "info")

    # Run with uvicorn
    uvicorn.run(
        "apps.guard.fastapi_app:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        loop="uvloop",  # Use uvloop for better async performance
        access_log=True,
    )


if __name__ == "__main__":
    main()
