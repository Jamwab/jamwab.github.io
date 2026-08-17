# -*- coding: utf-8 -*-
"""Tient le journal d'audience du site, sans service tiers et sans cookie.

Le probleme. GitHub Pages sert des fichiers ; il n'execute rien. Une page
statique ne peut donc pas compter ses propres visiteurs : il faut un tiers
qui recoive le coup et le retienne. Les compteurs habituels (GoatCounter,
Plausible, Google Analytics) demandent tous un compte, et deux d'entre eux
posent un traceur chez le lecteur.

La sortie. GitHub compte deja les visites de nos pages et les copies du
depot, et les rend par son interface de programmation :

    GET /repos/{proprietaire}/{depot}/traffic/views
    GET /repos/{proprietaire}/{depot}/traffic/clones

Ces deux releves ne retiennent que quatorze jours. Ce script les lit chaque
nuit et les verse dans data/audience.json, qui, lui, garde tout. Au bout
d'un mois le fichier porte un mois d'histoire ; au bout d'un an, un an. Le
journal vit dans le depot, versionne avec le reste : personne d'autre que
GitHub ne voit passer le lecteur, et le lecteur ne recoit aucun cookie.

Ce qui est compte, et ce qui ne l'est pas. Les « vues » sont les pages
servies, les « visiteurs » les adresses distinctes, les « copies » les
clonages du depot -- c'est-a-dire les lecteurs qui emportent tout le jeu de
donnees d'un coup. Les telechargements piece par piece, eux, sont fabriques
dans le navigateur a partir des donnees deja chargees : aucune requete ne
part vers le serveur, donc aucun serveur ne peut les compter. La page les
compte pour son lecteur seul, et le dit.

Usage :
    python3 tools/audience.py              # actualise data/audience.json
    python3 tools/audience.py --dry-run    # affiche sans ecrire

Le jeton vient de la variable d'environnement GITHUB_TOKEN. Dans une action
GitHub, {{ secrets.GITHUB_TOKEN }} suffit si le travail declare
`permissions: contents: write`. Si l'appel revient en 403, c'est que le
releve d'audience demande un droit que le jeton par defaut n'a pas : creez
un jeton personnel a portee `public_repo` et posez-le en secret sous le nom
AUDIENCE_TOKEN.
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOURNAL = os.path.join(ROOT, "data", "audience.json")
DRY = "--dry-run" in sys.argv

DEPOT = os.environ.get("GITHUB_REPOSITORY", "jamwab/jamwab.github.io")
JETON = (os.environ.get("AUDIENCE_TOKEN")
         or os.environ.get("GITHUB_TOKEN") or "")


def api(chemin):
    """Interroge l'API de GitHub ; rend None plutot que de lever."""
    url = "https://api.github.com/repos/%s/traffic/%s" % (DEPOT, chemin)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "audience-jamwab",
    })
    if JETON:
        req.add_header("Authorization", "Bearer " + JETON)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("  %s : HTTP %s (%s)" % (chemin, e.code, e.reason))
    except Exception as e:
        print("  %s : %s" % (chemin, e))
    return None


def journee(horodatage):
    """« 2026-08-14T00:00:00Z » -> « 2026-08-14 »."""
    return horodatage[:10]


def verse(histoire, releve, bloc):
    """Fond un releve de quatorze jours dans l'histoire deja tenue.

    Un jour deja present est remplace, non additionne : GitHub revise ses
    chiffres pendant quelques heures, et c'est le dernier releve qui fait
    foi. Un jour absent du releve mais present dans l'histoire est laisse
    tel quel -- il est sorti de la fenetre des quatorze jours, il n'est pas
    devenu faux pour autant.
    """
    if not releve:
        return 0
    neufs = 0
    for j in releve.get(bloc) or []:
        d = journee(j.get("timestamp", ""))
        if not d:
            continue
        if d not in histoire:
            neufs += 1
        histoire[d] = {"n": int(j.get("count", 0)), "u": int(j.get("uniques", 0))}
    return neufs


def somme(histoire, cle, depuis=None):
    total = 0
    for d, v in histoire.items():
        if depuis and d < depuis:
            continue
        total += v.get(cle, 0)
    return total


def main():
    if os.path.exists(JOURNAL):
        journal = json.load(open(JOURNAL, encoding="utf-8"))
    else:
        journal = {"vues": {}, "copies": {}}
    journal.setdefault("vues", {})
    journal.setdefault("copies", {})

    print("depot : %s" % DEPOT)
    if not JETON:
        print("  aucun jeton : le releve d'audience est reserve au proprietaire")

    n1 = verse(journal["vues"], api("views"), "views")
    n2 = verse(journal["copies"], api("clones"), "clones")

    if not journal["vues"] and not journal["copies"]:
        print("rien a ecrire : le journal reste en l'etat")
        return 1

    aujourdhui = dt.date.today()
    trente = (aujourdhui - dt.timedelta(days=30)).isoformat()
    debut = min(list(journal["vues"]) + list(journal["copies"]))

    journal["maj"] = aujourdhui.isoformat()
    journal["depuis"] = debut
    journal["total"] = {
        "vues": somme(journal["vues"], "n"),
        "visiteurs": somme(journal["vues"], "u"),
        "copies": somme(journal["copies"], "n"),
    }
    journal["trente_jours"] = {
        "vues": somme(journal["vues"], "n", trente),
        "visiteurs": somme(journal["vues"], "u", trente),
        "copies": somme(journal["copies"], "n", trente),
    }
    journal["source"] = ("GitHub repository traffic API "
                         "(/traffic/views, /traffic/clones)")

    print("  %d jours de vues, %d jours de copies (%d et %d nouveaux)"
          % (len(journal["vues"]), len(journal["copies"]), n1, n2))
    print("  cumul : %(vues)d vues, %(visiteurs)d visiteurs, %(copies)d copies"
          % journal["total"])

    if DRY:
        print("--dry-run : rien n'est ecrit")
        return 0
    with open(JOURNAL, "w", encoding="utf-8") as f:
        json.dump(journal, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("ecrit : data/audience.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
