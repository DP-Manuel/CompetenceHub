# Go-Live Evidence Index

Stand: 2026-08-25

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
| EXT-01 | offen | EDV | production infrastructure | DNS/TLS/SMTP-Vertrag | WAITING | strukturierter EDV-Input | keine | keine Live-Mail/Produktivaktivierung |
| EXT-03 | offen | Manuel / Janay / Thomas | controlled pilot | Named-user-Abnahme und Go/No-Go | WAITING | Onboarding-Protokoll | freigegebener Pilotmodus | Termin offen |
| EXT-04 | offen | Lars / Legal | public website | Betreiber, Rechtstexte und Freigabe | WAITING | Legal-Freigabe | keine | kein beworbener Livegang |
| G-PROD | offen | Thomas / Legal | production | dokumentiertes Go/No-Go | BLOCKED | Gate Board | keine | Termin wird neu geplant |

## Evidence-Regel

Jeder neue Eintrag nennt Gate, Datum, Owner, Umgebung, Nachweis, Ergebnis,
Fundstelle, Datenmodus und Recheck. Ein `PASS LOCAL` ersetzt keinen nativen
Betriebs- oder externen Restore-Nachweis.
