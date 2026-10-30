Voici une synthèse technique complète de l'avancement du projet AI\_Visage, conçue comme un document de reprise. Tu pourras la conserver et la coller intégralement dans une nouvelle conversation ChatGPT afin que nous puissions reprendre le développement sans devoir refaire les étapes précédentes.

J'ai volontairement inclus les chemins, versions, composants, résultats des tests, particularités techniques et prochaines étapes. J'ai également distingué les éléments effectivement validés de ceux qui restent à développer.

Écriture

# AI\_VISAGE — DOCUMENT DE REPRISE DU PROJET

**État du projet au 30 octobre 2026**

## 1\. Présentation générale du projet

Le projet AI\_Visage consiste à développer une application locale de remplacement de visages (Face Swap), sous Windows, exploitant les capacités du GPU NVIDIA pour effectuer les traitements d'intelligence artificielle.

Le moteur de traitement est basé sur une adaptation de l'extension Visage de Forge Neo, dont les modules Python ont été récupérés et intégrés dans un projet autonome.

L'objectif est de disposer d'une application indépendante de Stable Diffusion / Forge Neo, avec :

- Détection automatique des visages.
- Extraction et gestion des identités.
- Remplacement de visages (Face Swap).
- Gestion de plusieurs visages dans une même image.
- Sélection des modèles de remplacement.
- Gestion des masques et des occultations.
- Restauration et amélioration des visages.
- Traitement accéléré par GPU NVIDIA.
- Interface graphique permettant de piloter les opérations.
- Prévisualisation et sauvegarde des résultats.

Le moteur technique est désormais opérationnel et les premiers tests fonctionnels ont réussi.

---

## 2\. Environnement informatique

### Système

- Windows 10.
- PowerShell.
- GPU NVIDIA compatible CUDA.
- Installation Python indépendante du Python utilisé par les autres applications.

### Python

Version installée :

- Python 3.13.17

Interpréteur principal : `C:\Users\jpp\AppData\Local\Programs\Python\Python313\python.exe`

Environnement virtuel du projet : `E:\SYNC-01M.I7\80_Developpements_Informatique\Python\Projects\AI_Visage\python\venv`

Interpréteur à utiliser systématiquement : `E:\SYNC-01M.I7\80_Developpements_Informatique\Python\Projects\AI_Visage\python\venv\Scripts\python.exe`

Important : utiliser cet interpréteur plutôt que le Python 3.10 préexistant sur la machine.

Python 3.10 est toujours installé et visible dans le lanceur Windows, mais le projet utilise Python 3.13.17.

### Répertoire principal

`E:\SYNC-01M.I7\80_Developpements_Informatique\Python\Projects\AI_Visage`

Variable PowerShell couramment utilisée :

powershell

```
$Project = "E:\SYNC-01M.I7\80_Developpements_Informatique\Python\Projects\AI_Visage"
```

Le répertoire contenant la bibliothèque du moteur :

powershell

```
$Lib = "$Project\visage\lib_visage"
```

---

## 3\. Installation et dépendances

L'installation de Python a été automatisée avec un script PowerShell.

Le script a :

- Téléchargé Python 3.13.17.
- Installé Python.
- Créé l'environnement virtuel.
- Mis à jour pip.

L'installation des dépendances a ensuite été réalisée à partir du fichier requirements du projet.

Principaux composants installés et vérifiés :

| Composant | Version |
| --- | --- |
| Python | 3.13.17 |
| pip | 26.2.2 |
| NumPy | 2.5.4 |
| OpenCV | 5.0.0 |
| ONNX Runtime GPU | 1.31.1 |
| CUDA | 13.x |
| cuDNN | 9.x |

Les paquets NVIDIA identifiés :

- nvidia-cublas 13.8.0.4
- nvidia-cuda-nvrtc 13.4.92
- nvidia-cuda-runtime 13.4.92
- nvidia-cudnn-cu13 9.27.0.42
- nvidia-cufft 12.4.0.43
- nvidia-curand 10.4.4.72
- nvidia-nvjitlink 13.4.92
- onnxruntime-gpu 1.31.1

