#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepare les donnees que ggplot2 va tracer.

Le script lit les series deja publiees par le site (data/series.json et,
lorsqu'il existe, l'historique mensuel de data/prix-brut.json), ecrit un
fichier CSV propre par figure dans build/gg/ et depose a cote un plan.json
qui decrit, pour chaque figure, le type de graphique, les intitules anglais
et francais, la source et les dimensions.

Aucune dependance : bibliotheque standard seulement. Le script ne modifie
jamais le site ; il ne fait que preparer le terrain pour tools/figures.R.
"""

import csv
import html
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(RACINE, "data")
SORTIE = os.path.join(RACINE, "build", "gg")

# Palette du site : bleu d'Oxford, laiton, papier creme.
PINE = "#002147"
BRASS = "#8A6A18"
SAGE = "#3F6B52"
BRIQUE = "#8C2F27"


def texte(v):
    """Ramene une valeur a du texte lisible : entites HTML decodees."""
    if v is None:
        return ""
    s = str(v)
    if "&" in s:
        s = html.unescape(s)
    return s.strip()


def nombre(v):
    """Renvoie un flottant, ou None si la case n'est pas numerique."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        t = v.replace(" ", "").replace(" ", "").replace(" ", "")
        t = t.replace("−", "-").replace(",", ".")
        if re.match(r"^-?\d+(\.\d+)?$", t):
            return float(t)
    return None


def charge(chemin):
    if not os.path.exists(chemin):
        return None
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("  lecture impossible (%s) : %s" % (os.path.basename(chemin), e))
        return None


def ecrit_csv(cle, entetes, lignes):
    os.makedirs(SORTIE, exist_ok=True)
    chemin = os.path.join(SORTIE, cle + ".csv")
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(entetes)
        for l in lignes:
            w.writerow(l)
    return cle + ".csv"


# --------------------------------------------------------------------------
# Les figures, une fonction par figure. Chacune renvoie une fiche de plan,
# ou None si la serie n'est pas disponible : une figure manquante ne doit
# jamais interrompre la chaine.
# --------------------------------------------------------------------------

def fig_croissance(S):
    s = S.get("pib-croissance")
    if not s or len(s.get("rows") or []) < 5:
        return None
    lignes = []
    for r in s["rows"]:
        x, y = nombre(r[0]), nombre(r[1])
        if x is not None and y is not None:
            lignes.append([int(x), y])
    if len(lignes) < 5:
        return None
    ecrit_csv("pib-croissance", ["x", "y"], lignes)
    return {
        "cle": "pib-croissance",
        "type": "colonnes_zero",
        "csv": "pib-croissance.csv",
        "titre_en": "Real GDP growth",
        "titre_fr": "Croissance du PIB réel",
        "sous_en": "Annual percentage change, %d-%d" % (lignes[0][0], lignes[-1][0]),
        "sous_fr": "Variation annuelle en pourcentage, %d-%d" % (lignes[0][0], lignes[-1][0]),
        "x_en": "Year", "x_fr": "Année",
        "y_en": "Per cent", "y_fr": "Pour cent",
        "source_en": "Source: " + texte(s.get("source")),
        "source_fr": "Source : " + texte(s.get("source")),
        "couleur": PINE, "couleur2": BRIQUE,
        "largeur": 8.4, "hauteur": 4.6,
    }


