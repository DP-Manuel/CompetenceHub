# Competence Hub Readiness Gate Board

Stand: 2026-09-22

## Ampel

| Ziel | Status | Einordnung | Naechster Beweis |
| --- | --- | --- | --- |
| Technisches Readiness-Paket | GRUEN TECHNISCH | Website-/Webapp-Pakete, Staging und externer Backup-/Restore-Beweis sind gruen; die aktuelle Website hat zusaetzlich ein festes internes Link-Gate | Nach relevanten Codeaenderungen reproduzierbar neu bauen |
| Messe-Readiness oeffentliches Frontend | GELB / HOECHSTE PRIORITAET | lokale Routen-, Browser-, Clean-Artefakt-, Handover- und SFTP-Inhaltsnachweise sind gruen; EDV entfernte `phpinfo()` und akzeptierte `.htaccess`-Redirects; Inhalts- und Releasefreigaben offen | exakten Releaseinhalt und Go/No-Go festlegen; kontrollierter Live-Test Ziel 24.09. |
| Kalender-Discovery und Architektur | GRUEN FACHLICH / DESIGN / API STAGING / UI LOCAL / EINGEFROREN | CAL-0/CAL-0.1, Entscheidungen, Migrationen `0005`/`0006`, Repository, API und synthetische Coach-/Reviewer-UI sind bewiesen; 384 lokale, 17/17 native und 57/57 Edge-Checks gruen | nativen Staging-UI-Lauf erst nach Messe-Readiness und separater Freigabe fortsetzen |
| Erste freigegebene Firmen | GELB | Datenmodell, geschuetzter Firmen-/Kontakt-Slice und synthetischer Restore sind bewiesen; Echtdaten bleiben gegated | Vertrag, benannte Konten, Backup-Timer/Alarm und Betriebsfreigabe |
| Kontrollierter Website-Produktionsstart | GELB / CONDITIONAL | Live-Test am 24.09. moeglich; Webroot und Diagnose-P0 sind geschlossen, Clean-Artefakt liegt vor; finaler Inhalt, Rollback, Thomas-Go/No-Go und separate Uploadfreigabe bleiben | statische Website-Gates getrennt vom Backend schliessen |
| Budget | UNBEKANNT | Kein belastbarer Budgetrahmen dokumentiert | Nur bei kostenpflichtigem Mail-, Hosting- oder Backupbedarf entscheiden |

`GELB` bedeutet: mit den vorhandenen Nachweisen erreichbar, aber von offenen
Gates abhaengig. Es ist keine Produktionsfreigabe.

## Kanban

| DONE | READY / NEXT | WAITING EXTERNAL | BLOCKED UNTIL GATES CLOSE |
| --- | --- | --- | --- |
| ADR 0007, CAL-T01 bis CAL-T06, Migrationen `0005`/`0006`, CAL-1-Domain/Repository, APIs und synthetische Portal-UI inklusive 26-Punkte-Browserabnahme abgeschlossen | neuen Clean-Release mit freigegebenem Gülcan-Profil bauen | Kontaktmail-Zustellung als Produktions-Smoke | Echtdaten und erster realer Firmenrecord |
| Migration `0006`, Rollback-Smoke, Nullrueckstand, Pre/Post-Dumps, 17/17 native, 384 lokale Tests und 57/57 Edge-Checks bewiesen | Pre-Upload-Inventur/Backup und kontrollierten Live-Test ausfuehren | keine offene Coach-Inhalts- oder Bildrechtefreigabe | Produktive Einladungs-E-Mails und reale Konten |
| Verschluesselter externer Backup-/Restore-Nachweis mit 24 Tabellen abgeschlossen | Restentscheidungen CP-02/04/07/08 schliessen | EXT-03: Janay-Onboarding und Thomas-Ross-Go/No-Go fuer den Oktoberkorridor neu terminieren | Oeffentliche Bewerbung und Produktions-Go-Live |
| Lokaler Backup-Meldungsvertrag mit 21 fokussierten Tests abgeschlossen | Restentscheidungen CP-02/04/07/08 schliessen | EXT-01: SMTP-/Sendervertrag und Benachrichtigungskanal | Produktive Backup-Timer ohne getestete Zustellung |
| Pilot-Owner entschieden: Manuel Admin, Thomas technischer Break-glass, Janay Mailbox ohne Vertretung | EDV-Follow-up laeuft; Antwort nach Eingang verarbeiten | EXT-06: spaetere Mailboxvertretung bleibt unbesetzt; kein Service-Level versprechen | Automatisierter Website-Replace oder Remote-Loeschung |
| Clean-Messe-Kandidat `a8d034c`; Webroot-Inventur bestanden; EDV-P0 geschlossen; Gülcan-Inhalt/Bild/Release freigegeben | neuen Clean-Kandidaten bauen, Pre-Upload-Backup und Upload ausfuehren | Kontaktmail-Zustellung unmittelbar pruefen | Unternehmens-/personenbezogene Daten ohne aktiven Backup-/Alarmbetrieb |

