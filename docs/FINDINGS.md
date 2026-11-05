# Security & Performance Findings

This register separates observable public facts from risks that require internal verification.

| ID | Category | Finding / risk | Evidence status | Severity if control is absent | Recommendation |
|---|---|---|---|---|---|
| F-01 | API documentation | No public API contract or OpenAPI reference was identified in the reviewed pages. | Observed limitation; not a vulnerability | Medium (maintainability) | Publish versioned OpenAPI docs for supported APIs; keep internal schemas access-controlled. |
| F-02 | Input validation | Contact, career, and newsletter journeys imply data intake, but server-side validation cannot be assessed from page content. | Not publicly verifiable | High | Use strict request schemas, length limits, allowlists, normalization, and server-side validation. |
| F-03 | Abuse prevention | Public inquiry/subscription entry points can attract spam or automated submissions. Actual rate limiting is unknown. | Recommendation based on exposed user journeys | Medium | Apply per-IP and per-identity rate limits, bot controls, duplicate suppression, and monitoring. |
| F-04 | Privacy / consent | Newsletter CTA and contact/career pages imply collection of personal information; consent and retention implementation were not validated. | CTA observed; processing unknown | High | Record purpose-specific consent, retention, deletion, and access controls. |
| F-05 | File upload safety | Career applications may involve CV uploads, but no upload behaviour was tested or assumed. | Not publicly verifiable | High if uploads exist without controls | If uploads are supported, enforce MIME/size limits, malware scanning, private storage, random object keys, and short-lived signed URLs. |
| F-06 | Reliability | Email/CRM notifications tied to intake workflows can fail or increase request latency if performed synchronously. Actual design is unknown. | Recommendation | Medium | Persist request first, enqueue event transactionally (outbox pattern), and process with retry/backoff + DLQ. |
| F-07 | Performance | Public site performance and backend latency were not benchmarked; no load or synthetic performance test was run. | Not measured | Unknown | Establish RUM/APM baselines and p95/p99 SLOs before optimization. |
| F-08 | Authentication / authorization | No authenticated application flow was in scope; session handling and object-level authorization remain unverified. | Not publicly verifiable | Critical if absent on private APIs | Review token/session lifecycle and enforce resource ownership checks server-side. |
| F-09 | Browser/API boundary | CORS, CSRF, CSP, cookie flags, and security headers were not independently assessed as a full control set. | Not publicly verifiable | High | Validate headers in staging and apply restrictive, environment-specific policies. |
| F-10 | Observability | Public content does not expose operational telemetry or incident practices. | Not publicly verifiable | Medium | Add correlation IDs, redacted structured logs, traces, error budgets, and alerts. |

## Prioritization

1. **P0 / before processing sensitive data:** schema validation, authorization, PII minimization, secret management, and safe file handling (if uploads exist).
2. **P1 / operational hardening:** rate limits, idempotency, queue-based notifications, audit logs, security headers, and alerting.
3. **P2 / maintainability and scale:** OpenAPI contracts, pagination conventions, performance budgets, caching policy, dependency and migration governance.

## Important interpretation

None of F-02 through F-10 states that Cynbit currently has the weakness. “Severity if control is absent” describes potential impact, not a verified Cynbit state. Upgrade a finding to confirmed only with reproducible, authorized evidence and a recorded request/response or server-side configuration reference.
