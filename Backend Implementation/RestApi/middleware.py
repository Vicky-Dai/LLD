import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach trace_id and log request latency for every HTTP call."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
        request.state.trace_id = trace_id

        start = time.perf_counter()
        logger.info(
            "request_started method=%s path=%s trace_id=%s client=%s",
            request.method,
            request.url.path,
            trace_id,
            request.client.host if request.client else "unknown",
        )

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "request_failed method=%s path=%s trace_id=%s elapsed_ms=%.2f",
                request.method,
                request.url.path,
                trace_id,
                elapsed_ms,
            )
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Trace-Id"] = trace_id
        logger.info(
            "request_completed method=%s path=%s status=%s trace_id=%s elapsed_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            trace_id,
            elapsed_ms,
        )
        return response
