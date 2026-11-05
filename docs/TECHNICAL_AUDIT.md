# Cynbit — Backend Technical Audit

## 1. Executive summary
This report reviews Cynbit from a backend developer's perspective using only the publicly accessible website and publicly visible user journeys. It focuses on how public web workflows typically cross backend trust boundaries: content delivery, contact/inquiry intake, careers applications, newsletter subscriptions, and linked integrations.

**This is not a penetration test or source-code review.** No private API, authenticated account, database, server configuration, cloud account, or internal log was accessed. The report distinguishes public-surface evidence from hypotheses requiring authorized verification.

### Overall assessment
The strongest improvement opportunities concern public submission handling, security headers and transport policy, request validation, abuse prevention, personal-data lifecycle, and operational observability. Backend controls must be verified from actual HTTP responses and in staging before any issue is classified as a confirmed defect.

## 2. Scope
**In scope:** public pages reachable without login; visible navigation and business workflows; passive HTTP metadata checks; defensive backend architecture recommendations.

**Out of scope:** credential guessing, account enumeration, password reset manipulation, authorization bypass, IDOR, injection attempts, fuzzing, form submissions, file uploads, bulk requests, crawling, load testing, denial-of-service testing, private endpoints, admin interfaces, employee data, source repositories, or non-public infrastructure.

## 3. Methodology and evidence taxonomy
1. Review public pages and identify journeys that appear to collect or route data.
2. Map each journey to backend responsibilities without assuming a framework or database.
3. Review response metadata exposed by conservative GET requests.
4. Recommend defensive controls and define safe verification by an authorized owner.

Evidence labels:
- **Observed:** directly visible on the public website or in a captured public HTTP response.
- **Inferred:** reasonable architectural interpretation, not proof of implementation.
- **Verify:** requires server-side evidence, a test account, owner confirmation, or authorized staging test.

A lack of visibility is not evidence that a control is absent.

## 4. Public workflow / backend boundary map

| Public journey | Likely backend responsibility | Important controls |
|---|---|---|
| Company and service pages | CMS or static content delivery | HTTPS, cache policy, CSP, safe redirects |
| Contact / inquiry journey, if enabled | Accept, validate, persist, notify or route a lead | Schema validation, anti-abuse, idempotency, consent, PII minimization |
| Careers / application journey, if enabled | Candidate data and resume attachments | File validation, private object storage, retention, access control |
| Newsletter journey, if enabled | Subscription lifecycle and provider integration | Double opt-in, duplicate handling, unsubscribe, consent evidence |
| Third-party links or embedded forms | Cross-origin integration and vendor transfer | Origin allowlist, vendor review, minimal data sharing |

These are candidate responsibilities based on public journey types, not assertions that Cynbit uses a particular API or vendor.

## 5. Candidate architecture

```text
Browser
  |
 HTTPS
  v
CDN / WAF / Edge
  |
Web application / API gateway
  +--> Public content service / CMS
  +--> Inquiry service ------> Relational DB
  |          +---------------> Queue -> Notification worker
  +--> Careers service ------> Private object storage
  +--> Newsletter adapter ---> Consent-aware email provider
  +--> Central logs, metrics, traces, audit events
```

Keep public read-only content cacheable at the edge. Put writes behind server-side validation and abuse controls. Queue non-critical notifications after durable acceptance. Store candidate documents privately with short-lived signed downloads. Persist consent and retention metadata. Enforce authorization in the service/data layer, not only the frontend.

## 6. API design review checklist
No private API inventory is asserted. For every discovered or owner-provided endpoint, document:

