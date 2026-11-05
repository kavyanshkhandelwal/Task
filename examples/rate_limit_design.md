# Rate-limit design notes

## Goals
Protect anonymous public submissions without blocking legitimate traffic or relying on a single signal.

## Suggested layered policy (illustrative only)
| Route class | Starting policy | Additional controls |
|---|---:|---|
| Contact inquiry | 5 submissions / 10 min / IP | CAPTCHA/risk challenge after threshold; idempotency |
| Newsletter subscribe | 3 attempts / 10 min / IP + normalized email | Double opt-in; generic response to avoid enumeration |
| Login | 5 failures / 15 min / account + IP | Progressive delay; MFA; alerting |
| Password recovery | 3 requests / hour / account + IP | Generic success response; token expiry |

These are tuning starting points, not universal safe defaults. Tune using real traffic and abuse telemetry; account for NAT/shared networks and accessibility.

## Implementation requirements
- Use a shared atomic counter store (e.g. Redis) across all API replicas.
- Use a sliding-window or token-bucket algorithm with atomic increments.
- Return 429 and a truthful Retry-After value.
- Normalize account/email keys carefully; do not store raw identifiers in metrics.
- Keep allowlists narrow and audited; never rely exclusively on client-supplied headers such as X-Forwarded-For.
- Record rate-limit decisions as structured events while avoiding payload/PII logging.
