# Coach-Verfügbarkeitskalender v0.1

Stand: 10.09.2026

Status: Produktwunsch bestätigt; visueller Prototyp freigegeben, fachliche
Regeln und produktive Umsetzung noch nicht freigegeben.

## Quelle und Ziel

Grundlage sind Janays Notizen vom 27.08.2026 und ihre positive Website-Abnahme
mit erneutem Kalenderwunsch vom 10.09.2026. Der Kalender soll verfügbare
Coach-Angebote bis zu drei Monate im Voraus sichtbar machen, nach Themen
unterscheiden und unverbindliche Platzvormerkungen ermöglichen. Eine interne
Prüfung trennt Vormerkung und verbindliche Buchung.

Die private Word-Datei bleibt außerhalb von Git. Dieses Dokument übernimmt nur
die für Produktentscheidung, Architektur und Test notwendigen Aussagen.

## Inkremente

| Inkrement | Ergebnis | Status |
| --- | --- | --- |
| CAL-0 | Interaktive, crawler-gesperrte Website-Vorschau mit ausschließlich synthetischen Terminen | umgesetzt, geprüft und review-deployed; Stakeholder-Abnahme offen |
| CAL-1 | Coach pflegt eigene Verfügbarkeit in einem rollierenden Drei-Monats-Fenster; intern wird geprüft und veröffentlicht | geplant; benötigt Coach-Konten, RBAC und Statusmodell |
| CAL-2 | Unternehmen oder Personen sehen veröffentlichte Angebote und merken begrenzt Plätze vor | geplant; benötigt Zugangs-, Datenschutz-, Ablauf- und Missbrauchsschutzentscheidung |
| CAL-3 | Schwellenwert löst interne Prüfung aus; nur Berechtigte geben ein verbindliches Angebot frei | geplant; benötigt Geschäftsregel, Benachrichtigung und Vertragsprozess |
| CAL-4 | Anbieterneutrale `.ics`-Einladung für einen intern bestätigten Termin | geplant; benötigt führenden Termindatensatz und Versandentscheidung |

CAL-0 dient nur der visuellen und fachlichen Abstimmung. Es speichert nichts,
versendet nichts und zeigt keine echte Coach-Verfügbarkeit.

## Funktionale Anforderungen

- **CAL-FR-001:** Das System soll höchstens ein konfigurierbares rollierendes
  Planungsfenster anzeigen; der Arbeitswert beträgt drei Monate.
- **CAL-FR-002:** Ein veröffentlichter Termin soll Datum, Uhrzeit, Thema,
  Format, Coachanzeige, Kapazität und Lebenszyklusstatus besitzen.
- **CAL-FR-003:** Themen sollen per Text und Farbe unterscheidbar sein; Farbe
  darf nie das einzige Unterscheidungsmerkmal sein.
- **CAL-FR-004:** Coaches sollen später nur eigene Verfügbarkeiten anlegen und
  ändern dürfen; interne Rollen dürfen sie prüfen und veröffentlichen.
- **CAL-FR-005:** Sichtbare Interessierte sollen eine begrenzte Zahl von
  Plätzen unverbindlich vormerken können, ohne dass daraus automatisch ein
  Vertrag entsteht.
- **CAL-FR-006:** Gleichzeitige Vormerkungen dürfen die freigegebene Kapazität
  nicht überschreiten.
- **CAL-FR-007:** Das Erreichen eines je Angebot konfigurierten Schwellenwerts
  soll eine interne Prüfung auslösen. Der Vorschlag `25` ist kein globaler
  Festwert.
- **CAL-FR-008:** Nur eine freigegebene interne Rolle darf aus einem geprüften
  Angebot einen verbindlich buchbaren Zustand machen.
- **CAL-FR-009:** Änderungen und Absagen bestätigter Termine sollen dieselbe
  stabile Kalenderereignis-ID verwenden und keine Duplikate erzeugen.
