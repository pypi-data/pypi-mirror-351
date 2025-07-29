##  GemeindeStart.ps1
##
##  Mit diesem Skript soll der Programmstart der GUI vereinfacht werden. Insb. kann die GUI
##  dann über einen Starter auch pre Mausklick gestartet werden.

##  Virtuelle Umgebung aktivieren
echo "Virtuelle Umgebung aktivieren"
.\venv\Scripts\Activate.ps1

##  GUI Gemeinde starten
python -m ug_gemeinde.Gemeinde
##  alternativ:
# python -m -ug_gemeinde.Gemeinde -u username -p password

##  Virtuelle Umgebung deaktivieren
echo "Virtuelle Umgebung deaktivieren"
deactivate
