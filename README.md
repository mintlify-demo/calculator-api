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
