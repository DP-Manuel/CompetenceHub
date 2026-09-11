# Competence Hub Readiness Gate Board

Stand: 2026-09-11

## Ampel

| Ziel | Status | Einordnung | Naechster Beweis |
| --- | --- | --- | --- |
| Technisches Readiness-Paket | GRUEN TECHNISCH | Website-/Webapp-Pakete, Staging und externer Backup-/Restore-Beweis sind gruen; die aktuelle Website hat zusaetzlich ein festes internes Link-Gate | Nach relevanten Codeaenderungen reproduzierbar neu bauen |
| Kalender-Discovery und Architektur | GRUEN FACHLICH / DESIGN | CAL-0/CAL-0.1, CAL-D01 bis CAL-D08 und ADR 0007 sind akzeptiert; CAL-1-Entwurf liegt vor | CAL-T01..T06 entscheiden; keine Migration oder Echtdaten ableiten |
| Erste freigegebene Firmen | GELB | Datenmodell, geschuetzter Firmen-/Kontakt-Slice und synthetischer Restore sind bewiesen; Echtdaten bleiben gegated | Vertrag, benannte Konten, Backup-Timer/Alarm und Betriebsfreigabe |
| Kontrollierter Produktionsstart | GELB / TERMINKANDIDATEN | 17.09. bevorzugt, wenn alle Gates schliessen; 24.09. als Ausweichtermin, sonst spaeter | EDV/Legal klaeren und Onboarding-/Go-No-Go bestaetigen |
| Budget | UNBEKANNT | Kein belastbarer Budgetrahmen dokumentiert | Nur bei kostenpflichtigem Mail-, Hosting- oder Backupbedarf entscheiden |

`GELB` bedeutet: mit den vorhandenen Nachweisen erreichbar, aber von offenen
Gates abhaengig. Es ist keine Produktionsfreigabe.

## Kanban

| DONE | READY / NEXT | WAITING EXTERNAL | BLOCKED UNTIL GATES CLOSE |
| --- | --- | --- | --- |
| ADR 0007 angenommen und CAL-1-Architektur/API/RBAC entworfen | CAL-T01 bis CAL-T06 annehmen oder aendern | EXT-02: Vertragsstand, finaler Betreiber, Impressum und Rechtspruefung | Echtdaten und erster realer Firmenrecord |
| CAL-D01 bis CAL-D08 und Pilotablauf von Janay akzeptiert | Nach CAL-T-Freigabe Migration `0005` lokal entwerfen | EXT-03: Onboarding-/Go-No-Go-Terminbestaetigung | Produktive Einladungs-E-Mails und reale Konten |
| Verschluesselter externer Backup-/Restore-Nachweis mit 24 Tabellen abgeschlossen | Restentscheidungen CP-02/04/07/08 schliessen | EXT-03: Janay-Onboarding und Thomas-Ross-Go/No-Go fuer 17.09., ersatzweise 24.09. bestaetigen | Oeffentliche Bewerbung und Produktions-Go-Live |
| Lokaler Backup-Meldungsvertrag mit 21 fokussierten Tests abgeschlossen | Restentscheidungen CP-02/04/07/08 schliessen | EXT-01: SMTP-/Sendervertrag und Benachrichtigungskanal | Produktive Backup-Timer ohne getestete Zustellung |
| Pilot-Owner entschieden: Manuel Admin, Thomas technischer Break-glass, Janay Mailbox ohne Vertretung | Ab 14.09. EDV-Antwort pruefen; ab 15.09. nachfassen | EXT-06: spaetere Mailboxvertretung bleibt unbesetzt; kein Service-Level versprechen | Automatisierter Website-Replace oder Remote-Loeschung |
| Sauberes Website-Artefakt `5d126cbaec0e` mit 1.137 geprueften internen Referenzen | Nach EDV-Korrektur: SFTP-Webroot nur lesend inventarisieren | Korrigiertes IONOS-SFTP-Startverzeichnis | Unternehmens-/personenbezogene Daten ohne aktiven Backup-/Alarmbetrieb |

WIP-Regel: maximal ein technischer Ausfuehrungsblock gleichzeitig. Externe
Anfragen laufen parallel, erweitern aber nicht stillschweigend den Scope.

## Gate-Matrix

