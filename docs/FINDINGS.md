# Security & Performance Findings Register

## Interpretation
This register separates risk areas worth investigating from confirmed vulnerabilities. Since this assessment is limited to passive public-surface review, items marked **Verify** are not claims that Cynbit currently has the weakness.

| ID | Category | Finding / risk hypothesis | Evidence | Severity if control is absent | Validation needed |
|---|---|---|---|---|---|
| F-01 | Input validation | Public inquiry fields may be exposed to malformed, oversized, or unexpected input if server-side schemas are incomplete. | Verify | Medium | Review API schema and staging validation cases |
| F-02 | Abuse prevention | Public write endpoints can be abused for spam or notification flooding without layered rate limits and bot controls. | Inferred | Medium | Review edge and application rate-limit config |
| F-03 | Privacy | Inquiry, candidate, or newsletter data may be retained longer than necessary without explicit lifecycle policy. | Verify | High | Review retention schedule, deletion workflow, processor contracts |
| F-04 | File handling | If resumes/attachments are accepted, publicly accessible storage or unsafe file processing could expose data. | Conditional | High | Review upload pipeline, bucket policy, malware scanning |
| F-05 | Authentication | Any authenticated portal should use secure session/token handling and safe recovery flows. | Verify | High | Authorized account review in staging |
| F-06 | Authorization | Object-level authorization must be enforced server-side to prevent cross-user/tenant access. | Verify | Critical | Owner-approved two-account staging tests |
| F-07 | Browser security | Security headers and cookie attributes should be verified against current public responses. | Verify | Medium | Capture response headers for each relevant host |
| F-08 | Error handling | Verbose errors could disclose internals if exceptions are returned directly. | Verify | Medium | Induce only documented validation errors in staging |
| F-09 | Performance | Unbounded lists, missing indexes, or synchronous third-party calls can cause tail latency. | Inferred | Medium | APM traces, query plans, load profiles in staging |
| F-10 | Reliability | Notification provider outages can lose submissions if delivery is synchronous and no durable queue exists. | Inferred | Medium | Review persistence/queue/retry architecture |

## Prioritization
- **P0 / Critical:** Verify object-level authorization and private file access before handling sensitive multi-user data.
- **P1 / High:** Data minimization/retention and upload isolation where these workflows exist.
- **P2 / Medium:** Server validation, abuse throttling, secure headers, sanitized errors, and queue-backed integrations.
- **P3 / Medium:** Query/index and caching optimization based on measured telemetry.

## Evidence discipline
No issue above is a confirmed exploitable vulnerability. “Severity if control is absent” describes potential impact, not a verified Cynbit state. Upgrade a finding to confirmed only with reproducible, authorized evidence and a recorded request/response or server-side configuration reference.
