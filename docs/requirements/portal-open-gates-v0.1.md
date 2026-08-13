# Portal Open Gates v0.1

Stand: 13.08.2026

## Gate A - vor dem jeweiligen Implementierungsschritt

### Anfrageworkflow

Mit Janay beziehungsweise der spaeteren Bearbeitung einen realen Fall von der
ersten Firmenanfrage bis zum Abschluss durchspielen. Offen sind insbesondere:

- Beginn und Parallelitaet der Coach-Suche
- Reihenfolge Coach-Zusage, Angebot und Auftrag
- Pause, Reaktivierung, Ablehnung und kein passender Coach
- Terminierung, Abschluss und Feedback
- erlaubte Statusuebergaenge und automatische Aktionen

Bis dahin sind Datenstruktur, Draftstatus, Wireframes und Spezifikation erlaubt;
harte Transitionregeln und Automation nicht.

### Authentifizierung

ADR 0003 wurde von Manuel am 13.08.2026 freigegeben; die testbaren Anforderungen
stehen in `internal-authentication-v0.1.md`. Migration `0002`, API-Vertrag,
Sicherheitsprimitive und synthetische Tests sind vorbereitet; die Migration ist
auf der leeren VPS-Staging-Datenbank angewendet und verifiziert. Vor einem
laufenden Login bleiben Repository-/API-Implementierung und Security-Review
erforderlich. ADR 0003 entscheidet:

- Session oder Tokenmodell
- Passwort-/Einladungs-/Resetverfahren
- Logout, Ablauf, Geraeteverlust und Mehrgeraetebetrieb
- CSRF, XSS, Rate Limits und MFA
- Audit und Secretbetrieb

Noch offene Produktivpunkte sind finale App-Origin, Mailanbindung,
Nachfolge-/Break-glass-Admin und Aufbewahrungsdauer von Auth-/Auditereignissen.
Sie blockieren einen synthetischen lokalen Implementierungsslice nicht, aber
den Produktivbetrieb.

### Produktive personenbezogene Daten

Vor Echtdaten:

- verschluesselter Off-Server-Dump auf D+P-kontrolliertem Ziel
- erfolgreicher Restore aus genau dieser externen Kopie
- Aufbewahrungs- und Loeschregeln
- Verantwortlichkeiten und Notfallzugriff

## Gate B - vor fachlichem CRUD-Abschluss

- Unternehmen: Rechtsname gegen Anzeigename, Anschrift und Kundennummer nur bei
  echtem Arbeitsbedarf.
- Ansprechpartner: Primaerkontakt ja oder nein.
- Coach/Leistung: optionale Relation bestaetigen oder verwerfen; keine
  Pflichtzuordnung vorwegnehmen.
- Rollen: vier Arbeitscodes formal bestaetigen; Rechtebasis ist bereits v0.1.

## Gate C - deferred

- B2C-/Mindforge-Portal
- Teilnehmer, Massnahmen, Praktikum/Vermittlung und Stellen
- Auftraege, Termine, Dokumente und Feedback
- Reportingformeln und Mindestmengen
- Push, Offline-Fachdaten und native Stores
- Vertraege, Rechnungen, Kalender und KI-Matching
