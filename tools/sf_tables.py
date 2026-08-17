#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Les tableaux de faits stylises de l'economie congolaise.

Deux tableaux accompagnent les planches produites par sf_prepare.py.

Le premier est le tableau de moments du cycle : pour chaque agregat, on
donne l'ecart-type de la composante cyclique, sa volatilite rapportee a
celle de la production, l'autocorrelation d'ordre un et la correlation
contemporaine avec la production. C'est la forme sous laquelle un modele
d'equilibre general se confronte aux donnees.

Le second rassemble les traits de structure : concentration des
exportations, dependance des recettes publiques aux mines, dollarisation
des depots, acces au systeme bancaire.

Le script ecrit les deux tableaux dans le registre des series de la page,
de sorte que les boutons de telechargement existants les servent en CSV,
en XLSX et en LaTeX booktabs sans aucune ligne de code supplementaire, et
les rend en HTML dans la zone SF:TAB de index.html.

Bibliotheque standard seulement.
"""

import html
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sf_prepare as sf                                          # noqa: E402


def _index():
    """Le fichier de la page, selon que le depot est a plat ou non."""
    for c in (os.path.join(RACINE, "index.html"),
              os.path.join(RACINE, "site", "index.html")):
        if os.path.exists(c):
            return c
    return os.path.join(RACINE, "index.html")


INDEX = _index()
DONNEES = os.path.join(RACINE, "data")
CSV = os.path.join(DONNEES, "csv")

DEBUT, FIN = "<!-- SF:TAB:START -->", "<!-- SF:TAB:END -->"

# Garde-fou : aucun numero de telephone ne doit reparaitre dans la page.
# L'expression ne contient elle-meme aucun chiffre de numero.
_TEL = re.compile(r"(?:tel:|\+\s?1[\s.\-]?)\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}")

# Les agregats retenus, dans l'ordre ou on les lit habituellement.
SUITE = [
    ("GDP",             "Output",              "Production"),
    ("Consumption",     "Consumption",         "Consommation"),
    ("Investment",      "Investment",          "Investissement"),
    ("Hours",           "Hours worked",        "Heures travaillées"),
    ("Exports",         "Exports",             "Exportations"),
    ("Imports",         "Imports",             "Importations"),
    ("CPI",             "Consumer prices",     "Prix à la consommation"),
    ("M2",              "Broad money",         "Masse monétaire M2"),
    ("ExchangeRate",    "Exchange rate",       "Taux de change"),
    ("Reserves",        "Foreign reserves",    "Réserves de change"),
    ("CopperPrice",     "Copper price",        "Prix du cuivre"),
    ("GovtRevenue",     "Public revenue",      "Recettes publiques"),
    ("GovtExpenditure", "Public spending",     "Dépenses publiques"),
]


# ----------------------------------------------------------------------
# Statistiques
# ----------------------------------------------------------------------
def moyenne(v):
    return sum(v) / float(len(v)) if v else 0.0


def ecart_type(v):
    if len(v) < 2:
        return 0.0
    m = moyenne(v)
    return (sum((x - m) ** 2 for x in v) / float(len(v) - 1)) ** 0.5


def correlation(x, y):
    n = min(len(x), len(y))
    if n < 3:
        return None
    mx, my = moyenne(x[:n]), moyenne(y[:n])
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dx = sum((x[i] - mx) ** 2 for i in range(n)) ** 0.5
    dy = sum((y[i] - my) ** 2 for i in range(n)) ** 0.5
    if dx <= 0 or dy <= 0:
        return None
    return num / (dx * dy)


def autocorrelation(v, k=1):
    return correlation(v[k:], v[:-k]) if len(v) > k + 2 else None


def cycle_de(serie, en_taux):
    """Composante cyclique, en pourcentage.

    Les series de niveau positives sont d'abord portees en logarithme :
    l'ecart au trend s'y lit alors directement en pourcentage. Les series
    deja exprimees en taux sont filtrees telles quelles, et l'ecart se lit
    en points de pourcentage.
    """
    v = list(serie)
    if not en_taux and all(x > 0 for x in v):
        import math
        v = [100.0 * math.log(x) for x in v]
    return sf.hp(v)


# ----------------------------------------------------------------------
# Les deux tableaux
# ----------------------------------------------------------------------
def tableau_moments(dates, cols):
    """Volatilite, persistance et co-mouvement, sur la composante cyclique."""
    if "GDP" not in cols or len(dates) < 36:
        return None
    cycles = {}
    for cle, _, _ in SUITE:
        if cle in cols:
            cycles[cle] = cycle_de(cols[cle], cle in sf.TAUX)
    if "GDP" not in cycles:
        return None
    ref = ecart_type(cycles["GDP"])

    rows = []
    for cle, en, fr in SUITE:
        c = cycles.get(cle)
        if not c:
            continue
        s = ecart_type(c)
        rel = (s / ref) if ref > 0 else None
        rho = autocorrelation(c, 1)
        cor = correlation(c, cycles["GDP"])
        rows.append([[en, fr],
                     round(s, 2),
                     "—" if rel is None else round(rel, 2),
                     "—" if rho is None else round(rho, 2),
                     "—" if cor is None else round(cor, 2)])
    if len(rows) < 5:
        return None

    debut, fin = dates[0], dates[-1]
    return {
        "name_en": "Business cycle moments, DR Congo",
        "name_fr": "Moments du cycle économique, RD Congo",
        "source": "Banque centrale du Congo, Banque mondiale, FMI ; "
                  "calculs de l\u2019auteur.",
        "note_en": ("Cyclical components from a Hodrick-Prescott filter with "
                    "lambda = 14400, on monthly data from %s to %s. Level "
                    "series are taken in logarithms, so the standard "
                    "deviation reads as a percentage; rate series are "
                    "filtered as they stand and the standard deviation reads "
                    "in percentage points. The real aggregates (output, "
                    "consumption, investment, hours) are published annually "
                    "and interpolated to a monthly frequency, so their "
                    "measured autocorrelation is an upper bound and should "
                    "be read as one." % (debut, fin)),
        "note_fr": ("Composantes cycliques obtenues par filtre "
                    "Hodrick-Prescott, lambda = 14400, sur données mensuelles "
                    "de %s à %s. Les séries de niveau sont portées en "
                    "logarithme, de sorte que l\u2019écart-type se lit en "
                    "pourcentage ; les séries de taux sont filtrées en "
                    "l\u2019état et l\u2019écart-type se lit en points de "
                    "pourcentage. Les agrégats réels (production, "
                    "consommation, investissement, heures) sont publiés à "
                    "fréquence annuelle puis mensualisés par interpolation ; "
                    "leur autocorrélation mesurée constitue donc une borne "
                    "supérieure et doit se lire comme telle."
                    % (debut, fin)),
        "chiffres": [2, 2, 2, 2],
        "cols": [["Series", "Série"],
                 ["Std. dev., %", "Écart-type, %"],
                 ["Relative to output", "Rapporté à la production"],
                 ["Autocorr. (1)", "Autocorr. (1)"],
                 ["Corr. with output", "Corr. avec la production"]],
        "rows": rows,
    }


def _en_log(serie, en_taux):
    """La serie sous la forme ou on la filtre : log fois cent, ou telle quelle."""
    v = list(serie)
    if not en_taux and all(x > 0 for x in v):
        import math
        return [100.0 * math.log(x) for x in v]
    return v


def _appariees(a, b):
    """Les deux series reduites aux dates ou l'une et l'autre sont definies."""
    couples = [(u, v) for u, v in zip(a, b) if u is not None and v is not None]
    return [u for u, _ in couples], [v for _, v in couples]


def tableau_filtres(dates, cols):
    """Les memes faits stylises, vus par cinq filtres differents.

    L'objet du tableau n'est pas de departager les filtres mais de montrer
    ce qui tient malgre eux. La volatilite relative de l'investissement et
    le signe des correlations ne dependent pas du filtre ; la persistance,
    elle, en depend entierement, ce que la note dit sans detour.
    """
    besoin = ("GDP", "Consumption", "Investment")
    if any(c not in cols for c in besoin) or len(dates) < 60:
        return None
    bases = dict((c, _en_log(cols[c], c in sf.TAUX)) for c in besoin)

    rows = []
    for cle, (nom_en, nom_fr), filtre, _ in sf.FILTRES:
        cyc = dict((c, filtre(bases[c])) for c in besoin)
        pib = [v for v in cyc["GDP"] if v is not None]
        if len(pib) < 36:
            continue
        s = ecart_type(pib)
        ligne = [[nom_en, nom_fr], round(s, 2)]
        for c in ("Consumption", "Investment"):
            x, y = _appariees(cyc[c], cyc["GDP"])
            sx = ecart_type(x)
            ligne.append("—" if s <= 0 or not x else round(sx / ecart_type(y), 2))
        for c in ("Consumption", "Investment"):
            x, y = _appariees(cyc[c], cyc["GDP"])
            r = correlation(x, y)
            ligne.append("—" if r is None else round(r, 2))
        rho = autocorrelation(pib, 1)
        ligne.append("—" if rho is None else round(rho, 2))
        rows.append(ligne)
    if len(rows) < 3:
        return None

    debut, fin = dates[0], dates[-1]
    return {
        "name_en": "The stylised facts under five filters",
        "name_fr": "Les faits stylisés vus par cinq filtres",
        "source": "Banque centrale du Congo, Banque mondiale, FMI ; "
                  "calculs de l’auteur.",
        "note_en": (
            "Monthly data from %s to %s, level series in logarithms. Each row "
            "applies one filter to output, consumption and investment, then "
            "measures the same four moments. The smoothing parameter of the "
            "Hodrick-Prescott filter is 14400, the monthly counterpart of the "
            "1600 used on quarterly data under the rule of Ravn and Uhlig, "
            "which scales lambda with the fourth power of the observation "
            "frequency. The Hamilton regression projects the series two years "
            "ahead on twelve monthly lags, the transposition of the h = 8, "
            "p = 4 that Hamilton recommends for quarterly data. The two band "
            "pass filters isolate cycles of eighteen to ninety-six months, the "
            "range Burns and Mitchell gave the business cycle; the "
            "Baxter-King filter truncates its weights at thirty-six months and "
            "therefore loses three years at each end of the sample, while the "
            "Christiano-Fitzgerald filter keeps every month at the cost of "
            "weights that vary with the position in the sample. Correlations "
            "and relative volatilities are computed on the months where both "
            "series are defined. What survives the choice of filter is the "
            "shape of the cycle rather than its size: the standard deviation "
            "of output ranges from a quarter of a point to two and a half "
            "points depending on the filter, while investment stays between "
            "two and a half and three and a half times as volatile as output, "
            "consumption stays smoother than output, and both stay strongly "
            "procyclical. The autocorrelation column is high under every "
            "filter, but the real aggregates are published annually and "
            "interpolated to a monthly frequency: that column measures the "
            "interpolation as much as the economy and should not be used as "
            "evidence of persistence." % (debut, fin)),
        "note_fr": (
            "Données mensuelles de %s à %s, séries de niveau en logarithme. "
            "Chaque ligne applique un filtre à la production, à la "
            "consommation et à l’investissement, puis mesure les mêmes "
            "quatre moments. Le paramètre de lissage du filtre de Hodrick et "
            "Prescott vaut 14400, la contrepartie mensuelle du 1600 retenu sur "
            "données trimestrielles selon la règle de Ravn et Uhlig, qui fait "
            "varier lambda comme la puissance quatre de la fréquence "
            "d’observation. La régression de Hamilton projette la série à "
            "deux ans sur douze retards mensuels, transposition du couple "
            "h = 8, p = 4 que Hamilton recommande au trimestre. Les deux "
            "filtres passe-bande isolent les cycles de dix-huit à "
            "quatre-vingt-seize mois, l’intervalle que Burns et Mitchell "
            "assignaient au cycle des affaires ; celui de Baxter et King "
            "tronque ses poids à trente-six mois et perd donc trois ans à "
            "chaque extrémité de l’échantillon, tandis que celui de "
            "Christiano et Fitzgerald conserve tous les mois, au prix de poids "
            "qui varient avec la position dans l’échantillon. Les "
            "corrélations et les volatilités relatives sont calculées sur les "
            "mois où les deux séries sont définies. Ce qui résiste au choix du "
            "filtre est la forme du cycle, non son amplitude : l’écart-type de "
            "la production va d’un quart de point à deux points et demi selon "
            "le filtre, tandis que l’investissement reste deux fois et demie à "
            "trois fois et demie plus volatil que la production, que la "
            "consommation reste plus lisse qu’elle et que l’un et l’autre "
            "restent nettement procycliques. La colonne d’autocorrélation est "
            "élevée sous tous les filtres, mais les agrégats réels sont "
            "publiés à fréquence annuelle puis mensualisés par interpolation : "
            "cette colonne mesure l’interpolation autant que l’économie et ne "
            "saurait servir de preuve de persistance." % (debut, fin)),
        "chiffres": [2, 2, 2, 2, 2, 2],
        "cols": [["Filter", "Filtre"],
                 ["Output std. dev., %", "Écart-type production, %"],
                 ["Cons. / output", "Consommation / production"],
                 ["Invest. / output", "Investissement / production"],
                 ["Corr. cons.-output", "Corr. consommation-production"],
                 ["Corr. invest.-output", "Corr. investissement-production"],
                 ["Autocorr. (1)", "Autocorr. (1)"]],
        "rows": rows,
    }


def tableau_structure():
    """Les traits de structure, tels que les rapports officiels les donnent."""
    rows = [
        [["Mining, share of goods exports", "Mines, part des exportations de biens"],
         98.9, ["IMF Article IV", "FMI, article IV"]],
        [["Mining, share of fiscal revenue", "Mines, part des recettes fiscales"],
         46.0, ["EITI-DRC", "ITIE-RDC"]],
        [["Cobalt, share of world output", "Cobalt, part de la production mondiale"],
         76.0, ["USGS", "USGS"]],
        [["Bank deposits held in foreign currency",
          "Dépôts bancaires en devises"],
         90.9, ["IMF Article IV", "FMI, article IV"]],
        [["Adults with an account at a financial institution",
          "Adultes disposant d\u2019un compte bancaire"],
         26.0, ["Global Findex", "Global Findex"]],
    ]
    return {
        "name_en": "Structural features of the Congolese economy",
        "name_fr": "Traits de structure de l\u2019économie congolaise",
        "source": "FMI, ITIE-RDC, USGS, Global Findex.",
        "note_en": ("Each line refers to the official publication cited "
                    "beside it. The first four describe one and the same "
                    "dependence, seen from external trade, from the budget, "
                    "from the world market and from the banking system; the "
                    "fifth measures what limits the transmission of monetary "
                    "policy."),
        "note_fr": ("Chaque ligne renvoie à la publication officielle citée "
                    "en regard. Les quatre premières décrivent une seule et "
                    "même dépendance, vue du commerce extérieur, du budget, "
                    "du marché mondial et du système bancaire ; la cinquième "
                    "mesure ce qui limite la transmission de la politique "
                    "monétaire."),
        "chiffres": [1],
        "cols": [["Feature", "Trait"],
                 ["Share, %", "Part, %"],
                 ["Source", "Source"]],
        "rows": rows,
    }


# ----------------------------------------------------------------------
# Rendu
# ----------------------------------------------------------------------
def bilingue(en, fr):
    return ('<span class="l-en">%s</span>'
            '<span class="l-fr" lang="fr">%s</span>'
            % (html.escape(str(en), quote=False),
               html.escape(str(fr), quote=False)))


def cellule(v, chiffres=2):
    """Rend une case : bilingue si c'est une paire, numerique si c'est un
    nombre, tiret cadratin si la valeur manque. Le nombre de decimales est
    fixe par colonne, de sorte que la colonne s'aligne sur la virgule."""
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return '<td>%s</td>' % bilingue(v[0], v[1])
    if isinstance(v, (int, float)):
        en = "%.*f" % (chiffres, v)
        return '<td class="n">%s</td>' % bilingue(en, en.replace(".", ","))
    if v in ("—", "", None):
        return '<td class="na">&#8212;</td>'
    return '<td>%s</td>' % html.escape(str(v))


