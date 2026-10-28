"""Regenerate the committed OpenAPI specs from the FastAPI app.

Run from the repo root:  python scripts/export_openapi.py   (or: make spec)

Writes:
  docs/openapi.json      the full spec (v1 and v2)
  docs/openapi.v2.json   v2 only: the "v2 (Latest)" version in the docs
  docs/openapi.v1.json   v1 only: the "v1 (Legacy)" version in the docs

The files are committed so Mintlify can build the API reference without
running the app.
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from main import app  # noqa: E402

VERSION_INFO = {
    "v1": {"title": "Calculator API v1 (Legacy)", "version": "1.0.0"},
    "v2": {"title": "Calculator API v2", "version": None},  # None: keep the app's version
}


def _refs(node) -> set[str]:
    """Names of every `#/components/schemas/<name>` referenced inside `node`."""
    if isinstance(node, dict):
        found = {node["$ref"].rsplit("/", 1)[-1]} if isinstance(node.get("$ref"), str) else set()
        return found.union(*(_refs(v) for v in node.values()))
    if isinstance(node, list):
        return set().union(*(_refs(v) for v in node))
    return set()


def version_spec(full: dict, version: str) -> dict:
    """The full spec, filtered to the paths, tags and schemas of one API version."""
    spec = copy.deepcopy(full)
    spec["paths"] = {p: ops for p, ops in full["paths"].items() if p.startswith(f"/{version}/")}
    spec["tags"] = [t for t in full.get("tags", []) if t["name"] == version]
    schemas = full.get("components", {}).get("schemas", {})
    keep, todo = set(), _refs(spec["paths"])
    while todo:  # follow refs between schemas
        name = todo.pop()
        if name in schemas and name not in keep:
            keep.add(name)
            todo |= _refs(schemas[name])
    if schemas:
        spec["components"]["schemas"] = {k: v for k, v in schemas.items() if k in keep}
    info = VERSION_INFO[version]
    spec["info"]["title"] = info["title"]
    if info["version"]:
        spec["info"]["version"] = info["version"]
    return spec


def write(name: str, spec: dict) -> None:
    out = ROOT / "docs" / name
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    full = app.openapi()
    write("openapi.json", full)
    for v in ("v2", "v1"):
        write(f"openapi.{v}.json", version_spec(full, v))
