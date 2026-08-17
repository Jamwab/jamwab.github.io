#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publie les planches tracees par ggplot2.

Le script lit les SVG ecrits par tools/figures.R dans build/gg/svg/, les
verifie un par un, les assainit, les depose dans figures/ puis reecrit la
zone balisee <!-- GG:FIGS:START --> ... <!-- GG:FIGS:END --> de index.html.

Les figures sont publiees comme fichiers distincts plutot qu'inserees dans
la page : le lecteur peut les telecharger, le navigateur les met en cache,
et le depot ne recoit chaque nuit que les images reellement modifiees.

Assainissement, dans l'ordre :
  1. tout ce qui precede la balise <svg> est ecarte ;
  2. les attributs width et height du <svg> racine sont retires pour que la
     figure epouse la largeur de sa colonne ; le viewBox est conserve ;
  3. la famille de caracteres est alignee sur celle du site ;
  4. le document est relu par un analyseur XML : une figure qui ne se relit
     pas est ecartee sans toucher aux autres.

Si aucune figure valable n'est trouvee, la page n'est pas modifiee : mieux
vaut une planche absente qu'une page cassee.
"""

import datetime as dt
import html
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(RACINE, "build", "gg", "svg")


def _page():
    """Trouve la page a modifier, et le dossier des figures a cote d'elle.

    L'arbre de travail tient la page sous site/ ; le depot livre, lui, la
    porte a sa racine. Le script sert les deux, et depose toujours les
    images dans le dossier figures/ voisin de la page qui les cite --
    autrement le src rendu ne designerait rien.
    """
    for base in (os.path.join(RACINE, "site"), RACINE):
        p = os.path.join(base, "index.html")
        if os.path.exists(p):
            return p, os.path.join(base, "figures")
    return os.path.join(RACINE, "index.html"), os.path.join(RACINE, "figures")


PAGE, FIGURES = _page()

DEBUT = "<!-- GG:FIGS:START -->"
FIN = "<!-- GG:FIGS:END -->"

# Une planche se lit a cote du tableau qui la nourrit. Les planches
# macroeconomiques vivent donc dans le volet des faits stylises, et celles
# qui portent sur les epidemies dans le volet de la sante. Le tri se fait
# sur le prefixe de la cle, qui est deja celui du tableau d'ou vient la
# serie ; une zone absente de la page renvoie ses planches a la premiere,
# de sorte qu'une page plus ancienne reste servie.
ZONES = [("SANTE:FIGS", lambda c: c.startswith("sante-")),
         ("GG:FIGS", lambda c: True)]

POLICE = ("Iowan Old Style, Palatino Linotype, Palatino, "
          "Georgia, Cambria, serif")

# Garde-fou : aucun numero de telephone ne doit jamais reparaitre dans la
# page. L'expression ne contient elle-meme aucun chiffre de numero.
_TEL = re.compile(r"(?:tel:|\+\s?1[\s.\-]?)\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}")

# Les planches sont composees ici : le cartouche de la page et l'image
# elle-meme portent la meme mention de droits, millesimee a la date de
# fabrication.
DROITS = "\u00a9 %d James Wabenga Yango" % dt.date.today().year

# L'ordre des planches sur la page ; les cles inconnues suivent, par ordre
# alphabetique, de sorte qu'une figure ajoutee plus tard apparaisse sans
# qu'il faille modifier ce script.
ORDRE = ["sf-niveaux", "sf-cycles", "sf-xcorr", "sf-regimes",
         "sf-vulnerabilites", "sf-filtres", "sf-lambda",
         "sf-structure", "sf-secteur-cle",
         "sf-exportations",
         "pib-croissance", "inflation-longue", "pib-indice",
         "taux-directeur", "prix-indices-hist", "pop-top15",
         # Le volet de la sante se lit dans cet ordre : le mouvement de
         # l'epidemie d'abord, puis les seize qui l'ont precedee, puis les
         # zones de sante ou elle se concentre.
         "sante-ebola-trajectoire", "sante-ebola-histoire",
         "sante-ebola-zones"]

# La famille des filtres : une planche par agregat macroeconomique, cinq
# panneaux chacune. Ces planches ne se lisent pas a la suite mais l'une a
# la place de l'autre, et le poseur les enferme dans un selecteur.
#
# Elles se rangent la ou l'ordre ci-dessus nomme « sf-filtres », c'est-a-dire
# juste apres la planche d'ouverture qui montre ce qu'un filtre fait ; leur
# ordre entre elles est celui du plan, donc celui des panneaux fixe par
# sf_prepare.py. Ajouter un agregat la-bas suffit : rien ici ne bouge.
FAMILLE = re.compile(r"^sf-filtres-.")


def assainit(source):
    """Rend le SVG utilisable comme image de page, ou leve une exception."""
    i = source.find("<svg")
    if i < 0:
        raise ValueError("aucune balise <svg>")
    s = source[i:]

    j = s.find(">")
    if j < 0:
        raise ValueError("balise racine incomplete")
    racine, reste = s[:j + 1], s[j + 1:]
    if "viewBox" not in racine:
        raise ValueError("viewBox absent : la figure ne pourrait pas "
                         "se redimensionner")
    racine = re.sub(r"\s(?:width|height)=(['\"])[^'\"]*\1", "", racine)
    s = racine + reste

    s = re.sub(r"font-family:\s*(?:sans|sans-serif|Helvetica|Arial)\s*;",
               "font-family: " + POLICE + ";", s)
    s = re.sub(r"font-family=(['\"])(?:sans|sans-serif|Helvetica|Arial)\1",
               'font-family="' + POLICE + '"', s)

    ET.fromstring(s)          # le document doit etre bien forme
    if _TEL.search(s):
        raise ValueError("garde-fou : un numero de telephone apparait "
                         "dans la figure")
    return s.strip() + "\n"


def charge_plan():
    """Reunit les plans des deux preparateurs, gg_prepare et sf_prepare."""
    plan = {}
    for nom in ("plan.json", "plan-sf.json"):
        p = os.path.join(RACINE, "build", "gg", nom)
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                for fiche in json.load(f):
                    plan[fiche["cle"]] = fiche
        except Exception:
            continue
    return plan


def format_taille(fiche):
    """Rend la taille de trace, en pouces puis en centimetres."""
    try:
        l = float(fiche.get("largeur") or 0)
        h = float(fiche.get("hauteur") or 0)
    except (TypeError, ValueError):
        return None
    if l <= 0 or h <= 0:
        return None
    return (u"%.1f \u00d7 %.1f po (%.0f \u00d7 %.0f mm)"
            % (l, h, l * 25.4, h * 25.4)).replace(".", ",")


def bilingue(en, fr):
    return ('<span class="l-en">%s</span>'
            '<span class="l-fr" lang="fr">%s</span>'
            % (html.escape(en), html.escape(fr)))


AUTEUR = "James Wabenga Yango"


def credit(fiche):
    """La note de bas de planche : qui l'a composee, sur quelles donnees.

    La mention suit la figure partout ou elle va : elle est ecrite dans le
    SVG telecharge par le traceur, et repetee ici sous l'image pour le
    lecteur qui consulte la page. Le renvoi conduit au bloc de citation.
    """
    src_en = str(fiche.get("source_en") or "").strip()
    src_fr = str(fiche.get("source_fr") or "").strip()
    en = "Figure by %s." % AUTEUR
    fr = "Figure de %s." % AUTEUR
    if src_en:
        en += " Source: " + src_en.rstrip(".") + "."
    if src_fr:
        fr += " Source : " + src_fr.rstrip(".") + "."
    return ('<span class="l-en">%s</span>'
            '<span class="l-fr" lang="fr">%s</span>'
            ' <a class="citelink" href="#citer">'
            '<span class="l-en">How to cite</span>'
            '<span class="l-fr" lang="fr">Comment citer</span></a>'
            % (html.escape(en), html.escape(fr)))


def selecteur(famille, plan):
    """Enferme les planches d'une famille dans un selecteur d'agregat.

    Sans script, la barre de boutons reste cachee et les dix-sept planches
    se lisent a la suite : la page dit alors tout ce qu'elle sait, ce qui
    est le seul repli honnete. Le script montre la barre et n'en laisse
    qu'une visible ; c'est un confort de lecture, non une condition.
    """
    boutons = []
    for i, (cle, _) in enumerate(famille):
        fiche = plan.get(cle) or {}
        en = str(fiche.get("choix_en") or cle)
        fr = str(fiche.get("choix_fr") or cle)
        boutons.append(
            '<button type="button" data-fig="fig-%s" aria-pressed="%s">%s</button>'
            % (cle, "true" if i == 0 else "false", bilingue(en, fr)))

    # La note de procede voyage avec la premiere planche de la famille et
    # se lit une fois, sous la derniere.
    note = ""
    for cle, _ in famille:
        fiche = plan.get(cle) or {}
        pen = fiche.get("note_en") or []
        pfr = fiche.get("note_fr") or []
        if pen and pfr:
            note = ('<div class="ggnote"><p class="ggnote-titre">%s</p>%s</div>'
                    % (bilingue("Procedure", "Procédure"),
                       "".join("<p>%s</p>" % bilingue(a, b)
                               for a, b in zip(pen, pfr))))
            break

    return ('<div class="ggpick" id="pick-filtres">'
            '<div class="pickbar" role="group" aria-label="Aggregate / Agrégat"'
            ' hidden><span class="picklabel">%s</span>%s</div>%s%s</div>'
            % (bilingue("Aggregate", "Agrégat"), "".join(boutons),
               "".join(b for _, b in famille), note))


def assemble(paires, plan):
    """Rend le contenu d'une zone, familles enfermees dans leur selecteur."""
    out, i = [], 0
    while i < len(paires):
        if not FAMILLE.match(paires[i][0]):
            out.append(paires[i][1])
            i += 1
            continue
        j = i
        while j < len(paires) and FAMILLE.match(paires[j][0]):
            j += 1
        out.append(selecteur(paires[i:j], plan))
        i = j
    return "".join(out)


