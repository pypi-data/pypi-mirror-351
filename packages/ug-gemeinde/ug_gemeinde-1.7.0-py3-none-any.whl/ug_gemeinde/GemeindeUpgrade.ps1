##  GemeindeUpgrade.ps1
##
##  Diese Datei führt ein Upgrade erst der benötigten Bibliotheken und dann der GUI durch.
##  Mit diesem Skript soll das Upgrade der GUI vereinfacht werden. Insb. kann das Upgrade
##  der GUI dann über einen Starter auch pre Mausklick gestartet werden.

##  Virtuelle Umgebung aktivieren
echo "Virtuelle Umgebung aktivieren"
.\venv\Scripts\Activate.ps1

##  GUI Upgrade
##      pip übersieht durch Caching unter Umständen neue Versionen. Dem beugen wir vor
##      1.  durch pip cache purge
##      2.  durch --no-cache-dir
##  Braucht man wirklich beide Schritte?
pip cache purge
pip install --no-cache-dir -U ugbib_divers ugbib_modell ugbib_tkinter ugbib_werkzeug
pip install --no-cache-dir -U ug_gemeinde

##  Virtuelle Umgebung deaktivieren
deactivate
