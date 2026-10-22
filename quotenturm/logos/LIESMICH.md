# Eigene Logos

Legen Sie hier Logo-Dateien ab (SVG oder PNG). Das Spiel zeigt sie automatisch statt der Wappen an.

Dateinamen (Kleinbuchstaben):

- Sender: `zdf`, `ard`, `dritte`, `rtl`, `sat1`, `vox`, `pro7`, `kabel1`, `zdfneo`, `rtl2`, `nitro`, `arte`
- Streamer: `netflix`, `prime`, `disney`, `rtlplus`, `wow`, `dazn`, `joyn`, `paramount`, `mediathek`

Beispiel: `logos/rtl.svg` oder `logos/netflix.png`. Alternativ funktioniert auch der Ordner `assets/logos/` und gängige Dateinamen wie `prosieben.png`, `daserste.png`, `kabeleins.png`, `rtlzwei.png`. Transparente PNG oder SVG sehen am besten aus.

Hinweis: Senderlogos sind geschützte Marken. Für eine private Spielversion auf dem eigenen Gerät ist das unproblematisch; bei einer Veröffentlichung sollten die Logos wieder entfernt werden.

## Automatisch holen (auf dem eigenen Rechner)

```
cd quotenturm/tools
python3 logos_holen.py                              # Sender- und Streamerlogos (Wikimedia)
TMDB_API_KEY=dein_schluessel python3 logos_holen.py --titel   # Logos/Poster der Filme, Serien, Shows (TMDb)
```

Die Dateien landen in `logos/` und `logos/titel/` und sind per `.gitignore` vom Repository ausgeschlossen – sie bleiben privat auf Ihrem Gerät. Danach `quotenturm/index.html` lokal im Browser öffnen. In der veröffentlichten Online-Version (claude.ai) sind lokale Dateien nicht sichtbar.
