# IONOS-Website-Release17.11

**RELEASE PASS.** Die öffentliche Website entspricht am17.11.2026 exakt dem
freigegebenen Paket. SFTP55/55, öffentliches HTTP54/54 und tatsächliche
Desktop-/Smartphone-Browserwege bestanden. Kein VPS-/Pages-/DB-Eingriff.

## Freigegebener Betriebsblock

Manuel erteilt am17.11 die ausdrückliche Produktionsfreigabe für den unveränderten
[geprüften Websiteumfang](../content/website-release-2026-11-17.md): Quelle
`11cb1ea90fb5d72c38a5c9cd5c661285bcfdfbe5`, ZIP
`competence-hub-website-11cb1ea90fb5-20261117T184034Z.zip`, vollständiger SHA-256
`c3169746eaeaee9e4959cf8b67923d408a845aafce18d69c5659011db6695c05`.

Freigabe umfasst aktuelle Inventur, vollständige geschützte Webrootkopie,
Hash-/Rückfallprüfung, kontrollierten Upload und tatsächliche Produktionsprüfung
in einem zusammenhängenden Betriebsfenster. Keine erneute Owner-Freigabeschleife
für diese Schritte. Bei tatsächlichen Paket-/Sicherheits-/Rechteabweichungen stoppen.
Kein VPS/Pages/DB/Konto/Kalender-/Benutzerverwaltungs-/GPG-/USB-Eingriff.

## Tatsächlicher Zustand

| Gate | Stand |
| --- | --- |
| Paket/Manifest/Commit | PASS: vollständiger Hash exakt, Quelle11cb1ea, dirty=false |
| Entpackte Dateien | PASS:55/55 entsprechen dem gebundenen Releaseinventar; Inventar-SHA ebenfalls exakt |
| SSH-Host-Key | PASS: bestehender Pin entspricht bestätigtem ED25519-Fingerprint; keine Trust-Ausnahme |
| Frische HTTP-Inventur | PASS:51/51 Vorgängerdateien exakt; kanonisches HTTPS200, drei HTTP/Aliasvarianten301 auf kanonisches HTTPS |
| Geschützter Backupordner | PASS: C:, keine geerbten Root-ACLs; Kopien/Archiv/Probe nur aktueller Benutzer, SYSTEM und Administratoren |
| Aktueller BitLockerstatus | PASS: Manuel bestätigt lokale Adminausgabe C: FullyEncrypted/On/Unlocked; keine Entsperrung oder Schlüsselaktion |
| SFTP-Anmeldung/Inventur | PASS: manuelle Diagnoseanmeldung überIPv4; vollständige52-Datei-Kopie exakt zum bestätigten Webroot, keine unbekannten Dateien/Verknüpfungen |
| Vollständige Webrootsicherung | PASS:52 Dateien,11.759.090 Byte, einschließlich .htaccess; alle52 Hashes exakt zum Vorgänger |
| Rückfall-/Hashnachweis | PASS LOKAL: neue Sicherung archiviert, getrennt entpackt und52/52 Hashes erneut exakt; konkrete Rückfallbefehle vorbereitet, kein produktiver Rollback nötig |
| Upload | OPERATOR_COMPLETE:37 neue/geänderte Dateien,18 unveränderte nicht geschrieben; Assets zuerst/index.html zuletzt, kein Normalbetrieb-rm |
| SFTP-Rücklesen | PASS:55/55 einschließlich .htaccess exakt zum genehmigten Paket |
| Öffentliche HTTP-Prüfung | PASS:54/54 öffentlich abrufbare Dateien paketgenau; sechs nicht freigegebene persönliche Profilrouten404; zentrale Rechtsziele200 |
| Browser-Smoke | PASS:1440px/390px, Tastatur, Startnavigation, Finder/Filter, Profile, fünf Formate/Mailto, Kontaktformular ohne Versand, Kalender-Beispielgrenze und Mindforge-P0-Textgeometrie |
| Domains/TLS | PASS: kanonisches HTTPS200; HTTP/Alias301 auf kanonisches HTTPS, neuer Profilpfad bleibt erhalten; keine unsichere TLS-Ausnahme |