| Gate | Status | Owner | Ziel / Frist | Evidence / Abnahme | Wirkung bei offenem Gate |
| --- | --- | --- | --- | --- | --- |
| G-CODE: gepruefter Source-Checkpoint | DONE / PUSHED | Manuel | aktualisiert 11.09. | Backup-Notifier-Commit `58299ae` und Website-Checkpoint `5d126cb` gepusht | Kein Release aus ungeprueftem Source |
| G-TEST: lokale und Staging-Qualitaet | DONE fuer aktuellen Slice | Manuel | aktualisiert 11.09. | Website: 43 Astro-Dateien, 30 Seiten, 1.137 interne Referenzen; Webapp: 315 Passes/14 erwartete Staging-Skips, 21 fokussierte Operations-Tests, vorher 14/14 Staging und BA-01..17 | Bei Codeaenderung erneut pruefen |
| G-WEBSITE: statisches Produktionsartefakt | DONE LOKAL / REVIEW GREEN | Manuel | aktualisiert 11.09. | Clean `5d126cbaec0e`; 51 Eintraege; SHA-256 `8056d431...5269d4`; `index.html`, `404.html`, `.htaccess`; Workflow `34582211406`; Deploymentflag false | Noch kein SFTP-Upload |
| G-WEBAPP: reproduzierbares Runtime-Paket | DONE LOKAL | Manuel | vor Backenddeployment neu bauen | Clean Paket mit Restore-Tool, isolierter Installation und Fail-closed Runtime | Noch keine VPS-Aktivierung |
| G-BACKUP: verschluesselte externe Kopie plus Restore | DONE REHEARSAL / DELIVERY OPEN | Manuel / Wuerzburg | quartalsweise nach Echtdatenstart | Guarded Pull und digest-gepinnter netzloser Restore mit 24 Tabellen; Zeitplan/Retention entschieden; lokaler Meldungsvertrag mit 21 Tests gruen | Timer bleiben aus, bis der EDV-abhaengige Adapter Erfolg und synthetische Stoerung zugestellt hat |
| G-CALENDAR: CAL-0/CAL-0.1 | DONE REVIEW | Janay / Manuel | akzeptiert 11.09. | Review, Browser-/Netzwerk-Smokes und Janays ausdrueckliche Zustimmung | Produktive CAL-1-Umsetzung bleibt hinter Fachentscheidungen |
| G-CALENDAR-RULES: CAL-D01..D08 / ADR 0007 | DONE / ACCEPTED | Janay / Manuel | abgeschlossen 11.09. | Janay akzeptierte alle Regeln/Pilotablauf; Manuel akzeptierte ADR 0007 | Erlaubt Design, aber keine Migration, Konten, Daten oder Aktivierung |
| G-CALENDAR-DESIGN: CAL-1 Daten/API/RBAC | DONE LOCAL / MIGRATION DECISIONS OPEN | Manuel | aktualisiert 11.09. | revisionssichere Publikation, `calendar_reviewer`, öffentliche/private Projektion und Testmatrix dokumentiert | Migration `0005` wartet auf CAL-T01..T06 und separate Staging-Freigabe |
| G-EDV: App-DNS/TLS/SMTP | WAITING UNTIL 14.09. | EDV | ab 14.09. pruefen, ab 15.09. nachfassen | DNS-/TLS-Preflight, Nginx-Check, autorisierter Einzelabsender und Testzustellung | Keine Live-Einladung, keine Webapp-Produktion |
| G-SFTP: bestaetigter Webroot und Rollbackkopie | WAITING EXTERNAL | Manuel / Thomas Ross / EDV | vor Website-Go-Live | Host-Key bestaetigt; Anmeldung bewiesen; zugewiesener Webroot fehlt noch | Kein Website-Replace |
| G-CONTRACT: finaler Vertragsweg | WAITING | Lars Donner / Fachseite | im September klaeren | Freigegebener Vertragsstand und Prozess | Kein freigegebener erster Firmenprozess |
| G-LEGAL: Betreiber und Rechtstexte | WAITING | Lars Donner / Rechtspruefung | Reviewpfad bis 24.09.; Abschluss vor Go/No-Go | Finaler Betreiber, Impressum und anwendbare Datenschutz-/AGB-Fassung | Kein beworbener Livegang |
| G-ACCOUNT: benannte Konten und MFA | WAITING ACTIVATION | Manuel / Janay / Thomas Ross | bevorzugt 17.09., ersatzweise 24.09. | E-Mail-Einladung, MFA, Least-Privilege-Matrix, getrennt getesteter technischer Break-glass-Zugang | Kein realer Fachbetrieb |
| G-ACCEPT: Fachabnahme und Go/No-Go | WAITING | Janay / Thomas Ross | 17.09. bevorzugt, 24.09. als Fallback | Janay-Walkthrough und dokumentiertes Go/No-Go | Keine Produktion |
| G-MAILBOX: Reaktion und Vertretung | KNOWN GAP | Janay | Routing vor Pilot testen; Vertretung spaeter benennen | Janay ist Owner; aktuell keine Abwesenheitsvertretung; Thomas deckt nur technische Notfaelle | Kein versprochenes Service-Level |

## Pull-Regel

1. ADR 0007 und CAL-D01 bis CAL-D08 sind akzeptiert. Manuel entscheidet
   CAL-T01 bis CAL-T06; bis dahin entsteht keine Migration.
2. Die EDV-Antwort wird ab 14.09. geprueft und ab 15.09. nachgefasst. Erst nach
   korrigiertem SFTP-Startverzeichnis folgt eine read-only Webroot-Inventur.
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
