#!/usr/bin/env python3
"""Conservative passive HTTP metadata checker. Does not submit forms or crawl."""
from __future__ import annotations
import argparse
import sys
from urllib.parse import urljoin, urlparse
import requests

PATHS = ("", "robots.txt", "sitemap.xml", "favicon.ico")
HEADERS_TO_REPORT = (
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "cache-control",
    "server",
)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://www.cynbit.in/")
    parser.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args()
    parsed = urlparse(args.base_url)
    if parsed.scheme != "https" or not parsed.netloc:
        parser.error("--base-url must be an absolute HTTPS URL")
    if args.timeout <= 0 or args.timeout > 15:
        parser.error("--timeout must be greater than 0 and at most 15 seconds")

    session = requests.Session()
    session.headers.update({"User-Agent": "Cynbit-Passive-Audit/1.0 (metadata-only)"})
    origin = f"{parsed.scheme}://{parsed.netloc}/"
    for path in PATHS:
        url = urljoin(origin, path)
        try:
            response = session.get(url, timeout=args.timeout, allow_redirects=True, stream=True)
            print(f"\n{url}")
            print(f"  status: {response.status_code}")
            print(f"  final_url: {response.url}")
            print(f"  content_type: {response.headers.get('Content-Type', 'not supplied')}")
            print(f"  content_length: {response.headers.get('Content-Length', 'not supplied')}")
            for key in HEADERS_TO_REPORT:
                value = response.headers.get(key)
                print(f"  {key}: {value if value is not None else 'not supplied'}")
            response.close()
        except requests.RequestException as exc:
            print(f"\n{url}\n  request_error: {type(exc).__name__}: {exc}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
