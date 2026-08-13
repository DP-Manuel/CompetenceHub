# Requirements Engineering Update - 07.08.2026

## Quelle und Status

Quelle ist Manuels bestätigte Produkt- und Betriebsrichtung vom 07.08.2026.
Dieses Dokument konkretisiert den späteren geschützten Portalbereich. Es löst
noch keine Implementierung aus. Rollenmatrix, Excel-Dateninput und
Authentifizierungsdetails folgen.

Fortschreibung 13.08.2026: Rollenmatrix und Excel-Dateninput liegen vor und
sind in `portal-domain-model-v0.1.md`, `portal-schema-spec-v0.1.md`,
`portal-rbac-matrix-v0.1.md`, `portal-information-architecture-v0.1.md` und
`portal-open-gates-v0.1.md` ueberfuehrt. Authentifizierung und finale
Anfrage-Transitionen bleiben offen.

## Bestätigte Richtung

- Die öffentliche Astro-Website bleibt von operativen Daten und
  Datenbankzugriff getrennt.
- Hinter dem Login entsteht eine eigenständige Webapp mit Backend-API und der
  localhost-gebundenen PostgreSQL-Datenbank auf dem VPS.
- Berechtigte interne Personen sollen Nutzer anlegen, Rollen verwalten, Firmen
  und Coaches pflegen sowie später Feedback und Statistiken bearbeiten können.
- Coaches und Firmenkontakte erhalten nur fachlich erforderliche, auf ihren
  Kontext begrenzte Rechte. Eine Person kann mehrere Rollen besitzen.
- Die angekündigte Excel-Tabelle dient als fachlicher Ideengeber und
  Mappingquelle. Sie ist nicht automatisch das Datenbankschema und wird vor
  Import auf Felder, Beziehungen, Pflichtangaben, Datenschutz und Dubletten
  geprüft.

## MVP-Grenze des ersten Portal-Slices

Der erste Slice umfasst ausschließlich eine belastbare interne Grundlage:

1. Authentifizierung für freigegebene interne Testnutzer.
2. Nutzer anlegen, aktivieren und deaktivieren.
3. Mehrere Rollen pro Nutzer zuweisen und entziehen.
4. Berechtigungsprüfungen im Backend, nicht nur im Frontend.
5. Nachvollziehbare Protokollierung sicherheitsrelevanter Änderungen.

Firmen-, Coach-, Feedback- und Statistikfunktionen folgen als getrennte
vertikale Slices. Externe Selbstregistrierung, Zahlungen, produktive
Personendaten und ein öffentliches Nutzerverzeichnis gehören nicht in den
ersten Slice.

## Funktionale Anforderungen

### Identität und Rollen

- `AUTH-001`: Das System muss Nutzerkonten ausschließlich durch dazu
  berechtigte interne Rollen oder einen später ausdrücklich freigegebenen
  Einladungsprozess anlegen.
- `AUTH-002`: Das System muss einer Person mehrere Rollen zuweisen können.
- `AUTH-003`: Das System muss Rollenänderungen sofort serverseitig wirksam
  machen und unberechtigte API-Zugriffe ablehnen.
- `AUTH-004`: Das System muss Nutzer deaktivieren können, ohne historische
  Vorgänge oder Auditnachweise zu löschen.
- `AUTH-005`: Das System muss Anlage, Deaktivierung sowie Rollenvergabe und
  Rollenentzug mit Akteur und Zeitpunkt protokollieren.
- `AUTH-006`: Passwörter dürfen weder durch Administratoren ausgelesen noch im
  Klartext gespeichert oder protokolliert werden.

### Firmen und Coaches

- `ORG-001`: Berechtigte interne Nutzer müssen Firmen und zugehörige Kontakte
  anlegen, bearbeiten, deaktivieren und suchen können.
- `COACH-001`: Berechtigte interne Nutzer müssen Coachprofile, fachliche
  Schwerpunkte, Freigabestatus und zugewiesene Rechte verwalten können.
- `COACH-002`: Coachrechte müssen auf freigegebene eigene oder zugewiesene
  Datensätze begrenzbar sein.
- `LINK-001`: Themen, Leistungen und Coaches müssen als Mehrfachbeziehungen
  modellierbar sein, da mehrere Coaches dasselbe Thema anbieten können.

### Feedback

- `FB-001`: Feedback muss einem konkreten Kontext wie Firma, Auftrag, Coaching,
  Coach oder Veranstaltung zugeordnet werden.
- `FB-002`: Nur berechtigte Nutzer dürfen nicht-öffentliche Feedbackinhalte
  sehen oder auswerten.
- `FB-003`: Spätere externe Feedbacklinks müssen widerrufbar, zeitlich
  begrenzbar und auf genau einen freigegebenen Kontext beschränkt sein.
- `FB-004`: Eine öffentliche Nutzung als Kundenstimme erfordert eine getrennte,
  nachweisbare Veröffentlichungsfreigabe.

### Statistiken

