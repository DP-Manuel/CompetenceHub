# Competence Hub Readiness Gate Board

Stand: 2026-09-17

## Ampel

| Ziel | Status | Einordnung | Naechster Beweis |
| --- | --- | --- | --- |
| Technisches Readiness-Paket | GRUEN TECHNISCH | Website-/Webapp-Pakete, Staging und externer Backup-/Restore-Beweis sind gruen; die aktuelle Website hat zusaetzlich ein festes internes Link-Gate | Nach relevanten Codeaenderungen reproduzierbar neu bauen |
| Kalender-Discovery und Architektur | GRUEN FACHLICH / DESIGN / STAGING | CAL-0/CAL-0.1, Entscheidungen, Architektur und Migration `0005` sind akzeptiert und auf leerem Staging bewiesen | CAL-1-Domain/Repository mit synthetischen Tests umsetzen; keine Echtdaten ableiten |
| Erste freigegebene Firmen | GELB | Datenmodell, geschuetzter Firmen-/Kontakt-Slice und synthetischer Restore sind bewiesen; Echtdaten bleiben gegated | Vertrag, benannte Konten, Backup-Timer/Alarm und Betriebsfreigabe |
| Kontrollierter Produktionsstart | GELB / NACH URLAUB | 17.09. ist verstrichen; 24.09. ist kein Releaseversprechen; naechster Korridor fruehestens zweite Oktoberhaelfte | EDV/Legal klaeren und Onboarding-/Go-No-Go neu terminieren |
| Budget | UNBEKANNT | Kein belastbarer Budgetrahmen dokumentiert | Nur bei kostenpflichtigem Mail-, Hosting- oder Backupbedarf entscheiden |

`GELB` bedeutet: mit den vorhandenen Nachweisen erreichbar, aber von offenen
Gates abhaengig. Es ist keine Produktionsfreigabe.

## Kanban

| DONE | READY / NEXT | WAITING EXTERNAL | BLOCKED UNTIL GATES CLOSE |
| --- | --- | --- | --- |
| ADR 0007, CAL-T01 bis CAL-T06 und CAL-1-Architektur/API/RBAC angenommen | CAL-1-Domain und Repository implementieren | EXT-02: Vertragsstand, finaler Betreiber, Impressum und Rechtspruefung | Echtdaten und erster realer Firmenrecord |
| Migration `0005`, Rollback-Smoke, Nullrueckstand und Pre/Post-Dumps bewiesen | Geschuetzte/oeffentliche APIs nach Repository-Gate umsetzen | EXT-03: Onboarding-/Go-No-Go-Terminbestaetigung | Produktive Einladungs-E-Mails und reale Konten |
| Verschluesselter externer Backup-/Restore-Nachweis mit 24 Tabellen abgeschlossen | Restentscheidungen CP-02/04/07/08 schliessen | EXT-03: Janay-Onboarding und Thomas-Ross-Go/No-Go fuer den Oktoberkorridor neu terminieren | Oeffentliche Bewerbung und Produktions-Go-Live |
| Lokaler Backup-Meldungsvertrag mit 21 fokussierten Tests abgeschlossen | Restentscheidungen CP-02/04/07/08 schliessen | EXT-01: SMTP-/Sendervertrag und Benachrichtigungskanal | Produktive Backup-Timer ohne getestete Zustellung |
| Pilot-Owner entschieden: Manuel Admin, Thomas technischer Break-glass, Janay Mailbox ohne Vertretung | EDV-Follow-up laeuft; Antwort nach Eingang verarbeiten | EXT-06: spaetere Mailboxvertretung bleibt unbesetzt; kein Service-Level versprechen | Automatisierter Website-Replace oder Remote-Loeschung |
| Sauberes Website-Artefakt `5d126cbaec0e` mit 1.137 geprueften internen Referenzen | Nach EDV-Korrektur: SFTP-Webroot nur lesend inventarisieren | Korrigiertes IONOS-SFTP-Startverzeichnis | Unternehmens-/personenbezogene Daten ohne aktiven Backup-/Alarmbetrieb |

WIP-Regel: maximal ein technischer Ausfuehrungsblock gleichzeitig. Externe
Anfragen laufen parallel, erweitern aber nicht stillschweigend den Scope.

## Gate-Matrix

