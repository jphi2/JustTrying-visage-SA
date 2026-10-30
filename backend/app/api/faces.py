"""Face detection endpoints."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.face_service import detect_faces
from app.services.image_service import ImageInputError, decode_rgb

router = APIRouter(prefix="/faces", tags=["Faces"])


@router.post("/detect")
async def detect(
    image: UploadFile = File(...),
    detector: str = Form("retinaface_10g"),
    det_size: int = Form(640),
    threshold: float = Form(0.5),
    try_rotations: bool = Form(False),
    sort_order: str = Form("large-small"),
):
    try:
        rgb = decode_rgb(await image.read(), image.filename or "image")
        faces = detect_faces(
            rgb,
            detector=detector,
            det_size=det_size,
            threshold=threshold,
            try_rotations=try_rotations,
            sort_order=sort_order,
        )
        return {"count": len(faces), "faces": faces}
    except (ImageInputError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
