import psycopg2, psycopg2.extras

from __main__ import glb
import logging
logger = logging.getLogger()

import os, os.path, shutil
import sys

import yaml
from argparse import ArgumentParser

import psycopg2

import smtplib, ssl
from email.message import EmailMessage

def setup():
    
    def find(name):
        for root, dirs, files in os.walk('./'):
            if name in files:
                return os.path.abspath(os.path.join(root, name))
    
    dateien = (
        find('Gemeinde.yaml'),
        find('Icons.yaml'),
        find('GemeindeStart.sh'),
        find('GemeindeUpgrade.sh'),
        find('GemeindeStart.ps1'),
        find('GemeindeUpgrade.ps1'),
        )
    for f in dateien:
        print(f'copy {f} ins aktuelle Verzeichnis.')
        shutil.copy(f, os.path.abspath('./'))

def aktive_gemeinden():
    """Liefert eine Liste der aktiven Gemeinden zurück
    
      Liest aus der Tabelle public.tbl_gemeinde die aktiven Gemeinden und liefert sie
      als Liste von Dictionaries zurück. Das Dictionary entspricht jeweils einem
      von der Cursor-Factory psycopg2.extras.DictCursor Objekt, vgl. dazu
      http://initd.org/psycopg/docs/extras.html
      
      Das Dictionary kann (u.a.!) über die keys aus der Tabelle (bzw. den ggf. 
      angegebenen Aliases) angesprochen werden.
          kurz_bez    -- Kurzbezeichnung der Gemeinde
          schema      -- PostgreSQL-Schema, in dem die Tabellen der Gemeinde
                      -- gehalten werden
          rel_verz    -- Relatives Verzeichnis zum Veröffentlichen der Auswertungen
                      -- Vgl. dazu die Dokumentation in Tabellen.pg_sql
          mail_from   -- From-Header für automatisch zu verschickende Mails
          mail_reply  -- Reply-To-Header für automatisch zu verschickende Mails
    """
    sql_gemeinde = """
        select *
        from public.tbl_gemeinde
        where aktiv
        order by kurz_bez
    """
    with psycopg2.connect(
                  host        = glb.PSQL_HOST,
                  port        = glb.PSQL_PORT,
                  database    = glb.PSQL_DATABASE,
                  user        = glb.PSQL_USER,
                  password    = glb.PSQL_PASSWORD) as DB:
        with DB.cursor(cursor_factory=psycopg2.extras.DictCursor) as curGemeinde:
            try:
                curGemeinde.execute(sql_gemeinde)
                gemeinden = curGemeinde.fetchall()
            except Exception as e:
                logging.error('Gemeinden lassen sich nicht auslesen: {}'.format(e))
                gemeinden = [{},]
    return gemeinden

