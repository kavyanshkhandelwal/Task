# Cynbit — Backend Technical Assessment

**Role:** Backend Developer Intern  
**Target:** https://www.cynbit.in/  
**Prepared:** 6 November 2026

> **Evidence discipline:** This repository documents public-surface observations and proposes backend controls. It does not claim access to Cynbit's source code, private APIs, databases, infrastructure, logs, or authenticated systems. Controls not directly observable are labelled as recommendations or verification items—not confirmed vulnerabilities.

## Deliverables
- [Technical audit](docs/TECHNICAL_AUDIT.md)
- [Security & performance findings](docs/FINDINGS.md)
- [Recommended improvements](docs/RECOMMENDATIONS.md)
- [Passive HTTP metadata checker](scripts/passive_check.py)
- [Pydantic inquiry schema](examples/inquiry_schema.py)
- [FastAPI security middleware](examples/security_middleware.py)
- [Rate-limit design](examples/rate_limit_design.md)

## Run the passive checker
Python 3.10+:
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python scripts/passive_check.py --base-url https://www.cynbit.in/
```

The checker makes conservative GET requests to the homepage and a fixed set of conventional metadata paths. It does not crawl, fuzz, submit forms, test authentication, or access protected resources.

## Key conclusions
1. Public pages can reveal workflows, but cannot establish the complete backend architecture.
2. Public inquiry, careers, and newsletter workflows should validate input server-side, minimize personal data, rate-limit submissions, and prevent duplicate processing.
3. Authentication and authorization cannot be verified without authorized test access. Apply object-level checks and least privilege by design.
4. Measure performance with endpoint traces and production telemetry; do not claim bottlenecks from page appearance alone.
5. Prioritize an API contract, threat model, and observability baseline, then validate controls in staging.

## Ethical testing statement
Only perform additional verification with written authorization and an agreed scope. Do not enumerate hidden routes, exploit suspected issues, submit unsolicited forms, stress-test production, or access other users' data.