Die Passwortabfrage ist eine notwendige lokale Authentifizierung, keine neue
Ownerentscheidung. Keine gespeicherten Zugangsdaten durchsuchen, keine unbekannten
Schlüssel verwenden und keine automatischen Passwortversuche.

Erster manueller Anmeldeversuch endete mit `Connection closed` ohne erkennbare
Phase. Kein falsches Passwort daraus abgeleitet. Zwei passwortlose SSH-Handshakes
bestätigten den gleichen gepinnten Server überIPv4 undIPv6; das erwartete Ende
ohne Authentifizierung ist kein Passwortfehler. Danach ein gezielter manueller
IPv4-Diagnoseaufruf, ohne persönliche Schlüssel/Agent/SSH-Konfiguration und mit
nur einer Passwortabfrage, erfolgreich. Keine IPv6-Ursache oder Serverreparatur
behauptet. Passwort nie vom Agent gelesen; kein automatischer Anmelderetry.

## Bindung und Rückfallnachweis

Die ZIP-Datei selbst wurde nicht öffentlich hochgeladen. Ihre55 Inhalte sind
über den vollständigen Archivhash und das Dateiinventar an Quelle11cb1ea gebunden.
37 neue/geänderte Dateien übertragen,18 unveränderte ausdrücklich nicht angefasst.
Alle55 anschließend per SFTP neu heruntergeladen und bytegenau verglichen;
sämtliche54 HTTP-öffentlichen Dateien stimmen ebenfalls exakt überein.

| Beleg in der privaten lokalen Ablage | SHA-256 / Ergebnis |
| --- | --- |
| `release-receipt.json` | `9c258b6fbcf957db60b5c880b255208419ee27a8724900850597b86eb23ceeea` |
| `webroot-before.zip` | `83afc74324f6215056228922fef194ca8ce4f75a55d200c3f36895e5ef559012` |
| `webroot-files.sha256` | `2bf2abd0a6d09af431942b20cb73443335fc35f6800996de064e433e0fc316d8` |
| `readback-files.sha256` | `5e4904b10482ecebfb7baad8295dd8b7ac85adfc14040e347d9f6f30cb9fae0d` |
| `backup-verification.json` |52/52 aktuelle Vorgängerdateien,11.759.090 Byte, keine Zusatzdatei/Verknüpfung |
| `restore-probe/` | Archiv getrennt lokal entpackt,52/52 Dateihashes exakt; keine produktive Rücksicherung |
| `SFTP-UPLOAD-COMMANDS.txt` |37 verifizierte Pfade, Assets zuerst, letzter put=index.html, keine Löschung |
| `SFTP-ROLLBACK-COMMANDS.txt` |34 Originaldateien aus frischer Kopie zurück, index.html als letzter put; nur drei eigene neue Pfade und ihr neues leeres Profilverzeichnis entfernen |
| `SFTP-READBACK-COMMANDS.txt` | Nur55 verifizierte get-Pfade, keine Remoteänderung |
| `http-postflight.json` |54/54 Paketbytes, sechs zurückgehaltene Personenrouten404, zentrale Impressum-/Datenschutz-Ziele200 |
| `domain-postflight.json` | Strikte TLS-/Redirectprüfung, fünf Fälle einschließlich Erhalt des Profilpfades |
| `browser-postflight.json`, `screenshots/` | Tatsächliche Desktop-/390px-Wege und sichtbare Formate/P0-Abschnitt geprüft |

