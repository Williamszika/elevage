#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan de masse architectural DÉTAILLÉ — Ferme d'élevage ovin, Tchoro (Korhogo).

Génère un plan de masse complet, à l'échelle, montrant TOUTES les infrastructures
du projet (bâtiments, élevage/manipulation, réseaux eau/électricité/assainissement,
gestion des effluents, aménagements extérieurs) avec une LÉGENDE numérotée, une
sous-légende des réseaux, une échelle graphique, une rose des vents et un cartouche.

Sortie : output/plan_masse_detaille.svg  (fichier vectoriel autonome).

Lancer depuis la racine du projet :
    python3 python/make_site_master.py

Autonome : n'utilise que la bibliothèque standard de Python (aucune dépendance).
Les coordonnées (en mètres) prolongent celles de make_arch.py / make_plan400.py.
"""

import os

# ---------------------------------------------------------------------------
# Palette (esprit « planche de dessin »)
# ---------------------------------------------------------------------------
PAPER    = "#f7f4ec"
INK      = "#22303a"
INK_SOFT = "#5b6b70"
GREEN    = "#2e7d32"
GREEN_D  = "#1b5e20"
WALL     = "#efe7d6"
ROOF     = "#b0463c"
SAND     = "#e9dcc2"
GRASS    = "#d7e6c2"
EARTH    = "#8d6e63"
WATER    = "#2f79b8"
ELEC     = "#e0952b"
DRAIN    = "#9c7a52"
VEG      = "#6f9a4e"
PATH     = "#e7e1d1"
BADGE    = "#1b5e20"

SANS = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
MONO = "ui-monospace, 'DejaVu Sans Mono', 'Courier New', monospace"

# ---------------------------------------------------------------------------
# Géométrie du dessin
# ---------------------------------------------------------------------------
W, H = 1580, 1160
SCALE = 38.0            # px par mètre
PLOT = 20.0
DX = 70                 # x px du bord gauche du terrain
DYB = 910               # y px du bas du terrain (SVG : y vers le bas)


def X(m): return DX + m * SCALE
def Y(m): return DYB - m * SCALE


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


S = []   # fragments SVG


def rectm(x0, y0, x1, y1, fill, stroke=INK, sw=1.4, dash=None, rx=0, opacity=1):
    d = 'stroke-dasharray="%s" ' % dash if dash else ""
    o = 'opacity="%s" ' % opacity if opacity != 1 else ""
    S.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" '
             'fill="%s" stroke="%s" stroke-width="%.2f" %s%s/>'
             % (X(x0), Y(y1), (x1 - x0) * SCALE, (y1 - y0) * SCALE, rx,
                fill, stroke, sw, d, o))


def line(pts, stroke, sw=1.6, dash=None, cap="butt", opacity=1):
    d = 'stroke-dasharray="%s" ' % dash if dash else ""
    o = 'opacity="%s" ' % opacity if opacity != 1 else ""
    pl = " ".join("%.1f,%.1f" % (X(px), Y(py)) for px, py in pts)
    S.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.2f" '
             'stroke-linecap="%s" stroke-linejoin="round" %s%s/>'
             % (pl, stroke, sw, cap, d, o))


def circ(xm, ym, r_px, fill, stroke=INK, sw=1.2):
    S.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
             'stroke-width="%.2f"/>' % (X(xm), Y(ym), r_px, fill, stroke, sw))


def text(px, py, s, size, fill=INK, font=SANS, anchor="start", weight="normal",
         spacing=None, italic=False):
    ls = 'letter-spacing="%s" ' % spacing if spacing else ""
    it = 'font-style="italic" ' if italic else ""
    S.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
             'text-anchor="%s" font-weight="%s" %s%s>%s</text>'
             % (px, py, font, size, fill, anchor, weight, ls, it, esc(s)))


def textm(xm, ym, s, size, **kw):
    text(X(xm), Y(ym), s, size, **kw)


def badge(xm, ym, num):
    """Pastille numérotée sur le dessin."""
    px, py = X(xm), Y(ym)
    S.append('<circle cx="%.1f" cy="%.1f" r="10.5" fill="%s" stroke="#ffffff" '
             'stroke-width="1.6"/>' % (px, py, BADGE))
    S.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="12.5" fill="#fff" '
             'text-anchor="middle" font-weight="bold">%s</text>'
             % (px, py + 4.3, MONO, num))


def tree(xm, ym, r=0.9):
    circ(xm, ym, r * SCALE, VEG, stroke=GREEN_D, sw=1.2)
    circ(xm, ym, r * SCALE * 0.55, "#7fae5c", stroke="none", sw=0)


def light_pole(xm, ym):
    px, py = X(xm), Y(ym)
    S.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="%s" stroke="%s" '
             'stroke-width="1.2"/>' % (px, py, ELEC, INK))
    for dx, dy in [(-9, -9), (9, -9), (-9, 9), (9, 9)]:
        S.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1"/>' % (px, py, px + dx, py + dy, ELEC))


# ===========================================================================
# CONSTRUCTION DU DESSIN
# ===========================================================================
def build_drawing():
    # --- fond terrain (parcelle) ---
    rectm(0, 0, PLOT, PLOT, GRASS, stroke=GREEN_D, sw=2.6)

    # --- allées de circulation (23) ---
    rectm(2, 11.5, 14, 12.5, PATH, stroke="none")          # bergerie <-> aire
    rectm(14, 0.4, 15, 18.6, PATH, stroke="none")          # couloir de service vertical
    rectm(0.2, 0.4, 14, 2, PATH, stroke="none", opacity=0.55)  # esplanade d'entrée

    # --- Aire d'exercice (6) ---
    rectm(2, 2, 14, 11.5, SAND, stroke=GREEN_D, sw=1.4, dash="7 5")

    # --- Bergerie (1) avec trame des 6 cases + couloir ---
    rectm(2, 12.5, 14, 18.5, WALL, stroke=INK, sw=1.8)
    line([(2, 13.7), (14, 13.7)], INK, sw=1.0)             # couloir de service
    for i in range(1, 6):
        x = 2 + i * 2.0
        line([(x, 13.7), (x, 18.5)], INK, sw=0.9)
    textm(8, 13.05, "couloir de service", 10.5, fill=INK_SOFT, anchor="middle", font=MONO)

    # --- Bâtiments de service (colonne droite) ---
    rectm(15, 13, 18.5, 18.5, WALL, stroke=INK, sw=1.6)    # 2 hangar fourrage
    rectm(15, 8, 18.5, 12.5, WALL, stroke=INK, sw=1.6)     # 3 local technique
    rectm(15, 4, 18.5, 7.5, WALL, stroke=INK, sw=1.6)      # 4 infirmerie
    # --- Bureau / gardien (5) ---
    rectm(0.4, 0.4, 1.8, 3.2, WALL, stroke=INK, sw=1.6)

    # --- Effluents ---
    rectm(15, 1.6, 18.5, 3.5, EARTH, stroke=INK, sw=1.4)   # 17 fumière
    rectm(15, 0.4, 18.5, 1.4, "#a58a6b", stroke=INK, sw=1.2, dash="4 3")  # 18 compostage

    # --- Château d'eau (11) + panneau solaire (12) ---
    rectm(0.4, 16.6, 1.9, 18.4, "#cfe0ea", stroke=WATER, sw=1.8)
    line([(0.4, 16.6), (1.9, 18.4)], WATER, sw=1.0)
    line([(1.9, 16.6), (0.4, 18.4)], WATER, sw=1.0)
    # panneau solaire (rectangle « incliné » hachuré)
    rectm(0.4, 14.7, 1.9, 16.1, "#2b3d52", stroke=INK, sw=1.2)
    for k in range(1, 4):
        line([(0.4 + k * 0.375, 14.7), (0.4 + k * 0.375, 16.1)], "#6d86a6", sw=0.8)

    # --- Silo / trémie d'aliments (10) ---
    circ(14.5, 15.6, 0.55 * SCALE, "#d9c7a6", stroke=INK, sw=1.4)
    circ(14.5, 15.6, 0.30 * SCALE, "#c8b184", stroke="none", sw=0)

    # --- Manipulation : couloir de contention (7) + quai d'embarquement (8) ---
    rectm(12.2, 2.0, 13.1, 3.6, WALL, stroke=INK, sw=1.4)          # parc de tri
    line([(12.2, 2.0), (12.2, 0.5), (13.1, 0.5), (13.1, 2.0)], INK, sw=1.4)  # race en U
    rectm(13.3, 0.5, 14.9, 2.0, "#e5d3b0", stroke=INK, sw=1.6)     # quai d'embarquement
    for k in range(1, 4):                                          # rampe (marches)
        line([(13.3, 0.5 + k * 0.375), (14.9, 0.5 + k * 0.375)], INK_SOFT, sw=0.7)

    # --- Abreuvoirs (9) ---
    for (ax, ay) in [(4.0, 5.5), (9.0, 4.0), (7.0, 9.0)]:
        circ(ax, ay, 0.42 * SCALE, "#bfe0f2", stroke=WATER, sw=1.4)
    circ(3.0, 16.0, 0.35 * SCALE, "#bfe0f2", stroke=WATER, sw=1.2)   # abreuvoir bergerie

    # --- Éclairage (15) : poteaux ---
    for (lx, ly) in [(1.6, 3.6), (13.4, 2.7), (19.2, 10.5), (16.7, 18.0)]:
        light_pole(lx, ly)

    # --- Puisard / assainissement (16) ---
    circ(19.2, 0.9, 0.45 * SCALE, "#cdbfa6", stroke=DRAIN, sw=1.6)
    line([(19.2 - 0.3, 0.9), (19.2 + 0.3, 0.9)], DRAIN, sw=1.0)
    line([(19.2, 0.9 - 0.3), (19.2, 0.9 + 0.3)], DRAIN, sw=1.0)

    # =====================================================================
    #  RÉSEAUX (tracés)
    # =====================================================================
    # Eau (13) — bleu tireté
    line([(1.15, 16.6), (1.15, 5.5), (4.0, 5.5)], WATER, sw=2.4, dash="9 5")
    line([(1.15, 8.0), (9.0, 4.0)], WATER, sw=2.4, dash="9 5")
    line([(1.15, 8.0), (7.0, 9.0)], WATER, sw=2.4, dash="9 5")
    line([(1.15, 16.2), (3.0, 16.0)], WATER, sw=2.4, dash="9 5")

    # Électricité (14) — ambre point-tiret, depuis le coffret (bureau)
    line([(1.8, 2.6), (13.4, 2.6), (13.4, 2.7)], ELEC, sw=2.2, dash="10 4 2 4")
    line([(1.6, 2.6), (1.6, 3.6)], ELEC, sw=2.2, dash="10 4 2 4")
    line([(1.8, 2.6), (0.9, 2.6), (0.9, 15.4)], ELEC, sw=2.2, dash="10 4 2 4")
    line([(15.0, 6.0), (14.5, 6.0), (14.5, 2.6)], ELEC, sw=2.0, dash="10 4 2 4")
    line([(16.7, 13.0), (16.7, 18.0)], ELEC, sw=2.0, dash="10 4 2 4")

    # Assainissement (16) — brun pointillé
    line([(13.5, 12.5), (14.5, 12.5), (14.5, 2.0), (18.6, 1.4), (19.2, 0.9)],
         DRAIN, sw=2.2, dash="3 4")
    line([(18.5, 2.4), (19.2, 1.6), (19.2, 0.9)], DRAIN, sw=2.2, dash="3 4")

    # =====================================================================
    #  Clôtures & ouvertures
    # =====================================================================
    # Portail (19)
    line([(8, 0), (11, 0)], ROOF, sw=6)
    # Portillon piéton (20)
    line([(2.5, 0), (3.3, 0)], ROOF, sw=5)
    # ticks de clôture périmétrique (21) — petits traits vers l'intérieur
    n = 40
    for i in range(n + 1):
        t = i / n
        # bas & haut
        for yy in (0.0, PLOT):
            xx = t * PLOT
            sgn = 0.28 if yy == 0 else -0.28
            S.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="0.7"/>' % (X(xx), Y(yy), X(xx), Y(yy + sgn), GREEN_D))
        for xx in (0.0, PLOT):
            yy = t * PLOT
            sgn = 0.28 if xx == 0 else -0.28
            S.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="0.7"/>' % (X(xx), Y(yy), X(xx + sgn), Y(yy), GREEN_D))

    # Haie brise-vent / arbres (22)
    for (tx, ty) in [(0.9, 19.2), (10.0, 19.35), (19.1, 19.2), (19.1, 6.0)]:
        tree(tx, ty)

    # =====================================================================
    #  Étiquettes des grandes zones (dans le dessin)
    # =====================================================================
    def zlabel(xm, ym, name, area):
        textm(xm, ym + 0.15, name, 12.5, anchor="middle", weight="bold", fill=INK)
        textm(xm, ym - 0.35, area, 10, anchor="middle", fill=INK_SOFT, font=MONO)

    zlabel(8, 15.9, "BERGERIE", "12 × 6 m — 72 m²")
    zlabel(8, 6.6, "AIRE D'EXERCICE", "≈ 114 m²")
    textm(16.75, 15.75, "Hangar", 10.5, anchor="middle", fill=INK)
    textm(16.75, 15.35, "fourrage", 10.5, anchor="middle", fill=INK)
    textm(16.75, 10.25, "Local", 10.5, anchor="middle", fill=INK)
    textm(16.75, 9.85, "technique", 10.5, anchor="middle", fill=INK)
    textm(16.75, 5.75, "Infirmerie", 10.5, anchor="middle", fill=INK)
    textm(16.75, 2.5, "Fumière", 9.5, anchor="middle", fill="#fff")

    # =====================================================================
    #  Pastilles numérotées
    # =====================================================================
    badges = {
        1: (3.0, 17.8), 2: (18.0, 17.9), 3: (18.0, 11.9), 4: (18.0, 6.9),
        5: (1.1, 2.55), 6: (5.5, 9.6), 7: (12.65, 3.1), 8: (14.1, 1.25),
        9: (4.0, 5.5), 10: (14.5, 16.7), 11: (1.15, 17.5), 12: (1.15, 15.4),
        13: (1.15, 10.5), 14: (7.0, 2.6), 15: (13.4, 3.7), 16: (19.2, 0.9),
        17: (15.6, 3.1), 18: (15.6, 0.9), 19: (9.5, -0.55), 20: (2.9, -0.55),
        21: (-0.55, 13.5), 22: (10.0, 19.35), 23: (14.5, 7.5),
    }
    for num, (xm, ym) in badges.items():
        badge(xm, ym, num)

    # =====================================================================
    #  Échelle graphique + rose des vents (dans le dessin)
    # =====================================================================
    # rose des vents (haut-droit du dessin)
    nx, ny = X(PLOT) - 6, Y(PLOT) - 6
    S.append('<g>'
             '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2"/>'
             '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             '<text x="%.1f" y="%.1f" font-family="%s" font-size="15" fill="%s" '
             'text-anchor="middle" font-weight="bold">N</text></g>'
             % (nx, ny + 34, nx, ny, INK,
                nx, ny - 2, nx - 6, ny + 12, nx + 6, ny + 12, INK,
                nx, ny - 8, SANS, INK))

    # échelle graphique (bas du dessin)
    bx, by = X(0), DYB + 46
    seg = 5 * SCALE     # 5 m
    for i in range(4):
        fill = INK if i % 2 == 0 else "#ffffff"
        S.append('<rect x="%.1f" y="%.1f" width="%.1f" height="8" fill="%s" '
                 'stroke="%s" stroke-width="0.8"/>'
                 % (bx + i * seg, by, seg, fill, INK))
    for i in range(5):
        text(bx + i * seg, by + 24, "%d" % (i * 5), 10.5, fill=INK_SOFT,
             font=MONO, anchor="middle")
    text(bx + 4 * seg + 14, by + 24, "m", 10.5, fill=INK_SOFT, font=MONO)
    text(bx, by - 6, "Échelle graphique (1 case = 5 m)", 10.5, fill=INK_SOFT)


# ===========================================================================
#  PANNEAU LATÉRAL : titre, légende, réseaux, cartouche
# ===========================================================================
LX = 895            # x gauche du panneau
LW = W - LX - 30    # largeur


def build_panel():
    # bandeau de titre (haut, pleine largeur du panneau)
    S.append('<rect x="%d" y="40" width="%d" height="70" rx="6" fill="%s"/>'
             % (LX, LW, GREEN_D))
    text(LX + 22, 76, "PLAN DE MASSE — FERME D'ÉLEVAGE OVIN", 20, fill="#ffffff",
         weight="bold")
    text(LX + 22, 98, "Toutes infrastructures · Tchoro — Korhogo (Côte d'Ivoire)",
         12.5, fill="#c8e6c9")

    y = 140
    text(LX, y, "LÉGENDE", 15, fill=GREEN_D, weight="bold", spacing="1.5")
    y += 8
    S.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>'
             % (LX, y, LX + 70, y, GREEN))
    y += 22

    groups = [
        ("A · BÂTIMENTS & ABRIS", [
            (1, "Bergerie", "6 cases + couloir de service (72 m²)"),
            (2, "Hangar à fourrage", "foin, paille, aliments"),
            (3, "Local technique", "matériel, pharmacie vétérinaire"),
            (4, "Infirmerie / quarantaine", "isolement des animaux malades / neufs"),
            (5, "Bureau / poste de gardien", "à l'entrée du site"),
        ]),
        ("B · ÉLEVAGE & MANIPULATION", [
            (6, "Aire d'exercice", "sol stabilisé, clôturée (≈ 114 m²)"),
            (7, "Couloir de contention + parc de tri", "soins, tri, embarquement"),
            (8, "Quai d'embarquement", "chargement des animaux"),
            (9, "Abreuvoirs (×4)", "eau propre en permanence"),
            (10, "Silo / trémie d'aliments", "stockage concentrés"),
        ]),
        ("C · RÉSEAUX & TECHNIQUE", [
            (11, "Château d'eau / réserve surélevée", "alimentation par gravité"),
            (12, "Panneau solaire + pompe", "pompage / énergie"),
            (13, "Réseau d'eau", "vers abreuvoirs et nettoyage"),
            (14, "Réseau électrique", "coffret, bâtiments, éclairage"),
            (15, "Éclairage extérieur (×4)", "sécurité nocturne"),
            (16, "Assainissement / puisard", "eaux de lavage, drainage"),
        ]),
        ("D · GESTION DES EFFLUENTS", [
            (17, "Fumière", "fosse maçonnée étanche"),
            (18, "Aire de compostage", "valorisation du fumier"),
        ]),
        ("E · AMÉNAGEMENTS EXTÉRIEURS", [
            (19, "Portail (3,00 m)", "accès véhicules / bétail"),
            (20, "Portillon piéton", "accès du personnel"),
            (21, "Clôture périmétrique", "grillage sur muret"),
            (22, "Haie brise-vent / arbres d'ombrage", "confort thermique"),
            (23, "Allées de circulation", "liaisons entre zones"),
        ]),
    ]

    col2_x = LX + 360
    # colonne 1 : A, B, C ; colonne 2 : D, E + sous-légende réseaux
    def draw_group(gx, gy, title, items):
        text(gx, gy, title, 11.5, fill=INK, weight="bold", spacing="0.6")
        gy += 20
        for num, name, note in items:
            S.append('<circle cx="%.1f" cy="%.1f" r="9.5" fill="%s"/>'
                     % (gx + 9, gy - 4, BADGE))
            S.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11.5" '
                     'fill="#fff" text-anchor="middle" font-weight="bold">%d</text>'
                     % (gx + 9, gy - 0.2, MONO, num))
            text(gx + 26, gy - 6, name, 11.5, fill=INK, weight="bold")
            text(gx + 26, gy + 7, note, 9.8, fill=INK_SOFT)
            gy += 27
        return gy + 10

    y1 = y
    for title, items in groups[:3]:
        y1 = draw_group(LX, y1, title, items)

    y2 = y
    for title, items in groups[3:]:
        y2 = draw_group(col2_x, y2, title, items)

    # ---- Sous-légende : types de réseaux (colonne 2) ----
    y2 += 4
    text(col2_x, y2, "RÉSEAUX (tracés)", 11.5, fill=INK, weight="bold", spacing="0.6")
    y2 += 18
    nets = [
        (WATER, "9 5", "Réseau d'eau"),
        (ELEC, "10 4 2 4", "Réseau électrique"),
        (DRAIN, "3 4", "Assainissement / drainage"),
    ]
    for col, dash, lab in nets:
        S.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="2.6" stroke-dasharray="%s"/>'
                 % (col2_x, y2 - 4, col2_x + 44, y2 - 4, col, dash))
        text(col2_x + 54, y2, lab, 10.8, fill=INK)
        y2 += 22
    # trame matériaux
    y2 += 6
    text(col2_x, y2, "TRAMES", 11.5, fill=INK, weight="bold", spacing="0.6")
    y2 += 16
    mats = [(WALL, INK, "Bâti (murs)"), (SAND, GREEN_D, "Sol stabilisé / aire"),
            (GRASS, GREEN_D, "Terrain / abords"), (EARTH, INK, "Effluents"),
            (PATH, "#c8c0ad", "Allées")]
    for fill, stroke, lab in mats:
        S.append('<rect x="%.1f" y="%.1f" width="26" height="14" fill="%s" '
                 'stroke="%s" stroke-width="1"/>' % (col2_x, y2 - 12, fill, stroke))
        text(col2_x + 34, y2, lab, 10.8, fill=INK)
        y2 += 20

    # ---- Principes d'implantation (colonne 1) ----
    y1 += 6
    text(LX, y1, "PRINCIPES D'IMPLANTATION", 11.5, fill=INK, weight="bold", spacing="0.6")
    y1 += 20
    principes = [
        "Bergerie ventilée : air traversant (climat chaud).",
        "Quarantaine / infirmerie à l'écart du troupeau sain.",
        "Fumière & compost sous le vent, loin de l'eau.",
        "Réserve d'eau surélevée → distribution gravitaire.",
        "Quai d'embarquement accessible depuis le portail.",
    ]
    for p in principes:
        S.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (LX + 4, y1 - 4, GREEN))
        text(LX + 14, y1, p, 10.5, fill=INK)
        y1 += 19

    # ---- Surfaces indicatives (colonne 2) ----
    y2 += 8
    text(col2_x, y2, "SURFACES INDICATIVES", 11.5, fill=INK, weight="bold", spacing="0.6")
    y2 += 19
    surf = [
        ("Bergerie", "72 m²"),
        ("Aire d'exercice", "114 m²"),
        ("Bâtiments de service", "47 m²"),
        ("Bureau, manip., effluents", "14 m²"),
    ]
    for name, val in surf:
        text(col2_x, y2, name, 10.5, fill=INK)
        text(col2_x + 285, y2, val, 10.5, fill=INK, font=MONO, anchor="end")
        y2 += 18
    S.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="0.9"/>'
             % (col2_x, y2 - 12, col2_x + 285, y2 - 12, INK_SOFT))
    text(col2_x, y2, "Emprise bâtie + aire", 10.5, fill=GREEN_D, weight="bold")
    text(col2_x + 285, y2, "≈ 247 / 400 m²", 10.5, fill=GREEN_D, font=MONO,
         anchor="end", weight="bold")

    # ---- Cartouche (bas du panneau) ----
    cy = 980
    S.append('<rect x="%d" y="%d" width="%d" height="150" rx="6" fill="#ffffff" '
             'stroke="%s" stroke-width="1.4"/>' % (LX, cy, LW, INK_SOFT))
    S.append('<rect x="%d" y="%d" width="%d" height="30" rx="6" fill="%s"/>'
             % (LX, cy, LW, GREEN_D))
    S.append('<rect x="%d" y="%d" width="%d" height="16" fill="%s"/>'
             % (LX, cy + 14, LW, GREEN_D))
    text(LX + 16, cy + 20, "CARTOUCHE", 12.5, fill="#fff", weight="bold", spacing="1")

    rows = [
        ("Projet", "Ferme d'élevage ovin (moutons Djallonké)"),
        ("Localisation", "Tchoro — Korhogo, Côte d'Ivoire"),
        ("Objet", "Plan de masse — toutes infrastructures"),
        ("Terrain / échelle", "400 m² (20 × 20 m) · échelle graphique"),
        ("Statut", "Vue d'artiste — non contractuel"),
        ("Porteur", "Williams"),
    ]
    ry = cy + 48
    for k, v in rows:
        text(LX + 16, ry, k, 10.5, fill=INK_SOFT, weight="bold")
        text(LX + 165, ry, v, 10.5, fill=INK)
        ry += 16.5

    # note d'avertissement (sous l'échelle, dans la colonne de dessin)
    text(DX, 1015, "Avant construction : faire coter et valider les plans par un "
         "professionnel du bâtiment sur place.", 10, fill=INK_SOFT, italic=True)


# ===========================================================================
def render():
    S.clear()
    S.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
             'width="%d" height="%d" font-family="%s">' % (W, H, W, H, SANS))
    S.append('<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (W, H, PAPER))
    # filet de cadre de la planche
    S.append('<rect x="16" y="16" width="%d" height="%d" fill="none" stroke="%s" '
             'stroke-width="1.2"/>' % (W - 32, H - 32, INK_SOFT))
    build_drawing()
    build_panel()
    S.append('</svg>')
    return "\n".join(S)


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "plan_masse_detaille.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(render())
    print("OK →", os.path.relpath(path))


if __name__ == "__main__":
    main()
