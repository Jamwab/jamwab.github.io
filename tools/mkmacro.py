# -*- coding: utf-8 -*-
"""Regenere le bloc macroeconomique de la RD Congo.

Lit  : data/macro-rdc.json  (series longues + tableau des agregats annuels)
       data/bcc.json        (taux directeur, reserves, releve monetaire)
Ecrit: macro_figs.html   les trois figures longues       -> marqueur MACRO:FIGS
       macro_tab.html    le tableau des agregats         -> marqueur MACRO:TAB
       bcc_figs.html     les deux figures de la BCC      -> marqueur BCC:FIGS
       bcc_kpi.html      le releve monetaire             -> marqueur BCC:KPI
       series_macro.json les entrees du registre de series

Le script n'a aucune dependance : il n'ecrit que du SVG et du HTML.
Conventions de dessin de la page : viewBox 0 0 720 250, aire de trace
X de 56 a 704, Y de 20 a 194, etiquettes d'axe a y = 214.
"""

import datetime as _dt
import json, math, os, sys

# La composition des planches appartient a l'auteur : chaque note de
# source la revendique, et le millesime suit la date de fabrication.
DROITS = '<span class="fig-c">\u00a9 %d James Wabenga Yango</span>' \
    % _dt.date.today().year

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


def _lit(nom):
    for c in (os.path.join(_ROOT, "data", nom),
              os.path.join(_HERE, "data", nom),
              os.path.join("data", nom)):
        if os.path.exists(c):
            return json.load(open(c, encoding="utf-8"))
    raise SystemExit("fichier introuvable : data/" + nom)


X0, X1 = 56.0, 704.0
Y0, Y1 = 20.0, 194.0          # haut, bas de l'aire de trace
YLAB = 214                    # ligne des etiquettes d'annees

MOIS_FR = ["janvier", "f&#233;vrier", "mars", "avril", "mai", "juin", "juillet",
           "ao&#251;t", "septembre", "octobre", "novembre", "d&#233;cembre"]
ABR_FR = ["janv.", "f&#233;vr.", "mars", "avr.", "mai", "juin", "juil.",
          "ao&#251;t", "sept.", "oct.", "nov.", "d&#233;c."]
ABR_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul",
          "Aug", "Sep", "Oct", "Nov", "Dec"]
MOIS_EN = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]


# ----------------------------------------------------------------- formatage

def nb(v, dec=1):
    """Retourne le couple (anglais, francais) d'un nombre."""
    if v is None:
        return "&#8212;", "&#8212;"
    s = ("%%.%df" % dec) % abs(v)
    ent, _, frac = s.partition(".")
    grp = ""
    while len(ent) > 3:
        grp = ent[-3:] + "|" + grp
        ent = ent[:-3]
    ent = (ent + "|" + grp).rstrip("|") if grp else ent
    en = ent.replace("|", ",") + (("." + frac) if frac else "")
    fr = ent.replace("|", "&#8239;") + (("," + frac) if frac else "")
    if v < 0:
        en, fr = "&#8722;" + en, "&#8722;" + fr
    return en, fr


def txt(x, y, en, fr, taille=9, fill="var(--muted)", anc="middle", gras=False):
    """Un couple de <text> bilingues, ou un seul si les deux chaines coincident."""
    att = ('x="%s" y="%s" text-anchor="%s" font-family="var(--mono)" '
           'font-size="%s" fill="%s"' % (x, y, anc, taille, fill))
    if gras:
        att += ' font-weight="600"'
    if en == fr:
        return '<text %s>%s</text>' % (att, en)
    return ('<text class="l-en" %s>%s</text><text class="l-fr" %s>%s</text>'
            % (att, en, att, fr))


# --------------------------------------------------------------------- axes

def echelle(vmin, vmax):
    """Retourne la fonction valeur -> ordonnee, avec une marge haute de 6 %."""
    if vmax - vmin < 1e-9:
        vmax = vmin + 1.0
    marge = (vmax - vmin) * 0.06
    lo, hi = vmin - marge * 0.35, vmax + marge
    return lambda v: Y1 - (v - lo) * (Y1 - Y0) / (hi - lo), lo, hi