Les bibliothèques CUDA et cuDNN sont présentes dans l'environnement virtuel.

---

## 4\. Configuration de l'accélération GPU

Une difficulté a été rencontrée lors de la première initialisation d'ONNX Runtime.

Les bibliothèques CUDA étaient installées, mais ONNX Runtime ne parvenait pas à charger correctement :

`cublasLt64_13.dll`

Le diagnostic a révélé que les DLL étaient présentes dans les répertoires de l'environnement virtuel, mais qu'elles n'étaient pas correctement accessibles au chargement du fournisseur CUDA.

Une correction a été apportée au script de diagnostic :

- Identification des répertoires NVIDIA.
- Préchargement des DLL CUDA.
- Préchargement des DLL cuDNN.
- Utilisation de `os.add_dll_directory()` pour déclarer les chemins nécessaires sous Windows.

Les DLL suivantes ont été localisées :

text

```
nvidia\cu13\bin\x86_64\cublas64_13.dll
nvidia\cu13\bin\x86_64\cublasLt64_13.dll
nvidia\cu13\bin\x86_64\cudart64_13.dll

nvidia\cudnn\bin\cudnn64_9.dll
```

### Résultat final

Les fournisseurs ONNX actifs dans la session sont :

python

```
['CUDAExecutionProvider', 'CPUExecutionProvider']
```

Une inférence réelle sur GPU a été exécutée avec succès.

Le test a chargé un modèle RetinaFace avec une entrée de dimensions :

`[1, 3, 640, 640]`

Les neuf sorties du modèle ont été calculées correctement.

**Le fonctionnement CUDA est donc validé.**

Attention : les fournisseurs disponibles au niveau global peuvent inclure TensorRT, CUDA et CPU, mais le test effectivement réussi a utilisé CUDA et CPU.

---

## 5\. Récupération du moteur Visage

Le code source de l'extension Visage de Forge Neo a été récupéré depuis :

text

```
C:\Users\jpp\sd-webui-forge-neo\extensions\visage-forge-neo
```

Le fichier `pyproject.toml` indique :

toml

```
[project]
name = "visage-forge-neo"
version = "0.4.0"
requires-python = ">=3.11"
```

La bibliothèque Python a été copiée dans le projet autonome :

text

```
AI_Visage\visage\lib_visage
```

Modules récupérés :

text

```
analysis.py
facemodel.py
forge.py
geometry.py
hashes.py
masks.py
models.py
onnxread.py
pipeline.py
preview.py
restorer.py
runtime.py
safety.py
swapper.py
__init__.py
```

Les imports internes du moteur ont été examinés.

Dépendances externes principales identifiées :

- NumPy
- OpenCV
- ONNX Runtime
- Pillow
- Bibliothèques standard Python

Certains modules de l'extension d'origine font référence à `modules.paths` et `modules.shared`, qui appartiennent à Forge Neo. Il faudra vérifier précisément les chemins concernés avant de supprimer définitivement toute dépendance à Forge Neo.

---

## 6\. Architecture du moteur

Le moteur est organisé autour de plusieurs modules.

### analysis.py

Responsable de :

- Détection des visages.
- Extraction des caractéristiques.
- Classification éventuelle.
- Tri des visages.
- Comparaison de similarité.

### facemodel.py

Gestion des identités et des embeddings.

### geometry.py

Transformations géométriques :

- Alignement des visages.
- Déformations.
- Transformations de perspective.
- Réinsertion des visages dans l'image originale.

### hashes.py

Gestion des empreintes SHA-256 des modèles.

### masks.py

Gestion des masques :

- Masques rectangulaires.
- Masques d'occlusion.
- Segmentation faciale.
- Régions anatomiques.
- Fusion des masques.

### models.py

Registre et téléchargement des modèles.

### onnxread.py

Gestion de la lecture et de l'exécution des modèles ONNX.

### pipeline.py

