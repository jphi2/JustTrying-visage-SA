
import os
import sys
import cv2
import numpy as np

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

from visage.lib_visage import models
from visage.lib_visage.pipeline import (
    Options,
    identity_from_images,
    process
)

print("=" * 55)
print(" AI_VISAGE - PREMIER FACE SWAP")
print("=" * 55)

SOURCE = os.path.join(PROJECT, "tests", "test_face.jpg")
TARGET = os.path.join(PROJECT, "tests", "target_face.jpg")
OUTPUT = os.path.join(PROJECT, "tests", "result_swap.jpg")

# Initialisation des DLL CUDA
dll_dirs = []

site_packages = os.path.join(
    os.path.dirname(sys.executable),
    "..", "Lib", "site-packages", "nvidia"
)

for package in ("cu13", "cudnn"):
    folder = os.path.join(site_packages, package, "bin")

    if os.path.isdir(folder):
        dll_dirs.append(os.add_dll_directory(folder))

# Vérification des images
for path in (SOURCE, TARGET):
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

def load_rgb(path):
    image = cv2.imread(path)
    if image is None:
        raise RuntimeError(f"Image illisible : {path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

source = load_rgb(SOURCE)
target = load_rgb(TARGET)

# Configuration
opts = Options(
    swapper="hyperswap_1a_256",
    detector="retinaface_10g",
    det_size=640,
    det_threshold=0.5
)

print("\n1. Préparation de l'identité source")

identity, notes = identity_from_images(
    [source],
    opts
)

for note in notes:
    print("Avertissement :", note)

if identity is None:
    raise RuntimeError("Impossible d'extraire l'identité source.")

print("Identité source créée.")

# Vérification du modèle
print("\n2. Chargement du modèle de remplacement")

model_path = models.ensure(opts.swapper)
print("Modèle :", model_path)

# Traitement
print("\n3. Exécution du Face Swap")

result = process(
    target,
    [identity],
    opts
)

print("\nRésultat du traitement :")
print("Message :", result.message)
print("Visages trouvés :", result.faces_found)
print("Visages remplacés :", result.swapped)
print("Durée :", round(result.seconds, 2), "secondes")

if not result.swapped:
    raise RuntimeError("Aucun visage n'a été remplacé.")

# Sauvegarde
output = cv2.cvtColor(result.image, cv2.COLOR_RGB2BGR)

if not cv2.imwrite(OUTPUT, output):
    raise RuntimeError("Impossible de sauvegarder le résultat.")

print("\nImage enregistrée :", OUTPUT)
print("\nPREMIER FACE SWAP REUSSI")
