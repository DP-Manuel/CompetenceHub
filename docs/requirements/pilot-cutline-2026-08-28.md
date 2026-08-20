# Competence Hub Pilot Cutline - 28.08.2026

Stand: 20.08.2026

Status: Von Manuel am 20.08.2026 als verbindliche Pilotgrenze freigegeben.
Technischer Umfang und synthetische Nachweise sind belastbar; die unten
markierten Organisations- und Produktionsgates benoetigen weiterhin ihre
benannte Freigabe oder Evidenz. Die Freigabe autorisiert keine Konten,
Echtdaten, DNS-/Serveraenderung oder Veroeffentlichung.

## Pilotziel

Am 28.08.2026 ist die kanonische oeffentliche Website ueber den freigegebenen
Produktionspfad erreichbar. Frau Janay Rappelt kann sich mit einem persoenlichen,
MFA-geschuetzten Konto im getrennten Competence-Hub-Portal anmelden und eine
freigegebene Firma mit mindestens einem Geschaeftskontakt anlegen, wiederfinden,
lesen und in den erlaubten Feldern korrigieren. Jede Aenderung ist
datenminimiert auditiert und durch ein verifiziertes Backup wiederherstellbar.

Ein Datenbank-, API- oder UI-Teilerfolg allein erfuellt das Pilotziel nicht.

## Erste Nutzer und Rollen

| Person | Pilotrolle | Zweck | Loginidentitaet | Status/Gate |
| --- | --- | --- | --- | --- |
| Manuel | `admin` | technische Administration, Konten, Betrieb und Notfallreaktion | persoenliche D+P-Arbeitsadresse; final bestaetigen | Name/Rolle bestaetigt; Adresse und Nachfolge-/Break-glass-Regel offen |
| Frau Janay Rappelt | `internal` | Firmen und Kontakte erfassen und korrigieren | persoenliche D+P-Arbeitsadresse; final liefern | Name/Rolle bestaetigt; Adresse, Onboardingtermin und Vertretung offen |

`competencehub@donner-partner.de` bleibt die oeffentliche, von Frau Janay
Rappelt verantwortete Funktionsmailbox. Sie ist keine persoenliche
Authentifizierungsidentitaet und wird nicht von mehreren Personen als
Portal-Login geteilt.

Coach-, Firmenkontakt- und Teilnehmerkonten sind nicht Teil dieses Piloten.
Die Rollen bleiben im Datenmodell erhalten, erhalten aber keine realen Konten.

## Verbindlicher Fachumfang

### Unternehmen

- `name`: Pflichtfeld, maximal 200 Zeichen
- `industry`: optional, maximal 200 Zeichen
- `internal_notes`: optional, maximal 4.000 Zeichen; nur intern sichtbar
- `status`: serverseitiger technischer Startwert `prospect`; im Pilot nicht
  aenderbar und kein freigegebener Fachworkflow

### Geschaeftskontakt

- `first_name`, `last_name`, `email`: Pflichtfelder
- `phone`, `job_function`: optional
- mindestens ein Kontakt wird atomar mit der Firma angelegt
- weitere Kontakte koennen intern hinzugefuegt werden

### Pilotaktionen

- Firmen begrenzt nach Name suchen und als minimierte Liste anzeigen
- Firma mit Kontakten im Detail lesen
- Firma samt erstem Kontakt atomar anlegen
- erlaubte Firmen- und Kontaktfelder gezielt korrigieren
- weitere Kontakte hinzufuegen
- jede Schreibaktion ohne fachlichen Payload auditieren
- keine physische Loeschung ueber API oder Runtime-Rolle

Rechtsname/Anzeigename-Trennung, Anschrift, Kundennummer,
Primaerkontaktkennzeichen, Dublettenbereinigung und finaler Statusworkflow
werden erst nach belegtem Arbeitsbedarf additiv entschieden.

## Nicht Teil des Piloten

