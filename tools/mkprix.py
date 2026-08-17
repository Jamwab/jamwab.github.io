# -*- coding: utf-8 -*-
"""Figures de suivi des cours des matieres premieres produites par la RDC."""
import json
import mklib as M
from mklib import (reg, gr, ge, bil, tsp, num, esc, txt, line, rect, circ, poly,
                   PX0, PX1, PY0, PY1, LABY, yscale, xord, ygrid, xlabels, legend,
                   figure, SERIES)

PINE, DEEP, BRASS, RUST, TEAL, MUT = ("var(--pine)", "var(--pine-deep)", "var(--brass)",
                                      "var(--rust)", "var(--teal)", "var(--muted)")

import os
_HERE = os.path.dirname(os.path.abspath(__file__))
for _c in (os.path.join(_HERE, "data", "prix-brut.json"),
           os.path.join(_HERE, os.pardir, "data", "prix-brut.json"),
           "data/prix-brut.json"):
    _RAW = _c
    if os.path.exists(_RAW):
        break

_DEF_LAB = [["2023", "2023"], ["2024", "2024"], ["2025", "2025"],
            ["Q1-26", "T1-26"], ["Q2-26", "T2-26"],
            ["May 26", "mai 26"], ["Jun 26", "juin 26"], ["Jul 26", "juil. 26"]]
_DEF_D = {
    "copper": [8490, 9142, 9947, 12831, 13349, 13543, 13552, 13543],
    "tin":    [25938, 30066, 34059, 48519, 51802, 53563, 53037, 52971],
    "gold":   [1943, 2388, 3442, 4876, 4512, 4587, 4228, 4073],
    "brent":  [82.6, 80.7, 69.0, 80.5, 104.4, 107.5, 85.4, 83.4],
    "cocoa":  [3.28, 7.33, 7.80, 3.93, 3.98, 4.16, 4.40, 5.61],
    "arab":   [4.54, 5.62, 8.47, 7.49, 7.01, 6.95, 6.79, 7.91],
    "rob":    [2.63, 4.41, 4.86, 4.03, 3.68, 3.67, 3.73, 4.07],
    "palm":   [886, 963, 1007, 1051, 1129, 1136, 1104, 1101],
    "rubber": [1.38, 1.75, 1.77, 1.91, 2.17, 2.21, 2.25, 2.14],
    "logs":   [378.6, 378.7, 395.4, 409.7, 407.0, 408.8, 403.2, 399.7],
    "zinc":   [2653, 2776, 2868, 3240, 3462, 3482, 3539, 3599],
    "mm":     [104.0, 106.7, 112.2, 137.1, 145.7, 148.8, 144.6, 140.5],
    "pm":     [147.3, 180.2, 258.6, 393.1, 359.6, 368.7, 334.7, 317.2],
}

_DEF_HORS = {                     # series hors Pink Sheet, tenues a la main
    "cobalt": [["2025-02", "Hydroxide", "Hydroxyde", 5.60],
               ["2026-04-09", "Hydroxide", "Hydroxyde", 25.95],
               ["2026-06-24", "Hydroxide", "Hydroxyde", 25.40],
               ["2026-06-24", "Metal", "M&#233;tal", 26.23]],
    "coltan": [["2026-01-01", 106.6], ["2026-02-19", 152.5]],
    "lithium": [["2025-05", 8.0], ["2026-06", 24.2]],
}

if os.path.exists(_RAW):
    _J = json.load(open(_RAW, encoding="utf-8"))
    LAB = [tuple(x) for x in _J.get("labels", _DEF_LAB)]
    D = dict(_DEF_D); D.update(_J.get("series", {}))
    HORS = dict(_DEF_HORS); HORS.update(_J.get("hors_pink_sheet", {}))
    EDITION_EN = _J.get("edition_en", "4 August 2026")
    EDITION_FR = _J.get("edition_fr", "4 ao&#251;t 2026")
else:
    LAB = [tuple(x) for x in _DEF_LAB]
    D, HORS = dict(_DEF_D), dict(_DEF_HORS)
    EDITION_EN, EDITION_FR = "4 August 2026", "4 ao&#251;t 2026"

COLS = [("Period", "P&#233;riode")]
N = len(LAB)

FIGS = []
SRC_EN = ("World Bank, Commodity Markets Outlook, Pink Sheet of 4 August 2026; "
          "series compiled by James Wabenga Yango.")
SRC_FR = ("Banque mondiale, Commodity Markets Outlook, Pink Sheet du 4 ao&#251;t 2026&#8239;; "
          "s&#233;ries mises en forme par James Wabenga Yango.")


def rows_of(keys):
    """Construit les lignes du registre : periode + une colonne par serie."""
    return [[LAB[i][0]] + [D[k][i] for k in keys] for i in range(N)]


def dots(vals, lo, hi, col, r=1.9):
    return "".join(circ(xord(i, N), yscale(v, lo, hi), r, col)
                   for i, v in enumerate(vals))


