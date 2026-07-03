#!/usr/bin/env node
/*
 * Présentation partenaires (PowerPoint .pptx) — Ferme d'élevage ovin, Tchoro (Korhogo).
 *
 * Génère output/presentation_ferme_moutons.pptx (17 diapositives).
 *
 * Lancer depuis la racine du projet :
 *     npm install
 *     npm run build:deck      (ou : node node/build_deck.js)
 *
 * À PERSONNALISER avant de présenter : le nom du porteur, le téléphone et
 * l'email (constante CONTACT ci-dessous). Les montants sont des ordres de grandeur.
 */

"use strict";

const fs = require("fs");
const path = require("path");
const PptxGenJS = require("pptxgenjs");

// --------------------------------------------------------------------------
// À personnaliser
// --------------------------------------------------------------------------
const CONTACT = {
  porteur: "Williams",
  telephone: "+225 00 00 00 00",
  email: "contact@ferme-tchoro.ci",
  lieu: "Tchoro — Korhogo, Côte d'Ivoire",
};

// --------------------------------------------------------------------------
// Thème
// --------------------------------------------------------------------------
const C = {
  green: "2E7D32",
  greenD: "1B5E20",
  greenL: "E8F5E9",
  ink: "263238",
  grey: "607D8B",
  sand: "EFE6D5",
  earth: "8D6E63",
  roof: "B0463C",
  amber: "FFF3E0",
  white: "FFFFFF",
  paper: "F7FAF5",
};

const ROOT = path.dirname(__dirname);
const OUT_DIR = path.join(ROOT, "output");
const SITE_PLAN = path.join(ROOT, "assets", "site_plan.png");
const OUT = path.join(OUT_DIR, "presentation_ferme_moutons.pptx");

const pptx = new PptxGenJS();
pptx.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pptx.layout = "WIDE";
pptx.author = CONTACT.porteur;
pptx.company = "Ferme d'élevage ovin — Tchoro (Korhogo)";
pptx.subject = "Présentation partenaires";
pptx.title = "Ferme d'élevage ovin — Tchoro (Korhogo)";

const W = 13.333;
const H = 7.5;

// --------------------------------------------------------------------------
// Helpers
// --------------------------------------------------------------------------
let pageNo = 0;

function baseSlide(withFooter = true) {
  const s = pptx.addSlide();
  s.background = { color: C.paper };
  if (withFooter) {
    pageNo += 1;
    s.addShape(pptx.ShapeType.rect, {
      x: 0, y: H - 0.28, w: W, h: 0.28, fill: { color: C.greenD },
    });
    s.addText("Ferme d'élevage ovin — Tchoro (Korhogo)", {
      x: 0.4, y: H - 0.29, w: 8, h: 0.28, fontSize: 8, color: C.white,
      fontFace: "Arial", valign: "middle",
    });
    s.addText(`${pageNo}`, {
      x: W - 1.1, y: H - 0.29, w: 0.7, h: 0.28, fontSize: 8, color: C.white,
      align: "right", fontFace: "Arial", valign: "middle",
    });
  }
  return s;
}

function heading(s, title, kicker) {
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.28, h: 1.5, fill: { color: C.green } });
  if (kicker) {
    s.addText(kicker.toUpperCase(), {
      x: 0.6, y: 0.35, w: 11, h: 0.4, fontSize: 12, color: C.green,
      bold: true, charSpacing: 2, fontFace: "Arial",
    });
  }
  s.addText(title, {
    x: 0.6, y: kicker ? 0.72 : 0.5, w: 12, h: 0.8, fontSize: 30, bold: true,
    color: C.greenD, fontFace: "Arial",
  });
  s.addShape(pptx.ShapeType.line, {
    x: 0.62, y: 1.62, w: 2.2, h: 0, line: { color: C.green, width: 3 },
  });
}

