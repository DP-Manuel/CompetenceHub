# CAL-2: Kleine Platzvormerkung

Stand17.11.2026. Fachlicher Umsetzungsvorschlag, keine neue Implementierung,
Migration, Benutzerfreigabe oder Nachricht. Grundlage sind die angenommenen
[CAL-D01–D08](calendar-stakeholder-decisions-2026-09-11.md) und
[ADR0007](../decisions/0007-calendar-and-reservation-increments.md).
CAL-1-Veröffentlichung und Janays Abnahme bleiben abgeschlossen.

## Ein Begrenzter Erster Slice

Angemeldeter, berechtigter Firmenkontakt fragt für genau eine veröffentlichte
Veranstaltung eine positive ganze Platzzahl an. Firmen-/Kontaktdaten kommen aus
der bestätigten Zuordnung; Kontaktperson wird bestätigt, Nachricht/Telefon bleiben
freiwillig. Privatpersonen und nicht Angemeldete nutzen weiter den Kontaktweg.
Keine freie Buchung, Zahlung, Rechnung, Mail oder öffentlich sichtbare Kontaktdaten.

| Feld / Regel | Kleiner Zielumfang |
| --- | --- |
| Veranstaltung | Stabile Angebots-ID und veröffentlichte Revision; Entwürfe/Verfügbarkeiten ausgeschlossen |
| Platzzahl | Ganzzahl1…Kapazität; Einreichen/Ändern/Rücknahme mit idempotentem Auftrag und Versionsprüfung |
| Kapazität | Angebotsspezifisch; Prüfung und jede belegungswirksame Änderung atomar im Backend, niemals im statischen Browser |
| Prüfschwelle | Eigener je Angebot änderbarer Wert, derzeit25; löst Prüfaufgabe aus, keine automatische Vertragsannahme |
| Anfragestatus | Vorschlag: eingereicht oder zurückgenommen; keine Löschung des Statusverlaufs |
| Interne Entscheidung | Vorschlag: offen, Klärung nötig, positiv entschieden, abgelehnt; positiv ist weiterhin keine Vertragsannahme |
| Zuständigkeit | Berechtigte Firmenkontakte nur eigene Firma; vorgeschlagen calendar_reviewer für interne Entscheidungen, Admin als auditiertem Notfallzugang; kein Name im Berechtigungscode |
| Fristen | Veröffentlichte Entscheidungsfrist am Angebot; Rücknahme nach D03 bis zur internen Entscheidung |
| Nachvollziehbarkeit | Akteur, Zeitpunkt, Vorher/Nachher, Platzdelta, Angebotsrevision und Entscheidungsgrund; keine Secrets oder unnötigen Kontaktdaten im Audit |

Öffentlich bleiben nur freigegebene Veranstaltungsangaben. Coaches erhalten für
eigene Angebote höchstens den erforderlichen aggregierten Status; keine pauschale
Freigabe sämtlicher Kontaktdaten. Schwellenwert/Frist erzeugen eine Portalaufgabe.
E-Mail- und Kalendereinladungsereignisse bleiben bis zu ihren Zustell-/Bestätigungs-
gates geschlossen; CAL-D08 macht den Hub zur führenden Quelle, nicht Outlook.

## Zwei Präzisierungen Vor Der Umsetzung

1. **Welche Vormerkungen zählen gegen Kapazität?** D02 trennt Kapazität und
   Prüfschwelle, legt den Zeitpunkt der Sitzbindung aber nicht abschließend fest.
   Vorschlag: aktive eingereichte Vormerkungen zählen, Rücknahme/Ablehnung geben
   ihre Plätze frei; keine Warteliste im ersten Slice. Dies ist ein Vorschlag,
   keine bereits angenommene neue Fachregel.
2. **Was schließt die Entscheidungsfrist?** Vorschlag: keine neue/erhöhte Anfrage
   nach der Frist; bestehende Rücknahme bleibt bis zur Entscheidung möglich.
   Kein stilles automatisches Löschen, Vertragsabschluss oder Versand.

## Umsetzung Und Definition Of Done

1. Die zwei Präzisierungen und den minimalen Datenschutz-/Aufbewahrungsumfang
   bestätigen; vorhandene D-Regeln nicht erneut zur Gesamtabnahme vorlegen.
2. Ein enges Daten/API-/RBAC-Review mit bestehenden Versionierungs-, Idempotenz-,
   Transaktions- und Auditmustern; keine neue Plattform oder statische Schreib-API.
3. Synthetischer vertikaler Slice: Anfrage → eigene Liste → Rücknahme bzw.
   interne Entscheidung; keine echten Kontaktdaten/SMTP oder Kalenderzustellung.
4. Gezielte Nachweise: letzter freier Platz unter Parallelzugriff, doppelte/alte
   Aufträge, falsche Firma/Rolle, Frist, Zurückziehen, Angebotsrevision/-rücknahme,
   keine Kapazitätsüberschreitung und kein personenbezogener öffentlicher Export.

DoD des späteren Slices: diese vier Pfade nachvollziehbar, atomare Belegung und
Datenschutz/RBAC nachgewiesen. Tatsächliche Migration, reale Firmenkontakte und
Zustellung erst mit den jeweiligen Freigaben. **Dieser Sprint liefert nur den Vorschlag.**