- `STAT-001`: Statistiken müssen rollenabhängig sein und dürfen keine Daten
  außerhalb des erlaubten Firmen-, Coach- oder internen Kontexts offenlegen.
- `STAT-002`: Kennzahlen, Filter, Zeitraum, Datenbasis und Berechnungsregel
  müssen vor Implementierung fachlich definiert werden.
- `STAT-003`: Personenbezogene Detaildaten dürfen nur gezeigt werden, wenn sie
  für den konkreten Zweck erforderlich und freigegeben sind; sonst sind
  aggregierte Werte zu verwenden.

### Excel als Input

- `IMPORT-001`: Die Excel-Tabelle muss zunächst als Mappingquelle geprüft
  werden; kein automatischer Produktivimport erfolgt ohne Importvertrag und
  Validierung.
- `IMPORT-002`: Für jedes Feld sind fachliche Bedeutung, Datentyp,
  Pflichtstatus, Eindeutigkeit, Sichtbarkeit, Bearbeitungsrollen und
  Aufbewahrung zu bestimmen.
- `IMPORT-003`: Beispielzeilen für Entwicklung und Tests müssen synthetisch
  sein. Reale Personendaten bleiben bis zum Produktiv-Gate ausgeschlossen.
- `IMPORT-004`: Ein späterer Import muss fehlerhafte Zeilen melden, Dubletten
  kontrolliert behandeln und einen nachvollziehbaren Ergebnisbericht liefern.

## Nichtfunktionale Anforderungen

- `NFR-SEC-001`: Autorisierung muss für jede geschützte Backendoperation
  serverseitig geprüft werden.
- `NFR-SEC-002`: Sitzungen, Passwort-Reset, Einladungen, Rate Limits und eine
  mögliche MFA-Pflicht werden vor dem ersten öffentlichen Login entschieden.
- `NFR-PRIV-001`: Datenminimierung, Löschung, Aufbewahrung, Auskunft und
  Rollenentzug müssen vor produktiven personenbezogenen Daten definiert sein.
- `NFR-OPS-001`: Reale Daten sind erst zulässig, nachdem ein verschlüsseltes
  Off-Server-Backup auf D+P-kontrolliertem Speicher aus genau dieser externen
  Kopie erfolgreich wiederhergestellt wurde.
- `NFR-OPS-002`: Webapp, Systembenutzer, Secrets, Logs, Datenbankrollen und
  Deployment bleiben vollständig vom Chatbot getrennt.
- `NFR-AUDIT-001`: Auditprotokolle dürfen keine Passwörter, Sessiontokens oder
  unnötige Inhaltsdaten enthalten und sind nur für berechtigte Rollen sichtbar.

## Vorläufige Umsetzungsslices

1. Rollen- und Datenworkshop: Nutzerliste, Rechte je Aktion und Excel-Mapping.
2. Interne Auth-Grundlage: Login, Nutzerstatus, Mehrfachrollen, Auditlog.
3. Firmenverwaltung: Firmen, Kontakte und interne Zuständigkeiten.
4. Coachverwaltung: Profile, Themen, Freigaben und Coachrechte.
5. Feedback: interner Workflow, danach optional sichere externe Links.
6. Statistiken: erst nach fachlicher Definition der Kennzahlen und
   Sichtbarkeitsregeln.

## Noch benötigte Entscheidungen und Inputs

- Nutzer-/Rollentypen mit Rechten für Lesen, Anlegen, Bearbeiten, Freigeben,
  Löschen/Deaktivieren, Export und Statistik.
- Welche Personen im ersten internen Test echte Konten erhalten.
- Excel-Arbeitsmappe mit Feldideen und ausschließlich synthetischen
  Beispielwerten.
- Einladungs-, Passwort-Reset- und MFA-Verfahren.
- Sichtbarkeit eigener Daten für Coaches und Firmenkontakte.
- Benötigte Feedbackarten, Skalen, Freitextregeln und Veröffentlichungsprozess.
- Gewünschte Kennzahlen mit Formel, Zeitraum, Filter und Zielrolle.
- Aufbewahrungs- und Löschfristen je Datenart.

## Abnahmekriterien für den ersten Slice

- `AC-AUTH-001`: Ein berechtigter interner Admin kann einen Testnutzer anlegen,
  deaktivieren und Rollen zuweisen, ohne ein Passwort sehen zu können.
- `AC-AUTH-002`: Ein Nutzer mit zwei Rollen erhält genau die vereinigten
  freigegebenen Rechte.
- `AC-AUTH-003`: Ein nicht berechtigter Nutzer erhält bei direktem API-Zugriff
  eine Ablehnung, auch wenn er die Frontendroute kennt.
- `AC-AUTH-004`: Jede Konto- und Rollenänderung erscheint ohne Secretwerte im
  Auditnachweis.
- `AC-OPS-001`: Der Slice verarbeitet ausschließlich synthetische Testdaten,
  solange das externe Backup- und Datenschutz-Gate offen ist.
