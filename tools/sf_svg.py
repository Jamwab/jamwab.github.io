#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trace les figures du site sans R, en ecrivant le SVG a la main.

tools/figures.R reste la reference : c'est lui qui tourne chaque nuit sur
le serveur d'integration, ou ggplot2 et svglite sont installes. Ce module
est la roue de secours, pour les postes ou R fait defaut : il lit les
memes plans, build/gg/plan.json et build/gg/plan-sf.json, les memes CSV
prepares par gg_prepare.py et sf_prepare.py, et depose les memes fichiers
build/gg/svg/<cle>-<langue>.svg, de sorte que tools/gg_inject.py tourne
sans une ligne de changement.

Il reprend de figures.R la palette, la typographie et la geometrie de
chaque type de planche. Il n'imite pas ggplot2 dans le detail : les
graduations trop serrees sont eclaircies et les intitules de facette sont
replies sur deux lignes, faute de quoi une planche de dix-sept panneaux
sur huit centimetres et demi serait illisible.

Chaque figure est tracee a l'abri d'un try, comme dans figures.R : une
serie malformee ne fait pas tomber les autres, et le script se termine
avec le code 0 des qu'au moins une image a ete ecrite.

Bibliotheque standard seulement.
"""

import csv
import datetime
import json
import math
import os
import re
import sys
import unicodedata

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(RACINE, "build", "gg")
SORTIE = os.path.join(DOSSIER, "svg")

# Garde-fou : aucun numero de telephone ne doit jamais reparaitre dans une
# figure. L'expression ne contient elle-meme aucun chiffre de numero.
_TEL = re.compile(r"(?:tel:|\+\s?1[\s.\-]?)\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}")

# ----------------------------------------------------------------------
# Palette et typographie, reprises de figures.R
# ----------------------------------------------------------------------
PINE = "#002147"
BRASS = "#8A6A18"
ENCRE = "#22201C"
MUET = "#6F6B62"
FILET = "#E3DFD4"

CM = 28.3465                      # un centimetre, en points typographiques

BASE = 9.5                        # theme_wabenga(base = 9.5)
T_TITRE = BASE * 1.28
T_SOUS = BASE * 0.94
T_SOURCE = BASE * 0.82
T_AXE_TITRE = BASE * 0.88
T_AXE = BASE * 0.86
T_LEGENDE = BASE * 0.86
T_BANDE = 8.2                     # intitule de facette
T_AXE_F = 7.4                     # graduations des planches a facettes

INTERLIGNE = 1.16
GG_PT = 2.845276               # .pt : la taille des geom_text, en points
MARGE_H, MARGE_D, MARGE_B, MARGE_G = 4.0, 8.0, 4.0, 4.0

# Les planches sont dessinees ici, a partir de sources publiees : la
# composition appartient a l'auteur et chaque image la revendique. Le
# millesime suit la date de fabrication, de sorte qu'une planche refaite
# l'annee prochaine porte l'annee prochaine.
AUTEUR = "James Wabenga Yango"
DROITS = "\u00a9 %d %s" % (datetime.date.today().year, AUTEUR)
ESPACE = " "                 # espace fine insecable

# ----------------------------------------------------------------------
# Mesure du texte. Les chasses de l'Helvetica, en milliemes de cadratin :
# elles suffisent pour replier les phrases et pour reserver la gouttiere
# des graduations.
# ----------------------------------------------------------------------
_W = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667,
    "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584,
    "?": 556, "@": 1015, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556,
    "`": 333, "{": 334, "|": 260, "}": 334, "~": 584,
    "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556,
    "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556,
    "o": 556, "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556,
    "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
    "’": 191, "‘": 191, "“": 333, "”": 333,
    "–": 556, "—": 1000, "…": 1000, "−": 584,
    "«": 500, "»": 500, "·": 278, "×": 584,
    "°": 400, " ": 278, ESPACE: 200,
}


def chasse(c):
    """La chasse d'un caractere ; les lettres accentuees suivent leur base."""
    if c in _W:
        return _W[c]
    d = unicodedata.normalize("NFD", c)
    return _W.get(d[0], 500)


# gg_inject.py remplace la police par la serie a empattements du site,
# plus large que l'Helvetica dont on tient les chasses : on se donne du
# mou, faute de quoi les etiquettes se toucheraient une fois la figure
# posee dans la page.
MOU = 1.08


def larg(txt, taille, gras=False):
    """La largeur d'une chaine, en points."""
    n = sum(chasse(c) for c in str(txt))
    return n / 1000.0 * taille * MOU * (1.06 if gras else 1.0)


def enveloppe(txt, largeur, taille, gras=False, maxi=0):
    """Replie une phrase sur la largeur donnee, mot a mot.

    maxi borne le nombre de lignes : au-dela, la derniere est coupee et
    close par des points de suspension, comme le ferait une etiquette de
    facette trop longue pour son panneau."""
    txt = str(txt or "").strip()
    if not txt:
        return []
    lignes, courante = [], ""
    for mot in txt.split():
        essai = (courante + " " + mot) if courante else mot
        if courante and larg(essai, taille, gras) > largeur:
            lignes.append(courante)
            courante = mot
        else:
            courante = essai
    if courante:
        lignes.append(courante)
    if maxi and len(lignes) > maxi:
        lignes = lignes[:maxi]
        fin = lignes[-1]
        while fin and larg(fin + "…", taille, gras) > largeur:
            fin = fin[:-1].rstrip()
        lignes[-1] = fin + "…"
    return lignes


# ----------------------------------------------------------------------
# Ecriture du SVG
# ----------------------------------------------------------------------
def echappe(t):
    """Les trois caracteres reserves ; les accents restent en clair."""
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def num(v):
    """Un nombre pour un attribut SVG, sans exposant ni zeros inutiles."""
    if v != v or v in (float("inf"), float("-inf")):
        v = 0.0
    return ("%.2f" % v).rstrip("0").rstrip(".") or "0"


