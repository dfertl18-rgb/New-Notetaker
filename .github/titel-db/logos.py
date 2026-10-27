# Holt Senderlogos über Wikidata (Eigenschaft P154 „Logo“) von Wikimedia Commons – nur für die private Spielversion.
import base64, json, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "Medienmanager2027-private-build/1.0 (non-commercial)"}
ITEMS = {"ard": ["Das Erste"], "dritte": ["WDR Fernsehen", "NDR Fernsehen", "BR Fernsehen"], "kabel1": ["Kabel eins"], "zdfneo": ["ZDFneo"], "nitro": ["Nitro", "RTL Nitro"],
  "arte": ["Arte"], "prime": ["Amazon Prime Video", "Prime Video"], "disney": ["Disney+"], "rtlplus": ["RTL+"], "wow": ["WOW"], "joyn": ["Joyn"], "mediathek": ["ARD Mediathek", "ZDFmediathek"],
  "rtl2": ["RTL Zwei"], "vox": ["VOX"], "sat1": ["Sat.1"], "pro7": ["ProSieben"], "rtl": ["RTL"], "zdf": ["ZDF"], "netflix": ["Netflix"], "paramount": ["Paramount+"], "dazn": ["DAZN"]}
# Neue Sender: eindeutig über den Titel des deutschen Wikipedia-Artikels
WIKI = {"ntv": ["N-tv", "Ntv"], "dmax": ["DMAX (Deutschland)", "DMAX (Fernsehsender)", "DMAX"], "rtlup": ["RTLup", "RTLplus (Fernsehsender)", "RTLplus"],
  "skysport": ["Sky Sport (Deutschland)", "Sky Sport", "Sky Sport Bundesliga"], "kabel1": ["Kabel Eins", "Kabel eins"],
  "zdfinfo": ["ZDFinfo"], "phoenix": ["Phoenix (Fernsehsender)"], "dreisat": ["3sat"], "one": ["One (Fernsehsender)", "ONE (Fernsehsender)"], "kika": ["KiKA", "Kika"],
  "comedy": ["Comedy Central (Deutschland)", "Comedy Central Deutschland"], "nick": ["Nickelodeon (Deutschland)", "Nick (Deutschland)"]}
def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: return r.read(), r.headers.get("Content-Type", "")
        except Exception as e: print("Fehler", url, e, file=sys.stderr); time.sleep(5 * (i + 1))
    return None, None
out = {}
def fetch(sid, res, lab):
    url = res.replace("http://", "https://")
    data, ct = get(url + ("&" if "?" in url else "?") + "width=256")
    if not data: data, ct = get(url)
    if not data: return False
    ct = "image/svg+xml" if url.lower().endswith(".svg") and "svg" in (ct or "svg") else (ct or "image/png").split(";")[0]
    out[sid] = f"data:{ct};base64," + base64.b64encode(data).decode()
    print(sid, lab, url, len(data), file=sys.stderr); return True
for sid, arts in WIKI.items():
  for art in arts:
    if sid in out: break
    q = f'SELECT ?logo WHERE {{ ?a schema:about ?i ; schema:isPartOf <https://de.wikipedia.org/> ; schema:name "{art}"@de . ?i wdt:P154 ?logo }} LIMIT 1'
    b, _ = get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q))
    rows = json.loads(b)["results"]["bindings"] if b else []
    if rows: fetch(sid, rows[0]["logo"]["value"], art)
    else: print("kein Logo", sid, art, file=sys.stderr)
    time.sleep(1)
for sid, labels in ITEMS.items():
    if sid in out: continue
    for lab in labels:
        q = f'SELECT ?logo WHERE {{ ?i rdfs:label "{lab}"@de . ?i wdt:P154 ?logo . ?i wdt:P17 wd:Q183 }} LIMIT 3'
        q2 = f'SELECT ?logo WHERE {{ ?i rdfs:label "{lab}"@de . ?i wdt:P154 ?logo }} LIMIT 3'
        res = None
        for qq in (q, q2):
            b, _ = get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(qq))
            if b:
                rows = json.loads(b)["results"]["bindings"]
                if rows: res = rows[0]["logo"]["value"]; break
        if not res: continue
        url = res.replace("http://", "https://")
        data, ct = get(url + ("&" if "?" in url else "?") + "width=256")
        if not data: data, ct = get(url)
        if not data: continue
        ct = "image/svg+xml" if url.lower().endswith(".svg") and "svg" in (ct or "svg") else (ct or "image/png").split(";")[0]
        out[sid] = f"data:{ct};base64," + base64.b64encode(data).decode()
        print(sid, lab, url, len(data), file=sys.stderr); break
    time.sleep(1)
# Rückfall: direkte Dateisuche auf Wikimedia Commons (Logo-Dateien), wenn Wikidata kein Logo kennt
COMMONS = {"ntv": ["n-tv logo", "ntv Nachrichten logo"], "rtlup": ["RTLup logo", "RTL up logo"], "kika": ["KiKA logo", "Kika logo 2024"], "nick": ["Nickelodeon Deutschland logo", "Nickelodeon logo 2009"]}
for sid, queries in COMMONS.items():
    if sid in out: continue
    for qy in queries:
        b, _ = get("https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srlimit=10&srsearch=" + urllib.parse.quote(qy + " filetype:drawing"))
        hits = [h["title"] for h in json.loads(b)["query"]["search"]] if b else []
        key = sid.replace("rtlup", "rtl").replace("nick", "nick")[:3].lower()
        hits = [h for h in hits if key in h.lower().replace("-", "").replace(" ", "")]
        print("Commons", sid, qy, hits[:5], file=sys.stderr)
        if hits and fetch(sid, "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(hits[0][5:]), "commons:" + hits[0]): break
        time.sleep(1)
json.dump(out, open("logos.json", "w"))
print("Logos:", len(out), sorted(out), file=sys.stderr)
