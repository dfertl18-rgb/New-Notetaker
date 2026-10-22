#!/usr/bin/env python3
"""Lädt Original-Logos für die private Spielversion von Quotenturm auf den eigenen Rechner.

Sender und Streamer:  python3 logos_holen.py
Filme, Serien, Shows: TMDB_API_KEY=dein_schluessel python3 logos_holen.py --titel

- Senderlogos kommen über die öffentliche Suche von Wikimedia Commons bzw. der deutschen Wikipedia.
- Titel-Logos (bei fehlendem Logo das Poster) kommen von TMDb und brauchen einen eigenen, kostenlosen API-Schlüssel
  (themoviedb.org → Einstellungen → API).
- Alles landet in ../logos bzw. ../logos/titel und ist per .gitignore vom Repository ausgeschlossen.
  Die Logos sind geschützte Marken: nur privat nutzen, nicht veröffentlichen.
- Die Suche nimmt den ersten passenden Treffer. Falsche Bilder einfach löschen oder durch eigene Dateien ersetzen
  (Dateiname = Spiel-ID, siehe logos/LIESMICH.md).
Nur Standardbibliothek, Python 3.8+.
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(GAME, "logos")
OUT_T = os.path.join(OUT, "titel")
UA = "Quotenturm-private-logo-fetch/1.0 (personal use)"

# Spiel-ID → Suchbegriff
SENDER = {
    "zdf": "ZDF logo", "ard": "Das Erste logo", "rtl": "RTL logo 2021", "sat1": "Sat.1 logo", "vox": "VOX logo",
    "pro7": "ProSieben logo", "kabel1": "Kabel Eins logo", "zdfneo": "ZDFneo logo", "rtl2": "RTL Zwei logo",
    "nitro": "Nitro RTL logo", "arte": "Arte logo",
    "netflix": "Netflix 2015 logo", "prime": "Prime Video logo", "disney": "Disney+ logo", "rtlplus": "RTL+ logo",
    "wow": "WOW Sky logo", "dazn": "DAZN logo", "joyn": "Joyn logo", "paramount": "Paramount+ logo", "mediathek": "ARD Mediathek logo",
}


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def slug(title):
    s = title.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def wiki_logo(term):
    """Erster Bildtreffer auf Commons, sonst deutsche Wikipedia; SVG wird als PNG (400 px, transparent) gerendert."""
    for api in ("https://commons.wikimedia.org/w/api.php", "https://de.wikipedia.org/w/api.php"):
        data = json.loads(get(api, {"action": "query", "format": "json", "generator": "search", "gsrsearch": term,
                                    "gsrnamespace": 6, "gsrlimit": 8, "prop": "imageinfo", "iiprop": "url|mime", "iiurlwidth": 400}))
        pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
        for p in pages:
            info = (p.get("imageinfo") or [{}])[0]
            if info.get("mime") in ("image/svg+xml", "image/png") and "logo" in p.get("title", "").lower():
                return p["title"], info.get("thumburl") or info.get("url")
    return None, None


def sender():
    os.makedirs(OUT, exist_ok=True)
    for gid, term in SENDER.items():
        try:
            name, url = wiki_logo(term)
            if not url:
                print(f"–  {gid}: nichts gefunden ({term})")
                continue
            with open(os.path.join(OUT, gid + ".png"), "wb") as f:
                f.write(get(url))
            print(f"✓  {gid}.png  ←  {name}")
        except Exception as e:  # einzelne Fehler sollen den Rest nicht stoppen
            print(f"✗  {gid}: {e}")
        time.sleep(0.5)


def game_titles():
    """Titel aus den Listen im Spiel (FILM_DB, SERIES_DB) lesen."""
    with open(os.path.join(GAME, "index.html"), encoding="utf-8") as f:
        html = f.read()
    out = []
    for const in ("FILM_DB", "SERIES_DB"):
        m = re.search(r"const %s = \[(.*?)\n\];" % const, html, re.S)
        if m:
            out += re.findall(r'\[\s*"((?:[^"\\]|\\.)*)"', m.group(1))
    return list(dict.fromkeys(out))


def titel():
    key = os.environ.get("TMDB_API_KEY")
    if not key:
        sys.exit("Bitte TMDB_API_KEY setzen (kostenloser Schlüssel von themoviedb.org).")
    os.makedirs(OUT_T, exist_ok=True)
    manifest_path = os.path.join(OUT_T, "liste.json")
    manifest = json.load(open(manifest_path, encoding="utf-8")) if os.path.exists(manifest_path) else {}
    for t in game_titles():
        s = slug(t)
        if s in manifest:
            continue
        try:
            res = json.loads(get("https://api.themoviedb.org/3/search/multi", {"api_key": key, "query": t, "language": "de-DE"}))
            hit = next((r for r in res.get("results", []) if r.get("media_type") in ("movie", "tv")), None)
            if not hit:
                print(f"–  {t}: kein Treffer")
                continue
            imgs = json.loads(get(f"https://api.themoviedb.org/3/{hit['media_type']}/{hit['id']}/images",
                                  {"api_key": key, "include_image_language": "de,en,null"}))
            logos = sorted(imgs.get("logos", []), key=lambda l: {"de": 0, "en": 1}.get(l.get("iso_639_1"), 2))
            if logos:
                path, ext, kind = logos[0]["file_path"], ".png", "logo"
            elif hit.get("poster_path"):
                path, ext, kind = hit["poster_path"], ".jpg", "poster"
            else:
                print(f"–  {t}: kein Bild")
                continue
            if path.endswith(".svg"):
                ext = ".svg"
            fname = s + ext
            with open(os.path.join(OUT_T, fname), "wb") as f:
                f.write(get("https://image.tmdb.org/t/p/w300" + path))
            manifest[s] = {"file": fname, "kind": kind}
            print(f"✓  {t}  →  titel/{fname} ({kind})")
        except Exception as e:
            print(f"✗  {t}: {e}")
        time.sleep(0.3)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    # Zusätzlich als Skript, weil Browser lokale JSON-Dateien (file://) oft nicht laden dürfen
    with open(os.path.join(OUT_T, "liste.js"), "w", encoding="utf-8") as f:
        f.write("window.QT_TITLES = " + json.dumps(manifest, ensure_ascii=False) + ";\n")
    print(f"\n{len(manifest)} Titelbilder in logos/titel/liste.json eingetragen.")


if __name__ == "__main__":
    titel() if "--titel" in sys.argv else sender()
