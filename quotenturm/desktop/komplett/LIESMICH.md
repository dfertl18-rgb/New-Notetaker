# Komplett-Installer (privat)

`setup.7z.001/.002` enthalten den privaten Installer – **AES-256-verschlüsselt** (Passwort nur beim Besitzer).
Der Workflow `komplett-installer.yml` packt ihn zusammen mit dem KI-Modell (Qwen2.5-7B-Instruct, Apache-2.0)
in eine einzige selbstentpackende EXE. Beim Start fragt sie einmal nach dem Passwort.
