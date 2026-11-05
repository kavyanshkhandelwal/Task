"""Illustrative FastAPI middleware. Tune CSP/hosts for the real deployment.

HSTS is opt-in: only enable it after HTTPS is correctly configured for every
host covered by the policy. Do not trust arbitrary client-supplied request IDs.
"""
import os
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()


class RequestContextAndHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        supplied_id = request.headers.get("X-Request-ID", "")
        # Accept only a UUID-shaped identifier; otherwise generate our own.
        try:
            request_id = str(uuid4()) if not supplied_id else str(__import__("uuid").UUID(supplied_id))
        except (ValueError, AttributeError):
            request_id = str(uuid4())

        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # Add CSP after enumerating the production app's required origins.
        # Example baseline (may need changes for analytics, fonts, or embeds):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'"
        )

        if os.getenv("ENABLE_HSTS", "").lower() == "true":
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response


app.add_middleware(RequestContextAndHeaders)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    # Log exception + request ID to a protected, redacted logger in production.
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Something went wrong",
                "request_id": request_id,
            }
        },
    )
