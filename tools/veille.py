#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La veille des bulletins d'epidemie de l'Organisation mondiale de la sante.

Le probleme. Le volet « Sante et epidemies » de la page porte des chiffres
qui vieillissent vite : l'Organisation publie un bulletin tous les dix a
quinze jours, et chacun peut doubler un decompte. Un lecteur qui arrive sur
la page trois semaines apres sa derniere mise a jour ne voit rien qui le
lui dise. Il lit un chiffre perime en croyant lire le dernier.

La sortie. L'Organisation publie la liste de ses bulletins par une
interface de programmation ouverte, filtrable par pays. Ce script la lit et
la verse dans data/veille.json : le titre de chaque bulletin, sa date, son
identifiant et son adresse. La page, elle, compare l'identifiant du dernier
bulletin paru a celui que ses tableaux citent, et le dit au lecteur quand
les deux different. Le fichier sert de filet : si l'appel echoue depuis le
navigateur, la page se rabat sur le dernier releve verse ici.

Ce que le script ne fait pas. Il ne touche a aucun tableau et ne modifie
aucun chiffre. Relever qu'un bulletin est paru est mecanique ; en tirer les
chiffres ne l'est pas -- il faut lire le texte, distinguer un cas confirme
d'un cas suspect, reperer une reconciliation de donnees. La page annonce
donc la parution et renvoie a la source ; la mise a jour des tableaux reste
un acte de lecture.

Usage :
    python3 tools/veille.py              # actualise data/veille.json
    python3 tools/veille.py --dry-run    # affiche sans ecrire

Le script ne leve jamais : si l'appel echoue, le fichier deja ecrit est
laisse tel quel et le code de sortie vaut 1, ce que l'action GitHub traite
comme un avertissement et non comme une panne.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOURNAL = os.path.join(RACINE, "data", "veille.json")
DRY = "--dry-run" in sys.argv

# L'identifiant de la RD Congo dans la nomenclature de l'Organisation. Il
# figure tel quel dans le filtre de l'interface publique du site.
RDC = "efb17dee-87bf-4f2d-abfa-69f46b84b2e5"

BASE = "https://www.who.int/api/news/diseaseoutbreaknews"
ITEM = "https://www.who.int/emergencies/disease-outbreak-news/item/"

# Le nombre de bulletins retenus. Vingt couvre largement une annee de
# publications pour un seul pays, et le fichier reste minuscule.
COMBIEN = 20


def adresse():
    """L'appel, filtre sur la RD Congo et trie du plus recent au plus ancien."""
    params = [
        ("$filter", "regionscountries/any(t: t eq %s)" % RDC),
        ("$orderby", "PublicationDateAndTime desc"),
        ("$top", str(COMBIEN)),
        ("$select", "Title,DonId,UrlName,PublicationDateAndTime"),
    ]
    return BASE + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)


def interroge(url):
    """Rend la reponse decodee, ou None : ce script ne leve pas."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "veille-jamwab",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("  HTTP %s (%s)" % (e.code, e.reason))
    except Exception as e:                                       # noqa: BLE001
        print("  appel impossible : %s" % e)
    return None


def nettoie(s):
    """Les titres arrivent parfois avec des balises ou des espaces doubles."""
    s = re.sub(r"<[^>]+>", "", str(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def jour(horodatage):
    """« 2026-08-14T00:00:00Z » -> « 2026-08-14 » ; sinon chaine vide."""
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", str(horodatage or ""))
    return m.group(1) if m else ""


def depouille(brut):
    """Range la reponse en une liste de fiches, la plus recente d'abord."""
    if isinstance(brut, dict):
        brut = brut.get("value") or brut.get("Value") or []
    if not isinstance(brut, list):
        return []
    out = []
    for b in brut:
        if not isinstance(b, dict):
            continue
        don = nettoie(b.get("DonId"))
        nom = nettoie(b.get("UrlName"))
        titre = nettoie(b.get("Title"))
        date = jour(b.get("PublicationDateAndTime"))
        if not (don or nom):
            continue
        out.append({
            "id": don or nom,
            "titre": titre,
            "date": date,
            "lien": ITEM + (nom or don),
        })
    out.sort(key=lambda f: (f.get("date") or "", f.get("id") or ""),
             reverse=True)
    return out


def main():
    url = adresse()
    print("veille : %s" % BASE)
    fiches = depouille(interroge(url))
    if not fiches:
        print("aucun bulletin releve : le fichier reste en l'etat")
        return 1

    journal = {
        "maj": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pays": "Congo, République démocratique du",
        "source": ("Organisation mondiale de la santé, Disease Outbreak "
                   "News, interface publique, filtrée sur la RD Congo"),
        "url": url,
        "dernier": fiches[0]["id"],
        "bulletins": fiches,
    }

    print("  %d bulletins, le dernier est %s du %s"
          % (len(fiches), fiches[0]["id"], fiches[0]["date"] or "date inconnue"))
    for f in fiches[:3]:
        print("    %s  %s" % (f["date"] or "          ", f["titre"][:64]))

    if DRY:
        print("--dry-run : rien n'est ecrit")
        return 0
    os.makedirs(os.path.dirname(JOURNAL), exist_ok=True)
    with open(JOURNAL, "w", encoding="utf-8") as f:
        json.dump(journal, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("ecrit : data/veille.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