// Liste à puces stylée
function bullets(s, items, opts = {}) {
  const x = opts.x ?? 0.7;
  const y = opts.y ?? 2.0;
  const w = opts.w ?? 7.4;
  const h = opts.h ?? 4.6;
  const fontSize = opts.fontSize ?? 16;
  const text = items.map((it) => {
    if (typeof it === "string") {
      return { text: it, options: { bullet: { code: "2022" }, color: C.ink, paraSpaceAfter: 10 } };
    }
    return {
      text: it.t,
      options: {
        bullet: it.sub ? { indent: 20, code: "25AA" } : { code: "2022" },
        indentLevel: it.sub ? 1 : 0,
        bold: it.bold || false,
        color: it.color || C.ink,
        paraSpaceAfter: 8,
      },
    };
  });
  s.addText(text, { x, y, w, h, fontSize, fontFace: "Arial", valign: "top", lineSpacingMultiple: 1.1 });
}

// Carte / encadré coloré
function card(s, x, y, w, h, fill, line) {
  s.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: fill }, line: line ? { color: line, width: 1 } : { type: "none" },
  });
}

// Petites tuiles de chiffres-clés
function statTiles(s, tiles, y) {
  const n = tiles.length;
  const gap = 0.3;
  const totalW = W - 1.4;
  const w = (totalW - gap * (n - 1)) / n;
  tiles.forEach((t, i) => {
    const x = 0.7 + i * (w + gap);
    card(s, x, y, w, 1.5, C.white, "D8CDB8");
    s.addText(t.value, {
      x, y: y + 0.18, w, h: 0.7, align: "center", fontSize: 30, bold: true,
      color: C.green, fontFace: "Arial",
    });
    s.addText(t.label, {
      x: x + 0.1, y: y + 0.95, w: w - 0.2, h: 0.5, align: "center", fontSize: 11.5,
      color: C.grey, fontFace: "Arial",
    });
  });
}

// Tableau simple
function table(s, headers, rows, opts = {}) {
  const x = opts.x ?? 0.7;
  const y = opts.y ?? 2.0;
  const w = opts.w ?? W - 1.4;
  const colW = opts.colW;
  const head = headers.map((h) => ({
    text: h,
    options: { bold: true, color: C.white, fill: { color: C.greenD }, fontFace: "Arial", valign: "middle" },
  }));
  const body = rows.map((r, ri) =>
    r.map((cell, ci) => ({
      text: String(cell),
      options: {
        color: ci === 0 ? C.ink : C.ink,
        bold: ci === 0,
        fill: { color: ri % 2 ? C.white : C.greenL },
        fontFace: "Arial",
        align: ci === 0 ? "left" : "right",
        valign: "middle",
      },
    }))
  );
  s.addTable([head, ...body], {
    x, y, w, colW,
    border: { type: "solid", color: "D8CDB8", pt: 0.5 },
    fontSize: opts.fontSize ?? 13,
    rowH: opts.rowH ?? 0.42,
    align: "left",
    valign: "middle",
  });
}

// --------------------------------------------------------------------------
// 1 — Couverture
// --------------------------------------------------------------------------
(function cover() {
  const s = pptx.addSlide();
  s.background = { color: C.greenD };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: 0.35, fill: { color: C.green } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 5.1, w: W, h: 0.06, fill: { color: C.green } });

  s.addText("FERME D'ÉLEVAGE OVIN", {
    x: 0.8, y: 1.7, w: 11.7, h: 1.0, fontSize: 46, bold: true, color: C.white, fontFace: "Arial",
  });
  s.addText("Projet d'élevage de moutons — Tchoro, Korhogo (Côte d'Ivoire)", {
    x: 0.85, y: 2.9, w: 11.5, h: 0.6, fontSize: 20, color: "C8E6C9", fontFace: "Arial",
  });
  s.addText("Dossier de présentation aux partenaires", {
    x: 0.85, y: 3.6, w: 11.5, h: 0.5, fontSize: 15, color: "A5D6A7", italic: true, fontFace: "Arial",
  });

  s.addText(
    [
      { text: "Porteur : ", options: { bold: true, color: C.white } },
      { text: CONTACT.porteur, options: { color: "E8F5E9" } },
      { text: "     ·     " + CONTACT.lieu, options: { color: "A5D6A7" } },
    ],
    { x: 0.85, y: 5.5, w: 11.5, h: 0.5, fontSize: 15, fontFace: "Arial" }
  );
  s.addText("Représentations « vue d'artiste », non contractuelles — montants indicatifs.", {
    x: 0.85, y: 6.4, w: 11.5, h: 0.4, fontSize: 11, color: "81C784", italic: true, fontFace: "Arial",
  });
})();

