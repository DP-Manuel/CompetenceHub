# Competence Hub: Feedback und gemeinsame Abnahme

**Stand 20.11.2026.** Grundlage: `Quellen/20261119/Feedback.docx` mit vier
Screenshots; Original unverändert. Die 19.11 erteilte Profilfreigabe betrifft
die acht bereits aktiven Profile und ihre bestehenden Inhalte. Sie schließt
weder Frau Hupp noch offene Angebotskandidaten oder Frau Rappelts künftiges
Profil ein. Die Freigabe des tatsächlichen IONOS-Uploads bleibt separat.

## Feedback Und Prüfnachweis

| Feedback | Umsetzung | Prüfung / fachliche Grenze |
| --- | --- | --- |
| Bild 1: Trennlinie zu dicht | Schwabauers Angebotsliste mit Abstand und klarer Gruppierung | Sichtprüfung an der genannten Überschrift, schmal und breit |
| Bild 2: Rhetorik und Vertrieb liefert nichts | Bestehende belegte Angebote und Themenzuordnungen korrigiert | Finder-Kombinationen und Zurücksetzen; keine erfundenen Angebote |
| Bilder 3 und 4: geschlossene Angebotsgruppen, psychologische Schwerpunkte | Erste Gruppe sichtbar; Schwerpunkte und passende Angebote auf demselben Profil verbunden | Profil ohne Öffnen aller Gruppen verständlich; psychologische Angebote bleiben fachlich vom Coaching abgegrenzt |
| Namen, Profile und Frau Rappelt | Coach-Namen verlinkt, acht aktive Profile im lokalen Produktionskandidaten, Anrede vereinheitlicht | Keine Reaktivierung von Frau Hupp; kein neues Profil von Frau Rappelt. Später: Personalvermittlung |
| Aktuelle Termine und Coachprofil | Maximal fünf veröffentlichte Termine, Datum, Format, Ort, Preishinweis und Link zum selben Kalendereintrag | Lokale anonyme Projektion mit Testdaten. Statische Profile und Kalender zeigen ohne freigegebene Daten einen Leerzustand, keine privaten Portalabfragen. Alte Beispieldaten nur im ausdrücklichen Preview-Prototyp |
| Umkreissuche | Name/PLZ-Alias eines bekannten Orts und frei wählbarer Radius, Entfernung als Luftlinie | Nur Präsenz/Hybrid mit eindeutig zugeordnetem Ort; synthetischer Nachweis. Kein realer Ortsbestand und kein Geocoder freigegeben |
| Plätze, Preis und Newsletter | Text plus Farbe für Platzstatus; freigegebener Preishinweis und Frist in wiederverwendbarer Projektion | CAL-2-Platzbindung zählt nur in der lokalen Demo. Keine verbindliche Buchung, keine veröffentlichte Preisliste und kein Versand |
| Seminareditor und Rückantwort | Basis und Zeitangaben getrennt; Beschreibung optional und mit Absätzen; Reviewer-Hinweis nur in der passenden Entscheidung | Uhrzeiten vor Speichern weiter valide; vorhandene Grenze von 1.200 Zeichen bleibt. Keine neue Reviewer-Autorenschaft oder Selbstfreigabe. Faktenhierarchie inspiriert vom [Benediktushof-Kursdetail](https://www.benediktushof-holzkirchen.de/kategorie/kw/bereich/kursdetails/kurs/27PK02/kursname/NEU%20BUCHBAR%20Zen%20und%20die%20Kunst%20der%20KI/) |
| Führung durch das Portal | Stabile Ziele, sequenzielle Schritte und Fokusrückgabe für die vier Rollen | Desktop und Smartphone; Überspringen und erneuter Start |
| Firmen- und Privatkunden | Separates Privatkundenregister, optionale Anschrift; Firma erhält optionale Geschäfts-/Rechnungsanschrift und USt-IdNr. | Intern/Admin; Firmen- und Kontozuordnung unverändert. Siehe [Kundenvertrag](../requirements/customer-administration-local.md) |

## Vorführung

Ein PowerShell-Fenster, Docker Desktop (Linux) mit dem vorhandenen PostgreSQL-16
Image sowie die Projektumgebungen für Astro, Python und Firefox:

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp'
.\.venv\Scripts\python.exe scripts/run-cal2-local.py
```

Bei `V2_PLATFORM=READY` sind die fünf synthetischen Rollenfenster offen.
Keine echten Zugangsdaten eingeben oder teilen.

1. Im Website-Tab einen Coach-Namen öffnen; in Schwabauers Profil Schwerpunkte,
   erste Angebotsgruppe, Trennlinien und Rückweg prüfen. Im Finder „Rhetorik &
   Vertrieb“ filtern, ein zweites Thema wählen und den Filter zurücksetzen.
2. Als Demo-Coach einen Workshop mit Format Präsenz, Ort `Demo-Ort A`, Beginn
   in acht Tagen, fünf Plätzen und Prüfschwelle drei erfassen. Uhrzeiten im
   Zeitabschnitt eingeben; Kurztext optional ergänzen. Speichern und einreichen.
3. Als Reviewer veröffentlichen. Im Website-Tab auf „Aktuelle Termine“
   zurückgehen und neu laden, nach `Demo-Ort A` im 20-km-Radius suchen.
   Termin öffnen, zugehöriges Profil und Rücklink zum Termin prüfen.
4. Im Firmenfenster zwei Plätze vormerken. Die zweite Firma versucht vier
   weitere Plätze; das Portal weist den Versuch ab. Reviewer stellt der
   ersten Firma eine Rückfrage; diese antwortet und sieht die Entscheidung.
5. Als Admin unter Kunden einen fiktiven Privatkunden nur mit Namen anlegen.
   Danach bei einer bestehenden Demo-Firma die optionalen Zusatzangaben öffnen.
   Firmenkonten erhalten dadurch keine neuen Rechte.
6. Jede Rolle startet die Einführung, geht vor und zurück, überspringt oder
   startet erneut. Auf einem schmalen Fenster und mit Tastatur ausprobieren.
   **R + Enter** startet die Demo mit Datenpersistenz neu. **Enter** beendet
   sie; `CAL2_CLEANUP=PASS` bestätigt die Bereinigung.

## Offene Entscheidungen

- Für echte Termine: bestätigte Beziehung zwischen Coach, konkreter
  Angebotsvariante und Termin sowie verifizierte Veranstaltungsorte. Kein
  Matching über ähnlich klingende Namen, Titel oder Anschriften.
- Preise: freigegebene Coach-Einstufung, internes Honorar und öffentlicher
  Verkaufspreis pro Person/Gruppe getrennt liefern. Kein bestätigter
  öffentlicher Tarif für „Expert“ gefunden.
- Für Termine mit Vormerkungen bleiben die bisherigen Revisions- und
  Fristregeln bestehen. Vor Echtbetrieb Platzbindung und künftige
  Benachrichtigungen bestätigen. Keine Selbstfreigabe als Reviewer einführen.
- Für echte Privatkundendaten Zweck, Aufbewahrung und Löschweg festlegen.
  Echte Konten, Newsletter-Empfänger, Rechnungen und Zahlungen bleiben aus.

## Betrieb

Zwei getrennte Kandidaten: statische Website und
[geschütztes VPS-Paket](../operations/portal-v2-private-staging.md). Letzter
belegter privater VPS-Stand: V1.2 mit `0006`; Pilotzertifikat bis
30.11.2026, 19:09:39 MEZ. Erst nach gesonderter Freigabe und aktueller Prüfung
von TLS, Diensten und Wiederherstellbarkeit käme `0007`–`0012` auf einen
getrennten synthetischen Klon. App-Domain, dauerhaftes HTTPS und SMTP sind
für echte Zugänge weiter offen.

## Nachweis Und Releasepakete

- **34 integrierte Nachweise** mit Firefox und nativem PostgreSQL auf exakt
  `b9b90bfb88852a9dcffb5c1e78595340551b5b11`: Website und Kalender, 390 px,
  nativer 200-%-Zoom, CSRF/Rollen, konkurrierende Vormerkungen und
  Kundenpersistenz. Keine externen Browserzugriffe und keine Outbox-Einträge;
  eigener Container und Volume entfernt.
- **112 gezielte Portaltests**, darunter Rollen-Touren, Editor, Preis-/Orts-
  und Kundenvertrag; **41 Website-Tests**; **acht Website-Browserabläufe**
  (Produktion und Preview, Desktop, 390 px, ohne JavaScript und nativer 200-%-
  Zoom). 1.641 interne Produktionsreferenzen geprüft. Kein separater
  Screenreader-Durchlauf.
- **Sechs lokale Linux-/Klonprüfungen** einschließlich atomarem
  Migrationsrollback und unveränderter Ausgangsdatenbank. Das exakte
  VPS-ZIP wurde unabhängig offline installiert, ohne einen Dienst zu starten.

Beide Pakete liegen lokal unter
`release-artifacts/feedback-platform/b9b90bfb88852a9dcffb5c1e78595340551b5b11/`.
Der abschließende reine Dokumentationscommit ändert keine Paketbytes.

| Paket | Prüfsumme SHA-256 |
| --- | --- |
| `website/competence-hub-website-b9b90bfb8885-20261120T150236Z.zip` (64 Dateien, acht aktive Profile, keine Testtermine) | `e02b574bcb57844b69c9422b3517545d1ddc3811f0af0e101f0124f704b6fe2c` |
| `private-vps/competence-hub-private-v2-b9b90bfb88852a9dcffb5c1e78595340551b5b11.zip` | `0f3365ba9c32e04db331468dcaab9fa2210744f6467e54180c559d621b8174af` |
| `tested-source.json` | `d534bdcbf8a687b88afadceab7466e3f718c31bc418dc7056e8c222504213797` |

GitHub Pages bleibt auf Workflow `44149446991` / Quelle `11cb1ea`;
der Push löst diesen manuell gestarteten Workflow nicht aus. Keine
IONOS-/VPS-Installation, echte Datenmigration, GPG-/USB-Arbeit oder
Aktivierung echter Konten.

**Nächster Block:** Manuel und Frau Rappelt nehmen die sechs Schritte gemeinsam
ab. Eingaben: lokale Demo und diese Liste. Erledigt, sobald beide die
Nutzerwege, Abweichungen und offenen Geschäftsregeln protokolliert haben und
für Website und geschützten VPS separat über die Freigabe entscheiden können.