def curve(vals, lo, hi, col, w=1.7, dash=None):
    pts = [(xord(i, N), yscale(v, lo, hi)) for i, v in enumerate(vals)]
    return poly(pts, col, w, dash) + dots(vals, lo, hi, col)


# =============================================================== 1. cuivre / etain / zinc
def fig_cu_sn():
    keys = [("copper", PINE, "Copper", "Cuivre", "13,543 $/t", "13&#8239;543 $/t"),
            ("tin", TEAL, "Tin", "&#201;tain", "52,971 $/t", "52&#8239;971 $/t"),
            ("zinc", BRASS, "Zinc", "Zinc", "3,599 $/t", "3&#8239;599 $/t")]
    idx = {k: [100.0 * v / D[k][0] for v in D[k]] for k, _, _, _, _, _ in keys}
    lo, hi = 90, 220
    s = [ygrid([90, 122, 155, 187, 220], lo, hi, lambda v: (ge(v), gr(v)))]
    s.append(line(PX0, yscale(100, lo, hi), PX1, yscale(100, lo, hi), "var(--line)", 1, "3 3"))
    for k, c, _, _, _, _ in keys:
        s.append(curve(idx[k], lo, hi, c, 1.7))
    s.append(xlabels(LAB, N))
    for k, c, _, _, le, lf in keys:
        y = yscale(idx[k][-1], lo, hi)
        s.append(txt(xord(7, N) - 8, y - 8, tsp(le, lf), 9, c, "end", weight=600))
    s.append(legend([(PINE, "Copper, index 2023 = 100", "Cuivre, indice 2023 = 100"),
                     (TEAL, "Tin, index 2023 = 100", "&#201;tain, indice 2023 = 100"),
                     (BRASS, "Zinc, index 2023 = 100", "Zinc, indice 2023 = 100")], 240))
    return ('<svg viewBox="0 0 720 254" role="img" aria-label="Cuivre, etain et zinc">'
            + "".join(s) + "</svg>")


reg("prix-cu-sn", "Copper, tin and zinc prices",
    "Cours du cuivre, de l&#8217;&#233;tain et du zinc",
    "World Bank Pink Sheet, 4 Aug 2026",
    ["Period", "Copper, $/t", "Tin, $/t", "Zinc, $/t"], rows_of(["copper", "tin", "zinc"]))
FIGS.append(figure(
    "prix-cu-sn",
    "Copper, tin and zinc, index 2023 = 100, to July 2026",
    "Cuivre, &#233;tain et zinc, indice 2023 = 100, jusqu&#8217;en juillet 2026",
    fig_cu_sn(),
    "World Bank Pink Sheet, 4 August 2026, London Metal Exchange cash prices. The July 2026 "
    "level in dollars is written against each curve. Tin has risen twice as fast as copper "
    "since 2023.",
    "Banque mondiale, Pink Sheet du 4 ao&#251;t 2026, prix comptant du London Metal Exchange. "
    "Le niveau de juillet 2026 en dollars est inscrit contre chaque courbe. "
    "L&#8217;&#233;tain a progress&#233; deux fois plus vite que le cuivre depuis 2023."))


