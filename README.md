# Calculator API

A small [FastAPI](https://fastapi.tiangolo.com/) service for basic arithmetic, with a v1 and a v2. Part of the [Mintlify demo org](https://github.com/mintlify-demo): `docs/` holds this API's Mintlify docs.

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

## Regenerate the OpenAPI spec

`docs/openapi.json` is committed so Mintlify can build the API reference without running the app. After changing `main.py`:

```bash
python scripts/export_openapi.py    # or: make spec
```

A test fails if the committed spec is out of date.

## Docs

`docs/` is a complete Mintlify project. The central [`docs`](https://github.com/mintlify-demo/docs) repo publishes it at `/calculator-api`. Preview just this folder with `cd docs && mint dev`.

## Hosting

TODO(hosting): the API will be hosted with Mintlify's internal tooling (details TBD). Until then the OpenAPI `servers` list only `http://localhost:8000`. When the hosted URL exists, add it as the first entry of `servers=[...]` in `main.py`, run `make spec`, and rebase the demo stack (see the demo kit README).

The docs split the API reference by version: **v2 (Latest)** is built from `docs/openapi.v2.json` and **v1 (Legacy)** from `docs/openapi.v1.json`. `make spec` writes both, plus the full `docs/openapi.json`. (A real version switcher needs a change in the base `docs` repo too, because a multi-repo source referenced from `pages` must define `navigation.pages`.)

## Ticket → file map

Context for Mintlify's *Update docs from tickets* automation (seed tickets: `linear-tickets.json` in the demo kit).

| Ticket | What | Where |
| --- | --- | --- |
| DEMO-2 | `Sunset` and `Deprecation` headers on every v1 response | `main.py` (the `/v1/*` routes), `docs/v1/overview.mdx`, `docs/guides/v1-vs-v2.mdx` |
