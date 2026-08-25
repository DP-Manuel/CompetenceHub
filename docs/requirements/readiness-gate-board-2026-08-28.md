# Competence Hub Readiness Gate Board

Stand: 2026-08-25

## Ampel

| Ziel | Status | Einordnung | Naechster Beweis |
| --- | --- | --- | --- |
| Technisches Readiness-Paket bis 28.08.2026 | GRUEN TECHNISCH | Clean-Source Website-/Webapp-Pakete, Staging sowie externer Backup-/Restore-Beweis sind gruen. App-DNS/SMTP und Produktionsbetrieb bleiben separate externe Gates. | Gate-Stand am 28.08. bestaetigen; keine automatische Produktion |
| Erste freigegebene Firmen nach Vertragsabschluss | GELB | Datenmodell, geschuetzter Firmen-/Kontakt-Slice und synthetischer Restore sind bewiesen. Echtdaten bleiben bis Legal-, Konten-, Produktions- und Go/No-Go-Gate gesperrt. | Freigegebener Vertrag, benannte Konten und Betriebsfreigabe |
| Kontrollierter Produktionsstart | GELB / NEU TERMINIEREN | Der bisherige 25.09.2026-Termin ist aufgehoben. Ein erster kleiner Start ist fruehestens in der zweiten Oktoberhaelfte nach Manuels Rueckkehr vorgesehen; das exakte Datum ist offen. Alle Produktionsgates bleiben bindend. | EDV/Legal im September klaeren und bis 02.10. Onboarding-, Go/No-Go- und Pilottermin festlegen |
| Budget | UNBEKANNT | Im Projekt ist kein belastbarer Budgetrahmen dokumentiert. | Nur bei kostenpflichtigem Backup-, Mail- oder Hostingbedarf entscheiden |

`GELB` bedeutet hier: mit den vorhandenen Nachweisen erreichbar, aber von
offenen zeitkritischen Gates abhaengig. Es ist keine Produktionsfreigabe.

## Kanban

| DONE | READY / NEXT | WAITING EXTERNAL | BLOCKED UNTIL GATES CLOSE |
| --- | --- | --- | --- |
| Auth, MFA, Rollen und Firmen-/Kontakt-Slice lokal und auf Staging synthetisch bewiesen | Vertrauenswuerdigen SFTP-Host-Key belegen und danach Webroot nur lesend inventarisieren | EXT-01: App-DNS, TLS-/Proxy-Pfad, SMTP-Vertrag und Absender durch EDV; nicht vor 14.09. erwartet | Echtdaten und erster realer Firmenrecord |
| Portal-Browserabnahme BA-01 bis BA-17 abgeschlossen | Bei frueher EDV-Antwort: hostbezogene Konfiguration rendern und nativ validieren | EXT-02: Vertragsstand und fachliche Freigabe | Produktive Einladungs-E-Mails und reale Konten |
| Reproduzierbare Website- und Webapp-Artefaktvertraege vorhanden | Nach separater Verbindungsfreigabe: SFTP-Host-Key, `pwd` und vollstaendige Remote-Inventur nur lesend pruefen | EXT-03: Janay-Onboarding und Thomas-Ross-Go/No-Go terminieren | Oeffentliche Bewerbung und Produktions-Go-Live |
| Verschluesselter nativer Backup-/Monitorlauf, Guarded Pull und exakter externer Restore bestanden; Timer weiter disabled | Nach Inventur: gepinntes lokales SFTP-Rehearsal-Paket erzeugen | EXT-04: finaler Betreiber, Impressum und Rechtspruefung | Automatisierter Website-Replace oder Remote-Loeschung |
| Guarded Website-SFTP-Paket vorbereitet; keine Verbindung oder Freigabe eingebaut | Produktionszeitplan und Alarmweg fuer Backup/Monitor nach EDV-Mailklaerung festlegen | EXT-03: Janay-Onboarding und Thomas-Ross-Go/No-Go fuer zweite Oktoberhaelfte terminieren | Unternehmens-/personenbezogene Daten ohne aktivierten Backup-/Alarmbetrieb |
| Git-Checkpoint `ea276b9` auf `origin/main`; technischer Readiness-Nachweis gruen |  | EXT-06: Mailbox-Reaktion, Vertretung und Ownership mit Janay |  |

WIP-Regel: maximal ein technischer Ausfuehrungsblock gleichzeitig. Externe
Anfragen laufen parallel, erweitern aber nicht stillschweigend den Scope.

## Gate-Matrix