Der frische komplette Rückfallstand liegt unter
`release-artifacts/website-production/20261117-11cb1ea/`, nur auf dem bestätigten
BitLocker-C: mit restriktiver Benutzer-/SYSTEM-/Administratoren-ACL. Keine GPG-,
USB- oder Passwortarchitektur. Diese Dateien sind vollständig von Git ausgeschlossen.
Vor einem späteren tatsächlichen Rollback Hashes und aktuelle Remoteänderungen
erneut abgleichen. Der vorbereitete Rückfall entfernt nie fremde Pfade; bei einem
teilweise ausgeführten Upload sind bereits fehlende eigene Neudateien kein
Datenverlust und dürfen nicht durch pauschale Löschbefehle ersetzt werden.
Hier war kein Rollback erforderlich oder ausgeführt.

## Öffentlich Geprüfter Umfang

- Startseite mit neun Karten: drei reale Profile und sechs unverändert
  gekennzeichnete fiktive Demos, keine Umdeutung als reale verfügbare Coaches.
- Leistungen/Angebotsfinder: ausschließlich Gülcans drei Familien/fünf Formate;
  Coach-/Zielgruppenfilter, Leerzustand, Reset, Tastatur und Rückweg zum Profil.
- Gülcans Profil samt freigegebenem203×260-Originalporträt; alle fünf benannten
  Formate mit gültigem person-/formatbezogenem E-Mail-Entwurf. Keine Interna/Preise/
  Originalkonzepte oder ungeklärten Angebotsdetails ergänzt.
- Unternehmen → Workshops/Führung → Coach → Anfrage; bestehende Galvano- und
  Rodríguez-Profile, Kontextnavigation und zentrale Kontaktwege.
- Kontakt: öffentlicher Telefon-/Mailto-Weg, Formvalidierung und ausdrücklich
  beschriebener Mailclient-Handoff. Kein Formular versendet, kein SMTP-/Mailbox-
  Zustellnachweis behauptet.
- Kalender bleibt die bereits freigegebene, klar markierte Beispielansicht;
  nur gemeinsame Navigation aus dem genehmigten Paket. Funktionsskript/Daten
  unverändert, keine echte Verfügbarkeit, Buchung oder private Pilot-API eingebunden.
  Coach-Kalender und Benutzerverwaltung auf dem VPS bleiben vollständig unberührt.
- Impressum/Datenschutz verweisen weiterhin auf die erreichbaren zentralen
  D+P-Seiten. Canonical/Robots/Sitemap entsprechen dem geprüften Produktionsbuild.
- Hupp, Schwabauer, Klemm, Celic, Wegner-Ney und Becker nicht über persönliche
  Produktionsrouten veröffentlicht (alle404); Preview mit acht aktiven Profilen
  bleibt genau beim zuvor veröffentlichten Stand, ohne erneuten Pageslauf.
- Mindforge-Hinweis bei1440/390px: tatsächliche Text-Range-Rechtecke innerhalb der
  Spalten, keine Kollision/Abschneidung, erwartetes Stapeln; Screenshots visuell geprüft.

## Abweichungen und Gezielte Qualität

Keine offene kritische Produktionsabweichung. Der erste SFTP-Abbruch ist oben
begrenzt dokumentiert, ohne erfundene Passwort-/IPv6-Ursache. Ein Browserprüfschritt
fragte das Porträt zu früh ab: unabhängiges HTTP/SFTP war bereits paketgenau,
die echte Browseraufnahme zeigte anschließend vollständiges203px-Bild. Nur der
Test wartet jetzt ausdrücklich auf ein vollständig geladenes gültiges Bild,
statt lokales Ladetempo vorauszusetzen. Zwei synthetische lokale Regressionen
(verzögert gültig / defekt) bestanden; defekte Bilder bleiben ein Fehler.
Danach die zwei betroffenen echten Produktionswege erfolgreich ausgeführt;
bereits grüne HTTP-/Dateibelege wiederverwendet. Kein App-/CSS-/Datenwechsel,
kein erneutes Hochladen, keine vollständige Backend-/Kalender-Testwiederholung.

Website-Quelle bleibt11cb1ea, Paket-SHA bleibtc3169746…; ein neuerer Git-Commit
trägt ausschließlich diesen Betriebsrecord, Projektcheckpoint und den robusteren
Browsernachweis. Der Commit/Push führt keinen weiteren Pages-/IONOS-Deploy aus.

