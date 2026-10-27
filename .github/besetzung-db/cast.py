# Besetzungsdatenbank (nur für die private Spielversion): Wer moderiert bzw. spielt in welcher Sendung?
# Quelle: Wikidata (CC0) – Moderation (P371) und Besetzung (P161) mit Zeiträumen und Rollennamen,
# für Sendungen der im Spiel vorkommenden deutschen Sender und Streamer (Ausstrahlung P449).
# Schnell: Sender-IDs einmal auflösen, schlanke Abfragen ohne Beschriftungsdienst, Namen gesammelt über die API.
# Ausgabe wird im Workflow mit einem öffentlichen Schlüssel verschlüsselt – im Repository liegt nie Klartext.
import json, sys, time, urllib.parse, urllib.request, concurrent.futures as cf
UA = {"User-Agent": "Medienmanager2027-private-build/1.1 (non-commercial)"}
NETS = {"ard": ["Das Erste"], "zdf": ["ZDF"], "rtl": ["RTL"], "sat1": ["Sat.1"], "pro7": ["ProSieben"], "vox": ["VOX"], "kabel1": ["kabel eins", "Kabel eins"],
  "rtl2": ["RTL Zwei", "RTL II", "RTLZWEI"], "zdfneo": ["ZDFneo"], "nitro": ["Nitro", "RTL Nitro"], "arte": ["Arte", "ARTE"],
  "dritte": ["WDR Fernsehen", "NDR Fernsehen", "BR Fernsehen", "SWR Fernsehen", "MDR Fernsehen", "hr-fernsehen", "rbb Fernsehen"],
  "netflix": ["Netflix"], "prime": ["Amazon Prime Video", "Prime Video"], "disney": ["Disney+"], "rtlplus": ["RTL+", "TVNOW"], "wow": ["Sky Deutschland", "Sky Atlantic", "Sky One"],
  "joyn": ["Joyn"], "paramount": ["Paramount+"], "sport1": ["Sport1", "Deutsches Sportfernsehen"], "dreisat": ["3sat"], "kika": ["KiKA"], "sixx": ["Sixx"], "superrtl": ["Super RTL"],
  "dmax": ["DMAX"], "ntv": ["n-tv"], "welt": ["Welt", "N24"], "phoenix": ["Phoenix"], "one": ["One"], "tele5": ["Tele 5"], "sat1gold": ["Sat.1 Gold"], "pro7maxx": ["ProSieben Maxx"],
  "eurosport": ["Eurosport", "Eurosport 1"], "zdfinfo": ["ZDFinfo"], "comedy": ["Comedy Central"], "nick": ["Nickelodeon"], "tlc": ["TLC"], "voxup": ["VOXup"], "rtlup": ["RTLup", "RTLplus"]}
def get(url, timeout=120, tries=3):
  for i in range(tries):
    try:
      with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r: return json.load(r)
    except Exception as e: print("Fehler", url[:100], e, file=sys.stderr); time.sleep(8 * (i + 1))
  return None
def sparql(q, timeout=120):
  d = get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q), timeout)
  return d["results"]["bindings"] if d else None
v = lambda b, k: b[k]["value"] if k in b else None
qid = lambda u: u.rsplit("/", 1)[-1] if u else None
def year(s):
  try: return int(s[:4]) if s and s[:4].isdigit() else None
  except Exception: return None
# 1) Sender-IDs: das Objekt mit diesem Namen, dem die meisten Sendungen zugeordnet sind
netq = {}
for sid, labels in NETS.items():
  for lab in labels:
    rows = sparql(f'SELECT ?b (COUNT(?i) AS ?n) WHERE {{ ?b rdfs:label "{lab}"@de . ?i wdt:P449 ?b . }} GROUP BY ?b ORDER BY DESC(?n) LIMIT 1', 60) or []
    for b in rows: netq.setdefault(sid, set()).add(qid(v(b, "b")))
    time.sleep(1)
  print("Sender", sid, netq.get(sid), file=sys.stderr)
# 2) Moderation und Besetzung je Sender (ohne Beschriftungen)
out, need = {}, set()
for sid, qs in netq.items():
  for nq in qs:
    for prop, kind in (("P371", "host"), ("P161", "cast")):
      rows = sparql(f'''SELECT ?item ?p ?start ?end ?ch WHERE {{ ?item wdt:P449 wd:{nq} ; p:{prop} ?st . ?st ps:{prop} ?p . ?p wdt:P31 wd:Q5 .
        OPTIONAL {{ ?st pq:P580 ?start }} OPTIONAL {{ ?st pq:P582 ?end }} OPTIONAL {{ ?st pq:P453 ?ch }} }}''')
      if rows is None: print("Abfrage zu groß", sid, nq, kind, file=sys.stderr); continue
      for b in rows:
        iq, pq = qid(v(b, "item")), qid(v(b, "p"))
        t = out.setdefault(iq, {"q": iq, "net": [], "host": {}, "cast": {}})
        if sid not in t["net"]: t["net"].append(sid)
        d = t[kind].setdefault(pq, {"y0": None, "y1": None, "ch": None})
        y0, y1 = year(v(b, "start")), year(v(b, "end"))
        if y0 and (not d["y0"] or y0 < d["y0"]): d["y0"] = y0
        if y1 and (not d["y1"] or y1 > d["y1"]): d["y1"] = y1
        ch = qid(v(b, "ch")) if v(b, "ch") and v(b, "ch").startswith("http") else None
        if ch and not d["ch"]: d["ch"] = ch
        need.update([iq, pq] + ([ch] if ch else []))
      print(sid, nq, kind, len(rows), file=sys.stderr); time.sleep(1)
# Besetzung je Sendung begrenzen (Hauptrollen zuerst: die mit Rollennamen), Personen-IDs für Beschriftungen sammeln
for t in out.values():
  cs = sorted(t["cast"].items(), key=lambda kv: (kv[1]["ch"] is None,))[:40]; t["cast"] = dict(cs)
need = {x for t in out.values() for x in [t["q"]] + list(t["host"]) + list(t["cast"]) + [d["ch"] for d in t["cast"].values() if d["ch"]]}
# 3) Beschriftungen gesammelt (50 je Anfrage)
labels, alts = {}, {}
def fetch(ids):
  d = get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels|aliases&languages=de|en&ids=" + "|".join(ids), 60)
  return (d or {}).get("entities", {})
ids = sorted(need); chunks = [ids[i:i + 50] for i in range(0, len(ids), 50)]
with cf.ThreadPoolExecutor(4) as ex:
  for ents in ex.map(fetch, chunks):
    for k, e in ents.items():
      lb = e.get("labels", {}); labels[k] = (lb.get("de") or lb.get("en") or {}).get("value")
      alts[k] = [a["value"] for a in e.get("aliases", {}).get("de", [])][:6]
print("Beschriftungen:", len(labels), file=sys.stderr)
res = []
for t in out.values():
  n = labels.get(t["q"])
  if not n: continue
  hosts = [[labels.get(q), q, d["y0"], d["y1"]] for q, d in t["host"].items() if labels.get(q)]
  cast = [[labels.get(q), q, d["y0"], d["y1"], labels.get(d["ch"]) if d["ch"] else None] for q, d in t["cast"].items() if labels.get(q)]
  res.append({"q": t["q"], "n": n, "alt": alts.get(t["q"], []), "net": t["net"], "h": hosts, "c": cast})
print("Sendungen mit Besetzung:", len(res), "Moderationen:", sum(len(r["h"]) for r in res), "Besetzungen:", sum(len(r["c"]) for r in res), file=sys.stderr)
json.dump(res, open("besetzung.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