Orchestration du traitement complet.

### restorer.py

Restauration et amélioration des visages.

### runtime.py

Gestion du runtime ONNX et des fournisseurs d'exécution.

### safety.py

Filtrage optionnel du contenu NSFW.

### swapper.py

Exécution des modèles de remplacement de visages.

---

## 7\. Registre des modèles

Le moteur possède actuellement 37 modèles enregistrés.

### Détecteurs

- retinaface\_10g
- scrfd\_2.5g
- yoloface\_8n

### Reconnaissance faciale

- arcface\_w600k\_r50

### Landmark estimator

- fan\_68\_5

### Classification

- fairface

### Swappers

- hyperswap\_1a\_256
- hyperswap\_1b\_256
- hyperswap\_1c\_256
- inswapper\_128
- inswapper\_128\_fp16
- reswapper\_128
- reswapper\_256
- simswap\_256
- simswap\_unofficial\_512
- ghost\_1\_256
- ghost\_2\_256
- ghost\_3\_256
- hififace\_unofficial\_256
- alphaface\_256

### Convertisseurs d'identité

- crossface\_ghost
- crossface\_simswap
- crossface\_hififace

### Filtres de sécurité

- nsfw\_1
- nsfw\_2
- nsfw\_3

### Restaurateurs

- gfpgan\_1.4
- codeformer
- gpen\_bfr\_256
- gpen\_bfr\_512
- gpen\_bfr\_1024
- gpen\_bfr\_2048
- restoreformer\_plus\_plus

### Masques et segmentation

- xseg\_1
- xseg\_2
- bisenet\_resnet\_34
- bisenet\_resnet\_18

Les modèles sont téléchargés à la demande et stockés localement.

Le répertoire de modèles observé lors des tests est :

text

```
C:\Users\jpp\models\visage
```

La fonction `models.ensure()` gère les téléchargements et la vérification éventuelle des empreintes SHA-256.

Les modèles ne sont pas distribués avec le code source.

Attention aux licences : plusieurs modèles sont réservés à un usage non commercial ou à la recherche. Il faudra respecter les conditions de chaque modèle avant toute distribution de l'application.

---

## 8\. Pipeline de traitement

Le fichier `pipeline.py` constitue le cœur du moteur.

Il contient notamment :

python

```
@dataclass
class Options:
```

Les paramètres disponibles comprennent :

- swapper
- detector
- det\_size
- det\_threshold
- try\_rotations
- target\_indexes
- sort\_order
- gender
- min\_face\_size
- strength
- pixel\_boost
- mask\_box
- mask\_blur
- mask\_padding
- mask\_model
- mask\_occlusion
- occluder
- mask\_region
- parser
- regions
- region\_dilate
- keep\_mouth
- color\_match
- restorer
- restorer\_visibility
- codeformer\_weight
- face\_boost
- restore\_guard
- report\_similarity
- sfw

Valeurs par défaut importantes :

python

```
swapper = "hyperswap_1a_256"
detector = "retinaface_10g"
det_size = 640
det_threshold = 0.5
strength = 1.0
pixel_boost = 1
restorer = "none"
color_match = False
```

Les fonctions principales :

python

```
identity_from_images()
identities_from_image()
select_targets()
process()
restore_only()
```

Le traitement complet comprend :

1. Détection des visages cibles.
2. Sélection des visages à remplacer.
3. Extraction de l'identité source.
4. Fusion éventuelle de l'identité.
5. Remplacement du visage.
6. Construction et application du masque.
7. Harmonisation des couleurs facultative.
8. Restauration facultative.
9. Réinsertion dans l'image.
10. Calcul éventuel de la similarité.

Le moteur permet également le traitement de plusieurs visages et plusieurs identités.

---

## 9\. Tests effectués et résultats

Tous les tests suivants ont été exécutés avec succès.

### Test 1 — Installation Python

Résultat :

- Python 3.13.17 installé.
- Environnement virtuel créé.
- pip opérationnel.