def pas_lisible(etendue, cible=6):
    brut = etendue / float(cible)
    mag = 10.0 ** math.floor(math.log10(brut)) if brut > 0 else 1.0
    for m in (1, 2, 2.5, 5, 10):
        if brut <= mag * m:
            return mag * m
    return mag * 10


def grille(y, lo, hi, dec=0, zero=False, suffixe=""):
    """Lignes horizontales et etiquettes de gauche."""
    pas = pas_lisible(hi - lo)
    if pas < 1:                       # echelle serree : garder assez de decimales
        dec = max(dec, int(math.ceil(-math.log10(pas) - 1e-9)))
    out = []
    t = math.ceil(lo / pas) * pas
    while t <= hi + 1e-9:
        yy = y(t)
        trait = "var(--line)" if (zero and abs(t) < 1e-9) else "var(--line-soft)"
        out.append('<path d="M56 %.1fH704" stroke="%s" stroke-width="1"/>' % (yy, trait))
        en, fr = nb(t, dec)
        out.append(txt(48, "%.1f" % (yy + 3.2), en + suffixe, fr + suffixe, anc="end"))
        t += pas
    return "".join(out)


def grille_log(y, dmin, dmax):
    out = []
    for d in range(dmin, dmax + 1):
        yy = y(d)
        en, fr = nb(10.0 ** d, max(0, -d))
        out.append('<path d="M56 %.1fH704" stroke="var(--line-soft)" stroke-width="1"/>' % yy)
        out.append(txt(48, "%.1f" % (yy + 3.2), en, fr, anc="end"))
    return "".join(out)


def courbe(pts, couleur="var(--pine)", points=True):
    d = "L".join("%.1f %.1f" % p for p in pts)
    out = ['<path d="M%s" stroke="%s" stroke-width="1.7" fill="none" '
           'stroke-linejoin="round" stroke-linecap="round"/>' % (d, couleur)]
    if points:
        for x, yy in pts:
            out.append('<circle cx="%.1f" cy="%.1f" r="1.9" fill="%s"/>' % (x, yy, couleur))
    return "".join(out)


def projection(depuis, vers):
    return ('<g class="v-proj"><path d="M%.1f %.1fL%.1f %.1f" stroke="var(--brass)" '
            'stroke-width="1.7" stroke-dasharray="4 3" fill="none" stroke-linecap="round"/>'
            '<circle cx="%.1f" cy="%.1f" r="2.6" fill="var(--brass)"/></g>'
            % (depuis[0], depuis[1], vers[0], vers[1], vers[0], vers[1]))


# ------------------------------------------------------- les figures longues

def fig_annuelle(cle, annees, vals, proj, titre_en, titre_fr, alt, source_en, source_fr,
                 dec=1, log=False, zero=False, suffixe=""):
    n = len(annees)
    xs = [X0 + i * (X1 - 18.0 - X0) / (n - 1) for i in range(n)]

    if log:
        lv = [math.log10(max(v, 0.05)) for v in vals]
        pv = math.log10(max(proj, 0.05)) if proj is not None else None
        tout = lv + ([pv] if pv is not None else [])
        dmin, dmax = int(math.floor(min(tout))), int(math.ceil(max(tout)))
        y = lambda l: Y1 - (l - dmin) * (Y1 - Y0) / float(max(dmax - dmin, 1))
        pts = list(zip(xs, [y(v) for v in lv]))
        axes = grille_log(y, dmin, dmax)
        ypro = y(pv) if pv is not None else None
    else:
        tout = list(vals) + ([proj] if proj is not None else [])
        y, lo, hi = echelle(min(tout), max(tout))
        pts = list(zip(xs, [y(v) for v in vals]))
        axes = grille(y, lo, hi, dec=0, zero=zero, suffixe=suffixe)
        ypro = y(proj) if proj is not None else None

    corps = [axes, courbe(pts)]
    if ypro is not None:
        corps.append(projection(pts[-1], (X1, ypro)))

    # etiquettes d'annees tous les cinq ans
    for i, a in enumerate(annees):
        if a % 5 == 0 or i == n - 1:
            if a % 5 == 0:
                corps.append(txt("%.1f" % xs[i], YLAB, str(a), str(a)))

    # trois reperes chiffres : minimum, maximum, dernier point
    imin, imax = vals.index(min(vals)), vals.index(max(vals))
    for i, anc, dy in ((imin, "middle", 12), (imax, "middle", -8), (n - 1, "end", -9)):
        en, fr = nb(vals[i], dec)
        corps.append(txt("%.1f" % xs[i], "%.1f" % (pts[i][1] + dy), en, fr,
                         taille=10, fill="var(--ink-soft)", anc=anc))

    svg = ('<svg viewBox="0 0 720 250" role="img" aria-label="%s">%s</svg>'
           % (alt, "".join(corps)))
    return figure(cle, titre_en, titre_fr, svg, source_en, source_fr)


