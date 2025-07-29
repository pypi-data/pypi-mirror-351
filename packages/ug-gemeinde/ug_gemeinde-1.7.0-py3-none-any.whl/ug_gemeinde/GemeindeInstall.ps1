##  GemeindeInstall.ps1
##  
##  Diese Datei wird dem User gegeben, damit er damit die Gemeinde-GUI auf einem Windows-Rechner
##  einfach installieren kann.
##
##  Als Anleitung werden ihm folgende Schritte nahegelegt:
##      1.  Ordner/Verzeichnis für die GUI anlegen.
##      2.  Das Skript GemeindeInstall.ps1 in dieses Verzeichnis speichern.
##      2a. U.U. muss eine Einstellung der PowerShell geändert werden. Aus Sicherheitsgründen
##          erlaubt die PowerShell das Ausführen von Skripten nicht. Dann muss man z.B.:
##              a) Die PowerShell als Administrator öffnen und folgenden Befehl ausführen:
##              b)    Set-ExecutionPolicy Bypass
##              c) Dann kann man die PowerShell wieder schließen und normal öffnen.
##              d) Im Übrigen verweisen wir hier auf die Dokumentation von Windows.
##      3.  Das Skript in diesem Verzeichnis ausführen, d.h.
##          entweder   a) Terminal öffnen
##                     b) Mit cd in das neue Verzeichnis wechseln
##                     d) Dort das Skript ausführen (GemeindeInstall.ps1)
##          oder       a) Das Skript im Dateimanager anklicken
##      4.  Prüfen, ob die Installation erfolgreich war: In dem Verzeichnis müssen 
##          mindestens folgende Dateien erschienen sein:
##               Gemeinde.yaml
##               Icons.yaml
##               GemeindeStart.ps1
##               GemeindeUpgrade.ps1
##      5.  Damit die GUI bzw. das Upgrade bequem gestartet werden kann, sollte in
##          einem Panel oder auf dem Schreibtisch je ein Starter für GemeindeStart.sh
##          und GemeindeUpgrade.sh eingerichtet werden. In beiden Startern sollte
##          "Im Terminal ausführen" aktiviert werden.
##      6.  Optional: Um den Programmstart bzw. das dann folgende Login zu erleichtern,
##          kann in dem Skript GemeindeStart.sh die Zeile
##               python -m ug_gemeinde.Gemeinde
##          ersetzt werden durch
##               python -m ug_gemeinde.Gemeinde -u username -p password
##          Diese beiden Werte werden dann nach dem Start der GUI automatisch in die
##          entsprechenden Felder übernommen; es braucht nur noch der Login-Button
##          gedrückt zu werden.
##          WARNUNG: Diese Ergänzung sollte nur erfolgen, wenn der Rechner gut
##                   geschützt ist vor Fremdbenutzung usw., weil Username und Passwort
##                   im Klartext gespeichert werden.

##  Virtuelle Umgebung herstellen
echo "Virtuelle Umgebung herstellen"
python3 -m venv venv

##  Virtuelle Umgebung aktivieren
echo "Virtuelle Umgebung aktivieren"
.\venv\Scripts\Activate.ps1

##  GUI Gemeinde installieren
echo "GUI Gemeinde installieren"
pip cache purge
pip install --no-cache-dir ug_gemeinde

##  GUI im Setup-Modus aufrufen.
##  Damit wird von der GUI ein Setup ausgefürhrt, dass folgendes erledigt und dann stoppt:
##      1. Gemeinde.yaml und Icons.yaml ins aktuelle Verzeichnis kopiert
##      2. Upgrade-Skript GemeindeUpgrade.sh ins aktuelle Verzeichnis kopiert
##      3. Start-Skript GemeindeStart.sh ins aktuelle Verzeichnis kopiert
##      4. Die beiden neuen Skripte ausführbar machen
echo "GUI im Setup-Modus aufrufen"
python -m ug_gemeinde.Gemeinde --setup

##  Virtuelle Umgebung deaktivieren
deactivate
