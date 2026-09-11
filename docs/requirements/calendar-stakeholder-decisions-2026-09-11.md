# Fachentscheidungen zum Coach-Kalender

Stand: 11.09.2026

Quelle: von Manuel freigegebener Rücklauf aus
`Quellen/11.09.2026/Competence-Hub_Fachliche-Abstimmung-Coach-Kalender_2026-09-11.docx`.
Die private Word-Datei bleibt außerhalb von Git. Dieses Dokument übernimmt nur
die für Anforderungen, Architektur und Tests erforderlichen Entscheidungen.

Status: CAL-D01 bis CAL-D08 und der vorgeschlagene Pilotablauf wurden von Janay
jeweils mit `Passt so` bestätigt. Die Fachfreigabe autorisiert weder Migration,
Echtdaten, Konten, Nachrichtenversand noch Produktion.

## Entscheidungen

| ID | Freigegebene Regel | Folge für den ersten Pilot |
| --- | --- | --- |
| CAL-D01 | Angebote sind öffentlich sichtbar. Nur angemeldete Firmenkontakte dürfen Plätze vormerken. Privatpersonen und nicht angemeldete Interessierte nutzen den Kontaktweg. | Öffentliche Lese- und authentifizierte Firmen-Schreibpfade bleiben technisch getrennt. |
| CAL-D02 | `25` ist ein je Angebot änderbarer interner Prüfschwellenwert. Die Höchstkapazität wird separat je Angebot festgelegt. | Schwellenwert und Kapazität sind getrennte, nicht global hart codierte Werte. |
| CAL-D03 | Jedes Angebot besitzt eine sichtbare Entscheidungsfrist. Vormerkungen können bis zur internen Entscheidung zurückgenommen werden. Änderungen, Absagen und geänderte Platzzahlen lösen Informationen aus. Eine Vormerkung ist kein Vertrag. | Frist, Rücknahme und Benachrichtigungsereignisse gehören zum Statusmodell; Vertragsstatus bleibt getrennt. |
| CAL-D04 | Im Firmenpilot werden bestehende Firmen- und Kontaktdaten verwendet. Zusätzlich sind gewünschte Platzzahl und Bestätigung der Kontaktperson nötig; Telefonnummer und Nachricht bleiben freiwillig. | Kein doppelter Kontaktdatensatz und kein unnötiges Pflichtfeld. |
| CAL-D05 | Der Pilot startet mit wenigen kontrollierten Oberthemen aus freigegebenen Coach-Schwerpunkten. Janay prüft Bezeichnung und Zuordnung; freie Themeneingabe ist nicht vorgesehen. | Themen erhalten eine verwaltete Taxonomie und Freigabestatus. |
| CAL-D06 | Janay erhält eine Portalaufgabe und zusätzlich eine E-Mail. Eine spätere Vertretung arbeitet ausschließlich mit eigenem Zugang. | Janay ist initiale fachliche Ownerin; aktuell ist keine Vertretung benannt. Zustellung wartet auf das Mail-Gate. |
| CAL-D07 | Coach, Thema, Datum, Uhrzeit, Format, Ort/Online-Angabe, Platzzahl sowie Preis oder Preishinweis werden vor Veröffentlichung geprüft. Nur ausdrücklich freigegebene Angaben erscheinen öffentlich. | Veröffentlichung benötigt einen vollständigen, auditierten Prüfentscheid. |
| CAL-D08 | Der bestätigte Termin wird zentral im Competence Hub geführt. Teilnehmende und Coach erhalten eine anbieterneutrale Kalendereinladung; direkte Outlook-Anbindung bleibt optional für später. | Competence Hub ist führend; `.ics` ist der erste Zustellweg, Microsoft Graph ein eigenes späteres Gate. |

## Freigegebener Ablauf

1. Coaches tragen eigene Angebote und Verfügbarkeiten ein.
2. Janay oder eine später benannte Vertretung prüft und veröffentlicht mit
   persönlichem Zugang.
3. Angemeldete Firmenkontakte melden unverbindlich Interesse und Platzzahl an.
4. Beim angebotsspezifischen Schwellenwert erhält Janay eine interne Aufgabe
   und E-Mail und klärt das weitere Vorgehen.
5. Erst nach ausdrücklicher Bestätigung werden Termin und Kalendereinladung
   verbindlich versendet.

## Verbleibende Gates

- ADR 0007 benötigt Manuels ausdrückliche Architekturfreigabe.
- Thema, Statusmodell, Rechte, API und Datenmodell benötigen technischen Review.
- Migration auf Staging benötigt eine separate Freigabe und Rollback-Smoke.
- Mailzustellung benötigt EDV-/SMTP-Vertrag, Absender und Testzustellung.
- Datenschutz, Aufbewahrung und Löschweg müssen vor echten Vormerkungen
  freigegeben sein.
- Produktive Konten, echte Termine und Echtdaten bleiben separat gesperrt.
