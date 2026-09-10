# ADR 0007: Kalender und Platzvormerkung in getrennten Inkrementen

Status: Proposed

Date: 2026-09-10

## Context

Janays Workshop-Notiz beschreibt einen hotelähnlichen Kalender: Coaches geben
Termine für bis zu drei Monate frei, Themen werden unterscheidbar dargestellt,
Interessierte merken Plätze vor und Competence Hub prüft das Angebot vor einer
verbindlichen Buchung. Ein zusätzlicher Wunsch sieht Kalendereinträge bei den
Coaches vor, ohne Outlook als einzigen Anbieter vorauszusetzen.

Der aktuelle Pilot umfasst nur interne Firmen-/Kontaktpflege. Coachkonten,
öffentliche Reservierungen, Terminstatus, Vertragsannahme und produktiver
Mailversand sind noch nicht freigegeben. Eine einzige große Kalenderfunktion
würde diese Grenzen vermischen und wäre schwer sicher zu testen oder
zurückzurollen.

## Proposed Decision

1. Visuelle Validierung, bestätigte Terminzustellung, Coach-Verfügbarkeit,
   öffentliche Vormerkung und verbindliche Freigabe werden als getrennte
   Inkremente umgesetzt.
2. Der erste öffentliche Entwurf ist eine crawler-gesperrte statische Vorschau
   mit ausschließlich synthetischen Daten und ohne Netzwerkschreibvorgang.
3. Der erste produktive Fachschritt bildet Coach-Verfügbarkeit, interne Prüfung
   und Veröffentlichung ab. Der erste externe Kalenderzustellungsschritt
   erzeugt für intern bestätigte Termine standardkonforme `.ics`-Einladungen
   mit stabiler UID. Outlook, Google Calendar, Apple Calendar und andere
   kompatible Clients bleiben möglich.
4. Direkte Microsoft-Graph-Synchronisation ist eine spätere optionale
   Integration mit eigenem OAuth-, Datenschutz-, Secret-, Monitoring- und
   Support-Gate.
5. Verfügbarkeit und Vormerkung werden im Competence-Hub-Backend als führende
   Daten gehalten. Externe Kalender sind keine Quelle für öffentliche freie
   Plätze, solange Free/Busy nicht separat freigegeben ist.
6. Schwellenwert und Kapazität sind Werte je Angebot. `25` wird nicht global
   hart codiert, bevor die fachliche Bedeutung bestätigt ist.
7. Veröffentlichung und verbindliche Freigabe sind getrennte, auditierte
   Statusübergänge. Farbe ergänzt den Status, ersetzt aber nie dessen Text.
8. Reservierungen dürfen Kapazität nur in einer Datenbanktransaktion verändern;
   öffentliche Schreibzugriffe erhalten Rate Limit, Datenminimierung und einen
   ausdrücklich freigegebenen Missbrauchsschutz.
9. Ein öffentlicher Termin verlinkt ein freigegebenes Coachprofil. Das Profil
   zeigt später ausschließlich veröffentlichte Vorträge und Gruppenangebote;
   der persönliche Pflegekalender liegt ausschließlich hinter dem Coach-Login.
10. Parallel und zeitlich überlappend stattfindende Angebote sind zulässig.
    Konfliktregeln gelten pro Coach oder Ressource und nicht global pro Datum.
11. Freigabe wird als rollenbasierte Berechtigung modelliert. Janay erhält die
    initiale fachliche Freigabeverantwortung, ohne ihren Namen im Code oder
    Schema als Berechtigungsregel zu verankern.
12. Die Adminrolle darf alle Kalenderoperationen ausführen, um Betrieb und
    Notfälle zu unterstützen; Authentifizierung, Audit und fachliche
    Statusübergänge bleiben trotzdem bindend.

## Consequences

Positive:

- Janay kann den Ablauf früh visuell prüfen, ohne falsche Verfügbarkeit oder
  personenbezogene Daten zu veröffentlichen.
- Anbieterneutralität bleibt erhalten und Outlook kann später gezielt ergänzt
  werden.
- Fachliche Unsicherheiten wie `25`, Ablauf und Sichtbarkeit bleiben
  konfigurierbar statt dauerhaft im Schema versteckt.
- Sicherheits-, Datenschutz- und Rollbacktests bleiben je Inkrement begrenzt.

Negative:

- Der vollständige Wunsch benötigt mehrere Releases statt einer Oberfläche.
- Öffentliche Verfügbarkeit und Coachkalender bleiben zunächst getrennt.
- Vor der ersten produktiven Migration sind zusätzliche fachliche
  Entscheidungen und ein erneuter Frontend-Stack-Review nach ADR 0006 nötig.

## Alternatives

### Outlook/Graph zuerst

Nicht empfohlen. Es erzeugt Anbieterbindung, OAuth- und Tenant-Abhängigkeiten,
bevor der interne Termin- und Freigabeprozess geklärt ist.

### Öffentliche Reservierung direkt in der statischen Website

Abgelehnt. Die IONOS-Seite besitzt keine vertrauenswürdige serverseitige
Kapazitäts-, Rechte-, Audit- oder Missbrauchsschutzgrenze.

### Ein globaler Mindestwert von 25

Abgelehnt, solange unklar ist, ob 25 Mindestgruppe, Prüfschwelle oder Kapazität
bezeichnet und ob die Regel für jedes Format gelten soll.

## Acceptance Evidence

- CAL-0 erfüllt die visuellen Kriterien aus
  `docs/requirements/coach-availability-calendar-v0.1.md`.
- Vor Migration und Backendcode sind die acht offenen Fachentscheidungen
  angenommen oder ausdrücklich verschoben.
- CAL-4 weist stabile UID, Import, Update, Absage, Zeitzone,
  Datenminimierung und sichtbare Zustellfehler synthetisch nach.
- CAL-1 bis CAL-3 weisen RBAC, Audit, Nebenläufigkeit, Kapazitätsgrenze,
  Ablauf/Stornierung und Schutz vor Massenreservierung nach.

## Approval Boundary

Die Annahme dieses ADR autorisiert die lokale technische Vorbereitung in
Inkrementen. Migration auf Staging, echte Coachkonten, Echtdaten,
Kalenderzustellung, öffentliche Reservierung und Produktionsdeployment bleiben
jeweils separate Freigaben.
