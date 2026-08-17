#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Les onglets thematiques de la section « Donnees macroeconomiques ».

Le module rdc_donnees.py porte les chiffres ; celui-ci les met en page.

Il fait trois choses et rien d'autre. Il reecrit la barre d'onglets de la
section entre les reperes RDC:TABS, de sorte que l'ordre de lecture tienne
en un seul endroit. Il rend les nouveaux volets entre les reperes
RDC:PANES, chacun avec son intertitre, son introduction bilingue et ses
tableaux. Il verse enfin chaque tableau dans le registre des series de la
page, ce qui suffit pour que les boutons de telechargement existants le
servent en CSV, en XLSX et en LaTeX sans une ligne de plus.

Les volets deja ecrits a la main -- conjoncture, prix, structure,
population, faits stylises -- ne sont pas touches : le script ne connait
d'eux que leur libelle, pour les remettre dans la barre au bon rang.

Bibliotheque standard seulement.
"""

import csv
import html
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rdc_donnees as D                                          # noqa: E402

DONNEES = os.path.join(RACINE, "data")
CSV = os.path.join(DONNEES, "csv")

TABS = ("<!-- RDC:TABS:START -->", "<!-- RDC:TABS:END -->")
PANES = ("<!-- RDC:PANES:START -->", "<!-- RDC:PANES:END -->")

# Garde-fou : aucun numero de telephone ne doit reparaitre dans la page.
_TEL = re.compile(r"(?:tel:|\+\s?1[\s.\-]?)\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}")


def index():
    """Le fichier de la page, selon que le depot est a plat ou non."""
    for c in (os.path.join(RACINE, "index.html"),
              os.path.join(RACINE, "site", "index.html")):
        if os.path.exists(c):
            return c
    return None


# ----------------------------------------------------------------------
# Rendu
# ----------------------------------------------------------------------
def bilingue(en, fr):
    return ('<span class="l-en">%s</span>'
            '<span class="l-fr" lang="fr">%s</span>'
            % (html.escape(str(en), quote=False),
               html.escape(str(fr), quote=False)))


ESPACE = "\u202f"          # espace fine insecable : le groupement des
                           # milliers en francais


def nombre(v, chiffres):
    """Le meme nombre dans les deux conventions : point decimal et virgule
    de milliers en anglais, virgule decimale et espace fine en francais."""
    en = "{:,.{p}f}".format(v, p=chiffres)
    ent, _, dec = en.partition(".")
    fr = ent.replace(",", ESPACE) + ("," + dec if dec else "")
    return en, fr


def cellule(v, chiffres=2):
    """Une case : bilingue si c'est une paire, numerique si c'est un
    nombre, tiret cadratin si la valeur manque. Le nombre de decimales est
    fixe par colonne, de sorte que la colonne s'aligne sur la virgule."""
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return '<td>%s</td>' % bilingue(v[0], v[1])
    if isinstance(v, bool):
        v = int(v)
    if isinstance(v, (int, float)):
        return '<td class="n">%s</td>' % bilingue(*nombre(v, chiffres))
    if v in ("—", "", None):
        return '<td class="na">&#8212;</td>'
    return '<td>%s</td>' % html.escape(str(v))


AUTEUR = "James Wabenga Yango"


def credit(source_en="", source_fr=""):
    """La note de pied de tableau : qui l'a compose, sur quelles donnees.

    Le renvoi conduit au bloc de citation de la section, de sorte qu'un
    lecteur qui reprend le tableau trouve la reference a un clic.
    """
    en = "Table compiled by %s." % AUTEUR
    fr = "Tableau composé par %s." % AUTEUR
    if source_en:
        en += " Source: " + source_en.rstrip(".") + "."
    if source_fr:
        fr += " Source : " + source_fr.rstrip(".") + "."
    return ('<span class="l-en">%s</span>'
            '<span class="l-fr" lang="fr">%s</span>'
            ' <a class="citelink" href="#citer">'
            '<span class="l-en">How to cite</span>'
            '<span class="l-fr" lang="fr">Comment citer</span></a>'
            % (html.escape(en, quote=False), html.escape(fr, quote=False)))