- Coach- oder Firmenlogin
- Coachinganfragen, Matching, Verfuegbarkeiten oder Kundennennung an Coaches
- Angebote, Auftraege, Vertraege, Rechnungen oder Zahlungen
- Termine, Kalender oder Buchungssystem
- Feedback, Kundenstimmen oder Statistiken
- Dokumentgenerierung, E-Mail-Automation oder App/PWA
- Datenimport aus Excel oder privaten Rohquellen
- physische Loeschung, Massenbearbeitung oder Export
- finale Fachstatus und automatische Transitionen

## Abnahmekriterien

| ID | Kriterium | Nachweis |
| --- | --- | --- |
| PILOT-01 | Kanonische Website und Recht-/Kontaktpfade sind ueber HTTPS erreichbar | Domain-, TLS-, Redirect- und Kernrouten-Smoke |
| PILOT-02 | Portal und API laufen getrennt von Website und Chatbot | eigene systemd-Identitaet, Verzeichnis, Konfiguration, Ports und Logs |
| PILOT-03 | Manuel und Frau Janay Rappelt nutzen persoenliche Konten mit MFA | beaufsichtigtes Onboarding und Login/MFA-Smoke |
| PILOT-04 | `internal` kann Firma plus Erstkontakt anlegen, suchen, lesen und korrigieren | Browser-E2E gegen synthetische Daten, danach freigegebener Erstrecord |
| PILOT-05 | Unauthentifizierte, falsche Rollen sowie fehlende Origin/CSRF werden abgewiesen | negative API-/Browser-Tests ohne Datenleck |
| PILOT-06 | Listen enthalten keine internen Notizen; Audit enthaelt keine Kontakt- oder Notizpayloads | API-/SQL-Pruefung und Audit-Stichprobe |
| PILOT-07 | Doppeltes Absenden erzeugt nicht unbemerkt zwei Firmen | UI-Sperre plus E2E-Doppelklicktest; persistente Idempotenz bleibt Folgearbeit |
| PILOT-08 | Produktive Daten sind aus einer verschluesselten externen Kopie wiederherstellbar | Download zum D+P-Rechner in Wuerzburg und isolierter Restore aus genau dieser Kopie |
| PILOT-09 | Deployment und Rollback beeinflussen den Chatbot nicht | Vorher-/Nachher-Healthchecks, Ressourcen- und Logpruefung |
| PILOT-10 | Thomas Ross gibt den Produktionsweg frei; Fachseite akzeptiert den Janay-Workflow | dokumentiertes Go/No-Go mit Datum und offenen Restpunkten |

## Gate- und Owner-Matrix

| Gate | Owner/Freigabe | Erforderliche Evidenz | Status 20.08. |
| --- | --- | --- | --- |
| Fachlicher Pilotumfang | Manuel und Frau Janay Rappelt | diese Cutline und Feld-/Ablaufabnahme | vorgeschlagen; Janay-Abnahme offen |
| Konten und Rollen | Manuel | persoenliche Adressen, Rollenliste, Onboardingtermin, Break-glass-Regel | Namen/Rollen gesetzt; Details offen |
| Einladungszustellung | Manuel; Mailbetrieb nach D+P-Vorgabe | freigegebener Mailadapter oder separat security-gepruefter persoenlicher Uebergabeweg | offen; keine Tokenanzeige in API/Logs |
| Off-Server-Backup | Manuel | verschluesselter Download zum D+P-Rechner Wuerzburg plus Restoreprotokoll | Zielkandidat gesetzt; Verschluesselung/Zugriff/Restore offen |
| Website-Produktion | Thomas Ross | freigegebenes Artefakt, Rollbackkopie, Domain/TLS/Recht/Kontakt-Smoke | offen |
| Backend-Produktion | Thomas Ross; Betrieb Manuel | eigene Services, Secrets, Reverse Proxy, Monitoring, Rollback und Chatbot-Isolation | offen |
| Rechtlicher Betreiber | Lars Donner / finale Gesellschaft | finales Impressum, Datenschutz-/AGB-Anwendbarkeit und Vertragsbezug | Gesellschaft/Unterlagen offen |
| Echtdaten | Manuel plus rechtliche/fachliche Freigabe | G-DATA, G-SEC, G-OPS und G-PROD geschlossen | gesperrt |

