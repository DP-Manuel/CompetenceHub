# SB-23 Wuerzburg Execution

Stand: 2026-08-25

Ziel ist der technische Nachweis eines verschluesselten Off-Server-Backups mit
synthetischen Staging-Daten und Restore aus exakt dieser externen Kopie. Dieses
Dokument autorisiert weder Echtdaten noch Deployment oder Produktion.

## Aktueller Precheck

- `D:`: gesundes, fast leeres 2-GB-USB-Wechselmedium, FAT, D+P-Kandidat.
- BitLocker To Go ist aktiv: `FullyEncrypted`, Schutz aktiv, `Aes128`,
  100 Prozent, `Unlocked`.
- Das lokale Systemlaufwerk `C:` ist ebenfalls `FullyEncrypted`, Schutz aktiv,
  `XtsAes128`, 100 Prozent. Der private GPG-Key darf deshalb im geschuetzten
  lokalen Benutzerprofil der Restore-Umgebung liegen.
- Der USB-Stick wird im Safe verwahrt. Janay Rappelt ist als Notfall-/Recovery-
  Verantwortliche benannt. Der Recovery-Code selbst bleibt ausserhalb von Git,
  Chat, Excel und Projektdateien.
- Passwort- und RecoveryPassword-Protector wurden bestaetigt. Recovery-Code
  und GPG-Passphrase sind sicher hinterlegt; ihre Werte wurden nicht uebermittelt
  oder dokumentiert.
- `manage-bde.exe`, `ssh.exe` und `scp.exe` sind vorhanden.
- Gpg4win 5.1.0 wurde ueber den Windows-Paketmanager installiert; der
  Installer-Hash wurde durch Winget geprueft. Verfuegbar ist GnuPG 2.5.21 unter
  `C:\Program Files\GnuPG\bin\gpg.exe`.
- Die fokussierten Betriebspakettests bestehen mit 11/11.

Der Stick ist nur fuer den synthetischen Rehearsal vorgesehen. Zwei GB sind
kein belastbarer langfristiger Kapazitaetsplan.

## Gate A: Datentraeger verschluesseln

Dieser Schritt muss in einer **als Administrator gestarteten PowerShell** durch
Manuel erfolgen, weil das Passwort geheim eingegeben wird. Vorher sicherstellen,
dass `D:` weiterhin der leere vorgesehene USB-Stick ist.

```powershell
Get-Volume -DriveLetter D |
  Select-Object DriveLetter, FileSystemLabel, FileSystem, DriveType,
    HealthStatus, Size, SizeRemaining

$BitLockerPassword = Read-Host `
  "Neues starkes BitLocker-Passwort fuer den Backup-Stick" `
  -AsSecureString

Enable-BitLocker `
  -MountPoint 'D:' `
  -EncryptionMethod Aes256 `
  -PasswordProtector `
  -Password $BitLockerPassword `
  -UsedSpaceOnly

do {
  Start-Sleep -Seconds 2
  $Status = Get-BitLockerVolume -MountPoint 'D:'
  $Status |
    Select-Object MountPoint, VolumeStatus, ProtectionStatus,
      EncryptionMethod, EncryptionPercentage, LockStatus
} until ($Status.VolumeStatus -eq 'FullyEncrypted')

Remove-Variable BitLockerPassword
```

Das Passwort niemals in Chat, Git, Excel, Projektlog oder `.env` eintragen.
Ein Recovery-Key-Protector wird erst angelegt, wenn ein D+P-kontrollierter
Aufbewahrungsort und ein Recovery-Owner feststehen. Bis dahin bleibt das
langfristige Betriebsgate offen.

## Gate B: Verschluesselung nachweisen

Die folgende Ausgabe darf nur Statusmetadaten enthalten, niemals Protector-
Details oder Recovery Keys:

```powershell
Get-BitLockerVolume -MountPoint 'D:' |
  Select-Object MountPoint, VolumeType, VolumeStatus, ProtectionStatus,
    EncryptionMethod, EncryptionPercentage, LockStatus
