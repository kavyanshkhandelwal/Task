# Backend Technical Audit — Cynbit Technologies

**Assessment:** Backend Developer Intern — Phase 2  
**Target:** https://www.cynbit.in/  
**Review date:** 6 November 2026  
**Method:** Passive public-surface review; no authenticated or intrusive testing.

## 1. Executive summary

Cynbit's public website presents a company and product ecosystem spanning AI automation, custom software, cloud services, careers, and contact channels. The services page publicly advertises technologies across languages, frameworks, AI/data, cloud/ops, and databases, including TypeScript, Python, Go, Rust, Java, C++, React, Next.js, NestJS, FastAPI, Django, PostgreSQL, MongoDB, Redis, Prisma, AWS, Azure, Docker, and Kubernetes. These are advertised capabilities and must not be treated as proof that the public website itself uses this stack.

The careers page lists a **Backend Developer Intern** role under Tech Internships (Remote / Jaipur) and describes it as work on the high-performance core of the company's software architecture. The public site also exposes contact/discovery navigation and newsletter subscription calls to action.

The externally visible pages do not expose a documented API contract, API versioning policy, authentication protocol, database schema, or deployment topology. This is not itself a vulnerability; it is a limitation of black-box visibility. The report therefore focuses on the backend controls that should support visible and likely user journeys: contact/inquiry intake, newsletter subscription, careers/application workflows, and any product-specific authenticated APIs.

**Overall assessment:** No exploitable vulnerability is claimed. The highest-value next step is an authorized review of ordinary browser network traffic for the contact and career journeys, followed by a read-only review of API schemas, middleware, and deployment configuration.

## 2. Scope and limitations

### In scope
- Public website pages and visible navigation/content.
- Publicly described contact, newsletter, careers, and product/service journeys.
- Backend design recommendations for validation, abuse prevention, privacy, reliability, and observability.
- Conservative GET-only metadata checks against explicitly allowlisted public pages, if run.

### Out of scope
- Login, account creation, privileged portals, internal/admin APIs, or any non-public product environment.
- Endpoint enumeration, directory brute forcing, fuzzing, injection payloads, credential testing, bypass attempts, or automated crawling.
- Form submission, newsletter signup, or contact-message submission (these create records and were intentionally not triggered).
- Load testing, stress testing, destructive actions, or access to personal/customer data.

### Evidence labels
- **Observed:** Directly visible in public page content or a public HTTP response.
- **Not publicly verifiable:** Cannot be confirmed from the accessible public surface.
- **Recommendation:** A proposed control or design improvement, not a finding that Cynbit currently lacks it.

## 3. Public surface and likely backend workflows

| Surface | Public evidence | Backend implications | Confidence |
|---|---|---|---|
| Home / services | Site describes AI automation, software development, SaaS products, cloud infrastructure, and a broad technical capability stack. | Pages may be static/CMS-backed; product apps may have separate APIs. | Public content observed; implementation unknown |
| Contact / discovery | Contact navigation and “Start discovery” calls to action are visible. The contact route could not be independently retrieved during this review. | If an inquiry form exists, it needs strict schema validation, spam controls, consent/privacy handling, and durable delivery. | CTA observed; page/API details not verified |
| Careers | Careers page lists a Backend Developer Intern role and other internship/full-time roles; role-detail links are visible. | Role detail and application workflows may use CMS or application APIs; implementation is unknown. | Role listing observed; application flow unknown |
| Newsletter | “Subscribe to our Briefing” / newsletter calls to action are visible on public pages. | Subscription needs double opt-in, unsubscribe, deduplication, and consent records. | CTA observed; processing unknown |
| Privacy / cookies | Footer links to Privacy Policy and Cookies pages. | Data collection, retention, cookie categories, and consent enforcement should match actual tracking and form processing. | Links observed; policy contents not audited |

## 4. Observable architecture assessment

### 4.1 What can be said
1. The public site has multiple content areas and distinct user journeys (company information, services, product suite, careers, contact, newsletter).
2. The careers page lists the Backend Developer Intern role under Tech Internships and describes a high-performance software architecture focus.
3. The services page advertises several languages, backend frameworks, data technologies, and cloud platforms. This is a statement of capabilities, not evidence that the public website itself uses any one of them.
4. No public OpenAPI/Swagger document, API reference, or backend architecture diagram was identified in the reviewed public content.

### 4.2 What cannot responsibly be inferred
- Whether the website is implemented with Next.js, another framework, a headless CMS, or a custom server.
- Whether public forms call a first-party API, a third-party form provider, or server actions.
- Which database, cache, queue, hosting provider, WAF, or authentication provider is in use.
- Whether authorization, rate limiting, CSRF protection, input validation, encryption-at-rest, or audit logging are correctly implemented.
- Whether any API is vulnerable. A lack of public documentation does not prove a lack of API security.

### 4.3 Recommended logical architecture