## Vorgeschlagene technische Adressen

- Website: `https://competencehub.donner-partner.de`
- Portal und Pilot-API: `https://competencehub-app.donner-partner.de`
- spaetere reservierbare API-Origin: `https://competencehub-api.donner-partner.de`

Fuer den Pilot werden Portaldateien und `/api/v1/...` durch denselben getrennten
Competence-Hub-Dienst auf einer Origin ausgeliefert. Das reduziert CORS-,
Cookie-, CSRF- und TLS-Komplexitaet. Eine separate API-Origin bleibt eine
spaetere, eigens zu pruefende Skalierungsoption. Der App-Name bleibt Vorschlag,
bis DNS, Wildcard-TLS, Reverse-Proxy-Ziel und Freigabe durch Thomas Ross
bestaetigt sind. Zweistufige Namen wie
`app.competencehub.donner-partner.de` werden nicht vorausgesetzt, weil das
bestaetigte Wildcard-Zertifikat nur `*.donner-partner.de` abdeckt.

## Rueckwaertsplan

| Termin | Ergebnis/Gate |
| --- | --- |
| 20.08. | Firmen-/Kontakt-API mit 14/14 Staging-Pfaden versioniert; Pilot-Cutline vorgeschlagen |
| 21.08. | Feldcut und Same-Origin-Portalentscheidung akzeptiert; Runtime-/Portal-UI-Slice lokal mit 241 Tests gruen. Nutzeradressen, Einladungsweg, DNS-Owner und Backupnachweis bleiben offen |
| 24.08. | Portal-UI fuer Login/MFA und Firmenworkflow lokal barrierearm und E2E-geprueft |
| 25.08. | getrennte VPS-Dienste, Reverse Proxy und statisches Website-Artefakt in freigegebener Staging-/Releaseprobe |
| 26.08. | verschluesselter Off-Server-Dump und Restore aus Wuerzburg nachgewiesen; Konten vorbereitet |
| 27.08. | internes End-to-End, Sicherheits-/Rollback-Smoke und Go/No-Go mit Manuel, Janay und Thomas Ross |
| 28.08. | kontrollierte Freigabe, Produktions-Smoke und erster freigegebener Firmenrecord oder dokumentiertes No-Go ohne Echtdaten |

Der Plan ist eng. Der lokale technische Slice liegt vor, aber jede nicht bis
21.08. geschlossene Organisationsentscheidung reduziert den 28.08. auf
Website- oder synthetischen Portalbetrieb; Echtdaten werden nicht zugelassen,
um den Termin scheinbar zu halten.

## Unmittelbar benoetigte Entscheidungen

1. Persoenliche Arbeits-E-Mail fuer Manuels Admin- und Janays Intern-Konto.
2. Bestaetigung, dass die oben genannten Pilotfelder bis nach dem Erstrecord
   ausreichen.
3. Freigegebener Einladungsweg: D+P-/IONOS-SMTP oder separat gepruefter
   persoenlicher Uebergabeweg; kein externer SaaS-Provider.
4. Bestaetigung der vorgeschlagenen gemeinsamen App-Origin und des DNS-Owners.
5. Nachweis von Datentraegerverschluesselung und eingeschraenktem Zugriff am
   Wuerzburger Backuprechner sowie Termin fuer den Restore-Test.
6. Datum/Uhrzeit fuer Janays Onboarding und die Abnahme am 27.08.
7. Produktions-Go/No-Go-Termin mit Thomas Ross.
