# Geschuetzte Wiederaufnahme 04.11.2026

Lokale Implementierung/Nativprobe als `0260161` verpackt; Dokumentation separat.
Kein echter Betriebslauf durch das Packaging.

**Spaetere Korrektur04.11:** Dieser kombinierte Startablauf ist fuer den aktuellen
Auftrag abgeloest durch den [lokalen Schluesselblock](local-staging-keys-2026-11-04.md).
VERIFY jetzt tolerant/verstaendlich; neuer Einstieg endet nach GPG/verschluesselter
Kopie. Auch der kompatible alte Resume-Pfad startet kein Backup/Admin mehr.
Die folgende Vollfensterplanung und1315-Testevidenz bleiben historische Grenzen;
aktueller Auftrag startet keine Server-/Backup-/Adminaktion.

## Freigabe und Grenze

Manuel bestaetigt physischen Zugriff, entsperrtes `D:\CompetenceHub` und benoetigte
Passwoerter; danach ausdruecklich die Freigabe fuer den beschriebenen Betriebsweg.
Das ist keine Freigabe fuer COACH-3B REAL APPLY, reale Coachmigration, Live-Export,
weitere Rollen oder Deployment. Vor Backup und Admin-Anlage wird der konkrete
Betriebsblock im privaten Terminal erneut separat bestaetigt. Keine alten
Execute-Kommandos und keine Neuinitialisierung der bestehenden Schluessel.

## Tatsaechliche PostgreSQL-Probe

Der [lokale Runner](../../apps/webapp/scripts/run-coach-export-local.ps1) nutzt
nur Docker Desktop, das bereits gecachte gepinnte PostgreSQL16-Image, tmpfs,
127.0.0.1:55437 und `competence_hub_export_synthetic`. Bestehende Migrationen
0001-0009 wurden ausschliesslich in diesem eigenen Wegwerfcontainer ausgefuehrt,
nicht auf Staging/VPS. Generierte Testpasswoerter nur im Prozess/Standardinput,
keine Credentialdatei, kein Download, keine realen Coachdaten.

[Native Probe](../../apps/webapp/tests/test_coach_export_postgres_local.py):

- **1 nativer Test PASS**, vier getrennte Nachweisgruppen tatsaechlich ausgefuehrt.
- Echte Transaktion: `REPEATABLE READ`, `READ ONLY`, nach jedem Lauf beendet.
- Drei Wiederholungsexporte je Internal/Preview/Production byte-/hashgleich;
  bestehender COACH-4-Output exakt gleich, kein High-Attention-Diff.
- Alle Schema-Tabellen einschliesslich Zeilendaten **und xmin** vor/nach reinen
  Exporten sowie verweigerten Schreibversuchen unveraendert.
- Sieben direkte Schreibversuche auf Coach/Audit/Revision/Publication/Assets,
  einschliesslich INSERT/UPDATE/DELETE, vom echten PostgreSQL mit SQLSTATE25006
  abgewiesen; Rollback jeweils nachgewiesen. Der enge Lesefilter wurde im Test
  bewusst umgangen, damit die zweite Datenbank-Schutzschicht wirklich geprueft wird.
- Eine zweite Verbindung bestaetigt nach dem Coach-SELECT, aber vor Revision/
  Child-SELECTs einen neuen Entwurf samt Themen-/Angebots-/Qualifikationskindern
  und Versionsaenderung. Laufender Snapshot bleibt vollstaendig alt; erst der
  folgende Export sieht den neuen Entwurf. Kein bloss simulierter Zeitablauf.
- Exakter eigener Container nach jedem Versuch entfernt und per Container-ID
  nochmals auf Abwesenheit geprueft; Port55437 frei. Keine fremden Container
  beendet. tmpfs verschwindet mit dem Container, Prozessvariablen entfernt.

Die erste neue Fixture hatte den erforderlichen `public_profile_status` nicht
gesetzt; korrigiert wurde nur der synthetische Aufbau, nicht das Schema oder der
Adapter. Die staerkere Parallelprobe nutzt jetzt die wirklich unterstuetzten
Revisionsschreibwege. Auch fehlgeschlagene Proben wurden vollstaendig bereinigt.
Letzte native Schlussmeldung:

