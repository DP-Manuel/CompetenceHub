# Portal Open Gates v0.1

Stand: 14.08.2026

## Gate A - vor dem jeweiligen Implementierungsschritt

### Anfrageworkflow

Janays operatives Feedback vom 14.08.2026 beschreibt den Weg von der ersten
Anfrage ueber parallele Coach-Verfuegbarkeitspruefung, Angebot, Auftrag,
Durchfuehrung, Feedback, Rechnung und Zahlung bis zum Abschluss. Die sichere
Auswertung steht in `janay-request-workflow-feedback-2026-08-14.md`.

Vor Transitionregeln und Automation bleiben insbesondere offen:

- finale Statusnamen, erlaubte Uebergaenge, Reaktivierung und Actor-Rechte
- rechtlich freigegebene Auftragsannahme und Stornierungsregeln
- Vertraulichkeitsfreigabe vor Nennung der Kundenidentitaet an Coaches
- Quelle der Wahrheit fuer Angebot, Rechnung und Zahlung
- Aufbewahrung und Minimalinhalt von Aktivitaets-/Abschlussnachweisen
- Erinnerungs-, Vertretungs- und Eskalationsregeln

Bis dahin sind Datenstruktur, Draftstatus, Wireframes und Spezifikation erlaubt;
harte Transitionregeln und Automation nicht. Die im Feedback enthaltene
48-Stunden-Angabe, Klickannahme und Ergebnisbewertung sind nicht freigegeben.

### Authentifizierung

ADR 0003 wurde von Manuel am 13.08.2026 freigegeben; die testbaren Anforderungen
stehen in `internal-authentication-v0.1.md`. Migration `0002`, API-Vertrag,
Sicherheitsprimitive und synthetische Tests sind vorbereitet; die Migration ist
auf der leeren VPS-Staging-Datenbank angewendet und verifiziert. Login-,
Session-, MFA-, Lifecycle- und Outbox-Repositories/APIs sind lokal implementiert
und ueber 13/13 synthetische Staging-Pfade verifiziert. Ein laufender Dienst,
echte Konten, externe Zustellung und Produktion bleiben durch Security-,
Operations-, Daten- und Deployment-Gates gesperrt. ADR 0003 entscheidet:

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