WIP-Regel: maximal ein technischer Ausfuehrungsblock gleichzeitig. Externe
Anfragen laufen parallel, erweitern aber nicht stillschweigend den Scope.

## Gate-Matrix

| Gate | Status | Owner | Ziel / Frist | Evidence / Abnahme | Wirkung bei offenem Gate |
| --- | --- | --- | --- | --- | --- |
| G-CODE: gepruefter Source-Checkpoint | DONE / PUSHED | Manuel | aktualisiert 11.09. | Backup-Notifier-Commit `58299ae` und Website-Checkpoint `5d126cb` gepusht | Kein Release aus ungeprueftem Source |
| G-TEST: lokale und Staging-Qualitaet | PASS LOCAL / API STAGING | Manuel | aktualisiert 18.09. | 384 lokale Passes/17 Skips; 57/57 Edge-Checks und 26/26 Browserpunkte; fokussiert 3/3 und vollstaendig 17/17 native Staging-Pfade; null Zeilen in 19 dynamischen Bereichen; vier Dienste aktiv | Native Staging-UI-Abnahme nach separater Freigabe |
| G-WEBSITE: statisches Produktionsartefakt | DONE LOKAL / REVIEW GREEN | Manuel | aktualisiert 21.09. | Clean `a8d034c`; 53 Eintraege; SHA-256 `15a1ae6b...96300`; `index.html`, `404.html`, `.htaccess`; 722 Edge-Checks; Deploymentflag false | Noch kein SFTP-Upload; neue Coach-Seite ist noch nicht Teil dieses Artefakts |
| G-WEBAPP: reproduzierbares Runtime-Paket | DONE LOKAL | Manuel | vor Backenddeployment neu bauen | Clean Paket mit Restore-Tool, isolierter Installation und Fail-closed Runtime | Noch keine VPS-Aktivierung |
| G-BACKUP: verschluesselte externe Kopie plus Restore | DONE REHEARSAL / DELIVERY OPEN | Manuel / Wuerzburg | quartalsweise nach Echtdatenstart | Guarded Pull und digest-gepinnter netzloser Restore mit 24 Tabellen; Zeitplan/Retention entschieden; lokaler Meldungsvertrag mit 21 Tests gruen | Timer bleiben aus, bis der EDV-abhaengige Adapter Erfolg und synthetische Stoerung zugestellt hat |
| G-CALENDAR: CAL-0/CAL-0.1 | DONE REVIEW | Janay / Manuel | akzeptiert 11.09. | Review, Browser-/Netzwerk-Smokes und Janays ausdrueckliche Zustimmung | Produktive CAL-1-Umsetzung bleibt hinter Fachentscheidungen |
| G-CALENDAR-RULES: CAL-D01..D08 / ADR 0007 | DONE / ACCEPTED | Janay / Manuel | abgeschlossen 11.09. | Janay akzeptierte alle Regeln/Pilotablauf; Manuel akzeptierte ADR 0007 | Erlaubt Design, aber keine Migration, Konten, Daten oder Aktivierung |
| G-CALENDAR-DESIGN: CAL-1 Daten/API/RBAC/UI | UI LOCAL ACCEPTED / API STAGING PROVEN | Manuel | aktualisiert 18.09. | `calendar_reviewer`, Migrationen `0005`/`0006`, Domain/Repository, getrennte Session-Rollen, geschuetzte/oeffentliche API sowie 26/26 lokale Browserpunkte gruen | Native Staging-UI, Rollenvergabe, Echtdaten und Aktivierung bleiben getrennt |
| G-EDV: App-DNS/TLS/SMTP | WAITING / FOLLOW-UP ACTIVE | EDV | Antwort ausstehend seit 14.09. | DNS-/TLS-Preflight, Nginx-Check, autorisierter Einzelabsender und Testzustellung | Keine Live-Einladung, keine Webapp-Produktion |
| G-SFTP: bestaetigter Webroot und Rollbackkopie | PASS READ-ONLY / P0 CLOSED / BACKUP OPEN | Manuel / Thomas Ross / EDV | Inhaltsnachweis 21.09.; EDV-Korrektur 22.09.; Backup vor jedem Replace | Host-Key und Auth bestanden; `/` ist der bestaetigte Chroot; Thomas entfernte die temporaere `index.php`; vier URLs liefern `403` ohne `phpinfo()`; `.htaccess`-Redirects akzeptiert | Kein Website-Replace ohne aktuelle Pre-Upload-Inventur, datierte Rollbackkopie und separate Freigabe |
| G-CONTRACT: finaler Vertragsweg | WAITING | Lars Donner / Fachseite | im September klaeren | Freigegebener Vertragsstand und Prozess | Kein freigegebener erster Firmenprozess |
| G-LEGAL: Betreiber und Rechtstexte | PASS DECISION | Lars Donner / Manuel | bestaetigt 21.09. | Donner + Partner als Betreiber, Lars Donner verantwortlich und zentrale D+P-Seiten fuer Impressum, AGB und Datenschutz bestaetigt | Bei neuer Datenerhebung oder neuen externen Diensten erneut pruefen |
| G-ACCOUNT: benannte Konten und MFA | DEFERRED FOR BACKEND | Manuel / Janay / Thomas Ross | nach Website Messe-Readiness | E-Mail-Einladung, MFA, Least-Privilege-Matrix, getrennt getesteter technischer Break-glass-Zugang | Kein realer Fachbetrieb; blockiert statisches Messepaket nicht |
| G-ACCEPT: Website Fachabnahme und Go/No-Go | PASS CONTENT / RELEASE AUTHORIZED | Manuel / Thomas Ross | freigegeben 22.09.; kontrollierter Live-Test folgt | Gülcan-Profil samt Bild und beruflichen Daten freigegeben; EDV-Webroot/Redirectpfad bestaetigt; Manuel autorisiert Fertigstellung | Pre-Upload-Backup und Produktion-Smokes bleiben zwingend |
| G-MAILBOX: Reaktion und Vertretung | KNOWN GAP | Janay | Routing vor Pilot testen; Vertretung spaeter benennen | Janay ist Owner; aktuell keine Abwesenheitsvertretung; Thomas deckt nur technische Notfaelle | Kein versprochenes Service-Level |