def main():
    if not os.path.isdir(SVG):
        print("Aucun dossier %s : rien a publier." % SVG)
        return 1
    plan = charge_plan()

    trouvees = {}
    for nom in os.listdir(SVG):
        m = re.match(r"^(.+)-(en|fr)\.svg$", nom)
        if m:
            trouvees.setdefault(m.group(1), {})[m.group(2)] = nom

    cles = []
    for c in ORDRE:
        if c in trouvees:
            cles.append(c)
        if c == "sf-filtres":
            cles += [k for k in plan if FAMILLE.match(k) and k in trouvees]
    cles += sorted(c for c in trouvees if c not in cles)

    os.makedirs(FIGURES, exist_ok=True)
    morceaux, publiees, poids = [], [], 0
    ou = {}
    for cle in cles:
        paire = trouvees[cle]
        if "en" not in paire or "fr" not in paire:
            print("  %s : une seule langue disponible, planche ecartee" % cle)
            continue
        propres = {}
        for langue in ("en", "fr"):
            try:
                with open(os.path.join(SVG, paire[langue]), encoding="utf-8") as f:
                    propres[langue] = assainit(f.read())
            except Exception as e:
                print("  %s (%s) : ecartee, %s" % (cle, langue, e))
                propres = None
                break
        if not propres:
            continue

        fiche = plan.get(cle) or {}
        for langue, contenu in propres.items():
            chemin = os.path.join(FIGURES, "%s-%s.svg" % (cle, langue))
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(contenu)
            poids += len(contenu.encode("utf-8"))
            publiees.append(os.path.basename(chemin))

        titre_en = str(fiche.get("titre_en") or cle.replace("-", " "))
        titre_fr = str(fiche.get("titre_fr") or cle.replace("-", " "))
        sous_en = str(fiche.get("sous_en") or "")
        sous_fr = str(fiche.get("sous_fr") or "")
        alt_en = titre_en + (". " + sous_en if sous_en else "")
        alt_fr = titre_fr + (". " + sous_fr if sous_fr else "")
        taille = format_taille(fiche)
        # La planche sort de figures.R quand R est installe, et du traceur
        # de secours sinon : la mention ne nomme donc pas l'outil.
        marque_en = "vector figure"
        marque_fr = "figure vectorielle"
        if taille:
            marque_en += " \u00b7 " + taille.replace(",", ".").replace("po", "in")
            marque_fr += " \u00b7 " + taille
        # La planche est composee par l'auteur a partir de sources publiees :
        # le cartouche le dit, comme l'image elle-meme, pour que la mention
        # suive le fichier telecharge aussi bien que la page.
        marque_en += " \u00b7 " + DROITS
        marque_fr += " \u00b7 " + DROITS
        # Une planche dessinee large -- les facettes mensuelles, les
        # correlations croisees -- occupe toute la colonne : c'est la seule
        # facon de laisser respirer l'axe des abscisses. Le critere est la
        # largeur de trace elle-meme, de sorte qu'une planche ajoutee plus
        # tard se place d'elle-meme.
        try:
            large = float(fiche.get("largeur") or 0) >= 10.0
        except (TypeError, ValueError):
            large = False
        morceaux.append(
            '<figure class="ggfig%s" id="fig-%s">'
            '<img class="l-en" src="figures/%s-en.svg" alt="%s" loading="lazy" decoding="async">'
            '<img class="l-fr" lang="fr" src="figures/%s-fr.svg" alt="%s" loading="lazy" decoding="async">'
            '<figcaption class="ggstamp">%s '
            '<a class="ggdl" href="figures/%s-en.svg" download hreflang="en">SVG&nbsp;EN</a> '
            '<a class="ggdl" href="figures/%s-fr.svg" download hreflang="fr">SVG&nbsp;FR</a>'
            '</figcaption>'
            '<p class="ggsource">%s</p>'
            '</figure>'
            % (" ggfig-large" if large else "", cle,
               cle, html.escape(alt_en, quote=True),
               cle, html.escape(alt_fr, quote=True),
               bilingue(marque_en, marque_fr),
               cle, cle,
               credit(fiche)))
        ou[len(morceaux) - 1] = cle
        print("  %s : deux langues publiees" % cle)

    if not morceaux:
        print("Aucune planche valable : la page reste en l'etat.")
        return 1

    # Les figures disparues du plan ne doivent pas trainer dans le depot.
    for nom in sorted(os.listdir(FIGURES)):
        if nom.endswith(".svg") and nom not in publiees:
            os.remove(os.path.join(FIGURES, nom))
            print("  %s : figure devenue inutile, retiree" % nom)

    with open(PAGE, encoding="utf-8") as f:
        page = f.read()

    # Chaque planche part vers la premiere zone qui la reclame et qui
    # existe reellement dans la page.
    presentes = [(z, p) for z, p in ZONES
                 if ("<!-- %s:START -->" % z) in page
                 and ("<!-- %s:END -->" % z) in page]
    if not presentes:
        print("Zone %s absente de index.html." % DEBUT)
        return 1
    lots = {z: [] for z, _ in presentes}
    for i, bloc in enumerate(morceaux):
        cle = ou.get(i, "")
        for z, p in presentes:
            if p(cle):
                lots[z].append((cle, bloc))
                break

    for z, _ in presentes:
        d, f_ = "<!-- %s:START -->" % z, "<!-- %s:END -->" % z
        a, b = page.find(d), page.find(f_)
        if b < a:
            print("Zone %s mal formee." % z)
            return 1
        neuf = ('<div class="ggwrap">' + assemble(lots[z], plan) + "</div>"
                if lots[z] else "")
        page = page[:a + len(d)] + neuf + page[b:]
        print("  zone %-10s : %d planche(s)" % (z, len(lots[z])))

    if _TEL.search(page):
        print("Garde-fou : un numero de telephone apparait dans la page, "
              "ecriture annulee.")
        return 1

    shutil.copyfile(PAGE, PAGE + ".bak")
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(page)
    print("%d planches publiees dans figures/ (%.0f Ko) et referencees "
          "dans index.html." % (len(morceaux), poids / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
