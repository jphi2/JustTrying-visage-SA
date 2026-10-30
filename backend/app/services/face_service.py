"""Face detection service backed directly by visage.lib_visage.analysis."""

from __future__ import annotations

from app.services.engine_service import get_engine


def detect_faces(
    image,
    *,
    detector: str = "retinaface_10g",
    det_size: int = 640,
    threshold: float = 0.5,
    try_rotations: bool = False,
    sort_order: str = "large-small",
) -> list[dict]:
    engine = get_engine()
    models = engine["models"]
    analysis = engine["analysis"]

    spec = models.REGISTRY.get(detector)
    if spec is None or spec.kind != "detector":
        raise ValueError(f"Modèle de détection inconnu ou invalide : {detector}")
    if sort_order not in analysis.SORT_ORDERS:
        raise ValueError(f"sort_order doit être parmi : {', '.join(analysis.SORT_ORDERS)}")
    if not 160 <= det_size <= 2048:
        raise ValueError("det_size doit être compris entre 160 et 2048.")
    if not 0.0 < threshold < 1.0:
        raise ValueError("threshold doit être strictement compris entre 0 et 1.")

    faces = analysis.detect(
        image,
        detector,
        det_size,
        threshold,
        try_rotations=try_rotations,
    )
    faces = analysis.sort_faces(faces, sort_order)
    return [
        {
            "index": index,
            "bbox": [float(value) for value in face.bbox.tolist()],
            "landmarks": [[float(x), float(y)] for x, y in face.kps.tolist()],
            "score": float(face.score),
            "area": float(face.area),
        }
        for index, face in enumerate(faces)
    ]