# =============================================================== 2. cobalt
def fig_cobalt():
    """Chronologie du cobalt : le prix est ici une variable de politique publique."""
    VH = 268
    s = []
    y0, y1 = 40.0, 178.0
    lo, hi = 0.0, 30.0
    for v in (0, 5, 10, 15, 20, 25, 30):
        y = y1 - (y1 - y0) * (v - lo) / (hi - lo)
        s.append(line(PX0, y, PX1, y, "var(--line-soft)"))
        s.append(txt(PX0 - 8, y + 3, tsp(ge(v), gr(v)), 9, MUT, "end"))
    # trois observations datees
    OBS = [(0.11, 5.60, "Feb 2025", "f&#233;vr. 2025", "hydroxide, pre-ban", "hydroxyde, avant l&#8217;interdiction"),
           (0.62, 25.95, "9 Apr 2026", "9 avr. 2026", "hydroxide", "hydroxyde"),
           (0.93, 25.40, "24 Jun 2026", "24 juin 2026", "hydroxide", "hydroxyde")]
    pts = []
    for f, v, de, df, ne, nf in OBS:
        x = PX0 + (PX1 - PX0) * f
        y = y1 - (y1 - y0) * (v - lo) / (hi - lo)
        pts.append((x, y))
    s.append(poly(pts, RUST, 1.7))
    for i, ((x, y), (f, v, de, df, ne, nf)) in enumerate(zip(pts, OBS)):
        s.append(circ(x, y, 3.4, RUST))
        if i == 0:                     # a droite du trait de politique
            s.append(txt(x + 11, y - 14, tsp(f"{ge(v,2)} $/lb", f"{gr(v,2)} $/lb"),
                         9.5, "var(--ink-soft)", "start", weight=600))
            s.append(txt(x + 11, y - 2, tsp(de, df), 8.6, MUT, "start"))
        else:
            s.append(txt(x, y - 12, tsp(f"{ge(v,2)} $/lb", f"{gr(v,2)} $/lb"),
                         9.5, "var(--ink-soft)", "middle", weight=600))
            s.append(txt(x, y + 19, tsp(de, df), 8.6, MUT, "middle"))
    # metal de juin
    xm = PX0 + (PX1 - PX0) * 0.93
    ym = y1 - (y1 - y0) * (26.23 - lo) / (hi - lo)
    s.append(circ(xm, ym, 3.0, TEAL))
    s.append(txt(xm, ym - 26, tsp("metal 26.23 $/lb", "m&#233;tal 26,23 $/lb"),
                 9, TEAL, "middle", weight=600))
    # bande de politique
    xb = PX0 + (PX1 - PX0) * 0.11
    s.append(line(xb, y0 - 14, xb, y1 + 6, BRASS, 1, "3 3"))
    s.append(txt(xb - 4, y0 - 18, tsp("22 Feb 2025: export ban", "22 f&#233;vr. 2025 : interdiction d&#8217;exporter"),
                 9, BRASS, "start", weight=600))
    xq = PX0 + (PX1 - PX0) * 0.46
    s.append(line(xq, y0 - 2, xq, y1 + 6, BRASS, 1, "3 3"))
    s.append(txt(xq + 7, y0 - 6, tsp("Oct 2025: quota regime", "oct. 2025 : r&#233;gime de quotas"),
                 9, BRASS, "start", weight=600))
    s.append(line(PX0, y1 + 6, PX1, y1 + 6, "var(--line)"))
    s.append(txt(PX0, y1 + 24, tsp("2025", "2025"), 9, MUT, "start"))
    s.append(txt(PX1, y1 + 24, tsp("mid-2026", "mi-2026"), 9, MUT, "end"))
    s.append(txt(PX0, y1 + 46,
                 tsp("DRC supplies 73 per cent of world cobalt. 2026 quota: 96,600 tonnes.",
                     "La RDC fournit 73 pour cent du cobalt mondial. Quota 2026 : 96&#8239;600 tonnes."),
                 9, MUT, "start"))
    s.append(legend([(RUST, "Cobalt hydroxide, $/lb", "Hydroxyde de cobalt, $/lb"),
                     (TEAL, "Cobalt metal, $/lb", "Cobalt m&#233;tal, $/lb")], VH - 8))
    return f'<svg viewBox="0 0 720 {VH}" role="img" aria-label="Cobalt">' + "".join(s) + "</svg>"


reg("prix-cobalt", "Cobalt price", "Cours du cobalt", "Fastmarkets, Reuters, press reports",
    ["Date", "Product", "Price, $/lb"],
    [["2025-02", "Hydroxide", 5.60], ["2026-04-09", "Hydroxide", 25.95],
     ["2026-06-24", "Hydroxide", 25.40], ["2026-06-24", "Metal", 26.23]],
    note="Cobalt n'est pas dans la Pink Sheet.")
FIGS.append(figure(
    "prix-cobalt",
    "Cobalt: a price made by Congolese policy, February 2025 to June 2026",
    "Cobalt : un prix fait par la politique congolaise, f&#233;vrier 2025 &#224; juin 2026",
    fig_cobalt(),
    "Fastmarkets and press reports. The Democratic Republic of the Congo suspended cobalt "
    "exports on 22 February 2025, when hydroxide delivered to China had fallen to about "
    "5.60 dollars a pound, and replaced the ban with a quota regime running to 2027. "
    "Cobalt is not covered by the Pink Sheet, so these are dated observations rather than "
    "a continuous series.",
    "Fastmarkets et presse sp&#233;cialis&#233;e. La R&#233;publique d&#233;mocratique du "
    "Congo a suspendu les exportations de cobalt le 22 f&#233;vrier 2025, alors que "
    "l&#8217;hydroxyde livr&#233; en Chine &#233;tait tomb&#233; &#224; environ 5,60 dollars "
    "la livre, puis a remplac&#233; l&#8217;interdiction par un r&#233;gime de quotas courant "
    "jusqu&#8217;en 2027. Le cobalt ne figure pas dans la Pink Sheet&#8239;: il s&#8217;agit "
    "donc d&#8217;observations dat&#233;es et non d&#8217;une s&#233;rie continue."))


# =============================================================== 3. or et petrole
def fig_au_brent():
    PXR = 656.0                       # bord droit reduit : place pour l'axe de droite
    old = M.PX1
    M.PX1 = PXR
    r = _fig_au_brent(PXR)
    M.PX1 = old
    return r