- **CAL-FR-010:** Zustellfehler von Kalendereinladungen müssen intern sichtbar
  sein und dürfen keinen erfolgreichen Versand vortäuschen.

## Sicherheits- und Datenschutzanforderungen

- Öffentliche Verfügbarkeit enthält keine fremden Kundennamen, internen Notizen
  oder privaten Kalenderdetails eines Coaches.
- Reservierungsdaten sind personenbezogen und werden nur nach freigegebenem
  Zweck, Pflichtfeldsatz, Datenschutzhinweis, Aufbewahrung und Löschweg erhoben.
- Lese- und Schreibrechte werden serverseitig und deny-by-default geprüft.
- Kapazität und Status werden transaktional geändert; die UI allein ist keine
  Schutzgrenze gegen Überbuchung.
- Jede Veröffentlichung, relevante Statusänderung, interne Freigabe und
  Stornierung wird ohne vertraulichen Rohpayload auditiert.
- Der öffentliche Endpunkt benötigt Rate Limit, CSRF-/Origin-Konzept oder eine
  begründete Alternative sowie Schutz gegen automatisierte Massenreservierung.

## Offene Entscheidungen vor CAL-1 bis CAL-4

1. **CAL-D01:** Ist die Sichtung öffentlich, nur nach Firmenlogin oder in beiden Varianten
   vorgesehen, und dürfen Privatpersonen Plätze vormerken?
2. **CAL-D02:** Bedeutet `25` Mindestgruppengröße, interner Prüfschwellenwert oder Kapazität;
   gilt der Wert je Format und wer darf ihn ändern?
3. **CAL-D03:** Wie lange bleibt eine Vormerkung gültig, wer darf sie ändern/stornieren und
   was passiert bei Kapazitätsänderung oder zu wenigen Interessierten?
4. **CAL-D04:** Welche Kontaktangaben sind für eine Vormerkung zwingend und wann wird eine
   Firma beziehungsweise Person im Portal angelegt?
5. **CAL-D05:** Welche Themen bilden die verbindliche Taxonomie und welche Farbe ist ihnen
   barrierefrei zugeordnet?
6. **CAL-D06:** Wer erhält die Schwellenwertmeldung, über welchen Kanal und mit welcher
   Vertretungsregel?
7. **CAL-D07:** Wann darf der Coachname öffentlich erscheinen, und welche Freigabe gilt für
   Termine, Profil, Ort, Preis und Format?
8. **CAL-D08:** Welcher Datensatz ist führend für den bestätigten Termin und wer ist
   organisatorischer Absender der `.ics`-Einladung?

## Abnahmekriterien CAL-0

- Der Prototyp zeigt genau drei aufeinanderfolgende Monate.
- Themen lassen sich per Tastatur und sichtbarem Text filtern.
- Monatsschalter verlassen das Drei-Monats-Fenster nicht.
- Ein Beispieltermin zeigt Details, Vormerkungsstand und eine lokale
  Platzsimulation; Neuladen hinterlässt keine Daten.
- Alle Namen und Termine sind sichtbar als Beispiele gekennzeichnet.
- Bei 390 Pixeln gibt es keine Dokumentüberbreite; Fokus, Kontrast und Status
  sind ohne reine Farbcodierung verständlich.
- Die Route ist `noindex` und wird nicht als produktiver Kalender verlinkt.

## Definition of Done für den ersten produktiven Slice

Die acht Entscheidungen sind freigegeben oder explizit verschoben, ADR 0007
ist angenommen, Datenmodell/API/RBAC und Migration sind geprüft und
synthetische Nebenläufigkeits- und Berechtigungstests sind grün. Sobald CAL-4
in den freigegebenen Umfang gelangt, funktioniert der Kalenderimport in Outlook
und mindestens einem Nicht-Outlook-Client. Weder echte Daten noch produktive
Zustellung werden vor den bestehenden Betriebs- und Legal-Gates aktiviert.
