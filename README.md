# Cynbit Technologies — Backend Technical Audit

A passive, public-surface backend review of [Cynbit Technologies](https://www.cynbit.in/) prepared for the Backend Developer Intern assessment.

## Deliverables

- `docs/TECHNICAL_AUDIT.md` — backend architecture assessment, public-surface evidence, API/data-handling review.
- `docs/FINDINGS.md` — prioritized security, performance, validation, and observability findings.
- `docs/RECOMMENDATIONS.md` — target architecture, rollout plan, and implementation guidance.
- `examples/` — illustrative FastAPI/Pydantic patterns for request validation, safe errors, rate limiting, and security headers. These are reference patterns, not Cynbit production code.
- `scripts/passive_check.py` — low-rate, allowlisted, GET-only public-page metadata checker.

## Key conclusion

Cynbit's public website describes AI automation, software services, products, careers, and contact channels. The public content reviewed does not provide an API specification, backend architecture diagram, authentication flow, or data contract. A defensible audit can identify backend controls that should support public inquiry, newsletter, career, and product workflows, but cannot assert that controls are absent without authorized access to implementation or telemetry.

## Run the passive checker

Python 3.10+; install dependencies:

```bash
python -m pip install -r requirements.txt
python scripts/passive_check.py
```

The checker requests only the fixed public pages in its allowlist, with a delay between requests. Redirects are validated before following them. It does not crawl, enumerate endpoints, submit forms, test authentication, fuzz inputs, or run load tests. Review the allowlist before execution.
