# Quotenturm

Eine Fernsehsender-Wirtschaftssimulation für das iPad. Das Spielprinzip ist vom Klassiker *Mad TV* (Rainbow Arts, 1991) inspiriert, die Oberfläche von modernen Manager-Spielen: Kopfleiste mit „Weiter“, Navigationsleiste, Posteingang, datendichte Tabellen mit farbcodierten Werten. Alle Namen, Figuren, Titel und Grafiken sind eigene Erfindungen.

## Spielen

`index.html` in Safari öffnen (lokal oder über einen beliebigen Webserver, z. B. GitHub Pages). Auf dem iPad über „Teilen“ → „Zum Home-Bildschirm“ wie eine App starten. Keine Installation, keine Abhängigkeiten außer Google Fonts.

## Spielprinzip

- Sie leiten **KANAL 13** und konkurrieren mit **FLIMMER TV** und **SONNENKANAL** um 100 Imagepunkte.
- Zur vollen Stunde (16–23 Uhr) gibt der schwächste Sender einen Punkt an den Quotensieger ab.
- Alle drei Sender laufen in Echtzeit durch dasselbe Hochhaus. Aufzug und Räume fassen nur eine Person, wer zuerst kommt, blockiert die anderen.
- Räume: Filmkiste (Programme), Spotfabrik (Werbung = Einnahmen), Ticker24 (Nachrichten = Quotenbonus), eigenes Büro (Sendeplan), Archiv (Verkauf), Kantine (Sendepläne der Konkurrenz), Intendanz (Kredit), Goldene Antenne (Jury).
- Genres haben ideale Sendezeiten, FSK-18-Filme erst ab 21 Uhr, Wiederholungen verlieren an Aktualität.
- **Sieg:** 60 Imagepunkte oder die Goldene Antenne (Jury-Ansehen 100, max. doppeltes Image).
- **Niederlage:** Image unter 5, Schulden über 250.000 € oder ein Konkurrent gewinnt zuerst.

## Datenschutz

Das Spiel sammelt keine Daten. Der Spielstand liegt ausschließlich im `localStorage` des Geräts.
