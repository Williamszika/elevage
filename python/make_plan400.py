#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan de construction sur 400 m² — Ferme d'élevage ovin, Tchoro (Korhogo).

Produit un PDF de 3 pages :
    1. Plan de masse coté (implantation sur les 400 m²)
    2. Plan de la bergerie (coupe en plan, cases + circulation)
    3. Tableau des dimensions + métré indicatif

Lancer depuis la racine du projet :
    python3 python/make_plan400.py
    → output/plan_construction_ferme_400m2.pdf
"""

import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Polices ---------------------------------------------------------------
FONT, FONT_B = "Helvetica", "Helvetica-Bold"
_REG = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/DejaVuSans.ttf", "C:/Windows/Fonts/DejaVuSans.ttf"]
_BLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/DejaVuSans-Bold.ttf"]
for p in _REG:
    if os.path.exists(p):
        try:
            pdfmetrics.registerFont(TTFont("DejaVuSans", p)); FONT = "DejaVuSans"
        except Exception:
            pass
        break
for p in _BLD:
    if os.path.exists(p):
        try:
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", p)); FONT_B = "DejaVuSans-Bold"
        except Exception:
            pass
        break

# --- Palette ---------------------------------------------------------------
GREEN = HexColor("#2e7d32"); GREEN_D = HexColor("#1b5e20")
INK = HexColor("#263238"); GREY = HexColor("#607d8b")
SAND = HexColor("#efe6d5"); WALL = HexColor("#f3ede1")
GRASS = HexColor("#cfe3b8"); EARTH = HexColor("#8d6e63")
ROOF_D = HexColor("#8c3128"); SKY = HexColor("#dfeaf2")
WHITE = HexColor("#ffffff")

# --- IMPLANTATION (mêmes coordonnées que make_arch.py / maquette 3D) -------
PLOT_W, PLOT_H = 20.0, 20.0
ZONES = {
    "bergerie":   (2.0, 12.5, 14.0, 18.5),
    "aire":       (2.0,  2.0, 14.0, 11.5),
    "fourrage":   (15.0, 13.0, 18.5, 18.5),
    "technique":  (15.0,  8.0, 18.5, 12.5),
    "infirmerie": (15.0,  4.0, 18.5,  7.5),
    "fumiere":    (15.0,  1.5, 18.5,  3.5),
}
LABELS = {
    "bergerie": "Bergerie (12 × 6 m)", "aire": "Aire d'exercice",
    "fourrage": "Hangar fourrage", "technique": "Local technique",
    "infirmerie": "Infirmerie / quarantaine", "fumiere": "Fumière",
}

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
PDF = os.path.join(OUT, "plan_construction_ferme_400m2.pdf")
PW, PH = landscape(A4)   # on travaille en paysage


def text(c, x, y, s, size=10, font=None, color=INK, center=False, right=False):
    c.setFont(font or FONT, size); c.setFillColor(color)
    (c.drawCentredString if center else c.drawRightString if right else c.drawString)(x, y, s)


def dim_h(c, x0, x1, y, label, color=GREY):
    """Ligne de cote horizontale."""
    c.setStrokeColor(color); c.setLineWidth(0.6)
    c.line(x0, y, x1, y)
    c.line(x0, y - 3, x0, y + 3); c.line(x1, y - 3, x1, y + 3)
    text(c, (x0 + x1) / 2, y + 3, label, 7.5, FONT, color, center=True)


def dim_v(c, y0, y1, x, label, color=GREY):
    c.setStrokeColor(color); c.setLineWidth(0.6)
    c.line(x, y0, x, y1)
    c.line(x - 3, y0, x + 3, y0); c.line(x - 3, y1, x + 3, y1)
    c.saveState(); c.translate(x - 4, (y0 + y1) / 2); c.rotate(90)
    text(c, 0, 0, label, 7.5, FONT, color, center=True); c.restoreState()


def header(c, title, sub, page_no):
    c.setFillColor(GREEN_D); c.rect(0, PH - 16 * mm, PW, 16 * mm, fill=1, stroke=0)
    text(c, 16 * mm, PH - 11 * mm, title, 15, FONT_B, WHITE)
    text(c, PW - 16 * mm, PH - 11 * mm,
         "Ferme ovine — Tchoro (Korhogo)", 9, FONT, HexColor("#c8e6c9"), right=True)
    text(c, 16 * mm, PH - 15.2 * mm, sub, 8, FONT, HexColor("#a5d6a7"))
    text(c, PW - 16 * mm, 8 * mm, "%d / 3" % page_no, 8, FONT, GREY, right=True)
    text(c, 16 * mm, 8 * mm, "Plan « vue d'artiste », non contractuel — à faire coter sur place.",
         7.5, FONT, GREY)


# ---------------------------------------------------------------------------
# PAGE 1 — Plan de masse coté
# ---------------------------------------------------------------------------
def page_masse(c):
    header(c, "Plan de masse — 400 m²", "Implantation cotée sur le terrain de 20 × 20 m", 1)

    scale = 7.6 * mm      # 1 m = 7,6 mm → 20 m = 152 mm (tient dans la hauteur A4 paysage)
    ox = (PW - PLOT_W * scale) / 2 + 6 * mm
    oy = 32 * mm

    def X(m): return ox + m * scale
    def Y(m): return oy + m * scale

    c.setFillColor(GRASS); c.setStrokeColor(GREEN_D); c.setLineWidth(1.6)
    c.rect(X(0), Y(0), PLOT_W * scale, PLOT_H * scale, fill=1, stroke=1)

    fills = {"bergerie": WALL, "aire": SAND, "fourrage": WALL,
             "technique": WALL, "infirmerie": WALL, "fumiere": EARTH}
    for key, (x0, y0, x1, y1) in ZONES.items():
        c.setFillColor(fills[key])
        c.setStrokeColor(GREEN_D if key == "aire" else INK)
        c.setLineWidth(1.0)
        if key == "aire":
            c.setDash(3, 3)
        c.rect(X(x0), Y(y0), (x1 - x0) * scale, (y1 - y0) * scale, fill=1, stroke=1)
        c.setDash()
        cx, cy = X((x0 + x1) / 2), Y((y0 + y1) / 2)
        text(c, cx, cy + 2, LABELS[key], 7.5, FONT_B, INK, center=True)
        text(c, cx, cy - 7, "%.1f m²" % ((x1 - x0) * (y1 - y0)), 7, FONT, GREY, center=True)

    # portail
    c.setStrokeColor(ROOF_D); c.setLineWidth(3)
    c.line(X(8), Y(0), X(11), Y(0))
    text(c, X(9.5), Y(0) - 13, "Portail 3,00 m", 7.5, FONT_B, ROOF_D, center=True)

    # cotes principales
    dim_h(c, X(0), X(PLOT_W), Y(0) - 26, "20,00 m")
    dim_v(c, Y(0), Y(PLOT_H), X(0) - 18, "20,00 m")
    # cotes de la bergerie
    bx0, by0, bx1, by1 = ZONES["bergerie"]
    dim_h(c, X(bx0), X(bx1), Y(by1) + 8, "12,00 m")
    dim_v(c, Y(by0), Y(by1), X(bx1) + 10, "6,00 m")
    # implantation depuis les limites (reculs)
    dim_h(c, X(0), X(bx0), Y(by0 + 1), "2,00 m", color=ROOF_D)

    # boussole
    nx, ny = PW - 30 * mm, PH - 40 * mm
    c.setStrokeColor(INK); c.setLineWidth(1.2)
    c.line(nx, ny - 8, nx, ny + 12)
    c.line(nx, ny + 12, nx - 3, ny + 6); c.line(nx, ny + 12, nx + 3, ny + 6)
    text(c, nx, ny + 16, "N", 9, FONT_B, INK, center=True)
    c.showPage()


# ---------------------------------------------------------------------------
# PAGE 2 — Plan de la bergerie (12 × 6 m)
# ---------------------------------------------------------------------------
def page_bergerie(c):
    header(c, "Plan de la bergerie", "12,00 × 6,00 m — cases, couloir de service et abris", 2)

    # échelle : bergerie 12 x 6 m
    scale = 19.0 * mm
    bw, bh = 12.0, 6.0
    ox = (PW - bw * scale) / 2
    oy = 45 * mm

    def X(m): return ox + m * scale
    def Y(m): return oy + m * scale

    wall_t = 0.15   # épaisseur de mur (m) pour l'effet double trait

    # dalle
    c.setFillColor(WALL); c.setStrokeColor(INK); c.setLineWidth(1.8)
    c.rect(X(0), Y(0), bw * scale, bh * scale, fill=1, stroke=1)
    # trait intérieur (épaisseur de mur)
    c.setLineWidth(0.6); c.setStrokeColor(GREY)
    c.rect(X(wall_t), Y(wall_t), (bw - 2 * wall_t) * scale, (bh - 2 * wall_t) * scale,
           fill=0, stroke=1)

    # Couloir de service central (largeur 1,2 m) le long de y = 0..1.2
    corr = 1.2
    c.setFillColor(SAND)
    c.rect(X(0), Y(0), bw * scale, corr * scale, fill=1, stroke=0)
    text(c, X(bw / 2), Y(corr / 2) - 3, "Couloir de service (1,20 m)", 8, FONT_B, EARTH, center=True)

    # Cases (au-dessus du couloir) : 6 cases de 2,0 m de large × 4,8 m de profond
    ncase = 6
    cw = bw / ncase
    for i in range(ncase):
        x0 = i * cw
        c.setStrokeColor(INK); c.setLineWidth(1.0)
        c.rect(X(x0), Y(corr), cw * scale, (bh - corr) * scale, fill=0, stroke=1)
        # porte de case (ouverture sur couloir)
        c.setStrokeColor(WHITE); c.setLineWidth(2.2)
        c.line(X(x0 + 0.4), Y(corr), X(x0 + cw - 0.4), Y(corr))
        c.setStrokeColor(GREEN); c.setLineWidth(0.7)
        # arc de débattement de la porte
        c.arc(X(x0 + 0.4), Y(corr), X(x0 + 0.4 + 1.0), Y(corr) + 1.0 * scale, 0, 90)
        label = "Case %d" % (i + 1)
        if i == 0:
            label = "Agnelage"
        if i == ncase - 1:
            label = "Béliers"
        text(c, X(x0 + cw / 2), Y(corr + (bh - corr) / 2), label, 8, FONT_B, INK, center=True)
        text(c, X(x0 + cw / 2), Y(corr + (bh - corr) / 2) - 9,
             "≈ %.1f m²" % (cw * (bh - corr)), 7, FONT, GREY, center=True)

    # portes extérieures : une à chaque pignon + ouverture vers l'aire (mur bas)
    c.setStrokeColor(WHITE); c.setLineWidth(3)
    c.line(X(0), Y(0.2), X(0), Y(1.0))          # entrée gauche couloir
    c.line(X(bw), Y(0.2), X(bw), Y(1.0))        # entrée droite couloir
    text(c, X(0) - 4, Y(0.6), "Accès", 7, FONT, EARTH, right=True)

    # mangeoires le long du couloir (bande hachurée)
    c.setStrokeColor(EARTH); c.setLineWidth(0.5)
    for i in range(ncase):
        x0 = i * cw + 0.15
        c.rect(X(x0), Y(corr), (cw - 0.3) * scale, 0.35 * scale, fill=0, stroke=1)

    # cotes
    dim_h(c, X(0), X(bw), Y(0) - 16, "12,00 m")
    dim_v(c, Y(0), Y(bh), X(0) - 14, "6,00 m")
    dim_h(c, X(0), X(cw), Y(bh) + 8, "%.2f m" % cw)
    dim_v(c, Y(corr), Y(bh), X(bw) + 12, "%.2f m" % (bh - corr))
    dim_v(c, Y(0), Y(corr), X(bw) + 12, "1,20 m")

    # légende
    lx, ly = 20 * mm, 30 * mm
    text(c, lx, ly, "Légende :", 9, FONT_B, INK)
    text(c, lx, ly - 6 * mm,
         "• Cases 1 à 6 : logements ovins  • Case 1 : agnelage  • Case 6 : béliers",
         8.5, FONT, INK)
    text(c, lx, ly - 11 * mm,
         "• Bande le long du couloir = mangeoires / râteliers  • Arcs verts = débattement des portillons",
         8.5, FONT, INK)
    c.showPage()


# ---------------------------------------------------------------------------
# PAGE 3 — Tableau dimensions + métré indicatif
# ---------------------------------------------------------------------------
def page_metre(c):
    header(c, "Dimensions & métré indicatif", "Ordres de grandeur — à confirmer par un professionnel", 3)

    # Tableau 1 : dimensions par zone
    y = PH - 30 * mm
    text(c, 16 * mm, y, "Dimensions par zone", 12, FONT_B, GREEN_D)
    y -= 8 * mm
    cols = [18 * mm, 90 * mm, 140 * mm, 185 * mm]
    c.setFillColor(GREEN_D); c.rect(16 * mm, y - 2 * mm, PW - 32 * mm, 7 * mm, fill=1, stroke=0)
    for cx, h in zip(cols, ["Zone", "Dimensions", "Surface", "Observation"]):
        text(c, cx, y, h, 9, FONT_B, WHITE)
    y -= 9 * mm
    total = 0.0
    obs = {"bergerie": "6 cases + couloir", "aire": "sol stabilisé, clôturée",
           "fourrage": "hangar ouvert", "technique": "matériel, pharmacie",
           "infirmerie": "isolement sanitaire", "fumiere": "fosse étanche"}
    for i, key in enumerate(["bergerie", "aire", "fourrage", "technique", "infirmerie", "fumiere"]):
        x0, y0, x1, y1 = ZONES[key]
        a = (x1 - x0) * (y1 - y0); total += a
        if i % 2 == 0:
            c.setFillColor(HexColor("#f2f6ef"))
            c.rect(16 * mm, y - 2 * mm, PW - 32 * mm, 7 * mm, fill=1, stroke=0)
        text(c, cols[0], y, LABELS[key].split(" (")[0], 9, FONT, INK)
        text(c, cols[1], y, "%.1f × %.1f m" % (x1 - x0, y1 - y0), 9, FONT, INK)
        text(c, cols[2], y, "%.1f m²" % a, 9, FONT, INK)
        text(c, cols[3], y, obs[key], 9, FONT, GREY)
        y -= 7 * mm
    c.setStrokeColor(GREY); c.setLineWidth(0.7)
    c.line(16 * mm, y + 4 * mm, PW - 16 * mm, y + 4 * mm)
    text(c, cols[0], y, "TOTAL bâti + aire", 9, FONT_B, INK)
    text(c, cols[2], y, "%.1f m²" % total, 9, FONT_B, GREEN_D)
    text(c, cols[3], y, "terrain : 400 m²", 9, FONT, GREY)

    # Tableau 2 : métré indicatif (gros œuvre)
    y -= 16 * mm
    text(c, 16 * mm, y, "Métré indicatif — gros œuvre bergerie", 12, FONT_B, GREEN_D)
    y -= 8 * mm
    c.setFillColor(GREEN_D); c.rect(16 * mm, y - 2 * mm, PW - 32 * mm, 7 * mm, fill=1, stroke=0)
    for cx, h in zip([18 * mm, 120 * mm, 175 * mm], ["Poste", "Quantité indicative", "Unité"]):
        text(c, cx, y, h, 9, FONT_B, WHITE)
    y -= 9 * mm
    metre = [
        ("Dalle béton bergerie (12 × 6 m)", "72", "m²"),
        ("Murs parpaings 15 cm (périmètre ~36 m × 2,6 m)", "94", "m²"),
        ("Muret + clôture aire d'exercice", "~43", "ml"),
        ("Toiture bac acier (avec débords)", "~85", "m²"),
        ("Portes / portillons de cases", "8", "u"),
        ("Mangeoires / râteliers", "6", "u"),
        ("Fumière maçonnée étanche", "7", "m²"),
    ]
    for i, (poste, q, u) in enumerate(metre):
        if i % 2 == 0:
            c.setFillColor(HexColor("#f2f6ef"))
            c.rect(16 * mm, y - 2 * mm, PW - 32 * mm, 7 * mm, fill=1, stroke=0)
        text(c, 18 * mm, y, poste, 9, FONT, INK)
        text(c, 120 * mm, y, q, 9, FONT, INK)
        text(c, 175 * mm, y, u, 9, FONT, GREY)
        y -= 7 * mm

    text(c, 16 * mm, y - 4 * mm,
         "Les quantités sont des ordres de grandeur destinés au chiffrage. "
         "Faire établir un métré détaillé et un devis par un maçon local.",
         8.5, FONT, GREY)
    c.showPage()


def main():
    os.makedirs(OUT, exist_ok=True)
    c = canvas.Canvas(PDF, pagesize=landscape(A4))
    c.setTitle("Plan de construction 400 m² — Ferme d'élevage ovin (Tchoro, Korhogo)")
    page_masse(c)
    page_bergerie(c)
    page_metre(c)
    c.save()
    print("OK →", os.path.relpath(PDF))


if __name__ == "__main__":
    main()