def _fig_au_brent(PX1):
    lo1, hi1 = 1800, 5000
    lo2, hi2 = 60, 115
    s = []
    for v in (2000, 2750, 3500, 4250, 5000):
        y = yscale(v, lo1, hi1)
        s.append(line(PX0, y, PX1, y, "var(--line-soft)"))
        s.append(txt(PX0 - 8, y + 3, tsp(ge(v), gr(v)), 9, MUT, "end"))
    for v in (60, 75, 90, 105):
        y = yscale(v, lo2, hi2)
        s.append(txt(PX1 + 8, y + 3, tsp(ge(v), gr(v)), 9, RUST, "start"))
    s.append(curve(D["gold"], lo1, hi1, BRASS))
    s.append(curve(D["brent"], lo2, hi2, RUST, 1.5, "4 3"))
    s.append(xlabels(LAB, N))
    yg = yscale(4876, lo1, hi1)
    s.append(txt(xord(3, N) + 6, yg - 8, tsp("4,876 $/oz, peak", "4&#8239;876 $/oz, sommet"),
                 9, BRASS, "start", weight=600))
    yb = yscale(107.5, lo2, hi2)
    s.append(txt(xord(5, N) - 6, yb - 8, tsp("107.5 $/bbl", "107,5 $/bbl"),
                 9, RUST, "end", weight=600))
    s.append(legend([(BRASS, "Gold, $/troy ounce, left", "Or, $/once troy, gauche"),
                     (RUST, "Brent crude, $/barrel, right", "P&#233;trole Brent, $/baril, droite")], 240))
    return ('<svg viewBox="0 0 720 258" role="img" aria-label="Or et petrole">'
            + "".join(s) + "</svg>")


reg("prix-au-brent", "Gold and Brent crude prices", "Cours de l&#8217;or et du Brent",
    "World Bank Pink Sheet, 4 Aug 2026",
    ["Period", "Gold, $/toz", "Brent, $/bbl"], rows_of(["gold", "brent"]))
FIGS.append(figure(
    "prix-au-brent",
    "Gold and Brent crude, 2023 to July 2026",
    "Or et p&#233;trole Brent, 2023 &#224; juillet 2026",
    fig_au_brent(),
    "World Bank Pink Sheet, 4 August 2026. Gold is an export for the Democratic Republic "
    "of the Congo and crude oil an import, so the two lines move the terms of trade in "
    "opposite directions.",
    "Banque mondiale, Pink Sheet du 4 ao&#251;t 2026. L&#8217;or est une exportation pour la "
    "R&#233;publique d&#233;mocratique du Congo et le p&#233;trole brut une importation&#8239;: "
    "les deux courbes d&#233;placent donc les termes de l&#8217;&#233;change en sens contraire."))


# =============================================================== 4. agricole, indice
def fig_agri():
    keys = [("cocoa", RUST, "Cocoa", "Cacao"),
            ("arab", "var(--pine)", "Arabica coffee", "Caf&#233; arabica"),
            ("palm", TEAL, "Palm oil", "Huile de palme"),
            ("rubber", BRASS, "Rubber", "Caoutchouc"),
            ("logs", DEEP, "African logs", "Grumes d&#8217;Afrique")]
    idx = {k: [100.0 * v / D[k][0] for v in D[k]] for k, _, _, _ in keys}
    lo, hi = 50, 250
    s = [ygrid([50, 100, 150, 200, 250], lo, hi, lambda v: (ge(v), gr(v)))]
    s.append(line(PX0, yscale(100, lo, hi), PX1, yscale(100, lo, hi), "var(--line)", 1, "3 3"))
    for k, c, _, _ in keys:
        s.append(curve(idx[k], lo, hi, c, 1.6))
    s.append(xlabels(LAB, N))
    s.append(legend([(RUST, "Cocoa", "Cacao"),
                     (PINE, "Arabica coffee", "Caf&#233; arabica"),
                     (TEAL, "Palm oil", "Huile de palme"),
                     (BRASS, "Rubber", "Caoutchouc"),
                     (DEEP, "African logs", "Grumes d&#8217;Afrique")], 240))
    return ('<svg viewBox="0 0 720 252" role="img" aria-label="Produits agricoles">'
            + "".join(s) + "</svg>")


reg("prix-agri", "Agricultural commodity prices",
    "Cours des produits agricoles", "World Bank Pink Sheet, 4 Aug 2026",
    ["Period", "Cocoa, $/kg", "Arabica coffee, $/kg", "Robusta coffee, $/kg",
     "Palm oil, $/t", "Rubber TSR20, $/kg", "African logs, $/cum"],
    rows_of(["cocoa", "arab", "rob", "palm", "rubber", "logs"]))
FIGS.append(figure(
    "prix-agri",
    "Agricultural export prices, index 2023 = 100",
    "Prix des exportations agricoles, indice 2023 = 100",
    fig_agri(),
    "World Bank Pink Sheet, 4 August 2026. Cocoa, coffee, palm oil, rubber and tropical "
    "logs are the agricultural products the Democratic Republic of the Congo exports or "
    "could export at scale. Robusta coffee is in the downloadable series.",
    "Banque mondiale, Pink Sheet du 4 ao&#251;t 2026. Le cacao, le caf&#233;, l&#8217;huile "
    "de palme, le caoutchouc et les grumes tropicales sont les produits agricoles que la "
    "R&#233;publique d&#233;mocratique du Congo exporte ou pourrait exporter &#224; grande "
    "&#233;chelle. Le caf&#233; robusta figure dans la s&#233;rie t&#233;l&#233;chargeable."))