class Toile(object):
    """Le SVG en cours d'ecriture : une suite de fragments."""

    def __init__(self, largeur, hauteur):
        self.w = largeur
        self.h = hauteur
        self.corps = []

    # -- primitives ----------------------------------------------------
    def ligne(self, x1, y1, x2, y2, couleur, epaisseur=0.4, pointille=None):
        d = ' stroke-dasharray="%s"' % pointille if pointille else ""
        self.corps.append(
            '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
            'stroke-width="%s"%s/>'
            % (num(x1), num(y1), num(x2), num(y2), couleur,
               num(epaisseur), d))

    def rect(self, x, y, w, h, remplissage, opacite=1.0):
        if w <= 0 or h <= 0:
            return
        o = '' if opacite >= 1 else ' fill-opacity="%.3g"' % opacite
        self.corps.append(
            '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"%s/>'
            % (num(x), num(y), num(w), num(h), remplissage, o))

    def polyligne(self, points, couleur, epaisseur=0.6, pointille=None):
        if len(points) < 2:
            return
        d = ' stroke-dasharray="%s"' % pointille if pointille else ""
        p = " ".join("%s,%s" % (num(a), num(b)) for a, b in points)
        self.corps.append(
            '<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%s" stroke-linejoin="round" '
            'stroke-linecap="round"%s/>' % (p, couleur, num(epaisseur), d))

    def polygone(self, points, remplissage, opacite=1.0):
        if len(points) < 3:
            return
        o = '' if opacite >= 1 else ' fill-opacity="%.3g"' % opacite
        p = " ".join("%s,%s" % (num(a), num(b)) for a, b in points)
        self.corps.append('<polygon points="%s" fill="%s" stroke="none"%s/>'
                          % (p, remplissage, o))

    def rond(self, x, y, r, couleur):
        self.corps.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
                          % (num(x), num(y), num(r), couleur))

    def texte(self, x, y, contenu, taille, couleur, ancre="start",
              gras=False, rotation=0.0, opacite=1.0):
        contenu = str(contenu)
        if not contenu.strip():
            return
        a = {"start": "", "middle": ' text-anchor="middle"',
             "end": ' text-anchor="end"'}[ancre]
        g = ' font-weight="bold"' if gras else ""
        r = (' transform="rotate(%s %s %s)"'
             % (num(rotation), num(x), num(y))) if rotation else ""
        o = '' if opacite >= 1 else ' fill-opacity="%.3g"' % opacite
        self.corps.append(
            '<text x="%s" y="%s" font-size="%s" fill="%s"%s%s%s%s>%s</text>'
            % (num(x), num(y), num(taille), couleur, a, g, r, o,
               echappe(contenu)))

    # -- assemblage ----------------------------------------------------
    def rendu(self):
        """Le document complet. La famille de caracteres est posee une
        fois sur le groupe racine : gg_inject.py la remplace par celle du
        site, et le viewBox laisse la figure epouser sa colonne."""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="%spt" '
            'height="%spt" viewBox="0 0 %s %s">\n'
            '<g font-family="sans">\n%s\n</g>\n</svg>\n'
            % (num(self.w), num(self.h), num(self.w), num(self.h),
               "\n".join(self.corps)))


def bloc(t, x, y, lignes, taille, couleur, gras=False):
    """Un paragraphe deja replie ; rend l'ordonnee juste apres."""
    for l in lignes:
        t.texte(x, y + taille * 0.78, l, taille, couleur, gras=gras)
        y += taille * INTERLIGNE
    return y


# ----------------------------------------------------------------------
# Nombres. Meme convention que nombre() dans tools/rdc_themes.py : point
# decimal et virgule de milliers en anglais, virgule decimale et espace
# fine insecable en francais.
# ----------------------------------------------------------------------
def nombre(v, chiffres, fr):
    en = "{:,.{p}f}".format(v, p=chiffres)
    if not fr:
        return en
    ent, _, dec = en.partition(".")
    return ent.replace(",", ESPACE) + ("," + dec if dec else "")


def sans_zeros(t, fr):
    """drop0trailing : la queue de zeros decimaux tombe."""
    sep = "," if fr else "."
    if sep in t:
        t = t.rstrip("0").rstrip(sep)
    return t or "0"


def fmt(v, fr, chiffres=2, groupe=True):
    """Une graduation, drop0trailing comme le veut fmt_nombre() dans
    figures.R. Sans groupement, c'est le format() de base : ainsi les
    millesimes de l'axe des abscisses ne prennent pas de separateur de
    milliers, que ggplot2 ne leur donne pas non plus."""
    if not groupe:
        t = ("%.*f" % (chiffres, v))
        if fr:
            t = t.replace(".", ",")
    else:
        t = nombre(v, chiffres, fr)
    t = sans_zeros(t, fr)
    return "0" if t in ("-0", "−0") else t


# ----------------------------------------------------------------------
# Echelles et graduations
# ----------------------------------------------------------------------
class Ech(object):
    """Une echelle lineaire : un intervalle de donnees vers des points."""

    def __init__(self, lo, hi, a, b, marge=0.05):
        lo, hi = float(lo), float(hi)
        if not (hi > lo):
            d = abs(hi) * 0.1 or 0.5
            lo, hi = lo - d, hi + d
        e = (hi - lo) * marge
        self.lo, self.hi = lo - e, hi + e
        self.a, self.b = float(a), float(b)

    def __call__(self, v):
        return self.a + (float(v) - self.lo) / (self.hi - self.lo) * (self.b - self.a)

    def dedans(self, v):
        return self.lo - 1e-9 <= v <= self.hi + 1e-9


def jolis(lo, hi, n=5):
    """L'equivalent de pretty() : un pas rond, des bornes rondes."""
    lo, hi = float(lo), float(hi)
    if not (hi > lo):
        hi = lo + (abs(lo) * 0.1 or 1.0)
    brut = (hi - lo) / max(1, n)
    if brut <= 0:
        return [lo]
    exp = math.floor(math.log10(brut))
    f = brut / (10 ** exp)
    for c in (1.0, 2.0, 2.5, 5.0, 10.0):
        if f <= c * 1.0000001:
            pas = c * (10 ** exp)
            break
    deb = math.floor(lo / pas) * pas
    ticks, k = [], 0
    while deb + k * pas <= hi + pas * 1e-6 and k < 400:
        ticks.append(deb + k * pas)
        k += 1
    return ticks


def decimales(pas):
    """Le nombre de decimales qu'exige un pas de graduation."""
    pas = abs(float(pas))
    if pas <= 0:
        return 0
    d, p = 0, pas
    while abs(p - round(p)) > 1e-7 and d < 6:
        p *= 10
        d += 1
    return d


def graduations(lo, hi, n, fr, entier=False):
    """Les couples (valeur, etiquette) d'un axe continu.

    entier vaut pour les axes que figures.R laisse a l'etiquetage par
    defaut de ggplot2, les millesimes surtout : ni separateur de milliers
    ni decimale."""
    v = jolis(lo, hi, n)
    pas = (v[1] - v[0]) if len(v) > 1 else 1.0
    c = 0 if entier else decimales(pas)
    return [(x, fmt(x, fr, c, groupe=not entier)) for x in v]


def eclaircit(ticks, ech, taille, ecart=3.0, gras=False):
    """Retire une graduation sur deux tant que les etiquettes se touchent.

    ggplot2 laisse les etiquettes se chevaucher ; sur un panneau de
    quarante points de large, cela donne une bouillie. On prefere en
    montrer moins."""
    if len(ticks) < 2:
        return ticks
    for saut in range(1, len(ticks) + 1):
        pris = ticks[::saut]
        ok = True
        for i in range(1, len(pris)):
            a = ech(pris[i - 1][0]) + larg(pris[i - 1][1], taille, gras) / 2.0
            b = ech(pris[i][0]) - larg(pris[i][1], taille, gras) / 2.0
            if b - a < ecart:
                ok = False
                break
        if ok or len(pris) <= 2:
            return pris
    return ticks[:1]


# ----------------------------------------------------------------------
# Dates
# ----------------------------------------------------------------------
MOIS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
           "juil.", "août", "sept.", "oct.", "nov.", "déc."]
MOIS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def en_date(v):
    """Les dates arrivent en aaaa-mm ou en aaaa-mm-jj."""
    t = str(v).strip()
    if re.match(r"^\d{4}-\d{2}$", t):
        t += "-01"
    return datetime.date(*[int(x) for x in t.split("-")[:3]])


def jour(d):
    return float(d.toordinal())