```text
COACH_EXPORT_NATIVE=PASS CONTAINER_REMOVED=PASS PORT55437_CLEAR=PASS REAL_DATA=NONE
```

Das ist lokale native SQL-Evidenz, kein Staging-/real9-/Live-Export-Nachweis.
Der [Exportvertrag](../architecture/coach-read-only-export-contract-v0.1.md)
behaelt die festen Ziel- und Publication-Grenzen.

## Metadatenpruefung Ohne Keyinhalt

Vorhanden: DPAPI-Datei und verschluesselte portable Kopie. Fehlend:
Verifikationsmetadaten und `bootstrap-attempt.json`. Beide bestehenden Dateien
und ihr Verzeichnis bestehen die Eigentums-/privaten ACL-/Pfadpruefung; keine
Keyinhalte gelesen, kein GPG/PIN-Dialog und keine Kryptoverifikation ausgefuehrt.
Beide Anfangsdateien sind nicht leer (nur Dateilaenge geprueft). USB-Verzeichnis,
bekannter lokaler GPG-Ordner und Corpus vorhanden. Bestehender
genehmigter Logininput vorhanden, Inhalt nicht erneut in Chat/Reports geladen.
Die Verfuegbarkeit eines Ordners ist kein Schluesselnutzbarkeitsnachweis.

## Ein Privates Terminalfenster

Neuer [Resume-Einstieg](../../apps/webapp/scripts/resume-staging-admin-window.ps1),
ohne Execute definition-only. Exakten geprueften/gepushten Quellcommit benutzen;
der Einstieg prueft HEAD, kanonischen Remote und alle ausfuehrbaren Pfade.
Manuel startet ihn selbst in **einem** PowerShell7-NoProfile-Fenster; keine
Transkripte, Bildschirmaufnahmen oder geteilten Bildschirme. Der Abschluss im
Chat liefert den einen vollstaendigen Befehl, keinen Platzhalter-/Altbefehl.

1. `VERIFY`: bestehendes Paar erforderlich. Fehlende Metadaten ausschliesslich
   durch `Complete-StagingOperatorConfig` / den vorgesehenen Resume-Weg
   vervollstaendigen. Bereits vorhandene Metadaten verifizieren, nicht ersetzen.
   DPAPI/GPG-Vergleich nur im lokalen Prozess, GPG-Pinentry ausschliesslich durch
   Manuel. Kein Initializer-Neuanlegen, keine Rotation, kein Rechnerwechsel-
   Fallback. Nach Erfolg bestehende **verschluesselte** portable Keykopie nach
   `D:\CompetenceHub\staging-operator-key-backups\<ciphertext-sha256>.keys.json.gpg`
   kopieren und Hash gegen die verifizierten nicht geheimen Metadaten pruefen;
   Quelle vor/nach dem Kopieren erneut binden. Vorhandene identische Kopie nur pruefen; andere/
   unvollstaendige Kopie niemals ueberschreiben. Keine DPAPI-/Klartext-/privaten
   GPG-Schluesseldateien auf den Stick kopieren. Bei Fehler STOP/Originale erhalten.
2. `BACKUP`: eigener neuer verschluesselter Vorher-Snapshot exakt auf dem bekannten
   VPS fuer `competence_hub_staging`; aktueller ruhiger DB-/DDL-/Rollenbestand
   muss von Manuel bestaetigt werden. Bestehende Backupjobs/Retention bleiben
   unveraendert. Geschuetzte NTFS-Kopie ausserhalb Repository, dieselbe exakte
   Kopie isoliert lokal restaurieren, Vollbaseline vergleichen, eigene Restore-
   Ressourcen entfernen. Originalset/verschluesselte Kopie behalten; keine
   produktive DB ersetzen. Kein Admin bei unvollstaendigem oder veraltetem Beleg.
3. `ADMIN`: erst nach erfolgreicher aktueller Backup-/Restorepruefung und eigener
   Bestaetigung. Genau ein Manuel-Admin mit bestehendem genehmigtem Login, keine
   Coach-/Reviewer-/Internal-/Contact-/Calendar-Zuordnung. Verdeckte DB-/persoenliche
   Passwortabfragen nur lokal. Eigenes Edge/HTTPS-Fenster fuer MFA, sichere private
   Recovery-Ablage, Login/Session/Logout, einmaliger Recoveryverbrauch und
   Wiederverwendungsablehnung, Audit/RBAC/Abschlussgesundheit und Bereinigung.

