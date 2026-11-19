# CAL-2: Lokale Vormerkungsdemo

Stand: 19.11.2026. Nur lokale synthetische Daten. Kein VPS-Update, keine öffentliche
Schreibfunktion, keine realen Konten und kein Versand. Die Website und der bestehende
CAL-1-Pilot bleiben unverändert.

Dies ist der Nachweis des ersten MVP. Für den aktuellen Vier-Rollen-Start,
Neustart und die Entscheidungsliste gilt die
[gemeinsame CAL-2-Pilotabnahme](2026-11-19-cal2-pilot-acceptance.md).

## Demo Starten

In **PowerShell**, aus dem Webapp-Verzeichnis. Docker Desktop mit lokalem Linux-Engine,
vorhandenem Image `postgres:16-bookworm` und die bestehende Webapp-Umgebung mit
Playwright/Firefox werden benötigt. Kein Passwort eingeben oder aus dem Chat übernehmen.

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp'
.\.venv\Scripts\python.exe scripts/run-cal2-local.py
```

Bei `CAL2_DEMO=READY` sind Firmenkontakt und Reviewer in getrennten Firefox-Fenstern
über lokales HTTPS angemeldet. Die Anmeldung/MFA verwendet nur für diesen Lauf
erzeugte Daten und eine isolierte Loopback-Testverbindung. Der Runner akzeptiert
dabei das eigene lokale Testzertifikat; es wird kein Betriebssystemvertrauen geändert
und kein Beleg für ein öffentliches TLS-Zertifikat abgeleitet. **Enter im Terminal**
beendet die Demo; erwartet ist `CAL2_CLEANUP=PASS`. Ein belegter lokaler
PostgreSQL-Port 55433 wird nicht übernommen.

1. Als **Demo-Firma A** den freigegebenen zweitägigen Workshop öffnen.
2. Zwei Plätze eingeben, vorhandenen Kontakt bestätigen, **Unverbindlich vormerken**.
3. Als **Reviewer** in **Vormerkungen prüfen** den Vorgang öffnen. Sie sehen
   belegte/angefragte Plätze, Kapazität, Prüfschwelle und Entscheidungsfrist.
4. **Klärung anfordern** wählen, eine kurze Begründung eingeben und speichern.
5. Firmenansicht neu laden, Änderung öffnen und drei Plätze eintragen. Beim Reviewer
   nach Neuladen den Hinweis **Prüfschwelle erreicht** prüfen.
6. Reviewer entscheidet **Positiv prüfen (keine Buchung)**. Dann **Auch
   abgeschlossene Vorgänge anzeigen** wählen und in der Firmenansicht neu laden:
   Status **Positiv geprüft** und Statusverlauf sind sichtbar.

## Fachgrenzen

Die [angenommenen CAL-D01–D08](../requirements/calendar-stakeholder-decisions-2026-09-11.md),
[CAL-T01–T06](../requirements/calendar-cal1-migration-decisions-2026-09-11.md) und
[ADR 0007](../decisions/0007-calendar-and-reservation-increments.md) bleiben
unverändert. Die folgenden ergänzenden Regeln konkretisieren die
[offenen Vorschläge vom 17.11](../requirements/cal2-small-slice-2026-11-17.md)
**für die synthetische Demo**, nicht als Freigabe fürs echte Vormerken:

| Status bzw. Aktion | Wirkung |
| --- | --- |
| Eingereicht / Klärung nötig | Belegt Plätze. Firma kann die Menge ändern oder bis zur abschließenden Entscheidung zurücknehmen. Pro Angebot eine belegende Vormerkung je Firma. |
| Positiv geprüft | Belegt weiter; keine Vertragsannahme, keine Buchung und kein Versand. Nicht mehr durch die Firma zurücknehmbar. |
| Abgelehnt / zurückgenommen | Gibt Plätze frei und erhält den Verlauf. |
| Angebot zurückgezogen | Offene und positiv geprüfte Vormerkungen werden in derselben Transaktion abgesagt; die veröffentlichten Daten und ICS verschwinden gemäß CAL-1. |
| Entscheidungsfrist erreicht | Keine neuen oder erhöhten Anfragen. Reduzieren und Zurücknehmen bleiben bei offenen Vorgängen möglich. Offene Vorgänge bleiben sichtbar überfällig, mit explizitem Hinweis auf die bis zur Entscheidung gehaltenen Plätze. |
| Prüfschwelle erreicht | Portalaufgabe/Hinweis und Ereignis bei Überschreiten der Schwelle; keine automatische Entscheidung. Die Prüfschwelle ist der vorhandene angebotsbezogene CAL-1-Wert, keine neu erfundene zwingende Mindestgruppe. |

Ein entschiedener Vorgang bleibt lesbar. Solange Plätze belegt sind, darf eine neue
Angebotsrevision nicht veröffentlicht werden; die bisherige bleibt sichtbar.
Damit ändern sich zugesagte Angebotsbedingungen nicht stillschweigend. Die
spätere fachliche Behandlung solcher Revisionen muss vor dem Echtbetrieb bestätigt werden.

## Technischer Umfang

- Migration [0010](../../apps/webapp/database/migrations/0010_calendar_reservations.sql):
  Vormerkung mit Angebotsrevision, Firma/Kontakt, Platzzahl und Versionszähler;
  manipulationsgeschützt für den App-DB-Account anhängbarer Statusverlauf. Dieser
  enthält Aktion, Akteur, Zeitpunkt, Vorher/Nachher, Platzdelta und Begründung.
  Allgemeines Audit enthält keine Telefonnummern, Nachrichten oder Begründungstexte.
- Geschützte Routen unter `/api/v1/portal/reservations`: Katalog, Liste, Detail,
  Erstellen, Mengenänderung, Rücknahme und Entscheidung. Rollen, bestehendes
  MFA-/Sessionverfahren, Origin/CSRF und `no-store` bleiben bindend. Eine eindeutige
  Firmenzuordnung wird serverseitig aus der vorhandenen Kontaktbindung ermittelt.
  `calendar_reviewer` und `admin` dürfen entscheiden; `internal` und Coach nicht
  allein aufgrund ihrer Rolle. Kein Browser- oder Personenname autorisiert eine Entscheidung.
- Die CAL-1-Angebotszeile serialisiert Kapazität, Veröffentlichung und Rücknahme.
  Der DB-Zeitpunkt wird nach der Sperre gelesen. Geschützte Wiederholungsschlüssel
  werden an Akteur und Inhalt gebunden; `If-Match` schützt Folgeänderungen.
- Statusereignisse sind interne, getestete Benachrichtigungssignale. Keine SMTP-
  oder Outbox-Einträge, keine E-Mails, Kalendereinladungen oder Rechnungen.
  Öffentliche CAL-1-Projektion, ICS und unverbindliche E-Mail-Anfrageentwürfe bleiben
  ohne Reservierungs- oder Kontaktdaten.
- CAL-2 ist im neugestarteten Standardruntime deaktiviert. Nur der vorhandene
  lokale Fixture-Start mit eigenem PostgreSQL-Container aktiviert es explizit.

## Prüfung Und Nächstes Gate

Der gleiche Startbefehl mit `--verify` führt den echten Browser-/PostgreSQL-
Abnahmelauf aus. Ergebnis: **17 native Nachweise und 72 gezielte Vertragstests
bestanden**. Geprüft wurden mobile Tastatur- und Feldbedienung bei 390 px,
native 200 % Zoom, Wiederholung, konkurrierender letzter Platz, Frist, fachliche
Rücknahme/Entscheidung, Rollen/Firmengrenzen, CAL-1-Revisionskonflikt/Absage und
Persistenz nach Neustart. Bei nativem Zoom wurden Hit-Tests und Tastaturbedienung
geprüft, kein physischer Mausklick und kein manueller Screenreader-Lauf. Kein
vollständiger CAL-1-Wiederholungslauf. Container und Volume nachweislich entfernt.

Nächster Block: **lokale fachliche CAL-2-Abnahme mit Janay**. Mit der Demo
Platzbindung, Entscheidungsfrist, Revisionsschutz und Arbeitsübersicht bestätigen.
Staging-Migration und Aktivierung bleiben separat genehmigungspflichtig.
Vor echten Vorgängen zusätzlich EDV-Zugang/HTTPS, bestätigte Firmenidentitäten,
Rollen, Aufbewahrung/Löschweg und produktiven Missbrauchsschutz klären.
SMTP bleibt ein getrenntes Gate und ist für die lokale Abnahme nicht erforderlich.