```text
Browser / public website
        |
        v
CDN + WAF + TLS termination
        |
        v
Backend API gateway / application entrypoint
        |             \
        |              +--> rate limits, request IDs, security headers
        v
Domain services
  |-- Contact / lead intake
  |-- Careers / application intake
  |-- Newsletter subscription
  |-- Product APIs (separate auth boundary)
        |
        +--> Relational DB (transactional records)
        +--> Queue + worker (email, notifications, integrations)
        +--> Object storage (private uploads, if required)
        +--> Audit log / metrics / traces
```

This is a proposed reference architecture, not a diagram of Cynbit's current infrastructure.

## 5. API contract and payload recommendations

For public intake endpoints, define explicit contracts rather than accepting arbitrary dictionaries. Example endpoints (proposed only):

- `POST /api/v1/inquiries` — validate and persist a project inquiry; enqueue notification asynchronously.
- `POST /api/v1/newsletter/subscriptions` — normalize email, record consent and source, send confirmation.
- `POST /api/v1/careers/applications` — validate role identifier and applicant fields; accept uploads only through constrained private storage.
- `GET /api/v1/health/live` and `/ready` — separate process liveness from dependency readiness; do not disclose internals.

For every endpoint document: method, path, auth requirement, request schema, response schema, status codes, idempotency behaviour, rate limit, PII classification, retention, and owner.

### Example inquiry request (illustrative)

```json
{
  "name": "Aarav Sharma",
  "email": "aarav@example.com",
  "company": "Example Labs",
  "project_type": "web_platform",
  "message": "We need a customer portal with role-based access.",
  "consent": true
}
```

The API should reject unknown/oversized fields, normalize email safely, bound string lengths, and never trust client-supplied role, status, owner, or internal routing fields.

## 6. Data handling and privacy

- Collect only fields needed to respond to the inquiry or process an application.
- Record consent purpose, policy version, timestamp, and source for newsletter and marketing opt-ins.
- Keep contact inquiries, job applications, and newsletter subscriptions in separate logical data domains with different retention rules.
- Restrict applicant CV/resume files to private object storage; use short-lived signed download URLs and malware scanning where uploads are supported.
- Encrypt traffic with TLS; use managed encryption at rest and managed secrets for database/API credentials.
- Define deletion and access-request workflows, retention windows, and backup expiry. Avoid logging full messages, CVs, tokens, or raw personal data.

## 7. Reliability and performance

- Perform server-side validation before database writes.
- Use bounded pagination for any list endpoints; set maximum page size and stable sort order.
- Add indexes for fields used in filters and uniqueness constraints (e.g., normalized email for newsletter subscriptions).
- Send email/CRM notifications through a queue with retry/backoff and a dead-letter path; do not make user-facing requests wait on external email providers.
- Use idempotency keys for retryable create operations to prevent duplicate inquiries/applications.
- Cache only public, non-personal content. Do not cache authenticated or user-specific responses in shared CDN caches.
- Set connection pool limits, request timeouts, and upstream timeouts. Instrument p50/p95/p99 latency, error rates, queue lag, and database pool saturation.

## 8. Security controls to verify with authorization

The following are verification targets, not confirmed vulnerabilities:

1. **Authentication:** secure session/token lifecycle, expiry, refresh rotation, logout invalidation, and MFA for privileged users.
2. **Authorization:** server-side role/resource checks on every protected operation; deny by default; test tenant/object ownership with test accounts.
3. **Input handling:** allowlist validation, parameterized queries/ORM, output encoding, safe file handling, and bounded payload sizes.
4. **Browser protections:** restrictive CORS allowlist, CSRF protection where cookie authentication is used, CSP, HSTS, frame protections, and secure cookie flags.
5. **Abuse prevention:** endpoint-specific rate limits, bot/spam controls, request body limits, and email verification for newsletter signup.
6. **Secrets:** no credentials in frontend bundles or source maps; rotate exposed secrets; use a managed secret store.
7. **Observability:** structured redacted logs, correlation IDs, immutable audit events for privileged actions, and alerting on suspicious patterns.

## 9. Safe next steps for a fuller audit

With written authorization and a designated test environment:
1. Capture ordinary browser Network-panel requests while manually using test contact/career forms with synthetic data.
2. Obtain OpenAPI specs or route/controller inventory from the engineering team.
3. Review authentication and authorization middleware and test with two approved test accounts.
4. Review schemas/migrations, indexes, transaction boundaries, and data-retention jobs.
5. Review CI/CD, dependency scanning, secrets management, and production observability.
6. Run approved automated security checks only against the agreed staging host and scope.

## 10. Public references

- Cynbit Technologies homepage: https://www.cynbit.in/
- Services and advertised technology capabilities: https://www.cynbit.in/services
- Contact navigation / discovery CTA: https://www.cynbit.in/ (contact route was not independently retrievable during this review)
- Careers and role listings: https://www.cynbit.in/careers

## Final assessment

The public website provides clear user-facing journeys but insufficient evidence to make claims about internal backend quality. The strongest backend contribution is to establish explicit contracts and controls around public intake workflows, isolate product authentication boundaries, move integrations to asynchronous workers, and make privacy/security controls observable through tests and telemetry. The highest-priority engineering action is an authorized review of actual form/API traffic and backend implementation, not speculative endpoint probing.
