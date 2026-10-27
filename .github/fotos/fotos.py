# Holt Fotos für die private Spielversion: frei lizenzierte Bilder (Wikimedia Commons) über Wikidata (P18).
# Eingabe sind nur gesalzene Prüfsummen der Namen (targets.json) – die Namensliste selbst liegt nicht im Repository.
# Zuordnung nur, wenn Name, Berufsgruppe (und ggf. Herkunftsland) eindeutig passen; Fotograf und Lizenz werden mitgespeichert.
import base64, hashlib, json, re, sys, time, unicodedata, urllib.parse, urllib.request
UA = {"User-Agent": "Medienmanager2027-private-build/1.0 (non-commercial; photos with attribution)"}
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
def h(name): return hashlib.sha256((SALT + norm(name)).encode()).hexdigest()[:24]
def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r: return r.read()
        except Exception as e: print("Fehler", url[:120], e, file=sys.stderr); time.sleep(6 * (i + 1))
    return None
def sparql(q):
    b = get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q))
    return json.loads(b)["results"]["bindings"] if b else None
need = {}  # (gruppe, land) -> set(hash)
for t in T["items"]:
    for c in (t["c"] and [t["c"]] or ["DE", "AT", "CH"]): need.setdefault((t["g"], c), set()).add(t["h"])
want = {t["h"]: t for t in T["items"]}
cand = {}  # hash -> {q: [sitelinks, img, gruppe-treffer]}
def collect(rows, g):
    for r in rows:
        q = r["p"]["value"].rsplit("/", 1)[1]; img = r["img"]["value"]; sl = int(r.get("sl", {}).get("value", 0))
        for k in ("lde", "len", "alt"):
            if k in r:
                x = h(r[k]["value"])
                if x in want: cand.setdefault(x, {}).setdefault(q, [sl, img])
for (g, c), hs in sorted(need.items()):
    cq = CTRY.get(c)
    for occ in OCC.get(g, []):
        base = f'?p wdt:P106 wd:{occ} ; wdt:P18 ?img . {"?p wdt:P27 wd:" + cq + " ." if cq else ""} ?a schema:about ?p ; schema:isPartOf <https://de.wikipedia.org/> . ?p wikibase:sitelinks ?sl .'
        lab = 'OPTIONAL { ?p rdfs:label ?lde FILTER(LANG(?lde) = "de") } OPTIONAL { ?p rdfs:label ?len FILTER(LANG(?len) = "en") } OPTIONAL { ?p skos:altLabel ?alt FILTER(LANG(?alt) = "de") }'
        rows = sparql(f"SELECT ?p ?img ?sl ?lde ?len ?alt WHERE {{ {base} {lab} }}")
        if rows is None:  # zu groß: nach Geburtsjahrzehnten aufteilen
            rows = []
            for y in range(1900, 2020, 10):
                part = sparql(f'SELECT ?p ?img ?sl ?lde ?len ?alt WHERE {{ {base} ?p wdt:P569 ?b . FILTER(YEAR(?b) >= {y} && YEAR(?b) < {y + 10}) {lab} }}')
                rows += part or []
        collect(rows, g); print(g, c, occ, len(rows), file=sys.stderr); time.sleep(1)
# Eindeutigkeit: genau ein Kandidat, oder einer mit deutlich mehr Sitelinks (mindestens doppelt so viele)
pick = {}
for x, qs in cand.items():
    ranked = sorted(qs.items(), key=lambda kv: -kv[1][0])
    if len(ranked) == 1 or ranked[0][1][0] >= 2 * max(1, ranked[1][1][0]): pick[x] = (ranked[0][0], ranked[0][1][1])
print("Treffer:", len(pick), "von", len(want), "– mehrdeutig:", len(cand) - len(pick), file=sys.stderr)
out = {}
items = list(pick.items())
for i in range(0, len(items), 40):
    chunk = items[i:i + 40]
    titles = {urllib.parse.unquote(img.rsplit("/", 1)[1]): x for x, (q, img) in chunk}
    meta = get("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=extmetadata|url&iiurlwidth=320&titles=" + urllib.parse.quote("|".join("File:" + t for t in titles)))
    pages = json.loads(meta)["query"]["pages"] if meta else {}
    for pg in pages.values():
        t = pg.get("title", "")[5:]; x = titles.get(t) or titles.get(t.replace(" ", "_"))
        if not x or "imageinfo" not in pg: continue
        ii = pg["imageinfo"][0]; em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", ""); artist = re.sub(r"<[^>]+>", "", em.get("Artist", {}).get("value", "")).strip()[:120]
        if not lic or "fair use" in lic.lower(): continue
        data = get(ii.get("thumburl") or ii["url"])
        if not data: continue
        out[x] = {"q": pick[x][0], "img": "data:image/jpeg;base64," + base64.b64encode(data).decode(), "by": artist, "lic": lic, "file": t}
        time.sleep(0.3)
json.dump(out, open("photos.json", "w"))
print("Fotos:", len(out), file=sys.stderr)
