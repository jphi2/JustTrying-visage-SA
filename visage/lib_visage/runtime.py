"""ONNX Runtime session management for Visage.

The standalone backend prepares CUDA/cuDNN before this module creates any
sessions. When used by Forge Neo, the runtime can still use ONNX Runtime's
standard DLL preloading behavior.
"""

from __future__ import annotations

import gc
import sys
import threading

from . import models

_sessions: dict[tuple[str, str], object] = {}
_lock = threading.RLock()
provider_preference = "auto"
prefer_gpu = True

_AUTO_ORDER = [
    "CUDAExecutionProvider",
    "TensorrtExecutionProvider",
    "ROCMExecutionProvider",
    "MIGraphXExecutionProvider",
    "DmlExecutionProvider",
    "CoreMLExecutionProvider",
    "CPUExecutionProvider",
]

PROVIDER_CHOICES = {
    "auto": None,
    "cuda": "CUDAExecutionProvider",
    "tensorrt": "TensorrtExecutionProvider",
    "rocm": "ROCMExecutionProvider",
    "migraphx": "MIGraphXExecutionProvider",
    "directml": "DmlExecutionProvider",
    "coreml": "CoreMLExecutionProvider",
    "cpu": "CPUExecutionProvider",
}


def configure_provider(preference: str = "auto", use_gpu: bool = True) -> None:
    """Set the requested execution provider before any sessions are created."""
    global provider_preference, prefer_gpu
    normalized = (preference or "auto").strip().lower()
    if normalized not in PROVIDER_CHOICES:
        raise ValueError(
            f"VISAGE_DEVICE invalide : {preference!r}. Valeurs admises : "
            f"{', '.join(PROVIDER_CHOICES)}"
        )
    with _lock:
        if _sessions and (normalized != provider_preference or bool(use_gpu) != prefer_gpu):
            raise RuntimeError("Impossible de modifier le fournisseur après la création de sessions ONNX.")
        provider_preference = normalized
        prefer_gpu = bool(use_gpu)


def ort():
    try:
        import onnxruntime
    except ImportError as exc:
        raise RuntimeError(
            "onnxruntime n'est pas installé dans l'interpréteur Python du projet. "
            "Installe les dépendances avec .\\python\\python.exe -m pip install -r requirements.txt."
        ) from exc
    if not hasattr(onnxruntime, "InferenceSession"):
        raise RuntimeError(
            "Installation ONNX Runtime invalide (InferenceSession absent). "
            "Vérifie qu'une seule distribution onnxruntime est installée."
        )
    return onnxruntime


def available_providers() -> list[str]:
    try:
        return list(ort().get_available_providers())
    except RuntimeError:
        return []


def resolve_providers() -> list:
    available = available_providers()
    requested = PROVIDER_CHOICES[provider_preference]

    if requested:
        if requested not in available:
            raise RuntimeError(
                f"Le fournisseur ONNX Runtime demandé ({requested}) est indisponible. "
                f"Fournisseurs disponibles : {available}"
            )
        chosen = [requested]
    elif not prefer_gpu:
        if "CPUExecutionProvider" not in available:
            raise RuntimeError(f"CPUExecutionProvider indisponible : {available}")
        chosen = ["CPUExecutionProvider"]
    else:
        chosen = [name for name in _AUTO_ORDER if name in available][:1]
        if not chosen:
            raise RuntimeError(f"Aucun fournisseur ONNX Runtime utilisable : {available}")

    if chosen[0] != "CPUExecutionProvider" and "CPUExecutionProvider" in available:
        chosen.append("CPUExecutionProvider")
    return [_with_options(provider) for provider in chosen]


def _with_options(name: str):
    if name == "CUDAExecutionProvider":
        return (name, {"device_id": 0, "cudnn_conv_algo_search": "HEURISTIC", "arena_extend_strategy": "kSameAsRequested"})
    if name == "TensorrtExecutionProvider":
        return (name, {"trt_engine_cache_enable": True, "trt_engine_cache_path": models.models_dir() + "/trt_cache"})
    return name


def active_provider() -> str:
    provider = resolve_providers()[0]
    return provider[0] if isinstance(provider, tuple) else provider


def ort_gpu_spec(cuda_major: int | None) -> str:
    """Return the PyPI ONNX Runtime GPU constraint matching the CUDA major."""
    return "onnxruntime-gpu<1.27" if cuda_major is not None and cuda_major < 13 else "onnxruntime-gpu>=1.27"


def gpu_hint(nvidia: bool, cuda_major: int | None = None) -> str | None:
    """Compatibility helper retained for the Forge Neo integration module."""
    available = available_providers()
    if not nvidia or not available or {"CUDAExecutionProvider", "TensorrtExecutionProvider"} & set(available):
        return None
    python_exe = sys.executable
    return (
        "Visage fonctionne actuellement sur CPU : un GPU NVIDIA est détecté, "
        "mais ONNX Runtime n'expose aucun fournisseur CUDA/TensorRT. "
        f"Dans l'environnement Python actif ({python_exe}), vérifie la distribution ONNX Runtime "
        f"et la compatibilité CUDA. Version conseillée : {ort_gpu_spec(cuda_major)}."
    )


def _prepare_cuda() -> None:
    """Fallback preload for non-standalone callers (e.g. the Forge extension)."""
    rt = ort()
    preload = getattr(rt, "preload_dlls", None)
    if preload is not None:
        preload()


def session(key: str, progress=None):
    path = models.ensure(key, progress)
    provider = active_provider()
    cache_key = (path, provider)
    with _lock:
        sess = _sessions.get(cache_key)
        if sess is None:
            rt = ort()
            if provider in ("CUDAExecutionProvider", "TensorrtExecutionProvider"):
                _prepare_cuda()
            options = rt.SessionOptions()
            options.log_severity_level = 3
            options.graph_optimization_level = rt.GraphOptimizationLevel.ORT_ENABLE_ALL
            requested_providers = resolve_providers()
            sess = rt.InferenceSession(path, sess_options=options, providers=requested_providers)
            actual = sess.get_providers()
            if provider in ("CUDAExecutionProvider", "TensorrtExecutionProvider") and (
                not actual or actual[0] != provider
            ):
                raise RuntimeError(
                    f"Le fournisseur demandé ({provider}) n'est pas le fournisseur principal de la session. "
                    f"Fournisseurs de la session : {actual}"
                )
            _sessions[cache_key] = sess
        return sess


def loaded() -> list[str]:
    return sorted({path for path, _ in _sessions})


def loaded_session_status() -> list[dict[str, object]]:
    """Describe the providers actually attached to each instantiated session."""
    with _lock:
        return [
            {"model_path": path, "requested_provider": requested, "session_providers": sess.get_providers()}
            for (path, requested), sess in _sessions.items()
        ]


def unload(kind: str | None = None) -> int:
    with _lock:
        if kind is None:
            dropped = len(_sessions)
            _sessions.clear()
        else:
            paths = {models.local_path(key) for key in models.keys_of(kind)}
            victims = [key for key in _sessions if key[0] in paths]
            for key in victims:
                del _sessions[key]
            dropped = len(victims)
    gc.collect()
    return dropped


def input_names(sess) -> list[str]:
    return [item.name for item in sess.get_inputs()]
