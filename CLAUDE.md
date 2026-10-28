# Medienmanager 2027 – Hinweise für die Weiterentwicklung

Privates TV-Manager-Spiel (Stil Fußball-Manager), komplett auf Deutsch. Entwickler: Daniel Fertl. Kommunikation auf Deutsch.
Hauptziel ist die **private Windows-Version** (Electron) mit echten Logos, Namen und Fotos. Steam ist vorerst kein Thema.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `quotenturm/src/quotenturm.html` | **Spielquelle** (eine Datei: CSS + gesamtes Spielskript). Hier wird entwickelt. |
| `quotenturm/src/hf/` | three.js + HumanForge (MIT, Assets CC0) als Bundle `hf.iife.js` → `window.THREE`, `window.HF` |
| `quotenturm/human/` | MakeHuman-Modelle (CC0) für 3D-Avatare, Wohnzimmer, Zwischensequenzen |
| `quotenturm/tools/build.js` | Baut `quotenturm/index.html` (öffentlich) und mit `--privat` `quotenturm/privat/index.html` |
| `quotenturm/index.html` | Gebaute öffentliche Version (nie direkt bearbeiten) |
| `quotenturm/privat/` | **Private Daten, per .gitignore ausgeschlossen** (siehe unten) |
| `quotenturm/desktop/` | Electron-App: `prepare.js` bettet private Daten ein, `main.js`/`preload.js` (Spielstände als Dateien) |
| `.github/` | Workflows für Datenabruf (Wikidata/Commons), Ergebnisse nur verschlüsselt |

## Bauen

```
cd quotenturm
node tools/build.js --privat          # index.html + privat/index.html, inkl. Syntaxprüfung
cd desktop
npm install                           # einmalig
npm start                             # App lokal starten
npx electron-builder --win nsis --publish never   # → dist/Medienmanager-2027-<version>-Setup.exe
```
Version in `quotenturm/desktop/package.json` bei jeder Auslieferung erhöhen (aktuell 1.5.1).
`prepare.js` bettet die privaten Dateien in EINEM Skriptblock in fester Reihenfolge ein: realdata, titles, extra, besetzung, photos, logos (realdata legt `window.MM_PRIVATE` an).
HumanForge-Bundle neu bauen (nur bei Änderungen an `src/hf/`): `cd quotenturm/src/hf && npm install && npm run build`.
Das KI-Modell (~4,7 GB) wird nicht mitgeliefert, sondern im Spiel unter Einstellungen geladen (EXE > 4 GB läuft unter Windows nicht).

## Private Daten (`quotenturm/privat/`, nie committen)

`realdata.js` (Personen mit Vita/QID), `extra.js` (Stammliste/Masterdaten, Politik), `titles.js`, `besetzung.js` (Wikidata-Besetzung → `MM_PRIVATE.castList`),
`logos.js` (echte Senderlogos), `photos/` + `photos.js` (Wikimedia-Commons-Fotos mit Urheber und Lizenz), `keys/` (RSA-Schlüssel für Workflow-Ergebnisse).
Diese Dateien werden separat (nicht über GitHub) übergeben. Das Repository ist öffentlich.

## Feste Regeln (Datenschutz, verantwortungsvolle KI, AGG)

- Datenschutzprobleme ansprechen, **bevor** etwas damit gemacht wird.
- Kein Geschlecht in der Spielmechanik. Der Avatar-Regler „Gesichtszüge“ (weich ↔ markant) ist rein optisch, keine Geschlechtsauswahl.
- Echte Personen und Politiker nur in privaten Dateien; nie unverschlüsselt veröffentlichen.
- Keine erfundenen Skandale oder Zitate über echte Personen; echte Personen erhalten neutrale Werte.
- Falschmeldungen/Gerüchte nur vom fiktiven „Branchendienst Medienplatz“.
- IMDb-Daten nur für den privaten Gebrauch.
- Echte Personen nur bei belegter Mitwirkung an Sendungen binden (Wikidata P371/P161); als Moderation nur aktuelle (kein Endjahr oder Ende ≥ 2025).
- Eingaben an öffentliche Workflows nur als gesalzene Hashes (Namen/QIDs); Ergebnisse RSA/AES-verschlüsselt.
- KI-ausformulierte Nachrichten (`msgLong`/`aiLongClean`): nur Zahlen aus der Quelle, keine Zitate, keine Namen, die nicht in der Quelle stehen.

## Konventionen

- Code-Stil der Spielquelle beibehalten (kompakt, deutsche UI-Texte, deutsche Kommentare).
- Nach Änderungen immer `node tools/build.js --privat` (Syntaxprüfung) ausführen.
- Installer werden dem Nutzer direkt übergeben, nicht über GitHub-Releases.
