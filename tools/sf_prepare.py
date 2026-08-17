#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepare les planches de faits stylises de l'economie congolaise.

Le socle est data/drc-mensuel.csv, les dix-sept series mensuelles qui
servent au modele DSGE (janvier 2013 a aujourd'hui). Il est prolonge par
les series longues du site, data/series.json et data/macro-rdc.json, que
l'actualisation nocturne rafraichit. Chaque planche sort d'ici sous forme
d'un CSV en forme longue, pret pour ggplot2, et d'une fiche dans le plan.

Les planches suivent celles du dossier MODEL_DSGE_RDC : niveaux en
facettes avec episodes de tension grises, composantes cycliques, traits
de structure, composition des exportations. S'y ajoutent le cycle reel
par regime politique, les secteurs porteurs et les vulnerabilites.

Aucune dependance : la bibliotheque standard suffit. Le filtre
Hodrick-Prescott est resolu directement, par elimination de Gauss sur la
matrice pentadiagonale du probleme, ce qui evite d'installer numpy sur le
serveur d'integration.
"""

import csv
import html
import json
import math
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DONNEES = os.path.join(RACINE, "data")
SORTIE = os.path.join(RACINE, "build", "gg")

PINE = "#002147"
BRASS = "#8A6A18"
SAGE = "#3F6B52"
BRIQUE = "#8C2F27"
PRUNE = "#5B3A6B"
ARDOISE = "#4A5A6A"

# Episodes de tension macroeconomique, tels que retenus dans le papier.
TENSIONS = [("2015-09", "2016-12"), ("2020-03", "2020-12"), ("2023-06", "2024-06")]


# ----------------------------------------------------------------------
# Petits utilitaires
# ----------------------------------------------------------------------
def texte(v):
    return html.unescape(str(v)) if v is not None else ""


def nombre(v):
    """Convertit en flottant ce qui peut l'etre, sinon rend None."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip()
    if not t or t.upper() in ("NA", "NAN", "NULL", "-", "—"):
        return None
    t = (t.replace(" ", "").replace(" ", "").replace(" ", "")
          .replace("−", "-").replace("%", ""))
    if "," in t and "." not in t:
        t = t.replace(",", ".")
    else:
        t = t.replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None


def charge(nom):
    chemin = os.path.join(DONNEES, nom)
    if not os.path.exists(chemin):
        return None
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def charge_csv(nom):
    chemin = os.path.join(DONNEES, nom)
    if not os.path.exists(chemin):
        return []
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def ecrit_csv(nom, entetes, lignes):
    os.makedirs(SORTIE, exist_ok=True)
    chemin = os.path.join(SORTIE, nom)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(entetes)
        w.writerows(lignes)
    return nom


def mois_suivant(iso):
    a, m = int(iso[:4]), int(iso[5:7])
    return "%04d-%02d" % (a + (m == 12), 1 if m == 12 else m + 1)


# ----------------------------------------------------------------------
# Le filtre de Hodrick et Prescott, resolu sans numpy
# ----------------------------------------------------------------------
def hp(serie, lam=14400.0):
    """Rend la composante cyclique, en points de la serie fournie.

    Le probleme se ramene au systeme (I + lam * K'K) tau = y, dont la
    matrice est symetrique, definie positive et pentadiagonale. Une
    factorisation de Cholesky en bande le resout en O(n).
    """
    y = [v for v in serie]
    n = len(y)
    if n < 5:
        return [0.0] * n

    # bandes de A = I + lam K'K, indexees par decalage 0, 1 et 2
    d0 = [0.0] * n
    d1 = [0.0] * (n - 1)
    d2 = [0.0] * (n - 2)
    for i in range(n):
        d0[i] = 1.0
    for t in range(n - 2):          # une ligne de K par triplet (t, t+1, t+2)
        for (i, ci) in ((t, 1.0), (t + 1, -2.0), (t + 2, 1.0)):
            for (j, cj) in ((t, 1.0), (t + 1, -2.0), (t + 2, 1.0)):
                if i == j:
                    d0[i] += lam * ci * cj
                elif j == i + 1:
                    d1[i] += lam * ci * cj
                elif j == i + 2:
                    d2[i] += lam * ci * cj

    # Cholesky en bande : A = L L', L de demi-largeur 2
    l0 = [0.0] * n
    l1 = [0.0] * (n - 1)
    l2 = [0.0] * (n - 2)
    for i in range(n):
        s = d0[i]
        if i >= 1:
            s -= l1[i - 1] ** 2
        if i >= 2:
            s -= l2[i - 2] ** 2
        if s <= 0:
            return [0.0] * n
        l0[i] = math.sqrt(s)
        if i + 1 < n:
            s = d1[i]
            if i >= 1:
                s -= l1[i - 1] * l2[i - 1]
            l1[i] = s / l0[i]
        if i + 2 < n:
            l2[i] = d2[i] / l0[i]

    # descente puis remontee
    z = [0.0] * n
    for i in range(n):
        s = y[i]
        if i >= 1:
            s -= l1[i - 1] * z[i - 1]
        if i >= 2:
            s -= l2[i - 2] * z[i - 2]
        z[i] = s / l0[i]
    tau = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = z[i]
        if i + 1 < n:
            s -= l1[i] * tau[i + 1]
        if i + 2 < n:
            s -= l2[i] * tau[i + 2]
        tau[i] = s / l0[i]

    return [y[i] - tau[i] for i in range(n)]


# ----------------------------------------------------------------------
# Les autres filtres : Hamilton, Baxter-King, Christiano-Fitzgerald,
# difference premiere. Aucun ne demande numpy.
#
# Le choix des parametres est celui de la litterature, transpose au pas
# mensuel et justifie dans la page :
#   - HP : lambda = 14400 au mois (Backus et Kehoe), 1600 au trimestre,
#     129600 dans la variante de Ravn et Uhlig, qui fait varier lambda
#     comme la puissance quatre de la frequence d'observation ;
#   - Hamilton (2018) : horizon h = 24 mois, soit deux ans, et p = 12
#     retards, soit une annee, ce qui est la transposition mensuelle du
#     couple (h = 8, p = 4) recommande pour des donnees trimestrielles ;
#   - Baxter-King et Christiano-Fitzgerald : bande de 18 a 96 mois, soit
#     un an et demi a huit ans, la definition de Burns et Mitchell ;
#     troncature K = 36 mois pour Baxter-King, qui coute trois ans a
#     chaque extremite de l'echantillon.
# ----------------------------------------------------------------------
HAM_H, HAM_P = 24, 12
BANDE_BASSE, BANDE_HAUTE, BK_K = 18, 96, 36


def _resout(A, b):
    """Elimination de Gauss avec pivot partiel ; rend None si singuliere."""
    n = len(b)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda i: abs(M[i][c]))
        if abs(M[p][c]) < 1e-12:
            return None
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        for i in range(c + 1, n):
            f = M[i][c] / piv
            if f:
                for j in range(c, n + 1):
                    M[i][j] -= f * M[c][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = s / M[i][i]
    return x


def hamilton(serie, h=HAM_H, p=HAM_P):
    """Le filtre de regression de Hamilton (2018).

    On regresse la valeur observee h periodes plus tard sur une constante
    et sur p valeurs consecutives connues aujourd'hui ; le residu est le
    cycle. La regression ne suppose aucune tendance et n'engendre pas les
    dynamiques parasites que Hamilton reproche au filtre de Hodrick et
    Prescott.

    Le cycle n'est defini qu'a partir de la periode h + p - 1 : les
    premieres periodes recoivent None, que le traceur ignore.
    """
    y = list(serie)
    n = len(y)
    if n < h + p + 10:
        return [None] * n
    lignes, cible = [], []
    for t in range(h + p - 1, n):
        lignes.append([1.0] + [y[t - h - j] for j in range(p)])
        cible.append(y[t])
    k = p + 1
    A = [[sum(l[i] * l[j] for l in lignes) for j in range(k)] for i in range(k)]
    b = [sum(lignes[m][i] * cible[m] for m in range(len(cible))) for i in range(k)]
    beta = _resout(A, b)
    if beta is None:
        return [None] * n
    out = [None] * (h + p - 1)
    for m, l in enumerate(lignes):
        out.append(cible[m] - sum(beta[i] * l[i] for i in range(k)))
    return out


def _poids_bande(j, bas, haut):
    """Le poids ideal de rang j du filtre passe-bande [bas, haut] periodes."""
    a = 2.0 * math.pi / float(haut)      # frequence basse
    b = 2.0 * math.pi / float(bas)       # frequence haute
    if j == 0:
        return (b - a) / math.pi
    return (math.sin(j * b) - math.sin(j * a)) / (j * math.pi)


def baxter_king(serie, bas=BANDE_BASSE, haut=BANDE_HAUTE, K=BK_K):
    """Le filtre passe-bande tronque et symetrique de Baxter et King (1999).

    Les poids ideaux sont tronques au rang K puis recentres pour que leur
    somme soit nulle, condition sans laquelle le filtre ne retirerait pas
    une tendance deterministe. Les K premieres et K dernieres periodes ne
    peuvent pas etre calculees : elles recoivent None.
    """
    y = list(serie)
    n = len(y)
    if n < 2 * K + 12:
        return [None] * n
    w = [_poids_bande(j, bas, haut) for j in range(K + 1)]
    theta = -(w[0] + 2.0 * sum(w[1:])) / (2.0 * K + 1.0)
    w = [v + theta for v in w]
    out = [None] * n
    for t in range(K, n - K):
        s = w[0] * y[t]
        for j in range(1, K + 1):
            s += w[j] * (y[t - j] + y[t + j])
        out[t] = s
    return out


def christiano_fitzgerald(serie, bas=BANDE_BASSE, haut=BANDE_HAUTE,
                          derive=True):
    """Le filtre passe-bande asymetrique de Christiano et Fitzgerald (2003).

    Le filtre est optimal sous l'hypothese que la serie suit une marche
    aleatoire ; il mobilise tout l'echantillon a chaque date, si bien
    qu'aucune periode n'est perdue, au prix de poids qui changent avec la
    position dans l'echantillon. La derive est retiree au prealable.
    """
    y = list(serie)
    n = len(y)
    if n < 24:
        return [None] * n
    if derive and n > 1:
        pente = (y[-1] - y[0]) / float(n - 1)
        y = [y[i] - i * pente for i in range(n)]
    B = [_poids_bande(j, bas, haut) for j in range(n + 1)]

    def Btilde(k):
        """Le poids de bord : -B0/2 moins la somme des poids deja poses."""
        return -0.5 * B[0] - sum(B[1:k]) if k >= 1 else -0.5 * B[0]

    out = [0.0] * n
    for t in range(n):
        s = B[0] * y[t]
        for j in range(1, n - t - 1):
            s += B[j] * y[t + j]
        s += Btilde(n - t - 1) * y[n - 1]
        for j in range(1, t):
            s += B[j] * y[t - j]
        s += Btilde(t) * y[0]
        out[t] = s
    return out


def difference_premiere(serie):
    """Le cycle le plus simple : la variation d'une periode a l'autre."""
    y = list(serie)
    return [None] + [y[i] - y[i - 1] for i in range(1, len(y))]


# Le repertoire des filtres, dans l'ordre ou la page les presente.
FILTRES = [
    ("hp", ("Hodrick-Prescott, λ = 14400",
            "Hodrick et Prescott, λ = 14400"),
     lambda v: hp(v, 14400.0), PINE),
    ("hamilton", ("Hamilton regression, h = 24, p = 12",
                  "Régression de Hamilton, h = 24, p = 12"),
     hamilton, BRIQUE),
    ("bk", ("Baxter-King band pass, 18-96 months",
            "Passe-bande de Baxter et King, 18-96 mois"),
     baxter_king, SAGE),
    ("cf", ("Christiano-Fitzgerald band pass, 18-96 months",
            "Passe-bande de Christiano et Fitzgerald, 18-96 mois"),
     christiano_fitzgerald, BRASS),
    ("diff", ("First difference", "Différence première"),
     difference_premiere, PRUNE),
]


def correlations_croisees(x, y, retards=12):
    """Correlations de x avec y decale de k periodes, k de -retards a +retards."""
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    mx = sum(x) / n
    my = sum(y) / n
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    if sx == 0 or sy == 0:
        return []
    out = []
    for k in range(-retards, retards + 1):
        s = 0.0
        c = 0
        for t in range(n):
            u = t + k
            if 0 <= u < n:
                s += (x[t] - mx) * (y[u] - my)
                c += 1
        out.append((k, s / (sx * sy) if c > 4 else 0.0))
    return out


# ----------------------------------------------------------------------
# Le socle mensuel
# ----------------------------------------------------------------------
NOMS = {
    "CPI":             ("Consumer price index", "Indice des prix à la consommation"),
    "M2":              ("Broad money M2", "Masse monétaire M2"),
    "Reserves":        ("Gross reserves", "Réserves brutes"),
    "ExchangeRate":    ("Exchange rate, CDF per USD", "Taux de change, CDF pour un USD"),
    "CopperPrice":     ("Copper price", "Cours du cuivre"),
    "PolicyRate":      ("Policy rate", "Taux directeur"),
    "FedFunds":        ("US federal funds rate", "Taux des fonds fédéraux américains"),
    "TradeBalance":    ("Trade balance", "Balance commerciale"),
    "Inflation":       ("CPI inflation", "Inflation"),
    "GDP":             ("Output", "Production"),
    "Consumption":     ("Consumption", "Consommation"),
    "Investment":      ("Investment", "Investissement"),
    "Exports":         ("Exports", "Exportations"),
    "Imports":         ("Imports", "Importations"),
    "GovtRevenue":     ("Government revenue", "Recettes publiques"),
    "GovtExpenditure": ("Government expenditure", "Dépenses publiques"),
    "Hours":           ("Hours worked", "Heures travaillées"),
}

# Les taux et les soldes ne se lisent pas en logarithme.
TAUX = {"PolicyRate", "FedFunds", "Inflation", "TradeBalance",
        "GovtRevenue", "GovtExpenditure"}

# L'ordre des panneaux, choisi pour que la lecture aille du prix a l'activite.
ORDRE_PANNEAUX = ["CPI", "Inflation", "ExchangeRate", "M2", "PolicyRate",
                  "FedFunds", "Reserves", "CopperPrice", "TradeBalance",
                  "GDP", "Consumption", "Investment", "Exports", "Imports",
                  "GovtRevenue", "GovtExpenditure", "Hours"]


def socle_mensuel():
    """Rend (dates, {colonne: [valeurs]}) apres interpolation des trous."""
    lignes = charge_csv("drc-mensuel.csv")
    if not lignes:
        return [], {}
    dates = [str(r["date"])[:7] for r in lignes]
    cols = {}
    for c in lignes[0]:
        if c == "date":
            continue
        brut = [nombre(r.get(c)) for r in lignes]
        if sum(v is not None for v in brut) < 24:
            continue
        # interpolation lineaire des trous, prolongement par la valeur voisine
        connus = [i for i, v in enumerate(brut) if v is not None]
        rempli = list(brut)
        for i in range(len(brut)):
            if rempli[i] is not None:
                continue
            avant = [j for j in connus if j < i]
            apres = [j for j in connus if j > i]
            if avant and apres:
                a, b = avant[-1], apres[0]
                w = (i - a) / float(b - a)
                rempli[i] = brut[a] + w * (brut[b] - brut[a])
            elif avant:
                rempli[i] = brut[avant[-1]]
            elif apres:
                rempli[i] = brut[apres[0]]
        cols[c] = rempli
    return dates, cols


def prolonge_par_le_site(dates, cols):
    """Complete le socle avec les series du site quand elles vont plus loin.

    Le taux directeur et les reserves sont publies mensuellement par la
    Banque centrale et repris chaque nuit dans data/series.json. Lorsque
    ces series depassent la derniere date du socle, la fin est recopiee.
    """
    src = charge("series.json") or {}
    couples = [("taux-directeur", "PolicyRate"), ("reserves", "Reserves")]
    ajouts = 0
    for cle, colonne in couples:
        fiche = src.get(cle)
        if not fiche or colonne not in cols:
            continue
        points = []
        for r in fiche.get("rows") or []:
            if len(r) < 2:
                continue
            d = str(r[0]).strip()
            m = re.match(r"^(\d{4})[-/](\d{1,2})", d)
            if m:
                iso = "%s-%02d" % (m.group(1), int(m.group(2)))
            elif re.match(r"^\d{4}$", d):
                iso = d + "-12"
            else:
                continue
            v = nombre(r[1])
            if v is not None:
                points.append((iso, v))
        if not points:
            continue
        points.sort()
        connus = dict(zip(dates, cols[colonne]))
        derniere = dates[-1]
        neuf = [(d, v) for d, v in points if d > derniere]
        if not neuf:
            continue
        attendue = mois_suivant(derniere)
        for d, v in neuf:
            while attendue < d:                 # comble les mois manquants
                dates.append(attendue)
                for c in cols:
                    cols[c].append(cols[c][-1])
                attendue = mois_suivant(attendue)
            if attendue == d:
                dates.append(d)
                for c in cols:
                    cols[c].append(cols[c][-1])
                cols[colonne][-1] = v
                attendue = mois_suivant(d)
                ajouts += 1
        connus = None
    return ajouts


# ----------------------------------------------------------------------
# Les planches
# ----------------------------------------------------------------------
def fig_niveaux(dates, cols):
    """Dix-sept panneaux de niveaux, avec les episodes de tension grises."""
    if not dates:
        return None
    lignes = []
    for c in ORDRE_PANNEAUX:
        if c not in cols:
            continue
        v = cols[c]
        log = c not in TAUX and all(x > 0 for x in v)
        en, fr = NOMS.get(c, (c, c))
        if log:
            en += " (log)"
            fr += " (log)"
        for d, x in zip(dates, v):
            lignes.append([d, c, en, fr, "%.6g" % x, "1" if log else "0"])
    if not lignes:
        return None
    csvf = ecrit_csv("sf-niveaux.csv",
                     ["date", "cle", "panneau_en", "panneau_fr", "y", "log"], lignes)
    return {
        "cle": "sf-niveaux", "type": "facettes_niveaux", "csv": csvf,
        "largeur": 12.6, "hauteur": 8.6, "colonnes": 3, "bandes": TENSIONS,
        "pas_annees": 2,
        "titre_en": "Macroeconomic series of the DR Congo",
        "titre_fr": "Séries macroéconomiques de la RD Congo",
        "sous_en": "Levels, monthly, log scale where the series is positive. "
                   "Shading marks episodes of macroeconomic stress.",
        "sous_fr": "Niveaux, données mensuelles, échelle logarithmique "
                   "là où la série est positive. Les plages grisées "
                   "signalent les épisodes de tension macroéconomique.",
        "source_en": "Central Bank of the Congo, World Bank, IMF; author’s calculations.",
        "source_fr": "Banque centrale du Congo, Banque mondiale, FMI ; calculs de l’auteur.",
    }


def fig_cycles(dates, cols):
    """Composantes cycliques, filtre de Hodrick et Prescott."""
    if not dates:
        return None
    lignes = []
    for c in ORDRE_PANNEAUX:
        if c not in cols:
            continue
        v = cols[c]
        if c in TAUX:
            base = list(v)                      # deja en points de pourcentage
        elif all(x > 0 for x in v):
            base = [100.0 * math.log(x) for x in v]     # ecarts en pourcentage
        else:
            base = list(v)
        cyc = hp(base, 14400.0)
        en, fr = NOMS.get(c, (c, c))
        for d, x in zip(dates, cyc):
            lignes.append([d, c, en, fr, "%.6g" % x])
    if not lignes:
        return None
    csvf = ecrit_csv("sf-cycles.csv",
                     ["date", "cle", "panneau_en", "panneau_fr", "y"], lignes)
    return {
        "cle": "sf-cycles", "type": "facettes_cycles", "csv": csvf,
        "largeur": 12.6, "hauteur": 8.6, "colonnes": 3, "bandes": TENSIONS,
        "pas_annees": 2,
        "titre_en": "Cyclical components",
        "titre_fr": "Composantes cycliques",
        "sous_en": "Deviation from the Hodrick-Prescott trend, smoothing 14400. "
                   "Rates in percentage points, other series in per cent.",
        "sous_fr": "Écart à la tendance de Hodrick et Prescott, lissage "
                   "14400. Les taux sont en points de pourcentage, les autres "
                   "séries en pourcentage.",
        "source_en": "Central Bank of the Congo, World Bank, IMF; author’s calculations.",
        "source_fr": "Banque centrale du Congo, Banque mondiale, FMI ; calculs de l’auteur.",
    }


def fig_xcorr(dates, cols):
    """Correlations croisees de la production avec les autres cycles."""
    if "GDP" not in cols:
        return None
    ref = hp([100.0 * math.log(x) for x in cols["GDP"]], 14400.0)
    choix = ["Consumption", "Investment", "Exports", "Imports",
             "ExchangeRate", "CopperPrice", "Inflation", "PolicyRate"]
    lignes = []
    for c in choix:
        if c not in cols:
            continue
        v = cols[c]
        base = list(v) if c in TAUX else (
            [100.0 * math.log(x) for x in v] if all(x > 0 for x in v) else list(v))
        cyc = hp(base, 14400.0)
        en, fr = NOMS.get(c, (c, c))
        for k, r in correlations_croisees(ref, cyc, 12):
            lignes.append([k, c, en, fr, "%.5f" % r])
    if not lignes:
        return None
    csvf = ecrit_csv("sf-xcorr.csv",
                     ["retard", "cle", "panneau_en", "panneau_fr", "r"], lignes)
    return {
        "cle": "sf-xcorr", "type": "barres_xcorr", "csv": csvf,
        "largeur": 12.6, "hauteur": 5.4, "colonnes": 4,
        "titre_en": "Comovement with output",
        "titre_fr": "Comouvement avec la production",
        "sous_en": "Correlation of the output cycle with each series, "
                   "the series being shifted by k months. A peak to the right "
                   "of zero means the series lags output.",
        "sous_fr": "Corrélation du cycle de la production avec chaque "
                   "série, celle-ci étant décalée de k mois. "
                   "Un sommet à droite de zéro indique une série "
                   "en retard sur la production.",
        "source_en": "Author’s calculations on the monthly series.",
        "source_fr": "Calculs de l’auteur sur les séries mensuelles.",
    }


def fig_filtres(dates, cols):
    """Le meme cycle de la production, vu par cinq filtres."""
    if not dates or "GDP" not in cols:
        return None
    base = [100.0 * math.log(x) for x in cols["GDP"]]
    lignes = []
    for cle, (en, fr), filtre, couleur in FILTRES:
        cyc = filtre(base)
        for d, x in zip(dates, cyc):
            if x is None:
                continue
            lignes.append([d, cle, en, fr, "%.6g" % x, couleur])
    if not lignes:
        return None
    csvf = ecrit_csv("sf-filtres.csv",
                     ["date", "filtre", "panneau_en", "panneau_fr", "y",
                      "couleur"], lignes)
    return {
        "cle": "sf-filtres", "type": "facettes_aires", "csv": csvf,
        "largeur": 12.0, "hauteur": 8.6, "colonnes": 1, "bandes": TENSIONS,
        "pas_annees": 1,
        "titre_en": "One cycle, five filters",
        "titre_fr": "Un cycle, cinq filtres",
        "sous_en": "Cyclical component of output, per cent of trend. The "
                   "vertical scale is free in each panel: what is read here "
                   "is the timing of the turns, not the size of the gap.",
        "sous_fr": "Composante cyclique de la production, en pourcentage "
                   "de la tendance. L’échelle verticale est libre dans chaque "
                   "panneau : ce qui se lit ici est la date des "
                   "retournements, non l’ampleur de l’écart.",
        "source_en": "Central Bank of the Congo, World Bank, IMF; author’s calculations.",
        "source_fr": "Banque centrale du Congo, Banque mondiale, FMI ; calculs de l’auteur.",
    }


# ----------------------------------------------------------------------
# Les cinq filtres, agregat par agregat
# ----------------------------------------------------------------------
# La planche precedente ne portait que la production. Elle montrait ce que
# les filtres font, non ce qu'ils donnent : or le desaccord entre eux ne se
# constate pas sur une serie, il se constate sur toutes. Une serie tres
# persistante -- l'indice des prix, la masse monetaire -- separe nettement
# Hamilton du reste ; une serie deja stationnaire -- l'inflation, le taux
# directeur -- les rapproche jusqu'a les confondre. Chaque agregat a donc
# sa planche, et les dix-sept se lisent dans un selecteur.

def base_cyclable(cle, v):
    """Rend la serie sous la forme ou le filtre doit la prendre.

    Trois cas, et un seul principe : le filtre doit travailler sur une
    grandeur dont l'ecart a la tendance se lise dans une unite constante.
    Un taux est deja en points de pourcentage et se filtre tel quel ; une
    grandeur strictement positive passe en cent fois son logarithme, de
    sorte que l'ecart se lise en pourcentage ; un solde, qui change de
    signe, n'admet pas le logarithme et se filtre dans son unite propre.
    """
    if cle in TAUX:
        return list(v), ("percentage points", "points de pourcentage")
    if all(x > 0 for x in v):
        return [100.0 * math.log(x) for x in v], ("per cent", "pourcentage")
    return list(v), ("units of the series", "unités de la série")


# La note de procede, posee une fois sous le selecteur. Elle dit ce que
# chaque filtre calcule, avec quels parametres, et ce qu'il en coute --
# notamment les mois perdus aux extremites, qui sont la premiere chose
# qu'un lecteur remarque et la derniere qu'on lui explique d'ordinaire.
NOTE_FILTRES_EN = [
    "How these panels are built. Each series is first put in the form a "
    "filter can take. A strictly positive series is replaced by a hundred "
    "times its natural logarithm, so that the deviation from trend reads "
    "directly as a percentage; a rate is already in percentage points and "
    "is filtered as it stands; a balance, which changes sign, admits no "
    "logarithm and is filtered in its own unit. The five filters are then "
    "applied to that same transformed series, and each panel shows the "
    "cyclical component one of them returns.",

    "Hodrick-Prescott. The trend is the series that minimises the sum of "
    "squared deviations from the data plus λ times the sum of squared "
    "second differences of the trend itself; the cycle is what is left. "
    "The smoothing parameter is set to λ = 14400, the monthly "
    "counterpart of the quarterly 1600 under the fourth-power rule; the "
    "plate that follows shows what other values would have decided. The "
    "filter uses the whole sample and loses no observation, but the last "
    "points of the trend are estimated with data on one side only and move "
    "as the sample grows.",

    "Hamilton regression. The value observed h months ahead is regressed on "
    "a constant and on p successive lags of the series; the cycle is the "
    "residual of that regression, that is, the part of the future value "
    "that the recent past does not predict. The parameters are h = 24 and "
    "p = 12, the monthly transposition of the (8, 4) pair Hamilton "
    "recommends for quarterly data. The construction consumes the first "
    "h + p − 1 = 35 months, which is why this panel starts later than "
    "the others.",

    "Band-pass filters. Both keep only the fluctuations whose period falls "
    "between 18 and 96 months — a year and a half to eight years, the "
    "range Burns and Mitchell assigned to the business cycle — and "
    "discard everything slower or faster. The Baxter-King filter is a "
    "symmetric moving average truncated at K = 36 months, which costs three "
    "years at each end of the sample; the Christiano-Fitzgerald filter is "
    "asymmetric, uses every observation and therefore loses none, at the "
    "price of weights that differ from one date to the next.",

    "First difference. The plainest cycle there is: the change from one "
    "month to the next, which removes any trend that is a straight line and "
    "keeps the rest. It loses only the first month. It is shown here "
    "because it assumes nothing, and because where it agrees with the other "
    "four the reading does not depend on the filter.",

    "Reading the panels. The vertical scale is free in each panel: the "
    "filters do not return comparable amplitudes, and forcing a common "
    "scale would flatten three of them. What is comparable, and what these "
    "plates are for, is the date of the turning points. Where the five "
    "panels turn together, the cycle is in the data; where they part, it is "
    "in the method. The shaded bands mark the episodes of macroeconomic "
    "stress, identical on every panel.",

    "The whole calculation is in tools/sf_prepare.py, in the standard "
    "library alone; each plate can be downloaded as an SVG from the line "
    "beneath it, and the table of moments under the five filters, higher up "
    "this pane, in CSV, XLSX or LaTeX. "
    "References: Hodrick and Prescott (1997); Hamilton (2018); Baxter and "
    "King (1999); Christiano and Fitzgerald (2003); Ravn and Uhlig (2002); "
    "Burns and Mitchell (1946).",
]

NOTE_FILTRES_FR = [
    "Comment ces panneaux sont construits. Chaque série est d’abord mise "
    "sous la forme qu’un filtre peut prendre. Une série strictement "
    "positive est remplacée par cent fois son logarithme naturel, de sorte "
    "que l’écart à la tendance se lise directement en pourcentage ; un taux "
    "est déjà en points de pourcentage et se filtre tel quel ; un solde, "
    "qui change de signe, n’admet pas le logarithme et se filtre dans son "
    "unité propre. Les cinq filtres sont ensuite appliqués à cette même "
    "série transformée, et chaque panneau montre la composante cyclique que "
    "l’un d’eux restitue.",

    "Hodrick et Prescott. La tendance est la série qui minimise la somme "
    "des écarts au carré aux données, augmentée de λ fois la somme des "
    "carrés de ses propres différences secondes ; le cycle est ce qui "
    "reste. Le paramètre de lissage est fixé à λ = 14400, la "
    "contrepartie mensuelle du 1600 trimestriel selon la règle de la "
    "puissance quatre ; la planche suivante montre ce qu’auraient décidé "
    "d’autres valeurs. Le filtre utilise tout l’échantillon et ne perd "
    "aucune observation, mais les derniers points de la tendance sont "
    "estimés avec des données d’un seul côté et bougent à mesure que "
    "l’échantillon s’allonge.",

    "Régression de Hamilton. On régresse la valeur observée h mois plus "
    "tard sur une constante et sur p retards successifs de la série ; le "
    "cycle est le résidu de cette régression, c’est-à-dire la part de la "
    "valeur future que le passé récent ne prédit pas. Les paramètres "
    "retenus sont h = 24 et p = 12, transposition mensuelle du couple "
    "(8, 4) que Hamilton recommande pour des données trimestrielles. La "
    "construction consomme les h + p − 1 = 35 premiers mois : c’est "
    "pourquoi ce panneau commence plus tard que les autres.",

    "Filtres passe-bande. Tous deux ne retiennent que les fluctuations dont "
    "la période tombe entre 18 et 96 mois — un an et demi à huit ans, "
    "l’intervalle que Burns et Mitchell assignaient au cycle des affaires "
    "— et rejettent tout ce qui est plus lent ou plus rapide. Le "
    "filtre de Baxter et King est une moyenne mobile symétrique tronquée à "
    "K = 36 mois, ce qui coûte trois ans à chaque extrémité de "
    "l’échantillon ; celui de Christiano et Fitzgerald est asymétrique, "
    "utilise toutes les observations et n’en perd donc aucune, au prix de "
    "pondérations qui diffèrent d’une date à l’autre.",

    "Différence première. Le cycle le plus simple qui soit : la variation "
    "d’un mois à l’autre, qui retranche toute tendance linéaire et garde le "
    "reste. Elle ne perd que le premier mois. Elle figure ici parce qu’elle "
    "ne suppose rien, et parce que là où elle s’accorde avec les quatre "
    "autres, la lecture ne dépend pas du filtre.",

    "Lire les panneaux. L’échelle verticale est libre dans chaque panneau : "
    "les filtres ne restituent pas des amplitudes comparables, et leur "
    "imposer une échelle commune en aplatirait trois. Ce qui est "
    "comparable, et ce à quoi ces planches servent, est la date des "
    "retournements. Là où les cinq panneaux se retournent ensemble, le "
    "cycle est dans les données ; là où ils divergent, il est dans la "
    "méthode. Les plages grisées signalent les épisodes de tension "
    "macroéconomique, identiques sur tous les panneaux.",

    "Tout le calcul tient dans tools/sf_prepare.py, avec la seule "
    "bibliothèque standard ; chaque planche se télécharge en SVG depuis la "
    "ligne qui la suit, et le tableau des moments sous les cinq filtres, "
    "plus haut dans ce volet, en CSV, XLSX ou LaTeX. "
    "Références : Hodrick et Prescott (1997) ; Hamilton "
    "(2018) ; Baxter et King (1999) ; Christiano et Fitzgerald (2003) ; "
    "Ravn et Uhlig (2002) ; Burns et Mitchell (1946).",
]


def slug(cle):
    """Rend la cle d'un agregat sous la forme qu'un fichier livre peut porter.

    Les colonnes du dossier sont nommees a l'anglaise -- ExchangeRate,
    GovtRevenue --, mais une figure publiee s'ecrit en minuscules et par
    mots separes : le disque de l'auteur ne distingue pas la casse, le
    serveur qui sert la page si. Un fichier ecrit ExchangeRate ici et
    demande exchangerate la-bas se perdrait entre les deux.
    """
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", cle).lower()


def fig_filtres_agregat(cle, dates, cols):
    """Les cinq filtres appliques a un agregat : cinq panneaux empiles."""
    if not dates or cle not in cols:
        return None
    base, (unite_en, unite_fr) = base_cyclable(cle, cols[cle])
    nom_en, nom_fr = NOMS.get(cle, (cle, cle))
    lignes = []
    for c, (en, fr), filtre, couleur in FILTRES:
        try:
            cyc = filtre(base)
        except Exception:                                        # noqa: BLE001
            continue
        for d, x in zip(dates, cyc):
            if x is None:
                continue
            lignes.append([d, c, en, fr, "%.6g" % x, couleur])
    if not lignes:
        return None
    csvf = ecrit_csv("sf-filtres-%s.csv" % slug(cle),
                     ["date", "filtre", "panneau_en", "panneau_fr", "y",
                      "couleur"], lignes)
    return {
        "cle": "sf-filtres-%s" % slug(cle), "type": "facettes_aires",
        "csv": csvf,
        "largeur": 12.0, "hauteur": 8.6, "colonnes": 1, "bandes": TENSIONS,
        "pas_annees": 1,
        # Le nom de l'agregat sert d'intitule au bouton du selecteur.
        "choix_en": nom_en, "choix_fr": nom_fr,
        "titre_en": "%s: one series, five filters" % nom_en,
        "titre_fr": "%s : une série, cinq filtres" % nom_fr,
        "sous_en": "Cyclical component, %s. The vertical scale is free in "
                   "each panel: what is read here is the timing of the "
                   "turns, not the size of the gap." % unite_en,
        "sous_fr": "Composante cyclique, en %s. L’échelle verticale est "
                   "libre dans chaque panneau : ce qui se lit ici est la "
                   "date des retournements, non l’ampleur de l’écart."
                   % unite_fr,
        "source_en": "Central Bank of the Congo, World Bank, IMF; author’s calculations.",
        "source_fr": "Banque centrale du Congo, Banque mondiale, FMI ; calculs de l’auteur.",
    }


def fig_lambda(dates, cols):
    """La sensibilite du filtre HP au parametre de lissage."""
    if not dates or "GDP" not in cols:
        return None
    base = [100.0 * math.log(x) for x in cols["GDP"]]
    choix = [
        (1600.0, "λ = 1600, the quarterly convention applied as it stands",
         "λ = 1600, la convention trimestrielle appliquée telle quelle",
         ARDOISE),
        (14400.0, "λ = 14400, the monthly value used throughout this page",
         "λ = 14400, la valeur mensuelle retenue dans toute cette page",
         PINE),
        (129600.0, "λ = 129600, the Ravn-Uhlig monthly value",
         "λ = 129600, la valeur mensuelle de Ravn et Uhlig", BRASS),
    ]
    lignes = []
    for lam, en, fr, couleur in choix:
        for d, x in zip(dates, hp(base, lam)):
            lignes.append([d, "%g" % lam, en, fr, "%.6g" % x, couleur])
    csvf = ecrit_csv("sf-lambda.csv",
                     ["date", "lambda", "panneau_en", "panneau_fr", "y",
                      "couleur"], lignes)
    return {
        "cle": "sf-lambda", "type": "facettes_aires", "csv": csvf,
        "largeur": 12.0, "hauteur": 5.8, "colonnes": 1, "bandes": TENSIONS,
        "pas_annees": 1,
        "titre_en": "What the smoothing parameter decides",
        "titre_fr": "Ce que décide le paramètre de lissage",
        "sous_en": "A low value hands the movement to the trend and "
                   "leaves a flat cycle; a high one holds the trend straight "
                   "and pushes every swing into the cycle.",
        "sous_fr": "Une valeur faible confie le mouvement à la tendance "
                   "et laisse un cycle plat ; une valeur forte maintient la "
                   "tendance droite et rejette toute l’oscillation dans le "
                   "cycle.",
        "source_en": "Central Bank of the Congo, World Bank, IMF; author’s calculations.",
        "source_fr": "Banque centrale du Congo, Banque mondiale, FMI ; calculs de l’auteur.",
    }


def fig_structure():
    """Traits de structure : ce qui distingue cette economie des autres."""
    faits = [
        ("Mining, share of exports", "Mines, part des exportations", 98.9, PINE,
         "IMF Article IV", "FMI, article IV"),
        ("Mining, share of fiscal revenue", "Mines, part des recettes fiscales", 46.0, SAGE,
         "EITI-DRC", "ITIE-RDC"),
        ("Cobalt, share of world output", "Cobalt, part de la production mondiale", 76.0, BRASS,
         "USGS", "USGS"),
        ("Deposits held in foreign currency", "Dépôts en devises", 90.9, PRUNE,
         "IMF Article IV", "FMI, article IV"),
        ("Adults with a bank account", "Adultes titulaires d’un compte", 26.0, BRIQUE,
         "Global Findex", "Global Findex"),
    ]
    lignes = [[en, fr, "%.1f" % v, c, sen, sfr] for en, fr, v, c, sen, sfr in faits]
    csvf = ecrit_csv("sf-structure.csv",
                     ["label_en", "label_fr", "y", "couleur", "src_en", "src_fr"], lignes)
    return {
        "cle": "sf-structure", "type": "barres_v", "csv": csvf,
        # Les intitules sont longs, et chacun nomme sa source : la planche
        # est haute pour que le panneau reste plus grand que sa legende.
        "largeur": 8.4, "hauteur": 6.4,
        "titre_en": "Five structural features",
        "titre_fr": "Cinq traits de structure",
        "sous_en": "Per cent. Reported shares, latest year available.",
        "sous_fr": "En pourcentage. Parts publiées, dernier exercice disponible.",
        "source_en": "IMF Article IV, EITI-DRC, USGS, Global Findex.",
        "source_fr": "FMI article IV, ITIE-RDC, USGS, Global Findex.",
    }


def fig_secteur_cle():
    """Le secteur cle : la croissance extractive contre le reste.

    Les comptes nationaux congolais ne publient pas de ligne separee pour
    les industries extractives ; on ne peut donc pas lire le secteur cle
    dans les parts de valeur ajoutee. Le Fonds, lui, decompose la
    croissance en extractif et non extractif. C'est cette decomposition
    qui nomme le secteur, et c'est elle qu'on trace : quatre annees, deux
    series, la meme unite. Les chiffres sont ceux du tableau
    « str-croissance » de la section, sans retouche.
    """
    postes = [
        (2023, "Extractive", "Extractif", 20.2, PINE),
        (2023, "Non-extractive", "Non extractif", 3.4, SAGE),
        (2024, "Extractive", "Extractif", 11.9, PINE),
        (2024, "Non-extractive", "Non extractif", 3.1, SAGE),
        (2025, "Extractive", "Extractif", 10.1, PINE),
        (2025, "Non-extractive", "Non extractif", 3.1, SAGE),
        (2026, "Extractive", "Extractif", 5.0, PINE),
        (2026, "Non-extractive", "Non extractif", 5.4, SAGE),
    ]
    # L'annee tient l'intitule et le secteur passe dessous, entre
    # parentheses, la ou les autres planches mettent leur source : huit
    # colonnes ne laissent pas la place a une legende ecrite en toutes
    # lettres sous chaque barre. Le millesime porte l'etoile des
    # projections, expliquee dans le sous-titre.
    lignes = []
    for a, en, fr, v, c in postes:
        etoile = "*" if a >= 2025 else ""
        lignes.append(["%d%s" % (a, etoile), "%d%s" % (a, etoile),
                       "%.1f" % v, c, en, fr])
    csvf = ecrit_csv("sf-secteur-cle.csv",
                     ["label_en", "label_fr", "y", "couleur", "src_en",
                      "src_fr"], lignes)
    return {
        "cle": "sf-secteur-cle", "type": "barres_v", "csv": csvf,
        "largeur": 8.6, "hauteur": 5.2,
        "titre_en": "The key sector of the Congolese economy",
        "titre_fr": "Le secteur clé de l’économie congolaise",
        "sous_en": "Real growth, per cent, extractive output against the "
                   "rest of the economy. The extractive sector grows two to "
                   "six times faster than the rest through 2025, and makes "
                   "up more than ninety-eight per cent of goods exports; it "
                   "employs about one worker in nine. An asterisk marks a "
                   "projection.",
        "sous_fr": "Croissance réelle, en pourcentage, production "
                   "extractive contre reste de l’économie. Le secteur "
                   "extractif croît deux à six fois plus vite que le reste "
                   "jusqu’en 2025, et fait plus de quatre-vingt-dix-huit "
                   "pour cent des exportations de biens ; il occupe environ "
                   "un travailleur sur neuf. L’astérisque signale une "
                   "projection.",
        "source_en": "IMF country report 26/2, table 1; USGS; ILO.",
        "source_fr": "FMI, rapport pays 26/2, tableau 1 ; USGS ; OIT.",
    }


def fig_exportations():
    """Composition des exportations, en barres empilees."""
    postes = [
        ("Refined copper", "Cuivre raffiné", 19.50, PINE),
        ("Cobalt", "Cobalt", 3.05, BRASS),
        ("Copper ore", "Minerai de cuivre", 3.03, SAGE),
        ("Other goods", "Autres biens", 4.02, ARDOISE),
    ]
    lignes = [["2024", en, fr, "%.2f" % v, c] for en, fr, v, c in postes]
    csvf = ecrit_csv("sf-exportations.csv",
                     ["annee", "poste_en", "poste_fr", "y", "couleur"], lignes)
    return {
        "cle": "sf-exportations", "type": "barres_empilees", "csv": csvf,
        # La pile est haute plutot que large : les deux postes minces, le
        # cobalt et le minerai, n'auraient pas la place de porter leur part.
        "largeur": 5.2, "hauteur": 6.2,
        "titre_en": "What the country sells",
        "titre_fr": "Ce que le pays vend",
        "sous_en": "Merchandise exports 2024, billions of US dollars. "
                   "Copper and cobalt together account for more than four fifths.",
        "sous_fr": "Exportations de marchandises 2024, en milliards de dollars "
                   "américains. Le cuivre et le cobalt en représentent "
                   "plus des quatre cinquièmes.",
        "source_en": "Observatory of Economic Complexity, 2024.",
        "source_fr": "Observatory of Economic Complexity, 2024.",
    }


REGIMES = [
    (1990, 1996, "Late Mobutu years", "Fin de la période Mobutu", BRIQUE),
    (1997, 2000, "War and transition", "Guerre et transition", ARDOISE),
    (2001, 2018, "Reconstruction", "Reconstruction", SAGE),
    (2019, 2026, "Present administration", "Administration actuelle", PINE),
]

# Le libelle d'une periode ne se glisse pas tel quel dans une phrase : on
# lui donne ici sa forme prepositionnelle, dans chaque langue.
LIAISON_EN = {
    "Late Mobutu years": "in the late Mobutu years",
    "War and transition": "during the war and the transition",
    "Reconstruction": "during the reconstruction",
    "Present administration": "under the present administration",
}
LIAISON_FR = {
    "Fin de la période Mobutu": "à la fin de la période Mobutu",
    "Guerre et transition": "pendant la guerre et la transition",
    "Reconstruction": "pendant la reconstruction",
    "Administration actuelle": "sous l’administration actuelle",
}


def fig_regimes():
    """Le cycle reel, decoupe selon les regimes politiques successifs."""
    m = charge("macro-rdc.json")
    if not m:
        return None
    annees = [int(a) for a in m.get("annees") or []]
    crois = [nombre(v) for v in m.get("croissance") or []]
    if len(annees) < 10 or len(crois) != len(annees):
        return None
    lignes = []
    for a, g in zip(annees, crois):
        if g is None:
            continue
        for d, f, en, fr, c in REGIMES:
            if d <= a <= f:
                lignes.append([a, "%.4g" % g, en, fr, c])
                break
    if not lignes:
        return None
    csvf = ecrit_csv("sf-regimes.csv",
                     ["annee", "y", "regime_en", "regime_fr", "couleur"], lignes)
    moy = {}
    for a, g, en, fr, c in lignes:
        moy.setdefault((en, fr, c), []).append(float(g))

    def enumere(items, et):
        """Une enumeration lisible plutot qu'une liste a point-virgules."""
        if len(items) < 2:
            return "".join(items)
        return ", ".join(items[:-1]) + " " + et + " " + items[-1]

    moyennes_fr = enumere(
        ["%s pour cent %s" % (("%.1f" % (sum(v) / len(v))).replace(".", ","),
                              LIAISON_FR[fr])
         for (en, fr, c), v in moy.items()], "et")
    moyennes_en = enumere(
        ["%.1f per cent %s" % (sum(v) / len(v), LIAISON_EN[en])
         for (en, fr, c), v in moy.items()], "and")
    return {
        "cle": "sf-regimes", "type": "colonnes_regimes", "csv": csvf,
        "largeur": 8.6, "hauteur": 5.0,
        "titre_en": "The real cycle, by political period",
        "titre_fr": "Le cycle réel, par période politique",
        "sous_en": "Real GDP growth, per cent. The colour marks the period "
                   "and the dashed line the average growth of that period, "
                   "which came to " + moyennes_en + ".",
        "sous_fr": "Croissance du PIB réel, en pourcentage. La couleur "
                   "marque la période et le trait discontinu donne la "
                   "croissance moyenne de cette période, qui a valu "
                   + moyennes_fr + ".",
        "source_en": "IMF, World Bank, BCC, AfDB.",
        "source_fr": "FMI, Banque mondiale, BCC, BAD.",
    }


def fig_vulnerabilites(dates, cols):
    """Quatre mesures de vulnerabilite, ramenees a une echelle commune."""
    if not dates or "Reserves" not in cols:
        return None
    n = len(dates)
    mesures = []

    # 1. Couverture des importations par les reserves, en mois
    if "Imports" in cols:
        base_imp = sum(cols["Imports"][:12]) / 12.0
        couv = [cols["Reserves"][i] / max(cols["Reserves"][0], 1e-9) /
                max(cols["Imports"][i] / base_imp, 1e-9) for i in range(n)]
        ech = 3.0 / max(couv[0], 1e-9)
        mesures.append(("Reserve cover, months of imports",
                        "Couverture des réserves, en mois d’importations",
                        [v * ech for v in couv], PINE))

    # 2. Depreciation du franc sur douze mois
    if "ExchangeRate" in cols:
        e = cols["ExchangeRate"]
        dep = [0.0] * 12 + [100.0 * (e[i] / e[i - 12] - 1.0) for i in range(12, n)]
        mesures.append(("Depreciation over twelve months, per cent",
                        "Dépréciation sur douze mois, en pourcentage",
                        dep, BRIQUE))

    # 3. Dependance au cuivre : cours rapporte a sa moyenne longue
    if "CopperPrice" in cols:
        cu = cols["CopperPrice"]
        moy = sum(cu) / len(cu)
        mesures.append(("Copper price, ratio to its long average",
                        "Cours du cuivre, rapporté à sa moyenne longue",
                        [100.0 * v / moy for v in cu], BRASS))

    # 4. Solde public, en points de PIB
    if "GovtRevenue" in cols and "GovtExpenditure" in cols:
        sol = [cols["GovtRevenue"][i] - cols["GovtExpenditure"][i] for i in range(n)]
        mesures.append(("Fiscal balance, points of GDP",
                        "Solde public, en points de PIB", sol, SAGE))

    if len(mesures) < 3:
        return None
    lignes = []
    for en, fr, v, c in mesures:
        for d, x in zip(dates, v):
            lignes.append([d, en, fr, "%.5g" % x, c])
    csvf = ecrit_csv("sf-vulnerabilites.csv",
                     ["date", "panneau_en", "panneau_fr", "y", "couleur"], lignes)
    return {
        "cle": "sf-vulnerabilites", "type": "facettes_aires", "csv": csvf,
        "largeur": 12.0, "hauteur": 5.4, "colonnes": 2, "bandes": TENSIONS,
        "pas_annees": 2,
        "titre_en": "Four ways the economy is exposed",
        "titre_fr": "Quatre expositions de l’économie",
        "sous_en": "Each panel keeps its own unit. Shading marks the episodes "
                   "of macroeconomic stress.",
        "sous_fr": "Chaque panneau garde son unité propre. Les plages "
                   "grisées signalent les épisodes de tension "
                   "macroéconomique.",
        "source_en": "Central Bank of the Congo, World Bank; author’s calculations.",
        "source_fr": "Banque centrale du Congo, Banque mondiale ; calculs de l’auteur.",
    }


# ----------------------------------------------------------------------
def planches():
    """Rend la liste des fiches de planches de faits stylises."""
    dates, cols = socle_mensuel()
    if dates:
        ajouts = prolonge_par_le_site(dates, cols)
        print("  socle mensuel : %d mois, %d series, %d mois ajoutes par le site"
              % (len(dates), len(cols), ajouts))
    else:
        print("  socle mensuel absent : data/drc-mensuel.csv introuvable")

    fabriques = [
        ("sf-niveaux", lambda: fig_niveaux(dates, cols)),
        ("sf-cycles", lambda: fig_cycles(dates, cols)),
        ("sf-xcorr", lambda: fig_xcorr(dates, cols)),
        ("sf-vulnerabilites", lambda: fig_vulnerabilites(dates, cols)),
        ("sf-filtres", lambda: fig_filtres(dates, cols)),
    ]
    # Les dix-sept planches d'agregat prennent la place de la planche
    # d'ouverture dans la lecture : elles la suivent immediatement, dans
    # l'ordre des panneaux, et c'est cet ordre-la que le selecteur reprend.
    fabriques += [("sf-filtres-%s" % slug(c),
                   (lambda c=c: fig_filtres_agregat(c, dates, cols)))
                  for c in ORDRE_PANNEAUX]
    fabriques += [
        ("sf-lambda", lambda: fig_lambda(dates, cols)),
        ("sf-regimes", fig_regimes),
        ("sf-structure", fig_structure),
        ("sf-secteur-cle", fig_secteur_cle),
        ("sf-exportations", fig_exportations),
    ]
    out = []
    note_posee = False
    for cle, f in fabriques:
        try:
            fiche = f()
        except Exception as e:
            print("  %s : ecartee, %s" % (cle, e))
            continue
        if fiche:
            # La note de procede vaut pour les dix-sept planches et ne se
            # lit qu'une fois : elle voyage donc avec la premiere qui sort,
            # et le poseur l'ecrit sous le selecteur, non sous chacune.
            if cle.startswith("sf-filtres-") and not note_posee:
                fiche["note_en"] = NOTE_FILTRES_EN
                fiche["note_fr"] = NOTE_FILTRES_FR
                note_posee = True
            out.append(fiche)
            print("  %s : prete" % cle)
        else:
            print("  %s : donnees insuffisantes" % cle)
    return out


if __name__ == "__main__":
    import sys
    p = planches()
    os.makedirs(SORTIE, exist_ok=True)
    with open(os.path.join(SORTIE, "plan-sf.json"), "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    print("%d planches de faits stylises." % len(p))
    sys.exit(0 if p else 1)
