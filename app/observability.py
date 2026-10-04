"""Structured JSON logs, a correlation id on every request, health and Prometheus metrics."""

from __future__ import annotations

import contextvars
import json
import logging
import re
import sys
import time
import uuid
from collections import Counter
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

CORRELATION_HEADER = "x-correlation-id"
_VALID_CORRELATION = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)
log = logging.getLogger("wmd")


class ApiError(Exception):
    """An error with a stable code, returned as {"error": {"code", "message"}}."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str) -> None:
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname.lower(),
            "service": self.service,
            "message": record.getMessage(),
            "correlationId": correlation_id.get(),
            **getattr(record, "fields", {}),
        }
        if record.exc_info:
            entry["error"] = self.formatException(record.exc_info)
        return json.dumps(entry)


def configure_logging(service: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(service))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(logging.INFO)
    # The middleware logs each request once, with its correlation id.
    logging.getLogger("uvicorn.access").disabled = True


def outbound_headers() -> dict[str, str]:
    """Headers for calls to other services: carry the caller's correlation id."""
    value = correlation_id.get()
    return {CORRELATION_HEADER: value} if value else {}


class _Observability(BaseHTTPMiddleware):
    def __init__(self, app, requests: Counter) -> None:
        super().__init__(app)
        self.requests = requests

    async def dispatch(self, request: Request, call_next):
        incoming = request.headers.get(CORRELATION_HEADER, "")
        cid = incoming if _VALID_CORRELATION.match(incoming) else str(uuid.uuid4())
        token = correlation_id.set(cid)
        started = time.perf_counter()
        try:
            response = await call_next(request)
            route = request.scope.get("route")
            path = getattr(route, "path", "unmatched")
            self.requests[(request.method, path, response.status_code)] += 1
            response.headers[CORRELATION_HEADER] = cid
            if path not in ("/healthz", "/readyz", "/metrics"):
                log.info(
                    "request",
                    extra={
                        "fields": {
                            "method": request.method,
                            "path": path,
                            "status": response.status_code,
                            "durationMs": round((time.perf_counter() - started) * 1000, 1),
                        }
                    },
                )
            return response
        finally:
            correlation_id.reset(token)


def install(app: FastAPI, ready_check) -> None:
    """Middleware, error shape, /healthz, /readyz and /metrics."""
    requests: Counter = Counter()
    app.add_middleware(_Observability, requests=requests)

    @app.exception_handler(ApiError)
    async def _api_error(_request: Request, error: ApiError) -> JSONResponse:
        return JSONResponse(
            {"error": {"code": error.code, "message": error.message}}, status_code=error.status
        )

    @app.get("/healthz", include_in_schema=False)
    def healthz() -> dict:
        return {"status": "ok"}

    @app.get("/readyz", include_in_schema=False)
    def readyz() -> dict:
        ready_check()
        return {"status": "ready"}

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> PlainTextResponse:
        lines = ["# TYPE http_requests_total counter"]
        for (method, path, status), count in sorted(requests.items()):
            lines.append(
                f'http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
            )
        return PlainTextResponse("\n".join(lines) + "\n")
