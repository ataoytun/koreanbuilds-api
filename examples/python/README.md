# Python client

> **Unofficial.** This client is community-maintained and is not endorsed by koreanbuilds.net or its
> maintainer. Anyone using these endpoints is expected to rate-limit responsibly and avoid behaviour
> that would burden the site (no parallel scraping, no aggressive polling). The site owner may request
> removal of any document in this repository by opening a GitHub issue.

A small `requests`-based wrapper around the koreanbuilds.net public API. No async, no retries, no
caching, by design. See [`docs/endpoints.md`](../../docs/endpoints.md) and
[`docs/authentication.md`](../../docs/authentication.md) for the reference.

## Install

```
pip install -r requirements.txt
```

## Quick example

```python
from koreanbuilds import KoreanBuilds

client = KoreanBuilds()
data = client.builds("seraphine")
for entry in data["builds3"][:3]:
    print(entry["champion"]["name"], entry["games"], "games")
```

## Authentication

Token resolution: explicit `token=` argument first, then the `KB_AUTH_TOKEN` environment variable, then
the `DEFAULT_TOKEN` constant. If requests start returning `401` or `403`, run `python extract_token.py`
to pull the current value from the live bundle. Full notes in
[`docs/authentication.md`](../../docs/authentication.md).

## Available methods

All return `Any` (parsed JSON; shape varies by endpoint):

- `builds(champion, patchid=-2)`: build details for one champion.
- `champions(patchid=-1)`: champion roster with per-position counts.
- `tierlists(patchid)`: by-position tierlists for a patch.
- `patches_with_reports()`: patches that have an associated report.
- `patch_report(patch_version)`: patch report content for a version.
- `realtime()`: currently popular champions.

For paths, parameters, and response shapes, see [`docs/endpoints.md`](../../docs/endpoints.md). For the
auth header and how to re-extract it, see [`docs/authentication.md`](../../docs/authentication.md).