// --------------------------------------------------------------------------
// 2 — Le projet en bref
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Le projet en bref", "Vue d'ensemble");
  bullets(s, [
    "Créer une ferme d'élevage ovin sur un terrain de 400 m² à Tchoro (Korhogo).",
    "Race rustique adaptée au climat local : mouton Djallonké.",
    "Bergerie couverte, aire d'exercice clôturée, local technique et infirmerie.",
    "Objectif : produire des animaux sains pour la vente (viande, reproduction, Tabaski).",
    "Démarche progressive : démarrage maîtrisé puis montée en cheptel.",
  ], { w: 6.9 });

  statTiles(s, [
    { value: "400 m²", label: "Surface du terrain" },
    { value: "40–60", label: "Têtes (cible)" },
    { value: "72 m²", label: "Bergerie couverte" },
  ], 5.4);

  // encadré à droite
  card(s, 8.0, 1.9, 4.6, 3.1, C.greenL, C.green);
  s.addText("Pourquoi les moutons ?", {
    x: 8.25, y: 2.05, w: 4.1, h: 0.4, fontSize: 15, bold: true, color: C.greenD, fontFace: "Arial",
  });
  bullets(s, [
    "Demande forte et régulière en viande.",
    "Pics de vente à la Tabaski.",
    "Animal rustique, peu exigeant.",
    "Cycle de reproduction rapide.",
  ], { x: 8.3, y: 2.5, w: 4.1, h: 2.4, fontSize: 13.5 });
})();

// --------------------------------------------------------------------------
// 3 — Contexte & opportunité
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Contexte & opportunité", "Marché");
  bullets(s, [
    "Korhogo, dans le Nord, est une zone d'élevage traditionnelle reconnue.",
    "Consommation de viande ovine soutenue toute l'année.",
    "Fête de la Tabaski : forte demande et prix élevés sur une période courte.",
    "Approvisionnement local encore insuffisant face à la demande urbaine.",
    "Opportunité : produire près du marché, avec une conduite d'élevage soignée.",
  ], { w: 7.0 });

  card(s, 8.1, 1.9, 4.5, 4.3, C.white, "D8CDB8");
  s.addText("Atouts de Korhogo", {
    x: 8.35, y: 2.05, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.greenD, fontFace: "Arial",
  });
  bullets(s, [
    "Tradition pastorale ancrée.",
    "Disponibilité de fourrage et résidus de culture.",
    "Marchés à bétail actifs.",
    "Main-d'œuvre connaissant les animaux.",
    "Proximité des zones de consommation.",
  ], { x: 8.4, y: 2.5, w: 4.0, h: 3.6, fontSize: 13.5 });
})();

// --------------------------------------------------------------------------
// 4 — Localisation
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Localisation — Tchoro", "Le site");
  bullets(s, [
    "Site du projet : Tchoro, dans la région de Korhogo (Nord ivoirien).",
    "Terrain de 400 m² (20 m × 20 m), à plat, accessible.",
    "Proche des points d'eau et des axes pour l'approvisionnement.",
    "Environnement rural adapté à l'élevage.",
  ], { w: 7.0 });

  card(s, 8.1, 1.9, 4.5, 4.3, C.greenL, C.green);
  s.addText("Repères du site", {
    x: 8.35, y: 2.05, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.greenD, fontFace: "Arial",
  });
  s.addText(
    [
      { text: "Région : ", options: { bold: true } }, { text: "Korhogo (Nord)\n" },
      { text: "Localité : ", options: { bold: true } }, { text: "Tchoro\n" },
      { text: "Terrain : ", options: { bold: true } }, { text: "400 m² (20 × 20 m)\n" },
      { text: "Relief : ", options: { bold: true } }, { text: "plat\n" },
      { text: "Vocation : ", options: { bold: true } }, { text: "élevage ovin" },
    ],
    { x: 8.35, y: 2.55, w: 4.0, h: 3.5, fontSize: 14, color: C.ink, fontFace: "Arial", lineSpacingMultiple: 1.3 }
  );
})();

