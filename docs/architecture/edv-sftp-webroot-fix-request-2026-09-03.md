# EDV-Nachfrage: SFTP-Startverzeichnis

Stand: 2026-09-03

Status: Versand durch Manuel ausstehend.

## Betreff

Competence Hub: SFTP-Anmeldung erfolgreich, Startverzeichnis fehlt

## Nachricht

Hallo Herr Roß,

bei der vorbereitenden, rein lesenden SFTP-Prüfung für die Competence-Hub-
Website konnte ich den Zugang bis zur Serverauthentifizierung erfolgreich
testen. Benutzername, Passwort, Host und der gegen die offizielle IONOS-Liste
geprüfte ED25519-Host-Key funktionieren.

Der Server beendet die SFTP-Sitzung jedoch unmittelbar danach. Eine getrennte
Diagnose liefert folgende Ursache:

```text
Could not chdir to home directory
<IONOS-Kontopfad>/htdocs/projektwue: No such file or directory
```

Das Konto ist erwartungsgemäß per `rssh` auf SFTP beschränkt. Diese
Beschränkung soll bitte bestehen bleiben; eine allgemeine SSH-Shell wird für
die statische Website nicht benötigt.

Könnten Sie bitte prüfen und korrigieren:

1. Existiert das dem SFTP-Konto zugewiesene Startverzeichnis mit dem Ziel
   `/htdocs/projektwue`? Den vollständigen Kontopfad liefere ich bei Bedarf
   über den bestehenden internen Kanal.
2. Falls der Pfad veraltet oder falsch ist: Bitte das Konto dem tatsächlichen
   Website-Document-Root zuordnen, statt die SFTP-Beschränkung aufzuheben.
3. Bitte den exakten Document Root bestätigen, auf den
   `competencehub.donner-partner.de` und
   `competence-hub.donner-partner.de` zeigen.
4. Das vorhandene Konto benötigt dort später Lese- und Schreibrechte für
   den kontrollierten statischen Website-Release. Ein Upload erfolgt erst nach
   separater Produktionsfreigabe und vorheriger Webspace-Sicherung.

Die öffentliche Gegenprüfung zeigt bereits:

- beide Subdomains lösen auf dieselbe IONOS-IPv4- und IPv6-Adresse auf;
- das Wildcard-Zertifikat für `*.donner-partner.de` wird ausgeliefert und ist
  für beide Namen gültig;
- HTTP und HTTPS liefern aktuell auf beiden Namen nur die IONOS-Parkingseite
  mit Status `403 Forbidden`;
- weder HTTP auf HTTPS noch die Bindestrich-Variante auf die kanonische Domain
  `competencehub.donner-partner.de` werden derzeit umgeleitet.

Bitte daher auch bestätigen, dass beide Domains wirklich dem korrigierten
Document Root und nicht nur dem allgemeinen IONOS-Parkingziel zugeordnet sind.
Die kanonische Weiterleitung und Website-Header können wir nach der
Nur-Lese-Inventur kontrolliert mit dem statischen Release bereitstellen.

Die in Ihrer vorherigen Nachricht genannte Kontaktadresse ist korrekt:
`competencehub@donner-partner.de`. Fachliche Empfängerin beziehungsweise
Mailbox-Ownerin soll Frau Janay Rappelt sein. Bitte bestätigen Sie Einrichtung
und Zustellweg; ein Passwort wird dafür nicht per E-Mail benötigt.

Bitte keine Zugangsdaten per E-Mail senden. Eine kurze Bestätigung des
korrigierten Startverzeichnisses und der beiden Domain-Zuordnungen reicht für
den erneuten Nur-Lese-Test.

Vielen Dank und viele Grüße

Manuel Rödel
