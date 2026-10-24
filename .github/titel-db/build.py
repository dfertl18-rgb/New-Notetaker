# Baut eine kompakte Titeldatenbank (nur für die private Spielversion):
# Wikidata (CC0): Serien/Formate/Filme mit Erstausstrahlung bei deutschen Sendern und Streamern, Staffeln, Folgen
# IMDb-Datensätze (nur private, nicht-kommerzielle Nutzung): Bewertung, Stimmen, Laufzeit, Genres, deutscher Titel
# Ausgabe wird im Workflow mit einem öffentlichen Schlüssel verschlüsselt – im Repository liegt nie Klartext.
import csv, gzip, json, os, sys, time, urllib.parse, urllib.request
csv.field_size_limit(10**9)
UA = {"User-Agent": "Medienmanager2027-private-build/1.0 (non-commercial)"}
NETS = {"ard": ["Das Erste"], "zdf": ["ZDF"], "rtl": ["RTL"], "sat1": ["Sat.1"], "pro7": ["ProSieben"], "vox": ["VOX"], "kabel1": ["kabel eins", "Kabel eins"],
  "rtl2": ["RTL Zwei", "RTL II", "RTLZWEI"], "zdfneo": ["ZDFneo"], "nitro": ["Nitro", "RTL Nitro"], "arte": ["Arte", "ARTE"],
  "dritte": ["WDR Fernsehen", "NDR Fernsehen", "BR Fernsehen", "SWR Fernsehen", "MDR Fernsehen", "hr-fernsehen", "rbb Fernsehen", "Westdeutscher Rundfunk", "Norddeutscher Rundfunk", "Bayerischer Rundfunk", "Südwestrundfunk", "Mitteldeutscher Rundfunk", "Hessischer Rundfunk", "Rundfunk Berlin-Brandenburg"],
  "netflix": ["Netflix"], "prime": ["Amazon Prime Video", "Prime Video"], "disney": ["Disney+"], "rtlplus": ["RTL+", "TVNOW"], "wow": ["Sky Deutschland", "Sky Atlantic", "Sky One", "WOW"],
  "joyn": ["Joyn"], "paramount": ["Paramount+"], "dazn": ["DAZN"], "kika": ["KiKA"], "3sat": ["3sat"]}
def sparql(q):
  url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q)
  for i in range(4):
    try:
      with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r: return json.load(r)["results"]["bindings"]
    except Exception as e: print("SPARQL-Fehler", e, file=sys.stderr); time.sleep(20 * (i + 1))
  return []
v = lambda b, k: b[k]["value"] if k in b else None
titles = {}
for sid, labels in ({} if os.environ.get("SKIP_WD") else NETS).items():
  for lab in labels:
    for lang in ("de", "en"):
      q = f'''SELECT ?item ?itemLabel ?typeLabel ?imdb ?seasons ?eps ?start ?end ?genreLabel ?origLabel WHERE {{
        ?b rdfs:label "{lab}"@{lang} . ?item wdt:P449 ?b . ?item wdt:P31 ?type .
        OPTIONAL {{ ?item wdt:P345 ?imdb }} OPTIONAL {{ ?item wdt:P2437 ?seasons }} OPTIONAL {{ ?item wdt:P1113 ?eps }}
        OPTIONAL {{ ?item wdt:P580 ?start }} OPTIONAL {{ ?item wdt:P582 ?end }} OPTIONAL {{ ?item wdt:P136 ?genre }} OPTIONAL {{ ?item wdt:P495 ?orig }}
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de,en". }} }} LIMIT 20000'''
      rows = sparql(q); print(sid, lab, lang, len(rows), file=sys.stderr)
      for b in rows:
        qid = v(b, "item").rsplit("/", 1)[-1]; t = titles.setdefault(qid, {"q": qid, "n": v(b, "itemLabel"), "net": [], "ty": set(), "g": set(), "o": set()})
        if sid not in t["net"]: t["net"].append(sid)
        for k, f in (("ty", "typeLabel"), ("g", "genreLabel"), ("o", "origLabel")):
          if v(b, f): t[k].add(v(b, f))
        for k, f in (("imdb", "imdb"), ("s", "seasons"), ("e", "eps"), ("y0", "start"), ("y1", "end")):
          if v(b, f) and k not in t: t[k] = v(b, f)
      time.sleep(2)
for t in titles.values():
  for k in ("ty", "g", "o"): t[k] = sorted(t[k])[:4]
  for k in ("y0", "y1"):
    if t.get(k): t[k] = int(t[k][:4]) if t[k][:4].isdigit() else None
  for k in ("s", "e"):
    try: t[k] = int(float(t[k])) if t.get(k) else None
    except Exception: t[k] = None
print("Wikidata-Titel:", len(titles), file=sys.stderr)
# IMDb: Bewertungen + Basisdaten + deutsche Titel + Folgen
def tsv(name):
  with gzip.open(name, "rt", encoding="utf-8") as f:
    rd = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE); next(rd)
    for row in rd: yield row
rating = {r[0]: (float(r[1]), int(r[2])) for r in tsv("title.ratings.tsv.gz")}
want = {t["imdb"] for t in titles.values() if t.get("imdb")}
TYPES = {"movie": "film", "tvMovie": "tvfilm", "tvSeries": "serie", "tvMiniSeries": "mini", "tvSpecial": "special"}
basics = {}
for r in tsv("title.basics.tsv.gz"):
  tid, ty = r[0], r[1]
  if ty not in TYPES or r[4] == "1": continue
  rt = rating.get(tid)
  keep = tid in want or (rt and ((ty == "movie" and rt[1] >= 3000) or (ty in ("tvSeries", "tvMiniSeries") and rt[1] >= 1500) or (ty == "tvMovie" and rt[1] >= 1500)))
  if not keep: continue
  basics[tid] = {"i": tid, "k": TYPES[ty], "n": r[2], "y": int(r[5]) if r[5].isdigit() else None, "y1": int(r[6]) if r[6].isdigit() else None,
    "rt": int(r[7]) if r[7].isdigit() else None, "g": r[8].split(",") if r[8] != "\\N" else [], "r": rt[0] if rt else None, "v": rt[1] if rt else 0}
print("IMDb-Titel:", len(basics), file=sys.stderr)
for r in tsv("title.akas.tsv.gz"):
  if r[3] == "DE" and r[0] in basics and (r[5] in ("imdbDisplay", "\\N", "") ) and "de" not in basics[r[0]]: basics[r[0]]["de"] = r[2]
eps = {}
for r in tsv("title.episode.tsv.gz"):
  if r[1] in basics:
    e = eps.setdefault(r[1], [0, 0]); e[0] += 1
    if r[2].isdigit(): e[1] = max(e[1], int(r[2]))
for tid, (n, s) in eps.items(): basics[tid]["ep"] = n; basics[tid]["se"] = s
out = {"made": time.strftime("%Y-%m-%d"), "wd": list(titles.values()), "imdb": list(basics.values())}
json.dump(out, open("titeldb.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("fertig", len(out["wd"]), len(out["imdb"]), file=sys.stderr)