// --------------------------------------------------------------------------
// 5 — Le site : plan de masse (image)
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Le site : plan de masse", "Implantation sur 400 m²");
  if (fs.existsSync(SITE_PLAN)) {
    s.addImage({ path: SITE_PLAN, x: 0.7, y: 1.85, w: 4.9, h: 4.9 });
  } else {
    card(s, 0.7, 1.85, 4.9, 4.9, C.white, "D8CDB8");
    s.addText("[ Image du plan de masse manquante ]\n\nGénérer assets/site_plan.png :\npython3 python/draw_plan_png.py", {
      x: 0.9, y: 3.5, w: 4.5, h: 1.6, align: "center", fontSize: 13, color: C.grey, fontFace: "Arial",
    });
  }
  s.addText("Organisation du terrain", {
    x: 6.1, y: 1.95, w: 6.4, h: 0.4, fontSize: 16, bold: true, color: C.greenD, fontFace: "Arial",
  });
  bullets(s, [
    "Bergerie couverte (12 × 6 m = 72 m²) au nord.",
    "Aire d'exercice clôturée (≈ 114 m²) au sud.",
    "Hangar à fourrage et local technique.",
    "Infirmerie / case de quarantaine.",
    "Fumière à l'écart des logements.",
    "Portail d'accès et abreuvoir.",
  ], { x: 6.2, y: 2.45, w: 6.3, h: 3.8, fontSize: 15 });
})();

// --------------------------------------------------------------------------
// 6 — Les bâtiments
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Les bâtiments", "Implantation");
  table(s,
    ["Zone", "Dimensions", "Surface", "Rôle"],
    [
      ["Bergerie", "12 × 6 m", "72 m²", "Logement — 6 cases"],
      ["Aire d'exercice", "12 × 9,5 m", "114 m²", "Sortie, exercice"],
      ["Hangar fourrage", "3,5 × 5,5 m", "19 m²", "Foin, aliments"],
      ["Local technique", "3,5 × 4,5 m", "16 m²", "Matériel, pharmacie"],
      ["Infirmerie", "3,5 × 3,5 m", "12 m²", "Quarantaine, soins"],
      ["Fumière", "3,5 × 2 m", "7 m²", "Gestion du fumier"],
    ],
    { y: 2.0, w: W - 1.4, colW: [3.0, 2.6, 2.2, 4.13], rowH: 0.55, fontSize: 14 }
  );
  s.addText("Toitures en bac acier, murs en parpaings enduits, ventilation haute (climat chaud).", {
    x: 0.7, y: 6.4, w: 12, h: 0.4, fontSize: 12.5, italic: true, color: C.grey, fontFace: "Arial",
  });
})();

// --------------------------------------------------------------------------
// 7 — Vue 3D / maquette
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Vue 3D & maquette interactive", "Rendu");
  bullets(s, [
    "Un dossier architectural présente une vue 3D « vue d'artiste » de l'ensemble.",
    "Une maquette 3D interactive permet de tourner autour de la ferme dans un navigateur.",
    "Objectif : visualiser l'implantation et les volumes avant construction.",
    "Les plans devront être cotés et validés par un professionnel du bâtiment sur place.",
  ], { w: 7.0 });

  card(s, 8.1, 1.9, 4.5, 4.3, C.greenL, C.green);
  s.addText("À consulter", {
    x: 8.35, y: 2.05, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.greenD, fontFace: "Arial",
  });
  bullets(s, [
    "Dossier architectural (PDF, 4 pages).",
    "Plan de construction 400 m² (PDF).",
    "Maquette 3D : web/maquette_3d_ferme.html.",
    "Glisser = tourner · molette = zoomer.",
  ], { x: 8.4, y: 2.55, w: 4.0, h: 3.4, fontSize: 13.5 });
})();