AUTEUR = "James Wabenga Yango"


def credit(fiche):
    """La note de pied de tableau : qui l'a compose, sur quelles donnees."""
    src = str(fiche.get("source") or "").strip().rstrip(".")
    en = "Table compiled by %s." % AUTEUR
    fr = "Tableau composé par %s." % AUTEUR
    if src:
        en += " Source: " + src + "."
        fr += " Source : " + src + "."
    return ('<span class="l-en">%s</span>'
            '<span class="l-fr" lang="fr">%s</span>'
            ' <a class="citelink" href="#citer">'
            '<span class="l-en">How to cite</span>'
            '<span class="l-fr" lang="fr">Comment citer</span></a>'
            % (html.escape(en, quote=False), html.escape(fr, quote=False)))


def rend(cle, fiche):
    entetes = "".join('<th scope="col">%s</th>' % bilingue(c[0], c[1])
                      for c in fiche["cols"])
    lignes = []
    for r in fiche["rows"]:
        tete = r[0]
        th = '<th scope="row">%s</th>' % (
            bilingue(tete[0], tete[1]) if isinstance(tete, (list, tuple))
            else html.escape(str(tete)))
        dec = fiche.get("chiffres") or []
        lignes.append("<tr>" + th + "".join(
            cellule(v, dec[i] if i < len(dec) else 2)
            for i, v in enumerate(r[1:])) + "</tr>")
    return (
        '<figure class="sftab" id="tab-%s">'
        '<figcaption>%s</figcaption>'
        '<div class="tablewrap"><table class="macro-tab">'
        '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
        '<p class="note">%s</p>'
        '<p class="tabsource">%s</p>'
        '<div class="dlbar" data-series="%s">'
        '<button type="button" class="dl" data-fmt="csv">CSV</button>'
        '<button type="button" class="dl" data-fmt="xlsx">XLSX</button>'
        '</div></figure>'
        % (cle, bilingue(fiche["name_en"], fiche["name_fr"]),
           entetes, "".join(lignes),
           bilingue(fiche.get("note_en") or fiche.get("note") or "",
                    fiche.get("note_fr") or fiche.get("note") or ""),
           credit(fiche), cle))


