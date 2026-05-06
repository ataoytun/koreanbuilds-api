# Endpoints

> **Unofficial.** This documentation is community-maintained and is not endorsed by koreanbuilds.net or
> its maintainer. Anyone using these endpoints is expected to rate-limit responsibly and avoid behaviour
> that would burden the site (no parallel scraping, no aggressive polling). The site owner may request
> removal of any document in this repository by opening a GitHub issue.

The koreanbuilds.net frontend exposes a small JSON API at `https://api.koreanbuilds.net`. Seven endpoints
are reachable from the bundled JavaScript — six read endpoints plus one write-only telemetry endpoint.

## Base URL

```
https://api.koreanbuilds.net
```

The frontend is served from `https://en.koreanbuilds.net`. The API host is a separate origin.

## Authentication

Every request requires a single static `Authorization` header. The value is an opaque token that the
official frontend hardcodes in its bundled JavaScript:

```
authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC
```

Clients should also send `Origin: https://en.koreanbuilds.net` and `Referer: https://en.koreanbuilds.net/`
to match the conditions under which the token is issued.

The token is non-standard. Base64-decoded it reads `Basic kb-frontend <pw>` — space-separated rather
than the colon-separated `<user>:<pw>` form prescribed by RFC 7617. The server expects the literal value
above; do not normalise the format.

The token may rotate. When `401` or `403` responses appear, re-extract from the current bundle.

## Common parameters

### `patchid`

Accepts negative integers as relative selectors and positive integers as absolute patch row IDs.

| value | meaning |
| --- | --- |
| `-1` | latest patch only |
| `-2` | last two patches combined |
| positive integer (e.g. `247`, `248`) | a specific patch row id, available in the `patches` array of any response that returns one |

### `position` (`/builds` only)

Confirmed via `bundle.js`:

- `COMPOSITE` — all positions combined. The official frontend always sends this value.

The labels `TOP`, `JUNGLE`, `MID`, `SUPPORT`, `BOT` appear in `bundle.js` as client-side strings (not as
URL builder values for `/builds`). Their server-side acceptance for the `position` parameter has not been
verified in this session.

### Position label casing

Position names appear in three casings depending on context:

| casing | where | examples |
| --- | --- | --- |
| `ALL CAPS` | URL parameters; the `positions` array on `/builds` | `SUPPORT`, `BOT` |
| `Title Case` | nested `position.positionName` fields; `/builds` `percentiles` keys | `Support`, `Bot`, `Top`, `Mid`, `Jungle` |
| `lowercase` | by-position keys on `/tierlists.tierlists` and `/champions[*].builds`/`usage` | `support`, `bot`, `top`, `mid`, `jungle`, plus `all` on tierlists |

`/tierlists` entries also use `position.positionName: "None"` for entries that don't bind to a single
canonical position.

## Caching

Every read endpoint emits a weak `ETag` (`W/"..."`) on `200` responses. No `Cache-Control` header is
returned. `If-None-Match` with a previously seen ETag is honoured: a follow-up request to
`/patches/with-reports` carrying the prior `ETag` returned `304 Not Modified` with an empty body.

`Content-Type` is `application/json; charset=utf-8` on `2xx` JSON responses.

Recommended client behaviour: store the response body alongside its `ETag`, send `If-None-Match` on
subsequent requests to the same URL.

## Endpoints overview