def etiq_mois(d, fr):
    return "%s %d" % ((MOIS_FR if fr else MOIS_EN)[d.month - 1], d.year)


def annees(d0, d1, pas):
    """Les premiers janvier, de <pas> en <pas> annees, comme scale_x_date."""
    a = datetime.date(d0.year, 1, 1)
    out = []
    while a.year <= d1.year + pas:
        if a >= d0 and a <= d1:
            out.append(a)
        a = datetime.date(a.year + pas, 1, 1)
    return out


def premiers_du_mois(d0, d1, pas):
    """Les premiers du mois compris dans l'intervalle, de <pas> en <pas>."""
    a = datetime.date(d0.year, d0.month, 1)
    out = []
    while a <= d1:
        if a >= d0:
            out.append(a)
        m = a.month + pas
        a = datetime.date(a.year + (m - 1) // 12, (m - 1) % 12 + 1, 1)
    return out


def dates_axe(d0, d1, fr, n=5):
    """Les graduations de l'axe des dates, a l'echelle de l'intervalle.

    Une serie qui court sur des decennies se gradue en annees ; une serie
    qui tient dans une saison -- le suivi d'une epidemie, par exemple --
    n'a aucun premier janvier a l'interieur d'elle-meme et resterait sans
    aucune graduation. On descend alors au mois, en espacant les
    graduations pour qu'il en reste environ <n>, et si l'intervalle est
    plus court qu'un mois on se rabat sur ses deux bornes : mieux vaut
    deux dates lisibles qu'un axe muet.
    """
    mois = (d1.year - d0.year) * 12 + d1.month - d0.month
    if mois >= 24:
        pas = max(1, int(round(mois / 12.0 / float(n))))
        return [(jour(a), str(a.year)) for a in annees(d0, d1, pas)]
    if mois >= 2:
        pas = max(1, int(round(mois / float(n))))
        return [(jour(a), etiq_mois(a, fr))
                for a in premiers_du_mois(d0, d1, pas)]
    return [(jour(a), "%d %s" % (a.day, etiq_mois(a, fr)))
            for a in (d0, d1)]


# ----------------------------------------------------------------------
# Lecture du plan et des series
# ----------------------------------------------------------------------
def champ(fiche, base, fr):
    v = fiche.get(base + ("_fr" if fr else "_en"))
    return "" if v is None else str(v)


def lire(fiche):
    """Le CSV de la fiche, en liste de dictionnaires."""
    f = os.path.join(DOSSIER, fiche.get("csv") or "")
    if not os.path.exists(f):
        raise ValueError("fichier absent : %s" % fiche.get("csv"))
    with open(f, encoding="utf-8", newline="") as h:
        d = list(csv.DictReader(h))
    if not d:
        raise ValueError("serie vide : %s" % fiche.get("csv"))
    return d


def flot(v):
    """Un flottant, ou None si la case ne s'y prete pas."""
    try:
        x = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return None if x != x or x in (float("inf"), float("-inf")) else x


def colonne(d, nom, conv=flot):
    return [conv(r.get(nom)) for r in d]


def etendue(vals, avec_zero=False):
    v = [x for x in vals if x is not None]
    if not v:
        raise ValueError("aucune valeur exploitable")
    lo, hi = min(v), max(v)
    if avec_zero:
        lo, hi = min(lo, 0.0), max(hi, 0.0)
    return lo, hi


def panneaux(d, fr, cle="panneau"):
    """L'intitule de facette dans la langue voulue, dans l'ordre du
    preparateur."""
    c = cle + ("_fr" if fr else "_en")
    ordre = []
    for r in d:
        v = r.get(c) or ""
        if v not in ordre:
            ordre.append(v)
    return ordre


# ----------------------------------------------------------------------
# L'entete : titre, sous-titre, source. La zone qui reste sert au panneau.
# ----------------------------------------------------------------------
def entete(t, fiche, fr, W, H):
    """Le bandeau de tete et la source ; rend la zone laissee au panneau.

    Un titre de deux lignes, un sous-titre en forme de paragraphe et une
    source de deux lignes suffisent a devorer une planche de quatre
    centimetres de haut. Le bandeau se resserre donc par paliers tant
    qu'il ne laisse pas au panneau une part decente de la hauteur."""
    g, d = MARGE_G, W - MARGE_D
    titre = champ(fiche, "titre", fr)
    sous = champ(fiche, "sous", fr)
    source = champ(fiche, "source", fr)

    def mesure(r):
        tt, ts, tc = T_TITRE * r, T_SOUS * r, T_SOURCE * r
        lt = enveloppe(titre, d - g, tt, True)
        ls = enveloppe(sous, d - g, ts)
        # Le sous-titre ne prend jamais plus du tiers de la planche.
        maxi = max(1, int(H * 0.30 / (ts * INTERLIGNE)))
        if len(ls) > maxi:
            ls = enveloppe(sous, d - g, ts, maxi=maxi)
        lc = enveloppe(source, d - g, tc)
        haut = MARGE_H + len(lt) * tt * INTERLIGNE + (2 if lt else 0) \
            + len(ls) * ts * INTERLIGNE + 10
        # La ligne de droits d'auteur occupe sa propre ligne de base, sous
        # la source : accolee a celle-ci, elle chevaucherait la derniere
        # ligne des que la source court sur toute la largeur.
        bas = H - MARGE_B - (len(lc) + 1) * tc * INTERLIGNE - (10 if lc else 0)
        return (tt, ts, tc, lt, ls, lc, haut, bas)

    for r in (1.0, 0.94, 0.88, 0.82, 0.76, 0.7, 0.64):
        m = mesure(r)
        if m[7] - m[6] >= H * 0.42:
            break
    tt, ts, tc, lt, ls, lc, haut, bas = m

    y = MARGE_H
    if lt:
        y = bloc(t, g, y, lt, tt, PINE, gras=True) + 2
    if ls:
        bloc(t, g, y, ls, ts, MUET)
    pied = H - MARGE_B - (len(lc) + 1) * tc * INTERLIGNE
    if lc:
        bloc(t, g, pied, lc, tc, MUET)
    # La planche est dessinee par l'auteur : elle porte sa mention de
    # droits, a droite pour ne pas se confondre avec la source.
    t.texte(d, H - MARGE_B, DROITS, tc * 0.92, MUET, "end")
    return [g, haut, d, bas]


# ----------------------------------------------------------------------
# Les axes. On mesure d'abord les etiquettes, on en deduit le cadre, puis
# on pose la grille, les graduations et les intitules d'axe.
# ----------------------------------------------------------------------
def axes(t, zone, fiche, fr, dom_x, dom_y, xt, yt, marge_x=0.05,
         marge_y=0.05, grille_x=True, grille_y=True, taille=T_AXE,
         lignes_x=1, titres=True, eclaircir=True, reserve_x=False):
    """Pose le cadre et rend (boite, echelle_x, echelle_y).

    xt et yt sont des listes de couples (valeur, etiquette)."""
    x0, y0, x1, y1 = zone
    tx = champ(fiche, "x", fr) if titres else ""
    ty = champ(fiche, "y", fr) if titres else ""

    if tx:
        y1 -= T_AXE_TITRE * INTERLIGNE + 6
    if ty:
        x0 += T_AXE_TITRE * INTERLIGNE + 6
    # reserve_x : les modalites que l'appelant pose lui-meme reclament la
    # meme gouttiere que des graduations ordinaires.
    haut_x = taille * INTERLIGNE * lignes_x + 3 if (xt or reserve_x) else 0
    larg_y = (max([larg(e, taille) for _, e in yt]) + 3) if yt else 0
    boite = [x0 + larg_y, y0, x1, y1 - haut_x]

    ex = Ech(dom_x[0], dom_x[1], boite[0], boite[2], marge_x)
    ey = Ech(dom_y[0], dom_y[1], boite[3], boite[1], marge_y)

    if eclaircir:
        xt = eclaircit([p for p in xt if ex.dedans(p[0])], ex, taille)
    else:
        xt = [p for p in xt if ex.dedans(p[0])]
    yt = [p for p in yt if ey.dedans(p[0])]

    for v, e in xt:
        if grille_x:
            t.ligne(ex(v), boite[1], ex(v), boite[3], FILET, 0.32)
        for i, l in enumerate(str(e).split("\n")):
            t.texte(ex(v), boite[3] + 3 + taille * (0.78 + i * INTERLIGNE),
                    l, taille, ENCRE, "middle")
    for v, e in yt:
        if grille_y:
            t.ligne(boite[0], ey(v), boite[2], ey(v), FILET, 0.32)
        t.texte(boite[0] - 3, ey(v) + taille * 0.34, e, taille, ENCRE, "end")

    if tx:
        t.texte((boite[0] + boite[2]) / 2.0,
                boite[3] + haut_x + 6 + T_AXE_TITRE * 0.78, tx,
                T_AXE_TITRE, MUET, "middle")
    if ty:
        t.texte(zone[0] + T_AXE_TITRE * 0.78, (boite[1] + boite[3]) / 2.0,
                ty, T_AXE_TITRE, MUET, "middle", rotation=-90)
    return boite, ex, ey


# ----------------------------------------------------------------------
# Les legendes. En haut a gauche par defaut, comme theme_wabenga ; a
# droite pour les barres empilees.
# ----------------------------------------------------------------------
def legende_haut(t, zone, items, taille=T_LEGENDE):
    """Une bande de cles au-dessus du panneau ; elle se replie si la
    ligne unique voulue par guide_legend(nrow = 1) deborde."""
    x0, y0, x1, y1 = zone
    cle, gouttiere, entre = 7.5, 3.0, 9.0
    rangs, courant, l = [], [], 0.0
    for c, e in items:
        w = cle + gouttiere + larg(e, taille) + entre
        if courant and l + w > (x1 - x0):
            rangs.append(courant)
            courant, l = [], 0.0
        courant.append((c, e))
        l += w
    if courant:
        rangs.append(courant)
    h = max(cle, taille) * INTERLIGNE
    for i, rang in enumerate(rangs):
        x, y = x0, y0 + i * h
        for c, e in rang:
            t.rect(x, y + (h - cle) / 2.0, cle, cle, c)
            t.texte(x + cle + gouttiere, y + h / 2.0 + taille * 0.34, e,
                    taille, ENCRE)
            x += cle + gouttiere + larg(e, taille) + entre
    return [x0, y0 + len(rangs) * h + 4, x1, y1]


def legende_droite(t, zone, items, taille=T_LEGENDE):
    """Les cles rangees a droite du panneau, alignees sur son sommet."""
    x0, y0, x1, y1 = zone
    cle, gouttiere = 7.5, 3.0
    w = cle + gouttiere + max([larg(e, taille) for _, e in items]) + 6
    h = max(cle, taille) * INTERLIGNE
    for i, (c, e) in enumerate(items):
        y = y0 + i * h
        t.rect(x1 - w + 6, y + (h - cle) / 2.0, cle, cle, c)
        t.texte(x1 - w + 6 + cle + gouttiere, y + h / 2.0 + taille * 0.34,
                e, taille, ENCRE)
    return [x0, y0, x1 - w, y1]


# ----------------------------------------------------------------------
# Les planches a facettes. Les panneaux sont de meme taille ; l'axe des
# abscisses n'est pose qu'au bas de chaque colonne, comme facet_wrap.
# ----------------------------------------------------------------------
def facettes(t, zone, titres, ncol, larg_y, haut_x, espace_x=13.0,
             espace_y=11.0, axe_partout=True):
    """Decoupe la zone en panneaux et rend (cases, taille des graduations).

    Une case vaut (boite, pose_axe_x, pose_axe_y, rang du panneau).

    Dix-sept panneaux sur neuf centimetres et demi ne tiennent pas a la
    taille de base : la typographie des facettes est donc resserree par
    paliers, jusqu'a ce que les panneaux aient de quoi respirer. C'est le
    seul endroit ou l'on s'ecarte des tailles de figures.R."""
    n = len(titres)
    ncol = max(1, int(ncol))
    nrow = int(math.ceil(n / float(ncol)))
    x0, y0, x1, y1 = zone

    dernier = {}
    for i in range(n):
        dernier[i % ncol] = i
    bas_de_colonne = set(dernier.values())
    rangs_avec_axe = set(i // ncol for i in bas_de_colonne)

    retenu = None
    for r in (1.0, 0.9, 0.8, 0.7, 0.62, 0.55, 0.48, 0.42):
        tb, ta = T_BANDE * r, T_AXE_F * r
        ex_, ey_ = espace_x * r, espace_y * r
        lc = (x1 - x0 - (ncol - 1) * ex_) / float(ncol)
        replis, nl = [], 1
        for s in titres:
            # Deux lignes, quelle que soit la taille : un intitule de
            # facette coupe ne dit plus quelle serie il coiffe.
            l = enveloppe(s, lc, tb, maxi=2)
            nl = max(nl, len(l))
            replis.append(l)
        hb = nl * tb * INTERLIGNE + 3 * r
        hx = haut_x * r
        hp = ((y1 - y0) - nrow * hb - len(rangs_avec_axe) * hx
              - (nrow - 1) * ey_) / float(nrow)
        retenu = (r, tb, ta, ex_, ey_, lc, replis, hb, hx, hp)
        if hp >= max(14.0, 1.1 * hb):
            break
    r, tb, ta, espace_x, espace_y, larg_case, replis, h_bande, haut_x, \
        h_panneau = retenu
    if h_panneau <= 6:
        raise ValueError("place insuffisante pour %d panneaux" % n)
    larg_y *= r

    # Les rangs qui portent un axe sont plus hauts d'autant.
    haut_rang, y = {}, y0
    for i in range(nrow):
        haut_rang[i] = y
        y += h_bande + h_panneau + (haut_x if i in rangs_avec_axe else 0) \
            + espace_y

    cases = []
    for i in range(n):
        rg, c = i // ncol, i % ncol
        cx = x0 + c * (larg_case + espace_x)
        cy = haut_rang[rg]
        bloc(t, cx, cy, replis[i], tb, PINE)
        gx = cx + larg_y if (axe_partout or c == 0) else cx
        boite = [gx, cy + h_bande, cx + larg_case, cy + h_bande + h_panneau]
        cases.append((boite, i in bas_de_colonne, axe_partout or c == 0, i))
    return cases, ta


def axe_facette(t, boite, ex, ey, xt, yt, pose_x, pose_y, taille=T_AXE_F,
                grille=True):
    """La grille et les graduations d'un panneau de facette."""
    xt = [p for p in xt if ex.dedans(p[0])]
    yt = [p for p in yt if ey.dedans(p[0])]
    if pose_x:
        xt = eclaircit(xt, ex, taille, 2.5)
    for v, e in xt:
        if grille:
            t.ligne(ex(v), boite[1], ex(v), boite[3], FILET, 0.32)
        if pose_x:
            t.texte(ex(v), boite[3] + 3 + taille * 0.78, e, taille,
                    ENCRE, "middle")
    if pose_y and len(yt) > 1:
        h = abs(ey(yt[1][0]) - ey(yt[0][0]))
        if h < taille * 1.05:
            yt = yt[::2]
    for v, e in yt:
        if grille:
            t.ligne(boite[0], ey(v), boite[2], ey(v), FILET, 0.32)
        if pose_y:
            t.texte(boite[0] - 3, ey(v) + taille * 0.34, e, taille,
                    ENCRE, "end")


def bandes(t, fiche, boite, ex):
    """Les plages grisees des episodes de tension, communes aux planches
    mensuelles."""
    for p in (fiche.get("bandes") or []):
        try:
            a, b = jour(en_date(p[0])), jour(en_date(p[1]))
        except Exception:                                        # noqa: BLE001
            continue
        a = max(a, ex.lo)
        b = min(b, ex.hi)
        if b <= a:
            continue
        t.rect(ex(a), boite[1], ex(b) - ex(a), boite[3] - boite[1],
               ENCRE, 0.055)


def aire_sous(t, pts, base, couleur, opacite):
    """Le polygone d'un geom_area : la courbe, refermee sur sa ligne de
    fond."""
    if len(pts) < 2:
        return
    t.polygone([(pts[0][0], base)] + pts + [(pts[-1][0], base)],
               couleur, opacite)


# ======================================================================
# Les traces des series publiees par le site (plan.json)
# ======================================================================
def trace_colonnes_zero(t, d, fiche, fr, zone):
    xs, ys = colonne(d, "x"), colonne(d, "y")
    pts = [(a, b) for a, b in zip(xs, ys) if a is not None and b is not None]
    dx = etendue([p[0] for p in pts])
    dy = etendue([p[1] for p in pts], avec_zero=True)
    xt = graduations(dx[0], dx[1], 8, fr, entier=True)
    yt = graduations(dy[0], dy[1], 5, fr)
    boite, ex, ey = axes(t, zone, fiche, fr, dx, dy, xt, yt)

    pas = 0.72
    if len(pts) > 1:
        pas *= min(abs(pts[i][0] - pts[i - 1][0]) for i in range(1, len(pts)))
    w = abs(ex(pas) - ex(0))
    zero = ey(0)
    for a, b in pts:
        c = fiche.get("couleur") if b >= 0 else fiche.get("couleur2")
        yv = ey(b)
        t.rect(ex(a) - w / 2.0, min(zero, yv), w, abs(yv - zero), c or PINE)
    t.ligne(boite[0], zero, boite[2], zero, ENCRE, 0.4)


def trace_ligne_log(t, d, fiche, fr, zone):
    xs, ys = colonne(d, "x"), colonne(d, "y")
    pts = [(a, math.log10(b)) for a, b in zip(xs, ys)
           if a is not None and b is not None and b > 0]
    if len(pts) < 2:
        raise ValueError("moins de deux points positifs")
    dx = etendue([p[0] for p in pts])
    dy = etendue([p[1] for p in pts])
    xt = graduations(dx[0], dx[1], 8, fr, entier=True)
    yt = [(math.log10(v), fmt(v, fr))
          for v in (1, 10, 100, 1000, 10000, 100000, 1000000)]
    boite, ex, ey = axes(t, zone, fiche, fr, dx, dy, xt, yt)

    c = fiche.get("couleur") or PINE
    ecran = [(ex(a), ey(b)) for a, b in pts]
    t.polyligne(ecran, c, 0.7)
    for x, y in ecran:
        t.rond(x, y, 1.15, c)


def trace_aire(t, d, fiche, fr, zone):
    xs, ys = colonne(d, "x"), colonne(d, "y")
    pts = [(a, b) for a, b in zip(xs, ys) if a is not None and b is not None]
    dx = etendue([p[0] for p in pts])
    dy = etendue([p[1] for p in pts], avec_zero=True)
    xt = graduations(dx[0], dx[1], 8, fr, entier=True)
    yt = graduations(dy[0], dy[1], 5, fr)
    boite, ex, ey = axes(t, zone, fiche, fr, dx, dy, xt, yt)

    ecran = [(ex(a), ey(b)) for a, b in pts]
    aire_sous(t, ecran, ey(0), fiche.get("couleur2") or FILET, 0.55)
    t.polyligne(ecran, fiche.get("couleur") or PINE, 0.75)


def _barres_h(t, d, fiche, fr, zone, couleurs, chiffres, marge_haute,
              taille_etiq):
    """Le fond commun aux deux barres horizontales : coord_flip, les
    modalites rangees par valeur croissante, la valeur au bout de la
    barre."""
    lignes = [(r.get("label") or "", flot(r.get("y")), couleurs(r))
              for r in d]
    lignes = [l for l in lignes if l[1] is not None]
    if not lignes:
        raise ValueError("aucune valeur exploitable")
    taille_etiq *= GG_PT
    lignes.sort(key=lambda l: l[1])
    n = len(lignes)
    hi = max(l[1] for l in lignes)
    lo = min(0.0, min(l[1] for l in lignes))
    etiqs = [nombre(l[1], chiffres, fr) for l in lignes]

    # coord_flip : l'intitule pose par labs(y = ...) passe a l'horizontale.
    tourne = dict(fiche)
    for s in ("_en", "_fr"):
        tourne["x" + s] = fiche.get("y" + s) or ""
        tourne["y" + s] = fiche.get("x" + s) or ""

    # La gouttiere de gauche porte les modalites, non des nombres ; la
    # marge haute de l'echelle laisse la place aux valeurs chiffrees.
    # Quinze barres sur cinq centimetres ne laissent que trois points par
    # rang : les intitules sont donc mis au pas de la grille.
    x0, y0, x1, y1 = zone
    utile = (y1 - y0) - (T_AXE * INTERLIGNE + 3)
    if champ(tourne, "x", fr):
        utile -= T_AXE_TITRE * INTERLIGNE + 6
    tl = min(T_AXE, max(3.6, utile / float(n + 1.2) * 0.92))
    taille_etiq = min(taille_etiq, tl)

    plafond = (x1 - x0) * 0.40
    courts = []
    for l in lignes:
        s = l[0]
        while s and larg(s, tl) > plafond:
            s = s[:-1].rstrip()
            if larg(s + "…", tl) <= plafond:
                s += "…"
                break
        courts.append(s)
    lmod = max(larg(s, tl) for s in courts) + 3

    dv = (lo, hi + (hi - lo) * marge_haute)
    vt = graduations(dv[0], dv[1], 5, fr)
    boite, ev, _ = axes(t, [x0 + lmod, y0, x1, y1], tourne, fr, dv, (0, 1),
                        vt, [], marge_x=0.0, grille_y=False)
    ec = Ech(0.4, n + 0.6, boite[3], boite[1], 0.0)
    h = abs(ec(0.68) - ec(0))
    for i, (lab, val, coul) in enumerate(lignes):
        yc = ec(i + 1)
        t.rect(min(ev(0), ev(val)), yc - h / 2.0, abs(ev(val) - ev(0)), h,
               coul)
        t.texte(max(ev(0), ev(val)) + 3, yc + taille_etiq * 0.34,
                etiqs[i], taille_etiq, ENCRE)
        t.texte(boite[0] - 3, yc + tl * 0.34, courts[i], tl, ENCRE, "end")


def trace_barres_h(t, d, fiche, fr, zone):
    c = fiche.get("couleur") or PINE
    # « ou 2 » avalerait le zero : une planche qui demande des entiers
    # obtiendrait deux decimales. On teste donc la presence, non la verite.
    n = fiche.get("chiffres")
    try:
        chiffres = 2 if n is None else int(n)
    except (TypeError, ValueError):
        chiffres = 2
    _barres_h(t, d, fiche, fr, zone, lambda r: c, chiffres, 0.16, 2.7)


def trace_courbe_cumul(t, d, fiche, fr, zone):
    xs, ys = colonne(d, "x"), colonne(d, "y")
    pts = [(a, b) for a, b in zip(xs, ys) if a is not None and b is not None]
    dx = etendue([p[0] for p in pts])
    xt = graduations(dx[0], dx[1], 8, fr, entier=True)
    yt = [(v, fmt(v, fr)) for v in range(0, 101, 20)]
    boite, ex, ey = axes(t, zone, fiche, fr, dx, (0.0, 100.0), xt, yt)

    c = fiche.get("couleur") or PINE
    ecran = [(ex(a), ey(b)) for a, b in pts]
    aire_sous(t, ecran, ey(0), c, 0.13)
    for seuil in (50, 80):
        t.ligne(boite[0], ey(seuil), boite[2], ey(seuil), FILET, 0.5, "2,2")
    t.polyligne(ecran, c, 0.8)
    for x, y in ecran:
        t.rond(x, y, 1.05, c)


def trace_marches(t, d, fiche, fr, zone):
    pts = []
    for r in d:
        v = flot(r.get("y"))
        try:
            j = jour(en_date(r.get("x")))
        except Exception:                                        # noqa: BLE001
            continue
        if v is not None:
            pts.append((j, v))
    pts.sort()
    if len(pts) < 2:
        raise ValueError("moins de deux decisions")
    dx = etendue([p[0] for p in pts])
    dy = etendue([p[1] for p in pts])
    if len(pts) > 10:
        d0, d1 = datetime.date.fromordinal(int(dx[0])), \
            datetime.date.fromordinal(int(dx[1]))
        rep = annees(d0, d1, max(1, (d1.year - d0.year) // 6 or 1))
        xt = [(jour(a), str(a.year)) for a in rep]
    else:
        xt = [(j, etiq_mois(datetime.date.fromordinal(int(j)), fr))
              for j, _ in pts]
    yt = graduations(dy[0], dy[1], 5, fr)
    boite, ex, ey = axes(t, zone, fiche, fr, dx, dy, xt, yt)

    c = fiche.get("couleur") or PINE
    escalier = [(ex(pts[0][0]), ey(pts[0][1]))]
    for i in range(1, len(pts)):
        escalier.append((ex(pts[i][0]), ey(pts[i - 1][1])))
        escalier.append((ex(pts[i][0]), ey(pts[i][1])))
    t.polyligne(escalier, c, 0.8)
    for j, v in pts:
        t.rond(ex(j), ey(v), 1.6, fiche.get("couleur2") or BRASS)


def trace_lignes_multi(t, d, fiche, fr, zone):
    noms = fiche.get("series_fr" if fr else "series_en") or {}
    series, ordre = {}, []
    for r in d:
        s = r.get("serie") or ""
        v = flot(r.get("y"))
        try:
            j = jour(en_date(r.get("x")))
        except Exception:                                        # noqa: BLE001
            continue
        if v is None:
            continue
        if s not in series:
            series[s] = []
            ordre.append(s)
        series[s].append((j, v))
    if not series:
        raise ValueError("aucune serie exploitable")
    if noms:
        ordre = [s for s in noms if s in series] + \
            [s for s in ordre if s not in noms]

    tous = [p for s in series.values() for p in s]
    dx = etendue([p[0] for p in tous])
    dy = etendue([p[1] for p in tous])
    teintes = [fiche.get("couleur") or PINE, fiche.get("couleur2") or BRASS,
               BRASS]
    items = [(teintes[i % len(teintes)], str(noms.get(s, s)))
             for i, s in enumerate(ordre)]
    zone = legende_haut(t, zone, items)

    d0 = datetime.date.fromordinal(int(dx[0]))
    d1 = datetime.date.fromordinal(int(dx[1]))
    xt = dates_axe(d0, d1, fr)
    yt = graduations(dy[0], dy[1], 5, fr)
    boite, ex, ey = axes(t, zone, fiche, fr, dx, dy, xt, yt)
    for i, s in enumerate(ordre):
        pts = sorted(series[s])
        t.polyligne([(ex(a), ey(b)) for a, b in pts],
                    teintes[i % len(teintes)], 0.65)


# ======================================================================
# Les planches de faits stylises (plan-sf.json)
# ======================================================================
def _series_par_panneau(d, fr, log=False):
    """Range les points mensuels par panneau, dans l'ordre du preparateur."""
    ordre = panneaux(d, fr)
    par, teinte = dict((p, []) for p in ordre), {}
    cle = "panneau_fr" if fr else "panneau_en"
    for r in d:
        p = r.get(cle) or ""
        v = flot(r.get("y"))
        try:
            j = jour(en_date(r.get("date")))
        except Exception:                                        # noqa: BLE001
            continue
        if v is None:
            continue
        if log and str(r.get("log") or "").strip() == "1":
            if v <= 0:
                continue
            v = math.log(v)
        teinte.setdefault(p, r.get("couleur") or PINE)
        par.setdefault(p, []).append((j, v))
    ordre = [p for p in ordre if len(par.get(p) or []) > 1]
    if not ordre:
        raise ValueError("aucun panneau exploitable")
    for p in ordre:
        par[p].sort()
    return ordre, par, teinte


def _planche_mensuelle(t, d, fiche, fr, zone, aires, zero, pas_annees,
                       couleur_colonne=False, log=False):
    """Le fond commun aux trois planches mensuelles a facettes."""
    ordre, par, teinte = _series_par_panneau(d, fr, log=log)
    tous = [p for s in par.values() for p in s]
    dx = etendue([p[0] for p in tous])

    # La gouttiere des ordonnees est commune : c'est la plus large des
    # etiquettes de tous les panneaux.
    bornes, lgy = {}, 0.0
    for p in ordre:
        lo, hi = etendue([v for _, v in par[p]], avec_zero=zero)
        e = Ech(lo, hi, 0, 1)
        bornes[p] = (graduations(e.lo, e.hi, 4, fr), (lo, hi))
        for _, s in bornes[p][0]:
            lgy = max(lgy, larg(s, T_AXE_F))
    lgy += 3
    hx = T_AXE_F * INTERLIGNE + 3

    cases, ta = facettes(t, zone, ordre, fiche.get("colonnes") or 3, lgy, hx)
    d0 = datetime.date.fromordinal(int(dx[0]))
    d1 = datetime.date.fromordinal(int(dx[1]))
    # Le pas des annees en abscisse suit la largeur reelle de la planche :
    # une facette large supporte une graduation plus serree, une facette
    # etroite doit s'en tenir a un millesime sur trois.
    try:
        pas_annees = int(fiche.get("pas_annees") or pas_annees)
    except (TypeError, ValueError):
        pass
    xt = [(jour(a), str(a.year)) for a in annees(d0, d1, max(1, pas_annees))]

    for boite, pose_x, pose_y, i in cases:
        p = ordre[i]
        yt, (lo, hi) = bornes[p]
        ex = Ech(dx[0], dx[1], boite[0], boite[2], 0.05)
        ey = Ech(lo, hi, boite[3], boite[1], 0.05)
        bandes(t, fiche, boite, ex)
        axe_facette(t, boite, ex, ey, xt, yt, pose_x, pose_y, ta)
        if zero and ey.dedans(0):
            t.ligne(boite[0], ey(0), boite[2], ey(0), MUET, 0.36)
        c = teinte.get(p, PINE) if couleur_colonne else PINE
        ecran = [(ex(a), ey(b)) for a, b in par[p]]
        if aires:
            aire_sous(t, ecran, ey(max(min(0.0, hi), lo)), c, aires)
        t.polyligne(ecran, c, 0.52 if not couleur_colonne else 0.6)


def trace_facettes_niveaux(t, d, fiche, fr, zone):
    _planche_mensuelle(t, d, fiche, fr, zone, aires=0.0, zero=False,
                       pas_annees=3, log=True)


def trace_facettes_cycles(t, d, fiche, fr, zone):
    _planche_mensuelle(t, d, fiche, fr, zone, aires=0.13, zero=True,
                       pas_annees=3)


def trace_facettes_aires(t, d, fiche, fr, zone):
    fiche = dict(fiche)
    fiche.setdefault("colonnes", 2)
    _planche_mensuelle(t, d, fiche, fr, zone, aires=0.16, zero=True,
                       pas_annees=2, couleur_colonne=True)


def trace_barres_xcorr(t, d, fiche, fr, zone):
    ordre = panneaux(d, fr)
    cle = "panneau_fr" if fr else "panneau_en"
    par = dict((p, []) for p in ordre)
    for r in d:
        k, v = flot(r.get("retard")), flot(r.get("r"))
        if k is not None and v is not None:
            par.setdefault(r.get(cle) or "", []).append((k, v))
    ordre = [p for p in ordre if par.get(p)]
    if not ordre:
        raise ValueError("aucun panneau exploitable")

    # Facettes a echelle fixe : une seule etendue pour tous les panneaux.
    tous = [v for s in par.values() for _, v in s]
    dy = etendue(tous, avec_zero=True)
    yt = graduations(dy[0], dy[1], 5, fr)
    lgy = max(larg(s, T_AXE_F) for _, s in yt) + 3
    hx = T_AXE_F * INTERLIGNE + 3
    xt = [(v, fmt(v, fr)) for v in range(-12, 13, 6)]

    cases, ta = facettes(t, zone, ordre, fiche.get("colonnes") or 4, lgy, hx,
                         axe_partout=False)
    for boite, pose_x, pose_y, i in cases:
        pts = sorted(par[ordre[i]])
        dx = etendue([k for k, _ in pts])
        ex = Ech(dx[0], dx[1], boite[0], boite[2], 0.05)
        ey = Ech(dy[0], dy[1], boite[3], boite[1], 0.05)
        axe_facette(t, boite, ex, ey, xt, yt, pose_x, pose_y, ta)
        t.ligne(ex(0), boite[1], ex(0), boite[3], MUET, 0.36, "2,2")
        w = abs(ex(0.72) - ex(0))
        z = ey(0)
        for k, v in pts:
            t.rect(ex(k) - w / 2.0, min(z, ey(v)), w, abs(ey(v) - z),
                   PINE if v >= 0 else BRASS)
        t.ligne(boite[0], z, boite[2], z, ENCRE, 0.36)


def trace_colonnes_regimes(t, d, fiche, fr, zone):
    cle = "regime_fr" if fr else "regime_en"
    pts, ordre, teinte = [], [], {}
    for r in d:
        a, v = flot(r.get("annee")), flot(r.get("y"))
        p = r.get(cle) or ""
        if a is None or v is None:
            continue
        if p not in teinte:
            ordre.append(p)
            teinte[p] = r.get("couleur") or PINE
        pts.append((a, v, p))
    if not pts:
        raise ValueError("aucune valeur exploitable")

    zone = legende_haut(t, zone, [(teinte[p], p) for p in ordre])
    dx = etendue([p[0] for p in pts])
    dy = etendue([p[1] for p in pts], avec_zero=True)
    xt = graduations(dx[0], dx[1], 9, fr, entier=True)
    yt = graduations(dy[0], dy[1], 5, fr)
    boite, ex, ey = axes(t, zone, fiche, fr, dx, dy, xt, yt)

    w = abs(ex(0.74) - ex(0))
    z = ey(0)
    for a, v, p in pts:
        t.rect(ex(a) - w / 2.0, min(z, ey(v)), w, abs(ey(v) - z), teinte[p])
    t.ligne(boite[0], z, boite[2], z, ENCRE, 0.4)
    # Le trait discontinu porte la croissance moyenne de chaque periode.
    for p in ordre:
        vs = [v for _, v, q in pts if q == p]
        xs = [a for a, _, q in pts if q == p]
        if not vs:
            continue
        m = ey(sum(vs) / len(vs))
        t.ligne(ex(min(xs) - 0.45), m, ex(max(xs) + 0.45), m, ENCRE, 0.5,
                "2,2")


def trace_barres_h_couleur(t, d, fiche, fr, zone):
    _barres_h(t, d, fiche, fr, zone,
              lambda r: r.get("couleur") or PINE, 3, 0.18, 2.55)


def trace_barres_v(t, d, fiche, fr, zone):
    lab = "label_fr" if fr else "label_en"
    src = "src_fr" if fr else "src_en"
    lignes = []
    for r in d:
        v = flot(r.get("y"))
        if v is None:
            continue
        lignes.append(((r.get(lab) or ""), (r.get(src) or ""), v,
                       r.get("couleur") or PINE))
    if not lignes:
        raise ValueError("aucune valeur exploitable")
    n = len(lignes)
    hi = max(l[2] for l in lignes)
    lo = min(0.0, min(l[2] for l in lignes))
    dv = (lo, hi + (hi - lo) * 0.14)
    vt = graduations(dv[0], dv[1], 5, fr)

    # L'intitule est suivi de la source entre parentheses, sur sa propre
    # ligne, comme le veut le saut de ligne pose dans figures.R. Il est
    # replie, et rapetisse si besoin, plutot que de chevaucher le voisin.
    x0, y0, x1, y1 = zone
    # La gouttiere entre deux intitules voisins : sans elle, ils se
    # touchent, chacun etant centre sur sa colonne.
    lcase = (x1 - x0 - 30) / float(n) * 0.85
    # On rapetisse jusqu'a ce que l'intitule tienne entier : un libelle
    # coupe par des points de suspension ne dit plus de quelle grandeur
    # il s'agit, et c'est la le seul endroit ou on la nomme.
    for r in (1.0, 0.92, 0.85, 0.78, 0.72, 0.66, 0.60):
        tl = T_AXE_F * r
        corps = [enveloppe(l[0], lcase, tl) for l in lignes]
        notes = [enveloppe("(%s)" % l[1], lcase, tl) for l in lignes]
        if (max(len(x) for x in corps) <= 4
                and max(len(a) + len(b) for a, b in zip(corps, notes)) <= 6):
            break
    replis = [enveloppe(l[0], lcase, tl, maxi=4)
              + enveloppe("(%s)" % l[1], lcase, tl, maxi=3) for l in lignes]
    nl = max(len(x) for x in replis)
    boite, _, ev = axes(t, zone, fiche, fr, (0, 1), dv, [], vt,
                        marge_y=0.0, lignes_x=nl, taille=tl,
                        reserve_x=True)
    ec = Ech(0.4, n + 0.6, boite[0], boite[2], 0.0)
    w = abs(ec(0.6) - ec(0))
    for i, (_, _, v, c) in enumerate(lignes):
        x = ec(i + 1)
        t.rect(x - w / 2.0, min(ev(0), ev(v)), w, abs(ev(v) - ev(0)), c)
        t.texte(x, ev(v) - 3, "%s %%" % nombre(v, 1, fr), 2.9 * GG_PT,
                ENCRE, "middle")
        for k, l in enumerate(replis[i]):
            t.texte(x, boite[3] + 3 + tl * (0.78 + k * INTERLIGNE), l,
                    tl, ENCRE, "middle")


def trace_barres_empilees(t, d, fiche, fr, zone):
    cle = "poste_fr" if fr else "poste_en"
    postes = []
    for r in d:
        v = flot(r.get("y"))
        if v is None:
            continue
        postes.append((r.get(cle) or "", v, r.get("couleur") or PINE,
                       str(r.get("annee") or "")))
    if not postes:
        raise ValueError("aucune valeur exploitable")
    total = sum(p[1] for p in postes)
    if total <= 0:
        raise ValueError("total nul")

    # guide_legend(reverse = TRUE) sur des niveaux renverses : la legende
    # se lit dans l'ordre du fichier, la pile s'empile a l'envers.
    zone = legende_droite(t, zone, [(p[2], p[0]) for p in postes])
    dv = (0.0, total * 1.04)
    vt = graduations(dv[0], dv[1], 5, fr)
    annee = postes[0][3]
    boite, _, ev = axes(t, zone, fiche, fr, (0, 1), dv, [(1, annee)], vt,
                        marge_y=0.0, grille_x=False)
    ec = Ech(0.4, 1.6, boite[0], boite[2], 0.0)
    x = ec(1)
    taille = 2.7 * GG_PT
    parts = ["%s %%" % nombre(100.0 * v / total, 1, fr) for _, v, _, _ in postes]
    # La barre est assez large pour porter ses parts a l'interieur : une
    # etiquette qui deborderait tomberait sur le fond blanc de la page, ou
    # l'encre blanche ne se lit plus.
    w = max(abs(ec(0.46) - ec(0)),
            max(larg(p, taille) for p in parts) / 0.82)
    w = min(w, (boite[2] - boite[0]) * 0.72)
    bas = 0.0
    for (nom, v, c, _), part in zip(reversed(postes), reversed(parts)):
        haut = abs(ev(bas + v) - ev(bas))
        t.rect(x - w / 2.0, ev(bas + v), w, haut, c)
        if larg(part, taille) <= w * 0.9 and haut >= taille * 0.70:
            t.texte(x, (ev(bas) + ev(bas + v)) / 2.0 + taille * 0.34,
                    part, taille, "#FFFFFF", "middle")
        bas += v


TRACES = {
    "colonnes_zero": trace_colonnes_zero,
    "ligne_log": trace_ligne_log,
    "aire": trace_aire,
    "barres_h": trace_barres_h,
    "courbe_cumul": trace_courbe_cumul,
    "marches": trace_marches,
    "lignes_multi": trace_lignes_multi,
    # planches de faits stylises
    "facettes_niveaux": trace_facettes_niveaux,
    "facettes_cycles": trace_facettes_cycles,
    "barres_xcorr": trace_barres_xcorr,
    "facettes_aires": trace_facettes_aires,
    "colonnes_regimes": trace_colonnes_regimes,
    "barres_h_couleur": trace_barres_h_couleur,
    "barres_v": trace_barres_v,
    "barres_empilees": trace_barres_empilees,
}


# ----------------------------------------------------------------------
def charge_plan():
    """Les deux plans bout a bout ; l'absence de l'un n'empeche rien."""
    plan = []
    for nom in ("plan.json", "plan-sf.json"):
        p = os.path.join(DOSSIER, nom)
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                plan += json.load(f)
        except Exception as e:                                   # noqa: BLE001
            print("  %s : plan illisible, %s" % (nom, e))
    return plan


def figure(fiche, fr):
    """Une planche, dans une langue ; rend le texte du SVG."""
    W = float(fiche.get("largeur") or 8.4) * CM
    H = float(fiche.get("hauteur") or 4.6) * CM
    f = TRACES.get(fiche.get("type"))
    if f is None:
        raise ValueError("type de figure inconnu : %s" % fiche.get("type"))
    t = Toile(W, H)
    zone = entete(t, fiche, fr, W, H)
    if zone[3] - zone[1] < 20 or zone[2] - zone[0] < 40:
        raise ValueError("l'entete ne laisse pas de place au panneau")
    f(t, lire(fiche), fiche, fr, zone)
    s = t.rendu()
    if _TEL.search(s):
        raise ValueError("garde-fou : un numero de telephone apparait "
                         "dans la figure")
    return s


def main():
    plan = charge_plan()
    if not plan:
        print("aucun plan de figures dans", DOSSIER)
        return 1
    os.makedirs(SORTIE, exist_ok=True)

    produites = 0
    for fiche in plan:
        for fr in (False, True):
            langue = "fr" if fr else "en"
            cle = fiche.get("cle") or "sans-cle"
            nom = os.path.join(SORTIE, "%s-%s.svg" % (cle, langue))
            try:
                s = figure(fiche, fr)
            except Exception as e:                               # noqa: BLE001
                print("  %s-%s : abandon (%s)" % (cle, langue, e))
                if os.path.exists(nom):
                    os.remove(nom)
                continue
            with open(nom, "w", encoding="utf-8") as h:
                h.write(s)
            produites += 1
            print("  %s-%s : %d octets" % (cle, langue,
                                           len(s.encode("utf-8"))))

    print("%d images SVG ecrites dans %s" % (produites, SORTIE))
    return 0 if produites else 1


if __name__ == "__main__":
    sys.exit(main())
