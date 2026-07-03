#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fiche d'achat des moutons au marché — Ferme d'élevage ovin, Tchoro (Korhogo).

Produit un PDF de 2 pages :
    1. Critères de choix + points de contrôle sanitaire (aide-mémoire)
    2. Grille de saisie à remplir au marché (lot d'animaux + budget)

Lancer depuis la racine du projet :
    python3 python/make_fiche.py
    → output/fiche_achat_moutons.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

GREEN = HexColor("#2e7d32"); GREEN_D = HexColor("#1b5e20")
INK = HexColor("#263238"); GREY = HexColor("#607d8b")
ROOF_D = HexColor("#8c3128"); WHITE = HexColor("#ffffff")
LIGHT = HexColor("#f2f6ef"); AMBER = HexColor("#fff3e0")

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
PDF = os.path.join(OUT, "fiche_achat_moutons.pdf")
PW, PH = A4


def text(c, x, y, s, size=10, font=None, color=INK, center=False, right=False):
    c.setFont(font or FONT, size); c.setFillColor(color)
    (c.drawCentredString if center else c.drawRightString if right else c.drawString)(x, y, s)


def wrap(c, x, y, s, size, width, font=None, color=INK, lead=None):
    font = font or FONT; lead = lead or size * 1.35
    c.setFont(font, size); c.setFillColor(color)
    line = ""
    for w in s.split():
        t = (line + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width:
            line = t
        else:
            c.drawString(x, y, line); y -= lead; line = w
    if line:
        c.drawString(x, y, line); y -= lead
    return y


def header(c, page_no):
    c.setFillColor(GREEN_D); c.rect(0, PH - 26 * mm, PW, 26 * mm, fill=1, stroke=0)
    c.setFillColor(GREEN); c.rect(0, PH - 28 * mm, PW, 2 * mm, fill=1, stroke=0)
    text(c, 18 * mm, PH - 13 * mm, "FICHE D'ACHAT DES MOUTONS", 18, FONT_B, WHITE)
    text(c, 18 * mm, PH - 20 * mm, "Marché — Ferme d'élevage ovin, Tchoro (Korhogo)", 10, FONT, HexColor("#c8e6c9"))
    text(c, PW - 18 * mm, PH - 13 * mm, "Race conseillée : Djallonké", 9, FONT, HexColor("#a5d6a7"), right=True)
    text(c, PW - 18 * mm, 10 * mm, "%d / 2" % page_no, 8, FONT, GREY, right=True)
    text(c, 18 * mm, 10 * mm, "Document d'aide à la décision — les prix sont des ordres de grandeur.",
         7.5, FONT, GREY)


def checkbox(c, x, y, s, size=9.5):
    c.setStrokeColor(GREY); c.setLineWidth(0.8)
    c.rect(x, y - 0.5, 3.4 * mm, 3.4 * mm, fill=0, stroke=1)
    text(c, x + 5.5 * mm, y, s, size, FONT, INK)


# ---------------------------------------------------------------------------
# PAGE 1 — Critères & contrôles
# ---------------------------------------------------------------------------
def page_criteres(c):
    header(c, 1)
    y = PH - 38 * mm

    text(c, 18 * mm, y, "1. Bons critères de choix", 13, FONT_B, GREEN_D)
    y -= 8 * mm
    crit = [
        "Animal vif et alerte, qui se déplace sans boiter.",
        "Bon état corporel : ni trop maigre (côtes saillantes), ni trop gras.",
        "Dos droit, aplombs solides, pattes et onglons sains.",
        "Yeux clairs et brillants, sans écoulement ; muqueuses roses (pas pâles).",
        "Nez sec, respiration calme, pas de toux ni d'écoulement nasal.",
        "Toison/peau propre, sans plaques, gale ni parasites visibles.",
        "Dents et âge cohérents (jeunes adultes pour la reproduction).",
        "Femelles : mamelle souple et saine. Béliers : testicules symétriques, fermes.",
    ]
    for s in crit:
        checkbox(c, 20 * mm, y, s); y -= 6.6 * mm

    y -= 3 * mm
    text(c, 18 * mm, y, "2. Signes à éviter (ne pas acheter)", 13, FONT_B, ROOF_D)
    y -= 8 * mm
    bad = [
        "Diarrhée, arrière-train souillé, amaigrissement marqué.",
        "Boiterie, articulations gonflées, onglons pourris.",
        "Écoulement des yeux ou du nez, toux répétée, respiration difficile.",
        "Abcès, plaies, gale, chute de laine par plaques.",
        "Animal isolé, abattu, qui reste couché ou ne rumine pas.",
    ]
    for s in bad:
        c.setFillColor(ROOF_D); c.circle(21 * mm, y + 1.3, 1.3, fill=1, stroke=0)
        text(c, 24 * mm, y, s, 9.5, FONT, INK); y -= 6.6 * mm

    y -= 3 * mm
    text(c, 18 * mm, y, "3. À faire au marché", 13, FONT_B, GREEN_D)
    y -= 8 * mm
    todo = [
        "Observer l'animal debout ET en marche avant de négocier.",
        "Demander l'origine et l'âge ; se méfier des prix « trop bas ».",
        "Prévoir une quarantaine de 2 à 3 semaines à la ferme (case infirmerie).",
        "Négocier le transport et convenir d'un point de chargement.",
        "Noter chaque achat dans la grille (page 2) et garder les reçus.",
    ]
    for s in todo:
        checkbox(c, 20 * mm, y, s); y -= 6.6 * mm

    # encadré budget indicatif
    y -= 4 * mm
    box_h = 30 * mm
    c.setFillColor(AMBER); c.setStrokeColor(GREEN_D); c.setLineWidth(0.8)
    c.rect(18 * mm, y - box_h + 6 * mm, PW - 36 * mm, box_h, fill=1, stroke=1)
    yy = y + 1 * mm
    text(c, 22 * mm, yy, "Repères de prix indicatifs (FCFA) — à vérifier sur place",
         10, FONT_B, GREEN_D)
    yy -= 7 * mm
    text(c, 22 * mm, yy, "• Brebis (reproductrice) : 45 000 – 75 000", 9.5, FONT, INK)
    text(c, 110 * mm, yy, "• Bélier reproducteur : 70 000 – 120 000", 9.5, FONT, INK)
    yy -= 6 * mm
    text(c, 22 * mm, yy, "• Agneau / antenais : 25 000 – 45 000", 9.5, FONT, INK)
    text(c, 110 * mm, yy, "• Mouton d'embouche : 40 000 – 90 000", 9.5, FONT, INK)
    yy -= 6 * mm
    text(c, 22 * mm, yy, "Les prix montent fortement à l'approche de la Tabaski (fête).",
         9, FONT, GREY)

    c.showPage()


# ---------------------------------------------------------------------------
# PAGE 2 — Grille de saisie
# ---------------------------------------------------------------------------
def page_grille(c):
    header(c, 2)
    y = PH - 38 * mm

    # bloc infos
    text(c, 18 * mm, y, "Date : __________________", 10, FONT, INK)
    text(c, 90 * mm, y, "Marché / lieu : ____________________________", 10, FONT, INK)
    y -= 7 * mm
    text(c, 18 * mm, y, "Acheteur : ______________________", 10, FONT, INK)
    text(c, 110 * mm, y, "Téléphone : __________________", 10, FONT, INK)
    y -= 10 * mm

    text(c, 18 * mm, y, "Lot d'animaux achetés", 13, FONT_B, GREEN_D)
    y -= 7 * mm

    # tableau
    cols_x = [18, 30, 62, 84, 106, 132, 168]      # en mm
    cols_x = [v * mm for v in cols_x]
    right = PW - 18 * mm
    heads = ["N°", "Type / sexe", "Âge", "État", "Prix (FCFA)", "Vendeur / tel", "OK"]
    row_h = 8.2 * mm
    n_rows = 12

    # entête
    c.setFillColor(GREEN_D)
    c.rect(cols_x[0], y - 2 * mm, right - cols_x[0], 7 * mm, fill=1, stroke=0)
    for i, h in enumerate(heads):
        text(c, cols_x[i] + 1.5 * mm, y, h, 8.5, FONT_B, WHITE)
    y -= 7 * mm

    # lignes
    top = y + 5 * mm
    for r in range(n_rows):
        if r % 2 == 0:
            c.setFillColor(LIGHT)
            c.rect(cols_x[0], y - (row_h - 5 * mm), right - cols_x[0], row_h, fill=1, stroke=0)
        # numéro pré-rempli
        text(c, cols_x[0] + 1.5 * mm, y, str(r + 1), 9, FONT, GREY)
        # petite case OK
        c.setStrokeColor(GREY); c.setLineWidth(0.7)
        c.rect(cols_x[6] + 1.5 * mm, y - 0.5, 3.2 * mm, 3.2 * mm, fill=0, stroke=1)
        y -= row_h
    bottom = y + (row_h - 5 * mm)

    # grille : lignes verticales + horizontales
    c.setStrokeColor(GREY); c.setLineWidth(0.5)
    for x in cols_x + [right]:
        c.line(x, top, x, bottom)
    yy = top
    c.line(cols_x[0], top, right, top)
    for r in range(n_rows + 1):
        c.line(cols_x[0], yy, right, yy)
        yy -= row_h

    # totaux
    y = bottom - 12 * mm
    text(c, 18 * mm, y, "Nombre d'animaux : __________", 10, FONT_B, INK)
    text(c, 90 * mm, y, "Total dépensé (FCFA) : ______________________", 10, FONT_B, GREEN_D)
    y -= 8 * mm
    text(c, 18 * mm, y, "Transport (FCFA) : __________", 10, FONT, INK)
    text(c, 90 * mm, y, "Divers (FCFA) : __________________", 10, FONT, INK)
    y -= 8 * mm
    c.setStrokeColor(GREY); c.setLineWidth(0.7)
    c.line(18 * mm, y + 3 * mm, PW - 18 * mm, y + 3 * mm)
    text(c, 18 * mm, y - 3 * mm, "COÛT TOTAL DE L'OPÉRATION (FCFA) : ______________________",
         11, FONT_B, GREEN_D)

    # note quarantaine
    y -= 16 * mm
    c.setFillColor(AMBER); c.setStrokeColor(ROOF_D); c.setLineWidth(0.7)
    c.rect(18 * mm, y - 6 * mm, PW - 36 * mm, 16 * mm, fill=1, stroke=1)
    text(c, 22 * mm, y + 4 * mm, "Rappel sanitaire", 10, FONT_B, ROOF_D)
    wrap(c, 22 * mm, y - 1 * mm,
         "Mettre les nouveaux animaux en quarantaine 2 à 3 semaines (case infirmerie) : "
         "observer, vermifuger et traiter si besoin avant de les mêler au troupeau.",
         9, PW - 44 * mm)

    c.showPage()


def main():
    os.makedirs(OUT, exist_ok=True)
    c = canvas.Canvas(PDF, pagesize=A4)
    c.setTitle("Fiche d'achat des moutons — Ferme d'élevage ovin (Tchoro, Korhogo)")
    page_criteres(c)
    page_grille(c)
    c.save()
    print("OK →", os.path.relpath(PDF))


if __name__ == "__main__":
    main()
