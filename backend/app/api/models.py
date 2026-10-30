"""Model inventory endpoints."""

from fastapi import APIRouter

from app.services.engine_service import get_engine

router = APIRouter(tags=["Models"])


@router.get("/models")
def list_models():

    engine = get_engine()

    registry = engine["models"].REGISTRY
    manager = engine["models"]

    result = []

    for key, spec in registry.items():

        result.append({
            "key": key,
            "kind": spec.kind,
            "title": spec.title,
            "downloaded": manager.is_downloaded(key),
        })

    return {
        "count": len(result),
        "models": result,
    }
