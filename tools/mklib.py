# -*- coding: utf-8 -*-
"""Outils communs : formatage bilingue, primitives SVG, registre des series."""
import datetime as _dt
import json, math

# La composition des planches appartient a l'auteur : chaque note de
# source la revendique, et le millesime suit la date de fabrication.
DROITS = '<span class="fig-c">\u00a9 %d James Wabenga Yango</span>' \
    % _dt.date.today().year

NBSP = "&#8239;"
SERIES = {}          # cle -> dict(name_en, name_fr, unit_en, unit_fr, source, cols, rows)


def reg(key, name_en, name_fr, source, cols, rows, note=""):
    SERIES[key] = dict(name_en=name_en, name_fr=name_fr, source=source,
                       cols=cols, rows=rows, note=note)
    return key


def gr(n, dec=0):
    """Groupe les milliers avec une espace fine, separateur decimal virgule."""
    s = f"{n:,.{dec}f}"
    return s.replace(",", NBSP).replace(".", ",")


def ge(n, dec=0):
    return f"{n:,.{dec}f}"


def bil(en, fr):
    return f'<span class="l-en">{en}</span><span class="l-fr" lang="fr">{fr}</span>'


def tsp(en, fr):
    return f'<tspan class="l-en">{en}</tspan><tspan class="l-fr" lang="fr">{fr}</tspan>'


def num(n, dec=0):
    return tsp(ge(n, dec), gr(n, dec))


def tnum(n, dec=0):
    return bil(ge(n, dec), gr(n, dec))


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace("é", "&#233;").replace("è", "&#232;").replace("ê", "&#234;")
             .replace("à", "&#224;").replace("â", "&#226;").replace("î", "&#238;")
             .replace("ï", "&#239;").replace("ô", "&#244;").replace("û", "&#251;")
             .replace("ù", "&#249;").replace("ç", "&#231;").replace("É", "&#201;")
             .replace("Ê", "&#202;").replace("È", "&#200;").replace("Â", "&#194;")
             .replace("Î", "&#206;").replace("Ô", "&#212;").replace("Û", "&#219;")
             .replace("«", "&#171;").replace("»", "&#187;").replace("’", "&#8217;")
             .replace("—", "&#8212;").replace("–", "&#8211;").replace("°", "&#176;"))


# --------------------------------------------------------------- primitives
def txt(x, y, s, size=9, fill="var(--muted)", anchor="start", family="mono",
        weight=None, ls=None):
    a = f'<text x="{x}" y="{y}" font-family="var(--{family})" font-size="{size}" fill="{fill}"'
    if anchor != "start":
        a += f' text-anchor="{anchor}"'
    if weight:
        a += f' font-weight="{weight}"'
    if ls:
        a += f' letter-spacing="{ls}"'
    return a + f">{s}</text>"


def line(x1, y1, x2, y2, stroke="var(--line-soft)", w=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>')


def rect(x, y, w, h, fill, op=None, rx=None):
    a = f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w,0):.1f}" height="{max(h,0):.1f}" fill="{fill}"'
    if op is not None:
        a += f' opacity="{op}"'
    if rx:
        a += f' rx="{rx}"'
    return a + "/>"


def circ(x, y, r, fill, stroke=None, sw=1, op=None):
    a = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"'
    if stroke:
        a += f' stroke="{stroke}" stroke-width="{sw}"'
    if op is not None:
        a += f' opacity="{op}"'
    return a + "/>"


def poly(pts, stroke, w=1.7, dash=None):
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"{da}/>')


def svg_open(vw, vh, aria):
    return f'<svg viewBox="0 0 720 {vh}" role="img" aria-label="{aria}">'


# --------------------------------------------------------------- cadre standard
PX0, PX1, PY0, PY1 = 56.0, 704.0, 20.0, 194.0
LABY = 214


def yscale(v, lo, hi):
    return PY1 - (PY1 - PY0) * (v - lo) / (hi - lo)


def xord(i, n):
    """Axe ordinal : n points repartis entre PX0 et PX1 avec une demi-marge."""
    if n == 1:
        return (PX0 + PX1) / 2
    pad = (PX1 - PX0) * 0.045
    return PX0 + pad + (PX1 - PX0 - 2 * pad) * i / (n - 1)


def ygrid(vals, lo, hi, fmt=lambda v: (str(v), str(v))):
    out = []
    for v in vals:
        y = yscale(v, lo, hi)
        out.append(line(PX0, y, PX1, y, "var(--line-soft)"))
        e, f = fmt(v)
        out.append(txt(PX0 - 8, y + 3, tsp(e, f), 9, "var(--muted)", "end"))
    return "".join(out)


def xlabels(labels, n):
    out = []
    for i, (e, f) in enumerate(labels):
        out.append(txt(xord(i, n), LABY, tsp(e, f), 9, "var(--muted)", "middle"))
    return "".join(out)


def legend(items, y, x0=56, step=None):
    """items : liste de (couleur, libelle_en, libelle_fr)."""
    out = []
    x = x0
    for c, e, f in items:
        out.append(rect(x, y - 7.5, 9, 9, c))
        out.append(txt(x + 14, y, tsp(e, f), 8.6, "var(--muted)"))
        x += step if step else max(len(e), len(f)) * 5.4 + 34
    return "".join(out)


def figure(key, title_en, title_fr, svg, src_en, src_fr, dl=True):
    dlbar = ""
    if dl:
        dlbar = (f'<div class="dlbar" data-series="{key}">'
                 f'<button type="button" class="dl" data-fmt="csv">CSV</button>'
                 f'<button type="button" class="dl" data-fmt="xlsx">XLSX</button>'
                 f'</div>')
    return (f'<figure class="fig" id="fig-{key}">'
            f'<figcaption class="fig-t">{bil(title_en, title_fr)}</figcaption>'
            f'{svg}'
            f'<p class="fig-s">{bil(src_en, src_fr)}{DROITS}</p>'
            f'{dlbar}</figure>')
