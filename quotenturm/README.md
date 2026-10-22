# Quotenturm

Ein TV- und Streaming-Manager für das iPad. Spielprinzip inspiriert von *Mad TV* (Rainbow Arts, 1991), Oberfläche im Stil moderner Fußball-Manager.

## Spielen

`index.html` in Safari öffnen (lokal oder über einen Webserver). Auf dem iPad über „Teilen“ → „Zum Home-Bildschirm“ wie eine App starten. Keine Installation, keine Abhängigkeiten außer Google Fonts. Eigene Logos: siehe `logos/LIESMICH.md`.

## Was drin ist

- **12 deutsche Sender** zur Auswahl (ÖRR und privat) mit Saisonziel, Vertrauen der Senderleitung und Bilanz nach 28 Tagen.
- **Wochenplan 0–24 Uhr, Montag bis Sonntag**, mit Planungsassistent und Kopierfunktion.
- **Zwei-Phasen-Tag:** Planung (Zeit steht) → „Weiter“: 0–18 Uhr wird ausgewertet, der Abend läuft in der **Live-Regie** (Monitorwand, Quotenkurve, Zusatz-Werbeblock, Notfall-Wiederholung).
- **Programmhandel** mit echten Film- und Serientiteln, Eigenformaten der Sender (z. B. Tatort, Wer wird Millionär?), Lizenzlaufzeiten.
- **Sportrechte-Auktionen** (Free-TV-Pakete) mit verdeckten Geboten der Konkurrenz; Pay-/Streaming-exklusive Rechte als Marktübersicht.
- **Streaming als Ausbaupfad:** Start als reiner TV-Sender; Stufe 1 Mediathek, Stufe 2 Premium-Abo (nicht für ÖRR), Stufe 3 Live-Sport im Stream – mit Bauzeit, Serverkosten, Kapazität und Absturzrisiko bei Großevents. Katalog, Exklusivtitel (aus dem TV abgezogen), Verwertungsfenster, Kampagne „Erster Monat gratis“, Abos, Churn, ARPU, Break-even-Anzeige, Wettbewerb und Top 10.
- **Produktion:** Studio mit Format (Film, Serie, Show-Vorlage, Doku), Autoren, Budgetklasse und Besetzung; Rating R = Drehbuch × 0,4 + Star-Power × 0,4 + Chemie × 0,1 + Budget × 0,1; verdeckte Drehbuchqualität, Drehverzug durch unzuverlässige Stars, Live-Pannen, Kritiken (Feuilleton, Publikumspresse, Blogs). Promotion (Print, Social Media, Boulevard-Leak, Cross-Promotion) mit Hype-Wert für die Erstausstrahlung.
- **Casting:** 27 frei erfundene Stars, Moderator*innen, Nachrichtengesichter und Journalist*innen mit Talent, Buzz, Zuverlässigkeit, Gage; Exklusivverträge, Abwerben gegen Ablöse, Konkurrenz-Verträge.
- **Nachrichtenredaktion:** Blattlinie (spiegelbildlich, keine Richtung wird bevorzugt), Stil, Etat, Sprecher*in; Glaubwürdigkeit, Werbe-Attraktivität, Kritik und Rügen.
- **Internationaler Rechtemarkt:** Format-Lizenz mit Tantiemen oder Fertig-Export; wöchentliche Genre-Trends.
- **Streaming-Pakete:** Basis (SD, Werbung), Standard (HD), Premium (4K); Churn = 2 % + Content-Mangel + Preisschock (> 15 % Erhöhung: sofort 8–12 % Kündigungen im Paket).
- **Blind-Auktionen:** verdeckte Gebote, Umschläge werden nach der Entscheidung offengelegt.
- **Medien-Insider:** Ereignisse am Morgen mit Entscheidungen – Markttrends und Gerüchte, Skandale (mit verzögertem Risiko beim Vertuschen) und Vorschläge aus dem Team.
- **Finanzen nach Segmenten** (TV-Werbung, Teleshopping, Distribution, Rundfunkbeitrag, Abos, AVoD; Programm, Sportrechte, Personal, Technik/CDN, Strafen) mit EBITDA.
- **Regeln:** ÖRR-Werbeverbot ab 20 Uhr und sonntags; Jugendschutz (FSK 16 ab 22 Uhr, FSK 18 ab 23 Uhr) mit Bußgeld.

Alle Quoten, Preise, Abozahlen und Bewertungen sind simuliert. Sender-, Film- und Serientitel dienen als Kulisse einer privaten Spielversion.

## Roadmap (aus den Konzeptideen)

1. EPG mit Synopsen und Tags für jedes Programm, „Medien-Blitz“-Branchennewsletter am Morgen, Marktforschungs-Abo (Demografie, Verlaufskurven).
2. Pressekonferenzen, Klon-Krieg der Konkurrenz, Zielgruppen/Demografie.
5. Konzern-Ebene: Sender gründen/kaufen/fusionieren/schließen, KEK-Konzentrationskontrolle, Sublizenzen, Lizenzverkauf ins Ausland.
7. Externe Datenbasis (z. B. TMDb-Export) als JSON-Datei statt der eingebauten Titellisten.

## Datenschutz

Das Spiel sammelt keine Daten. Der Spielstand liegt ausschließlich im `localStorage` des Geräts.