```

Erwartet und erreicht: `FullyEncrypted`, `On`, eine durch lokale Richtlinie
zugelassene AES-Methode, `100`, `Unlocked`. Windows hat auf diesem Rechner
`Aes128` angewendet. Die Backup-Nutzlast wird zusaetzlich mit OpenPGP
verschluesselt.

## Gate C: GPG-Werkzeug und Key Custody

Vor der Schluesselerzeugung ist eine kontrollierte GPG-Installation oder eine
andere genehmigte Restore-Umgebung festzulegen. Der private Backup-Key wird nur
dort erzeugt und bleibt ausserhalb von VPS, Git, Chat und Projektdateien. Auf
den VPS gelangt ausschliesslich der gepruefte Public Key; dokumentiert wird nur
sein 40-stelliger Fingerprint.

Das Werkzeug und der verschluesselte lokale Key-Ablageort sind bereit. Vor dem
Transfer werden der BitLocker-Recovery-Code im Safe hinterlegt, der GPG-Key
interaktiv mit eigener Passphrase erzeugt und nur der Public Key exportiert.
Gate C wird nicht durch ein improvisiertes Online-Tool, eine Website oder einen
auf dem VPS erzeugten Private Key umgangen.

Key-Evidence vom 25.08.2026:

- RSA 4096, fuer Verschluesselung geeignet, Ablauf 24.08.2028.
- Public Fingerprint:
  `2E44306121629A100F76A8B08CCA3D9186A28D4C`.
- Public Export:
  `D:\CompetenceHub\public-key\competence-hub-backup-public.asc`.
- SHA-256 des Public Exports:
  `1579983D981DBA4A674B464B84DECA16E3C97A034C049B85E21B6458D71605F6`.
- Der private Key liegt nur im geschuetzten lokalen GPG-Home auf `C:`. Die
  USB-Inventur enthaelt ausschliesslich das Verzeichnis `public-key` und den
  1717-Byte-Public-Export.

VPS-Handoff vom 25.08.2026:

- Public Key nach `/home/manuel/competence-hub-backup-public.asc` uebertragen;
  SHA-256 stimmt mit dem USB-Export ueberein, Owner `manuel`, Modus `0600`.
- Die drei Scripts, die secret-freie Konfigurationsvorlage und vier systemd-
  Vorlagen liegen unter
  `/home/manuel/competence-hub-backup-install-20260825`.
- Alle acht lokalen und entfernten SHA-256-Hashes stimmen ueberein. Das
  Stagingverzeichnis ist `0700`, die Dateien sind `0600`.
- Noch keine Installation, Unit-Aktivierung oder Backup-Ausfuehrung.

Native Installation vom 25.08.2026:

- Public-only GPG home fuer `postgres` angelegt und exakt der freigegebene
  Fingerprint importiert; keine Private-Key-Warnung.
- Root-owned Scripts, `root:postgres`-Konfiguration und vier systemd-Units
  installiert; `systemd-analyze verify` ohne Fehler.
- Backup- und Monitor-Timer bleiben bewusst `disabled`.
- Chatbot, Nginx, Fail2ban und PostgreSQL blieben `active`.
- Noch kein manueller Backup-Lauf, Export oder Restore.

Erster manueller Lauf und Fix vom 25.08.2026:

- Der Dienst brach vor Publikation mit `Permission denied` beim Verschieben des
  Arbeitsverzeichnisses in `daily/2026-08-25` ab. Cleanup hinterliess keinen
  Klartext und keinen partiellen Backup-Satz.
- Ein minimaler Rename-Test als `postgres` reproduzierte den Fehler ausserhalb
  systemd. Owner/Modi, ext4 `rw`, systemd `ReadWritePaths` und Kernel-Log waren
  unauffaellig. Ursache war `chmod 0500` auf dem Arbeitsverzeichnis vor dem
  Verzeichniswechsel.
- Der lokale Fix verschiebt zuerst und setzt danach `0500` auf dem finalen Satz;
  ein Fehler bei diesem letzten Schritt loest gezieltes Cleanup aus. Der
  fokussierte Test meldet 11/11.
- Das korrigierte Skript ist unter
  `/home/manuel/competence-hub-backup-install-20260825/competence-hub-postgres-backup.20260825-fix1`
  mit Modus `0600` abgelegt. Lokaler und entfernter SHA-256:
  `c8b6edcc7d79a077da8e2a8231e6756641873d5bb65c9114fb1327600672d1cb`.
  Der native `bash -n`-Check dieser Datei ist erfolgreich.
- Der fehlgeschlagene Diagnoseversuch hinterliess genau das Verzeichnis
  `.rename-probe-L83nbf`; es wird vor dem Wiederholungslauf gezielt entfernt.
- Fix 1 wurde installiert und der Wiederholungslauf war erfolgreich; Transfer
  und Restore sind noch offen.

Backup-Erfolg und Monitor-Fix vom 25.08.2026:

- Nach Installation von Fix 1 meldete die Backup-Unit `Result=success` und
  `ExecMainStatus=0`. Tages- und Monatssatz sind vollstaendig, read-only und
  enthalten je zwei `.gpg`-Nutzlasten, `METADATA`, `SHA256SUMS` und `COMPLETE`.
- Der Monitor scheiterte bei `gpg --list-packets`, weil die reine Paketpruefung
  ohne den absichtlich nur am Wuerzburger Rechner vorhandenen Private Key nicht
  erzwungen wurde. Die native Probe mit `--list-only` lieferte Exitcode 0 und
  erkannte das Public-Key-Verschluesselungspaket.
- Fix 2 verwendet `--no-tty --list-only --list-packets`; 11/11 fokussierte Tests
  und remote `bash -n` sind erfolgreich. Die gestagte Datei ist
  `/home/manuel/competence-hub-backup-install-20260825/competence-hub-postgres-backup-monitor.20260825-fix2`,
  SHA-256
  `335da9998893240c7a284334f8a075d4d9f75776ce558d476e87522ed7a60bdd`.
- An diesem Zwischenstand waren Fix-2-Installation und Monitor-Retry noch offen.
  Der erfolgreiche Backup-Satz blieb unveraendert; ein erneuter Backup-Lauf war
  nicht erforderlich.

Monitor-Retry vom 25.08.2026:

- Fix 2 wurde installiert. Die Monitor-Unit meldete `Result=success`,
  `ExecMainStatus=0` und bestaetigte den Satz `2026-08-25` als vollstaendig,
  verschluesselt und 307 Sekunden alt.
- Chatbot, Nginx, Fail2ban und PostgreSQL blieben `active`.
- Der vorhandene Satz bleibt unveraendert. Naechster Schritt ist die temporaere
  owner-only Exportkopie und der Guarded Pull auf das BitLocker-Laufwerk `D:`.

Guarded Pull vom 25.08.2026:

- Der owner-only Export unter
  `/home/manuel/competence-hub-backup-export/2026-08-25` bestand alle drei
  Manifestpruefungen und enthielt kein Klartextmaterial.
- Das Guarded-Pull-Skript erstellte und verifizierte
  `D:\CompetenceHub\competence-hub-backups\2026-08-25`. Zwei `.gpg`-Nutzlasten,
  `METADATA`, `SHA256SUMS` und `COMPLETE` sind vorhanden; alle drei Checksummen
  stimmen. Der Remote-Export bleibt bis zum akzeptierten Restore erhalten.
- Lokal ist Docker Desktop vorhanden, aber kein PostgreSQL-16-Image. Ein Pull
  des offiziellen Images wurde wegen der geltenden Grenze gegen externe
  Provider nicht ausgefuehrt. Vor dem Restore ist der Laufzeitweg explizit zu
  entscheiden; der private Backup-Key bleibt auf dem Wuerzburger Rechner.

Exact-Copy-Restore vom 25.08.2026:

- Manuel gab den einmaligen Download des offiziellen Images
  `postgres:16-bookworm` ausdruecklich frei. Es wurden keine Projekt- oder
  Backupdaten an Docker Hub uebertragen. Verwendeter Digest:
  `sha256:bb3e1a57e5407e0a5280b4211980a5e537f4abd234a87014ac979849a78dd825`.
- Die externe `D:`-Kopie bestand vor dem Restore erneut alle drei Checksummen.
  Der Private Key und die Passphrase blieben lokal; Klartext lag nur temporaer
  im ACL-geschuetzten Verzeichnis auf BitLocker-`C:`.
- Ein PostgreSQL-16-Container ohne Netzwerk und Portfreigabe stellte ein
  `competence_hub`-Schema mit 24 Tabellen wieder her. Der synthetische Snapshot
  enthielt null Portalnutzer.
- Der Ablauf wurde mit dem neuen, digest-gepinnten und implizite Pulls
  verbietenden `restore-competence-hub-backup-docker.ps1` wiederholt. Beide
  Restores waren erfolgreich; 12/12 fokussierte Tests und der PowerShell-Parser
  sind gruen.
- Abschlussinventur: null Restore-Container, null temporaere Restoreverzeichnisse
  und null Klartext-Dumps. Chatbot, Nginx, Fail2ban und PostgreSQL blieben
  `active`.
- SB-23 ist fuer den synthetischen Rehearsal-Scope abgeschlossen. Remote-Export
  wird erst nach expliziter Cleanup-Freigabe entfernt; die `D:`-Kopie bleibt im
  Safe. Produktionszeitplan/Alarmierung, Legal, Konten und Go/No-Go bleiben
  separate Echtdaten- und Produktionsgates.

Abschluss-Cleanup vom 25.08.2026:

- Manuel gab die Loeschung exakt des temporaeren Pfads
  `/home/manuel/competence-hub-backup-export/2026-08-25` frei.
- Ein erster Aufruf wurde vor Remote-Ausfuehrung durch lokale PowerShell-
  Substitution gestoppt. Der korrigierte Literalpfad-Aufruf verifizierte beide
  aufgeloesten Pfade, entfernte nur das freigegebene Datumsverzeichnis und
  bestaetigte dessen Abwesenheit.
- Originales VPS-Backup und externe `D:`-Kopie blieben bestehen. Die drei
  externen Checksummen sind erneut gruen; Backup/Monitor melden Erfolg und alle
  vier Dienste sind `active`.
- SB-23 ist damit ohne offene temporaere Exportkopie abgeschlossen.

## Gates D bis F

Nach A bis C folgen ausschliesslich nach erneutem Operator-Check:

1. SB-21-Scripts und systemd-Units nativ auf dem VPS validieren.
2. Einen synthetischen verschluesselten Backup-Satz erzeugen und monitoren.
3. Den vollstaendigen datierten Satz per Guarded Pull nach `D:` kopieren.
4. SHA-256 vor und nach Transfer vergleichen.
5. Aus genau dieser externen Kopie isoliert wiederherstellen und aufraeumen.
6. PostgreSQL localhost-only sowie Chatbot, Nginx, Fail2ban und PostgreSQL als
   gesund nachweisen.
7. Evidence Index, Gate Board und Projektstatus synchronisieren.

Kein Schritt verwendet reale Unternehmens- oder Personendaten.
