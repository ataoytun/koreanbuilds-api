# Authentication

> **Unofficial.** This documentation is community-maintained and is not endorsed by koreanbuilds.net or
> its maintainer. Anyone using these endpoints is expected to rate-limit responsibly and avoid behaviour
> that would burden the site (no parallel scraping, no aggressive polling). The site owner may request
> removal of any document in this repository by opening a GitHub issue.

The koreanbuilds.net API uses one static `Authorization` header. There is no OAuth flow, no login
endpoint, no refresh token. The header value is hardcoded in the site's bundled JavaScript (`bundle.js`)
and served identically to every visitor of `https://en.koreanbuilds.net`.

This document covers the auth scheme; for endpoint behaviour see [`endpoints.md`](endpoints.md).

## The header

```
Authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC
```

> **Note:** This token may rotate. If requests start returning `401` or `403`, see
> [When the token rotates](#when-the-token-rotates).

Base64-decoded the value reads `Basic kb-frontend <pw>` — space-separated, where RFC 7617 prescribes a
colon. Re-encoding it with a colon changes the literal; the server expects the value as shown above.

## Required and recommended headers

| Header | Required | Why |
| --- | --- | --- |
| `Authorization` | yes | The server rejects requests without it. |
| `Origin` | effectively | Browsers send `https://en.koreanbuilds.net` automatically. Included in the seed request that's known to work; behaviour without it is not verified. |
| `Referer` | effectively | Same. The seed sends `https://en.koreanbuilds.net/`. |
| `Accept` | recommended | The frontend sends `application/json`. |
| `User-Agent` | recommended | The frontend's UA is a normal Chrome string. Hosts sometimes drop non-browser UAs; not verified for this API. |

Working request, mirroring the official frontend:

```bash
curl 'https://api.koreanbuilds.net/realtime' \
  -H 'accept: application/json' \
  -H 'authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC' \
  -H 'origin: https://en.koreanbuilds.net' \
  -H 'referer: https://en.koreanbuilds.net/' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
```

## The CORS preflight gotcha

Cross-origin requests trigger an `OPTIONS` preflight before the real `GET`. The preflight returns `200`
regardless of whether the real request would succeed.

When debugging auth, inspect the `GET` response, not the `OPTIONS`. In browser dev tools the preflight is
a separate row above the real call, and reading only the preflight makes a failing request look fine.
Pasting the URL into the address bar also fails: the browser sends no `Authorization` header on a
navigation request.

## Why the token is static

The token lives in `bundle.js` and ships to every visitor identically. There is no per-user provisioning,
no client registration, no rotation tied to user state. Treat it as a frontend identifier; every browser
that loads the site already has the value.

## When the token rotates

Symptom: requests that previously worked start returning `401` or `403`.

Fetch the current `bundle.js` from `https://en.koreanbuilds.net/bundle.js` and compare the
`Authorization` literal to the value in your code. If they differ, the token rotated; update it. The
token carries no expiry indicator, so a hard failure is the only signal of rotation.

## Re-extracting the token

```python
import re, requests
b = requests.get("https://en.koreanbuilds.net/bundle.js").text
print(re.search(r'Authorization:"([^"]+)"', b).group(1))
```

A fuller helper may land in `examples/` later.

## What this file does not cover

Endpoint paths, parameters, and response shapes are documented in [`endpoints.md`](endpoints.md).