def rend(cle, fiche):
    """Un tableau, sous la meme forme que les tableaux de faits stylises,
    pour que la feuille de style et les boutons servent les deux."""
    entetes = "".join('<th scope="col">%s</th>' % bilingue(c[0], c[1])
                      for c in fiche["cols"])
    dec = fiche.get("chiffres") or []
    lignes = []
    for r in fiche["rows"]:
        tete = r[0]
        th = '<th scope="row">%s</th>' % (
            bilingue(tete[0], tete[1]) if isinstance(tete, (list, tuple))
            else html.escape(str(tete)))
        lignes.append("<tr>" + th + "".join(
            cellule(v, dec[i] if i < len(dec) else 2)
            for i, v in enumerate(r[1:])) + "</tr>")
    note = bilingue(fiche.get("note_en") or "", fiche.get("note_fr") or "")
    # La citation ne se traduit pas : seul le libelle change de langue.
    source = fiche.get("source") or ""
    if source:
        note += ('</p><p class="note src">'
                 '<span class="l-en">Source:</span>'
                 '<span class="l-fr" lang="fr">Source :</span> %s'
                 % html.escape(source, quote=False))
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
           entetes, "".join(lignes), note, credit(), cle))


def barre():
    """La barre d'onglets, dans l'ordre de lecture de la section."""
    b = ['<div class="tabs" role="tablist" aria-label="Données RD Congo">']
    for i, (cle, titre) in enumerate(D.ORDRE_ONGLETS):
        b.append('<button type="button" role="tab" data-tab="%s" '
                 'aria-selected="%s">%s</button>'
                 % (cle, "true" if i == 0 else "false",
                    bilingue(titre[0], titre[1])))
    b.append("</div>")
    return "".join(b)


def garde(page, nom):
    """Le contenu deja pose entre les deux reperes d'une zone de planches.

    Les planches sont ecrites par tools/gg_inject.py, non par ce script.
    Quand celui-ci refait les volets, il doit donc rendre la zone telle
    qu'il l'a trouvee, faute de quoi les figures disparaitraient de la
    page a chaque passage des tableaux, jusqu'au prochain trace.
    """
    d, f = "<!-- %s:START -->" % nom, "<!-- %s:END -->" % nom
    a, b = page.find(d), page.find(f)
    return page[a + len(d):b] if 0 <= a < b else ""


_DON = re.compile(r"\b(\d{4})-DON(\d+)\b")


def dernier_bulletin(onglet):
    """Le bulletin le plus recent que les tableaux du volet citent.

    Il est releve dans les sources elles-memes plutot que declare a part :
    le jour ou un tableau passera au bulletin suivant, la veille de la page
    suivra sans qu'on ait a y penser. Un volet qui ne cite aucun bulletin
    n'en rend aucun, et la veille se tait.
    """
    vus = []
    for _, fiche in onglet.get("tableaux") or []:
        for m in _DON.finditer(str(fiche.get("source") or "")):
            vus.append((int(m.group(1)), int(m.group(2))))
    if not vus:
        return ""
    a, n = max(vus)
    return "%04d-DON%d" % (a, n)


def veille(onglet):
    """La ligne d'alerte du volet, vide tant que la page n'a rien appris.

    Elle est posee ici mais remplie dans le navigateur : la page compare le
    dernier bulletin paru a celui que ses tableaux citent, et ne dit
    quelque chose que lorsque les deux different. Sans script, la ligne
    reste cachee -- un lecteur ne verra jamais une alerte vide, et les
    tableaux, eux, portent leur date en toutes lettres.
    """
    cle = dernier_bulletin(onglet)
    if not cle:
        return ""
    return ('<p class="veille" id="veille-%s" data-bulletin="%s" hidden></p>'
            % (onglet["cle"], html.escape(cle, quote=True)))


def volet(onglet, page=""):
    """Un volet : intertitre, introduction bilingue, puis les tableaux.

    Un volet peut en outre reserver une zone a ses planches ; elle est
    posee entre l'introduction et les tableaux, la ou le lecteur regarde
    d'abord la forme avant d'aller chercher le chiffre."""
    p = ['<div class="tabpane" data-pane="%s" hidden>' % onglet["cle"]]
    p.append("<h3>%s</h3>" % bilingue(onglet["intertitre"][0],
                                      onglet["intertitre"][1]))
    p.append('<p class="l-en">%s</p>'
             % html.escape(onglet["intro_en"], quote=False))
    p.append('<p class="l-fr" lang="fr">%s</p>'
             % html.escape(onglet["intro_fr"], quote=False))
    if onglet.get("veille"):
        p.append(veille(onglet))
    nom = onglet.get("figures")
    if nom:
        p.append("<!-- %s:START -->%s<!-- %s:END -->"
                 % (nom, garde(page, nom), nom))
    for cle, fiche in onglet["tableaux"]:
        p.append(rend(cle, fiche))
    p.append("</div>")
    return "".join(p)


