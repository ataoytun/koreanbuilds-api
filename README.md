# koreanbuilds-api

> **Unofficial.** This repository is community-maintained and is not endorsed by koreanbuilds.net or its
> maintainer. Anyone using the documented endpoints is expected to rate-limit responsibly and avoid
> behaviour that would burden the site (no parallel scraping, no aggressive polling). The site owner
> may request removal of any document in this repository by opening a GitHub issue.

This repository documents the unofficial public API behind [koreanbuilds.net](https://en.koreanbuilds.net),
a League of Legends build aggregator. The reference covers seven endpoints with parameters, response
shapes, and quirks observed against the live server. Every documented field traces to a real captured
response or to the site's `bundle.js`, never a guess. A reverse-engineering write-up is included as a
case study, alongside anonymized sample responses and a small Python client.

## Quick start

```
cd examples/python
pip install -r requirements.txt
```

Then:

```python
from koreanbuilds import KoreanBuilds

client = KoreanBuilds()
data = client.builds("seraphine")
for entry in data["builds3"][:3]:
    print(entry["champion"]["name"], entry["games"], "games")
```

## What's in this repo

```
docs/
├── endpoints.md            Reference for the 7 endpoints: paths, parameters,
│                           response shapes, per-endpoint quirks.
├── authentication.md       The auth header, why it is static, how to
│                           re-extract it if the maintainer rotates it.
└── reverse-engineering.md  Case study of figuring out the API from the
                            frontend bundle.
schemas/                    Anonymized sample responses, one per GET endpoint.
examples/python/            Small reference client (~85 lines) plus an
                            extract_token.py helper script.
```

## When the API breaks

**The token rotated.** Symptom: requests start returning `401` or `403`. The token has no expiry
signal; a hard failure is the only indicator of rotation. Run `python examples/python/extract_token.py`,
compare its output against `DEFAULT_TOKEN` in `examples/python/koreanbuilds.py`, and update the
constant if they differ. Full notes in [`docs/authentication.md`](docs/authentication.md).

**A new endpoint appeared.** Confirm it actually exists by grepping the live `bundle.js` for the URL
pattern — do not probe blindly. Once confirmed, document it in [`docs/endpoints.md`](docs/endpoints.md)
following the existing per-endpoint format, add an anonymized sample to `schemas/`, and open a PR.

**You are the site owner and want this repository taken down.** Open a GitHub issue requesting removal.

## Contributing

Verified data is preferred over guessed fields. New endpoint entries should follow the existing format in
[`docs/endpoints.md`](docs/endpoints.md) and include an anonymized sample under `schemas/`. PRs that add
scraping helpers, retry logic, parallel-request orchestration, or other features that would burden the
site will be declined.

## License

[MIT](LICENSE).

The site at [en.koreanbuilds.net](https://en.koreanbuilds.net) is built and maintained by Jakob Abfalter.