def configuration():
    """configuration - Setzt alle (globalen) Einstellungen/Konstanten
    
        configuration setzt globale Konstanten auf Werte, die sich ergeben aus:
        
            Default
                Gesetzt in der lokalen Variable confDefault in YAML-Syntax
                
            Konfi-File
                Konfigurations-Datei in YAML-Syntax
                
            Kommandozeilenparameter
                Klar
        
        Default-Werte werden überschrieben von Einträgen im Konfi-File. Anschließend
        werden die Werte ggf. überschrieben durch Kommandozeilenparameter.
        
        Nicht alle Default-Werte dürfen durch Einträge in Konfi-File überschrieben werden.
        Insb. CONFI_FILE_NAME gehört zu diesen Ausnahmen - es würde auch keinen Sinn ergeben.
        
        Die Werte/Einstellungen werden global, in diesem Fall als Attribut von glb,
        gespeichert. glb kann in Modulen importiert werden, entweder von __main__ (d.h.
        von "hier"), oder von ugbib_diver.bibGlobal.
        
        Außerdem werden dieverse globale Variablen initialisiert:
            glb.DB
    """
    
    ## confDefault hält die Default-Werte der Konstanzen
    #
    confDefault = """
        # Name der Anwendung
        #     Wird insb. zur Ausgabe der Version des Programms verwendet
        
        NAME: 'Gemeinde'
        
        # Name des Konfi-Files
        
        CONFI_FILE_NAME: 'Gemeinde.yaml'
        
        # Version des Programms
        
        VERSION: 'x.x'
        
        ##  ICON_THEME - Icon Theme
        #       'oxygen' oder 'breeze'
        ICON_THEME: 'oxygen'
        
        ##  ICON_NAVI_SIZE - Icon größe für Navis
        #       14 ist eine sinnvolle Größe, sonst auch kleiner
        ICON_NAVI_SIZE: 14

        # TkInter Theme
        #     Muss auf 'classic' gesetzt sein, damit PanedWindow richtig angezeigt wird.
        
        TKINTER_THEME: 'classic'
        
        ##  LIMIT_FORMLIST
        #       Limit für die angezeigten Zeilen in Listenansichten
        #       Listenansichten sind zeitintensiv, da für jede Zeile und jede
        #       Kolumne je ein Widget hergestellt und plaziert werden muss.
        #       Daher kann über diese Konstante die Zahl der angezeigten Zeilen
        #       limitiert werden.
        #       Der Wert wird später als Default für de Getter verwendet, der
        #       von bibModell.Modell.FactoryGetterDicts erzeugt wird.
        LIMIT_FORMLIST: 20
        
        ## LIMIT_CHOICES
        #       Limit für die angezeigten Zeilen in Select, ComboboxValueLabel
        #       u.ä. Widgets.
        #       Integer oder 'ALL'
        #       Der Aufbau dieser Widgets kann bei sehr vielen Zeilen in der
        #       Tabell lange dauern, daher hier die Möglichkeit der
        #       limitierung.
        #       Der Wert wird später als Default für de Getter verwendet, der
        #       von bibModell.Modell.FactoryGetterChoices erzeugt wird.
        #       Der hier verwendete Default von 500 ist aus der Luft gegriffen
        #       und kann später angepasst werden.
        LIMIT_CHOICES: 500
        
        ## LIMIT_NAVIAUSWAHL
        #       Limit für die angezeigten Zeilen in Select, ComboboxValueLabel
        #       u.ä. Widgets.
        #       Integer oder 'ALL'
        #       Der Aufbau dieser Widgets kann bei sehr vielen Zeilen in der
        #       Tabell lange dauern, daher hier die Möglichkeit der
        #       limitierung.
        #       Der Wert wird später als Default für de Getter verwendet, der
        #       von bibModell.Modell.FactoryGetterChoices erzeugt wird.
        #       Der hier verwendete Default von 500 ist aus der Luft gegriffen
        #       und kann später angepasst werden.
        LIMIT_NAVIAUSWAHL: 500
        
        # Logging Level
        #     Bezieht sich auf Python logging
        
        LOGGING_LEVEL: 'WARNING'
        
        # PostgreSQL Server
        #     Wird im Programm nicht gebraucht, aber von Modulen importiert,
        #     in diesem Fall z.B. von bibModell
        
        PSQL_HOST: '138.199.218.230'
        PSQL_PORT: '22555'
        PSQL_DATABASE: 'cg'
        PSQL_USER: ''
        PSQL_PASSWORD: ''
        
        # Format Strings für Datum, Zeit, DatumZeit
        #     Wird imProgramm nicht gebraucht, aber von Modulen importiert,
        #     in diesem Fall z.B. von bibForm
        
        FORMATS_TIME: ['%H:%M',]
        FORMATS_DATE: ['%d.%m.%Y', '%Y-%m-%d']
        FORMATS_DATETIME: ['%Y-%m-%d %H:%M',]
        
        ## SQL_INJECTION_MAXLENGTH
        ## SQL_INJECTION_BLACKLIST
        #       Werte aus Filter-Feldern der Navis werden in SELECT Abfragen auf der
        #       PostgreSQL-Datenbank verwendet. Aus Historischen und technischen Gründen
        #       war es nicht ohne weiteres möglich, dass über parametrisierte
        #       cursor.execute(...) zu programmieren. Daher schützen wir uns hier
        #       anders (und wohl letztlich nicht vollständig) vor SQL Injection Angriffen:
        #       1. Wir erlauben Filter-Werte nur bis zu einer Länge von maximal
        #             SQL_INJECTION_MAXLENGTH
        #       2. Wir eliminieren alle Zeichen aus
        #             SQL_INJECTION_BLACKLIST
        #          aus dem Filter-Wert
        #       Die Kombination aus beidem gibt einen nicht schlechten Schutz.
        #       Insb. wird der eingegebene Filter-Wert zuerst auf die maximale Länge
        #       reduziert. D.h. um so mehr kritische Zeichen aus der Blacklist
        #       vorkommen, um so mehr tatsächlich relevante Zeichen gehen verloren
        #       Vgl. bibModell.buildFilterSQL
        SQL_INJECTION_MAXLENGTH: 7
        SQL_INJECTION_BLACKLIST: ["'", '"', ';', '=', '(', ')', '[', ']', '{', '}', '\\', '-', '*', '/']

        ## TOOLTIP_DELAY
        #       Verzögerung in Millisekunden für die Anzeige eines Tooltips, nachdem
        #       die Maus über ein Widget kommt. Damit wird verhindert, dass bei schnellen
        #       Mausbewegungen über eine Reihe von Widgets ständig Tooltips aufblitzen.
        #       Sinnvoller Wert: 250
        TOOLTIP_DELAY: 250
    """
    #
    # Werte confDefault aus
    yamlConf = yaml.safe_load(confDefault)
    for key in yamlConf:
        glb.setup(key, value=yamlConf[key])
    #
    # Baue Kommandozeilenparameter
    parser = ArgumentParser()
    parser.add_argument('--version',
        action='version',
        version=f'{glb.NAME} {glb.VERSION}')
    parser.add_argument('--setup',
        dest='setup',
        action='store_true',
        help='Holt Gemeinde.yaml und Icons.yaml ins Arbeitsverzeichnis und beendet das Programm.')
    parser.add_argument('-c', '--config',
        dest='confifilename',
        help='Name des Konfi-Files')
    parser.add_argument('-l', '--logging',
        dest='logginglevel',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
        help='Logging Level')
    parser.add_argument('-u', '--user',
        dest='psql_user',
        default='',
        help='Username für die PostgreSQL Datenbank')
    parser.add_argument('-p', '--password',
        dest='psql_password',
        default='',
        help='Password für die PostgreSQL Datenbank')
    parser.add_argument('--host',
        dest='psql_host',
        default='',
        help='Host der Verbindung zum PostgreSQL Server')
    parser.add_argument('--port',
        dest='psql_port',
        default='',
        help='Port der Verbindung zum PostgreSQL Server')
    parser.add_argument('--database',
        dest='psql_database',
        default='',
        help='PostgreSQL Database Name')
    #
    # Lese Kommandozeilenparameter aus
    args = parser.parse_args()
    #
    # Setup durchführen, falls --setup angegeben
    if args.setup:
        setup()
        sys.exit()
    #
    # Setze ggf. Name des Konfi-Files nach Kommandozeilenparameter neu
    if args.confifilename:
        glb.setvalue(CONFI_FILE_NAME, args.confifilename)
    #
    # lese confFileName aus
    with open(glb.CONFI_FILE_NAME, 'r') as confFile:
        yamlConf = yaml.safe_load(confFile)
    #
    # Stelle Konstanten her, vorhandene Werte werden ggf. überschrieben
    for key in yamlConf:
        if key == 'CONFI_FILE_NAME':
            raise RuntimeError(f'{key} darf im Konfi File nicht gesetzt werden.')
        glb.setup(key, yamlConf[key], force=True)
    #
    # Suche nach Override.yaml, überschreibe daraus ggf. Werte
    # Suche Override.yaml zuerst im Entwicklungspfad, dann im Installationspfad
    overridePaths = [
        # zuerst in Entwicklungsumgebung
        os.path.join(os.path.dirname(__file__), 'Override.yaml'),
        # dann im Installationsumgebung
        os.path.join(os.path.dirname(sys.modules['ug_gemeinde'].__file__), 'Override.yaml')
        ]
    
    overrideFile = next((path for path in overridePaths if os.path.exists(path)), None)
    
    if overrideFile:
        with open(overrideFile, 'r') as f:
            yamlConfOverride = yaml.safe_load(f)
            for key in yamlConfOverride:
                glb.setup(key, yamlConfOverride[key], force=True)    
    
    #
    # Kommandozeilenparameter bearbeiten
    if args.logginglevel:
        glb.setvalue('LOGGING_LEVEL', args.logginglevel)
        logger.setLevel(glb.LOGGING_LEVEL)
    else:
        logging.debug(f'Setze Logging Level auf {glb.LOGGING_LEVEL}')
    logger.setLevel(glb.LOGGING_LEVEL)
    if args.psql_user:
        glb.setvalue('PSQL_USER', args.psql_user)
    if args.psql_password:
        glb.setvalue('PSQL_PASSWORD', args.psql_password)
    if args.psql_host:
        glb.setvalue('PSQL_HOST', args.psql_host)
    if args.psql_port:
        glg.setvalue('PSQL_PORT', args.psql_port)
    #
    # Globale Variablen initialisieren
    glb.setup('DB')
    glb.setup('schema')
    glb.setup('gemeinde')
    glb.setup('gemeinden', value=[])
    glb.setup('aktuelleGemeinde')

