# Kundenverwaltung im lokalen Pilotmodus

Das Word-Feedback vom 19.11.2026 benennt zwei Arten von Kunden. Die
Kundenverwaltung unterscheidet Privatkunden und bestehende Unternehmen, ohne
Firmenkontakte, Portalzugänge oder Kalender-Vormerkungen neu zuzuordnen.

| Bereich | Pflicht | Optional |
| --- | --- | --- |
| Privatkunde | Vorname, Nachname | E-Mail, Telefon, Rechnungsanschrift |
| Geschäftskunde | Bestehende Firmen- und Ansprechpartnerlogik | Eine Geschäfts- oder Rechnungsanschrift, USt-IdNr. |

Eine erfasste Anschrift besteht aus Straße/Hausnummer, Postleitzahl, Ort und
Land. Eine USt-IdNr. wird formal geprüft, nicht behördlich verifiziert.
Private Datensätze sind keine Benutzerkonten und keine Mandanten. Sie können
weder angemeldet noch für CAL-2-Firmenreservierungen verwendet werden.
Keine Importe, Einladungen, Rechnungen, Zahlungen oder öffentlichen Projektionen.

## API und Aktivierung

Prefix: `/api/v1/portal/customers`. Sämtliche Routen übernehmen die
bestehende serverseitige Admin-/Intern-Prüfung der Firmenverwaltung.

| Methode | Pfad | Funktion |
| --- | --- | --- |
| GET | `/capabilities` | `enabled` für einen berechtigten Portalzugang |
| POST | `/private/search` | Nach Namen suchen; nur UUID, Vor- und Nachname, optional Cursor |
| POST | `/private` | Privatkunden erfassen |
| GET / PUT | `/private/{customer_id}` | Geschützte Details lesen / mit Versionsprüfung speichern |
| GET / PUT | `/companies/{company_id}/details` | Zusatzdaten einer bestehenden Firma lesen / mit Versionsprüfung speichern |

Suche und Schreiben verlangen Origin und Session-CSRF. Private Namen stehen
nicht in Such-URLs. Alle Antworten bleiben `no-store`. Das Schreib-Audit
enthält nur Aktion, Benutzerkennung, Datensatzkennung, Zeit und Ergebnis.
`app.state.customer_administration` wird nur beim Start einer ausdrücklich
aktivierten lokalen Fixture oder eines isolierten synthetischen Piloten
gesetzt, wenn beide Tabellen aus
[Migration 0012](../../apps/webapp/database/migrations/0012_customer_administration.sql)
bereitstehen. Der historische CAL-2-Stand 0011 bleibt ohne die neue Funktion
startfähig; im Standardmodus bleibt sie auch mit 0012 deaktiviert.

## Einbindung und Prüfung

Das [Portal-Modul](../../apps/webapp/src/competence_hub_api/portal_ui/customer-administration.js)
baut Kundenart, Privatkundenliste, Privatkundenformular und Zusatzdatenformular.
Das Portal blendet beim Wechsel zur Privatkundenansicht nur die Firmenliste und
-suche aus. Der Anlegebutton verwendet den bestehenden Firmendialog weiter,
sofern `openPrivateCreate(button)` nicht übernimmt. Beim Firmenwechsel
`canLeave()` prüfen; beim Verlassen der Kundenverwaltung `leaveWorkspace()`
aufrufen und bei `false` dort bleiben. Beim Abmelden `reset()`.

Der [native Nachweis](../../apps/webapp/scripts/verify-local-customer-administration.py)
verwendet ausschließlich einen eigenen PostgreSQL-16-Container und lokale
synthetische Sitzungen. Er umfasst den Übergang 0011/0012, die Altmodus-Sperre,
Rollen, konkurrierende Versionen, minimale Auditdaten, exakte Erhaltung
bestehender Unternehmens- und Kontodaten sowie die Firefox-Bedienung bei 390 px.

Vor echter Nutzung sind insbesondere Verarbeitungszweck, Aufbewahrungs- und
Löschverfahren sowie gegebenenfalls getrennte Geschäfts- und
Rechnungsanschriften fachlich zu entscheiden. Dieser Stand legt keine
Veröffentlichungs- oder Echtbetriebsfreigabe fest.
