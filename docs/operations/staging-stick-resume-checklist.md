# Staging: Checkliste Bei Stick-Rueckkehr

Stand: 02.11.2026. Nur spaetere manuelle Wiederaufnahme, **jetzt nichts starten**.
Der Backupaufschub bleibt bis zu Manuels ausdruecklichem Signal bestehen. Diese
Checkliste ersetzt nicht das [kanonische Admin-Runbook](staging-admin-bootstrap-2026-10-30.md)
oder den [Backup-/Restorevertrag](../architecture/postgresql-backup-restore-runbook.md).
Keine ausfuehrbaren Befehle, kein Keyzugriff und kein neues Betriebs-PASS hier.

1. **Freigabe und Arbeitsplatz.** Manuelles Signal, Stick/privater Keyzugriff und
   geeigneter Windows-Benutzer/Rechner vorhanden? DPAPI ist rechner-/benutzergebunden.
   Anderer Rechner ist kein Anlass zum Key-Neuanlegen oder Kopieren privater
   Dateien ins Repo/Chat. Quellstand fuer das Fenster erneut aktuell pruefen und
   freigeben; dieser lokale Slice belegt keinen sauberen/gepushten Stand.
2. **Bestehende Keys zuerst nur lokal verifizieren.** Nach
   [vorbereiteter Wiederaufnahme](staging-admin-bootstrap-2026-10-30.md#lokal-vorbereitete-wiederaufnahme)
   die vorhandene DPAPI-/verschluesselte Kopie erhalten. Der gepruefte
   [Initializer](../../deploy/scripts/initialize-staging-operator-config.ps1)
   bietet `-ResumeExisting` (`Complete-StagingOperatorConfig`), nicht einen
   Resume-Schalter am Adminfenster. Schnittstelle: `StorageDirectory`,
   `FingerprintPath`, `ExpectedCorpusSha256`, `AllowedOrigin`, `GpgHome`,
   `GpgExecutable`, `AcknowledgeProtectedStorage`, `AcknowledgeOperatorCustody`.
   Die spaetere private Pinentry-/Speicherpruefung darf nur neue Verifikations-
   Metadaten erzeugen, keine Keys ersetzen. Bei vorhandenen Metadaten oder
   frueherem Anlageversuch separat aufklaeren; kein Reset/Blindretry. Erwartet:
   READY und unveraenderte Keys, **noch kein** DB-/Backup-/Adminnachweis.
3. **Aktuelles Backup und exakte Restoreprobe vor Admin.** Nach
   [Ablauf und Schutz](staging-admin-bootstrap-2026-10-30.md#ablauf-und-schutz)
   im spaeter freigegebenen Fenster neues verschluesseltes Vorher-Set,
   hashgepruefte externe exakte Kopie und isolierten Restore derselben Kopie
   einschliesslich Gleichheit/Bereinigung nachweisen. Off-Machine-Keybackup
   bleibt eigener Recovery-Gate; lokale READY-Metadaten oder alte Restorebelege
   ersetzen nichts. Nach Passwortabfragen Snapshot-/Restorebindung und maximal
   vier Stunden Alter erneut pruefen; bei Ablauf STOP statt Bypass.
4. **Erst dann genau ein Admin.** Das
   [Fensterskript](../../apps/webapp/scripts/run-staging-admin-window.ps1)
   hat aktuell nur `Execute`, `ExpectedSourceCommit`, `AcknowledgePrivateWindow`,
   `AcknowledgeQuietDatabase`, `AcknowledgeOperatorCustody`; ohne `Execute`
   startet es nichts. Spaetere Einmalbedienung gemaess
   [Runbook](staging-admin-bootstrap-2026-10-30.md#einmalige-bedienung), kein
   jetzt geratener Befehl/Commit. Echte MFA/Recovery/Session/RBAC, exakt admin
   only und Abschlussgesundheit/Bereinigung belegen. Kein Coach-/Calendarrecht;
   `registry_unavailable` bleibt moeglich. STOP/unklarer Commit: nicht wiederholen.
5. **real9 bleibt separater Gate.** Erst danach aktuellen Schema-/Themenbestand,
   MATCH_ONLY, Dry-Run, exakte Evidence-Bindung und separat abgenommenen
   Import-Orchestrator nach [Importvertrag](../architecture/coach-import-contract-v0.1.md)
   und [aktuellem Importstand](../architecture/coach3-existing-content-migration-plan-2026-10-23.md#backend-sprint-addendum-3010-neuer-aktueller-stand)
   pruefen und eigene Ausfuehrungsfreigabe einholen. Oeffentlicher realer APPLY
   bleibt hart deaktiviert, leere Themen sind kein Bootstrap-Auftrag. Kein
   Coach10 im Neuner-Manifest. Erst nach abgenommenem Import folgt
   [normales Coach-Onboarding](coach-post-migration-onboarding.md); Website- und
   Backenddeployments bleiben getrennt freizugeben.
