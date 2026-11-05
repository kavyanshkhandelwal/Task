# Recommended Backend Improvements

These patterns are reference designs. They are not claimed to match Cynbit's current stack; adapt them to the repository and deployment conventions used by the engineering team.

## 1. Define API contracts with strict schemas

Use request models with field constraints and reject unexpected fields. Return stable error envelopes and never expose stack traces.

```python
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class InquiryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    company: str | None = Field(default=None, max_length=120)
    project_type: str = Field(min_length=2, max_length=40)
    message: str = Field(min_length=20, max_length=5000)
    consent: bool
```

## 2. Keep handlers thin; persist then enqueue

A public intake request should validate, persist a domain record, and enqueue notifications. Email/CRM outages should not erase the user's submission. Use a transactional outbox so a committed database record and its notification event cannot drift apart.

```python
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/inquiries", tags=["inquiries"])

@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_inquiry(payload: InquiryCreate):
    # Pseudocode: use one DB transaction for inquiry + outbox event.
    inquiry = await inquiry_service.create_with_outbox_event(payload)
    if inquiry is None:
        raise HTTPException(503, detail={"code": "temporarily_unavailable"})
    return {"id": str(inquiry.id), "status": "accepted"}
```

## 3. Rate-limit public endpoints

Use a shared store (e.g. Redis) for distributed rate limits. Tune limits per route and identity; do not rely only on in-process counters behind multiple instances. Return `429` with `Retry-After`. Also add bot detection and duplicate suppression for public intake.

## 4. Use safe, consistent errors

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from uuid import uuid4

app = FastAPI()

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    # Log exception with request ID internally; never return its details.
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Something went wrong", "request_id": request_id}},
    )
```

In production, ensure the logger records stack traces only in protected logs and redacts PII, cookies, authorization headers, and message bodies.

## 5. Apply browser security headers

Configure headers at the trusted reverse proxy or application boundary. A CSP must be tuned to actual first-party and third-party assets; do not blindly copy a policy that breaks the site.

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # Set HSTS only after HTTPS and all covered subdomains have been verified.
        return response
```

Use a nonce/hash-based CSP and configure `frame-ancestors` intentionally. Enable HSTS only after HTTPS is correct for every covered host.

## 6. Authentication and authorization

For product APIs, choose secure server-managed sessions or short-lived access tokens with rotating refresh tokens. Store browser session credentials in `HttpOnly`, `Secure`, `SameSite` cookies where appropriate. Enforce authorization at the service/data-access layer for every resource, not only in frontend routing. Use deny-by-default policies and tests for cross-user/cross-tenant object access.

## 7. Data and database practices

- Use parameterized queries or ORM bindings; never concatenate user input into SQL.
- Add unique constraints for canonical identifiers (e.g. normalized newsletter email).
- Use transactions for multi-record state changes and the outbox pattern for events.
- Add indexes from observed query plans, not guesses; review slow queries and connection pool saturation.
- Keep personal data separate by purpose; define retention/deletion jobs and backup expiry.

## 8. Operational visibility

Instrument request duration, status code, route template, dependency latency, queue depth, retries, and DB pool usage. Add trace/correlation IDs across API, worker, and email provider. Alert on error-rate spikes, queue backlog, repeated rate-limit hits, and unusual authentication failures. Logs must be structured and redacted.

## 9. Suggested implementation sequence

| Phase | Work | Exit criteria |
|---|---|---|
| 1 | Inventory actual routes and data flows | Approved route map, data classification, owner for every endpoint |
| 2 | Contracts and validation | OpenAPI spec, schema tests, payload-size limits |
| 3 | Security baseline | AuthZ tests, rate limits, CSRF/CORS policy, secure headers, secret scan |
| 4 | Reliability | Transactional outbox, retries/DLQ, idempotency, timeouts |
| 5 | Observability | Dashboards, redacted logs, traces, alert thresholds, SLOs |

## 10. Test strategy (authorized staging only)

- Unit tests for schema boundaries, invalid enum values, missing consent, overlong messages, and malformed email.
- Integration tests for transaction rollback, outbox delivery, idempotency, and duplicate subscription handling.
- Authorization tests using two synthetic users and resources owned by each user.
- Security-header and CORS tests against the staging origin.
- Upload tests only if an upload feature exists, using harmless synthetic files and an approved test bucket.
- Performance tests only with written scope, test data, a defined rate, and a staging environment.
