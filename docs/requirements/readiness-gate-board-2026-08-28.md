# Competence Hub Readiness Gate Board

Stand: 2026-08-25

## Ampel

| Ziel | Status | Einordnung | Naechster Beweis |
| --- | --- | --- | --- |
| Technisches Readiness-Paket bis 28.08.2026 | GELB | Software, Website-/Webapp-Pakete, Staging sowie externer Backup-/Restore-Beweis sind gruen. App-DNS/SMTP und Produktionsbetrieb bleiben extern abhaengig. | EXT-01-Antwort und hostbezogene Validierung |
| Erste freigegebene Firmen nach Vertragsabschluss | GELB | Datenmodell, geschuetzter Firmen-/Kontakt-Slice und synthetischer Restore sind bewiesen. Echtdaten bleiben bis Legal-, Konten-, Produktions- und Go/No-Go-Gate gesperrt. | Freigegebener Vertrag, benannte Konten und Betriebsfreigabe |
| Kontrollierter Produktionsstart | NEU PLANEN | Der bisherige 25.09.2026-Termin wird verschoben; ein Ersatztermin ist noch nicht bestaetigt. Alle Produktionsgates bleiben bindend. | Ersatztermin mit Ownern und Rueckwaertsplan festlegen |
| Budget | UNBEKANNT | Im Projekt ist kein belastbarer Budgetrahmen dokumentiert. | Nur bei kostenpflichtigem Backup-, Mail- oder Hostingbedarf entscheiden |

`GELB` bedeutet hier: mit den vorhandenen Nachweisen erreichbar, aber von
offenen zeitkritischen Gates abhaengig. Es ist keine Produktionsfreigabe.

## Kanban

| DONE | READY / NEXT | WAITING EXTERNAL | BLOCKED UNTIL GATES CLOSE |
| --- | --- | --- | --- |
| Auth, MFA, Rollen und Firmen-/Kontakt-Slice lokal und auf Staging synthetisch bewiesen | SB-23-Export nach Freigabe gezielt bereinigen; dann erstes verfuegbares Infrastruktur-Gate ziehen | EXT-01: App-DNS, TLS-/Proxy-Pfad, SMTP-Vertrag und Absender durch EDV | Echtdaten und erster realer Firmenrecord |
| Portal-Browserabnahme BA-01 bis BA-17 abgeschlossen | Bei frueher EDV-Antwort: hostbezogene Konfiguration rendern und nativ validieren | EXT-02: Vertragsstand und fachliche Freigabe | Produktive Einladungs-E-Mails und reale Konten |
| Reproduzierbare Website- und Webapp-Artefaktvertraege vorhanden | Nach separater Verbindungsfreigabe: SFTP-Host-Key, `pwd` und vollstaendige Remote-Inventur nur lesend pruefen | EXT-03: Janay-Onboarding und Thomas-Ross-Go/No-Go terminieren | Oeffentliche Bewerbung und Produktions-Go-Live |
| Lokales PostgreSQL-Backup-/Monitor-/Restore-Paket vorbereitet | Nach Inventur: gepinntes lokales SFTP-Rehearsal-Paket erzeugen | EXT-04: finaler Betreiber, Impressum und Rechtspruefung | Automatisierter Website-Replace oder Remote-Loeschung |
| Guarded Website-SFTP-Paket vorbereitet; keine Verbindung oder Freigabe eingebaut | Readiness-Nachweise am 28.08. gegen dieses Board abgleichen | EXT-05: kontrollierter Wuerzburg-Termin und geschuetzter Ablageort | Unternehmens-/personenbezogene Daten ohne externen Restore |
| Git-Checkpoint `9210ea1` plus Statuscommit `e8c7d53` auf `origin/main` |  | EXT-06: Mailbox-Reaktion, Vertretung und Ownership mit Janay |  |

WIP-Regel: maximal ein technischer Ausfuehrungsblock gleichzeitig. Externe
Anfragen laufen parallel, erweitern aber nicht stillschweigend den Scope.

