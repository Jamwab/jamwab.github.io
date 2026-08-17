#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le rapprochement du curriculum vitae et du dossier de travaux.

Le probleme. Le dossier de travaux vit a trois endroits qui ne se parlent
pas. publications.json est refait chaque nuit par sync_publications.py, a
partir de SSRN, de Crossref et d'ORCID. La page, elle, porte en outre une
poignee de travaux anciens qui n'existent que sur RePEc et que la
synchronisation ne releve pas. Le curriculum vitae, enfin, est compose a la
main en LaTeX, en deux langues, et personne ne le relit quand un article
parait. Les trois divergent lentement, et rien ne le signale : un CV a jour
et un CV perime se ressemblent trait pour trait.

Ce que fait ce script. Il rassemble le dossier tel que le depot le connait
-- publications.json, la page, et ORCID si l'appel passe -- puis lit les
deux fichiers LaTeX du CV, et dit ce que l'un porte et que l'autre ignore,
dans les deux sens. Un travail paru et absent du CV est un oubli ; un
travail du CV absent du dossier n'en est pas forcement un -- un chapitre,
un rapport de consultation --, mais il merite d'etre vu.

Ce qu'il ne fait pas. Il ne recrit pas le CV. Un CV n'est pas un tableau :
l'ordre des rubriques, la facon de nommer un coauteur, le choix de citer un
modele entre parentheses, la decision meme de retenir un travail ou de le
laisser de cote sont des actes d'ecriture. Un script qui les prendrait a sa
charge livrerait un document que son auteur n'aurait pas ecrit, et qu'il
signerait quand meme. Le script releve donc l'ecart et s'arrete la.

La seule chose qu'il ecrit, sur demande expresse, est le mois porte en pied
de page -- « August 2026 », « août 2026 ». Celui-la est mecanique, et il ne
doit bouger que lorsque le CV a change : d'ou l'option, plutot qu'un
horodatage automatique qui vieillirait le document chaque mois sans qu'une
ligne ait bouge.

Usage :
    python3 tools/cv_maj.py             # le rapport d'ecart
    python3 tools/cv_maj.py --orcid     # en interrogeant ORCID en plus
    python3 tools/cv_maj.py --dater     # pose le mois courant au pied du CV

