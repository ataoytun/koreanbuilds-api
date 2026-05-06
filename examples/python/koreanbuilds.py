"""Python client for the koreanbuilds.net public API.

Unofficial; see docs/endpoints.md and docs/authentication.md for the
canonical reference. Override the auth token via the KB_AUTH_TOKEN
environment variable, or run extract_token.py to pull the current
literal from the live bundle.
"""
from __future__ import annotations
import os
from typing import Any
import requests

API_HOST = "https://api.koreanbuilds.net"
SITE_ORIGIN = "https://en.koreanbuilds.net"
DEFAULT_TOKEN = "QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC"  # may rotate; see extract_token.py
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)

class KoreanBuildsError(Exception):
    def __init__(self, status: int, url: str, body: str) -> None:
        self.status = status
        self.url = url
        self.body = body
        excerpt = body[:200] + ("..." if len(body) > 200 else "")
        super().__init__(f"{status} {url}: {excerpt}")

class KoreanBuilds:
    def __init__(
        self,
        token: str | None = None,
        host: str = API_HOST,
        session: requests.Session | None = None,
    ) -> None:
        token = token or os.environ.get("KB_AUTH_TOKEN") or DEFAULT_TOKEN
        self.host = host
        self.session = session or requests.Session()
        self.session.headers.update({
            "Authorization": token,
            "Accept": "application/json",
            "Origin": SITE_ORIGIN,
            "Referer": SITE_ORIGIN + "/",
            "User-Agent": DEFAULT_USER_AGENT,
        })

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = self.host + path
        r = self.session.get(url, params=params, timeout=20)
        if not r.ok:
            raise KoreanBuildsError(r.status_code, r.url, r.text)
        return r.json()

    def builds(self, champion: str, patchid: int = -2) -> Any:
        """Build statistics for `champion`. `patchid=-2` means the last two patches combined.
        Position is fixed to COMPOSITE; see docs/endpoints.md for the full position notes."""
        params = {"chmpname": champion, "patchid": patchid, "position": "COMPOSITE"}
        return self._get("/builds", params)

    def champions(self, patchid: int = -1) -> Any:
        return self._get("/champions", {"patchid": patchid})

    def tierlists(self, patchid: int) -> Any:
        return self._get("/tierlists", {"patchid": patchid})

    def patches_with_reports(self) -> Any:
        return self._get("/patches/with-reports")

    def patch_report(self, patch_version: str) -> Any:
        return self._get("/patch-report", {"patchVersion": patch_version})

    def realtime(self) -> Any:
        return self._get("/realtime")

# /log is the telemetry write endpoint; intentionally not exposed.

if __name__ == "__main__":
    client = KoreanBuilds()
    rows = client.realtime()
    print(f"realtime() returned {len(rows)} entries; top: {rows[0]['championName']}")