# Abgleich der Stakeholder-Updates - 2026-09-10

## Zweck und Grenze

Dieser Abgleich hält fest, welche freigegebenen Hinweise aus den Update-Paketen
vom 13.08., 14.08., 24.08., 27.08. und 04.09.2026 bereits umgesetzt, geplant
oder weiterhin durch ein Gate gesperrt sind. Die privaten Quelldateien bleiben
außerhalb von Git; hier stehen nur die für Planung und Abnahme notwendigen
Ergebnisse.

## Abgleich

| Paket | Kernthemen | Stand | Noch offen / Gate |
| --- | --- | --- | --- |
| 13.08.2026 | Portal-Fachmodell, Datenmodell, Informationsarchitektur und offene Implementierungsentscheidungen | Portal-Kern, Rollenbasis, Authentifizierung und Firmen-/Kontaktgrenze sind versioniert, getestet und auf Staging nachgewiesen | Statusübergänge, Freigaberegeln, Statistikdefinitionen und spätere Module bleiben fachlich zu entscheiden |
| 14.08.2026 | Prozessdarstellung, Use Cases und Concept-Clean-Rückmeldung | Zwei belegungsbewusste Praxiswege und die freigegebene Kundenstimme mit Logo sind auf der Review-Seite vorhanden; Janay bestätigte am 10.09., dass die Darstellung soweit gut aussieht | Nur neue, konkret benannte Folgepunkte werden wieder geöffnet |
| 24.08.2026 | Aktivierung, Go-live-Nachweise, Backup/Restore und Eingangssteuerung | Release-, Backup-, Monitoring-, Transfer- und Restore-Proben sind mit synthetischen Daten abgeschlossen | Produktive Zeitplanung/Alarmierung, App-DNS, SMTP, Legal, benannte Konten und Go/No-Go bleiben offen |
| 27.08.2026 | Leistungsstruktur, Hub-Navigation, Coaches, Formulare, Assessment Center und Kalenderideen | Freigegebene Frontend-Korrekturen sind auf der Review-Seite umgesetzt; CAL-0 wurde review-deployed und am 10.09. akzeptiert | EDV-Daten sperren die echte Formularzustellung; fachliche Entscheidungen und ADR 0007 sperren produktive Kalender-/Reservierungsschritte |
| 04.09.2026 | Use Cases nebeneinander und aufklappbar; weniger Scrollen bei 150 Prozent | Beide Use Cases sind kompakt, unabhängig aufklappbar, review-deployed und von Janay am 10.09. als soweit gut bestätigt | Kein offener Punkt aus diesem Paket |
| 10.09.2026 | Coachprofil-Verlinkung, öffentliche Vorträge, persönlicher Coachkalender, Wochenendüberschneidungen und interne Freigabe | CAL-0.1 ist review-deployed; CAL-1-Rollenanforderungen sind dokumentiert und Janay ist als initiale fachliche Freigabeownerin bestätigt | CAL-0.1-Abnahme offen; persönlicher Kalender bleibt bis RBAC/Webapp-Umsetzung gesperrt; Vertretung, Benachrichtigungskanal und Terminveröffentlichungsregeln offen |

## Kalender-Lieferweg

Der Kalender ist ein eigener aktiver Discovery- und Prototyping-Strang und wird
nicht mit der öffentlichen Website oder einer produktiven Buchung vermischt.

1. **Visuelle Validierung:** CAL-0 und CAL-0.1 prüfen Kalender, Themen,
   Coachprofil-Verlinkung, Wochenendüberschneidungen und Vormerkungsablauf ohne
   Speicherung oder echte Verfügbarkeit.
2. **Coach-Verfügbarkeit:** CAL-1 führt den persönlichen Pflegekalender hinter
   dem Coach-Login sowie interne Prüfung und kontrollierte Veröffentlichung ein.
3. **Verfügbarkeit und Reservierung:** CAL-2/CAL-3 ergänzen freigegebene
   Zeitfenster und Gruppenplätze. Der Vorschlag von mindestens 25 Teilnehmenden
   ist bis zur fachlichen und vertraglichen Freigabe keine feste Regel.
4. **Bestätigte Termine:** CAL-4 erzeugt standardkonforme `.ics`-Einladungen,
   die in Outlook und mindestens einem Nicht-Outlook-Kalender funktionieren,
   eine stabile Ereignis-ID nutzen und Aktualisierung sowie Absage ohne
   Duplikate unterstützen.
5. **Optionale Outlook-Anbindung:** Eine direkte Microsoft-Graph-Synchronisation
   folgt nur bei belegtem Bedarf und nach Freigabe von Tenant-Administration,
   OAuth-Rechten, Datenschutz, Token-Verwahrung, Monitoring und Support.

## Kalender-Gates und Abnahme

- Fachlich: führender Termindatensatz, Ersteller, Status, Zeitzone, Ort oder
  Meeting-Link, Änderungs- und Absageregeln festlegen.
- Datenschutz: keine internen Notizen, Kundenidentitäten oder unnötigen
  personenbezogenen Daten in Einladungen oder öffentlichen Verfügbarkeiten.
- Rechte: festlegen, wer Termine erstellt, freigibt, ändert, absagt und
  Verfügbarkeiten veröffentlicht.
- Betrieb: Zustellfehler müssen für berechtigte Mitarbeitende sichtbar sein;
  Verantwortliche für Monitoring und Support müssen benannt sein.
- Test: Import in Outlook und einen weiteren Kalender, Update/Absage ohne
  Duplikat, Zeitzonen-/Sommerzeittest und Prüfung auf Datenminimierung.

## Nächste Verwendung

Der Abgleich ist bei jedem neuen Stakeholder-Paket zu aktualisieren. Ein Punkt
darf nur von `offen` auf `umgesetzt` wechseln, wenn die zugehörige Abnahme oder
das benannte Gate nachgewiesen ist.