### Test 2 — Installation des dépendances

Résultat :

- Dépendances installées.
- Bibliothèques importables.

### Test 3 — Accélération GPU

Résultat :

- CUDA fonctionnel.
- cuDNN fonctionnel.
- ONNX Runtime GPU fonctionnel.
- Inférence réelle réussie.

### Test 4 — Importation du moteur

Résultat :

text

```
IMPORTS OK

Modèles enregistrés : 37

Détecteurs :
['retinaface_10g', 'scrfd_2.5g', 'yoloface_8n']
```

Les paramètres par défaut du pipeline ont également été affichés correctement.

### Test 5 — Détection des visages

Script :

text

```
tests/test_detection.py
```

Modèle utilisé :

`retinaface_10g`

Image de test :

text

```
Dimensions : (2432, 1664, 3)
```

Résultat :

text

```
Visages détectés : 1

Bounding box :
[734.7309 221.44753 907.0011 449.46835]

Score :
0.8727755546569824

TEST DE DETECTION REUSSI
```

Le modèle RetinaFace a été téléchargé automatiquement.

### Test 6 — Extraction d'identité

Script :

text

```
tests/test_identity.py
```

Modèle utilisé :

`arcface_w600k_r50`

Le modèle a été téléchargé automatiquement (environ 166 MB).

Résultat :

text

```
Visages : 1

Extraction embedding

Type :
<class 'numpy.ndarray'>

Dimensions :
(512,)

Valeurs finies :
True

Norme L2 :
18.439041

TEST EXTRACTION IDENTITE REUSSI
```

L'extraction d'identité fonctionne correctement.

### Test 7 — Face Swap complet

Script :

text

```
tests/test_faceswap.py
```

**TEST RÉUSSI.**

Le premier remplacement de visage a été effectué avec succès.

Ce résultat valide le fonctionnement intégré du pipeline, au-delà des simples tests isolés de détection et d'extraction d'identité.

Les détails exacts de l'image de test, du modèle utilisé et du temps de traitement ne sont pas encore consignés dans ce document.

---

## 10\. État actuel du projet

### Éléments validés

- Installation autonome de Python.
- Environnement virtuel.
- Installation des dépendances.
- Accélération GPU CUDA.
- ONNX Runtime.
- Importation du moteur.
- Registre de 37 modèles.
- Téléchargement des modèles.
- Détection faciale.
- Extraction d'identité.
- Exécution du Face Swap complet.

**Le moteur de traitement est fonctionnel.**

### Éléments restant à développer ou à vérifier

- Interface graphique autonome.
- Chargement des images par l'utilisateur.
- Gestion visuelle des identités sources.
- Gestion visuelle des visages cibles.
- Sélection interactive des visages.
- Choix des modèles.
- Paramètres avancés de traitement.
- Prévisualisation avant/après.
- Sauvegarde des résultats.
- Gestion des erreurs et des téléchargements.
- Vérification de l'indépendance complète vis-à-vis de Forge Neo.
- Optimisation des performances.
- Tests avec plusieurs visages.
- Tests avec les différents swappers et restaurateurs.

---

## 11\. Orientation proposée pour la suite

La prochaine étape consiste à passer du moteur technique à une application utilisable.

Je recommande de procéder progressivement.

### Étape A — Architecture de l'application

Définir :

- La technologie de l'interface graphique.
- L'organisation des modules.
- La communication entre interface et moteur.
- La gestion des paramètres.
- La gestion des fichiers temporaires.
- La gestion des modèles.

Il faudra privilégier une architecture modulaire afin de ne pas mélanger l'interface graphique et le moteur de traitement.

### Étape B — Interface principale

Prévoir une interface comprenant :

1. Zone Image source.
2. Zone Image cible.
3. Zone de détection et sélection des visages.
4. Zone des paramètres de traitement.
5. Bouton de lancement.
6. Zone de prévisualisation du résultat.
7. Fonction de sauvegarde.

### Étape C — Paramètres avancés

Intégrer progressivement :

