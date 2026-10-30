"""Image processing endpoints: face swap and restoration."""

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.services.image_service import ImageInputError, decode_rgb, encode_jpeg
from app.services.processing_service import restore_faces, swap_faces

router = APIRouter(tags=["Processing"])


def _parse_options(raw: str) -> dict:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Options JSON invalide : {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("Le champ options doit contenir un objet JSON.")
    return value


def _image_response(result) -> Response:
    headers = {
        "X-Visage-Faces-Found": str(result.faces_found),
        "X-Visage-Seconds": f"{result.seconds:.4f}",
        "X-Visage-Message": result.message[:500],
        "X-Visage-Flagged": str(bool(result.flagged)).lower(),
        "X-Visage-Swapped": ",".join(str(i) for i in result.swapped),
    }
    return Response(content=encode_jpeg(result.image), media_type="image/jpeg", headers=headers)


@router.post("/swap")
async def face_swap(
    target: UploadFile = File(...),
    identity_names: list[str] = Form(...),
    options: str = Form("{}"),
):
    try:
        rgb = decode_rgb(await target.read(), target.filename or "target")
        result = swap_faces(rgb, identity_names, _parse_options(options))
        return _image_response(result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ImageInputError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/restore")
async def face_restore(
    target: UploadFile = File(...),
    options: str = Form("{}"),
):
    try:
        rgb = decode_rgb(await target.read(), target.filename or "target")
        result = restore_faces(rgb, _parse_options(options))
        return _image_response(result)
    except (ImageInputError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
