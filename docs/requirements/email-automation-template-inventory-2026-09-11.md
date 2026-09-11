# E-Mail-Automation: Vorlagen- und Gate-Inventar

Stand: 11.09.2026

Quelle: von Manuel freigegebener Entwurf
`Quellen/11.09.2026/E-Mail-Vorlagen Beratung & Schulungen.docx`.
Die private Word-Datei und ihre Gestaltung bleiben außerhalb von Git. Dieses
Inventar übernimmt nur Prozesszweck, Risiken und benötigte Entscheidungen.

Status: fachlicher Ideengeber; keine Vorlage ist für automatischen Versand,
rechtliche Wirkung oder Produktion freigegeben.

## Prozessinventar

| ID | Zweck | Sinnvolles späteres Ereignis | Offene Gates vor Automatisierung |
| --- | --- | --- | --- |
| MAIL-01 | Eingangsbestätigung Beratung | Anfrage technisch angenommen | Empfänger, Datenschutz, Mailboxrouting und belastbare Reaktionsregel; `1-2 Werktage` ist derzeit nicht freigegeben |
| MAIL-02 | Vormerkung bei noch offenem Angebot | Unverbindliche Vormerkung gespeichert | Wortlaut darf keinen reservierten oder gebuchten Platz vortäuschen; Schwelle/Kapazität und Vertragsgrenze |
| MAIL-03 | Durchführung bestätigt | Interne Freigabe und verbindliche Bestätigung | Wer darf garantieren, ab wann ist es verbindlich, welche Vertrags-/Stornoregel gilt |
| MAIL-04 | Termin-Erinnerung | Freigegebener Termin nähert sich | Versandzeitpunkt, Zeitzone, Datenminimierung, Zugangslink und Zustellfehler |
| MAIL-05 | Teilnahme-Nachbereitung | Termin abgeschlossen | Feedback-Rechtsgrundlage, Linkziel, Aufbewahrung; Newsletter nur mit eigenem Einwilligungsprozess |
| MAIL-06 | Firmenkunden-Nachbereitung | B2B-Termin abgeschlossen | Freigegebene Leistungsfelder und Wirkungsaussagen; Feedback- und Vertriebsfreigabe |
| MAIL-07 | Schwelle noch nicht erreicht | Status bleibt unverbindlich | Abgrenzung Warteliste/Vormerkung/Reservierung, Informationsrhythmus und Ablaufdatum |
| MAIL-08A | Terminverschiebung | Termin wesentlich geändert | Erneute Zustimmung versus automatische Übernahme, kostenfreie Stornierung und Kalender-Update |
| MAIL-08B | Veranstaltungsabsage | Termin abgesagt | Absagegrund, Erstattungsanspruch/-prozess, Verantwortliche und Kalender-Storno |
| MAIL-09 | Individuelles Angebot | Angebot freigegeben und versendet | Dokumentquelle, Angebotsnummer, Gültigkeit und rechtlich bindender Annahmekanal; E-Mail-Freigabe nicht ungeprüft festlegen |
| MAIL-10 | Angebotsnachfassung | Freigegebene Wiedervorlage erreicht | Frequenz, Stop-Regeln, Zuständigkeit, Tracking/Datenschutz und Buchungslink |
| MAIL-11 | Teilnahmebescheinigung | Teilnahme fachlich bestätigt | Aussteller, Nachweisdaten, Freigabe, sichere PDF-Erzeugung und Zustellung |
| MAIL-12 | Empfehlung/Incentive | Separat freigegebenes Empfehlungsprogramm | Vorteil, Bedingungen, Steuer/Recht, Missbrauchsschutz und Marketingeinwilligung |

## Querschnittsanforderungen

- Jede Nachricht besitzt einen eindeutigen fachlichen Auslöser, Empfänger,
  verantwortlichen Owner und idempotenten Versanddatensatz.
- Ein Versandfehler ist intern sichtbar und retrybar; Erfolg wird erst nach
  bestätigter Übergabe an den Mailadapter protokolliert.
- Personenbezogene Daten, Tokens und vertrauliche Notizen erscheinen weder in
  Betreff, URL, Logs noch Audit-Payloads.
- Transaktionale Nachricht, Marketing/Newsletter und rechtlich relevante
  Erklärung werden als getrennte Zwecke und Einwilligungs-/Nachweiswege geführt.
- Platzvormerkung, Warteliste, Reservierung, Buchung und Vertrag dürfen in Text
  und Statusmodell nicht synonym verwendet werden.
- Platzhalter werden vor Versand vollständig und typisiert aufgelöst; ein
  fehlender Pflichtwert stoppt die Nachricht statt Rohplatzhalter zu versenden.
- Terminänderungen und Absagen verwenden dieselbe Kalender-UID wie die
  ursprüngliche Einladung.
- Texte, Absender, Reply-To, Impressumspflichten, Aufbewahrung und Löschung
  benötigen vor Produktion fachliche sowie rechtliche Freigabe.

## Empfohlene Inkremente

1. **MAIL-0:** Kanonisches Ereignis-/Vorlageninventar, Statusbegriffe,
   Platzhaltervertrag und Preview ohne Versand.
2. **MAIL-1:** Rein interne Backup-Erfolgs-/Störungsmeldung an Manuel als
   kanalneutraler Betriebsnachweis.
3. **MAIL-2:** Transaktionale Eingangsbestätigung ohne Reaktionsversprechen,
   sobald Kontaktformular, Datenschutz, Mailbox und SMTP freigegeben sind.
4. **MAIL-3:** Kalenderbezogene Vormerkungs-, Bestätigungs-, Änderungs- und
   Absagemails nach CAL-2 bis CAL-4.
5. **MAIL-4:** Angebote, Teilnahmebescheinigungen, Feedback, Newsletter und
   Empfehlungen jeweils als eigene, später freizugebende Epics.

## Nächste Entscheidungen

1. Welche Vorlagen gehören wirklich zum ersten Pilotumfang?
2. Welche Statusbegriffe sind fachlich und vertraglich verbindlich?
3. Wer gibt Antwortzeit, Durchführung, Umbuchung, Storno und Erstattung frei?
4. Welche Nachrichten sind rein transaktional, welche Marketing?
5. Wer verantwortet Text, Absender, Reply-To und Freigabedatum je Vorlage?