- Choix du swapper.
- Taille de traitement.
- Force du remplacement.
- Pixel boost.
- Masques.
- Harmonisation des couleurs.
- Restauration faciale.
- CodeFormer.
- GFPGAN.
- Contrôle de similarité.

### Étape D — Finalisation

- Interface ergonomique.
- Gestion des erreurs.
- Optimisation GPU.
- Tests de stabilité.
- Documentation.
- Installation simplifiée.

---

## 12\. Consignes importantes pour la reprise du projet

Lors de la reprise dans une nouvelle conversation ChatGPT :

1. Considérer que les tests techniques précédemment mentionnés sont réussis.
2. Ne pas recommencer l'installation Python.
3. Ne pas réinstaller les dépendances sans raison précise.
4. Ne pas modifier la configuration CUDA qui fonctionne.
5. Ne pas réécrire les modules du moteur sans nécessité.
6. Conserver la structure actuelle du projet.
7. Utiliser systématiquement l'interpréteur Python de l'environnement virtuel.
8. Travailler par étapes successives.
9. Fournir des scripts complets, directement exécutables depuis PowerShell.
10. Privilégier les solutions automatisées plutôt que les manipulations manuelles.
11. Faire valider chaque étape avant de passer à la suivante.

Pour toute modification du moteur, demander d'abord le contenu actuel du fichier concerné afin d'éviter d'écraser des modifications déjà réalisées.

Ne pas supposer qu'un fichier, un script ou une fonctionnalité existe sans l'avoir vérifié.

---

## 13\. Informations de référence pour les prochaines commandes PowerShell

Initialisation habituelle :

powershell

```
$Project = "E:\SYNC-01M.I7\80_Developpements_Informatique\Python\Projects\AI_Visage"

$Python = "$Project\python\venv\Scripts\python.exe"

$Lib = "$Project\visage\lib_visage"
```

Exécution d'un script :

powershell

```
& $Python "$Project\tests\test_faceswap.py"
```

Vérification de Python :

powershell

```
& $Python --version
```

Vérification d'ONNX Runtime :

powershell

```
& $Python -c "import onnxruntime as ort; print(ort.__version__); print(ort.get_available_providers())"
```

---

# 14\. POINT DE REPRISE — INSTRUCTIONS POUR CHATGPT

Nous poursuivons le développement du projet AI\_Visage.

Le moteur autonome de Face Swap a été récupéré depuis Visage Forge Neo et intégré dans un projet Python indépendant.

L'environnement Windows, Python 3.13.17, ONNX Runtime GPU, CUDA 13 et cuDNN 9 sont opérationnels.

Les tests de détection RetinaFace, d'extraction d'identité ArcFace et le test complet `test_faceswap.py` ont réussi.

Le projet possède un registre de 37 modèles et un pipeline de traitement fonctionnel dans `visage/lib_visage`.

La prochaine mission est de concevoir et développer l'interface graphique de l'application, en conservant le moteur actuel intact.

Nous devons avancer étape par étape, avec des scripts complets et des commandes PowerShell directement exécutables.

**Première tâche à effectuer à la reprise : examiner l'arborescence actuelle du projet et les fichiers existants liés aux tests et à l'interface, puis proposer l'architecture graphique la plus adaptée.**

Ne pas repartir de zéro et ne pas refaire les tests déjà validés, sauf nécessité technique.

Fin du document de reprise.

## Mon conseil pour la reprise

Conserve ce document dans ton projet, par exemple sous :

`AI_Visage\docs\REPRISE_PROJET_AI_VISAGE.md`

Il servira de référence technique.

Un dernier point important : je n'ai pas inventé les résultats détaillés du test `test_faceswap.py`, puisque tu m'as simplement confirmé sa réussite sans fournir sa sortie complète. Nous pourrons compléter cette partie ultérieurement.

À la prochaine conversation, joins ce document et nous pourrons reprendre directement à la conception de l'interface graphique, sans revenir sur toute l'installation et les validations déjà réalisées.