## Reihenfolge und Schutz

1. **Terminal A**, Windows PowerShell als Administrator unter demselben Benutzer:
   aktuellen C:-Schutz prüfen; nur FullyEncrypted/ProtectionOn/Unlocked erlaubt.
   Dann vorhandenen gepinnten SFTP-Verbindungshelfer mit lokal bekanntem Benutzer
   starten. Kein Passwort in Chat, History, Skript oder Report.
2. Nach tatsächlichem `sftp>`: `pwd` und `ls -la`; Webroot `/` und unbekannte
   Einträge klassifizieren. Vorher keine Befehlsliste in die Zwischenablage laden.
3. **Terminal B** lädt erst danach die geprüfte Sicherungsdatei mit dem bestehenden
   Copy-Helfer. Datei beginnt mit bewiesenem ASCII-`lcd`, dann `lpwd`, Inventur,
   vollständiges `get -r . webroot` einschließlich versteckter Einträge. Kein
   Remote-Schreibbefehl. Lokale Zielrechte nicht mit `get -p` aufweichen.
4. Vollständigkeit/Dateiliste/Größen, aktuelles SHA-Inventar und alle52 bekannten
   Vorgängerdateien prüfen; Symlinks, ausgelassene Dateien oder Lesefehler sind
   Stopper. Unbekannte Dateien nicht veröffentlichen, löschen oder überschreiben.
   Relevante HTML-/Rechts-/Fehlerseiten und Konfiguration der Sicherung prüfen.
5. Daraus konkreten Wiederherstellungsbefehl und exakte betroffene Dateien ableiten;
   lokale Rückfallkopie nicht überschreiben. Erst dann Upload in derselben Sitzung,
   Assets vor Seiten und index.html zuletzt. Ausschließlich verifizierte55 Dateien.
6. SFTP-Rücklesen der geänderten Dateien und strikte öffentliche HTTP-/Browser-
   Smokes; bei kritischem Fehler den bestätigten Rückfallplan einsetzen. Keine
   Vollspiegelung, keine automatische Entfernung unbekannter Remotedateien.

Lokale private Ablage: `release-artifacts/website-production/20261117-11cb1ea/`.
Sie bleibt von Git ausgeschlossen. Sicherung ist statische Website, keine
Datenbank-/Portal-/Schlüsselsicherung. Remote-Verfügbarkeit und tatsächliche
Wiederherstellbarkeit werden nicht aus einem lokalen Vorbereitungstest abgeleitet.

## Erfüllte Abschlusskriterien

Paketgenaue Produktionsbytes, Gülcan3 Familien/5 Formate, Finder/Filter und
Coach-/Mailto-/Telefonwege, vorhandene freigegebene Inhalte, Smartphone/Tastatur,
zentrale Rechtslinks, Domainredirect, Canonical/Robots/Sitemap und sichtbarer
Mindforge-P0-Abschnitt. Hupp bleibt aus Preview entfernt; fünf andere Profile
werden nicht nach IONOS übernommen. Vorhandene klar markierte Demoansichten bleiben
im bereits genehmigten Umfang, keine echten Termine/privaten Daten ergänzt.
Tatsächliche Ausführung und unabhängige Nachweise sind abgeschlossen: **PASS**.
Manuel kann die lokale SFTP-Sitzung mit `bye` beenden; das beeinflusst die Website nicht.

## Genau Ein Nächster Block

EDV-Abgleich für bestätigte App-Adresse, dauerhaftes HTTPS/Zugriffsschutz und SMTP.
Inputs: die noch ausstehende EDV-Rückmeldung und die bestehenden Aktivierungsgates.
Ergebnis/DoD: bestätigte geheimnisfreie Infrastruktur-/Zustellparameter und ein
konkret freigabefähiger persönlicher Pilotstart; keine Identitäts-/UUID-/Rollen-
annahmen, Kontoaktivierung oder neuer Schlüsselprozess durch diese Websitefreigabe.