| Path | Method | Purpose |
| --- | --- | --- |
| [`/builds`](#get-builds) | `GET` | Build details (items, runes, skill order) for a single champion |
| [`/champions`](#get-champions) | `GET` | Champion list with per-position counts, plus the patch list and a tierlist summary |
| [`/tierlists`](#get-tierlists) | `GET` | Per-position tierlists (winrate, pickrate, banrate) for a patch |
| [`/patches/with-reports`](#get-patcheswith-reports) | `GET` | Patches that have an associated patch report |
| [`/patch-report`](#get-patch-report) | `GET` | The patch report HTML for a specific patch version |
| [`/realtime`](#get-realtime) | `GET` | Currently popular / trending champions |
| [`/log`](#post-log) | `POST` | Client error telemetry (write-only) |

---

## GET /builds

Build statistics, item sets, skill orders, perk pages, summoner spells, and matched summoner samples
for one champion across one or more patches.

```
GET /builds
```

### Parameters

| name | type | required | default | description |
| --- | --- | --- | --- | --- |
| `chmpname` | string | yes | — | Lowercase English champion name (e.g. `seraphine`, `leesin`). |
| `patchid` | int | no | `-2` | Patch id (relative or absolute). The frontend's `builds(name, patchid=-2)` defaults to `-2`. |
| `position` | string | yes | — | The frontend always sends `COMPOSITE`. See [Common parameters → `position`](#position-builds-only). |

### Sample request

```bash
curl 'https://api.koreanbuilds.net/builds?chmpname=seraphine&patchid=-2&position=COMPOSITE' \
  -H 'accept: application/json' \
  -H 'authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC' \
  -H 'origin: https://en.koreanbuilds.net' \
  -H 'referer: https://en.koreanbuilds.net/'
```

### Sample response (truncated, anonymized)

```json
{
  "builds2": [],
  "builds3": [
    {
      "buildId": 6932929,
      "puuid": "<puuid>",
      "games": 33,
      "wins": 17,
      "kills": 55,
      "deaths": 199,
      "assists": 354,
      "kda": 2.06,
      "confidenceScore": 66.3,
      "champion": { "chmpid": 147, "name": "Seraphine", "image": "Seraphine.png", "isSupp": true },
      "patch":    { "patchid": 248, "patchVersion": "26.09", "matchCount": 411961 },
      "position": { "idposition": 1, "positionName": "Support" },
      "summoner": {
        "puuid": "<puuid>",
        "summonerid": "<summonerid>",
        "name": "<gameName>",
        "gameName": "<gameName>",
        "tagLine": "KR1",
        "rank": "Dropped from Master",
        "wins": 449,
        "losses": 451,
        "accountId": null
      },
      "itemSets":       [{ "order": 0, "item0": 1011, "item1": 3001, "...": "..." }],
      "skillSets":      [{ "skillOrder": "Q,W,E,Q,...", "order": 0 }],
      "perkPage":       [{ "order": 0, "perks": [...] }],
      "summonerSpells": [{ "order": 0, "summonerSpell0": 4, "summonerSpell1": 14 }]
    }
  ],
  "positions": ["SUPPORT", "MID", "TOP"],
  "patches":   [{ "patchid": 248, "patchVersion": "26.09", "matchCount": 411961 }],
  "skills":    [{ "identifier": "SeraphineQ", "name": "High Note", "slot": 1 }],
  "tierlists": [{ "idTierList": 6669722, "winrate": "52.90", "pickrate": "8.68" }],
  "percentiles": {
    "Support": { "totalDamageDealtToChampionsPerMin_10": 0, "totalDamageDealtToChampionsPerMin_90": 0 },
    "Bot": { "...": "..." },
    "Top": { "...": "..." },
    "Mid": { "...": "..." },
    "Jungle": { "...": "..." }
  }
}
```

Full anonymized sample: [`schemas/builds-sample.json`](../schemas/builds-sample.json).

### Response notes

- `200` on success. The official client throws on any non-`200` response.
- `ETag` returned (weak). Cacheable.
- Payload can be very large — ~900 KB observed for `seraphine` on `patchid=-2`.

### Quirks

- Each entry of `builds3` has both a top-level `puuid` and a nested `summoner.puuid`; they refer to the
  same summoner.
- `builds2` is an empty array on observed responses; `builds3` carries the current data. Likely
  schema-versioned (the API client also exposes static `BUILD_V2`/`BUILD_V3` constants).
- The `position` query parameter is required by the frontend's URL builder; behaviour without it is
  unverified.

---

## GET /champions

Champion roster with per-position build counts and usage breakdowns, plus the patch list and a champion
tierlist summary for a given patch.

```
GET /champions
```

### Parameters

| name | type | required | default | description |
| --- | --- | --- | --- | --- |
| `patchid` | int | no | `-1` | Patch id (relative or absolute). The frontend's `champions(patchid=-1)` defaults to `-1`. |

### Sample request

```bash
curl 'https://api.koreanbuilds.net/champions?patchid=-1' \
  -H 'accept: application/json' \
  -H 'authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC' \
  -H 'origin: https://en.koreanbuilds.net' \
  -H 'referer: https://en.koreanbuilds.net/'
```

### Sample response (truncated)

```json
{
  "champions": [
    {
      "id": 266,
      "name": "Aatrox",
      "localName": "Aatrox",
      "image": "Aatrox.png",
      "className": "Aatrox",
      "builds": { "mid": 4, "support": 0, "top": 47, "jungle": 7, "bot": 0 },
      "usage": {
        "total":   { "rawGames": 624, "percentage": "0.40" },
        "top":     { "rawGames": 515, "percentage": "1.51" },
        "mid":     { "rawGames": 42,  "percentage": "0.13" },
        "bot":     { "rawGames": 0,   "percentage": 0 },
        "support": { "rawGames": 0,   "percentage": 0 },
        "jungle":  { "rawGames": 67,  "percentage": "0.19" }
      }
    }
  ],
  "patches": [
    { "patchid": 248, "patchVersion": "26.09", "matchCount": 411961, "hasReport": false }
  ],
  "tierlists": [{ "idTierList": 6669283, "winrate": "50.80", "pickrate": "27.77" }],
  "messages": [],
  "features": []
}
```

Full anonymized sample: [`schemas/champions-sample.json`](../schemas/champions-sample.json).

### Response notes

- `200` on success.
- `ETag` returned.
- 172 champions on observed responses; ~115 KB.

### Quirks

- `usage.<position>.percentage` is a string (`"0.40"`) when non-zero and a number (`0`) when zero.
  Clients should accept either.
- The `patches` array here carries a `hasReport: bool` per patch — that field is **absent** on items
  returned by [`/patches/with-reports`](#get-patcheswith-reports), where presence in the list itself
  implies a report exists.
- `messages` and `features` are empty arrays on observed responses; their schemas are not documented
  here.

---

## GET /tierlists

Per-position tierlists for a patch: winrate, pickrate, banrate, popularity, and a sample-size-aware
"skill gap" deviation.

```
GET /tierlists
```

### Parameters

| name | type | required | default | description |
| --- | --- | --- | --- | --- |
| `patchid` | int | yes | — | Patch id (relative or absolute). The frontend's `tierlists(patchid)` has no default — callers always pass one. |

### Sample request

```bash
curl 'https://api.koreanbuilds.net/tierlists?patchid=-1' \
  -H 'accept: application/json' \
  -H 'authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC' \
  -H 'origin: https://en.koreanbuilds.net' \
  -H 'referer: https://en.koreanbuilds.net/'
```

### Sample response (truncated)

```json
{
  "tierlists": {
    "all":     [/* 148 entries */],
    "top":     [/* 67 entries  */],
    "jungle":  [/* 53 entries  */],
    "mid":     [/* 54 entries  */],
    "bot":     [/* 33 entries  */],
    "support": [/* 48 entries  */]
  },
  "patches":       [{ "patchid": 248, "patchVersion": "26.09" }],
  "selectedPatch": { "patchid": 248, "patchVersion": "26.09" },
  "sampleSize":    411072
}
```

Each tierlist entry:

```json
{
  "idTierList": 6669283,
  "winrate":      "50.80",
  "winratePlus":  "51.20",
  "skillGap":     "0.40",
  "pickrate":     "27.77",
  "banrate":      "6.42",
  "games":        11436,
  "popularity":   "94.05",
  "position": { "idposition": 6, "positionName": "None" },
  "rank":     { "rankId": 1, "tierlistRankName": "S" },
  "champion": { "chmpid": 64, "name": "Lee Sin", "image": "LeeSin.png", "isSupp": false, "localName": "Lee Sin" },
  "patch":    { "patchid": 248, "patchVersion": "26.09", "matchCount": 411961 }
}
```

Full anonymized sample: [`schemas/tierlists-sample.json`](../schemas/tierlists-sample.json).

### Response notes

- `200` on success.
- `ETag` returned. ~400 KB on a recent patch.

### Quirks

- Numeric statistics (`winrate`, `winratePlus`, `skillGap`, `pickrate`, `banrate`, `popularity`) are
  serialised as **strings**, not numbers. Coerce client-side.
- `position.positionName` for entries in the `all` aggregate may be `"None"` — entries that don't bind
  to a single canonical position. The five per-position lists (`top`, `jungle`, `mid`, `bot`, `support`)
  contain only entries with their respective `positionName`.
- The map keys (`top`, `bot`, ...) are lowercase; `position.positionName` inside each entry is Title Case
  (`Top`, `Bot`, ...). See [Position label casing](#position-label-casing).

---

## GET /patches/with-reports

The list of patches that have an associated patch report. Use this list to drive a UI selector for
[`/patch-report`](#get-patch-report).

```
GET /patches/with-reports
```

### Parameters

None.

### Sample request

```bash
curl 'https://api.koreanbuilds.net/patches/with-reports' \
  -H 'accept: application/json' \
  -H 'authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC' \
  -H 'origin: https://en.koreanbuilds.net' \
  -H 'referer: https://en.koreanbuilds.net/'
```

### Sample response (truncated)

```json
[
  { "patchid": 247, "patchVersion": "26.08", "start": "2026-04-14T19:15:07.000Z", "enabled": true, "v3": true, "matchCount": 780006, "image": "26-8.webp" },
  { "patchid": 246, "patchVersion": "26.07", "start": "2026-03-31T19:15:05.000Z", "enabled": true, "v3": true, "matchCount": 882616, "image": "26-7.webp" },
  { "patchid": 245, "patchVersion": "26.06", "start": "2026-03-17T19:15:03.000Z", "enabled": true, "v3": true, "matchCount": 906814, "image": "26-6.webp" }
]
```

Full anonymized sample: [`schemas/patches-with-reports-sample.json`](../schemas/patches-with-reports-sample.json).

### Response notes

- `200` on success.
- 12 entries observed.
- `ETag` returned. `If-None-Match` with the prior `ETag` returned `304 Not Modified` with an empty body —
  caching confirmed on this endpoint.

### Quirks

- Items do **not** include a `hasReport` field. Presence in this list implies a report exists; compare
  with `/champions` where `patches[*].hasReport` is set per-patch.

---

## GET /patch-report

The patch report (HTML) for a specific patch version.

```
GET /patch-report
```

### Parameters

| name | type | required | default | description |
| --- | --- | --- | --- | --- |
| `patchVersion` | string | yes | — | A patch version string like `26.08`. The frontend wraps it in `encodeURI(...)`. |

### Sample request

```bash
curl 'https://api.koreanbuilds.net/patch-report?patchVersion=26.08' \
  -H 'accept: application/json' \
  -H 'authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC' \
  -H 'origin: https://en.koreanbuilds.net' \
  -H 'referer: https://en.koreanbuilds.net/'
```

### Sample response (truncated)

```json
{
  "patch": {
    "patchid":      247,
    "patchVersion": "26.08",
    "start":        "2026-04-14T19:15:07.000Z",
    "enabled":      true,
    "v3":           true,
    "matchCount":   780006,
    "image":        "26-8.webp"
  },
  "report": {
    "id":         16,
    "patchId":    247,
    "content":    "<p>Welcome to Koreanbuilds.net's comprehensive patch report for 26.08, your de...",
    "languageId": null,
    "language":   null,
    "created_at": "2026-04-25T12:01:40.000Z"
  }
}
```

Full anonymized sample: [`schemas/patch-report-sample.json`](../schemas/patch-report-sample.json).

### Response notes

- `200` on success.
- `ETag` returned.
- `report.content` is HTML. ~22 KB observed.

### Quirks

- The frontend passes `patchVersion` through `encodeURI(...)` rather than `encodeURIComponent(...)`.
  Patch versions seen so far (e.g. `26.08`) contain no characters that differ between the two, but
  follow the frontend's choice for parity.
- `report.languageId` and `report.language` are `null` on observed responses.

---

## GET /realtime

Currently popular / trending champions, ordered by descending viewer count.

```
GET /realtime
```

### Parameters

None.

### Sample request

```bash
curl 'https://api.koreanbuilds.net/realtime' \
  -H 'accept: application/json' \
  -H 'authorization: QmFzaWMga2ItZnJvbnRlbmQgVDNNMWV3dUhqMlF3c1dC' \
  -H 'origin: https://en.koreanbuilds.net' \
  -H 'referer: https://en.koreanbuilds.net/'
```

### Sample response (truncated)

```json
[
  { "championName": "Ezreal",  "encChampionName": "Ezreal",  "viewers": 6, "image": "Ezreal.png",  "localName": "Ezreal"  },
  { "championName": "Diana",   "encChampionName": "Diana",   "viewers": 3, "image": "Diana.png",   "localName": "Diana"   },
  { "championName": "Naafiri", "encChampionName": "Naafiri", "viewers": 3, "image": "Naafiri.png", "localName": "Naafiri" }
]
```

Full anonymized sample: [`schemas/realtime-sample.json`](../schemas/realtime-sample.json).

### Response notes

- `200` on success.
- 47 entries observed; size varies with what's currently popular.
- `ETag` returned.

### Quirks

- `viewers` is a small integer. The exact source (live stream count, recent match count, etc.) is not
  documented in the bundle.

---

## POST /log

Client-side error telemetry. Write-only; the official client does not consume the response body or check
the status code.

```
POST /log
```

### Request body (`application/json`)

| field | type | description |
| --- | --- | --- |
| `msg` | string | error message |
| `code` | any | error code (application-defined) |
| `context` | any | application-specific context |
| `stack` | string | stack trace |

### Source

Confirmed via `bundle.js` — the API client class defines:

```js
async logErrorToBackend(t) {
  const e = { msg: t.message, code: t.code, context: t.context, stack: t.stack };
  const r = `${this.host}/log`;
  const n = Object.assign({}, this.opts);
  n.method = "POST";
  n.body = JSON.stringify(e);
  n.headers["Content-type"] = "application/json";
  await fetch(r, n);
}
```

### Sample request

Intentionally not provided. **This endpoint was not probed in this session** — sending requests writes
to the maintainer's telemetry log.

### Response notes

- The official client does not check the status code (fire-and-forget).

### Quirks

- Sends `Content-type: application/json` (lowercase `t`) to match the literal in the bundle. Standard
  capitalisation (`Content-Type`) is not known to be rejected, but follow the frontend's form for parity.
