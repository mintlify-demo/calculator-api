# Calculator API

A small [FastAPI](https://fastapi.tiangolo.com/) service for basic arithmetic, with a v1 and a v2. Part of the [Mintlify demo org](https://github.com/mintlify-demo). Docs: [https://mintlify-demo.mintlify.site/calculator-api](https://mintlify-demo.mintlify.site/calculator-api).

| Version | Endpoints |
| --- | --- |
| v1 | `POST /v1/add`, `/v1/subtract`, `/v1/multiply`, `/v1/divide` with `{"a": 1, "b": 2}` |
| v2 | `POST /v2/calculate` with `{"operation": "add", "operands": [1, 2, 3]}` |

Dividing by zero returns HTTP `400`.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload        # http://localhost:8000  (Swagger UI at /docs)
```

```bash
curl -X POST localhost:8000/v1/add -H 'Content-Type: application/json' -d '{"a": 12, "b": 4}'
```

## Test it

```bash
python -m pytest -q
```

## Docs

Published at [https://mintlify-demo.mintlify.site/calculator-api](https://mintlify-demo.mintlify.site/calculator-api) (sign-in required). The pages and the API spec live in the [`docs` repo, under `calculator-api/`](https://github.com/mintlify-demo/docs/tree/main/calculator-api), not here. This repo holds only code and tests. When a pull request here changes the API, Mintlify's *Update from code changes* automation opens a pull request in the `docs` repo with the matching docs update.

## Hosting

TODO(hosting): the API will be hosted with Mintlify's internal tooling (details TBD). Until then the OpenAPI `servers` list only `http://localhost:8000`. When the hosted URL exists, add it as the first entry of `servers=[...]` in `main.py`, update the `servers` list in the `docs` repo's spec too, and rebase the demo stack (see the demo kit README).

The docs use Mintlify's version switcher: **v2 (Latest)** is built from `docs` repo `calculator-api/openapi.v2.json` and **v1 (Legacy)** from `calculator-api/openapi.v1.json`.

## Ticket → file map

Context for Mintlify's *Update docs from tickets* automation (seed tickets: `linear-tickets.json` in the demo kit).

| Ticket | What | Where |
| --- | --- | --- |
| DEMO-2 | `Sunset` and `Deprecation` headers on every v1 response | `main.py` (the `/v1/*` routes), `docs` repo `calculator-api/v1/overview.mdx`, `docs` repo `calculator-api/guides/v1-vs-v2.mdx` |
