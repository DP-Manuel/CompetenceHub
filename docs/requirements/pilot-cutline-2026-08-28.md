# Competence Hub Technical-Readiness Cutline - 28.08.2026

> Zeitplanhinweis vom 25.08.2026: Die technische 28.08.-Cutline bleibt als
> historischer Readiness-Meilenstein gueltig. Der in diesem Dokument genannte
> 25.09.-Produktivtermin ist aufgehoben; ein erster kleiner Pilot ist fruehestens
> fuer die zweite Oktoberhaelfte nach Manuels Rueckkehr vorgesehen. Das genaue
> Datum bleibt gate-abhaengig und offen.

Stand: 21.08.2026

Status: Von Manuel am 20.08.2026 als verbindliche Pilotgrenze freigegeben.
Technischer Umfang und synthetische Nachweise sind belastbar; die unten
markierten Organisations- und Produktionsgates benoetigen weiterhin ihre
benannte Freigabe oder Evidenz. Die Freigabe autorisiert keine Konten,
Echtdaten, DNS-/Serveraenderung oder Veroeffentlichung.

## Readiness-Ziel

Am 28.08.2026 sind die Vertraege voraussichtlich fertig und das technische
Produktionspaket soll weitgehend vorbereitet sein. Eine oeffentliche
Freigabe, reale Konten und der erste Firmenrecord duerfen danach erfolgen,
sobald Legal-, Backup-, DNS/Runtime- und Go/No-Go-Gates geschlossen sind.
Spaetester Produktivtermin ist 25.09.2026 vor Manuels dreiwoechiger Abwesenheit.

Ein Datenbank-, API- oder UI-Teilerfolg allein erfuellt das spaetere
Produktivziel nicht. Der 28.08. darf als Readiness-Meilenstein ohne Echtdaten
abgeschlossen werden, wenn verbleibende Gates mit Owner und Termin sichtbar
sind.

## Erste Nutzer und Rollen

| Person | Pilotrolle | Zweck | Loginidentitaet | Status/Gate |
| --- | --- | --- | --- | --- |
| Manuel | `admin` | technische Administration, Konten, Betrieb und Notfallreaktion | `roedel.kg@donner-partner.eu` | Name/Rolle/Adresse bestaetigt; Nachfolge-/Break-glass-Regel offen |
| Frau Janay Rappelt | `internal` | Firmen und Kontakte erfassen und korrigieren | `rappelt.wue@donner-partner.eu` | Name/Rolle/Adresse bestaetigt; Onboardingtermin und Vertretung offen |

`competencehub@donner-partner.de` bleibt die oeffentliche, von Frau Janay
Rappelt verantwortete Funktionsmailbox. Sie ist keine persoenliche
Authentifizierungsidentitaet und wird nicht von mehreren Personen als
Portal-Login geteilt.

`admin@competencehub.donner-partner.de` ist als technischer Weiterleitungsalias
zu Manuel vorgeschlagen. EDV muss Existenz, Mailrouting und Absendernutzung
separat bestaetigen. Der Alias ist kein Portal-Login. Einladungen werden per
E-Mail zugestellt; SMTP-Host, Port, TLS-Modus, Authentisierung und freigegebene
Absenderadresse sind noch zu liefern.

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

| Gate | Owner/Freigabe | Erforderliche Evidenz | Status 21.08. |
| --- | --- | --- | --- |
| Fachlicher Pilotumfang | Manuel und Frau Janay Rappelt | diese Cutline und Feld-/Ablaufabnahme | vorgeschlagen; Janay-Abnahme offen |
| Konten und Rollen | Manuel | persoenliche Adressen, Rollenliste, Onboardingtermin, Break-glass-Regel | Namen/Rollen/Adressen gesetzt; Termine und Notfallregel offen |
| Einladungszustellung | Manuel; Mailbetrieb nach D+P-Vorgabe | SMTP-Vertrag, freigegebener Absender und gepruefter Mailadapter | E-Mail entschieden; technische Mailparameter offen; keine Tokenanzeige in API/Logs |
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
| 21.08. | Same-Origin-Portal als `c1f4cc8` versioniert; 248 lokale Tests, 14/14 Staging-Pfade und BA-01 bis BA-17 gruen. Nutzeradressen, Einladungsweg, DNS-Owner, Backupnachweis und Abnahmetermine bleiben offen |
| 24.08. | Aktivierungsmatrix geschlossen; Runtime-/Worker-Paket fail-closed vorbereitet und lokal geprueft |
| 25.08. | getrennte VPS-Dienste, Reverse Proxy und statisches Website-Artefakt in freigegebener Staging-/Releaseprobe |
| 26.08. | verschluesselter Off-Server-Dump und Restore aus Wuerzburg nachgewiesen; Konten vorbereitet |
| 27.08. | internes End-to-End, Sicherheits-/Rollback-Smoke und Go/No-Go mit Manuel, Janay und Thomas Ross |
| 28.08. | technisches Readiness-Paket, Vertragsstand und dokumentierte Restgates; noch kein Echtdatenzwang |
| bis Mitte September | Legal-/Betreiberangaben, App-DNS/SMTP, Backup-Restore, Onboarding- und Go/No-Go-Termine schliessen |
| 25.09. | spaeteste kontrollierte Freigabe mit Produktions-Smoke und erstem freigegebenen Firmenrecord oder dokumentiertes No-Go ohne Echtdaten |

Der lokale technische Slice liegt vor. Der 28.08. ist bewusst ein
Readiness-Meilenstein; Echtdaten werden nicht zugelassen, um einen Termin
scheinbar zu halten. Wegen der erwarteten Legal-Informationen Mitte September
muessen technische Restarbeiten vorher weitgehend abgeschlossen sein.

## Unmittelbar benoetigte Entscheidungen

1. Bestaetigung, dass die oben genannten Pilotfelder bis nach dem Erstrecord
   ausreichen.
2. SMTP-Host, Port, TLS-Modus, Authentisierung, freigegebener Absender und
   Reply-To fuer E-Mail-Einladungen; kein externer SaaS-Provider.
3. Bestaetigung der vorgeschlagenen gemeinsamen App-Origin und des DNS-Owners.
4. Nachweis von Datentraegerverschluesselung und eingeschraenktem Zugriff am
   Wuerzburger Backuprechner sowie Termin fuer den Restore-Test.
5. Datum/Uhrzeit fuer Janays Onboarding nach dem 28.08.
6. Produktions-Go/No-Go-Termin mit Thomas Ross vor dem 25.09.
7. Finale Betreiber-/Rechtsangaben, erwartet bis Mitte September.