def checkLogin():
    """checkLogin - check loginDaten gegen PostgreSQL-DB u.a.
    
        checkLogin checkt die (globalen!) loginDaten
        (glb.PSQL_USER, glb.PSQL_PASSWORD) gegen die
        PostgreSQL-DB. Das dadurch, dass versucht wird, ein DB-Konnektor
        herzustellen. Im Falle des Erfolges wird dieser Konnektor global
        als glb.DB bereitgestellt und True zurück gegeben. Andernfalls
        bleibt glb.DB undefiniert und es wird False zurück gegeben.
        
        Anschließend werden die aktiven Gemeinden durchsucht nach solchen,
        auf die der User ausreichend Rechte hat. Diese Gemeinden werden
        in glb.gemeinden bereitgestellt.
        
        Ergebnis
            True    Erfolgreich DB-Konnektor aufgebaut, d.h. loginDaten
                    sind gültig, und Gemeinden gesucht
            False   Sonst
        
        Nebeneffekte
            glb.DB          Gültiger DB-Konnektor des Users
            glb.gemeinden   Liste der Gemeinden, auf denen der User arbeiten
                            kann und darf.
    """
    #
    # DB-Konnektor herstellen
    try:
        glb.setvalue(
            'DB',
            psycopg2.connect(
                host=glb.PSQL_HOST,
                port=glb.PSQL_PORT,
                dbname=glb.PSQL_DATABASE,
                user=glb.PSQL_USER,
                password=glb.PSQL_PASSWORD)
            )
        logging.info(f'Login erfolgreich als {glb.PSQL_USER}')
    except:
        logging.info(f'Login fehlgeschlagen als {glb.PSQL_USER}')
        return False
    #
    # Aktive Gemeinden suchen und filtern nach Rechten, die der Benutzer darauf hat
    # Das Ergebnis speichern wir in glb.Gemeinden
    glb.setvalue('gemeinden', [])
    for G in aktive_gemeinden():
        schema = G['schema']
        sql = f"select has_schema_privilege ('{schema}', 'USAGE')"
        hasUsage = False
        with glb.DB.cursor() as Cur:
            Cur.execute(sql)
            hasUsage = Cur.fetchone()[0]
            glb.DB.commit()
        if hasUsage:
            glb.gemeinden.append(G)
    #
    # Wenn bis hier keine Fehler aufgetreten sind, geben wir die Erolgsmeldung zurück
    return True