def fig_inflation(S):
    s = S.get("inflation-longue")
    if not s or len(s.get("rows") or []) < 5:
        return None
    lignes = []
    for r in s["rows"]:
        x, y = nombre(r[0]), nombre(r[1])
        if x is not None and y is not None and y > 0:
            lignes.append([int(x), y])
    if len(lignes) < 5:
        return None
    ecrit_csv("inflation-longue", ["x", "y"], lignes)
    return {
        "cle": "inflation-longue",
        "type": "ligne_log",
        "csv": "inflation-longue.csv",
        "titre_en": "Consumer price inflation",
        "titre_fr": "Inflation des prix à la consommation",
        "sous_en": "Annual rate, logarithmic scale, %d-%d" % (lignes[0][0], lignes[-1][0]),
        "sous_fr": "Taux annuel, échelle logarithmique, %d-%d" % (lignes[0][0], lignes[-1][0]),
        "x_en": "Year", "x_fr": "Année",
        "y_en": "Per cent, log scale", "y_fr": "Pour cent, échelle log",
        "source_en": "Source: " + texte(s.get("source")),
        "source_fr": "Source : " + texte(s.get("source")),
        "couleur": BRIQUE, "couleur2": PINE,
        "largeur": 8.4, "hauteur": 4.6,
    }


def fig_indice(S):
    s = S.get("pib-indice")
    if not s or len(s.get("rows") or []) < 5:
        return None
    lignes = []
    for r in s["rows"]:
        x, y = nombre(r[0]), nombre(r[1])
        if x is not None and y is not None:
            lignes.append([int(x), y])
    if len(lignes) < 5:
        return None
    ecrit_csv("pib-indice", ["x", "y"], lignes)
    return {
        "cle": "pib-indice",
        "type": "aire",
        "csv": "pib-indice.csv",
        "titre_en": "Real GDP, index 2015 = 100",
        "titre_fr": "PIB réel, indice 2015 = 100",
        "sous_en": "Level of activity, %d-%d" % (lignes[0][0], lignes[-1][0]),
        "sous_fr": "Niveau d’activité, %d-%d" % (lignes[0][0], lignes[-1][0]),
        "x_en": "Year", "x_fr": "Année",
        "y_en": "Index, 2015 = 100", "y_fr": "Indice, 2015 = 100",
        "source_en": "Source: " + texte(s.get("source")),
        "source_fr": "Source : " + texte(s.get("source")),
        "couleur": PINE, "couleur2": "#C9D3DF",
        "largeur": 8.4, "hauteur": 4.4,
    }


def fig_villes(S):
    s = S.get("pop-top15")
    if not s or len(s.get("rows") or []) < 5:
        return None
    lignes = []
    for r in s["rows"]:
        v = nombre(r[-1])
        if v is None:
            continue
        lignes.append([texte(r[0]), texte(r[1]), v / 1e6])
    if len(lignes) < 5:
        return None
    ecrit_csv("pop-top15", ["label", "groupe", "y"], lignes)
    return {
        "cle": "pop-top15",
        "type": "barres_h",
        "csv": "pop-top15.csv",
        "titre_en": "The fifteen most populous entities",
        "titre_fr": "Les quinze entités les plus peuplées",
        "sous_en": "Projected population 2026, millions of inhabitants",
        "sous_fr": "Population projetée 2026, millions d’habitants",
        "x_en": "", "x_fr": "",
        "y_en": "Millions of inhabitants", "y_fr": "Millions d’habitants",
        "source_en": "Source: " + texte(s.get("source")),
        "source_fr": "Source : " + texte(s.get("source")),
        "couleur": PINE, "couleur2": BRASS,
        "chiffres": 2,
        "largeur": 8.4, "hauteur": 5.4,
    }


# Les barres horizontales portent un seul intitule, tire de la colonne
# « label » du CSV : il sert aux deux langues a la fois. Pour les dix-sept
# epidemies, l'annee ne suffit pas -- 2021 et 2022 en comptent deux chacune
# -- et le nom de la province change d'une langue a l'autre (North Kivu,
# Nord-Kivu). On retient donc le toponyme, qui lui ne change pas, et
# l'annee devant. Les deux epidemies qui s'etendent sur plusieurs
# provinces n'ont pas de toponyme unique : leur annee suffit a les
# distinguer.
EBOLA_LIEUX = {
    "1976": "Yambuku", "1977": "Tandala", "1995": "Kikwit",
    "2007": "Luebo", "2008-2009": "Mweka", "2012": "Isiro",
    "2014": "Boende", "2017": "Likati", "2018": "Bikoro",
    "2018-2020": "", "2020": "Mbandaka", "2025": "Bulape",
    "2026": "",
}
# Les quatre annees qui reviennent deux fois sont nommees par leur rang.
EBOLA_LIEUX_RANG = {12: "Biena", 13: "Beni", 14: "Mbandaka", 15: "Beni"}


