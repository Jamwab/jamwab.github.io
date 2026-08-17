#!/usr/bin/env python3
"""
Update publications.json from SSRN, Crossref and, if you have one, ORCID.

Run it locally with:      python3 sync_publications.py
Or let the GitHub Action run it every night.

Only the standard library is used, so there is nothing to install.

Rules the script follows:
  - An entry already in publications.json is never overwritten. Your wording,
    your abstract and your topic tag survive every run.
  - A work is only added if its title is not already there.
  - Entries you wrote yourself keep "source": "manual" and are left alone.
"""

import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

# ---------------------------------------------------------------- settings

SSRN_AUTHOR_ID = "12206410"
SCHOLAR_AUTHOR_ID = "1d2zZn8AAAAJ"

# Papers that live only in the HTML, not in publications.json. Title on the left
# as Google Scholar spells it, the exact link used on the page on the right.
HTML_ONLY_WORKS = {
    "Une matrice de comptabilite sociale pour la rd congo: Mcs-rdc2005":
        "https://ideas.repec.org/p/pra/mprapa/65020.html",
    "Croisssance agricole et options d'investissement en rd congo: une analyse en equilibre general calculable":
        "https://ideas.repec.org/p/pra/mprapa/64828.html",
    "Analyse de l'economie congolaise a travers la matrice de comptabilite sociale de 2005":
        "https://ideas.repec.org/p/pra/mprapa/65037.html",
    "Zone de libre echange de la sadc et economie de la RDCongo: Creation de commerce et Bien-etre?":
        "https://ideas.repec.org/p/pra/mprapa/65050.html",
    "Markups, Trend positif d'inflation et Couts en bien-etre":
        "https://ideas.repec.org/p/pra/mprapa/71686.html",
    "Croissance schumpeterienne et taxe sur la pollution":
        "https://ideas.repec.org/p/pra/mprapa/65071.html",
}
CROSSREF_AUTHOR = "Wabenga Yango"
ORCID_ID = "0000-0002-4675-4583"
CONTACT_EMAIL = "james.wabenga-yango.1@ulaval.ca"   # Crossref asks for this

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publications.json")
TIMEOUT = 30

# Words that decide which filter chip a new work lands under.
TOPICS = [
    ("money", ["monetary", "inflation", "exchange rate", "dollariz", "interest rate",
               "central bank", "fiscal", "markup", "policy rate"]),
    ("cge", ["computable general equilibrium", "cge", "social accounting",
             "agricultur", "poverty", "trade liberal", "tariff", "development"]),
    ("demographics", ["demographic", "ageing", "aging", "fertility", "migration",
                      "longevity", "life-cycle", "life cycle", "overlapping generations",
                      "population", "pension"]),
]