## Gate-Matrix

| Gate | Status | Owner | Spaetester sinnvoller Termin | Evidence / Abnahme | Wirkung bei offenem Gate |
| --- | --- | --- | --- | --- | --- |
| G-CODE: gepruefter Source-Checkpoint | DONE | Manuel | erledigt 21.08. | Commits `9210ea1`, `e8c7d53`; Remote synchron | Kein neuer Release aus ungeprueftem Source |
| G-TEST: lokale und Staging-Qualitaet | DONE fuer aktuellen Slice | Manuel | erledigt | 304 lokale Passes, 14 erwartete Staging-Skips, vorherige 14/14 Staging- und BA-01..17-Nachweise | Bei Codeaenderung Gate erneut pruefen |
| G-WEBSITE: statisches Produktionsartefakt | DONE lokal | Manuel | 28.08. | 38 Astro-Dateien ohne Diagnose, 28 Seiten, SHA-/Manifestvertrag | Noch kein SFTP-Upload |
| G-WEBAPP: reproduzierbares Runtime-Paket | DONE lokal | Manuel | 28.08. | Wheel/ZIP, isolierte Installation, Fail-closed Runtime und Runbook | Noch keine VPS-Aktivierung |
| G-BACKUP: verschluesselte externe Kopie plus Restore | DONE REHEARSAL | Manuel / Wuerzburg | erledigt 25.08.; quartalsweise nach Echtdatenstart | verschluesselter Satz und Monitor gruen; Guarded Pull; digest-gepinnter netzloser Restore mit 24 Tabellen; 12/12; null Klartext-/Containerrest; vier Dienste active | Produktions-Timer/Alarmierung bleibt G-OPS; andere Echtdaten-Gates gelten weiter |
| G-EDV: App-DNS/TLS/SMTP | WAITING | EDV | Ziel 25.08.; spaetestens 04.09. | DNS-/TLS-Preflight, Nginx-Check, autorisierter Einzelabsender und Testzustellung | Keine Live-Einladung, keine Webapp-Produktion |
| G-SFTP: bestaetigter Webroot und Rollbackkopie | WAITING APPROVAL | Manuel / Thomas Ross | vor Website-Go-Live | Gepruefter Host-Key, read-only Inventur, vollstaendige Vorabkopie mit Hashliste | Kein Website-Replace |
| G-CONTRACT: finaler Vertragsweg | WAITING | Lars Donner / Fachseite | Ziel 28.08.; spaetestens 11.09. | Freigegebener Vertragsstand und Prozess | Kein freigegebener erster Firmenprozess |
| G-LEGAL: Betreiber und Rechtstexte | WAITING | Lars Donner / Rechtspruefung | Ziel 15.09.; spaetestens 18.09. | Finaler Betreiber, Impressum und anwendbare Datenschutz-/AGB-Fassung | Kein beworbener Livegang |
| G-ACCOUNT: benannte Konten und MFA | WAITING | Manuel / Janay | Ziel 11.09.; spaetestens 18.09. | E-Mail-Einladung, MFA, Least-Privilege-Matrix, keine Shared Accounts | Kein realer Fachbetrieb |
| G-ACCEPT: Fachabnahme und Go/No-Go | WAITING | Janay / Thomas Ross | nach Termin-Rebaseline | Janay-Walkthrough und dokumentiertes Go/No-Go mit Restpunkten | Keine Produktion |
| G-MAILBOX: Reaktion und Vertretung | WAITING | Janay / Manuel | Ziel 11.09.; spaetestens 18.09. | Owner, Vertretung, Reaktionsweg und Testzustellung | Kein versprochenes Service-Level |

## Pull-Regel

1. Nach expliziter Freigabe wird nur der temporaere VPS-Export entfernt; die
   originale VPS-Sicherung und die verifizierte `D:`-Kopie bleiben bestehen.
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