# ----------------------------------------------------------------------
# Fichiers
# ----------------------------------------------------------------------
def ecrit_csv(cle, fiche):
    """Le tableau au format texte, a cote des autres series du depot."""
    os.makedirs(CSV, exist_ok=True)
    chemin = os.path.join(CSV, cle + ".csv")
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([c[0] for c in fiche["cols"]])
        for r in fiche["rows"]:
            w.writerow([v[0] if isinstance(v, (list, tuple)) else v
                        for v in r])
    return chemin


def fin_de_bloc(txt, i):
    """La position juste apres le </div> qui ferme le div ouvert en i."""
    prof = 0
    for m in re.finditer(r"</?div\b[^>]*>", txt[i:]):
        prof += 1 if m.group(0)[1] != "/" else -1
        if prof == 0:
            return i + m.end()
    raise ValueError("div non ferme a la position %d" % i)


def volets_existants(zone):
    """Les volets deja ecrits a la main, releves tels quels.

    Ils sont rendus a l'identique : le script ne se mele pas de leur
    contenu, il ne fait que les remettre dans l'ordre voulu."""
    trouves, i = {}, 0
    while True:
        m = re.compile(r'<div class="tabpane" data-pane="([^"]+)"').search(
            zone, i)
        if not m:
            return trouves
        j = fin_de_bloc(zone, m.start())
        trouves[m.group(1)] = zone[m.start():j]
        i = j


def remplace(page, reperes, neuf):
    a, b = page.find(reperes[0]), page.find(reperes[1])
    if a < 0 or b < 0 or b < a:
        return None
    return page[:a + len(reperes[0])] + neuf + page[b:]


def main():
    chemin = index()
    if not chemin:
        print("index.html introuvable sous", RACINE)
        return 1
    page = open(chemin, encoding="utf-8").read()

    fiches = {}
    for onglet in D.ONGLETS:
        for cle, fiche in onglet["tableaux"]:
            fiches[cle] = fiche

    # 1. Le registre des series : les boutons y puisent les fichiers.
    mreg = re.search(r'(<!-- SERIES:START --><script type="application/json" '
                     r'id="series-data">)(.*?)(</script><!-- SERIES:END -->)',
                     page, re.S)
    if not mreg:
        print("Registre des series introuvable, rien n'est ecrit.")
        return 1
    reg = json.loads(mreg.group(2))
    reg.update(fiches)
    page = (page[:mreg.start()] + mreg.group(1)
            + json.dumps(reg, ensure_ascii=False, separators=(",", ":"))
            + mreg.group(3) + page[mreg.end():])
    print("  registre : %d series au total" % len(reg))

    # 2. La barre d'onglets, puis les volets.
    page = remplace(page, TABS, barre())
    if page is None:
        print("Zone RDC:TABS absente.")
        return 1

    a, b = page.find(PANES[0]), page.find(PANES[1])
    if a < 0 or b < a:
        print("Zone RDC:PANES absente.")
        return 1
    anciens = volets_existants(page[a + len(PANES[0]):b])
    neufs = {o["cle"]: volet(o, page) for o in D.ONGLETS}
    corps = []
    for cle, _ in D.ORDRE_ONGLETS:
        bloc = neufs.get(cle) or anciens.get(cle)
        if not bloc:
            print("  volet %s introuvable, onglet sans contenu" % cle)
            continue
        corps.append(bloc)
    manquants = set(anciens) - {c for c, _ in D.ORDRE_ONGLETS}
    if manquants:
        print("  volets hors ordre, laisses en fin :", ", ".join(manquants))
        corps += [anciens[c] for c in sorted(manquants)]
    page = remplace(page, PANES, "\n".join(corps))
    print("  volets : %d repris tels quels, %d ecrits ici"
          % (len([c for c in anciens if c not in neufs]), len(neufs)))

    if _TEL.search(page):
        print("Garde-fou : un numero de telephone apparait, ecriture annulee.")
        return 1

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(page)

    # 3. Les fichiers CSV et le registre tenu sur le disque.
    for cle, fiche in fiches.items():
        ecrit_csv(cle, fiche)
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

    print("%d onglets, %d tableaux publies."
          % (len(D.ORDRE_ONGLETS), len(fiches)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