| Gate | Status | Owner | Spaetester sinnvoller Termin | Evidence / Abnahme | Wirkung bei offenem Gate |
| --- | --- | --- | --- | --- | --- |
| G-CODE: gepruefter Source-Checkpoint | DONE | Manuel | aktualisiert 25.08. | Commit `ea276b9`; Remote synchron | Kein neuer Release aus ungeprueftem Source |
| G-TEST: lokale und Staging-Qualitaet | DONE fuer aktuellen Slice | Manuel | aktualisiert 25.08. | 305 lokale Passes, 14 erwartete Staging-Skips, vorherige 14/14 Staging- und BA-01..17-Nachweise | Bei Codeaenderung Gate erneut pruefen |
| G-WEBSITE: statisches Produktionsartefakt | DONE lokal | Manuel | aktualisiert 25.08. | 38 Astro-Dateien ohne Diagnose, 28 Seiten, SHA-/Manifestvertrag | Noch kein SFTP-Upload |
| G-WEBAPP: reproduzierbares Runtime-Paket | DONE lokal | Manuel | aktualisiert 25.08. | Clean Commit `70e92ba`; 33 Eintraege, Restore-Tool enthalten, keine `.env`/`.tmp`, SHA-256 `1db54187...be766`; Wheel/ZIP, isolierte Installation und Fail-closed Runtime | Noch keine VPS-Aktivierung |
| G-BACKUP: verschluesselte externe Kopie plus Restore | DONE REHEARSAL | Manuel / Wuerzburg | erledigt 25.08.; quartalsweise nach Echtdatenstart | verschluesselter Satz und Monitor gruen; Guarded Pull; digest-gepinnter netzloser Restore mit 24 Tabellen; 12/12; null Klartext-/Containerrest; vier Dienste active | Produktions-Timer/Alarmierung bleibt G-OPS; andere Echtdaten-Gates gelten weiter |
| G-EDV: App-DNS/TLS/SMTP | WAITING UNTIL 14.09. | EDV | Antwort nicht vor 14.09. erwartet; Produktionsdatum folgt Rebaseline | DNS-/TLS-Preflight, Nginx-Check, autorisierter Einzelabsender und Testzustellung | Keine Live-Einladung, keine Webapp-Produktion |
| G-SFTP: bestaetigter Webroot und Rollbackkopie | WAITING APPROVAL | Manuel / Thomas Ross | vor Website-Go-Live | Gepruefter Host-Key, read-only Inventur, vollstaendige Vorabkopie mit Hashliste | Kein Website-Replace |
| G-CONTRACT: finaler Vertragsweg | WAITING | Lars Donner / Fachseite | Status im September klaeren; vor Fachabnahme | Freigegebener Vertragsstand und Prozess | Kein freigegebener erster Firmenprozess |
| G-LEGAL: Betreiber und Rechtstexte | WAITING | Lars Donner / Rechtspruefung | bis 02.10. klaeren; vor Go/No-Go abschliessen | Finaler Betreiber, Impressum und anwendbare Datenschutz-/AGB-Fassung | Kein beworbener Livegang |
| G-ACCOUNT: benannte Konten und MFA | WAITING | Manuel / Janay | Termin bis 02.10.; Durchfuehrung nach Manuels Rueckkehr | E-Mail-Einladung, MFA, Least-Privilege-Matrix, keine Shared Accounts | Kein realer Fachbetrieb |
| G-ACCEPT: Fachabnahme und Go/No-Go | WAITING | Janay / Thomas Ross | zweite Oktoberhaelfte; exaktes Datum offen | Janay-Walkthrough und dokumentiertes Go/No-Go mit Restpunkten | Keine Produktion |
| G-MAILBOX: Reaktion und Vertretung | WAITING | Janay / Manuel | im September klaeren; vor Go/No-Go abschliessen | Owner, Vertretung, Reaktionsweg und Testzustellung | Kein versprochenes Service-Level |

## Pull-Regel

1. Read-only SFTP-Inventur erst nach vertrauenswuerdigem Host-Key-Nachweis oder
   ausdruecklich akzeptiertem Trust-Verfahren; keine Remote-Aenderung.
2. Trifft EXT-01 vorher ein, wird stattdessen die hostbezogene Konfiguration
   gerendert und validiert.
3. Liegt eine ausdrueckliche SFTP-Verbindungsfreigabe plus vertrauenswuerdiger
   Host-Key vor, darf nur die read-only Inventur vorbereitet werden.
4. Ist keines dieser Gates offen, bleibt Implementierungs-WIP leer. Dann werden
   externe Termine nach dem Radar verfolgt, statt Zukunftsfunktionen vorzuziehen.

## 28.08. Cutline

Der 28.08. ist ein technischer Readiness-Meilenstein, kein automatischer
Produktionsstart. Akzeptiert ist der Meilenstein, wenn alle lokalen Pakete
versioniert und geprueft sind, offene externe Gates mit Owner und Datum sichtbar
sind und kein Echtdatum ohne externen Restorepfad verarbeitet wird.

Verbindliche Detailquellen:

- `pilot-cutline-2026-08-28.md`
- `../architecture/production-release-plan-2026-09-25.md`
- `../architecture/postgresql-backup-restore-runbook.md`
- `../architecture/website-sftp-release-rehearsal-runbook.md`
- `activation-input-contract-2026-08-24.md`
- `../operations/go-live-evidence-index.md`
- `../../PROJECT_PLAN.md`