def fig_ebola_histoire(S):
    """Les dix-sept epidemies d'Ebola, rangees par nombre de cas."""
    s = S.get("sante-ebola-histoire")
    if not s or len(s.get("rows") or []) < 5:
        return None
    lignes = []
    for i, r in enumerate(s["rows"], start=1):
        annee = texte(r[1])
        v = nombre(r[4])
        if v is None:
            continue
        lieu = EBOLA_LIEUX_RANG.get(i, EBOLA_LIEUX.get(annee, ""))
        lignes.append([annee + (" · " + lieu if lieu else ""), annee, v])
    if len(lignes) < 5:
        return None
    ecrit_csv("sante-ebola-histoire", ["label", "groupe", "y"], lignes)
    return {
        "cle": "sante-ebola-histoire",
        "type": "barres_h",
        "csv": "sante-ebola-histoire.csv",
        "titre_en": "The seventeen Ebola outbreaks, 1976 to 2026",
        "titre_fr": "Les dix-sept épidémies d’Ebola, de 1976 à 2026",
        "sous_en": "Cases as published, by outbreak",
        "sous_fr": "Cas tels que publiés, par épidémie",
        "x_en": "", "x_fr": "",
        "y_en": "Cases", "y_fr": "Cas",
        "source_en": "Source: " + texte(s.get("source")),
        "source_fr": "Source : " + texte(s.get("source")),
        "couleur": BRIQUE, "couleur2": PINE,
        "chiffres": 0,
        "largeur": 8.4, "hauteur": 6.4,
    }


def fig_ebola_zones(S):
    """Les zones de sante de l'Ituri que le bulletin nomme."""
    s = S.get("sante-ebola-zones")
    if not s or len(s.get("rows") or []) < 3:
        return None
    lignes = []
    for r in s["rows"]:
        v = nombre(r[1])
        if v is None:
            continue
        lignes.append([texte(r[0]), "Ituri", v])
    if len(lignes) < 3:
        return None
    ecrit_csv("sante-ebola-zones", ["label", "groupe", "y"], lignes)
    return {
        "cle": "sante-ebola-zones",
        "type": "barres_h",
        "csv": "sante-ebola-zones.csv",
        "titre_en": "Ituri, the health zones the bulletin names",
        "titre_fr": "Ituri, les zones de santé que le bulletin nomme",
        "sous_en": "Confirmed cases at 30 July 2026",
        "sous_fr": "Cas confirmés au 30 juillet 2026",
        "x_en": "", "x_fr": "",
        "y_en": "Confirmed cases", "y_fr": "Cas confirmés",
        "source_en": "Source: " + texte(s.get("source")),
        "source_fr": "Source : " + texte(s.get("source")),
        "couleur": BRIQUE, "couleur2": BRASS,
        "chiffres": 0,
        "largeur": 8.4, "hauteur": 4.6,
    }


# Les bulletins datent leurs chiffres en toutes lettres, « 30 July 2026 ».
# La planche, elle, a besoin d'un axe des dates. On relit donc la colonne
# anglaise du tableau plutot que de tenir a cote une liste de dates : un
# bulletin ajoute au tableau se place ainsi de lui-meme, et un bulletin
# dont la date ne se lit pas est ecarte au lieu d'etre place au hasard.
MOIS_EN = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5,
           "june": 6, "july": 7, "august": 8, "september": 9, "october": 10,
           "november": 11, "december": 12}


def premier(v):
    """La forme anglaise d'une case bilingue, ou la case elle-meme."""
    if isinstance(v, (list, tuple)) and v:
        return texte(v[0])
    return texte(v)


