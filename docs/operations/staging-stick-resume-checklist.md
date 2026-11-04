# Staging: Checkliste Bei Stick-Rueckkehr

**Neueste Entscheidung04.11:** Statt des folgenden historischen August-Resume
gilt der [kontrollierte Backup-Key-Rebase](controlled-backup-key-rebase-2026-11-04.md).
Kein weiterer alter Passphraseversuch. Neue echte Schluessel/Recovery-Kopie erst
nach expliziter Freigabe; Anwendungen behalten ihre DPAPI-Keys. Backupziel,
aktueller Restore und genau ein Admin sind weitere getrennte Freigaben.

Aktuelle Eingrenzung04.11: ausschliesslich den
[lokalen Schluesselblock](local-staging-keys-2026-11-04.md) benutzen. Er akzeptiert
VERIFY/verify mit aeusseren Leerzeichen, endet nach der verschluesselten Kopie
und startet weder Backup noch Admin. Die folgenden fuenf Betriebsschritte sind
spaetere getrennte Gates, nicht durch die Schluesselbestaetigung genehmigt.

Stand: 04.11.2026. Das Signal liegt vor: Stick entsperrt/Passwoerter verfuegbar,
geschuetzter Betriebsweg freigegeben. [Aktueller einzelner Resume-Einstieg](staging-resume-2026-11-04.md)
mit getrennten VERIFY/BACKUP/ADMIN-Bestaetigungen; alte Befehle nicht wiederholen.
Kryptografische/Backup-/Admin-Ergebnisse bleiben bis zur echten Bedienung offen. Diese
Checkliste ersetzt nicht das [kanonische Admin-Runbook](staging-admin-bootstrap-2026-10-30.md)
oder den [Backup-/Restorevertrag](../architecture/postgresql-backup-restore-runbook.md).
Kein Keyzugriff oder neues Betriebs-PASS allein aus dieser Checkliste.

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
