from ugbib_modell.bibModell import *

#######################################################################
# Modelle Anwendungsübergreifend (Regelmäßige Aufgaben, Länder usw.)
#######################################################################

###   Jobs - Public (regelmäßige Aufgaben, insb. Auswertungen
class Jobs(Modell):
    
    # Tabellen
    _tab = 'tbl_jobs'
    
    # Felder
    _felder = [
        idFeld('id'),
        textFeld('titel'),
        # Angaben zum eigentlichen Programm
        textFeld('kommando'),
        textFeld('verzeichnis'),
        textFeld('beschreibung'),
        # Steuerung
        numFeld('intervall'),
        textFeld('einheit'),
        boolFeld('sofort'),
        boolFeld('aktiv'),
        boolFeld('gestoppt'),
        boolFeld('selbstzerstoerend'),
        ]
    
    keyFeldNavi = 'id'
        
    # Relationen
    _relationen = {}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)

    def __str__(self):
        return '{}'.format(self.titel)

class JobsSchlank(Modell):
    
    # Tabellen
    _tab = 'tbl_jobs'
    
    # Felder
    _felder = [
        idFeld('id'),
        textFeld('titel'),
        # Steuerung
        textFeld('kommando'),
        numFeld('intervall'),
        textFeld('einheit'),
        boolFeld('sofort'),
        boolFeld('aktiv'),
        boolFeld('gestoppt'),
        ]
    
    keyFeldNavi = 'id'
        
    # Relationen
    _relationen = {}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)

    def __str__(self):
        return '{}'.format(self.titel)

#######################################################################
# Hilfs-Modelle
#######################################################################

