#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Régénère l'image du plan de masse utilisée par la présentation.

Produit deux fichiers dans assets/ :
    * site_plan.png  — image rasterisée (rendue directement avec Pillow)
    * site_plan.pdf  — version vectorielle (reportlab)

Lancer depuis la racine du projet :
    python3 python/draw_plan_png.py

Autonome : n'a besoin que de reportlab + Pillow (installés par requirements.txt).
Aucun outil externe (poppler/pdftoppm) n'est requis pour le PNG.
"""

import os
from PIL import Image, ImageDraw, ImageFont

from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Implantation (mêmes coordonnées que make_arch.py / make_plan400.py) ---
PLOT_W, PLOT_H = 20.0, 20.0
ZONES = {
    "bergerie":   (2.0, 12.5, 14.0, 18.5),
    "aire":       (2.0,  2.0, 14.0, 11.5),
    "fourrage":   (15.0, 13.0, 18.5, 18.5),
    "technique":  (15.0,  8.0, 18.5, 12.5),
    "infirmerie": (15.0,  4.0, 18.5,  7.5),
    "fumiere":    (15.0,  1.5, 18.5,  3.5),
}
LABELS = {"bergerie": "Bergerie", "aire": "Aire d'exercice", "fourrage": "Hangar fourrage",
          "technique": "Local technique", "infirmerie": "Infirmerie", "fumiere": "Fumière"}

# --- Couleurs (RGB pour PIL) ---
RGB = {
    "grass": (207, 227, 184), "green_d": (27, 94, 32), "ink": (38, 50, 56),
    "grey": (96, 125, 139), "sand": (239, 230, 213), "wall": (243, 237, 225),
    "earth": (141, 110, 99), "roof_d": (140, 49, 40), "sky": (158, 201, 224),
    "white": (255, 255, 255),
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
PNG = os.path.join(ASSETS, "site_plan.png")
PDF = os.path.join(ASSETS, "site_plan.pdf")

_DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(path_candidates, size):
    for p in path_candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


REG_CANDS = [_DEJAVU, "/Library/Fonts/DejaVuSans.ttf", "C:/Windows/Fonts/DejaVuSans.ttf"]
BLD_CANDS = [_DEJAVU_B, "/Library/Fonts/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/DejaVuSans-Bold.ttf"]


def _centered(draw, cx, cy, txt, font, fill):
    l, t, r, b = draw.textbbox((0, 0), txt, font=font)
    draw.text((cx - (r - l) / 2, cy - (b - t) / 2), txt, font=font, fill=fill)


def draw_png():
    """Rendu direct en PNG avec Pillow (aucun outil externe requis)."""
    os.makedirs(ASSETS, exist_ok=True)
    SIZE = 1500
    margin = 150
    scale = (SIZE - 2 * margin) / PLOT_W

    img = Image.new("RGB", (SIZE, SIZE), RGB["white"])
    d = ImageDraw.Draw(img)

    f_title = _font(BLD_CANDS, 44)
    f_sub = _font(REG_CANDS, 26)
    f_lab = _font(BLD_CANDS, 24)
    f_area = _font(REG_CANDS, 21)
    f_small = _font(REG_CANDS, 22)

    # y écran inversé : le repère terrain a l'origine en bas.
    def X(m): return margin + m * scale
    def Y(m): return SIZE - margin - m * scale

    def rect(x0, y0, x1, y1, fill, outline, width=2, dash=False):
        a, b = (X(x0), Y(y1)), (X(x1), Y(y0))   # (haut-gauche, bas-droite)
        d.rectangle([a, b], fill=fill, outline=None)
        if dash:
            _dashed_rect(d, a, b, outline, width)
        else:
            d.rectangle([a, b], outline=outline, width=width)

    def _dashed_rect(dr, a, b, col, w):
        (x0, y0), (x1, y1) = a, b
        step = 14
        for x in range(int(x0), int(x1), step * 2):
            dr.line([(x, y0), (min(x + step, x1), y0)], fill=col, width=w)
            dr.line([(x, y1), (min(x + step, x1), y1)], fill=col, width=w)
        for y in range(int(y0), int(y1), step * 2):
            dr.line([(x0, y), (x0, min(y + step, y1))], fill=col, width=w)
            dr.line([(x1, y), (x1, min(y + step, y1))], fill=col, width=w)

    # Titre
    _centered(d, SIZE / 2, 55, "Plan de masse — Ferme ovine (400 m²)", f_title, RGB["green_d"])
    _centered(d, SIZE / 2, 100, "Tchoro — Korhogo   ·   20 × 20 m", f_sub, RGB["grey"])

    # terrain
    rect(0, 0, PLOT_W, PLOT_H, RGB["grass"], RGB["green_d"], width=4)

    fills = {"bergerie": RGB["wall"], "aire": RGB["sand"], "fourrage": RGB["wall"],
             "technique": RGB["wall"], "infirmerie": RGB["wall"], "fumiere": RGB["earth"]}
    for key, (x0, y0, x1, y1) in ZONES.items():
        if key == "aire":
            rect(x0, y0, x1, y1, fills[key], RGB["green_d"], width=3, dash=True)
        else:
            rect(x0, y0, x1, y1, fills[key], RGB["ink"], width=2)
        cx, cy = X((x0 + x1) / 2), Y((y0 + y1) / 2)
        lab_col = RGB["white"] if key == "fumiere" else RGB["ink"]
        area_col = (230, 224, 214) if key == "fumiere" else RGB["grey"]
        _centered(d, cx, cy - 12, LABELS[key], f_lab, lab_col)
        _centered(d, cx, cy + 16, "%.0f m²" % ((x1 - x0) * (y1 - y0)), f_area, area_col)

    # portail
    d.line([(X(8), Y(0)), (X(11), Y(0))], fill=RGB["roof_d"], width=7)
    _centered(d, X(9.5), Y(0) + 22, "Portail", f_small, RGB["roof_d"])

    # abreuvoir
    r = 16
    d.ellipse([X(4) - r, Y(5.5) - r, X(4) + r, Y(5.5) + r], fill=RGB["sky"], outline=RGB["grey"], width=2)
    _centered(d, X(4), Y(5.5) + 30, "Abreuvoir", f_small, RGB["grey"])

    # cote bas
    yb = Y(0) + 60
    d.line([(X(0), yb), (X(PLOT_W), yb)], fill=RGB["grey"], width=2)
    d.line([(X(0), yb - 7), (X(0), yb + 7)], fill=RGB["grey"], width=2)
    d.line([(X(PLOT_W), yb - 7), (X(PLOT_W), yb + 7)], fill=RGB["grey"], width=2)
    _centered(d, X(PLOT_W / 2), yb + 22, "20,00 m", f_small, RGB["grey"])

    # boussole
    nx, ny = X(PLOT_W) + 55, Y(PLOT_H) + 20
    d.line([(nx, ny + 34), (nx, ny)], fill=RGB["ink"], width=3)
    d.line([(nx, ny), (nx - 8, ny + 14)], fill=RGB["ink"], width=3)
    d.line([(nx, ny), (nx + 8, ny + 14)], fill=RGB["ink"], width=3)
    _centered(d, nx, ny - 18, "N", f_lab, RGB["ink"])

    img.save(PNG)
    print("OK →", os.path.relpath(PNG))


def draw_pdf():
    """Version vectorielle (reportlab)."""
    os.makedirs(ASSETS, exist_ok=True)
    font, font_b = "Helvetica", "Helvetica-Bold"
    if os.path.exists(_DEJAVU):
        try:
            pdfmetrics.registerFont(TTFont("DejaVuSans", _DEJAVU)); font = "DejaVuSans"
            if os.path.exists(_DEJAVU_B):
                pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", _DEJAVU_B)); font_b = "DejaVuSans-Bold"
        except Exception:
            pass

    green_d = HexColor("#1b5e20"); ink = HexColor("#263238"); grey = HexColor("#607d8b")
    sand = HexColor("#efe6d5"); wall = HexColor("#f3ede1"); grass = HexColor("#cfe3b8")
    earth = HexColor("#8d6e63"); roof_d = HexColor("#8c3128"); sky = HexColor("#9ec9e0")

    side = 200 * mm
    c = canvas.Canvas(PDF, pagesize=(side, side))
    margin = 22 * mm
    scale = (side - 2 * margin) / PLOT_W
    ox = oy = margin

    def X(m): return ox + m * scale
    def Y(m): return oy + m * scale

    def txt(x, y, s, size, fnt, col, center=False):
        c.setFont(fnt, size); c.setFillColor(col)
        (c.drawCentredString if center else c.drawString)(x, y, s)

    txt(side / 2, side - 14 * mm, "Plan de masse — Ferme ovine (400 m²)", 15, font_b, green_d, True)
    txt(side / 2, side - 20 * mm, "Tchoro — Korhogo   ·   20 × 20 m", 9, font, grey, True)

    c.setFillColor(grass); c.setStrokeColor(green_d); c.setLineWidth(2)
    c.rect(X(0), Y(0), PLOT_W * scale, PLOT_H * scale, fill=1, stroke=1)

    fills = {"bergerie": wall, "aire": sand, "fourrage": wall,
             "technique": wall, "infirmerie": wall, "fumiere": earth}
    for key, (x0, y0, x1, y1) in ZONES.items():
        c.setFillColor(fills[key]); c.setStrokeColor(green_d if key == "aire" else ink)
        c.setLineWidth(1.2)
        if key == "aire":
            c.setDash(4, 4)
        c.rect(X(x0), Y(y0), (x1 - x0) * scale, (y1 - y0) * scale, fill=1, stroke=1)
        c.setDash()
        cx, cy = X((x0 + x1) / 2), Y((y0 + y1) / 2)
        txt(cx, cy + 2, LABELS[key], 8.5, font_b, ink, True)
        txt(cx, cy - 9, "%.0f m²" % ((x1 - x0) * (y1 - y0)), 7.5, font, grey, True)

    c.setStrokeColor(roof_d); c.setLineWidth(3.5)
    c.line(X(8), Y(0), X(11), Y(0))
    txt(X(9.5), Y(0) - 13, "Portail", 8, font_b, roof_d, True)
    c.setFillColor(sky); c.setStrokeColor(grey); c.setLineWidth(1)
    c.circle(X(4), Y(5.5), 7, fill=1, stroke=1)
    txt(X(4), Y(5.5) - 13, "Abreuvoir", 7, font, grey, True)

    c.setStrokeColor(grey); c.setLineWidth(0.7)
    cy = Y(0) - 28
    c.line(X(0), cy, X(PLOT_W), cy)
    txt(X(PLOT_W / 2), cy - 11, "20,00 m", 9, font, grey, True)

    nx, ny = X(PLOT_W) + 10, Y(PLOT_H) - 6
    c.setStrokeColor(ink); c.setLineWidth(1.4)
    c.line(nx, ny - 8, nx, ny + 12)
    c.line(nx, ny + 12, nx - 3, ny + 6); c.line(nx, ny + 12, nx + 3, ny + 6)
    txt(nx, ny + 16, "N", 10, font_b, ink, True)

    c.save()
    print("OK →", os.path.relpath(PDF))


if __name__ == "__main__":
    draw_png()
    draw_pdf()
