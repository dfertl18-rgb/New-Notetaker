# Medienmanager 2027 für Windows

Das Spiel als eigenständiges Windows-Programm (Electron). Läuft komplett offline, die Schriften sind eingebettet.
Der Spielstand liegt im Benutzerprofil (`%APPDATA%\Quotenturm` – der Ordnername stammt aus dem früheren Spieltitel, damit alte Spielstände erhalten bleiben).

## Fertige Datei

- **Portable:** `Medienmanager-2027-1.0.0-portable.exe` – ohne Installation per Doppelklick starten.
- **Installer:** `Medienmanager-2027-1.0.0-Setup.exe` – mit Startmenü- und Desktop-Verknüpfung.

Beide entstehen automatisch bei jedem Push über GitHub Actions (Workflow „Medienmanager 2027 Windows-Build“, Artefakt „Medienmanager-2027-Windows“).

Die Dateien sind nicht digital signiert. Windows SmartScreen meldet deshalb beim ersten Start „Unbekannter Herausgeber“ → „Weitere Informationen“ → „Trotzdem ausführen“.

## Selbst bauen

```
cd quotenturm/desktop
npm install
npm start            # Spiel im Fenster starten
npm run dist         # Installer + portable EXE (unter Windows)
```

Bedienung: F11 = Vollbild, Strg+R = neu laden.