| Gate | Status | Owner | Ziel / Frist | Evidence / Abnahme | Wirkung bei offenem Gate |
| --- | --- | --- | --- | --- | --- |
| G-CODE: gepruefter Source-Checkpoint | DONE / PUSHED | Manuel | aktualisiert 11.09. | Backup-Notifier-Commit `58299ae` und Website-Checkpoint `5d126cb` gepusht | Kein Release aus ungeprueftem Source |
| G-TEST: lokale und Staging-Qualitaet | DONE FUER MIGRATION 0005 | Manuel | aktualisiert 17.09. | 318 lokale Passes/14 Skips; nativer Smoke, Nullrueckstand, 27 Owner-Tabellen, denied Runtime-Rechte, 86/108-KiB Dumps und vier aktive Dienste | Bei Domain-/Repository-Code erneut ausfuehren |
| G-WEBSITE: statisches Produktionsartefakt | DONE LOKAL / REVIEW GREEN | Manuel | aktualisiert 11.09. | Clean `5d126cbaec0e`; 51 Eintraege; SHA-256 `8056d431...5269d4`; `index.html`, `404.html`, `.htaccess`; Workflow `34582211406`; Deploymentflag false | Noch kein SFTP-Upload |
| G-WEBAPP: reproduzierbares Runtime-Paket | DONE LOKAL | Manuel | vor Backenddeployment neu bauen | Clean Paket mit Restore-Tool, isolierter Installation und Fail-closed Runtime | Noch keine VPS-Aktivierung |
| G-BACKUP: verschluesselte externe Kopie plus Restore | DONE REHEARSAL / DELIVERY OPEN | Manuel / Wuerzburg | quartalsweise nach Echtdatenstart | Guarded Pull und digest-gepinnter netzloser Restore mit 24 Tabellen; Zeitplan/Retention entschieden; lokaler Meldungsvertrag mit 21 Tests gruen | Timer bleiben aus, bis der EDV-abhaengige Adapter Erfolg und synthetische Stoerung zugestellt hat |
| G-CALENDAR: CAL-0/CAL-0.1 | DONE REVIEW | Janay / Manuel | akzeptiert 11.09. | Review, Browser-/Netzwerk-Smokes und Janays ausdrueckliche Zustimmung | Produktive CAL-1-Umsetzung bleibt hinter Fachentscheidungen |
| G-CALENDAR-RULES: CAL-D01..D08 / ADR 0007 | DONE / ACCEPTED | Janay / Manuel | abgeschlossen 11.09. | Janay akzeptierte alle Regeln/Pilotablauf; Manuel akzeptierte ADR 0007 | Erlaubt Design, aber keine Migration, Konten, Daten oder Aktivierung |
| G-CALENDAR-DESIGN: CAL-1 Daten/API/RBAC | DONE / STAGING PROVEN | Manuel | aktualisiert 17.09. | `calendar_reviewer`, drei leere Tabellen, Migration 0005, Rollback-Smoke, Nullrueckstand, Rechte und Backups verifiziert | Anwendungscode und Rollenvergabe bleiben getrennt |
| G-EDV: App-DNS/TLS/SMTP | WAITING / FOLLOW-UP ACTIVE | EDV | Antwort ausstehend seit 14.09. | DNS-/TLS-Preflight, Nginx-Check, autorisierter Einzelabsender und Testzustellung | Keine Live-Einladung, keine Webapp-Produktion |
| G-SFTP: bestaetigter Webroot und Rollbackkopie | WAITING EXTERNAL | Manuel / Thomas Ross / EDV | vor Website-Go-Live | Host-Key bestaetigt; Anmeldung bewiesen; zugewiesener Webroot fehlt noch | Kein Website-Replace |
| G-CONTRACT: finaler Vertragsweg | WAITING | Lars Donner / Fachseite | im September klaeren | Freigegebener Vertragsstand und Prozess | Kein freigegebener erster Firmenprozess |
| G-LEGAL: Betreiber und Rechtstexte | WAITING | Lars Donner / Rechtspruefung | Reviewpfad bis 24.09.; Abschluss vor Go/No-Go | Finaler Betreiber, Impressum und anwendbare Datenschutz-/AGB-Fassung | Kein beworbener Livegang |
| G-ACCOUNT: benannte Konten und MFA | WAITING ACTIVATION | Manuel / Janay / Thomas Ross | fuer Oktoberkorridor neu terminieren | E-Mail-Einladung, MFA, Least-Privilege-Matrix, getrennt getesteter technischer Break-glass-Zugang | Kein realer Fachbetrieb |
| G-ACCEPT: Fachabnahme und Go/No-Go | WAITING | Janay / Thomas Ross | fuer Oktoberkorridor neu terminieren | Janay-Walkthrough und dokumentiertes Go/No-Go | Keine Produktion |
| G-MAILBOX: Reaktion und Vertretung | KNOWN GAP | Janay | Routing vor Pilot testen; Vertretung spaeter benennen | Janay ist Owner; aktuell keine Abwesenheitsvertretung; Thomas deckt nur technische Notfaelle | Kein versprochenes Service-Level |

## Pull-Regel

1. ADR 0007, CAL-D01 bis CAL-D08 und CAL-T01 bis CAL-T06 sind akzeptiert;
   Migration `0005` ist auf isoliertem Staging bewiesen. Als naechstes folgt
   CAL-1-Domain/Repository ohne Konten, Echtdaten, Reservierungen oder Mail.
2. Das EDV-Follow-up laeuft bereits. Erst nach korrigiertem SFTP-Startverzeichnis
   folgt eine read-only Webroot-Inventur; bis dahin kein Upload.
3. Das CP-01-bis-CP-08-Inhaltspaket kann unabhaengig versendet werden; neue
   Ratgeberseiten oder unbelegte Aussagen bleiben gesperrt.
4. Wenn kein Gate schliesst, werden Release-, Sicherheits-, Barrierefreiheits-
   oder Dokumentationsarbeiten nur mit klarer Abnahme und ohne Echtdaten
   vorgezogen.

## Meilenstein und Produktionsgrenze

Der 28.08. war ein technischer Readiness-Meilenstein, kein Produktionsstart.
Der aktuelle Stand bestaetigt diese Basis und ergaenzt die akzeptierte
Kalender-Discovery sowie das aktualisierte Website-Paket. IONOS-Upload,
Webapp-Aktivierung, reale Konten, Echtdaten, Mailversand und Bewerbung brauchen
weiterhin ihre jeweiligen Freigaben.

Verbindliche Detailquellen:

- `pilot-cutline-2026-08-28.md`
- `coach-availability-calendar-v0.1.md`
- `calendar-stakeholder-decisions-2026-09-11.md`
- `calendar-stakeholder-review-handout-2026-09-11.md`
- `calendar-quality-plan-v0.1.md`
- `email-automation-template-inventory-2026-09-11.md`
- `../architecture/production-release-plan-2026-09-25.md`
- `../architecture/postgresql-backup-restore-runbook.md`
- `../architecture/website-sftp-release-rehearsal-runbook.md`
- `activation-input-contract-2026-08-24.md`
- `../operations/go-live-evidence-index.md`
- `../../PROJECT_PLAN.md`