# =============================================================== 5. coltan et lithium
def fig_coltan_li():
    VH = 250
    s = []
    # ---- panneau gauche : coltan
    ax0, ax1 = 56.0, 340.0
    y0, y1 = 46.0, 176.0
    lo, hi = 0.0, 180.0
    for v in (0, 60, 120, 180):
        y = y1 - (y1 - y0) * (v - lo) / (hi - lo)
        s.append(line(ax0, y, ax1, y, "var(--line-soft)"))
        s.append(txt(ax0 - 8, y + 3, tsp(ge(v), gr(v)), 9, MUT, "end"))
    s.append(txt(ax0, 30, tsp("TANTALITE, $/LB", "TANTALITE, $/LB"), 8.6, "var(--ink-soft)",
                 weight=600, ls="0.1em"))
    CT = [(0.10, 106.6, "1 Jan 2026", "1<tspan>er</tspan> janv. 2026"),
          (0.78, 152.5, "19 Feb 2026", "19 f&#233;vr. 2026")]
    p = []
    for f, v, de, df in CT:
        x = ax0 + (ax1 - ax0) * f
        y = y1 - (y1 - y0) * (v - lo) / (hi - lo)
        p.append((x, y))
    s.append(poly(p, RUST, 2.0))
    lbl = [("107", "107", "1 Jan 2026", "1 janv. 2026"), ("152", "152", "19 Feb 2026", "19 f&#233;vr. 2026")]
    for (x, y), (ne, nf, de, df) in zip(p, lbl):
        s.append(circ(x, y, 3.4, RUST))
        s.append(txt(x, y - 11, tsp(ne + " $/lb", nf + " $/lb"), 9.5, "var(--ink-soft)",
                     "middle", weight=600))
        s.append(txt(x, y + 16, tsp(de, df), 8.4, MUT, "middle"))
    s.append(txt((ax0 + ax1) / 2, y1 + 40,
                 tsp("+43% after the Rubaya landslide", "+43&#8239;% apr&#232;s l&#8217;&#233;boulement de Rubaya"),
                 9, RUST, "middle", weight=600))
    # ---- panneau droit : lithium
    bx0, bx1 = 420.0, 704.0
    lo2, hi2 = 0.0, 30.0
    for v in (0, 10, 20, 30):
        y = y1 - (y1 - y0) * (v - lo2) / (hi2 - lo2)
        s.append(line(bx0, y, bx1, y, "var(--line-soft)"))
        s.append(txt(bx0 - 8, y + 3, tsp(ge(v), gr(v)), 9, MUT, "end"))
    s.append(txt(bx0, 30, tsp("LITHIUM CARBONATE, $/KG", "CARBONATE DE LITHIUM, $/KG"),
                 8.6, "var(--ink-soft)", weight=600, ls="0.1em"))
    LI = [(0.14, 8.0, "May 2025", "mai 2025"), (0.86, 24.2, "Jun 2026", "juin 2026")]
    q = []
    for f, v, de, df in LI:
        x = bx0 + (bx1 - bx0) * f
        y = y1 - (y1 - y0) * (v - lo2) / (hi2 - lo2)
        q.append((x, y))
    s.append(poly(q, TEAL, 2.0))
    for (x, y), (f, v, de, df) in zip(q, LI):
        s.append(circ(x, y, 3.4, TEAL))
        s.append(txt(x, y - 11, tsp(f"{ge(v,1)} $/kg", f"{gr(v,1)} $/kg"), 9.5,
                     "var(--ink-soft)", "middle", weight=600))
        s.append(txt(x, y + 16, tsp(de, df), 8.4, MUT, "middle"))
    s.append(txt((bx0 + bx1) / 2, y1 + 40,
                 tsp("+203% in thirteen months", "+203&#8239;% en treize mois"),
                 9, TEAL, "middle", weight=600))
    s.append(txt(56, VH - 8,
                 tsp("Manono is one of the largest undeveloped lithium deposits in the world.",
                     "Manono est l&#8217;un des plus grands gisements de lithium non exploit&#233;s au monde."),
                 9, MUT))
    return f'<svg viewBox="0 0 720 {VH}" role="img" aria-label="Coltan et lithium">' + "".join(s) + "</svg>"


reg("prix-coltan-li", "Tantalite and lithium prices",
    "Cours de la tantalite et du lithium", "Press reports, Q1-Q2 2026",
    ["Date", "Product", "Price", "Unit"],
    [["2026-01-01", "Tantalite", 106.6, "$/lb, implied"],
     ["2026-02-19", "Tantalite", 152.5, "$/lb"],
     ["2025-05", "Lithium carbonate", 8.0, "$/kg"],
     ["2026-06", "Lithium carbonate", 24.2, "$/kg"]])