// --------------------------------------------------------------------------
// 8 — Le cheptel
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Le cheptel — mouton Djallonké", "Les animaux");
  bullets(s, [
    "Race locale rustique, bien adaptée au climat et aux maladies de la zone.",
    "Bonne fertilité ; les brebis peuvent agneler plus d'une fois par an.",
    "Démarrage conseillé avec un noyau de brebis et 1 à 2 béliers.",
    "Renouvellement du troupeau par les meilleures femelles nées à la ferme.",
  ], { w: 7.0 });

  statTiles(s, [
    { value: "1 ♂", label: "pour 15–20 ♀" },
    { value: "~5 mois", label: "gestation" },
    { value: "1–2", label: "agneaux / portée" },
  ], 5.3);

  card(s, 8.1, 1.9, 4.5, 3.1, C.white, "D8CDB8");
  s.addText("Composition de départ (cible)", {
    x: 8.3, y: 2.05, w: 4.1, h: 0.4, fontSize: 14, bold: true, color: C.greenD, fontFace: "Arial",
  });
  bullets(s, [
    "20 à 30 brebis reproductrices.",
    "1 à 2 béliers.",
    "Croissance vers 40–60 têtes.",
  ], { x: 8.35, y: 2.5, w: 4.0, h: 2.3, fontSize: 14 });
})();

// --------------------------------------------------------------------------
// 9 — Conduite d'élevage
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Conduite d'élevage", "Organisation");
  bullets(s, [
    { t: "Logement", bold: true, color: C.greenD },
    { t: "Cases séparées : reproduction, agnelage, jeunes, béliers.", sub: true },
    { t: "Litière propre et sèche, bergerie bien ventilée.", sub: true },
    { t: "Sorties", bold: true, color: C.greenD },
    { t: "Accès quotidien à l'aire d'exercice.", sub: true },
    { t: "Suivi", bold: true, color: C.greenD },
    { t: "Registre du troupeau : naissances, soins, ventes.", sub: true },
    { t: "Identification des animaux.", sub: true },
  ], { w: 7.0, fontSize: 15 });

  card(s, 8.1, 1.9, 4.5, 4.3, C.amber, C.roof);
  s.addText("Bonnes pratiques", {
    x: 8.35, y: 2.05, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.roof, fontFace: "Arial",
  });
  bullets(s, [
    "Eau propre en permanence.",
    "Quarantaine des nouveaux animaux.",
    "Nettoyage régulier, gestion du fumier.",
    "Observation quotidienne du troupeau.",
  ], { x: 8.4, y: 2.55, w: 4.0, h: 3.4, fontSize: 13.5 });
})();

// --------------------------------------------------------------------------
// 10 — Alimentation
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Alimentation", "Nutrition");
  bullets(s, [
    "Base : fourrage (herbe, foin) et résidus de culture disponibles localement.",
    "Complément : son, tourteaux et concentrés selon le stade (gestation, croissance).",
    "Pierre à sel / minéraux à disposition.",
    "Eau propre en permanence, surtout en saison sèche.",
    "Stock de fourrage constitué en saison des pluies pour la saison sèche.",
  ], { w: 7.0 });

  card(s, 8.1, 1.9, 4.5, 4.3, C.greenL, C.green);
  s.addText("Ration — principe", {
    x: 8.35, y: 2.05, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.greenD, fontFace: "Arial",
  });
  bullets(s, [
    "Fourrage à volonté.",
    "Concentré pour la finition.",
    "Minéraux + sel en libre-service.",
    "Adapter aux femelles gestantes.",
  ], { x: 8.4, y: 2.55, w: 4.0, h: 3.4, fontSize: 13.5 });
})();

// --------------------------------------------------------------------------
// 11 — Santé & sanitaire
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Santé & sanitaire", "Prévention");
  bullets(s, [
    "Quarantaine systématique des animaux nouvellement achetés (2–3 semaines).",
    "Vermifugation régulière et lutte contre les parasites externes.",
    "Vaccinations selon les recommandations vétérinaires locales.",
    "Hygiène : bergerie propre, litière sèche, fumière à l'écart.",
    "Suivi vétérinaire et trousse de premiers soins au local technique.",
  ], { w: 7.0 });

  card(s, 8.1, 1.9, 4.5, 4.3, C.amber, C.roof);
  s.addText("Signaux d'alerte", {
    x: 8.35, y: 2.05, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.roof, fontFace: "Arial",
  });
  bullets(s, [
    "Perte d'appétit, animal isolé.",
    "Diarrhée, amaigrissement.",
    "Boiterie, écoulements.",
    "→ Isoler et consulter rapidement.",
  ], { x: 8.4, y: 2.55, w: 4.0, h: 3.4, fontSize: 13.5 });
})();

