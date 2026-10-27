# Holt Fotos für die private Spielversion: frei lizenzierte Bilder (Wikimedia Commons) über Wikidata (P18).
# Eingabe sind nur gesalzene Prüfsummen (targets.json): von Wikidata-IDs (exakte Zuordnung) oder von Namen (nur eindeutige Treffer).
# Fotograf und Lizenz werden mitgespeichert; Bilder als kleine JPEGs (200 px).
import base64, concurrent.futures as cf, hashlib, json, re, sys, time, unicodedata, urllib.parse, urllib.request
UA = {"User-Agent": "Medienmanager2027-private-build/1.1 (non-commercial; photos with attribution)"}
T = json.load(open(".github/fotos/targets.json"))
SALT = T["salt"]
OCC = {
  "actor": ["Q33999", "Q10800557", "Q10798782", "Q2259451", "Q2405480"],
  "presenter": ["Q947873", "Q13590141", "Q270389", "Q1930187", "Q4220892"],
  "sport": ["Q2986228", "Q1930187", "Q937857", "Q628099"],
  "influencer": ["Q17125263", "Q2906862", "Q8246794", "Q57414145"],
  "music": ["Q177220", "Q639669", "Q2252262", "Q488205", "Q130857", "Q36834"],
  "producer": ["Q578109", "Q3282637"], "director": ["Q2526255", "Q2059704"], "writer": ["Q28389", "Q36180"],
  "comedy": ["Q245068", "Q18545066", "Q18814623"], "celeb": ["Q4610556", "Q177220", "Q33999", "Q947873"],
  "chef": ["Q3499072", "Q156839"], "expert": ["Q1930187", "Q39631", "Q901", "Q188094", "Q40348", "Q1622272"], "politician": ["Q82955"],
}
CTRY = {"DE": "Q183", "AT": "Q40", "CH": "Q39", "US": "Q30", "GB": "Q145", "CA": "Q16", "NZ": "Q664", "ES": "Q29", "FR": "Q142", "IE": "Q27", "KR": "Q884", "MX": "Q96", "CL": "Q298", "JP": "Q17", "IT": "Q38", "NL": "Q55"}
def norm(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s).strip().lower())
def h(x): return hashlib.sha256((SALT + x).encode()).hexdigest()[:24]
def get(url, tries=4, timeout=90):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r: return r.read()
        except Exception as e: print("Fehler", url[:110], e, file=sys.stderr); time.sleep(5 * (i + 1))
    return None
def sparql(q):
    b = get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q), tries=2)
    try: return json.loads(b)["results"]["bindings"] if b else None
    except Exception: return None
qwant = {t["h"] for t in T["items"] if t.get("k") == "q"}
nwant = {t["h"]: t for t in T["items"] if t.get("k") != "q"}
found = {}   # Hash -> (QID, Bilddatei)
cand = {}    # Namens-Hash -> {QID: [Sitelinks, Bild]}
def rows_for(base, extra=""):
    q = f"SELECT ?p ?img ?sl{extra and ' ?lde ?len ?alt'} WHERE {{ {base} {extra} }}"
    rows = sparql(q)
    if rows is not None: return rows
    out = []  # zu groß: nach Geburtsjahrzehnten
    for y in range(1880, 2020, 10):
        part = sparql(f"SELECT ?p ?img ?sl{extra and ' ?lde ?len ?alt'} WHERE {{ {base} ?p wdt:P569 ?b . FILTER(YEAR(?b) >= {y} && YEAR(?b) < {y + 10}) {extra} }}")
        out += part or []
    return out
