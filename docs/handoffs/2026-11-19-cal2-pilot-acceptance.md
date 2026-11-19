# CAL-2: Gemeinsame Pilotabnahme

**Ziel:** Manuel und Janay gehen die lokale Demo gemeinsam durch und entscheiden
einmal gebündelt über die offenen Fachregeln. Richtwert: 35 bis 45 Minuten.
Die Abnahme aktiviert weder die neue Version am VPS noch echte Benutzer,
Kundendaten, verbindliche Buchungen oder Nachrichten.

## Demo Starten

Docker Desktop mit Linux-Engine, vorhandenes Image `postgres:16-bookworm` und die
bestehende Webapp-Umgebung mit Playwright/Firefox verwenden. Terminal **PowerShell**:

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp'
.\.venv\Scripts\python.exe scripts/run-cal2-local.py
```

Bei `CAL2_DEMO=READY` öffnen sich vier getrennte, automatisch angemeldete
Firefox-Fenster: Coach, Reviewer, Demo-Firma A und Demo-Firma B. Auf localhost
läuft ein eigener HTTPS-Testserver. Sein temporäres Testzertifikat gilt nur in
den Testfenstern; Systemvertrauen und produktives TLS bleiben unangetastet.
Keine Zugangsdaten eingeben oder weitergeben. Ein bereits belegter PostgreSQL-Port
55433 wird nicht übernommen. **R + Enter** startet App und Datenbank neu und öffnet
die vier Rollen erneut; `CAL2_RESTART=PASS` bestätigt die erneute Erreichbarkeit.
**Enter ohne R** beendet den Lauf; `CAL2_CLEANUP=PASS` bestätigt die Entfernung
des eigenen Containers und Volumes. Ein neuer Lauf beginnt mit leeren Vorgängen.

## Checkliste Für Eine Sitzung

| Prüfung | Durchführung und erwartetes Ergebnis |
| --- | --- |
| [ ] Veranstaltung erstellen | Coach erstellt z. B. „Demo-Schulung“ in 8 Tagen; Ende am Folgetag, online, Kapazität 5, Prüfschwelle 3 und Entscheidungsfrist zwei Tage vor Beginn. Thema aus der Liste und „Preis nach Abstimmung“ wählen. Speichern und zur Prüfung einreichen. |
| [ ] Veröffentlichung prüfen | Reviewer veröffentlicht in der CAL-1-**Prüfliste**. Erst dann ist der Termin nach Neuladen für A und B im Unternehmensbereich vorhanden. |
| [ ] Suchen und verstehen | A sucht nach Titel oder Thema und öffnet Veranstaltungsdetails. Zeitraum, Format, Ort bzw. online, Preis, verfügbare Plätze und Frist sind verständlich. Hilfe erneut öffnen, die Einführung starten und überspringen. |
| [ ] A merkt vor, B sieht Grenze | B öffnet das Eingabeformular noch vor A. A bestätigt den vorhandenen Firmenkontakt und merkt 2 Plätze vor. B versucht aus seinem noch offenen Formular 4 Plätze; die serverseitige Prüfung lehnt die Anfrage ab und erklärt den Fehler am Feld. B merkt danach 2 Plätze vor. |
| [ ] Cockpit nutzen | Reviewer öffnet **Vormerkungen prüfen**, sucht nach Veranstaltung und Coach und probiert Status-, Tag- und Fristfilter. Am Angebot: 4 offen angefragt, 4 belegt, Kapazität 5, Prüfschwelle 3, 2 offene Vorgänge. Der Status **Entscheidung nötig** zeigt bearbeitbare Fälle. |
| [ ] Rückfrage stellen und beantworten | Reviewer stellt A eine Rückfrage. A lädt neu, findet unter **Aufgaben und Ereignisse** die offene Antwort und antwortet im Vorgang. Reviewer lädt neu; die Antwort und der Verlauf sind sichtbar. B sieht den fremden Vorgang nicht. |
| [ ] Ändern und Abbrechen | A trägt 3 Plätze ein, wählt **Abbrechen**, bleibt zunächst im Formular und kontrolliert die Eingabe. A speichert dann die Änderung. Fünf Plätze sind belegt. |
| [ ] Positiv prüfen und zurücknehmen | Reviewer wählt für A **Positiv prüfen (keine Buchung)** mit Begründung. A sieht das Ergebnis, kann aber nicht mehr selbst zurücknehmen. B zieht seine noch offene Vormerkung zurück; 2 Plätze werden wieder frei. Beide Vorgänge bleiben mit Status und Verlauf auffindbar. |
| [ ] Veranstaltungsänderung prüfen | Coach ändert Beginn, Ort/Format oder Kapazität in einer neuen Revision und reicht sie ein. Reviewer sieht in den Aufgaben die Änderung und im betroffenen Vorgang die Felder. Der Veröffentlichungsversuch wird nachvollziehbar gesperrt; A bleibt auf der alten Fassung. Nichts wird umgebucht. |
| [ ] Ablehnung und Absage unterscheiden | B kann vor Ablauf der Frist eine neue Anfrage stellen. Unter **Vormerkungen prüfen** ablehnen und über **Abgelehnt** wiederfinden. Optional: Coach zieht danach das Angebot zurück; A sieht die Absage samt Verlauf, das Angebot verschwindet aus Kalender und Katalog. |
| [ ] Neustart und Verlauf | Im Terminal **R + Enter**. Danach in denselben Rollen Status und Verlauf prüfen. Kein zweiter Vorgang und keine Nachricht. |
| [ ] Bedienung und Ergebnis | Auf Smartphone-Größe oder bei 200 % prüfen: Suche, Formulare, Status, Fokus nach Feldfehler und Abbrechen. Dann unten Entscheidungen festhalten und Demo mit Enter beenden. |

Alle Daten und Anzeigen sind synthetisch. **Eingereicht** und **Klärung nötig**
halten nach der Demo-Regel vorläufig Plätze. **Positiv geprüft** hält sie weiter,
ist aber ausdrücklich keine Buchung. **Abgelehnt**, **zurückgenommen** oder
**Veranstaltung abgesagt** geben Plätze frei. Nach Fristende sind neue oder
erhöhte Anfragen gesperrt; offene Vorgänge können weiterhin reduziert oder
zurückgenommen werden. Die Prüfschwelle ist ein Hinweis zur Prüfung, keine neue
verbindliche Mindestgruppe.

## Einmalige Entscheidungsliste

Die [Fachentscheidungen CAL-D01–D08](../requirements/calendar-stakeholder-decisions-2026-09-11.md),
[CAL-T01–T06](../requirements/calendar-cal1-migration-decisions-2026-09-11.md) und
[ADR 0007](../decisions/0007-calendar-and-reservation-increments.md) bleiben
unverändert. Nur die nachstehenden Ergänzungen vor dem Echtbetrieb festhalten:

| Thema | Demo-Stand und wirklich offene Entscheidung |
| --- | --- |
| Platzbindung und Frist | Demo bindet bei eingereicht, Klärung und positiver Prüfung; Fristende stoppt nur neue und erhöhte Anfragen. Bestätigen oder explizit festlegen, welche Status wie lange binden und wie überfällige Fälle aufgelöst werden. |
| Wesentliche Änderungen | Demo schützt die veröffentlichte Fassung bei jeder neuen Revision mit belegten Plätzen. Vorschlag, Datum, Frist, Kapazität, Ort und Format werden im Prüfprozess erkannt. Klären, wann explizite Rückbestätigung, Freigabe einer reinen Kapazitätserhöhung oder Absage zulässig sein soll. Keine stille Übernahme. |
| Zuständigkeit | Die zuweisbare Prüferrolle und der technische Admin-Notfallzugriff stehen bereits fest. Nur Zuständigkeiten bei Eskalation, Vertretung und späterem Ausnahmefall konkretisieren; Janay bekommt keine Adminrechte. |
| Verbindlicher Schritt | Der bereits festgelegte getrennte Freigabeschritt bleibt bestehen. Später konkretisieren, wessen Bestätigung und welcher Nachweis eine verbindliche Buchung auslösen. In dieser Demo nicht implementiert. |
| Benachrichtigungen | Interne Aufgaben und Ereignisse vorhanden. Nur spätere Zustellung, Empfänger, Auslöser und Umfang für z. B. Rückfragen, Fristen, Entscheidungen und Absagen bestätigen. Kein SMTP, keine SMS, keine Versandzusage. |
| Aufbewahrung und Löschung | Vergangene Vorgänge bleiben in der Demo filterbar; mit Demoschluss werden alle Testdaten gelöscht. Für echte Daten Löschfristen, Löschweg und zulässige Audit-Restdaten bestätigen. Keine Laufzeit erfunden. |

**Abnahme festhalten:** Datum, Teilnehmende, Ergebnis je Prüfung und Entscheidung;
offene Punkte mit Verantwortlichen protokollieren. Die fachliche Abnahme gilt als
abgeschlossen, wenn Manuel und Janay die geprüften Wege und offenen Regeln
gemeinsam bestätigt oder ausdrücklich abgegrenzt haben.

## Technischer Stand Und Betriebsgates

- Ein Reservierungsmodell, die Angebotsrevision und die bestehende Ereignistabelle
  aus [0010](../../apps/webapp/database/migrations/0010_calendar_reservations.sql).
  [0011](../../apps/webapp/database/migrations/0011_calendar_reservation_replies.sql)
  ergänzt den Ereignistyp für Antworten und Indizes; keine zweite Tabelle.
  Wiederholungen verwenden weiterhin denselben Auftragsschlüssel. Änderungen,
  Veröffentlichung und Rücknahme serialisieren sich an derselben Angebotszeile.
- Aufgaben werden aus vorhandenen Ereignissen, dem aktuellen Status, Fristen und
  Revisionen berechnet. Die Oberfläche zeigt bis zu 30 aktuelle Aufgaben und
  30 jüngste Ereignisse. Wiederholte Aufträge erzeugen keine zusätzlichen
  Ereignisse; ausstehende Fristen/Revisionen erscheinen je Angebot, nicht je Firma.
- Firmenzuordnung, MFA, Sessions, Origin/CSRF, `no-store`, keine fremden
  Firmenkontakte und keine Entwurfsdaten im Unternehmens- oder öffentlichen Bereich. Die
  Ereignisübersicht enthält keine Kontakt-/Nachrichtentexte; Antworten sind nur
  im berechtigten Vorgang sichtbar. Keine Postfacheinträge oder Versandversuche.
- Prüfung: **26 Browser-/PostgreSQL-Nachweise und 85 gezielte Regressionstests
  bestanden**. Start, interaktiver Neustart und Ende der Vier-Rollen-Demo separat
  geprüft; Container und Volume entfernt. Zusammenhängende Abnahme reproduzierbar
  mit demselben Startbefehl plus `--verify`: 390 px, nativer 200-%-Zoom per
  Tastatur, tatsächlicher PostgreSQL-Neustart während eines wartenden Schreibens.
  Gezielte CAL-1-API-, Laufzeit- und gemeinsame Tour-Regression, kein vollständiger
  CAL-1-Wiederholungslauf und kein manueller Screenreader-Lauf.
- Vor einem geschützten VPS-Piloten: gebündelte Fachabnahme abschließen; separat
  Code-/Migrationsstand (einschließlich nötiger Vorgängermigrationen),
  Wiederherstellung und Rollback bestätigen; isolierten geschützten
  Ausführungs- und synthetischen Smoke-Plan freigeben. Erst vor realer Nutzung
  zusätzlich tatsächliche Firmenidentitäten, Rollen, Datenschutz/Löschung,
  Zugriffsschutz und Missbrauchsschutz nachweisen. DNS/TLS und SMTP nach
  vorhandenem Verfahren behandeln. Kein Deploy und keine DB-Änderung autorisiert.