def figure(cle, t_en, t_fr, svg, s_en, s_fr):
    return ('        <figure class="fig" id="fig-%s">\n'
            '          <figcaption class="fig-t"><span class="l-en">%s</span>'
            '<span class="l-fr" lang="fr">%s</span></figcaption>\n'
            '          %s\n'
            '          <p class="fig-s"><span class="l-en">%s</span>'
            '<span class="l-fr" lang="fr">%s</span>' + DROITS + '</p>\n'
            '          <div class="dlbar" data-series="%s"><button type="button" class="dl" '
            'data-fmt="csv">CSV</button><button type="button" class="dl" '
            'data-fmt="xlsx">XLSX</button></div>\n'
            '        </figure>\n' % (cle, t_en, t_fr, svg, s_en, s_fr, cle))


# --------------------------------------------------------- les figures BCC

def _jour(iso):
    p = (iso + "-01-01").split("-")
    return int(p[0]), int(p[1]), int(p[2])


def _ord(iso):
    a, m, j = _jour(iso)
    return a * 372 + (m - 1) * 31 + (j - 1)


def fig_taux(serie):
    """Escalier du taux directeur."""
    o = [_ord(d) for d, _ in serie]
    v = [x for _, x in serie]
    fin = max(o) + 190
    deb = min(o)
    X = lambda t: X0 + (t - deb) * (X1 - X0) / float(fin - deb)
    y, lo, hi = echelle(0.0, max(v))
    corps = [grille(y, lo, hi, zero=True)]

    d = "M%.1f %.1f" % (X(o[0]), y(v[0]))
    for i in range(1, len(o)):
        d += "H%.1fV%.1f" % (X(o[i]), y(v[i]))
    d += "H%.1f" % X1
    corps.append('<path d="%s" stroke="var(--pine)" stroke-width="1.7" fill="none" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % d)
    for i in range(len(o)):
        corps.append('<circle cx="%.1f" cy="%.1f" r="2.2" fill="var(--pine)"/>'
                     % (X(o[i]), y(v[i])))

    # trois reperes : premier, sommet, dernier
    hi_i = v.index(max(v))
    for i, anc, dx, dy in ((0, "start", 4, -8), (hi_i, "middle", 0, -8),
                           (len(o) - 1, "end", 0, -8)):
        en, fr = nb(v[i], 1)
        corps.append(txt("%.1f" % (X(o[i]) + dx), "%.1f" % (y(v[i]) + dy),
                         en + "%", fr + "&#8239;%", fill="var(--ink-soft)",
                         anc=anc, gras=True))

    a0, a1 = _jour(serie[0][0])[0], _jour(serie[-1][0])[0]
    for a in range(a0, a1 + 1):
        corps.append(txt("%.1f" % X(a * 372), YLAB, str(a), str(a)))

    alt = ("Policy rate of the Central Bank of the Congo, %s to %s" % (a0, a1))
    return '<svg viewBox="0 0 720 250" role="img" aria-label="%s">%s</svg>' % (alt, "".join(corps))


def fig_reserves(serie):
    """Releves hebdomadaires, avec le crochet d'annee sous l'axe."""
    o = [_ord(d) for d, _ in serie]
    v = [x for _, x in serie]
    deb, fin = min(o) - 20, max(o) + 30
    X = lambda t: X0 + (t - deb) * (X1 - X0) / float(fin - deb)
    y, lo, hi = echelle(min(v), max(v))
    corps = [grille(y, lo, hi)]
    pts = [(X(t), y(x)) for t, x in zip(o, v)]
    corps.append(courbe(pts))
    for i, ((x, yy), val) in enumerate(zip(pts, v)):
        av = v[i - 1] if i else val
        ap = v[i + 1] if i + 1 < len(v) else val
        creux   = val <= av and val <= ap        # point bas : etiquette dessous
        sommet  = val >= av and val >= ap        # point haut : etiquette dessus
        dy  = 14 if creux else -9
        anc = "middle" if (creux or sommet) else "end"
        dx  = 0 if anc == "middle" else -6       # sur une pente : decaler a gauche
        en, fr = nb(val, 2)
        corps.append(txt("%.1f" % (x + dx), "%.1f" % (yy + dy), en, fr,
                         fill="var(--ink-soft)", anc=anc, gras=True))
    a0 = _jour(serie[0][0])[0]
    m0, m1 = _jour(serie[0][0])[1], _jour(serie[-1][0])[1]
    for m in range(m0, m1 + 2):
        if m > 12:
            break
        corps.append(txt("%.1f" % X(a0 * 372 + (m - 1) * 31 + 14), YLAB,
                         ABR_EN[m - 1], ABR_FR[m - 1]))
    corps.append('<text x="380" y="240" text-anchor="middle" font-family="var(--mono)" '
                 'font-size="9" letter-spacing="0.12em" fill="var(--muted)">%d</text>' % a0)
    corps.append('<path d="M56 222V228H704V222" fill="none" stroke="var(--line)" stroke-width="1"/>')
    alt = ("International reserves of the Democratic Republic of the Congo in %d, "
           "billions of US dollars" % a0)
    return '<svg viewBox="0 0 720 252" role="img" aria-label="%s">%s</svg>' % (alt, "".join(corps))


# ------------------------------------------------------------- tableau, KPI

def tableau(t):
    cols, pj = t["cols"], t.get("proj_col", -1)
    h = ['<tr><th scope="col"><span class="l-en">Indicator</span>'
         '<span class="l-fr" lang="fr">Indicateur</span></th>']
    for i, c in enumerate(cols):
        h.append('<th scope="col">%s%s</th>' % (c, '<span class="pj">p</span>' if i == pj else ''))
    h.append('<th scope="col"><span class="l-en">Source</span>'
             '<span class="l-fr" lang="fr">Source</span></th></tr>')
    corps = []
    for r in t["rows"]:
        c = ['<tr><th scope="row"><span class="l-en">%s</span>'
             '<span class="l-fr" lang="fr">%s</span></th>' % (r["en"], r["fr"])]
        for val in r["v"]:
            if val in (None, "", "&#8212;"):
                c.append('<td class="na">&#8212;</td>')
            else:
                c.append('<td class="n"><span class="l-en">%s</span>'
                         '<span class="l-fr" lang="fr">%s</span></td>'
                         % (val, val.replace(".", ",")))
        c.append('<td class="src">%s</td></tr>' % r["src"])
        corps.append("".join(c))
    return ('<div class="tablewrap">\n        <table class="macro-tab">\n'
            '          <thead>\n            %s\n          </thead>\n'
            '          <tbody>\n          %s\n          </tbody>\n'
            '        </table>\n      </div>' % ("".join(h), "\n          ".join(corps)))


def releve(kpi):
    out = ['<dl class="macro-now">']
    for k in kpi:
        out.append('<div><dt><span class="l-en">%s</span><span class="l-fr" lang="fr">%s</span></dt>'
                   '<dd><b><span class="l-en">%s</span><span class="l-fr" lang="fr">%s</span></b> '
                   '<span class="when"><span class="l-en">%s</span>'
                   '<span class="l-fr" lang="fr">%s</span></span></dd></div>'
                   % (k["en"], k["fr"], k["v_en"], k["v_fr"], k["w_en"], k["w_fr"]))
    out.append("</dl>")
    return "\n        ".join(out)


# ------------------------------------------------------------------- sortie

def main():
    M = _lit("macro-rdc.json")
    B = _lit("bcc.json")
    ans, pr = M["annees"], M["proj"]

    figs = [
        fig_annuelle("pib-croissance", ans, M["croissance"], pr.get("croissance"),
                     "Real GDP growth, %d&#8211;%d, per cent" % (ans[0], pr["annee"]),
                     "Croissance du PIB r&#233;el, %d&#8211;%d, en pourcentage" % (ans[0], pr["annee"]),
                     "Real GDP growth in the Democratic Republic of the Congo, "
                     "%d to %d, per cent" % (ans[0], pr["annee"]),
                     "Sources: IMF World Economic Outlook, World Bank and Banque Centrale du Congo. "
                     "Annual data, per cent; the dashed segment is a projection.",
                     "Sources&nbsp;: FMI, Perspectives de l&#8217;&#233;conomie mondiale, Banque mondiale "
                     "et Banque Centrale du Congo. Donn&#233;es annuelles, en pourcentage&nbsp;; le segment "
                     "en tiret&#233;s est une projection.",
                     zero=True),
        fig_annuelle("inflation-longue", ans, M["inflation"], pr.get("inflation"),
                     "Consumer price inflation, %d&#8211;%d, logarithmic scale" % (ans[0], pr["annee"]),
                     "Inflation des prix &#224; la consommation, %d&#8211;%d, &#233;chelle logarithmique"
                     % (ans[0], pr["annee"]),
                     "Consumer price inflation in the Democratic Republic of the Congo, "
                     "%d to %d, per cent, logarithmic scale" % (ans[0], pr["annee"]),
                     "Sources: IMF and World Bank consumer price series; African Development Bank for "
                     "the most recent years. The vertical scale is logarithmic, so each gridline is ten "
                     "times the one below it.",
                     "Sources&nbsp;: s&#233;ries de prix &#224; la consommation du FMI et de la Banque "
                     "mondiale&nbsp;; Banque africaine de d&#233;veloppement pour les ann&#233;es les plus "
                     "r&#233;centes. L&#8217;&#233;chelle verticale est logarithmique&nbsp;: chaque ligne "
                     "vaut dix fois la pr&#233;c&#233;dente.",
                     log=True),
        fig_annuelle("pib-indice", ans, M["indice"], pr.get("indice"),
                     "Real GDP, index, 2015 = 100, %d&#8211;%d" % (ans[0], pr["annee"]),
                     "PIB r&#233;el, indice 2015 = 100, %d&#8211;%d" % (ans[0], pr["annee"]),
                     "Real GDP of the Democratic Republic of the Congo, index 2015 equals 100, "
                     "%d to %d" % (ans[0], pr["annee"]),
                     "Own calculation, chaining the annual growth rates on a 2015 base. Output lost "
                     "close to half its level between 1990 and 2001 and regained the 1990 level only "
                     "in the second half of the 2000s.",
                     "Calcul de l&#8217;auteur, par cha&#238;nage des taux de croissance annuels sur une "
                     "base 2015. La production a perdu pr&#232;s de la moiti&#233; de son niveau entre 1990 "
                     "et 2001 et n&#8217;a retrouv&#233; celui de 1990 que dans la seconde moiti&#233; des "
                     "ann&#233;es 2000.",
                     dec=0),
    ]
    ecrit("macro_figs.html", '<div class="figs">\n%s        </div>' % "".join(figs))

    bf = [
        figure("taux-directeur",
               "BCC policy rate, %s &#8211; %s, per cent"
               % (_lib(B["taux_directeur"][0][0], "en"), _lib(B["taux_directeur"][-1][0], "en")),
               "Taux directeur de la BCC, %s &#8211; %s, en pourcentage"
               % (_lib(B["taux_directeur"][0][0], "fr"), _lib(B["taux_directeur"][-1][0], "fr")),
               fig_taux(B["taux_directeur"]),
               "Source: Banque Centrale du Congo, Monetary Policy Committee. The series records every "
               "decision of the Committee; the rate is held flat between two decisions.",
               "Source&nbsp;: Banque Centrale du Congo, Comit&#233; de politique mon&#233;taire. La s&#233;rie "
               "retient chaque d&#233;cision du Comit&#233;&nbsp;; le taux reste constant entre deux "
               "d&#233;cisions."),
        figure("reserves",
               "International reserves, %s, billions of US dollars" % B["reserves"][0][0][:4],
               "R&#233;serves internationales, %s, en milliards de dollars" % B["reserves"][0][0][:4],
               fig_reserves(B["reserves"]),
               "Source: weekly readings published by the Banque Centrale du Congo; months are shown as "
               "numbers. Reserves hover around eight billion dollars, close to three months of imports, "
               "and move with mining receipts and external disbursements.",
               "Source&nbsp;: relev&#233;s hebdomadaires publi&#233;s par la Banque Centrale du Congo&nbsp;; "
               "les mois sont indiqu&#233;s en chiffres. Les r&#233;serves &#233;voluent autour de huit "
               "milliards de dollars, soit pr&#232;s de trois mois d&#8217;importations, et suivent les "
               "recettes mini&#232;res et les d&#233;caissements ext&#233;rieurs."),
    ]
    ecrit("bcc_figs.html", '<div class="figs">\n%s      </div>' % "".join(bf))
    ecrit("macro_tab.html", tableau(M["tableau"]))
    ecrit("bcc_kpi.html", releve(B["kpi"]))

    reg = {
        "pib-croissance": _serie("Real GDP growth, per cent",
                                 "Croissance du PIB r&#233;el, en pourcentage",
                                 "IMF, World Bank, BCC, AfDB", ["Year", "Real GDP growth, %"],
                                 ans, M["croissance"], pr, "croissance"),
        "inflation-longue": _serie("Consumer price inflation, per cent",
                                   "Inflation des prix &#224; la consommation, en pourcentage",
                                   "IMF, World Bank, BCC", ["Year", "Inflation, %"],
                                   ans, M["inflation"], pr, "inflation"),
        "pib-indice": _serie("Real GDP, index 2015 = 100",
                             "PIB r&#233;el, indice 2015 = 100",
                             "IMF, World Bank, BCC", ["Year", "Index, 2015 = 100"],
                             ans, M["indice"], pr, "indice"),
        "taux-directeur": {"name_en": "BCC policy rate", "name_fr": "Taux directeur de la BCC",
                           "source": "Banque Centrale du Congo, Monetary Policy Committee",
                           "cols": ["Effective date", "Policy rate, %"],
                           "rows": [[d, v] for d, v in B["taux_directeur"]], "note": ""},
        "reserves": {"name_en": "International reserves, billions of US dollars",
                     "name_fr": "R&#233;serves internationales, en milliards de dollars",
                     "source": "Banque Centrale du Congo, weekly readings",
                     "cols": ["Week ending", "Reserves, $bn"],
                     "rows": [[d, v] for d, v in B["reserves"]], "note": ""},
    }
    open(os.path.join(_HERE, "series_macro.json"), "w", encoding="utf-8").write(
        json.dumps(reg, ensure_ascii=False))
    print("mkmacro : %d figures, %d series" % (len(figs) + len(bf), len(reg)))


def _serie(ne, nf, src, cols, ans, vals, pr, cle):
    rows = [[a, v] for a, v in zip(ans, vals)]
    if pr.get(cle) is not None:
        rows.append([pr["annee"], pr[cle]])
    return {"name_en": ne, "name_fr": nf, "source": src, "cols": cols,
            "rows": rows, "note": "Serie telle que tracee dans la figure."}


def _lib(iso, lang):
    a, m, _ = _jour(iso)
    return "%s %d" % ((MOIS_EN if lang == "en" else MOIS_FR)[m - 1], a)


def ecrit(nom, contenu):
    open(os.path.join(_HERE, nom), "w", encoding="utf-8").write(contenu)


if __name__ == "__main__":
    main()
