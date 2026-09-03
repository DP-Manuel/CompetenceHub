# EDV-Nachfrage: SFTP-Startverzeichnis

Stand: 2026-09-03

Status: Versand durch Manuel ausstehend.

## Betreff

Competence Hub: SFTP-Anmeldung erfolgreich, Startverzeichnis fehlt

## Nachricht

Hallo Herr Ross,

bei der vorbereitenden, rein lesenden SFTP-Pruefung fuer die Competence-Hub-
Website konnte ich den Zugang bis zur Serverauthentifizierung erfolgreich
testen. Benutzername, Passwort, Host und der gegen die offizielle IONOS-Liste
gepruefte ED25519-Host-Key funktionieren.

Der Server beendet die SFTP-Sitzung jedoch unmittelbar danach. Eine getrennte
Diagnose liefert folgende Ursache:

```text
Could not chdir to home directory
<IONOS-Kontopfad>/htdocs/projektwue: No such file or directory
```

Das Konto ist erwartungsgemaess per `rssh` auf SFTP beschraenkt. Diese
Beschraenkung soll bitte bestehen bleiben; eine allgemeine SSH-Shell wird fuer
die statische Website nicht benoetigt.

Koennten Sie bitte pruefen und korrigieren:

1. Existiert das dem SFTP-Konto zugewiesene Startverzeichnis mit dem Ziel
   `/htdocs/projektwue`? Den vollstaendigen Kontopfad liefere ich bei Bedarf
   ueber den bestehenden internen Kanal.
2. Falls der Pfad veraltet oder falsch ist: Bitte das Konto dem tatsaechlichen
   Website-Document-Root zuordnen, statt die SFTP-Beschraenkung aufzuheben.
3. Bitte den exakten Document Root bestaetigen, auf den
   `competencehub.donner-partner.de` und
   `competence-hub.donner-partner.de` zeigen.
4. Das vorhandene Konto benoetigt dort spaeter Lese- und Schreibrechte fuer
   den kontrollierten statischen Website-Release. Ein Upload erfolgt erst nach
   separater Produktionsfreigabe und vorheriger Webspace-Sicherung.

Bitte keine Zugangsdaten per E-Mail senden. Eine kurze Bestaetigung des
korrigierten Startverzeichnisses und der beiden Domain-Zuordnungen reicht fuer
den erneuten Nur-Lese-Test.

Vielen Dank und viele Gruesse

Manuel Roedel