Codes de sortie : 0 si le CV porte tout ce que le dossier connait, 1 s'il
manque quelque chose. L'action GitHub traite 1 comme un avertissement.
"""
import datetime as dt
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORCID_ID = "0000-0002-4675-4583"

CV = {
    "en": os.path.join(RACINE, "cv", "cv-james-wabenga-yango-en.tex"),
    "fr": os.path.join(RACINE, "cv", "cv-james-wabenga-yango-fr.tex"),
}
PAGE = os.path.join(RACINE, "site", "index.html")
DOSSIER = os.path.join(RACINE, "publications.json")

MOIS_EN = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"]


# ----------------------------------------------------------------------
# Comparer deux titres
# ----------------------------------------------------------------------
def nu(t):
    """Le titre reduit a ce qui permet de le reconnaitre.

    Accents, capitales, ponctuation et mots vides tombent : « D.R. Congo »
    et « DR Congo », « Aging » et « Ageing » doivent se rejoindre, sans quoi
    le rapport signalerait comme manquant un travail deja porte au CV.
    """
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = t.replace("ageing", "aging").replace("&", "and")
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def meme(a, b):
    """Vrai si les deux titres designent le meme travail.

    Le CV abrege : « Artificial Intelligence, Aging, and the Macroeconomy »
    pour un article dont le titre complet porte encore un sous-titre de
    deux lignes. La comparaison accepte donc qu'un titre soit le debut de
    l'autre, a condition qu'il compte assez de mots pour ne pas confondre
    deux articles voisins.
    """
    a, b = nu(a), nu(b)
    if not a or not b:
        return False
    if a == b:
        return True
    court, long = (a, b) if len(a) <= len(b) else (b, a)
    if len(court.split()) >= 4 and long.startswith(court):
        return True
    # Les deux versions d'un meme titre divergent parfois a la fin : le CV
    # ecrit « D.R. Congo » la ou la notice ecrit « Democratic Republic of
    # Congo ». Huit premiers mots identiques suffisent alors : deux
    # articles distincts ne commencent pas ainsi.
    ma, mb = a.split(), b.split()
    commun = 0
    for x, y in zip(ma, mb):
        if x != y:
            break
        commun += 1
    return commun >= 8


# ----------------------------------------------------------------------
# Le dossier, tel que le depot le connait
# ----------------------------------------------------------------------
def du_dossier():
    """Les travaux de publications.json."""
    if not os.path.exists(DOSSIER):
        # Dans le depot publie, le fichier est a la racine, a cote de
        # index.html. Son absence n'est pas une panne : le rapport se fait
        # alors sur la seule page, qui porte les memes notices. Mais elle
        # se dit, faute de quoi on lirait un rapport incomplet en le
        # croyant complet.
        print("  publications.json absent : le rapport se fait sans lui")
        return []
    try:
        j = json.load(open(DOSSIER, encoding="utf-8"))
    except Exception as e:                                       # noqa: BLE001
        print("  publications.json illisible (%s)" % e)
        return []
    return [(w.get("title"), w.get("year"), "publications.json")
            for w in (j.get("works") or []) if w.get("title")]


def _sans_balises(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def de_la_page():
    """Les travaux que la page publie : les notices et les travaux en cours.

    Les seconds comptent : un travail annonce sur la page et absent du CV
    est precisement le genre d'ecart qu'on cherche.
    """
    try:
        s = open(PAGE, encoding="utf-8").read()
    except Exception:                                            # noqa: BLE001
        return []
    out = []
    for m in re.finditer(r'<article class="paper"(.*?)</article>', s, re.S):
        bloc = m.group(1)
        t = re.search(r'class="paper-title"[^>]*>(.*?)</(?:h\d|p)>', bloc, re.S)
        an = re.search(r'data-year="(\d{4})"', m.group(0))
        if t:
            out.append((_sans_balises(t.group(1)),
                        int(an.group(1)) if an else None, "la page"))
    w = re.search(r'<ul class="wip">(.*?)</ul>', s, re.S)
    if w:
        for li in re.findall(r"<li.*?</li>", w.group(1), re.S):
            titre = re.search(r'class="paper-title"[^>]*>(.*?)</(?:h\d|p|b)>',
                              li, re.S)
            titre = _sans_balises(titre.group(1)) if titre else _sans_balises(li)
            # Les travaux en cours portent leurs deux langues cote a cote ;
            # seule la premiere sert a reconnaitre le travail.
            titre = titre.split("  ")[0].strip()
            if titre:
                out.append((titre, None, "travaux en cours"))
    # Les travaux anciens, ceux que la synchronisation ne releve pas parce
    # qu'ils ne vivent que sur RePEc. Ce sont eux, le plus souvent, que le
    # CV et le dossier se renvoient l'un a l'autre.
    # Le reperage se fait sur data-genre, non sur la liste qui les porte :
    # la page compte plusieurs listes de meme classe, dont l'une enumere des
    # ecoles d'ete, et un rapport qui reclamerait qu'on porte une ecole d'ete
    # a la rubrique des publications ne serait pas lu deux fois.
    for genre, li in re.findall(r'<li class="citable"[^>]*data-genre="([^"]+)"'
                                r'[^>]*>(.*?)</li>', s, re.S):
        # Un memoire ou une these se porte a la rubrique des diplomes, non a
        # celle des publications : le CV les nomme deja la, et les reclamer
        # ici reviendrait a demander qu'on les compte deux fois.
        if genre in ("mastersthesis", "phdthesis"):
            continue
        t = re.search(r'<span class="t">(.*?)</span>', li, re.S)
        an = re.search(r'<span class="yr">(\d{4})</span>', li)
        if t:
            out.append((_sans_balises(t.group(1)),
                        int(an.group(1)) if an else None, "travaux anciens"))
    return out


def d_orcid(timeout=30):
    """Les travaux deposes a l'ORCID, ou une liste vide : ce script ne leve pas."""
    url = "https://pub.orcid.org/v3.0/%s/works" % ORCID_ID
    req = urllib.request.Request(url, headers={
        "Accept": "application/json", "User-Agent": "cv-maj-jamwab"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            j = json.loads(r.read().decode("utf-8"))
    except Exception as e:                                       # noqa: BLE001
        print("  ORCID injoignable (%s) : le rapport se fait sans lui" % e)
        return []
    out = []
    for g in j.get("group") or []:
        for s in g.get("work-summary") or []:
            t = ((s.get("title") or {}).get("title") or {}).get("value")
            an = ((s.get("publication-date") or {}).get("year") or {}).get("value")
            if t:
                out.append((t, int(an) if str(an or "").isdigit() else None,
                            "ORCID"))
    return out


# ----------------------------------------------------------------------
# Le curriculum vitae
# ----------------------------------------------------------------------
def _sans_latex(s):
    s = re.sub(r"\\(?:textit|textbf|emph|href)\s*\{", "{", s)
    s = re.sub(r"\\href\s*\{[^}]*\}", "", s)
    s = s.replace("\\&", "&").replace("\\,", " ").replace("\\ ", " ")
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
    s = s.replace("{", " ").replace("}", " ")
    return re.sub(r"\s+", " ", s).strip()


def du_cv(chemin):
    """Les travaux portes a la rubrique des publications d'un fichier LaTeX.

    La rubrique va du \\section des publications au \\section suivant. Chaque
    \\item y est une notice ; le titre est ce qui suit l'annee entre
    parentheses, debarrasse de la revue et des mentions entre parentheses.
    """
    try:
        s = open(chemin, encoding="utf-8").read()
    except Exception:                                            # noqa: BLE001
        return []
    m = re.search(r"\\section\{(?:Publications and research"
                  r"|Publications et travaux de recherche)\}", s)
    if not m:
        return []
    fin = s.find("\\section{", m.end())
    bloc = s[m.end():fin if fin > 0 else len(s)]

    out = []
    for it in re.findall(r"\\item\s+(.*?)(?=\n\s*\\item|\n\s*\\end\{)", bloc, re.S):
        an = re.search(r"\((\d{4})\)", it)
        if an:
            # La notice datee se lit ainsi : auteurs, (annee), titre, puis
            # la revue ou la mention de genre. Le titre s'arrete donc au
            # premier point suivi d'une espace, ou a la parenthese qui
            # ferme la notice.
            titre = _sans_latex(it[an.end():]).lstrip(". ")
            titre = re.split(r"\.\s|\s\(", titre)[0]
        else:
            # Un travail en cours n'a pas d'annee : son titre est le seul
            # passage en italique de la notice.
            t = re.search(r"\\textit\{(.*?)\}", it, re.S)
            titre = _sans_latex(t.group(1)) if t else ""
        titre = titre.strip(" .:,").strip()
        if titre:
            out.append((titre, int(an.group(1)) if an else None, chemin))
    return out


# ----------------------------------------------------------------------
# Le mois porte en pied de page
# ----------------------------------------------------------------------
def date(quand=None):
    """Pose le mois courant au pied des deux fichiers. Rend ce qui a change."""
    quand = quand or dt.date.today()
    faits = []
    for langue, chemin in CV.items():
        mois = (MOIS_EN if langue == "en" else MOIS_FR)[quand.month - 1]
        neuf = "%s %d" % (mois, quand.year)
        s = open(chemin, encoding="utf-8").read()
        # Le pied porte trois mentions separees par \dotsep -- le nom, la
        # nature du document, le mois. Seule la derniere se date, d'ou le
        # quantificateur glouton : il faut le dernier \dotsep, non le premier.
        m = re.search(r"(\\fancyfoot\[L\]\{\\meta\{[^}]*\\dotsep\s+)"
                      r"([^}]*?)(\}\})", s)
        if not m:
            print("  pied de page introuvable dans %s" % os.path.basename(chemin))
            continue
        if m.group(2).strip() == neuf:
            continue
        s = s[:m.start(2)] + neuf + s[m.end(2):]
        open(chemin, "w", encoding="utf-8").write(s)
        faits.append((os.path.basename(chemin), m.group(2).strip(), neuf))
    return faits


# ----------------------------------------------------------------------
def main():
    if "--dater" in sys.argv:
        faits = date()
        if not faits:
            print("le pied de page porte deja le mois courant")
        for nom, avant, apres in faits:
            print("%s : « %s » devient « %s »" % (nom, avant, apres))
        return 0

    dossier = du_dossier() + de_la_page()
    if "--orcid" in sys.argv:
        dossier += d_orcid()

    cv_en, cv_fr = du_cv(CV["en"]), du_cv(CV["fr"])
    print("dossier : %d notices relevees ; CV : %d en anglais, %d en français"
          % (len(dossier), len(cv_en), len(cv_fr)))
    if not cv_en or not cv_fr:
        print("la rubrique des publications du CV n'a pas ete trouvee")
        return 1

    # 1. ce que le dossier porte et que le CV ignore
    manquants = []
    for titre, an, ou in dossier:
        if any(meme(titre, t) for t, _, _ in cv_en):
            continue
        if any(meme(titre, m) for m, _, _ in manquants):
            continue
        manquants.append((titre, an, ou))

    # 2. ce que le CV porte et que le dossier ignore
    inconnus = [(t, a) for t, a, _ in cv_en
                if not any(meme(t, d) for d, _, _ in dossier)]

    # 3. les deux langues portent le meme nombre de notices
    if len(cv_en) != len(cv_fr):
        print("\nles deux CV ne portent pas le meme nombre de notices : "
              "%d en anglais, %d en français" % (len(cv_en), len(cv_fr)))

    if manquants:
        print("\nAbsents du CV (%d) :" % len(manquants))
        for titre, an, ou in sorted(manquants, key=lambda x: -(x[1] or 0)):
            print("  %s  %s  [%s]" % (an or "    ", titre[:78], ou))
    else:
        print("\nLe CV porte tous les travaux que le depot connait.")

    if inconnus:
        print("\nAu CV, inconnus du dossier (%d) — a verifier, non a corriger :"
              % len(inconnus))
        for titre, an in inconnus:
            print("  %s  %s" % (an or "    ", titre[:78]))

    if manquants:
        print("\nLe script ne recrit pas le CV : les notices ci-dessus sont a "
              "porter\na la main dans les deux fichiers LaTeX, puis "
              "« python3 tools/cv_maj.py --dater ».")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