FIGS.append(figure(
    "prix-coltan-li",
    "Tantalite and lithium carbonate, 2025 to mid-2026",
    "Tantalite et carbonate de lithium, 2025 &#224; mi-2026",
    fig_coltan_li(),
    "Press reports. Tantalite stood at 149 to 156 dollars a pound on 19 February 2026, up "
    "43 per cent since the start of the year after the Rubaya landslide in the eastern "
    "Democratic Republic of the Congo; the January level is implied by that change. "
    "Lithium carbonate was quoted at 24,156 dollars a tonne in China and 24,244 in India "
    "in June 2026. Neither series is published in the Pink Sheet.",
    "Presse sp&#233;cialis&#233;e. La tantalite valait 149 &#224; 156 dollars la livre le "
    "19 f&#233;vrier 2026, en hausse de 43 pour cent depuis le d&#233;but de "
    "l&#8217;ann&#233;e apr&#232;s l&#8217;&#233;boulement de Rubaya dans l&#8217;est de la "
    "R&#233;publique d&#233;mocratique du Congo&#8239;; le niveau de janvier se d&#233;duit "
    "de cette variation. Le carbonate de lithium &#233;tait cot&#233; 24&#8239;156 dollars "
    "la tonne en Chine et 24&#8239;244 en Inde en juin 2026. Aucune des deux s&#233;ries "
    "n&#8217;est publi&#233;e dans la Pink Sheet."))


# =============================================================== 6. indices
def fig_indices():
    lo, hi = 80, 420
    s = [ygrid([80, 165, 250, 335, 420], lo, hi, lambda v: (ge(v), gr(v)))]
    s.append(line(PX0, yscale(100, lo, hi), PX1, yscale(100, lo, hi), "var(--line)", 1, "3 3"))
    s.append(curve(D["mm"], lo, hi, PINE))
    s.append(curve(D["pm"], lo, hi, BRASS))
    s.append(xlabels(LAB, N))
    yp = yscale(393.1, lo, hi)
    s.append(txt(xord(3, N) + 7, yp - 7,
                 tsp("precious metals peak, Q1-26", "sommet des m&#233;taux pr&#233;cieux, T1-26"),
                 9, BRASS, "start", weight=600))
    s.append(legend([(PINE, "Metals and minerals, 2010 = 100", "M&#233;taux et min&#233;raux, 2010 = 100"),
                     (BRASS, "Precious metals, 2010 = 100", "M&#233;taux pr&#233;cieux, 2010 = 100")], 240))
    return ('<svg viewBox="0 0 720 258" role="img" aria-label="Indices de prix">'
            + "".join(s) + "</svg>")


reg("prix-indices", "World Bank commodity price indices",
    "Indices de prix des mati&#232;res premi&#232;res, Banque mondiale",
    "World Bank Pink Sheet, 4 Aug 2026",
    ["Period", "Metals and minerals, 2010=100", "Precious metals, 2010=100"],
    rows_of(["mm", "pm"]))
FIGS.append(figure(
    "prix-indices",
    "World Bank price indices, metals and precious metals",
    "Indices de prix de la Banque mondiale, m&#233;taux et m&#233;taux pr&#233;cieux",
    fig_indices(),
    "World Bank Pink Sheet, 4 August 2026. The metals and minerals index is the single "
    "best summary of the Congolese terms of trade.",
    "Banque mondiale, Pink Sheet du 4 ao&#251;t 2026. L&#8217;indice des m&#233;taux et "
    "min&#233;raux est le meilleur r&#233;sum&#233; disponible des termes de "
    "l&#8217;&#233;change congolais."))


# =============================================================== tableau de synthese
def pct(a, b):
    return 100.0 * (b - a) / a


