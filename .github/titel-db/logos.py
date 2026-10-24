# Holt Senderlogos über Wikidata (Eigenschaft P154 „Logo“) von Wikimedia Commons – nur für die private Spielversion.
import base64, json, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "Medienmanager2027-private-build/1.0 (non-commercial)"}
ITEMS = {"ard": ["Das Erste"], "dritte": ["WDR Fernsehen", "NDR Fernsehen", "BR Fernsehen"], "kabel1": ["Kabel eins"], "zdfneo": ["ZDFneo"], "nitro": ["Nitro", "RTL Nitro"],
  "arte": ["Arte"], "prime": ["Amazon Prime Video", "Prime Video"], "disney": ["Disney+"], "rtlplus": ["RTL+"], "wow": ["WOW"], "joyn": ["Joyn"], "mediathek": ["ARD Mediathek", "ZDFmediathek"],
  "rtl2": ["RTL Zwei"], "vox": ["VOX"], "sat1": ["Sat.1"], "pro7": ["ProSieben"], "rtl": ["RTL"], "zdf": ["ZDF"], "netflix": ["Netflix"], "paramount": ["Paramount+"], "dazn": ["DAZN"]}
def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: return r.read(), r.headers.get("Content-Type", "")
        except Exception as e: print("Fehler", url, e, file=sys.stderr); time.sleep(5 * (i + 1))
    return None, None
out = {}
for sid, labels in ITEMS.items():
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
json.dump(out, open("logos.json", "w"))
print("Logos:", len(out), sorted(out), file=sys.stderr)
