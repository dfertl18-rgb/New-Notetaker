# Besetzungsdatenbank (nur für die private Spielversion): Wer moderiert bzw. spielt in welcher Sendung?
# Quelle: Wikidata (CC0) – Moderation (P371) und Besetzung (P161) mit Zeiträumen und Rollennamen,
# für Sendungen der im Spiel vorkommenden deutschen Sender und Streamer.
# Ausgabe wird im Workflow mit einem öffentlichen Schlüssel verschlüsselt – im Repository liegt nie Klartext.
import json, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "Medienmanager2027-private-build/1.0 (non-commercial)"}
NETS = {"ard": ["Das Erste"], "zdf": ["ZDF"], "rtl": ["RTL"], "sat1": ["Sat.1"], "pro7": ["ProSieben"], "vox": ["VOX"], "kabel1": ["kabel eins", "Kabel eins"],
  "rtl2": ["RTL Zwei", "RTL II", "RTLZWEI"], "zdfneo": ["ZDFneo"], "nitro": ["Nitro", "RTL Nitro"], "arte": ["Arte", "ARTE"],
  "dritte": ["WDR Fernsehen", "NDR Fernsehen", "BR Fernsehen", "SWR Fernsehen", "MDR Fernsehen", "hr-fernsehen", "rbb Fernsehen", "Westdeutscher Rundfunk", "Norddeutscher Rundfunk", "Bayerischer Rundfunk", "Südwestrundfunk", "Mitteldeutscher Rundfunk", "Hessischer Rundfunk", "Rundfunk Berlin-Brandenburg"],
  "netflix": ["Netflix"], "prime": ["Amazon Prime Video", "Prime Video"], "disney": ["Disney+"], "rtlplus": ["RTL+", "TVNOW"], "wow": ["Sky Deutschland", "Sky Atlantic", "Sky One", "WOW"],
  "joyn": ["Joyn"], "paramount": ["Paramount+"], "sport1": ["Sport1", "SPORT1", "Deutsches Sportfernsehen"], "3sat": ["3sat"], "kika": ["KiKA"], "sixx": ["Sixx"], "superrtl": ["Super RTL"],
  "dmax": ["DMAX"], "ntv": ["n-tv"], "welt": ["Welt", "N24"], "phoenix": ["Phoenix"], "one": ["One"], "tele5": ["Tele 5"], "sat1gold": ["Sat.1 Gold"], "pro7maxx": ["ProSieben Maxx"], "eurosport": ["Eurosport", "Eurosport 1"]}
def sparql(q):
  url = "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q)
  for i in range(4):
    try:
      with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r: return json.load(r)["results"]["bindings"]
    except Exception as e: print("SPARQL-Fehler", e, file=sys.stderr); time.sleep(20 * (i + 1))
  return []
v = lambda b, k: b[k]["value"] if k in b else None
def year(s):
  try: return int(s[:4]) if s and s[:4].isdigit() else None
  except Exception: return None
out = {}
for sid, labels in NETS.items():
  for lab in labels:
    for lang in ("de", "en"):
      q = f'''SELECT ?item ?itemLabel ?alt ?p ?pLabel ?kind ?start ?end ?chLabel WHERE {{
        ?b rdfs:label "{lab}"@{lang} . ?item wdt:P449 ?b .
        {{ ?item p:P371 ?st . ?st ps:P371 ?p . BIND("host" AS ?kind) }} UNION {{ ?item p:P161 ?st . ?st ps:P161 ?p . BIND("cast" AS ?kind) }}
        ?p wdt:P31 wd:Q5 .
        OPTIONAL {{ ?st pq:P580 ?start }} OPTIONAL {{ ?st pq:P582 ?end }} OPTIONAL {{ ?st pq:P453 ?ch }}
        OPTIONAL {{ ?item skos:altLabel ?alt . FILTER(LANG(?alt) = "de") }}
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de,en". }} }} LIMIT 200000'''
      rows = sparql(q); print(sid, lab, lang, len(rows), file=sys.stderr)
      for b in rows:
        qid = v(b, "item").rsplit("/", 1)[-1]
        t = out.setdefault(qid, {"q": qid, "n": v(b, "itemLabel"), "alt": set(), "net": [], "host": {}, "cast": {}})
        if sid not in t["net"]: t["net"].append(sid)
        if v(b, "alt"): t["alt"].add(v(b, "alt"))
        pq = v(b, "p").rsplit("/", 1)[-1]; name = v(b, "pLabel")
        if not name or name == pq: continue
        d = t[v(b, "kind")].setdefault(pq, {"n": name, "y0": None, "y1": None, "ch": None})
        y0, y1 = year(v(b, "start")), year(v(b, "end"))
        if y0 and (not d["y0"] or y0 < d["y0"]): d["y0"] = y0
        if y1 and (not d["y1"] or y1 > d["y1"]): d["y1"] = y1
        if v(b, "chLabel") and not d["ch"]: d["ch"] = v(b, "chLabel")
      time.sleep(2)
res = []
for t in out.values():
  hosts = [[d["n"], q, d["y0"], d["y1"]] for q, d in t["host"].items()]
  cast = [[d["n"], q, d["y0"], d["y1"], d["ch"]] for q, d in t["cast"].items()][:40]
  res.append({"q": t["q"], "n": t["n"], "alt": sorted(t["alt"])[:6], "net": t["net"], "h": hosts, "c": cast})
print("Sendungen mit Besetzung:", len(res), "Moderationen:", sum(len(r["h"]) for r in res), "Besetzungen:", sum(len(r["c"]) for r in res), file=sys.stderr)
json.dump(res, open("besetzung.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
