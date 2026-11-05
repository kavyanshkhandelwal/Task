"""Illustrative FastAPI middleware for request IDs and baseline headers.

Tune CSP directives to the actual frontend and third-party integrations.
Do not enable HSTS preload/includeSubDomains without verifying every subdomain.
"""
from uuid import uuid4
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; upgrade-insecure-requests"
        )
        # Enable only when the deployment is HTTPS-only and all subdomains are ready:
        # response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)
