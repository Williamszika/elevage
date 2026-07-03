# Ferme d'élevage ovin — Tchoro (Korhogo)

Générateurs de documents pour le projet : dossier architectural + vue 3D, plan de
construction, fiche d'achat des moutons, présentation partenaires (PowerPoint) et
maquette 3D interactive.

Tous les scripts sont autonomes. Ouvre ce dossier dans Claude Code et lance les
commandes ci-dessous.

## 1. Contenu

```
elevage/
├── python/
│   ├── make_arch.py            → Dossier architectural + VUE 3D (PDF, 4 pages)
│   ├── make_plan400.py         → Plan de construction sur 400 m² (PDF, 3 pages)
│   ├── make_fiche.py           → Fiche d'achat des moutons au marché (PDF, 2 pages)
│   └── draw_plan_png.py        → Régénère l'image du plan de masse (assets/site_plan.*)
├── node/
│   └── build_deck.js           → Présentation partenaires (PowerPoint .pptx, 17 diapos)
├── web/
│   └── maquette_3d_ferme.html  → Maquette 3D interactive (à ouvrir dans un navigateur)
├── assets/
│   └── site_plan.png           → Image du plan de masse (utilisée par la présentation)
├── output/                     → Les fichiers générés arrivent ici
├── requirements.txt            → Dépendances Python
└── package.json                → Dépendances Node
```

## 2. Prérequis

* Python 3.9+ (pour les documents PDF)
* Node.js 18+ (pour la présentation PowerPoint)

Vérifier :

```bash
python3 --version
node --version
```

## 3. Installation

Depuis la racine du projet :

```bash
pip install -r requirements.txt      # Python (reportlab)
npm install                          # Node (pptxgenjs — uniquement pour la présentation)
```

## 4. Génération des documents

⚠️ Lancer les commandes depuis la racine du projet (pour que le dossier `output/`
soit trouvé — les scripts le créent au besoin).

**Dossier architectural + vue 3D (PDF)**

```bash
python3 python/make_arch.py
# → output/dossier_architectural_ferme.pdf
```

**Plan de construction 400 m² (PDF)**

```bash
python3 python/make_plan400.py
# → output/plan_construction_ferme_400m2.pdf
```

**Fiche d'achat des moutons (PDF)**

```bash
python3 python/make_fiche.py
# → output/fiche_achat_moutons.pdf
```

**Présentation partenaires (PowerPoint)**

```bash
npm run build:deck
# ou : node node/build_deck.js
# → output/presentation_ferme_moutons.pptx
```

**Maquette 3D interactive**

Aucune installation. Ouvre simplement le fichier dans un navigateur récent
(Chrome, Edge, Safari, Firefox) :

```
web/maquette_3d_ferme.html
```

* Glisser : tourner autour de la ferme
* Molette : zoomer
* Clic droit : déplacer
* Bouton en haut à droite : rotation automatique / recentrer

> La maquette charge la bibliothèque Three.js depuis internet : une connexion est
> nécessaire au premier chargement.

## 5. Notes utiles

* **Polices / accents** : les scripts PDF cherchent automatiquement la police
  DejaVuSans (Windows, macOS, Linux). Si elle n'est pas trouvée, ils utilisent
  Helvetica (les accents français restent corrects). Pour un rendu identique
  partout, installe la police [DejaVu Sans](https://dejavu-fonts.github.io/)
  (gratuite).
* **Image du plan dans la présentation** : `assets/site_plan.png` est fournie.
  Pour la régénérer : `python3 python/draw_plan_png.py` (produit
  `assets/site_plan.pdf`, et directement `assets/site_plan.png` si l'outil
  `pdftoppm` de poppler est installé ; sinon convertir le PDF en PNG).
* **À personnaliser avant de présenter** : dans `node/build_deck.js`, la
  constante `CONTACT` (nom du porteur « Williams », téléphone, email, lieu).
  Les montants sont des ordres de grandeur.
* **Rappel** : les vues 3D et les plans sont des représentations « vue
  d'artiste », non contractuelles. Avant construction, fais coter et valider les
  plans par un maçon ou un technicien du bâtiment sur place.

## 6. Modifier le contenu

* **Chiffres, prix, textes des PDF** : directement dans les scripts
  `python/*.py` (le texte est en clair, en français).
* **Dimensions / implantation de la ferme** : les coordonnées (en mètres) sont
  définies en haut de `make_arch.py` et `make_plan400.py` (dictionnaire
  `ZONES`). La maquette 3D (`web/maquette_3d_ferme.html`) utilise **les mêmes
  coordonnées** — pense à les garder cohérentes entre les fichiers.
* **Diapositives** : contenu et mise en page dans `node/build_deck.js`.
```

_Projet : ferme d'élevage ovin, Tchoro — Korhogo (Côte d'Ivoire)._