Jeder Block nennt Ziel, Operationen und Rueckfallgrenze vor Ausfuehrung. Ablehnung
stoppt. Unklarer Kontocommit bleibt erhalten und muss separat untersucht werden;
kein automatisches Loeschen/Neuanlegen und kein ungenehmigtes DB-Restore.
Secrets niemals Chat, Shellargument, History, Report, Git oder Logs. Nur die
bereinigte Schlussmeldung zurueckmelden; private Ergebnisdateien nicht senden.
Fehlerausgabe nennt nur eine feste Phase, nie private Exceptiondetails.

Das [bestehende Admin-Runbook](staging-admin-bootstrap-2026-10-30.md) und der
[Backup-/Restorevertrag](../architecture/postgresql-backup-restore-runbook.md)
gelten weiter. Die Registry bleibt im lokalen Admin-Runtime bewusst unkonfiguriert;
503 `registry_unavailable` nach korrekter Autorisierung ist keine Freigabe zur
Backendaktivierung. Vier ko-gehostete Dienste/PG-Loopback werden ohne Neustart
geprueft; Webapp-Auth wird nativ im eigenen privaten Runtime-Kontext getestet,
nicht als produktiv aktivierter Dienst ausgegeben.

## Aktueller Gate-Stand

| Gate | Tatsaechlicher Stand vor Manuels privater Bedienung |
| --- | --- |
| Lokale PostgreSQL-Probe | PASS, eigener Container/Listener entfernt |
| Alte Keydateien/Pfad/ACL | Vorhanden/PASS; Inhalte unberuehrt |
| Kryptografische Keypruefung und USB-Keybackup | NOT EXECUTED, geschuetzte Interaktion erforderlich |
| Aktuelles echtes Backup / exakter Restore | NOT EXECUTED |
| Echter Staging-Admin / MFA / Recovery / Audit / RBAC | NOT EXECUTED |
| Aktuelle VPS-/Webapp-/Dienstgesundheit | Nicht neu geprueft; nach Betriebsblock nachzuweisen |
| Real Coach APPLY / Migration / Live-Export / Deployment | DISABLED / NOT EXECUTED |

Lokale vollstaendige Regression:1315 PASS/30 erwartete Opt-in-Skips. Der neue
native SQL-Test wurde separat mit Erfolg ausgefuehrt.12 neue Resume-/Datei- und
Zustimmungsfaelle ausschliesslich synthetisch; fokussiert178 PASS. Python-
Kompilierung, pip check und PowerShell-Syntaxpruefung aller3 betroffenen Skripte
PASS. Abschliessender Vollsuite-Lauf nach Hashbindungs-Haertung erneut1315/30;
JUnit bleibt ignoriert in `.tmp/coach4/resume-preparation-final-20261104.xml`.
Dokumentintegritaet7 Archive/21 Router/229 Links sowie58 gezielte Links PASS,
`git diff --check` PASS. Website-/Migrationsquellen unveraendert.
Native SQL-Probe und private Dateien-/Zustimmungsfaelle sind getrennte Evidenz.
Keine globalen Skills oder Quellen gelesen/geaendert. Unbekannte Arbeitsdateien
und bestehende Key-/Backupdateien bleiben erhalten.

## Genau Ein Naechster Block

Jetzt: dieses geschuetzte Resume-/Backup-/Adminfenster mit Manuels lokalen
Eingaben. Inputs: aktuelle gepruefte/gepushte Vorbereitung, vorhandene Keys,
Stick/Passwoerter und bestehender Logininput. Deliverable: echte Key-/Backup-/
Restore-/Admin- und Gesundheitsaussage ohne Rollenexpansion. DoD: alle genannten
nativen Nachweise und eigenen Cleanup-Gates PASS. Erst **danach** ist COACH-3B
REAL APPLY als naechster separat freizugebender Block zu empfehlen; aktuell
sind seine vorgeschalteten realen Gates noch nicht bestanden.
