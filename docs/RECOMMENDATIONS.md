# Recommended Backend Improvements

The patterns below are reference designs. They are not claimed to match Cynbit's current stack; adapt them to the repository and deployment conventions used by the engineering team.

## 1. Validate public inquiry input with a typed schema

See [inquiry_schema.py](../examples/inquiry_schema.py). Enforce strict field types, bounds, normalization, consent requirements, and safe error responses. Validate again at the service boundary even when frontend validation exists.

## 2. Add security headers and request correlation

See [security_middleware.py](../examples/security_middleware.py). Use a restrictive but application-compatible CSP, HSTS only after HTTPS readiness, MIME sniffing protection, referrer policy, and request IDs. Do not blindly copy a CSP without enumerating required script, image, font, and frame origins.

## 3. Rate limit public write endpoints

Use a shared store (for example Redis) so limits work across multiple API instances. Apply separate policies by endpoint and risk; combine IP limits with idempotency and bot mitigation rather than treating an IP address as a user identity. See [rate_limit_design.md](rate_limit_design.md).

## 4. Persist first, notify asynchronously

Recommended inquiry flow:
1. Validate and normalize request.
2. Apply abuse controls and idempotency.
3. Persist inquiry and outbox event in one database transaction.
4. Return `202 Accepted` with a request identifier.
5. Worker delivers email/CRM notification with bounded retries.
6. Move exhausted messages to a dead-letter queue and alert operators.

This avoids coupling successful intake to a transient mail provider outage. An outbox table prevents a database commit succeeding while queue publication is lost.

## 5. Protect candidate uploads
- Allow only business-required formats and strict size limits.
- Verify file signatures, not only filename or browser MIME.
- Generate opaque object keys; store outside public web root.
- Scan files in an isolated worker; do not execute or render originals inline.
- Use short-lived signed URLs after authorization.
- Encrypt storage and define retention/deletion.

## 6. Authentication and authorization
- Prefer a mature OIDC provider or well-maintained auth framework.
- Use short-lived access credentials and refresh rotation where token-based flows are necessary.
- For browser sessions use Secure, HttpOnly, SameSite cookies and CSRF defense.
- Perform authorization in each service operation and query, including object ownership and tenant scope.
- Test with two distinct staging principals and synthetic records; verify that changing an object identifier never crosses the boundary.

## 7. Performance and reliability
- Establish a baseline before tuning.
- Cache immutable static assets at CDN; use explicit cache-control for personalized responses.
- Add database indexes based on query plans and real filter/sort patterns.
- Bound all list queries and payload sizes.
- Add outbound timeouts, retry budgets, backoff+jitter, and circuit-breaking for optional dependencies.
- Measure p95/p99 latency, DB pool use, queue age, and dependency errors.

## 8. Operational quality
- Version APIs and publish OpenAPI contracts.
- Use structured logs and trace IDs across API, DB, and asynchronous workers.
- Keep secrets in a managed secret store and rotate them.
- Add dependency and container scanning to CI.
- Maintain incident runbooks and test backup restoration.

## Example endpoint contract
```http
POST /api/v1/inquiries
Content-Type: application/json
Idempotency-Key: 74cc... (client-generated opaque value)
```
Return 202 on durable acceptance; 422 for invalid fields; 429 with Retry-After for throttling; and a generic 5xx on unexpected failures with a request ID. Never expose provider or database implementation details.
