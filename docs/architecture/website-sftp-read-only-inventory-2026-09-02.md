# Website SFTP Read-only Inventory

Stand: 2026-09-02

## Zweck und Grenze

Diese Akte dokumentiert die einmalige, strikt lesende Bestandsaufnahme des
IONOS-Webroots vor jedem Website-Release. Die Inventur darf Verzeichnisse und
Dateinamen anzeigen, aber keine Datei hochladen, herunterladen, umbenennen,
loeschen oder bearbeiten.

Zugangsdaten bleiben ausserhalb von Git, Projektdateien, Kommandozeilen und
Chat. Benutzername und Passwort werden nur interaktiv in Manuels lokalem
Terminal eingegeben.

## Verifiziertes Ziel

- SFTP-Host: bestaetigter IONOS-Providerhost im privaten Zielvertrag
- Port: `22`
- Beobachteter Server-Banner: `OpenSSH_10.0p2`
- Host-Key-Typ: `ED25519`
- Beobachteter Fingerprint:
  `SHA256:1gx2w8Rtv3wCgi7Jh8myf/KVd72cRQbow03UP8P095Q`
- Unabhaengige Vertrauensquelle: offizielle IONOS-Uebersicht der
  SSH-Fingerabdruecke im Webhosting:
  <https://www.ionos.de/hilfe/hosting/ssh-zugaenge-einrichten-und-verwalten/uebersicht-der-ssh-fingerabdruecke-im-ionos-webhosting/>
- Ergebnis: Der beobachtete ED25519-Fingerprint stimmt exakt mit der
  offiziellen IONOS-Angabe ueberein. Das Host-Key-Gate ist geschlossen.

Die Erfassung erfolgte ohne Benutzername des echten Kontos, ohne Passwort und
ohne Benutzerschluessel. Der Windows-`ssh-keyscan` konnte den vom Server zuerst
angebotenen neueren KEX nicht verarbeiten. Ein isolierter OpenSSH-Probeaufbau
mit `curve25519-sha256`, deaktivierter Passwort-/Schluesselanmeldung und eigener
temporarer `known_hosts`-Datei lieferte den oben dokumentierten ED25519-Key.

## Interaktive Nur-Lese-Inventur

In einer lokalen PowerShell aus dem Repository-Root ausfuehren:

```powershell
$SftpUser = Read-Host 'IONOS SFTP-Benutzername'
$SftpHost = Read-Host 'IONOS SFTP-Host aus dem privaten Zielvertrag'

sftp `
  -P 22 `
  -o KexAlgorithms=curve25519-sha256 `
  -o HostKeyAlgorithms=ssh-ed25519 `
  -o StrictHostKeyChecking=ask `
  "${SftpUser}@${SftpHost}"
```

Beim ersten Verbindungsaufbau nur dann mit `yes` bestaetigen, wenn exakt dieser
Fingerprint angezeigt wird:

```text
SHA256:1gx2w8Rtv3wCgi7Jh8myf/KVd72cRQbow03UP8P095Q
```

Danach das Passwort ausschliesslich in der verdeckten Passwortabfrage des
SFTP-Clients eingeben. Am `sftp>`-Prompt zunaechst nur diese Befehle ausfuehren:

```text
pwd
ls -la
```

Die Ausgabe ohne Benutzername oder sonstige Zugangsdaten zur Klassifikation
bereitstellen. Unterverzeichnisse werden anschliessend mit weiteren
`cd`-/`ls -la`-Befehlen einzeln gelesen, bis die Inventur vollstaendig ist.

## Verbotene Befehle und Stop-Regeln

- Keine Befehle wie `put`, `mput`, `rm`, `rmdir`, `mkdir`, `rename`, `chmod`,
  `chown`, `symlink` oder `ln` verwenden.
- Noch kein `get` oder rekursiver Download; das datierte Rollback-Backup ist
  eine spaetere Phase mit separater Aenderungsfreigabe.
- Bei abweichendem Fingerprint sofort abbrechen und kein Passwort eingeben.
- Bei unerwartetem Startverzeichnis, unbekannten Providerdateien, `.htaccess`,
  Symlinks oder mehreren moeglichen Document Roots stoppen und klassifizieren.
- Der private Zielvertrag darf `remote_web_root_verified` erst nach der
  vollstaendigen Inventur auf `true` setzen.

## Noch Auszufuellende Evidenz

- Authentifizierung mit dem echten SFTP-Konto: erfolgreich am 2026-09-03;
  OpenSSH meldete `Authenticated ... using "password"`.
- SFTP-Subsystem: vom Server angenommen, danach sofortiges EOF und
  `Connection closed`.
- Read-only SSH-Diagnose: Authentifizierung erneut erfolgreich; der Server
  meldete, dass das zugewiesene Home-Verzeichnis unter dem kontospezifischen
  IONOS-Pfad mit dem Ziel `/htdocs/projektwue` nicht existiert. Das
  Konto ist erwartungsgemaess per `rssh` auf SFTP beschraenkt.
- Root Cause: serverseitig fehlendes oder falsch zugewiesenes
  SFTP-Startverzeichnis. Die Restriktion auf SFTP soll nicht aufgehoben werden.
- `pwd`-Ausgabe: durch den serverseitigen Pfadfehler blockiert
- Vollstaendige Verzeichnisinventur inklusive versteckter Eintraege: offen
- Tatsaechlicher Document Root fuer beide Subdomains: offen
- Klassifikation vorhandener Provider-/Konfigurationsdateien: offen
- Abgleich mit dem privaten SFTP-Zielvertrag: offen
- Upload, Remote-Backup, Deployment und Real-Daten-Nutzung: nicht erfolgt

Naechster Gate-Schritt: EDV korrigiert oder bestaetigt das Startverzeichnis und
die Document-Root-Zuordnung beider Domains. Danach wird nur `pwd` und `ls -la`
erneut ausgefuehrt. Die vorbereitete Nachricht steht in
`edv-sftp-webroot-fix-request-2026-09-03.md`.