TAB_ROWS = [
    # (nom_en, nom_fr, unite_en, unite_fr, ref2025, dernier, date_en, date_fr, source)
    ("Copper", "Cuivre", "$/tonne", "$/tonne", 9947, 13543, "Jul 2026", "juil. 2026", "PS"),
    ("Cobalt hydroxide", "Hydroxyde de cobalt", "$/lb", "$/lb", None, 25.40, "24 Jun 2026", "24 juin 2026", "FM"),
    ("Gold", "Or", "$/troy ounce", "$/once troy", 3442, 4073, "Jul 2026", "juil. 2026", "PS"),
    ("Tin", "&#201;tain", "$/tonne", "$/tonne", 34059, 52971, "Jul 2026", "juil. 2026", "PS"),
    ("Tantalite (coltan)", "Tantalite (coltan)", "$/lb", "$/lb", None, 152.5, "19 Feb 2026", "19 f&#233;vr. 2026", "PR"),
    ("Zinc", "Zinc", "$/tonne", "$/tonne", 2868, 3599, "Jul 2026", "juil. 2026", "PS"),
    ("Lithium carbonate", "Carbonate de lithium", "$/kg", "$/kg", None, 24.2, "Jun 2026", "juin 2026", "PR"),
    ("Crude oil, Brent", "P&#233;trole brut, Brent", "$/barrel", "$/baril", 69.0, 83.4, "Jul 2026", "juil. 2026", "PS"),
    ("Rough diamond", "Diamant brut", "index", "indice", None, None, "&#8212;", "&#8212;", "NA"),
    ("Cocoa", "Cacao", "$/kg", "$/kg", 7.80, 5.61, "Jul 2026", "juil. 2026", "PS"),
    ("Coffee, arabica", "Caf&#233; arabica", "$/kg", "$/kg", 8.47, 7.91, "Jul 2026", "juil. 2026", "PS"),
    ("Coffee, robusta", "Caf&#233; robusta", "$/kg", "$/kg", 4.86, 4.07, "Jul 2026", "juil. 2026", "PS"),
    ("Palm oil", "Huile de palme", "$/tonne", "$/tonne", 1007, 1101, "Jul 2026", "juil. 2026", "PS"),
    ("Rubber, TSR20", "Caoutchouc, TSR20", "$/kg", "$/kg", 1.77, 2.14, "Jul 2026", "juil. 2026", "PS"),
    ("Logs, Africa", "Grumes, Afrique", "$/cubic metre", "$/m&#232;tre cube", 395.4, 399.7, "Jul 2026", "juil. 2026", "PS"),
]


def build_tab():
    dec = {"$/kg": 2, "$/lb": 2, "$/barrel": 1, "$/cubic metre": 1}
    h = ['<div class="tablewrap"><table class="macro-tab prix-tab"><thead><tr>',
         f'<th scope="col">{bil("Commodity","Produit")}</th>',
         f'<th scope="col">{bil("Unit","Unit&#233;")}</th>',
         f'<th scope="col">{bil("2025 average","Moyenne 2025")}</th>',
         f'<th scope="col">{bil("Latest","Dernier")}</th>',
         f'<th scope="col">{bil("Change, %","Variation, %")}</th>',
         f'<th scope="col">{bil("As at","Au")}</th></tr></thead><tbody>']
    rows = []
    for ne, nf, ue, uf, ref, last, de, df, src in TAB_ROWS:
        d = dec.get(ue, 0)
        if last is None:
            cells = (f'<td class="na">&#8212;</td><td class="na">&#8212;</td>'
                     f'<td class="na">&#8212;</td>')
        else:
            rc = (f'<td class="n">{bil(ge(ref,d),gr(ref,d))}</td>' if ref is not None
                  else '<td class="na">&#8212;</td>')
            v = pct(ref, last) if ref is not None else None
            vc = ('<td class="n">' +
                  bil(("+" if v > 0 else "&#8722;") + ge(abs(v), 1),
                      ("+" if v > 0 else "&#8722;") + gr(abs(v), 1)) + "</td>"
                  ) if v is not None else '<td class="na">&#8212;</td>'
            cells = rc + f'<td class="n"><b>{bil(ge(last,d),gr(last,d))}</b></td>' + vc
        rows.append(f'<tr><th scope="row">{bil(ne,nf)}</th>'
                    f'<td class="pv">{bil(ue,uf)}</td>{cells}'
                    f'<td class="src">{bil(de,df)}</td></tr>')
    return "".join(h) + "".join(rows) + "</tbody></table></div>"


reg("prix-synthese", "Commodity price monitor", "Tableau de bord des cours",
    "World Bank Pink Sheet, Fastmarkets, press",
    ["Commodity", "Unit", "2025 average", "Latest", "Change, %", "As at"],
    [[ne, ue, ref if ref is not None else "", last if last is not None else "",
      round(pct(ref, last), 1) if (ref is not None and last is not None) else "", de]
     for ne, nf, ue, uf, ref, last, de, df, src in TAB_ROWS])


# =============================================================== bandeau d'indicateurs
MOIS_EN = ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]
MOIS_FR = ["janvier", "f&#233;vrier", "mars", "avril", "mai", "juin",
           "juillet", "ao&#251;t", "septembre", "octobre", "novembre", "d&#233;cembre"]


def date_bil(iso):
    """2026-06-24 -> ('24 June 2026', '24 juin 2026')."""
    p = iso.split("-")
    y, m = p[0], int(p[1])
    if len(p) < 3:
        return f"{MOIS_EN[m-1]} {y}", f"{MOIS_FR[m-1]} {y}"
    d = int(p[2])
    return f"{d} {MOIS_EN[m-1]} {y}", f"{d} {MOIS_FR[m-1]} {y}"


