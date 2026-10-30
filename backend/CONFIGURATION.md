# Backend configuration

The backend loads the repository-root `.env` file through `python-dotenv`.
Environment variables already defined by the process take precedence over the
file. Relative paths are resolved from the repository root, not from the
terminal's current working directory.

## Shared model locations

| Variable | Purpose |
| --- | --- |
| `VISAGE_ONNX_MODELS_DIR` | Root directory used by `lib_visage.models` for its ONNX registry and downloads |
| `VISAGE_NATIVE_FACE_MODELS_DIR` | Existing Visage native face identities |
| `VISAGE_REACTOR_FACE_MODELS_DIR` | Existing ReActor face identities |
| `VISAGE_SHARED_MODELS_ROOT` | Shared model collection root |
| `VISAGE_FACE_MODELS_OUTPUT_DIR` | Destination for newly created face identities |

These locations are intentionally independent. The backend does not copy,
move, rename, or automatically create the shared model directories. The
existing `VISAGE_ONNX_MODELS_DIR` is passed to `lib_visage.models.set_models_dir`.

## Application working directories

- `VISAGE_INPUT_DIR`: incoming images
- `VISAGE_OUTPUT_DIR`: processed images
- `VISAGE_TEMP_DIR`: temporary processing files

Relative values (for example `./input`) are rooted at the repository root.
Only application-owned working/output directories are created automatically.

## Server and execution preferences

- `VISAGE_HOST` (default `127.0.0.1`)
- `VISAGE_PORT` (default `8765`)
- `VISAGE_DEVICE` (default `auto`)
- `VISAGE_PREFER_GPU` (default `true`)
- `AI_VISAGE_DEBUG` (default `0`)

The device and GPU preference values are loaded into application settings
and applied to ONNX Runtime before the engine creates model sessions.

Do not replace an existing `.env` with `.env.example`: retain the established
model paths in the local `.env` file. `.env` is excluded from Git.

## GPU / ONNX Runtime

Le Python autonome est installé directement dans `python\\` (aucun `venv`).
Les bibliothèques CUDA/cuDNN distribuées par pip sont recherchées dans
`python\\Lib\\site-packages\\nvidia`. Le backend enregistre les dossiers qui
contiennent des DLL NVIDIA puis appelle `onnxruntime.preload_dlls()` avant
la création des sessions ONNX.

- `VISAGE_DEVICE=cuda` : CUDA est obligatoire ; le démarrage échoue si
  `CUDAExecutionProvider` n'est pas disponible.
- `VISAGE_DEVICE=auto` : choisit le premier provider disponible dans l'ordre
  CUDA, TensorRT, ROCm, MIGraphX, DirectML, CoreML, CPU si
  `VISAGE_PREFER_GPU=true` ; sinon force CPU.
- `VISAGE_DEVICE=cpu` : force CPU.
- `VISAGE_DEVICE=tensorrt` : exige `TensorrtExecutionProvider`.

`GET /api/system` expose la disponibilité des providers et les providers
réellement associés aux sessions ONNX déjà chargées. La disponibilité du
provider seule ne prouve pas qu'une inférence GPU a été exécutée.

Test réel (nécessite le modèle RetinaFace déjà présent, sans téléchargement) :

```powershell
.\\python\\python.exe tests\\test_onnx_gpu.py
```