def normalise(text):
    text = unicodedata.normalize("NFD", (text or "").lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def guess_topic(title, abstract=""):
    blob = (title + " " + (abstract or "")).lower()
    for topic, words in TOPICS:
        if any(w in blob for w in words):
            return topic
    return "demographics"


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {
        "User-Agent": "wabenga-site-sync/1.0 (mailto:%s)" % CONTACT_EMAIL,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


# ---------------------------------------------------------------- sources

def from_ssrn():
    """SSRN publishes a public RSS feed for every author page."""
    url = "https://api.ssrn.com/content/v1/authors/%s/papers/rss" % SSRN_AUTHOR_ID
    try:
        xml = get(url, headers={"User-Agent": "wabenga-site-sync/1.0",
                                "Accept": "application/rss+xml, application/xml"})
    except Exception as exc:
        print("  SSRN unavailable: %s" % exc)
        return []

    works = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        def tag(name):
            m = re.search(r"<%s>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</%s>" % (name, name), item, re.S)
            return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""

        title = tag("title")
        if not title:
            continue
        link = tag("link")
        pub = tag("pubDate")
        year = int(re.search(r"(20\d\d)", pub).group(1)) if re.search(r"(20\d\d)", pub) else date.today().year
        abstract = tag("description")
        abstract_id = re.search(r"abstract_id=(\d+)", link)
        works.append({
            "id": "ssrn-%s" % (abstract_id.group(1) if abstract_id else normalise(title)[:24].replace(" ", "-")),
            "title": title,
            "year": year,
            "authors": "Wabenga Yango, James",
            "coauthors_label_en": "Single-authored",
            "coauthors_label_fr": "Auteur unique",
            "venue": "SSRN",
            "url": link,
            "topic": guess_topic(title, abstract),
            "abstract": abstract[:1400],
            "source": "ssrn",
        })
    print("  SSRN: %d item(s)" % len(works))
    return works


def from_crossref():
    """Crossref covers anything with a DOI, including SSRN and journal articles."""
    url = ("https://api.crossref.org/works?query.author=%s&rows=60&select=DOI,title,issued,author,container-title,URL"
           % urllib.parse.quote(CROSSREF_AUTHOR))
    try:
        data = json.loads(get(url))
    except Exception as exc:
        print("  Crossref unavailable: %s" % exc)
        return []

    works = []
    for it in data.get("message", {}).get("items", []):
        names = [("%s %s" % (a.get("given", ""), a.get("family", ""))).strip()
                 for a in it.get("author", [])]
        if not any("wabenga" in normalise(n) for n in names):
            continue
        title = (it.get("title") or [""])[0]
        if not title:
            continue
        parts = it.get("issued", {}).get("date-parts", [[None]])[0]
        year = parts[0] or date.today().year
        others = [n for n in names if "wabenga" not in normalise(n)]
        label_en = "with " + " and ".join(others) if others else "Single-authored"
        label_fr = "avec " + " et ".join(others) if others else "Auteur unique"
        venue = (it.get("container-title") or [""])[0]
        works.append({
            "id": "doi-" + re.sub(r"[^a-z0-9]+", "-", (it.get("DOI") or "").lower()),
            "title": title,
            "year": int(year),
            "authors": "; ".join(names) or "Wabenga Yango, James",
            "coauthors_label_en": label_en,
            "coauthors_label_fr": label_fr,
            "venue": venue,
            "url": it.get("URL", ""),
            "doi": it.get("DOI", ""),
            "topic": guess_topic(title),
            "source": "crossref",
        })
    print("  Crossref: %d item(s)" % len(works))
    return works


def from_orcid():
    if not ORCID_ID:
        return []
    url = "https://pub.orcid.org/v3.0/%s/works" % ORCID_ID
    try:
        data = json.loads(get(url))
    except Exception as exc:
        print("  ORCID unavailable: %s" % exc)
        return []

    works = []
    for group in data.get("group", []):
        summary = (group.get("work-summary") or [{}])[0]
        title = ((summary.get("title") or {}).get("title") or {}).get("value", "")
        if not title:
            continue
        year = ((summary.get("publication-date") or {}).get("year") or {}).get("value")
        ext = [i for i in ((summary.get("external-ids") or {}).get("external-id") or [])
               if i.get("external-id-type") == "doi"]
        works.append({
            "id": "orcid-" + normalise(title)[:24].replace(" ", "-"),
            "title": title,
            "year": int(year) if year else date.today().year,
            "authors": "Wabenga Yango, James",
            "coauthors_label_en": "",
            "coauthors_label_fr": "",
            "venue": (summary.get("journal-title") or {}).get("value", ""),
            "url": ((summary.get("url") or {}) or {}).get("value", ""),
            "doi": ext[0].get("external-id-value", "") if ext else "",
            "topic": guess_topic(title),
            "source": "orcid",
        })
    print("  ORCID: %d item(s)" % len(works))
    return works



def scholar_counts():
    """Google Scholar counts, best effort.

    Scholar has no API and blocks robots, so there are only two honest routes:
      1. SerpApi, which pays Google for legitimate access. Set SERPAPI_KEY in
         the environment (a free tier covers a nightly run) and this works.
      2. The scholarly package, if it happens to be installed. Google throttles
         it, so treat a failure as normal rather than as a bug.
    Returns {normalised title: count}.
    """
    out = {}

    key = os.environ.get("SERPAPI_KEY", "").strip()
    if key:
        try:
            url = ("https://serpapi.com/search.json?engine=google_scholar_author"
                   "&author_id=%s&num=100&api_key=%s" % (SCHOLAR_AUTHOR_ID, key))
            data = json.loads(get(url))
            for art in data.get("articles", []):
                cited = (art.get("cited_by") or {}).get("value")
                if isinstance(cited, int):
                    out[normalise(art.get("title", ""))] = cited
            print("  Google Scholar via SerpApi: %d article(s)" % len(out))
            return out
        except Exception as exc:
            print("  SerpApi unavailable: %s" % exc)

    try:
        from scholarly import scholarly           # type: ignore
        author = scholarly.search_author_id(SCHOLAR_AUTHOR_ID)
        author = scholarly.fill(author, sections=["publications"])
        for pub in author.get("publications", []):
            title = (pub.get("bib") or {}).get("title", "")
            cited = pub.get("num_citations")
            if title and isinstance(cited, int):
                out[normalise(title)] = cited
        print("  Google Scholar via scholarly: %d article(s)" % len(out))
    except ImportError:
        print("  Google Scholar skipped: no SERPAPI_KEY and scholarly not installed")
    except Exception as exc:
        print("  Google Scholar refused the request: %s" % exc)
    return out


def semantic_scholar_count(work):
    """Semantic Scholar, free and keyless, by DOI when there is one, else by title."""
    try:
        if work.get("doi"):
            url = ("https://api.semanticscholar.org/graph/v1/paper/DOI:%s?fields=citationCount"
                   % urllib.parse.quote(work["doi"]))
            return json.loads(get(url)).get("citationCount")
        url = ("https://api.semanticscholar.org/graph/v1/paper/search?query=%s&limit=1&fields=title,citationCount"
               % urllib.parse.quote(work.get("title", "")[:180]))
        hits = json.loads(get(url)).get("data") or []
        if hits and normalise(hits[0].get("title", "")) == normalise(work.get("title", "")):
            return hits[0].get("citationCount")
    except Exception:
        pass
    return None


def crossref_count(work):
    if not work.get("doi"):
        return None
    try:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(work["doi"])
        return json.loads(get(url)).get("message", {}).get("is-referenced-by-count")
    except Exception:
        return None


def refresh_citations(store):
    """Fill store["citations"], keyed by the link each work uses on the page.

    A count is only ever raised, never lowered, so a good Scholar figure is not
    wiped out by a thinner Crossref one on the next run.
    """
    counts = store.setdefault("citations", {})
    scholar = scholar_counts()

    for w in store.get("works", []):
        link = w.get("url")
        if not link:
            continue
        candidates = [
            scholar.get(normalise(w.get("title", ""))),
            crossref_count(w),
            semantic_scholar_count(w),
        ]
        best = max([c for c in candidates if isinstance(c, int)] or [0])
        if best > counts.get(link, 0):
            counts[link] = best
            print("  %-60s %d" % (w.get("title", "")[:60], best))

    # works that live only in the HTML (the MPRA papers) are matched by title
    for title, link in HTML_ONLY_WORKS.items():
        n = scholar.get(normalise(title))
        if isinstance(n, int) and n > counts.get(link, 0):
            counts[link] = n
            print("  %-60s %d" % (title[:60], n))

    return counts


def update_html_badges(store):
    """Write the counts straight into index.html.

    This is what makes the badges appear even when the page is opened from disk,
    where a browser refuses to read publications.json.
    """
    path = os.path.join(os.path.dirname(OUTPUT), "index.html")
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    before = html

    for link, n in (store.get("citations") or {}).items():
        if not isinstance(n, int) or n <= 0:
            continue
        i = html.find('href="%s"' % link)
        if i < 0:
            continue
        stop = html.find("</li>", i)
        alt = html.find("</article>", i)
        if alt > 0 and (stop < 0 or alt < stop):
            stop = alt
        if stop < 0:
            continue
        seg = html[i:stop]
        badge = ('<span class="cited"><span class="l-en">Cited by %d</span>'
                 '<span class="l-fr" lang="fr">%s</span></span>'
                 % (n, "Cité 1 fois" if n == 1 else "Cité %d fois" % n))
        if 'class="cited"' in seg:
            seg = re.sub(r'<span class="cited">.*?</span></span>', badge, seg, count=1, flags=re.S)
            html = html[:i] + seg + html[stop:]
        else:
            html = html[:stop] + badge + html[stop:]

    if html != before:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print("index.html badges refreshed.")
        return True
    return False


# ---------------------------------------------------------------- merge

def main():
    if os.path.exists(OUTPUT):
        with open(OUTPUT, encoding="utf-8") as fh:
            store = json.load(fh)
    else:
        store = {"works": []}

    existing = store.get("works", [])
    seen = {normalise(w.get("title", "")) for w in existing}

    print("Fetching:")
    incoming = from_ssrn() + from_crossref() + from_orcid()

    print("Citation counts:")
    before = json.dumps(store.get("citations", {}), sort_keys=True)
    refresh_citations(store)
    citations_changed = json.dumps(store.get("citations", {}), sort_keys=True) != before

    added = []
    for w in incoming:
        key = normalise(w["title"])
        if key in seen or not key:
            continue
        seen.add(key)
        added.append(w)

    if not added and not citations_changed:
        print("Nothing new. publications.json left untouched.")
        return 0

    store["works"] = added + existing
    store["updated"] = date.today().isoformat()
    update_html_badges(store)
    with open(OUTPUT, "w", encoding="utf-8") as fh:
        json.dump(store, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    if added:
        print("\nAdded %d work(s):" % len(added))
        for w in added:
            print("  %s  %s" % (w["year"], w["title"][:80]))
    if citations_changed:
        print("Citation counts updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