def MailOderBrief(Brief, Absender):
    """Schreibt (verschickt) eMail oder Breif, falls keine eMail-Adresse vorhanden
    
      Falls eine eMail-Adresse vorhanden ist (d.h. Brief["Email"] ist nicht None und
      nicht ''), wird an diese eMail-Adresse eine Mail mit dem entsprechenden Inhalt
      geschickt.
      
      Andernfalls wird ein entpsrechendes PDF erzeugt und zum Ausdrucken an Druck_Mail
      geschickt. Falls es einen Anhang gibt, wird der ebenfalls an diese Mail angehängt.
      Es bleibt in der Verantwortung der Benutzer, diese Mail zu bearbeiten, d.h.
      den Brief und ggf. den Anhang auszudrucken und mit der Post zu verschicken.
      
      Parameter
          Brief         siehe weiter unten
          Mail_From,
          Mail_Reply    Für die Mail-Header
          Absender      Dict mit (mindestens) folgenden Feldern:
                            strasse
                            plz
                            ort
                            land
                            land_kurz
                            email
                            mail_from
                            mail_reply
                            smtp_server
                            smtp_port
                            smtp_user
                            smtp_password
                        Achtung: wenn smtp_server gesetzt ist, dann muss auch smtp_port
                        gesetzt sein.
                      
                        Daraus wird im Fall des Briefes der Absender erstellt.
                        Im Fall der eMail wird daraus die Verbindung zum SMTP-Server
                        gebaut und die Header entsprechend gesetzt.
      
      Brief muss ein Dictionary nach folgendem Muster sein:
          Brief = {
              "P_ID"        : "",
              "Name"        : "",
              "Vorname"     : "",
              "Email"       : "",
              "Bcc"         : "",
              "Strasse"     : "",
              "PLZ"         : "",
              "Ort"         : "",
              "Land"        : "",
              "Betreff"     : "",
              "Anrede"      : "",
              "Text"        : "",
              "Anhang"      : ""
          }
      Jeder der Values wird, falls er None ist, durch "" ersetzt.
      ACHTUNG: das hat den entsprechenden Nebeneffekt auf den übergebenen Brief!
      
      Wenn Brief['Anhang'] ein nicht leerer String ist, wird er als Dateiname
      interpretiert.
      Brief['Anhang'] kann auch eine Liste von Strings sein. Dann wird jeder der
      Strings als Dateiname interpretiert.
      
      Ergebnis = True, falls die eMail erfolgreich verschickt werden konnte
      bzw. das PDF erfolgreich erzeugt und verschickt werden konnte. Sonst False. 
    """
    #
    # Alle None-Values durch '' ersetzen
    for k in Brief.keys():
        if Brief[k] is None:
            Brief[k] = ''
    #
    # Falls eMail-Adresse vorhanden
    if Brief["Email"] != '':
        #
        # Mail herstellen (vgl. from email.message import EmailMessage)
        #
        Mail = EmailMessage()
        #
        # Mail zusammensetzen
        #
        ### Betreff
        Mail['Subject'] = Brief['Betreff']
        ### Adressen, falls vorhanden aus Absender
        Mail['From'] = Absender['mail_from']
        Mail['To'] = Brief['Email'].strip()
        if Absender['mail_reply']:
            Mail['Reply-To'] = Absender['mail_reply']
        if Brief['Bcc']:
            Mail['Bcc'] = Brief['Bcc']
        ### Text
        Nachricht_Text = ''
        # if Brief['Name'] or Brief['Vorname']:
        #     Nachricht_Text += "Liebe(r) {vorname} {name},\n\n".format(
        #         vorname = Brief["Vorname"],
        #         name = Brief["Name"])
        Nachricht_Text += Brief["Text"]
        Mail.set_content(Nachricht_Text)
        ### Anhang bzw. Anhänge
        if Brief['Anhang'] == '' or Brief['Anhang'] is None:
            # Es ist kein Anhang ,
            # wir machen daraus eine leere Liste
            listeAnhaenge = []
        elif type(Brief['Anhang']) == str:
            # Es ist ein Dateiname als String angegeben,
            # Wir machen daraus eine einelementige Liste
            listeAnhaenge = [Brief['Anhang'],]
        else:
            # Wir nehmen an, dass es eine Liste von Dateinamen ist
            listeAnhaenge = Brief['Anhang']
        for anhangPfad in listeAnhaenge:
            # Anhang angegeben
            dateiName = os.path.basename(anhangPfad)
            try:
                with open(anhangPfad, 'rb') as Datei:
                    Anhang = Datei.read()
                    Mail.add_attachment(Anhang,
                        maintype = 'application',
                        subtype = 'octet-stream',
                        filename = dateiName)
            except FileNotFoundError:
                # Anhang existiert nicht
                logging.warning('Ge_Definitionen.MailOderBrief: Anhang {} existiert nicht.'.format(anhangPfad))
            except Exception as e:
                # Alle übrigen Fehler
                logging.error('Ge_Definitionen.MailOderBrief: Feher {}'.format(e))
        #
        # Mail verschicken
        #
        context = ssl.create_default_context()
        try:
            smtp_server = Absender['smtp_server']
            smtp_port = Absender['smtp_port']
            with smtplib.SMTP(smtp_server, port=smtp_port) as smtp:
                smtp.starttls(context = context)
                smtp_user = Absender['smtp_user']
                smtp_password = Absender['smtp_password']
                smtp.login(smtp_user, smtp_password)
                smtp.send_message(Mail)
                logging.debug('Ge_Definitionen.MailOderBrief: Mail erfolgreich verschickt')
                return True
        except smtplib.SMTPConnectError:
            logging.error('Ge_Definitionen.MailOderBrief: SMTP-Connenection nicht möglich')
            return False
    else:
        # Keine eMail-Adresse vorhanden, also PDF erzeugen und zum Verschicken
        # an das Tagungsbüro mailen.
        
        ### Adresse
        BriefAdresse = "{vorname} {nachname} \\\\{strasse} \\\\{plz} {ort} \\\\{land}""".format(
                vorname = Brief["Vorname"], nachname = Brief["Name"],
                strasse = Brief["Strasse"],
                plz = Brief["PLZ"],
                ort = Brief["Ort"],
                land = Brief["Land"])
        
        ### Anhang
        BriefAnhang = ""
        if Brief["Anhang"] != '':
            # Anhang angegeben
            BriefAnhang = "\\vspace{{7mm}}Anlage: {}".format(Brief["Anhang"].rpartition('.')[0])
            
        ### Text
        BriefText = """Liebe(r) {vorname} {name},
            dear {vorname} {name},
            
            {text}{anlage}""".format(vorname = Brief["Vorname"], name = Brief["Name"],
                       text = Brief["Text"], #.rpartition("--")[0].strip(),
                       anlage = BriefAnhang)
            
        ### Brief zusammensetzen
        BriefGanz = "\\Brief{{{}}}{{{}}}".format(BriefAdresse,
            BriefText.replace("\n\n\n", "\\par\\vspace{7mm}").replace("\n\n", "\\par").replace("\n", "\\\\\n").replace("\\par", "\n\n"))
        
        ### LaTeX File herstellen
        with codecs.open(LaTeX_Verzeichnis + 'Brief-TB-Text.tex', 'w', encoding="utf-8") as latex_file:
            latex_file.write(BriefGanz)
        
        ### PDF herstellen
        xelatex('Brief-TB', None, 1)
        
        ### Das Ganze an das TB mailen
        #
        # Mail herstellen (vgl. from email.message import EmailMessage)
        #
        Mail = EmailMessage()
        #
        # Mail zusammensetzen
        #
        ### Betreff
        Mail['Subject'] = "DB: Ausrucken und verschicken"
        ### Adressen
        Mail['From'] = Mail_From
        Mail['To'] = Druck_Mail
        Mail.set_content("Automatische Mail von der DB\n\nBitte ausdrucken und mit der Post verschicken.\n")
        ### PDF anhängen
        try:
            with open(LaTeX_Verzeichnis + 'Brief-TB.pdf', 'rb') as Datei:
                Anhang = Datei.read()
                Mail.add_attachment(Anhang,
                    maintype = 'application',
                    subtype = 'octet-stream',
                    filename = 'Brief-TB.pdf')
        except FileNotFoundError:
            # Anhang existiert nicht
            logging.warning('Anhang {} existiert nicht.'.format('Brief-TB.pdf'))
        except Exception as e:
            # Alle übrigen Fehler
            logging.error('Ge_Definitionen.MailOderBrief: Feher {}'.format(e))
        ### Ggf. weitere Anlage hinzufügen (z.B. Einverständniserklärung)
        if Brief["Anhang"] != '':
            # Anhang angegeben
            anhangPfad = Brief["Anhang"]
            dateiName = os.path.basename(anhangPfad)
            try:
                with open(anhangPfad, 'rb') as Datei:
                    Anhang = Datei.read()
                    Mail.add_attachment(Anhang,
                        maintype = 'application',
                        subtype = 'octet-stream',
                        filename = dateiName)
            except FileNotFoundError:
                # Anhang existiert nicht
                logging.warning('Anhang {} existiert nicht.'.format(anhangPfad))
            except Exception as e:
                # Alle übrigen Fehler
                logging.error('Ge_Definitionen.MailOderBrief: Feher {}'.format(e))
        #
        # Mail verschicken
        #
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(SMTP_Server, port=SMTP_Port) as smtp:
                smtp.starttls(context = context)
                smtp.login(SMTP_User, SMTP_Password)
                smtp.send_message(Mail)
                logging.debug('Ge_Definitionen.MailOderBrief: Mail erfolgreich verschickt')
                return True
        except smtplib.SMTPConnectError:
            logging.error('Ge_Definitionen.MailOderBrief: SMTP-Connenection nicht möglich')
            return False
