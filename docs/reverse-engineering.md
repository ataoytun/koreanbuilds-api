# Reverse-engineering notes

> **Unofficial.** This documentation is community-maintained and is not endorsed by koreanbuilds.net or
> its maintainer. Anyone using these endpoints is expected to rate-limit responsibly and avoid behaviour
> that would burden the site (no parallel scraping, no aggressive polling). The site owner may request
> removal of any document in this repository by opening a GitHub issue.

The site at `https://en.koreanbuilds.net` is useful work by someone in the LoL community. The goal here
was to reach its build data from a Python script. In the browser, that call works; the Network panel
shows the XHR returning JSON, status 200. Hit the same URL with curl, no extra headers, and the server
returns 400:

```
curl 'https://api.koreanbuilds.net/builds?chmpname=seraphine&patchid=-2&position=COMPOSITE'
# 400 Bad Request
```

## The OPTIONS preflight trap

The first move was "Copy as cURL" from DevTools. The cURL it produced had `-X OPTIONS` and one tell:

```
access-control-request-headers: authorization
```

That's the CORS preflight, not the real request. Browsers send OPTIONS before a cross-origin GET to ask
which custom headers and methods are allowed; the preflight response doesn't carry application data. The
preflight returns 200 regardless of whether the real GET would succeed.

The trap is that the preflight cURL looks like an ordinary failing request when read on its own. Same
URL, no body in the response, status 200, nothing useful — and in the Network panel the OPTIONS row sits
directly above the real GET, easy to grab the wrong one. Read in isolation it offered nothing. Read
carefully it offered everything: the header `access-control-request-headers: authorization` is the
browser declaring, in advance, that the real GET will carry an `Authorization` header. That was the
missing piece. I'd glanced past it.

## The bundle as ground truth

Rather than chase the live GET through DevTools filtering, the faster path was to read the frontend code
directly. The site is Vanilla JS bundled with Webpack into a single `bundle.js` at
`https://en.koreanbuilds.net/bundle.js`, about 256 KB, minified to one line.

The extraction is mechanical. Fetch the homepage, parse the `<script src>`, download the bundle, grep
it. Patterns worth grepping for in any frontend bundle:

- `api.<sitename>` for backend hostnames
- `Authorization`, `Bearer`, `eyJ` (JWT prefix)
- `/auth`, `/login`, `/token`, `/refresh`
- `axios.defaults`, `fetch(` defaults
- `process.env` for build-time tokens

If any of those hit, the auth picture takes shape fast. A `Bearer` literal points to OAuth or session
tokens. An `eyJ` prefix is a JWT, with a refresh-token flow likely nearby. Calls to `/auth` or `/login`
mean the token gets minted somewhere; if those paths are missing, the token isn't being minted at all,
and whatever's in the bundle is what the server sees. Empty greps mean cookies, a service worker, or no
client-side auth at all. For a site whose API call lives in the same JavaScript that issues it from the
browser, the headers are usually right there.

## What the bundle said

The grep for `Authorization` returned one line:

```javascript
this.opts = { headers: { Accept: "application/json", Authorization: "QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC" } }
```

That literal lived in a small API client class. The class had a constructor taking host and auth, and
one async method per endpoint; each method built a URL on `this.host`, called `fetch(url, this.opts)`,
and threw on a non-200 status. There is no login, no refresh, no per-user token. The literal is the
entire auth story.

Base64-decoded: `Basic kb-frontend <pw>`, space-separated, where RFC 7617 prescribes a colon. That's a
non-standard form. The server expects this exact byte sequence. Re-encoding it with a colon produces a
different string.

The implications fell out of the absences:

- No `/auth`, `/login`, `/token`, or `/refresh` endpoints anywhere in the bundle.
- No `Bearer` literal, no `eyJ`-prefixed JWT, no token-rotation logic.
- The same value is served to every visitor's browser.

The auth boundary on this API is roughly: any client that sends the right opaque token gets in. The
token is not a secret in any meaningful sense; every browser that loads the homepage already has it.
It's a shape the server uses to gate scripted access from random origins.

## Closing the loop

A Python `requests.get` with the two headers from the bundle's `this.opts` — `Authorization` and
`Accept` — plus the `Origin`, `Referer`, and `User-Agent` that any normal Chrome would send, returned
200 with the JSON the browser had been rendering:

```python
import requests
url = "https://api.koreanbuilds.net/builds?chmpname=seraphine&patchid=-2&position=COMPOSITE"
headers = {
    "Authorization": "QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC",
    "Accept": "application/json",
    "Origin": "https://en.koreanbuilds.net",
    "Referer": "https://en.koreanbuilds.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}
print(requests.get(url, headers=headers).status_code)  # 200
```

I went back later to check the live GET cURL from DevTools, this time filtering past the OPTIONS
preflight. Same headers.

The formal reference is in two files. [`endpoints.md`](endpoints.md) covers paths, parameters, response
shapes, and per-endpoint quirks; [`authentication.md`](authentication.md) covers the auth header, the
headers that go alongside it, and how to re-extract the literal if the server rotates it.