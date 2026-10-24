; Liegt die KI-Modell-Datei (*.gguf) im selben Ordner wie der Installer, wird sie mitinstalliert.
; Alternativ in Teilen (*.gguf.part01, .part02 …): die Teile werden übernommen und beim ersten Start
; von der App zu einer Datei zusammengesetzt (danach werden die Teile gelöscht).
!macro customInstall
  CreateDirectory "$INSTDIR\resources\models"
  IfFileExists "$EXEDIR\*.gguf" 0 kiParts
    DetailPrint "Eingebaute KI: Modell wird übernommen (einige Minuten) …"
    CopyFiles /SILENT "$EXEDIR\*.gguf" "$INSTDIR\resources\models"
    Goto kiDone
  kiParts:
  IfFileExists "$EXEDIR\*.gguf.part*" 0 kiDone
    DetailPrint "Eingebaute KI: Modellteile werden übernommen (einige Minuten) …"
    CopyFiles /SILENT "$EXEDIR\*.gguf.part*" "$INSTDIR\resources\models"
  kiDone:
!macroend