## Pull-Regel

1. Bis zur operativen Cutline am 25.09. wird ausschliesslich Website
   Messe-Readiness als technischer WIP gezogen. Webroot-/EDV-P0, Gap-Analyse,
   Korrektur, Browsergate, Clean-Artefakt und Handover sind abgeschlossen.
   Jetzt folgen Inhaltsentscheid, Go/No-Go und kontrollierter Upload. Kein
   Upload ohne separate Freigabe.
2. CAL-1 bleibt mit 26/26 Browserpunkten, 57/57 Edge-Checks, 384 lokalen Tests
   und 17/17 nativen Staging-Pfaden erhalten, aber eingefroren. Native
   Staging-UI und CAL-2 folgen erst nach Messe-Readiness und eigener Freigabe.
3. Das CP-01-bis-CP-08-Inhaltspaket kann unabhaengig versendet werden; neue
   Ratgeberseiten oder unbelegte Aussagen bleiben gesperrt.
4. Wenn kein Gate schliesst, werden Release-, Sicherheits-, Barrierefreiheits-
   oder Dokumentationsarbeiten nur mit klarer Abnahme und ohne Echtdaten
   vorgezogen.

## Meilenstein und Produktionsgrenze

Der 28.08. war ein technischer Readiness-Meilenstein, kein Produktionsstart.
Neue verbindliche Steuerung: Manuel-Cutline 25.09., Abwesenheit ab 26.09. und
Messe am 17.10. Bis 25.09. muss mindestens ein stabiles, voll geprueftes und
uebergabefaehiges statisches Website-Paket vorliegen. IONOS-Upload,
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
