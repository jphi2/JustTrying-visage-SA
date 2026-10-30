"""Face swap and restoration services backed by Visage's existing pipeline."""

from __future__ import annotations

from dataclasses import fields

from app.services.engine_service import get_engine
from app.services.identity_service import load_identity


def build_options(options: dict | None = None):
    engine = get_engine()
    options = options or {}
    allowed = {item.name for item in fields(engine["pipeline"].Options)}
    unknown = sorted(set(options) - allowed)
    if unknown:
        raise ValueError(f"Options Visage inconnues : {', '.join(unknown)}")
    return engine["pipeline"].Options.from_dict(options)


def swap_faces(target_image, identity_names: list[str], options: dict | None = None):
    if not identity_names:
        raise ValueError("Sélectionne au moins une identité source.")
    engine = get_engine()
    identities = [load_identity(name) for name in identity_names]
    opts = build_options(options)
    result = engine["pipeline"].process(target_image, identities, opts)
    return result


def restore_faces(target_image, options: dict | None = None):
    engine = get_engine()
    opts = build_options(options)
    result = engine["pipeline"].restore_only(target_image, opts)
    return result
