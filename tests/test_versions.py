"""The per-version specs the docs' version switcher uses must match the app."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from export_openapi import version_spec  # noqa: E402
from main import app  # noqa: E402


def test_committed_version_specs_are_up_to_date():
    """If this fails, run `make spec` and commit docs/openapi.v1.json and docs/openapi.v2.json."""
    full = app.openapi()
    for v in ("v1", "v2"):
        committed = json.loads((ROOT / "docs" / f"openapi.{v}.json").read_text())
        assert committed == version_spec(full, v)


def test_each_version_spec_has_only_its_own_paths():
    full = app.openapi()
    for v in ("v1", "v2"):
        paths = version_spec(full, v)["paths"]
        assert paths and all(p.startswith(f"/{v}/") for p in paths)