| Area | Review questions |
|---|---|
| Contract | Are method, path, schema, response, and error model documented? |
| Validation | Are length, format, enum, range, and cross-field constraints enforced server-side? |
| Authentication | Is authentication required where appropriate? Are tokens safely stored and rotated? |
| Authorization | Is every object access checked against principal and tenant? |
| Error handling | Are errors stable, non-sensitive, and traceable with correlation IDs? |
| Idempotency | Can retries create duplicate inquiries, applications, or subscriptions? |
| Pagination | Are list endpoints bounded and semantics explicit? |
| Rate limiting | Are unauthenticated write endpoints protected by fair limits? |
| Observability | Are latency, failure rate, queue lag, and dependency errors measured? |
| Versioning | Are breaking changes managed and documented? |

### Suggested inquiry contract (recommendation, not observed endpoint)
- `POST /api/v1/inquiries`
- Request: `name`, `email`, `message`, `consent`, optional `source`.
- Success: `202 Accepted` with generic receipt and request ID.
- Validation failure: `422 Unprocessable Entity` with safe field errors.
- Rate limited: `429 Too Many Requests` with `Retry-After`.
- Never expose SQL errors, stack traces, provider credentials, or internal hostnames.

## 7. Security review

### Public write paths
If inquiry, application, or subscription endpoints exist, treat them as untrusted-input boundaries:
- Enforce allowlisted schemas and maximum payload sizes server-side.
- Encode output in any admin interface that displays submitted text.
- Apply rate limits, bot controls, and duplicate suppression.
- Record consent and purpose; minimize collected personal data.
- Store documents privately using random object keys and short-lived signed downloads.
- Validate upload content type and file signatures; never trust client MIME alone.

### Authentication and authorization
If authenticated portals exist beyond public pages:
- Use a vetted identity provider or mature framework implementation.
- Prefer secure, HttpOnly, SameSite cookies for browser sessions; protect cookie-authenticated writes against CSRF.
- Rotate session identifiers after authentication and privilege changes.
- Enforce role and object ownership checks on every request.
- Avoid long-lived bearer tokens in browser local storage.
- Log security events without secrets or complete personal payloads.

These are recommendations. Public browsing does not prove whether Cynbit has authenticated product features.

### Browser and transport controls
Review actual responses for HSTS (after HTTPS/subdomain readiness), a practical CSP, X-Content-Type-Options: nosniff, Referrer-Policy, restrictive Permissions-Policy, secure redirects, and cookie attributes. A header scan is point-in-time evidence, not a full security assessment.

## 8. Performance and reliability
Measure:
- p50/p95/p99 server duration by endpoint.
- TTFB and asset caching from representative geographies.
- Database query latency and connection-pool saturation.
- External provider latency and timeout rates.
- Queue depth, oldest-message age, retries, and dead-letter volume.
- 4xx/5xx rates by route and release.

Recommended controls: CDN caching for public assets; compression and correct cache-control; bounded pagination; query indexes based on observed plans; outbound timeouts and retry budgets with exponential backoff and jitter; graceful degradation for optional vendors; asynchronous email/CRM side effects; connection pooling.

Do not optimize from assumptions. Measure representative traffic and profile the slowest paths first.

## 9. Error handling and operations
Use a stable, non-sensitive error envelope:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Please review the highlighted fields.",
    "request_id": "req_01J..."
  }
}
```

Use structured logs with request IDs, distributed traces across API/DB/worker boundaries, dashboards for latency/error/queue signals, and alerts on actionable symptoms. Do not log passwords, tokens, full message bodies, or uploaded document contents.

## 10. Prioritized next steps
1. Inventory public and authenticated endpoints with the application owner.
2. Write OpenAPI contracts for public write workflows.
3. Add schema validation, request-size limits, rate limiting, and idempotency.
4. Review consent, retention, access boundaries, and upload storage.
5. Establish latency/error/dependency dashboards and safe alert thresholds.
6. Run an authorized staging test plan with test accounts and synthetic data.

## 11. Limitations
Public frontend behavior cannot reveal database schema, internal API topology, access-control policy, server-side validation, secrets management, deployment topology, or monitoring coverage. No vulnerability should be claimed in these areas without corroborating server-side or authorized test evidence.
