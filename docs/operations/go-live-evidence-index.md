# Go-Live Evidence Index

Stand: 2026-09-11

Dieser Index enthaelt nur freigabefaehige Metadaten und Verweise. Secrets,
Private Keys, Recovery Keys und produktive personenbezogene Daten gehoeren
nicht hierher.

| Evidence ID | Datum | Owner | Umgebung | Nachweis | Ergebnis | Evidence Location | Datenmodus | Recheck / Notiz |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB-19 | 2026-08-21 | Manuel | isolated Staging | synthetisches Onboarding 14/14 | PASS | `PROJECT_LOG.md`; Staging-Testpaket | synthetisch | bei Auth-Aenderung |
| SB-20 | 2026-08-21 | Manuel | local release build | reproduzierbares Webapp-Paket | PASS LOCAL | Release-Manifest und Webapp-Runbook | synthetisch | bei Release-Code-Aenderung |
| SB-21 | 2026-08-21 | Manuel | local | Backup-/Restore-Werkzeugpaket | PASS LOCAL | `docs/architecture/postgresql-backup-restore-runbook.md` | synthetisch | nativer SB-23-Nachweis offen |
| SB-22 | 2026-08-21 | Manuel | local | SFTP-Rehearsal-Paket | PASS LOCAL | Website-SFTP-Runbook und Tests | keine | keine Verbindung/kein Upload |
| SB-23-PRE | 2026-08-25 | Manuel | Wuerzburg workstation | USB/Systemlaufwerk verschluesselt; Safe/Janay; Recovery-Code/Passphrase hinterlegt; lokaler Private Key und Public Export verifiziert | PASS | `docs/requirements/activation-input-contract-2026-08-24.md`; `docs/operations/sb23-wuerzburg-execution.md` | keine | Fingerprint `2E44306121629A100F76A8B08CCA3D9186A28D4C`; Rehearsal abgeschlossen |
| SB-23-HANDOFF | 2026-08-25 | Manuel | VPS staging | Public Key und achtteilige SB-21-Dateimenge uebertragen; lokale/entfernte Hashes identisch | PASS INSTALLED | `docs/operations/sb23-wuerzburg-execution.md`; `PROJECT_LOG.md` | keine | Public Key Modus 0600; geprueftes Paket installiert, Timer disabled |
| SB-23-INSTALL | 2026-08-25 | Manuel | VPS staging | Public-only GPG home, Konfiguration, Scripts und Units installiert und nativ validiert | PASS DISABLED | `docs/operations/sb23-wuerzburg-execution.md`; operator output | synthetisch | Fingerprint exakt; keine Private-Key-Warnung; beide Timer disabled; vier bestehende Dienste active |
| SB-23-RUN1 | 2026-08-25 | Manuel | VPS staging | erster manueller Backup-Lauf und eingegrenzte Fehlerdiagnose | FAIL CLOSED | `docs/operations/sb23-wuerzburg-execution.md`; Journal/Probe | synthetisch | Publikation durch `chmod 0500` vor Rename blockiert; kein Plaintext oder partieller Satz verblieben |
| SB-23-FIX1 | 2026-08-25 | Manuel | local / VPS staging | Publikationsreihenfolge korrigiert, Regressionstest, Hash-Handoff und Installation | PASS INSTALLED | Source/Test; `PROJECT_LOG.md` | keine | 11/11; SHA-256 `c8b6edcc7d79a077da8e2a8231e6756641873d5bb65c9114fb1327600672d1cb`; nativer Backup-Retry erfolgreich |
| SB-23-BACKUP | 2026-08-25 | Manuel | VPS staging | korrigierter manueller Backup-Lauf | PASS | operator output; `PROJECT_LOG.md` | synthetisch | read-only Tages- und Monatssatz erzeugt; Monitor separat fehlgeschlagen |
| SB-23-MON1 | 2026-08-25 | Manuel | VPS staging | OpenPGP-Validierung des erzeugten Satzes | FAIL CLOSED | Journal und native `--list-only`-Probe | synthetisch | Payload gueltig; Monitor versuchte ohne `--list-only` eine Entschluesselung ohne Private Key |
| SB-23-FIX2 | 2026-08-25 | Manuel | local / VPS staging | GnuPG-Monitor auf reine Paketpruefung korrigiert und installiert | PASS INSTALLED | Source/Test; `PROJECT_LOG.md` | keine | 11/11; SHA-256 `335da9998893240c7a284334f8a075d4d9f75776ce558d476e87522ed7a60bdd` |
| SB-23-MON2 | 2026-08-25 | Manuel | VPS staging | korrigierter Monitor gegen den nativen Satz | PASS | Journal/operator output | synthetisch | `Result=success`, Exit 0, Satz vollstaendig und verschluesselt; vier Dienste active |
| SB-23-COPY | 2026-08-25 | Manuel | VPS export / BitLocker `D:` | vollstaendiger owner-only Export und Guarded Pull | PASS | Guarded-Pull-Ausgabe; `PROJECT_LOG.md` | synthetisch verschluesselt | drei Checksummen OK; zwei `.gpg`-Nutzlasten; Remote-Export bis Restore erhalten |
| SB-23 | 2026-08-25 | Manuel | Wuerzburg / isolated Docker restore | Restore aus exakter externer Kopie | PASS REHEARSAL | `docs/operations/sb23-wuerzburg-execution.md`; Restore-Ausgabe | synthetisch | 24 Tabellen; Digest `sha256:bb3e1a57...dd825`; 12/12; null Container/Temp/Klartext; quartalsweise nach Echtdatenstart |
| SB-23-CLEAN | 2026-08-25 | Manuel | VPS export / BitLocker `D:` | temporaeren Remote-Export gezielt entfernt und externe Kopie erneut verifiziert | PASS | Operator-/Manifest-Ausgabe; `PROJECT_LOG.md` | synthetisch verschluesselt | Remote-Datumspfad abwesend; drei Checksummen auf `D:` OK; Backup/Monitor success; vier Dienste active |
| READINESS-20260825 | 2026-08-25 | Codex / Manuel | clean local source `70e92ba` | vollstaendiger Website-/Webapp-Release-Nachweis nach SB-23 | PASS LOCAL | Release-Builder, Astro-Ausgabe; `PROJECT_LOG.md` | keine/synthetisch | 305 pass, 14 skip; 38 Astro-Dateien, 28 Seiten; ZIP 33 Eintraege, Restore-Tool enthalten, keine `.env`/`.tmp`; SHA-256 `1db54187...be766` |
| CAL-0.1-ACCEPT | 2026-09-11 | Janay / Manuel | crawler-blocked Website review | Coachlinks, Angebotsgrenze und parallele Wochenendtermine | PASS ACCEPTED | `docs/requirements/janay-calendar-feedback-2026-09-10.md`; `PROJECT_LOG.md` | ausschliesslich synthetisch | Janay bewertet die Fassung als sehr gut; keine produktive Kalenderfreigabe |
| WEBSITE-LINK-GATE-20260911 | 2026-09-11 | Codex / Manuel | local production build / crawler-blocked review | interne Seiten-, Asset- und Sprungziele plus 404-Metadaten | PASS | `apps/website/scripts/verify-dist-links.mjs`; workflow `34577486065`; `PROJECT_LOG.md` | keine | erster Lauf stoppte an `/404/`; korrigierter Lauf prueft 1.137 Referenzen in 30 HTML-Dateien; oeffentlicher 404/noindex/canonical/OG-Smoke gruen |
| WEBSITE-20260911 | 2026-09-11 | Codex / Manuel | clean local source `5d126cbaec0e` | aktuelles statisches IONOS-Produktionsartefakt und crawler-blocked Review | PASS LOCAL / REVIEW DEPLOYED / IONOS NOT DEPLOYED | lokales Release-Artefakt und Manifest; Workflow `34582211406`; `PROJECT_LOG.md` | keine | 43 Astro-Dateien, 30 Seiten, 1.137 Referenzen, 51 ZIP-Eintraege, Pflichtdateien vorhanden; SHA-256 `8056d431...5269d4`; Deploymentflag false; Public-Smoke HTTP 200/noindex |
| OPS-D-20260911 | 2026-09-11 | Manuel | decision record | Pilot-Konten, Break-glass, Mailbox, Backup-Zeitplan, Retention, Benachrichtigung und Terminkorridor | PASS DECISION / NOT ACTIVATED | `docs/operations/pilot-account-operations-decisions-2026-09-11.md` | keine | Thomas Ross technisch; Janay ohne Mailboxvertretung; Benachrichtigungskanal wartet auf EXT-01 |
| CONTENT-20260911 | 2026-09-11 | Manuel / Content owner | local website | erster CP-Ruecklauf und begrenzte Mindforge-Zielgruppenanpassung | PASS PARTIAL / REVIEW PENDING | `docs/content/priority-a-stakeholder-decisions-2026-09-11.md`; Astro/build/link/mobile evidence in `PROJECT_LOG.md` | keine | CP-01/03/05/06 akzeptiert; CP-02/04/07 partiell; CP-08 offen; keine Ratgeberseite oder unbelegte Aussage |
| CAL-D-20260911 | 2026-09-11 | Janay / Manuel | requirements | CAL-D01 bis CAL-D08 und gesamter Pilotablauf | PASS BUSINESS / ADR WAITING | `docs/requirements/calendar-stakeholder-decisions-2026-09-11.md`; privater Word-Ruecklauf ausserhalb Git | keine | alle Punkte `Passt so`; keine Migration, Nachricht, Echtdaten oder Produktion autorisiert |
| MAIL-INV-20260911 | 2026-09-11 | Janay / Manuel | requirements inventory | zwoelf E-Mail-Prozessideen und Freigabegates | PASS INVENTORY / NOT AUTHORIZED | `docs/requirements/email-automation-template-inventory-2026-09-11.md` | keine | feste Reaktionszeit, Garantien, Erstattung, automatische Umbuchung, Marketing und Annahmekanal bleiben offen |
| EXT-01 | offen | EDV | production infrastructure | DNS/TLS/SMTP-Vertrag | WAITING | strukturierter EDV-Input | keine | keine Live-Mail/Produktivaktivierung |
| EXT-03 | offen | Manuel / Janay / Thomas | controlled pilot | Named-user-Abnahme und Go/No-Go | WAITING DATES PROPOSED | Onboarding-Protokoll | freigegebener Pilotmodus | 17.09. bevorzugt, 24.09. Fallback; Bestaetigung offen |
| EXT-04 | offen | Lars / Legal | public website | Betreiber, Rechtstexte und Freigabe | WAITING | Legal-Freigabe | keine | kein beworbener Livegang |
| G-PROD | offen | Thomas / Legal | production | dokumentiertes Go/No-Go | BLOCKED | Gate Board | keine | Termin wird neu geplant |

## Evidence-Regel

Jeder neue Eintrag nennt Gate, Datum, Owner, Umgebung, Nachweis, Ergebnis,
Fundstelle, Datenmodus und Recheck. Ein `PASS LOCAL` ersetzt keinen nativen
Betriebs- oder externen Restore-Nachweis.
