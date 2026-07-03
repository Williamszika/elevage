#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dossier architectural + VUE 3D — Ferme d'élevage ovin, Tchoro (Korhogo).

Produit un PDF de 4 pages :
    1. Page de couverture
    2. Plan de masse (vue de dessus, coté)
    3. Vue 3D (axonométrie « vue d'artiste »)
    4. Notes techniques + tableau des surfaces

Lancer depuis la racine du projet :
    python3 python/make_arch.py
    → output/dossier_architectural_ferme.pdf

Autonome : n'a besoin que de reportlab (pip install -r requirements.txt).
"""

import os
from math import cos, sin, radians

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------------------------------------------------------------------------
# Polices : DejaVuSans si disponible (accents parfaits), sinon Helvetica.
# ---------------------------------------------------------------------------
FONT = "Helvetica"
FONT_B = "Helvetica-Bold"

_DEJAVU_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/DejaVuSans.ttf",
    "C:/Windows/Fonts/DejaVuSans.ttf",
]
_DEJAVU_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
]


def _setup_fonts():
    global FONT, FONT_B
    reg = next((p for p in _DEJAVU_CANDIDATES if os.path.exists(p)), None)
    bold = next((p for p in _DEJAVU_BOLD if os.path.exists(p)), None)
    if reg:
        try:
            pdfmetrics.registerFont(TTFont("DejaVuSans", reg))
            FONT = "DejaVuSans"
            if bold:
                pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold))
                FONT_B = "DejaVuSans-Bold"
            else:
                FONT_B = "DejaVuSans"
        except Exception:
            pass


_setup_fonts()

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
GREEN = HexColor("#2e7d32")
GREEN_D = HexColor("#1b5e20")
EARTH = HexColor("#8d6e63")
SAND = HexColor("#efe6d5")
SKY = HexColor("#dfeaf2")
INK = HexColor("#263238")
GREY = HexColor("#607d8b")
ROOF = HexColor("#b0463c")
ROOF_D = HexColor("#8c3128")
WALL = HexColor("#f3ede1")
WALL_S = HexColor("#d8cdb8")
GRASS = HexColor("#cfe3b8")

# ---------------------------------------------------------------------------
# IMPLANTATION DE LA FERME — coordonnées en mètres (origine en bas-gauche).
# Ces mêmes coordonnées sont reprises dans make_plan400.py et dans la
# maquette 3D (web/maquette_3d_ferme.html).
# ---------------------------------------------------------------------------
PLOT_W, PLOT_H = 20.0, 20.0        # terrain 20 x 20 = 400 m²

# zone : (x0, y0, x1, y1) en mètres
ZONES = {
    "bergerie":   (2.0, 12.5, 14.0, 18.5),   # bâtiment couvert   12 x 6   = 72,0 m²
    "aire":       (2.0,  2.0, 14.0, 11.5),    # aire d'exercice    12 x 9,5 = 114,0 m²
    "fourrage":   (15.0, 13.0, 18.5, 18.5),   # hangar à fourrage  3,5 x 5,5 = 19,3 m²
    "technique":  (15.0,  8.0, 18.5, 12.5),   # local technique    3,5 x 4,5 = 15,8 m²
    "infirmerie": (15.0,  4.0, 18.5,  7.5),   # infirmerie/quaran. 3,5 x 3,5 = 12,3 m²
    "fumiere":    (15.0,  1.5, 18.5,  3.5),   # fumière            3,5 x 2,0 = 7,0 m²
}

# Hauteurs (m) pour la vue 3D : (bas_mur, haut_mur, faîtage)
HEIGHTS = {
    "bergerie":   (0.0, 2.6, 4.1),
    "fourrage":   (0.0, 3.0, 3.0),
    "technique":  (0.0, 2.6, 2.6),
    "infirmerie": (0.0, 2.6, 2.6),
    "fumiere":    (0.0, 0.9, 0.9),
}

LABELS = {
    "bergerie":   "Bergerie",
    "aire":       "Aire d'exercice",
    "fourrage":   "Hangar fourrage",
    "technique":  "Local technique",
    "infirmerie": "Infirmerie / quarantaine",
    "fumiere":    "Fumière",
}

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
PDF = os.path.join(OUT, "dossier_architectural_ferme.pdf")

PAGE_W, PAGE_H = A4


# ---------------------------------------------------------------------------
# Utilitaires de texte
# ---------------------------------------------------------------------------
def text(c, x, y, s, size=10, font=None, color=INK, center=False, right=False):
    c.setFont(font or FONT, size)
    c.setFillColor(color)
    if center:
        c.drawCentredString(x, y, s)
    elif right:
        c.drawRightString(x, y, s)
    else:
        c.drawString(x, y, s)


def wrap(c, x, y, s, size, width, font=None, color=INK, leading=None):
    """Retour à la ligne simple sur une largeur en points. Renvoie le y final."""
    font = font or FONT
    leading = leading or size * 1.35
    c.setFont(font, size)
    c.setFillColor(color)
    words = s.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if pdfmetrics.stringWidth(test, font, size) <= width:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


def footer(c, page_no):
    text(c, 18 * mm, 12 * mm,
         "Ferme d'élevage ovin — Tchoro (Korhogo)   ·   Dossier architectural (vue d'artiste, non contractuel)",
         7.5, FONT, GREY)
    text(c, PAGE_W - 18 * mm, 12 * mm, "%d / 4" % page_no, 8, FONT, GREY, right=True)


# ---------------------------------------------------------------------------
# PAGE 1 — Couverture
# ---------------------------------------------------------------------------
def page_cover(c):
    c.setFillColor(GREEN_D)
    c.rect(0, PAGE_H - 95 * mm, PAGE_W, 95 * mm, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.rect(0, PAGE_H - 95 * mm, PAGE_W, 8 * mm, fill=1, stroke=0)

    text(c, PAGE_W / 2, PAGE_H - 42 * mm, "DOSSIER ARCHITECTURAL",
         30, FONT_B, HexColor("#ffffff"), center=True)
    text(c, PAGE_W / 2, PAGE_H - 55 * mm, "Ferme d'élevage ovin",
         18, FONT, HexColor("#e8f5e9"), center=True)
    text(c, PAGE_W / 2, PAGE_H - 68 * mm, "Tchoro — Korhogo (Côte d'Ivoire)",
         13, FONT, HexColor("#c8e6c9"), center=True)
    text(c, PAGE_W / 2, PAGE_H - 82 * mm, "Vue de dessus · Vue 3D · Notes techniques",
         11, FONT, HexColor("#a5d6a7"), center=True)

    # Vignette 3D de couverture
    c.saveState()
    c.translate(PAGE_W / 2 - 5 * mm, 95 * mm)
    draw_farm_iso(c, scale=5.2 * mm, cover=True)
    c.restoreState()

    text(c, 20 * mm, 40 * mm, "Surface du terrain : 400 m² (20 m × 20 m)", 11, FONT_B, INK)
    text(c, 20 * mm, 33 * mm, "Capacité indicative : 40 à 60 têtes (moutons Djallonké)", 10, FONT, INK)
    text(c, 20 * mm, 26 * mm, "Porteur de projet : Williams", 10, FONT, GREY)

    footer(c, 1)
    c.showPage()


# ---------------------------------------------------------------------------
# PAGE 2 — Plan de masse (vue de dessus)
# ---------------------------------------------------------------------------
def page_siteplan(c):
    text(c, 20 * mm, PAGE_H - 24 * mm, "1. Plan de masse", 18, FONT_B, GREEN_D)
    text(c, 20 * mm, PAGE_H - 31 * mm,
         "Vue de dessus de l'implantation sur le terrain de 400 m². Cotes en mètres.",
         10, FONT, GREY)

    # cadre de dessin
    ox, oy = 30 * mm, 55 * mm
    scale = 8.0 * mm   # 1 m = 8 mm  → 20 m = 160 mm

    def X(m): return ox + m * scale
    def Y(m): return oy + m * scale

    # terrain
    c.setFillColor(GRASS)
    c.setStrokeColor(GREEN_D)
    c.setLineWidth(1.5)
    c.rect(X(0), Y(0), PLOT_W * scale, PLOT_H * scale, fill=1, stroke=1)

    # zones
    fills = {
        "bergerie": WALL, "aire": SAND, "fourrage": WALL,
        "technique": WALL, "infirmerie": WALL, "fumiere": EARTH,
    }
    for key, (x0, y0, x1, y1) in ZONES.items():
        c.setFillColor(fills[key])
        c.setStrokeColor(INK if key != "aire" else GREEN_D)
        c.setLineWidth(1.2 if key != "aire" else 0.9)
        if key == "aire":
            c.setDash(3, 3)
        c.rect(X(x0), Y(y0), (x1 - x0) * scale, (y1 - y0) * scale, fill=1, stroke=1)
        c.setDash()
        # étiquette au centre
        cx, cy = X((x0 + x1) / 2), Y((y0 + y1) / 2)
        area = (x1 - x0) * (y1 - y0)
        text(c, cx, cy + 2, LABELS[key], 7.5, FONT_B, INK, center=True)
        text(c, cx, cy - 7, "%.0f m²" % area, 7, FONT, GREY, center=True)

    # portail (entrée) en bas au centre
    gx0, gx1 = 8.0, 11.0
    c.setStrokeColor(ROOF_D)
    c.setLineWidth(2.5)
    c.line(X(gx0), Y(0), X(gx1), Y(0))
    text(c, X((gx0 + gx1) / 2), Y(0) - 12, "Portail / entrée", 7.5, FONT_B, ROOF_D, center=True)

    # abreuvoir dans l'aire
    ax, ay = 4.0, 5.5
    c.setFillColor(SKY)
    c.setStrokeColor(GREY)
    c.setLineWidth(1)
    c.circle(X(ax), Y(ay), 6, fill=1, stroke=1)
    text(c, X(ax), Y(ay) - 12, "Abreuvoir", 6.5, FONT, GREY, center=True)

    # cotes globales (largeur et hauteur)
    c.setStrokeColor(GREY)
    c.setLineWidth(0.7)
    # cote bas
    cy = Y(0) - 26
    c.line(X(0), cy, X(PLOT_W), cy)
    c.line(X(0), cy - 3, X(0), cy + 3)
    c.line(X(PLOT_W), cy - 3, X(PLOT_W), cy + 3)
    text(c, X(PLOT_W / 2), cy - 10, "20,00 m", 8, FONT, GREY, center=True)
    # cote gauche
    cxx = X(0) - 16
    c.line(cxx, Y(0), cxx, Y(PLOT_H))
    c.line(cxx - 3, Y(0), cxx + 3, Y(0))
    c.line(cxx - 3, Y(PLOT_H), cxx + 3, Y(PLOT_H))
    c.saveState()
    c.translate(cxx - 4, Y(PLOT_H / 2))
    c.rotate(90)
    text(c, 0, 0, "20,00 m", 8, FONT, GREY, center=True)
    c.restoreState()

    # boussole
    nx, ny = PAGE_W - 32 * mm, PAGE_H - 60 * mm
    c.setStrokeColor(INK)
    c.setLineWidth(1.2)
    c.line(nx, ny - 10, nx, ny + 12)
    c.line(nx, ny + 12, nx - 3, ny + 6)
    c.line(nx, ny + 12, nx + 3, ny + 6)
    text(c, nx, ny + 16, "N", 9, FONT_B, INK, center=True)

    footer(c, 2)
    c.showPage()


# ---------------------------------------------------------------------------
# Vue 3D (axonométrie)
# ---------------------------------------------------------------------------
def _iso(x, y, z):
    """Projection isométrique. Renvoie (ex, ey) en unités 'mètre-écran'."""
    ex = (x - y) * cos(radians(30))
    ey = (x + y) * sin(radians(30)) + z
    return ex, ey


def _poly(c, pts, fill, stroke=INK, lw=0.6):
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.drawPath(p, fill=1, stroke=1)


def _shade(col, f):
    return Color(col.red * f, col.green * f, col.blue * f)


def draw_farm_iso(c, scale, cover=False):
    """Dessine la ferme en 3D. L'origine (0,0) locale = coin du repère isométrique.
    À appeler dans un contexte translaté. `scale` = taille d'un mètre en points."""

    def P(x, y, z):
        ex, ey = _iso(x, y, z)
        return ex * scale, ey * scale

    # --- Sol (terrain) ---
    ground = [P(0, 0, 0), P(PLOT_W, 0, 0), P(PLOT_W, PLOT_H, 0), P(0, PLOT_H, 0)]
    _poly(c, ground, GRASS, stroke=GREEN_D, lw=1.0)

    # aire d'exercice (sable) posée au sol
    ax0, ay0, ax1, ay1 = ZONES["aire"]
    _poly(c, [P(ax0, ay0, 0.01), P(ax1, ay0, 0.01), P(ax1, ay1, 0.01), P(ax0, ay1, 0.01)],
          SAND, stroke=EARTH, lw=0.5)

    def box(x0, y0, x1, y1, zt, zb=0.0, wall=WALL):
        """Dessine un volume rectangulaire (murs) sans toit."""
        # face droite (x1), face avant (y0) : les plus visibles dans cette iso
        # avant (y = y0)
        _poly(c, [P(x0, y0, zb), P(x1, y0, zb), P(x1, y0, zt), P(x0, y0, zt)],
              _shade(wall, 0.82), lw=0.5)
        # côté droit (x = x1)
        _poly(c, [P(x1, y0, zb), P(x1, y1, zb), P(x1, y1, zt), P(x1, y0, zt)],
              _shade(wall, 0.68), lw=0.5)

    def flat_roof(x0, y0, x1, y1, zt, col=WALL_S):
        _poly(c, [P(x0, y0, zt), P(x1, y0, zt), P(x1, y1, zt), P(x0, y1, zt)],
              _shade(col, 0.95), lw=0.5)

    # Ordre de dessin : du fond (grand y / grand x) vers l'avant.
    # 1) Bergerie (au fond, avec toit à deux pentes)
    bx0, by0, bx1, by1 = ZONES["bergerie"]
    _, _, zr = HEIGHTS["bergerie"]
    ze = HEIGHTS["bergerie"][1]
    box(bx0, by0, bx1, by1, ze, wall=WALL)
    # pignons + toit à 2 pentes (faîtage au milieu en x)
    xm = (bx0 + bx1) / 2
    # pignon avant (y0)
    _poly(c, [P(bx0, by0, ze), P(xm, by0, zr), P(bx1, by0, ze)], _shade(WALL, 0.86), lw=0.5)
    # pan de toit avant-droit
    _poly(c, [P(xm, by0, zr), P(xm, by1, zr), P(bx1, by1, ze), P(bx1, by0, ze)],
          _shade(ROOF, 0.78), lw=0.5)
    # pan de toit avant-gauche
    _poly(c, [P(bx0, by0, ze), P(xm, by0, zr), P(xm, by1, zr), P(bx0, by1, ze)],
          _shade(ROOF, 0.95), lw=0.5)

    # 2) Bâtiments de service (colonne de droite), du fond vers l'avant
    for key in ("fourrage", "technique", "infirmerie", "fumiere"):
        x0, y0, x1, y1 = ZONES[key]
        zt = HEIGHTS[key][1]
        col = EARTH if key == "fumiere" else WALL
        box(x0, y0, x1, y1, zt, wall=col)
        flat_roof(x0, y0, x1, y1, zt, col=ROOF if key != "fumiere" else EARTH)

    # 3) clôture de l'aire d'exercice (poteaux + lisse)
    c.setStrokeColor(_shade(EARTH, 0.9))
    c.setLineWidth(0.8)
    fence_h = 1.1
    step = 2.0
    xs = [ax0 + i * step for i in range(int((ax1 - ax0) / step) + 1)]
    ys = [ay0 + i * step for i in range(int((ay1 - ay0) / step) + 1)]
    for x in xs:
        a = P(x, ay0, 0); b = P(x, ay0, fence_h)
        c.line(a[0], a[1], b[0], b[1])
    for y in ys:
        a = P(ax1, y, 0); b = P(ax1, y, fence_h)
        c.line(a[0], a[1], b[0], b[1])
    # lisse haute avant + droite
    a = P(ax0, ay0, fence_h); b = P(ax1, ay0, fence_h)
    c.line(a[0], a[1], b[0], b[1])
    a = P(ax1, ay0, fence_h); b = P(ax1, ay1, fence_h)
    c.line(a[0], a[1], b[0], b[1])

    if not cover:
        # quelques moutons (ellipses) dans l'aire
        c.setFillColor(HexColor("#fbfbf7"))
        c.setStrokeColor(GREY)
        c.setLineWidth(0.4)
        for (mx, my) in [(4, 4), (6, 5.5), (8, 3.5), (5.5, 8), (9.5, 7)]:
            px, py = P(mx, my, 0.35)
            c.saveState()
            c.translate(px, py)
            c.scale(1.0, 0.55)
            c.circle(0, 0, 0.45 * scale, fill=1, stroke=1)
            c.restoreState()


def page_view3d(c):
    text(c, 20 * mm, PAGE_H - 24 * mm, "2. Vue 3D — axonométrie", 18, FONT_B, GREEN_D)
    text(c, 20 * mm, PAGE_H - 31 * mm,
         "Représentation « vue d'artiste » de l'ensemble. Non contractuelle.",
         10, FONT, GREY)

    # ciel léger
    c.setFillColor(SKY)
    c.rect(15 * mm, 55 * mm, PAGE_W - 30 * mm, 175 * mm, fill=1, stroke=0)

    c.saveState()
    # centrer : l'iso s'étend en x de -PLOT_H..PLOT_W ; on translate au milieu bas
    c.translate(PAGE_W / 2, 78 * mm)
    draw_farm_iso(c, scale=6.4 * mm)
    c.restoreState()

    # légende
    lx, ly = 22 * mm, 48 * mm
    items = [
        (ROOF, "Toitures (tôle bac / fibrociment)"),
        (WALL, "Murs (parpaings enduits)"),
        (SAND, "Aire d'exercice (sol stabilisé)"),
        (GRASS, "Terrain / abords"),
    ]
    for i, (col, lab) in enumerate(items):
        x = lx + (i % 2) * 85 * mm
        y = ly - (i // 2) * 8 * mm
        c.setFillColor(col)
        c.setStrokeColor(INK)
        c.setLineWidth(0.5)
        c.rect(x, y, 6 * mm, 4 * mm, fill=1, stroke=1)
        text(c, x + 8 * mm, y + 0.5 * mm, lab, 8.5, FONT, INK)

    footer(c, 3)
    c.showPage()


# ---------------------------------------------------------------------------
# PAGE 4 — Notes techniques + tableau des surfaces
# ---------------------------------------------------------------------------
def page_notes(c):
    text(c, 20 * mm, PAGE_H - 24 * mm, "3. Notes techniques", 18, FONT_B, GREEN_D)

    y = PAGE_H - 40 * mm
    # ---- Tableau des surfaces ----
    text(c, 20 * mm, y, "Tableau des surfaces", 12, FONT_B, INK)
    y -= 8 * mm
    rows = []
    total = 0.0
    for key in ("bergerie", "aire", "fourrage", "technique", "infirmerie", "fumiere"):
        x0, y0, x1, y1 = ZONES[key]
        a = (x1 - x0) * (y1 - y0)
        total += a
        rows.append((LABELS[key], "%.1f × %.1f" % (x1 - x0, y1 - y0), "%.1f m²" % a))

    col_x = [22 * mm, 95 * mm, 150 * mm]
    c.setFillColor(GREEN_D)
    c.rect(20 * mm, y - 2 * mm, PAGE_W - 40 * mm, 7 * mm, fill=1, stroke=0)
    text(c, col_x[0], y, "Zone", 9.5, FONT_B, HexColor("#ffffff"))
    text(c, col_x[1], y, "Dimensions (m)", 9.5, FONT_B, HexColor("#ffffff"))
    text(c, col_x[2], y, "Surface", 9.5, FONT_B, HexColor("#ffffff"))
    y -= 9 * mm
    for i, (name, dim, area) in enumerate(rows):
        if i % 2 == 0:
            c.setFillColor(HexColor("#f2f6ef"))
            c.rect(20 * mm, y - 2 * mm, PAGE_W - 40 * mm, 7 * mm, fill=1, stroke=0)
        text(c, col_x[0], y, name, 9.5, FONT, INK)
        text(c, col_x[1], y, dim, 9.5, FONT, INK)
        text(c, col_x[2], y, area, 9.5, FONT, INK)
        y -= 7 * mm
    c.setStrokeColor(GREY)
    c.setLineWidth(0.7)
    c.line(20 * mm, y + 4 * mm, PAGE_W - 20 * mm, y + 4 * mm)
    text(c, col_x[0], y, "Emprise bâtie + aire", 9.5, FONT_B, INK)
    text(c, col_x[2], y, "%.1f m²" % total, 9.5, FONT_B, GREEN_D)
    text(c, col_x[1], y, "sur 400 m² de terrain", 9.5, FONT, GREY)

    # ---- Descriptif ----
    y -= 14 * mm
    text(c, 20 * mm, y, "Descriptif constructif", 12, FONT_B, INK)
    y -= 8 * mm
    notes = [
        "Fondations : semelles filantes en béton, chaînage bas. Sol de la bergerie "
        "en dalle béton légèrement pentée vers l'extérieur pour l'écoulement.",
        "Murs : parpaings de 15 cm, enduit ciment. Muret de 1,10 m côté aire "
        "d'exercice surmonté d'une clôture grillagée.",
        "Toiture : charpente métallique légère, couverture bac acier (ou fibrociment), "
        "pente ~25 %. Débord de toit pour l'ombre et la ventilation.",
        "Ventilation : ouvertures hautes grillagées sur les longs pans de la bergerie "
        "(climat chaud — privilégier l'air traversant).",
        "Eau : abreuvoir alimenté depuis une réserve ; point d'eau pour le nettoyage.",
        "Fumière : fosse maçonnée étanche, à l'écart du bâtiment d'élevage.",
    ]
    for n in notes:
        c.setFillColor(GREEN)
        c.circle(23 * mm, y + 1.5, 1.4, fill=1, stroke=0)
        y = wrap(c, 27 * mm, y, n, 9.5, PAGE_W - 47 * mm)
        y -= 2 * mm

    # ---- Avertissement ----
    y -= 2 * mm
    c.setFillColor(HexColor("#fff3e0"))
    c.setStrokeColor(ROOF_D)
    c.setLineWidth(0.7)
    box_h = 20 * mm
    c.rect(20 * mm, y - box_h + 6 * mm, PAGE_W - 40 * mm, box_h, fill=1, stroke=1)
    yy = y + 1 * mm
    text(c, 24 * mm, yy, "⚠ Représentation non contractuelle", 9.5, FONT_B, ROOF_D)
    wrap(c, 24 * mm, yy - 6 * mm,
         "Les vues 3D et les plans sont des représentations « vue d'artiste ». Avant "
         "construction, faites coter et valider les plans par un maçon ou un technicien "
         "du bâtiment sur place.",
         8.5, PAGE_W - 48 * mm, color=INK)

    footer(c, 4)
    c.showPage()


# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    c = canvas.Canvas(PDF, pagesize=A4)
    c.setTitle("Dossier architectural — Ferme d'élevage ovin (Tchoro, Korhogo)")
    page_cover(c)
    page_siteplan(c)
    page_view3d(c)
    page_notes(c)
    c.save()
    print("OK →", os.path.relpath(PDF))


if __name__ == "__main__":
    main()
