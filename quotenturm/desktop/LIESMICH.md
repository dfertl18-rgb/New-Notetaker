# Medienmanager 2027 für Windows

Das Spiel als eigenständiges Windows-Programm (Electron). Läuft komplett offline, die Schriften sind eingebettet.
Der Spielstand liegt im Benutzerprofil (`%APPDATA%\Quotenturm` – der Ordnername stammt aus dem früheren Spieltitel, damit alte Spielstände erhalten bleiben).

## Fertige Datei

- **Portable:** `Medienmanager-2027-1.0.0-portable.exe` – ohne Installation per Doppelklick starten.
- **Installer:** `Medienmanager-2027-1.0.0-Setup.exe` – mit Startmenü- und Desktop-Verknüpfung.

Beide entstehen automatisch bei jedem Push über GitHub Actions (Workflow „Medienmanager 2027 Windows-Build“, Artefakt „Medienmanager-2027-Windows“).

### Private Version und Weitergabe-Version

- `npm run dist` bettet – falls lokal vorhanden – die private Datendatei `quotenturm/privat/realdata.js` ein (echte Personen, Politiker, Vitas). Diese Version ist nur für den eigenen Rechner gedacht.
- `npm run dist:share` baut die **Weitergabe-Version** (`…-Weitergabe-Setup.exe` / `…-Weitergabe-portable.exe`) ohne private Daten. Nur diese Version an andere weitergeben.

Programmsymbol und Versionsangaben setzt `afterpack.js` direkt in die EXE (Symbol: `build/icon.ico`).

Die Dateien sind nicht digital signiert. Windows SmartScreen meldet deshalb beim ersten Start „Unbekannter Herausgeber“ → „Weitere Informationen“ → „Trotzdem ausführen“.

## Selbst bauen

```
cd quotenturm/desktop
npm install
npm start            # Spiel im Fenster starten
npm run dist         # Installer + portable EXE (unter Windows)
```

Bedienung: F11 = Vollbild, Strg+R = neu laden.