# 1) Wikidata-IDs: alle Personen mit Foto und deutschem Wikipedia-Artikel in den Berufsgruppen, Abgleich über ID-Prüfsumme
if qwant:
    for g in ("actor", "presenter"):
        for occ in OCC[g]:
            base = f"?p wdt:P106 wd:{occ} ; wdt:P18 ?img . ?a schema:about ?p ; schema:isPartOf <https://de.wikipedia.org/> . ?p wikibase:sitelinks ?sl ."
            rows = rows_for(base)
            for r in rows:
                q = r["p"]["value"].rsplit("/", 1)[1]; x = h(q)
                if x in qwant and x not in found: found[x] = (q, r["img"]["value"])
            print("ID", g, occ, len(rows), "Treffer bisher", len(found), file=sys.stderr); time.sleep(1)
# 2) Namen (Personen ohne ID): nur eindeutige Treffer in Berufsgruppe und Land
need = {}
for t in nwant.values():
    for c in (t["c"] and [t["c"]] or ["DE", "AT", "CH"]): need.setdefault((t["g"], c), set()).add(t["h"])
lab = 'OPTIONAL { ?p rdfs:label ?lde FILTER(LANG(?lde) = "de") } OPTIONAL { ?p rdfs:label ?len FILTER(LANG(?len) = "en") } OPTIONAL { ?p skos:altLabel ?alt FILTER(LANG(?alt) = "de") }'
for (g, c), hs in sorted(need.items()):
    cq = CTRY.get(c)
    for occ in OCC.get(g, []):
        base = f'?p wdt:P106 wd:{occ} ; wdt:P18 ?img . {"?p wdt:P27 wd:" + cq + " ." if cq else ""} ?a schema:about ?p ; schema:isPartOf <https://de.wikipedia.org/> . ?p wikibase:sitelinks ?sl .'
        rows = rows_for(base, lab)
        for r in rows:
            q = r["p"]["value"].rsplit("/", 1)[1]; sl = int(r.get("sl", {}).get("value", 0))
            for k in ("lde", "len", "alt"):
                if k in r:
                    x = h(norm(r[k]["value"]))
                    if x in nwant: cand.setdefault(x, {}).setdefault(q, [sl, r["img"]["value"]])
        print("Name", g, c, occ, len(rows), file=sys.stderr); time.sleep(1)
for x, qs in cand.items():
    ranked = sorted(qs.items(), key=lambda kv: -kv[1][0])
    if len(ranked) == 1 or ranked[0][1][0] >= 2 * max(1, ranked[1][1][0]): found[x] = (ranked[0][0], ranked[0][1][1])
print("Treffer gesamt:", len(found), file=sys.stderr)
# 3) Lizenzangaben (Commons) und kleine Bilder laden
items = list(found.items()); meta = {}
for i in range(0, len(items), 45):
    chunk = items[i:i + 45]
    titles = {}
    for x, (q, img) in chunk: titles.setdefault(urllib.parse.unquote(img.rsplit("/", 1)[1]).replace("_", " "), []).append(x)
    b = get("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=extmetadata|url&iiurlwidth=200&titles=" + urllib.parse.quote("|".join("File:" + t for t in titles)))
    for pg in (json.loads(b)["query"]["pages"].values() if b else []):
        t = pg.get("title", "")[5:]
        if "imageinfo" not in pg or t not in titles: continue
        ii = pg["imageinfo"][0]; em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", ""); artist = re.sub(r"<[^>]+>", "", em.get("Artist", {}).get("value", "")).strip()[:120]
        if not lic or "fair use" in lic.lower(): continue
        for x in titles[t]: meta[x] = (ii.get("thumburl") or ii["url"], artist, lic, t)
    time.sleep(0.5)
def dl(x):
    u, by, lic, f = meta[x]; d = get(u, tries=3, timeout=60)
    return x, d, by, lic, f
out = {}
with cf.ThreadPoolExecutor(6) as ex:
    for x, d, by, lic, f in ex.map(dl, list(meta)):
        if d: out[x] = {"q": found[x][0], "img": "data:image/jpeg;base64," + base64.b64encode(d).decode(), "by": by, "lic": lic, "file": f}
json.dump(out, open("photos.json", "w"))
print("Fotos:", len(out), file=sys.stderr)
