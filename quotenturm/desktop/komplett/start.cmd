@echo off
chcp 65001 >nul
title Medienmanager 2027 - Installation
echo.
echo  Medienmanager 2027 - Installation mit eingebauter KI
echo  ----------------------------------------------------
echo  Bitte das Passwort fuer die private Version eingeben (steht im Chat).
echo.
7zr.exe x setup.7z.001 -y
if errorlevel 1 (
  echo.
  echo  Das Passwort war falsch. Bitte die Datei erneut starten.
  pause
  exit /b 1
)
echo.
echo  Installation startet - die KI (4,7 GB) wird dabei mitkopiert, das dauert einige Minuten.
start /wait "" "Medienmanager-2027-1.4.0-Setup.exe"