###   Gemeinde - Public
class Gemeinde(Modell):
    
    # Tabellen
    _tab = 'tbl_gemeinde'
    
    # Felder
    _felder = [
        idFeld('id'),
        textFeld('kurz_bez'),
        # Kontaktdaten
        textFeld('strasse'),
        textFeld('plz'),
        textFeld('ort'),
        textFeld('land'),
        textFeld('land_kurz'),
        textFeld('email'),
        # Weiteres, u.a. zur DB, Mailserver usw.
        boolFeld('aktiv'),
        textFeld('rel_verz'),
        textFeld('mail_from'),
        textFeld('mail_reply'),
        textFeld('mail_signatur'),
        textFeld('smtp_server'),
        textFeld('smtp_port'),
        textFeld('smtp_user'),
        textFeld('smtp_password'),
        textFeld('schema'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
        
    # Relationen
    _relationen = {}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)

    def __str__(self):
        return '{}'.format(self.kurz_bez)

###   Farbe - Public
class Farbe(Modell):
    # Tabellen
    _tab = 'tbl_farben'
    
    # Felder
    _felder = [
        idFeld('id'),
        textFeld('farbe'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    keyFeldNavi = 'id'
        
    # Relationen
    _relationen = {}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)

    def __str__(self):
        return '{}'.format(self.farbe)

###   Gruppe - entspricht Rollen
class Gruppe(Modell):
    # Tabelle und Felder
    _tab = 'tbl_gruppe'
    _felder = [
        idFeld('id'),
        textFeld('kurz_bez'),
        textFeld('bez'),
        textFeld('farbe'),
        textFeld('bemerkung'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
        
    # Relationen
    R_farbe = Relation('farbe', Farbe, 'farbe')
    R_farbe.setSQLsort('order by farbe')
    _relationen = {'farbe': R_farbe}
    
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return '{}: {}'.format(self.kurz_bez, self.bez)

class GruppeSchlank(Modell):
    # Tabelle und Felder
    _tab = 'tbl_gruppe'
    _felder = [
        idFeld('id'),
        textFeld('kurz_bez'),
        textFeld('bez'),
        textFeld('farbe'),
        ]
    
    keyFeldNavi = 'id'
        
    # Relationen
    R_farbe = Relation('farbe', Farbe, 'farbe')
    R_farbe.setSQLsort('order by farbe')
    _relationen = {'farbe': R_farbe}
    
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return '{}: {}'.format(self.kurz_bez, self.bez)

###   Anrede
class Anrede(Modell):
    # Tabelle
    _tab = 'tbl_anrede'
    
    # Felder
    _felder = [
        idFeld('id'),
        textFeld('anrede'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
        
    # Relationen
    _relationen = {}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)

    def __str__(self):
        return '{}'.format(self.anrede)

###   Versandart
class Versandart(Modell):
    # Tabelle
    _tab = 'tbl_versandart'
    
    # Felder
    _felder = [
        idFeld('id'),
        textFeld('kurz_bez'),
        textFeld('bez'),
        textFeld('bemerkung'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    _relationen = {}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return '{}: {}'.format(self.kurz_bez, self.bez)

#######################################################################
# Haupt-Modelle
#######################################################################

###   Person
class Person(Modell):
    # Tabelle
    _tab = 'tbl_person'
    
    # Felder
    _felder = [
        idFeld('id'),
        # Identität
        textFeld('name'),
        textFeld('vorname'),
        textFeld('anrede'),
        textFeld('von_und_zu'),
        textFeld('titel'),
        dateFeld('gebdat'),
        # Kontaktdaten
        textFeld('zusatz'),
        textFeld('strasse'),
        textFeld('plz'),
        textFeld('ort'),
        textFeld('land'),
        textFeld('land_kurz'),
        textFeld('email'),
        textFeld('kontaktdaten'),
        # Wohnt bei ...
        numFeld('wohnt_bei_person'),
        numFeld('wohnt_bei_familie'),
        # Bild
        rawFeld('bild'),
        # Bemerkung
        textFeld('bemerkung'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_anrede = Relation('anrede', Anrede, 'anrede')
    R_anrede.setSQLanzeige("anrede")
    R_anrede.setSQLsort('order by anrede')
    _relationen = {'anrede': R_anrede}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return '{}, {}'.format(self.name, self.vorname)

# Zusätzliche Relationen für Person:
#     WohntBeiPerson
#     WohntBeiFamilie kann erst weiter unten definiert werden, da Familie hier noch
#     nicht bekannt ist.

R_WohntBeiPerson = Relation('wohnt_bei_person', Person, 'id')
R_WohntBeiPerson.setSQLanzeige("name || ' ' || vorname || '(' || id || ' ' || ort || ')'")
R_WohntBeiPerson.setSQLsort('order by name, vorname, ort')
Modell.addRelation(Person, 'wohnt_bei_person', R_WohntBeiPerson)


class PersonSchlank(Modell):
    # Tabelle
    _tab = 'tbl_person'
    
    # Felder
    _felder = [
        idFeld('id'),
        # Identität
        textFeld('name'),
        textFeld('vorname'),
        textFeld('anrede'),
        textFeld('von_und_zu'),
        textFeld('titel'),
        dateFeld('gebdat'),
        # Kontaktdaten
        textFeld('zusatz'),
        textFeld('strasse'),
        textFeld('plz'),
        textFeld('ort'),
        textFeld('email'),
        textFeld('kontaktdaten'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_anrede = Relation('anrede', Anrede, 'anrede')
    R_anrede.setSQLanzeige("anrede")
    R_anrede.setSQLsort('order by anrede')
    
    _relationen = {'anrede': R_anrede}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return '{}, {}'.format(self.name, self.vorname)

###   Familie
class Familie(Modell):
    # Tabelle
    _tab = 'tbl_familie'
    
    # Felder
    _felder = [
        idFeld('id'),
        # Identität
        textFeld('name'),
        textFeld('anschrift'),
        textFeld('anrede'),
        # Kontaktdaten
        textFeld('zusatz'),
        textFeld('strasse'),
        textFeld('plz'),
        textFeld('ort'),
        textFeld('land'),
        textFeld('land_kurz'),
        textFeld('email'),
        textFeld('kontaktdaten'),
        # Bemerkung
        textFeld('bemerkung'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_anrede = Relation('anrede', Anrede, 'anrede')
    R_anrede.setSQLanzeige("anrede")
    R_anrede.setSQLsort('anrede')
    _relationen = {'anrede': R_anrede}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return 'Fam. {}'.format(self.anschrift)

# Nachtrag der zusätzlichen Relation zu Person:
R_WohntBeiFamilie = Relation('wohnt_bei_Familie', Familie, 'id')
R_WohntBeiFamilie.setSQLanzeige("anschrift || '(' || id || ' ' || ort || ')'")
R_WohntBeiFamilie.setSQLsort('order by name, ort')
Modell.addRelation(Person, 'wohnt_bei_familie', R_WohntBeiFamilie)

class FamilieSchlank(Modell):
    # Tabelle
    _tab = 'tbl_familie'
    
    # Felder
    _felder = [
        idFeld('id'),
        # Identität
        textFeld('name'),
        textFeld('anschrift'),
        textFeld('anrede'),
        # Kontaktdaten
        textFeld('zusatz'),
        textFeld('strasse'),
        textFeld('plz'),
        textFeld('ort'),
        textFeld('email'),
        textFeld('kontaktdaten'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_anrede = Relation('anrede', Anrede, 'anrede')
    R_anrede.setSQLanzeige("anrede")
    R_anrede.setSQLsort('anrede')
    _relationen = {'anrede': R_anrede}
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return 'Fam. {}'.format(self.anschrift)

#######################################################################
# Beziehungen (n-n-Relationen)
#######################################################################

###   Person - Gruppe
class PersonGruppe(Modell):
    # Tabelle
    _tab = 'tbl_person_gruppe'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('person_id'),
        textFeld('gruppe_kurz_bez'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
        
    # Relationen
    R_person = Relation('person_id', Person, 'id')
    R_person.setSQLanzeige("name || ', ' || vorname")
    R_person.setSQLsort('name, vorname')
    
    R_gruppe = Relation('gruppe_kurz_bez', Gruppe, 'kurz_bez')
    R_gruppe.setSQLanzeige("kurz_bez || ': ' || bez")
    R_gruppe.setSQLsort('order by kurz_bez')
    
    _relationen = {
        'person_id': R_person,
        'gruppe_kurz_bez': R_gruppe,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.person_id, self.gruppe_kurz_bez)

class PersonGruppeSchlank(Modell):
    # Tabelle
    _tab = 'tbl_person_gruppe'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('person_id'),
        textFeld('gruppe_kurz_bez'),
        ]
    
    keyFeldNavi = 'id'
        
    # Relationen
    R_person = Relation('person_id', Person, 'id')
    R_person.setSQLanzeige("name || ', ' || vorname")
    R_person.setSQLsort('name, vorname')
    
    R_gruppe = Relation('gruppe_kurz_bez', Gruppe, 'kurz_bez')
    R_gruppe.setSQLanzeige("kurz_bez || ': ' || bez")
    R_gruppe.setSQLsort('order by kurz_bez')
    
    _relationen = {
        'person_id': R_person,
        'gruppe_kurz_bez': R_gruppe,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.person_id, self.gruppe_kurz_bez)

###   Familie - Gruppe
class FamilieGruppe(Modell):
    # Tabelle
    _tab = 'tbl_familie_gruppe'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('familie_id'),
        textFeld('gruppe_kurz_bez'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_familie = Relation('familie_id', Familie, 'id')
    R_familie.setSQLanzeige("anschrift")
    R_familie.setSQLsort('order by name')
    
    R_gruppe = Relation('gruppe_kurz_bez', Gruppe, 'kurz_bez')
    R_gruppe.setSQLanzeige("kurz_bez || ': ' || bez")
    R_gruppe.setSQLsort('order by kurz_bez')
    
    _relationen = {
        'familie_id': R_familie,
        'gruppe_kurz_bez':  R_gruppe,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.familie_id, self.gruppe_kurz_bez)

class FamilieGruppeSchlank(Modell):
    # Tabelle
    _tab = 'tbl_familie_gruppe'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('familie_id'),
        textFeld('gruppe_kurz_bez'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_familie = Relation('familie_id', Familie, 'id')
    R_familie.setSQLanzeige("anschrift")
    R_familie.setSQLsort('order by name')
    
    R_gruppe = Relation('gruppe_kurz_bez', Gruppe, 'kurz_bez')
    R_gruppe.setSQLanzeige("kurz_bez || ': ' || bez")
    R_gruppe.setSQLsort('order by kurz_bez')
    
    _relationen = {
        'familie_id': R_familie,
        'gruppe_kurz_bez':  R_gruppe,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.familie_id, self.gruppe_kurz_bez)

###   Gruppe - Ansprechpartner
class GruppeAnsprechpartner(Modell):
    # Tabelle
    _tab = 'tbl_gruppe_ansprechpartner'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('person_id'),
        textFeld('gruppe_kurz_bez'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_person = Relation('person_id', Person, 'id')
    R_person.setSQLanzeige("name || ', ' || vorname")
    R_person.setSQLsort('order by name, vorname')
    
    R_gruppe = Relation('gruppe_kurz_bez', Gruppe, 'kurz_bez')
    R_gruppe.setSQLanzeige("kurz_bez || ': ' || bez")
    R_gruppe.setSQLanzeige('kurz_bez')
    
    _relationen = {
        'person_id'  : R_person,
        'gruppe_kurz_bez'  : R_gruppe,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.person_id, self.gruppe_kurz_bez)

class GruppeAnsprechpartnerSchlank(Modell):
    # Tabelle
    _tab = 'tbl_gruppe_ansprechpartner'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('person_id'),
        textFeld('gruppe_kurz_bez'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_person = Relation('person_id', Person, 'id')
    R_person.setSQLanzeige("name || ', ' || vorname")
    R_person.setSQLsort('order by name, vorname')
    
    R_gruppe = Relation('gruppe_kurz_bez', Gruppe, 'kurz_bez')
    R_gruppe.setSQLanzeige("kurz_bez || ': ' || bez")
    R_gruppe.setSQLanzeige('kurz_bez')
    
    _relationen = {
        'person_id'  : R_person,
        'gruppe_kurz_bez'  : R_gruppe,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.person_id, self.gruppe_kurz_bez)

###   Person - Versandart
class PersonVersandart(Modell):
    # Tabelle
    _tab = 'tbl_person_versandart'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('person_id'),
        textFeld('versandart'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_person = Relation('person_id', Person, 'id')
    R_person.setSQLanzeige("name || ', ' || vorname")
    R_person.setSQLsort('name, vorname')
    
    R_versandart = Relation('versandart', Versandart, 'kurz_bez')
    R_versandart.setSQLanzeige("kurz_bez || ': ' || bez")
    R_versandart.setSQLsort('order by kurz_bez')
    
    _relationen = {
        'person_id'      : R_person,
        'versandart'  : R_versandart,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.person_id, self.versandart)

class PersonVersandartSchlank(Modell):
    # Tabelle
    _tab = 'tbl_person_versandart'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('person_id'),
        textFeld('versandart'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_person = Relation('person_id', Person, 'id')
    R_person.setSQLanzeige("name || ', ' || vorname")
    R_person.setSQLsort('name, vorname')
    
    R_versandart = Relation('versandart', Versandart, 'kurz_bez')
    R_versandart.setSQLanzeige("kurz_bez || ': ' || bez")
    R_versandart.setSQLsort('order by kurz_bez')
    
    _relationen = {
        'person_id'      : R_person,
        'versandart'  : R_versandart,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.person_id, self.versandart)

###   Familie - Versandart
class FamilieVersandart(Modell):
    # Tabelle
    _tab = 'tbl_familie_versandart'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('familie_id'),
        textFeld('versandart'),
        # Verwaltung des Datensatzes
        textFeld('bearb_von'),
        datetimeFeld('bearb_am'),
        datetimeFeld('bearb_auto'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_familie = Relation('familie_id', Familie, 'id')
    R_familie.setSQLanzeige("anschrift")
    R_familie.setSQLsort('order by name')
    
    R_versandart = Relation('versandart', Versandart, 'kurz_bez')
    R_versandart.setSQLanzeige("kurz_bez")
    R_versandart.setSQLsort('order by kurz_bez')
    
    _relationen = {
        'familie_id'         : R_familie,
        'versandart'      : R_versandart,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.familie_id, self.versandart)

class FamilieVersandartSchlank(Modell):
    # Tabelle
    _tab = 'tbl_familie_versandart'
    
    # Felder
    _felder = [
        idFeld('id'),
        numFeld('familie_id'),
        textFeld('versandart'),
        ]
    
    keyFeldNavi = 'id'
    
    # Relationen
    R_familie = Relation('familie_id', Familie, 'id')
    R_familie.setSQLanzeige("anschrift")
    R_familie.setSQLsort('order by name')
    
    R_versandart = Relation('versandart', Versandart, 'kurz_bez')
    R_versandart.setSQLanzeige("kurz_bez || ': ' || bez")
    R_versandart.setSQLsort('order by kurz_bez')
    
    _relationen = {
        'familie_id'         : R_familie,
        'versandart'      : R_versandart,
        }
  
    def __init__(self, id=None, holen=False):
        super().__init__(id=id, holen=holen)
    
    def __str__(self):
        return "{}: {}".format(self.familie_id, self.versandart)