// --------------------------------------------------------------------------
// 12 — Plan de production
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Plan de production", "Cycle");
  bullets(s, [
    "Constitution du noyau reproducteur (brebis + béliers).",
    "Reproduction conduite, agnelages suivis à la case d'agnelage.",
    "Élevage des agneaux jusqu'au poids de vente.",
    "Ventes échelonnées + pic préparé pour la Tabaski.",
    "Sélection des meilleures femelles pour agrandir le troupeau.",
  ], { w: 7.0 });

  statTiles(s, [
    { value: "≥ 1", label: "agnelage / an / brebis" },
    { value: "Tabaski", label: "pic de vente" },
    { value: "40–60", label: "têtes visées" },
  ], 5.4);
})();

// --------------------------------------------------------------------------
// 13 — Marché & débouchés
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Marché & débouchés", "Commercialisation");
  bullets(s, [
    "Vente d'animaux sur pied aux particuliers et bouchers.",
    "Marchés à bétail de Korhogo et environs.",
    "Vente de reproducteurs à d'autres éleveurs.",
    "Pic annuel de la Tabaski : demande et prix élevés.",
    "Fidéliser une clientèle par la qualité et la régularité.",
  ], { w: 7.0 });

  card(s, 8.1, 1.9, 4.5, 4.3, C.greenL, C.green);
  s.addText("Canaux de vente", {
    x: 8.35, y: 2.05, w: 4.0, h: 0.4, fontSize: 15, bold: true, color: C.greenD, fontFace: "Arial",
  });
  bullets(s, [
    "Particuliers (fêtes, cérémonies).",
    "Bouchers / restaurateurs.",
    "Éleveurs (reproducteurs).",
    "Marché de la Tabaski.",
  ], { x: 8.4, y: 2.55, w: 4.0, h: 3.4, fontSize: 13.5 });
})();

// --------------------------------------------------------------------------
// 14 — Budget d'investissement
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Budget d'investissement", "Ordres de grandeur (FCFA)");
  table(s,
    ["Poste", "Montant indicatif"],
    [
      ["Construction bergerie + abris", "2 500 000"],
      ["Clôture aire d'exercice + portail", "600 000"],
      ["Aménagements (eau, mangeoires…)", "500 000"],
      ["Achat du cheptel de départ", "1 800 000"],
      ["Aliments & vétérinaire (1re année)", "900 000"],
      ["Divers & imprévus", "400 000"],
      ["TOTAL indicatif", "6 700 000"],
    ],
    { y: 2.0, w: 7.6, colW: [5.0, 2.6], rowH: 0.52, fontSize: 14 }
  );
  card(s, 8.6, 2.0, 4.0, 3.8, C.amber, C.roof);
  s.addText("À retenir", {
    x: 8.85, y: 2.15, w: 3.5, h: 0.4, fontSize: 15, bold: true, color: C.roof, fontFace: "Arial",
  });
  s.addText(
    "Montants indicatifs à ajuster avec des devis locaux (maçon, marché à bétail, "
    + "fournisseur d'aliments). Un démarrage progressif réduit le besoin initial.",
    { x: 8.85, y: 2.7, w: 3.5, h: 3.0, fontSize: 13, color: C.ink, fontFace: "Arial", valign: "top" }
  );
})();

// --------------------------------------------------------------------------
// 15 — Charges & revenus
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Charges & revenus", "Rentabilité (indicatif)");
  bullets(s, [
    "Charges récurrentes : aliments, soins vétérinaires, main-d'œuvre, entretien.",
    "Revenus : ventes d'animaux (viande, reproducteurs), pic à la Tabaski.",
    "La rentabilité dépend du taux de survie, de la reproduction et des prix de vente.",
    "Le fumier peut constituer un revenu d'appoint (fertilisant).",
  ], { w: 7.0 });

  card(s, 8.1, 1.9, 4.5, 4.3, C.white, "D8CDB8");
  s.addText("Leviers de performance", {
    x: 8.3, y: 2.05, w: 4.1, h: 0.4, fontSize: 14.5, bold: true, color: C.greenD, fontFace: "Arial",
  });
  bullets(s, [
    "Bonne conduite sanitaire (peu de pertes).",
    "Alimentation régulière.",
    "Vente au bon moment (Tabaski).",
    "Sélection des reproductrices.",
  ], { x: 8.35, y: 2.55, w: 4.0, h: 3.4, fontSize: 13.5 });
})();

