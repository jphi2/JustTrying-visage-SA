"""Backend API contract smoke test; does not initialize CUDA or load models."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "visage"))

from app.main import app  # noqa: E402


def test_expected_routes_are_registered():
    paths = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/api/faces/detect" in paths
    assert "/api/identities" in paths
    assert "/api/identities/{name}" in paths
    assert "/api/swap" in paths
    assert "/api/restore" in paths


def test_openapi_is_generated():
    schema = app.openapi()
    assert "/api/faces/detect" in schema["paths"]
    assert "/api/swap" in schema["paths"]
    assert "/api/restore" in schema["paths"]