def ecrit_csv(cle, fiche):
    """Depose aussi le tableau en CSV a cote des autres series."""
    import csv as _csv
    os.makedirs(CSV, exist_ok=True)
    chemin = os.path.join(CSV, cle + ".csv")
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = _csv.writer(f)
        w.writerow([c[0] for c in fiche["cols"]])
        for r in fiche["rows"]:
            w.writerow([v[0] if isinstance(v, (list, tuple)) else v for v in r])
    return chemin


def main():
    if not os.path.exists(INDEX):
        print("index.html introuvable :", INDEX)
        return 1

    dates, cols = sf.socle_mensuel()
    sf.prolonge_par_le_site(dates, cols)

    fiches = {}
    m = tableau_moments(dates, cols)
    if m:
        fiches["sf-moments"] = m
    f = tableau_filtres(dates, cols)
    if f:
        fiches["sf-filtres-tab"] = f
    else:
        print("  filtres : donnees insuffisantes, tableau ecarte")
    fiches["sf-structure-tab"] = tableau_structure()
    if "sf-moments" not in fiches:
        print("  moments : donnees insuffisantes, tableau ecarte")

    page = open(INDEX, encoding="utf-8").read()
    a, b = page.find(DEBUT), page.find(FIN)
    if a < 0 or b < 0 or b < a:
        print("Zone %s absente de index.html." % DEBUT)
        return 1

    # 1. Le registre des series, pour que les boutons servent les fichiers.
    mreg = re.search(r'(<!-- SERIES:START --><script type="application/json" '
                     r'id="series-data">)(.*?)(</script><!-- SERIES:END -->)',
                     page, re.S)
    if mreg:
        reg = json.loads(mreg.group(2))
        reg.update(fiches)
        page = (page[:mreg.start()] + mreg.group(1)
                + json.dumps(reg, ensure_ascii=False, separators=(",", ":"))
                + mreg.group(3) + page[mreg.end():])
        a, b = page.find(DEBUT), page.find(FIN)
        print("  registre : %d series au total" % len(reg))
    else:
        print("  registre des series introuvable, telechargements inchanges")

    # 2. Le rendu HTML des tableaux.
    neuf = "".join(rend(cle, fiches[cle])
                   for cle in ("sf-moments", "sf-filtres-tab",
                               "sf-structure-tab")
                   if cle in fiches)
    page = page[:a + len(DEBUT)] + neuf + page[b:]

    if _TEL.search(page):
        print("Garde-fou : un numero de telephone apparait dans la page, "
              "ecriture annulee.")
        return 1

    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(page)

    # 3. Les fichiers CSV, pour qui prefere les prendre directement au depot.
    for cle, fiche in fiches.items():
        ecrit_csv(cle, fiche)

    # Le registre des series est aussi tenu a jour sur le disque.
    p = os.path.join(DONNEES, "series.json")
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            d.update(fiches)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
        except Exception as e:                                   # noqa: BLE001
            print("  series.json non mis a jour :", e)

    print("%d tableaux de faits stylises publies." % len(fiches))
    return 0


if __name__ == "__main__":
    sys.exit(main())