def build_kpi():
    """Reconstruit le bandeau a partir des donnees, pour que l'actualisation soit mecanique."""
    def var(key, dec, unit):
        ref, last = D[key][2], D[key][-1]
        v = (last / ref - 1.0) * 100.0
        sg = "+" if v >= 0 else "&#8722;"
        return (bil(ge(last, dec) + M.NBSP + unit, gr(last, dec) + M.NBSP + unit),
                bil(sg + ge(abs(v), 1) + M.NBSP + "% on 2025",
                    sg + gr(abs(v), 1) + M.NBSP + "% sur 2025"))

    hyd = [r for r in HORS["cobalt"] if r[1] == "Hydroxide"][-1]
    hde, hdf = date_bil(hyd[0])
    col = HORS["coltan"][-1]
    cde, cdf = date_bil(col[0])

    items = []
    val, chg = var("copper", 0, "$/t")
    items.append((bil("Copper", "Cuivre"), val, chg))
    items.append((bil("Cobalt hydroxide", "Hydroxyde de cobalt"),
                  bil(ge(hyd[3], 2) + M.NBSP + "$/lb", gr(hyd[3], 2) + M.NBSP + "$/lb"),
                  bil(hde, hdf)))
    val, chg = var("gold", 0, "$/oz")
    items.append((bil("Gold", "Or"), val, chg))
    val, chg = var("tin", 0, "$/t")
    items.append((bil("Tin", "&#201;tain"), val, chg))
    items.append((bil("Tantalite", "Tantalite"),
                  bil(ge(col[1], 0) + M.NBSP + "$/lb", gr(col[1], 0) + M.NBSP + "$/lb"),
                  bil(cde, cdf)))
    val, chg = var("brent", 1, "$/bbl")
    items.append((bil("Brent crude, an import", "Brent, une importation"), val, chg))

    out = ['<dl class="macro-now">']
    for lab, val, chg in items:
        out.append(f'\n        <div><dt>{lab}</dt><dd><b>{val}</b> '
                   f'<span class="when">{chg}</span></dd></div>')
    out.append("\n      </dl>")
    return "".join(out)


# ======================================================= historique complet
# Le classeur mensuel de la Banque mondiale remonte a 1960. refresh_data.py y
# preleve tout : chaque mois, chaque trimestre, chaque annee pleine. On ne
# tronque rien ; ces trois tableaux ne sont pas dessines, ils sont offerts au
# telechargement. Tant que l'actualisation nocturne n'a pas tourne, la section
# n'existe pas et les boutons ne sont pas ecrits.
HIST = _J.get("historique") if os.path.exists(_RAW) else None


def build_hist():
    if not HIST or not HIST.get("mois"):
        return ""
    plans = [
        ("prix-hist-mensuel", "mois",
         "Commodity prices, complete monthly history",
         "Cours des mati&#232;res premi&#232;res, historique mensuel complet",
         "Month", "Mois", "Monthly", "Mensuel"),
        ("prix-hist-trimestriel", "trim",
         "Commodity prices, complete quarterly history",
         "Cours des mati&#232;res premi&#232;res, historique trimestriel complet",
         "Quarter", "Trimestre", "Quarterly", "Trimestriel"),
        ("prix-hist-annuel", "an",
         "Commodity prices, complete annual history",
         "Cours des mati&#232;res premi&#232;res, historique annuel complet",
         "Year", "Ann&#233;e", "Annual", "Annuel"),
    ]
    barres, comptes = [], []
    for cle, champ, ne, nf, pe, pf, be, bf in plans:
        lignes = HIST.get(champ) or []
        if not lignes:
            continue
        reg(cle, ne, nf,
            "World Bank, Commodity Markets Outlook, monthly historical workbook",
            [[pe, pf]] + [[a, b] for a, b in zip(HIST["cols_en"], HIST["cols_fr"])],
            lignes)
        barres.append(
            f'<div class="dlbar" data-series="{cle}">'
            f'<span class="dlname">{bil(be, bf)}</span>'
            f'<button type="button" class="dl" data-fmt="csv">CSV</button>'
            f'<button type="button" class="dl" data-fmt="xlsx">XLSX</button></div>')
        comptes.append((be, bf, len(lignes)))
    if not barres:
        return ""
    det_en = ", ".join("%s %s observations" % (ge(n), b.lower())
                       for b, _f, n in comptes)
    det_fr = ", ".join("%s observations %ss" % (gr(n), f.lower())
                       for _b, f, n in comptes)
    return ('<div class="histbar"><p class="stamp">'
            + bil("Complete history, nothing truncated: " + det_en
                  + ". Rebuilt every night from the World Bank workbook.",
                  "Historique complet, sans troncature&#8239;: " + det_fr
                  + ". Reconstruit chaque nuit &#224; partir du classeur de la "
                    "Banque mondiale.")
            + "</p>" + "".join(barres) + "</div>")


open("prix_kpi.html", "w", encoding="utf-8").write(build_kpi())

open("prix_figs.html", "w", encoding="utf-8").write("\n".join(FIGS))
open("prix_tab.html", "w", encoding="utf-8").write(build_tab() + build_hist())
json.dump(SERIES, open("series_prix.json", "w", encoding="utf-8"), ensure_ascii=False)
print("figures :", len(FIGS), "| series :", list(SERIES))
