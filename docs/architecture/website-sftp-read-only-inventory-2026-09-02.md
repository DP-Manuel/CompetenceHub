# Website SFTP Read-only Inventory

Stand: 2026-09-21

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

- Thomas Ross bestaetigte per E-Mail, dass beide Subdomains auf
  `/kunden/homepages/16/d101506010/htdocs/competencehub` zeigen und der
  SFTP-Benutzer auf diesen Pfad zugreifen kann. Die serverseitige Zuordnung ist
  damit bestaetigt.
- Der authentifizierte read-only Gegencheck am 21.09. war erfolgreich. SFTP
  zeigt den bestaetigten Webroot als abgeschottetes Startverzeichnis `/`.
- `ls -la` zeigte neben `.` und `..` ausschliesslich `index.php` mit 64 Byte;
  keine weitere sichtbare oder versteckte Providerdatei war vorhanden.
- Der oeffentliche Seitentitel `PHP 8.4.24 - phpinfo()` ordnet diese Datei der
  Diagnoseausgabe zu. Der Inhalt wurde nicht heruntergeladen oder veraendert.

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
- `pwd`-Ausgabe: `/` als SFTP-Chroot des bestaetigten physischen Webroots
- Vollstaendige Verzeichnisinventur inklusive versteckter Eintraege: bestanden
- Tatsaechlicher Document Root fuer beide Subdomains: durch Thomas bestaetigt
- Klassifikation vorhandener Provider-/Konfigurationsdateien: nur die
  64-Byte-`index.php`-Diagnosedatei vorhanden
- Abgleich mit dem privaten SFTP-Zielvertrag: bestanden
- Upload, Remote-Backup, Deployment und Real-Daten-Nutzung: nicht erfolgt

Die EDV schloss diesen Befund am 22.09.2026: Thomas Ross bestaetigte, dass die
`index.php` nur einem kurzen Test diente, und entfernte sie. HTTP-zu-HTTPS und
Alias-zu-Kanonisch duerfen per `.htaccess` umgesetzt werden. Das gepruefte
statische Artefakt enthaelt diese Regeln bereits.

Naechster Gate-Schritt: Unmittelbar vor einem freigegebenen Upload die nun
leere Remote-Ausgangslage erneut read-only inventarisieren und als datierten
Rollbacknachweis sichern. Bis zur separaten Remote-Change-Freigabe erfolgt
keine Aenderung.

## Oeffentlicher Gegencheck 2026-09-03

- Beide Subdomains liefern dieselbe IONOS-IPv4- und IPv6-Adresse.
- HTTPS validiert fuer das ausgelieferte Wildcard-Zertifikat; das Zertifikat
  nennt `*.donner-partner.de` und `donner-partner.de` und ist vom 2026-05-22
  bis 2026-12-02 gueltig.
- HTTP und HTTPS antworten auf beiden Subdomains mit `403 Forbidden` und einer
  IONOS-Parkingseite.
- Die Bindestrich-Variante leitet noch nicht auf die kanonische Domain um;
  HTTP leitet noch nicht auf HTTPS um.

Das bestaetigt DNS und TLS nur teilweise. Es beweist keinen nutzbaren Webroot
und keine releasefaehige Domain-Zuordnung. Bis zur EDV-Korrektur erfolgt kein
Upload in ein erratenes Alternativverzeichnis.

## Oeffentlicher Gegencheck 2026-09-21

- HTTP und HTTPS antworten auf beiden Subdomains mit Status 200.
- Beide Subdomains liefern als Seitentitel `PHP 8.4.24 - phpinfo()` aus. Diese
  oeffentliche Konfigurationsausgabe ist ein P0-Stopper und muss vor einem
  Website-Upload entfernt oder gesperrt werden.
- HTTP leitet weiterhin nicht auf HTTPS um.
- Die Bindestrich-Variante leitet weiterhin nicht auf die kanonische Domain
  `competencehub.donner-partner.de` um.
- Der Gegencheck veraenderte keine Remote-Datei und beweist weiterhin nicht den
  gemeldeten Webroot.

## Oeffentlicher Gegencheck 2026-09-22

- Nach der EDV-Entfernung antworten HTTP und HTTPS auf der kanonischen und der
  Bindestrich-Domain mit Status `403` und ohne `phpinfo()`-Titel oder
  Konfigurationsausgabe.
- Damit ist der Sicherheitsbefund der temporaeren Diagnose-Datei geschlossen;
  die `403`-Antwort ist vor dem Erst-Upload die erwartete leere Webspace-Lage.
- Redirects sind noch nicht aktiv, weil die freigegebenen `.htaccess`-Regeln
  erst mit dem statischen Website-Artefakt ausgeliefert werden.
- Der Gegencheck fuehrte keinen SFTP-Write, Upload oder sonstigen Remote-Change
  aus.