def date_iso(v):
    """« 30 July 2026 » devient « 2026-07-30 » ; sinon None."""
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", premier(v))
    if not m:
        return None
    mois = MOIS_EN.get(m.group(2).lower())
    if not mois:
        return None
    return "%s-%02d-%02d" % (m.group(3), mois, int(m.group(1)))


def fig_ebola_trajectoire(S):
    """La courbe des cas et des deces, bulletin par bulletin.

    Le tableau des bulletins porte deja les deux series ; la planche ne
    fait que les mettre sur un axe des dates, ou l'acceleration se voit
    d'un coup d'oeil et ou l'ecart entre les deux courbes est la letalite.
    Une case sans chiffre publie -- le premier bulletin ne donne aucun
    total de cas confirmes -- n'est pas tracee : elle n'est pas un zero.
    """
    s = S.get("sante-ebola-bulletins")
    if not s or len(s.get("rows") or []) < 4:
        return None
    lignes, bornes = [], {}
    for r in s["rows"]:
        if len(r) < 5:
            continue
        d = date_iso(r[2])
        if not d:
            continue
        bornes[d] = (premier(r[2]), texte(r[2][1] if isinstance(r[2], (list, tuple))
                                          and len(r[2]) > 1 else r[2]))
        for i, serie in ((3, "cas"), (4, "deces")):
            v = nombre(r[i])
            if v is not None:
                lignes.append([d, serie, v])
    if len([l for l in lignes if l[1] == "cas"]) < 4:
        return None
    ecrit_csv("sante-ebola-trajectoire", ["x", "serie", "y"], lignes)
    debut, fin = bornes[min(bornes)], bornes[max(bornes)]
    # Quand les deux bornes tombent dans la meme annee, elle ne se dit
    # qu'une fois : « 15 mai au 12 aout 2026 » et non deux millesimes.
    if debut[0][-4:] == fin[0][-4:]:
        debut = (debut[0][:-5], debut[1][:-5])
    return {
        "cle": "sante-ebola-trajectoire",
        "type": "lignes_multi",
        "csv": "sante-ebola-trajectoire.csv",
        "titre_en": "The seventeenth outbreak, bulletin by bulletin",
        "titre_fr": "La dix-septième épidémie, bulletin par bulletin",
        "sous_en": "Cumulative confirmed cases and deaths, "
                   "%s to %s" % (debut[0], fin[0]),
        "sous_fr": "Cas confirmés et décès cumulés, du %s au %s"
                   % (debut[1], fin[1]),
        "x_en": "Date figures were taken", "x_fr": "Date d’arrêt des chiffres",
        "y_en": "Persons", "y_fr": "Personnes",
        "series_en": {"cas": "Confirmed cases", "deces": "Deaths"},
        "series_fr": {"cas": "Cas confirmés", "deces": "Décès"},
        "source_en": "Source: " + texte(s.get("source")),
        "source_fr": "Source : " + texte(s.get("source")),
        "couleur": BRIQUE, "couleur2": PINE,
        "chiffres": 0,
        "largeur": 8.4, "hauteur": 5.4,
    }


def fig_taux(S):
    s = S.get("taux-directeur")
    if not s or len(s.get("rows") or []) < 3:
        return None
    lignes = []
    for r in s["rows"]:
        d = texte(r[0])
        v = nombre(r[1])
        if v is None or not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            continue
        lignes.append([d, v])
    if len(lignes) < 3:
        return None
    ecrit_csv("taux-directeur", ["x", "y"], lignes)
    return {
        "cle": "taux-directeur",
        "type": "marches",
        "csv": "taux-directeur.csv",
        "titre_en": "Policy rate of the Banque centrale du Congo",
        "titre_fr": "Taux directeur de la Banque centrale du Congo",
        "sous_en": "Per cent, successive decisions",
        "sous_fr": "Pour cent, décisions successives",
        "x_en": "Effective date", "x_fr": "Date d’effet",
        "y_en": "Per cent", "y_fr": "Pour cent",
        "source_en": "Source: " + texte(s.get("source")),
        "source_fr": "Source : " + texte(s.get("source")),
        "couleur": PINE, "couleur2": BRASS,
        "largeur": 8.4, "hauteur": 4.2,
    }


