"""Face identity library endpoints."""

import json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.identity_service import create_identity, delete_identity, list_identities
from app.services.image_service import ImageInputError, decode_rgb

router = APIRouter(prefix="/identities", tags=["Identities"])


@router.get("")
def get_identities():
    items = list_identities()
    public_items = [{"name": item["name"], "source": item["source"]} for item in items]
    return {"count": len(public_items), "identities": public_items}


@router.post("")
async def post_identity(
    images: list[UploadFile] = File(...),
    name: str = Form(...),
    face_index: int = Form(0),
    options: str = Form("{}"),
):
    if len(images) > 20:
        raise HTTPException(status_code=422, detail="20 images source maximum.")
    try:
        parsed_options = json.loads(options)
        if not isinstance(parsed_options, dict):
            raise ValueError("Le champ options doit contenir un objet JSON.")
        decoded = [decode_rgb(await item.read(), item.filename or "image") for item in images]
        result = create_identity(decoded, name=name, face_index=face_index, options=parsed_options)
        if not result["created"]:
            raise HTTPException(status_code=422, detail={"message": "Aucune identité extraite.", "warnings": result["warnings"]})
        return result
    except (json.JSONDecodeError, ImageInputError, ValueError, FileExistsError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{name}")
def remove_identity(name: str):
    try:
        delete_identity(name)
        return {"deleted": True, "name": name}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
