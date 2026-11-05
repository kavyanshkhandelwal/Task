#!/usr/bin/env python3
"""Low-rate GET-only metadata check for explicitly allowlisted Cynbit pages.

No crawling, endpoint guessing, form submission, authentication, fuzzing, or
load testing. Redirect targets are validated BEFORE following them.
"""
from __future__ import annotations

import time
from urllib.parse import urljoin, urlparse

import requests

APPROVED_HOSTS = {"www.cynbit.in", "cynbit.in"}
BASE = "https://www.cynbit.in"
PAGES = ["/", "/services", "/contact", "/careers"]
DELAY_SECONDS = 1.5
TIMEOUT_SECONDS = 10
MAX_REDIRECTS = 3


def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in APPROVED_HOSTS


def get_allowlisted(session: requests.Session, url: str) -> requests.Response | None:
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        if not validate_url(current):
            print(f"  refusing non-allowlisted URL: {current}")
            return None

        response = session.get(
            current,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
            stream=True,
        )
        if response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get("Location")
            response.close()
            if not location:
                return None
            current = urljoin(current, location)
            continue
        return response

    print("  redirect limit reached")
    return None


def main() -> None:
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Cynbit-Passive-Audit/1.0 (single-request public-page review)"}
    )

    for path in PAGES:
        url = BASE + path
        try:
            response = get_allowlisted(session, url)
            if response is None:
                continue

            print(f"\n{path}")
            print(f"  status: {response.status_code}")
            print(f"  final_url: {response.url}")
            print(f"  content_type: {response.headers.get('Content-Type', 'not present')}")
            print(f"  content_length: {response.headers.get('Content-Length', 'not present')}")
            for header in (
                "Strict-Transport-Security",
                "Content-Security-Policy",
                "X-Content-Type-Options",
                "X-Frame-Options",
                "Referrer-Policy",
                "Permissions-Policy",
                "Cache-Control",
            ):
                print(f"  {header}: {response.headers.get(header, 'not present')}")
            response.close()
        except requests.RequestException as exc:
            print(f"\n{path}: request failed ({type(exc).__name__})")
        finally:
            time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()