def fig_indices_prix():
    """Indices de prix : on prefere l'historique mensuel complet lorsqu'il
    a ete telecharge, sinon on renonce a la figure."""
    brut = charge(os.path.join(DATA, "prix-brut.json"))
    if not brut:
        return None
    hist = brut.get("historique") or {}
    mois = hist.get("mois") or []
    cles = hist.get("cles") or []
    if len(mois) < 24 or "mm" not in cles or "pm" not in cles:
        return None
    i_mm = cles.index("mm") + 1
    i_pm = cles.index("pm") + 1
    lignes = []
    for l in mois:
        p = texte(l[0])
        if not re.match(r"^\d{4}-\d{2}$", p):
            continue
        a = nombre(l[i_mm]) if i_mm < len(l) else None
        b = nombre(l[i_pm]) if i_pm < len(l) else None
        if a is not None:
            lignes.append([p + "-01", "mm", a])
        if b is not None:
            lignes.append([p + "-01", "pm", b])
    if len(lignes) < 48:
        return None
    ecrit_csv("prix-indices-hist", ["x", "serie", "y"], lignes)
    debut = min(l[0][:4] for l in lignes)
    fin = max(l[0][:4] for l in lignes)
    return {
        "cle": "prix-indices-hist",
        "type": "lignes_multi",
        "csv": "prix-indices-hist.csv",
        "titre_en": "World Bank commodity price indices",
        "titre_fr": "Indices de prix des matières premières, Banque mondiale",
        "sous_en": "Monthly, 2010 = 100, %s-%s" % (debut, fin),
        "sous_fr": "Mensuel, 2010 = 100, %s-%s" % (debut, fin),
        "x_en": "Year", "x_fr": "Année",
        "y_en": "Index, 2010 = 100", "y_fr": "Indice, 2010 = 100",
        "series_en": {"mm": "Metals and minerals", "pm": "Precious metals"},
        "series_fr": {"mm": "Métaux et minéraux", "pm": "Métaux précieux"},
        "source_en": "Source: World Bank, Commodity Markets Outlook, monthly workbook",
        "source_fr": "Source : Banque mondiale, Commodity Markets Outlook, classeur mensuel",
        "couleur": PINE, "couleur2": BRASS,
        "largeur": 8.4, "hauteur": 4.6,
    }


def main():
    S = charge(os.path.join(DATA, "series.json")) or {}
    plan = []
    fabriques = [
        ("croissance du PIB", lambda: fig_croissance(S)),
        ("inflation", lambda: fig_inflation(S)),
        ("indice du PIB", lambda: fig_indice(S)),
        ("quinze entites", lambda: fig_villes(S)),
        ("taux directeur", lambda: fig_taux(S)),
        ("indices de prix", fig_indices_prix),
        ("dix-sept epidemies", lambda: fig_ebola_histoire(S)),
        ("zones de l Ituri", lambda: fig_ebola_zones(S)),
        ("trajectoire d Ebola", lambda: fig_ebola_trajectoire(S)),
    ]
    for nom, f in fabriques:
        try:
            fiche = f()
        except Exception as e:
            print("  %s : abandon (%s)" % (nom, e))
            continue
        if fiche:
            plan.append(fiche)
            print("  %s : %d octets de donnees" % (
                nom, os.path.getsize(os.path.join(SORTIE, fiche["csv"]))))
        else:
            print("  %s : donnees insuffisantes, figure ecartee" % nom)

    if not plan:
        print("Aucune figure a produire.")
        return 1
    os.makedirs(SORTIE, exist_ok=True)
    with open(os.path.join(SORTIE, "plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    print("%d figures planifiees dans %s" % (len(plan), SORTIE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
