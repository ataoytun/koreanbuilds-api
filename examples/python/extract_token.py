#!/usr/bin/env python3
"""Print the current Authorization token from en.koreanbuilds.net's live bundle.js.

Idiom:
    export KB_AUTH_TOKEN=$(python extract_token.py)
"""
from __future__ import annotations
import re
import sys
import requests

BUNDLE_URL = "https://en.koreanbuilds.net/bundle.js"
TOKEN_RE = re.compile(r'Authorization:"([^"]+)"')

def main() -> int:
    body = requests.get(BUNDLE_URL, timeout=20).text
    m = TOKEN_RE.search(body)
    if not m:
        print("could not find Authorization literal in bundle.js", file=sys.stderr)
        return 1
    print(m.group(1))
    return 0

if __name__ == "__main__":
    sys.exit(main())