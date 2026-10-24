; Liegt die KI-Modell-Datei (*.gguf) im selben Ordner wie der Installer, wird sie mitinstalliert.
!macro customInstall
  IfFileExists "$EXEDIR\*.gguf" 0 kiDone
    CreateDirectory "$INSTDIR\resources\models"
    DetailPrint "Eingebaute KI: Modell wird übernommen (einige Minuten) …"
    CopyFiles /SILENT "$EXEDIR\*.gguf" "$INSTDIR\resources\models"
  kiDone:
!macroend
