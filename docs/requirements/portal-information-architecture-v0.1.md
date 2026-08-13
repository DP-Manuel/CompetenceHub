# Portal Information Architecture v0.1

Stand: 13.08.2026

## Navigation Phase 1

```text
Competence Hub Portal
|- Dashboard
|- Anfragen
|- Unternehmen
|- Coaches
|- Leistungen
|- Themen
|- Benutzer & Rollen
`- Audit
```

Auftraege, Termine, Dokumente, Feedback und Statistiken werden erst in Phase 2
in die Navigation aufgenommen.

## Internes Dashboard

Arbeitsuebersicht statt Reporting-Cockpit:

- neue und offene Anfragen
- eigene oder zugewiesene Vorgange
- zuletzt geaenderte relevante Vorgange
- Hinweise und Aufgaben

Keine Umsatzdiagramme, Coach-Auslastung, Feedbackscores oder KI-Empfehlungen im
ersten Slice.

## Unternehmen

### Liste

- Name, Status und Branche
- Suche nach Name; Filter nach Status und Branche
- Aktionen: Unternehmen oeffnen und anlegen

### Detail

- Firmenname, Branche, Status, interne Notiz
- mehrere Ansprechpartner
- laufende und abgeschlossene Anfragen
- Auftraege, Termine, Dokumente und Feedback nur als spaetere Anschlussbereiche

## Coaches

### Liste

- Anzeigename, Themen, Profilstatus, Region, interne Verfuegbarkeit
- Filter nach Thema, Status und Region

### Detail

- Bereich **Oeffentlich:** freigegebener Name, Region, Themen und Leistungen
- Bereich **Intern:** Profilstatus, Verfuegbarkeit und interne Zuordnungen
- keine Vermischung interner Felder mit Website-Ausgaben

## Anfragen

### Liste

- Betreff, Unternehmen, Themen, Status, Zustaendigkeit, Anfragedatum
- Filter nach Status, Thema, Zustaendigkeit und Unternehmen

### Detail

- Kopf: Betreff, Unternehmen, Status, zustaendig, erstellt am
- Anliegen: vertrauliche Beschreibung, Zeitraum, Format
- Themen und Leistungen als Mehrfachzuordnung
- Verlauf aus Audit-/Aktivitaetsereignissen

Bis zum Praxis-Gate nur neutrale Aktionen:

- Status als Draftwert aendern
- Zustaendigkeit aendern
- Thema oder Leistung zuordnen
- Aktivitaet dokumentieren

Keine Buttons fuer automatische Coach-Anfrage, Angebotserzeugung oder Auftrag.

## Benutzer und Rollen

- Anzeigename, Login/E-Mail, Aktivstatus und Rollen
- Benutzer anlegen und deaktivieren
- Rollen zuweisen und entziehen
- keine Anzeige oder Verwaltung von Klartextpasswoertern
- sicherheitsrelevante Aenderungen im Audit

## Mobile-first/PWA-ready

- wichtigste Aktion und Status im oberen Seitenbereich
- keine Hover-Abhaengigkeit
- Filter als mobiles Sheet/Drawer moeglich
- Details in Abschnitte statt breite Tabellen teilen
- stabile Deep Links
- authentifizierte Daten standardmaessig nicht offline cachen
- Fokus, Tastatur, Touchziele und Statusmeldungen von Beginn an barrierearm
