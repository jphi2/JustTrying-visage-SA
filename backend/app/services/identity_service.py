"""Identity extraction and persistence using Visage safetensors face models."""

from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.services.engine_service import get_engine


def _identity_folders() -> list[tuple[str, Path]]:
    # Priority is explicit and stable: app-created identities, then the two
    # existing shared face-model locations. No files are copied or relocated.
    return [
        ("AI_Visage", Path(settings.face_models_output_dir)),
        ("Native", Path(settings.native_face_models_dir)),
        ("ReActor", Path(settings.reactor_face_models_dir)),
    ]


def list_identities() -> list[dict]:
    engine = get_engine()
    facemodel = engine["facemodel"]
    result: list[dict] = []
    seen: set[str] = set()
    for source, folder in _identity_folders():
        for name, path in facemodel.list_models([str(folder)]).items():
            # Keep the first occurrence when names collide, matching Visage's
            # existing list_models precedence.
            if name in seen:
                continue
            seen.add(name)
            result.append({"name": name, "source": source, "path": path})
    return result


def _identity_path(name: str) -> Path:
    if not name or name in {".", ".."} or "/" in name or "\\" in name:
        raise ValueError("Nom d'identité invalide.")
    for item in list_identities():
        if item["name"] == name:
            return Path(item["path"])
    raise FileNotFoundError(f"Identité introuvable : {name}")


def load_identity(name: str):
    engine = get_engine()
    path = _identity_path(name)
    return engine["facemodel"].load(str(path))


def create_identity(images: list, *, name: str, face_index: int = 0, options: dict | None = None) -> dict:
    if not name or not name.strip():
        raise ValueError("Un nom d'identité est requis.")
    if len(images) < 1:
        raise ValueError("Au moins une image source est requise.")
    if not 0 <= face_index <= 100:
        raise ValueError("face_index doit être compris entre 0 et 100.")

    engine = get_engine()
    pipeline = engine["pipeline"]
    facemodel = engine["facemodel"]
    opts = pipeline.Options.from_dict(options or {})
    identity, warnings = pipeline.identity_from_images(
        images,
        opts,
        face_index=face_index,
        name=name.strip(),
    )
    if identity is None:
        return {"created": False, "name": name.strip(), "warnings": warnings}

    output_dir = Path(settings.face_models_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = facemodel.save(identity, str(output_dir), name=name.strip(), overwrite=False)
    return {
        "created": True,
        "name": Path(path).stem,
        "sources": identity.sources,
        "warnings": warnings,
    }


def delete_identity(name: str) -> None:
    path = _identity_path(name)
    output_dir = Path(settings.face_models_output_dir).resolve()
    # The API may delete only identities created in its own output directory;
    # shared Forge/ReActor face models are read-only from this application.
    if path.resolve().parent != output_dir:
        raise PermissionError("Cette identité appartient à un répertoire partagé et ne peut pas être supprimée ici.")
    path.unlink(missing_ok=True)