// --------------------------------------------------------------------------
// 16 — Calendrier / étapes
// --------------------------------------------------------------------------
(function () {
  const s = baseSlide();
  heading(s, "Calendrier des étapes", "Mise en œuvre");
  const steps = [
    ["1", "Préparation", "Terrain, autorisations, devis, financement"],
    ["2", "Construction", "Bergerie, abris, clôture, eau"],
    ["3", "Installation", "Équipements, mangeoires, litière"],
    ["4", "Cheptel", "Achat du noyau, quarantaine, mise en place"],
    ["5", "Production", "Reproduction, agnelages, croissance"],
    ["6", "Commercialisation", "Ventes échelonnées, Tabaski, réinvestissement"],
  ];
  let y = 2.0;
  steps.forEach((st) => {
    s.addShape(pptx.ShapeType.ellipse, { x: 0.7, y, w: 0.6, h: 0.6, fill: { color: C.green } });
    s.addText(st[0], { x: 0.7, y, w: 0.6, h: 0.6, align: "center", valign: "middle", color: C.white, bold: true, fontSize: 18, fontFace: "Arial" });
    s.addText(st[1], { x: 1.5, y: y + 0.02, w: 3.2, h: 0.6, fontSize: 16, bold: true, color: C.greenD, valign: "middle", fontFace: "Arial" });
    s.addText(st[2], { x: 4.7, y: y + 0.02, w: 8.0, h: 0.6, fontSize: 14, color: C.ink, valign: "middle", fontFace: "Arial" });
    y += 0.78;
  });
})();

// --------------------------------------------------------------------------
// 17 — Partenariat & contact
// --------------------------------------------------------------------------
(function () {
  const s = pptx.addSlide();
  s.background = { color: C.greenD };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: 0.35, fill: { color: C.green } });
  s.addText("Rejoignez le projet", {
    x: 0.8, y: 1.2, w: 11.7, h: 0.9, fontSize: 40, bold: true, color: C.white, fontFace: "Arial",
  });
  s.addText("Ensemble, développons un élevage ovin durable à Tchoro (Korhogo).", {
    x: 0.85, y: 2.2, w: 11.5, h: 0.6, fontSize: 18, color: "C8E6C9", fontFace: "Arial",
  });

  bullets(s, [
    "Participer au financement de l'installation.",
    "Appuyer l'approvisionnement (cheptel, aliments).",
    "Accompagner sur le plan technique ou vétérinaire.",
    "Ouvrir des débouchés commerciaux.",
  ], { x: 0.85, y: 3.1, w: 7.0, h: 2.4, fontSize: 16 });

  card(s, 8.2, 3.0, 4.3, 2.9, C.greenL, C.green);
  s.addText("Contact", {
    x: 8.45, y: 3.15, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: C.greenD, fontFace: "Arial",
  });
  s.addText(
    [
      { text: CONTACT.porteur + "\n", options: { bold: true, fontSize: 16 } },
      { text: CONTACT.telephone + "\n", options: { fontSize: 14 } },
      { text: CONTACT.email + "\n", options: { fontSize: 14 } },
      { text: CONTACT.lieu, options: { fontSize: 13, color: C.grey } },
    ],
    { x: 8.45, y: 3.65, w: 3.8, h: 2.0, color: C.ink, fontFace: "Arial", lineSpacingMultiple: 1.25 }
  );
  s.addText("Montants et représentations indicatifs, non contractuels.", {
    x: 0.85, y: 6.6, w: 11.5, h: 0.4, fontSize: 11, italic: true, color: "81C784", fontFace: "Arial",
  });
})();

// --------------------------------------------------------------------------
// Écriture
// --------------------------------------------------------------------------
if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });
pptx.writeFile({ fileName: OUT }).then((f) => {
  console.log("OK →", path.relative(ROOT, f));
}).catch((e) => {
  console.error("Erreur :", e);
  process.exit(1);
});
