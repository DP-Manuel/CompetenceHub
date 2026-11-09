# Integrierter Staging-Pilot: Release und Betriebs-Gate

Stand: 09.11.2026. Quelle vor diesem Batch: d8cd664. Aktueller Kandidat wird im
abschließenden Release-Nachweis gebunden. **Nicht auf dem VPS installiert.**
Der neue Auftrag erlaubt den bedingten Piloten, ersetzt aber keine fehlenden
Betriebsnachweise. IONOS/Pages, Coachimport und R2/GPG bleiben unangetastet.

## Aktuelle Freigabe und tatsächlicher Ausführungsstand

Manuels anschließender Auftrag **„FREIGABE GESCHÜTZTES STAGING-BETRIEBSFENSTER“**
genehmigt den technischen synthetischen VPS-Piloten bedingt: erst aktuelles
geschütztes Ziel, konsistenter Dump, Integrität und isolierte Wiederherstellung;
danach erforderliche geprüfte Migrationen/eigene Installation und Remote-Abnahme.
Keine erneute Grundsatzfreigabe nötig. Reale Konten, Coachimport, öffentliche
Freischaltung, IONOS und GPG bleiben ausgeschlossen. Fehlende technische
Berechtigung ist nicht mit fehlender Owner-Freigabe zu verwechseln.

Lesender Preflight am 09.11., **19:59 UTC**: vier bestehende Dienste aktiv;
PG `127.0.0.1:5432`, Chatbot `127.0.0.1:8000`, Port 8001 weiterhin frei.
Portal-Unit `not-found`, `/opt/competence-hub` nicht vorhanden; eigenes
Konfigurationsverzeichnis `0750 root:postgres`. Kein Konfigurationsinhalt gelesen.
Die tatsächliche DB-Inventur benötigt weiterhin `sudo`-Authentisierung.
Lokales C: NTFS/Healthy, 464480960512 Bytes frei; aktuelle Sitzung nicht erhöht,
BitLocker-Statusabfrage verweigert. **Speicherziel und echter DB-Zustand bleiben
unqualifiziert; Sicherung, Restore, Migration und Installation nicht ausgeführt.**

Einziger notwendiger Operator-Einstieg für diese noch fehlende lesende Prüfung:
[`run-protected-staging-preflight.ps1`](../../deploy/scripts/run-protected-staging-preflight.ps1)
mit exaktem geprüftem Commit in **PowerShell 7 als Administrator unter demselben
Windows-Benutzer**. Kein zweites Terminal und kein Zwischenablageablauf nötig.
Prüft Quellstand und C:-Schutz, dann gepinntes SSH und ausschließlich lesende
PostgreSQL-Transaktionen. Nur falls erforderlich einmal verdeckt das VPS-sudo-
Passwort abfragen; kein automatischer Passwortwiederholungsversuch. GPG, USB,
DPAPI-Anwendungsschlüssel und fremde Dateien werden nicht geöffnet oder verändert.

Der Lauf speichert ausschließlich bereinigte Metadaten als neue JSON-Datei unter
`release-artifacts/protected-staging-preflight/`; bestehende Berichte bleiben
erhalten. Die Ergebniszeile nennt ausdrücklich `BACKUP=NOT_RUN RESTORE=NOT_RUN
PILOT=NOT_INSTALLED`. Auch ein `PREFLIGHT=PASS` ist **noch kein** Sicherungs- oder
Installationsnachweis: exklusive Ziel-ACL, Konfigurationsverwahrung und die echte
Restoreprobe müssen anschließend innerhalb der bereits erteilten Freigabe folgen.
Bei STOP nur den betroffenen Betriebsweg anhalten, keine erneute Schlüsselrunde.

Lokale Verifikation des neuen Lesewerkzeugs: 28 neue, insgesamt 187 fokussierte
Regressionstests PASS; Kontext-/Linkprüfung ebenfalls PASS.
Echtes isoliertes PostgreSQL 16 mit Paket-Schema 0001–0008/40 Tabellen und
zusätzlich lokalem 0009-Schema/44 Tabellen geprüft. Ein tatsächlicher DDL-Versuch
innerhalb der Read-only-Transaktion wurde abgewiesen; kein Restobjekt angelegt.
Die unterschiedliche Tabellenzahl ist durch den geprüften Paketumfang erklärt,
kein Anlass, Migration 0009 auf dem VPS auszuführen. systemd-Zustände sind in
diesem Container simuliert, **kein zusätzlicher VPS-Dienstnachweis**. Container
entfernt und Löschung geprüft. Synthetischer Bericht:
`release-artifacts/protected-staging-preflight-local/report.json`, SHA-256
`cd74f31232693a2c74c51ea2b4933f3dccae934650b9398cceb3ce004d1839a6`.
Die folgenden früheren Vorschlagsabschnitte bleiben als Entscheidungsherkunft
erhalten; ihr separates Freigabegate ist durch Manuels neuen Auftrag geschlossen.

## Tatsächliche lesende VPS-Prüfung

09.11., 17:46 UTC: SSH mit vorhandenem Host-Key/Schlüssel erfolgreich.
Chatbot, Nginx, Fail2ban und PostgreSQL aktiv. Chatbot auf127.0.0.1:8000,
PostgreSQL auf127.0.0.1:5432;8001 unbenutzt. Keine Portal-API-Unit installiert.
Bestehende vier Backup-Units/Timer als disabled beobachtet, **nicht verändert**.
sudo verweigert den nichtinteraktiven Schema-Lesezugriff: aktueller DB-Stand
unbewiesen. Historisch0001–0006/27 Tabellen ersetzt keine aktuelle Inventur.
Der dokumentierte Vorschlag competencehub-app.donner-partner.de ist NXDOMAIN;
ein endgültiger Hostname wurde nicht bestätigt. Keine Konfigurations-/Secretdatei
gelesen, kein Paket kopiert, keine DB-/Dienst-/Proxyänderung.
Postflight09.11.,18:14 UTC bestätigt dieselben Dienste und Loopbackbindungen.
Zusätzliche reine Metadaten: `/opt/competence-hub` und sein Release-Link existieren
nicht. `/etc/competence-hub` ist750 root:postgres; auf die erwartete Runtime-
Konfiguration ist nicht einmal stat-Zugriff möglich. Ihr Inhalt wurde nicht
gelesen und ihre Existenz/Verwendbarkeit nicht behauptet.

## Tatsächliche lokale Abnahme

`release-artifacts/integrated-pilot-20261109/report.json`:98 integrierte und46
Kalender-SQL-/Browserprüfungen PASS, zusätzlich3 echte PostgreSQL-API-Tests.
Native Aktivierung/MFA für neue synthetische Reviewer-/Coachkonten, reine Rollen,
idempotente Einladung, verbrauchter Link, stabile UUID, drei vollständige Touren,
Fokus/Escape/Skip/fehlendes Ziel,390px und tatsächlicher200%-Browserzoom geprüft.
Der komplette Veröffentlichungs-/ICS-/Revisions-/Rücknahme-/Restartablauf läuft
in dieser Abnahme gegen die **gebaute** Kalenderseite, nicht nur den Demoshell.
Eigener PostgreSQL16.15-Container und sein Volume entfernt,20 dynamische Bereiche
ohne Rückstand, temporäre Kontexte entfernt. Keine realen Daten oder SMTP-Aktion.
Gesamtsuite1476 PASS/30 erwartete externe Skips; später88 gezielte PASS mit einem
transparenten Portbelegungs-Skip während der eigenen SQL-Fixture. Finale
Paket-/Linuxbelege werden im gebundenen Release-Nachweis ergänzt.
Anschließende fokussierte Endprüfung ohne laufenden Container:89 PASS, kein Skip.

## Implementierter lokaler Kandidat

- Echte rollenbegrenzte SQL-Statusübersicht; Admin-Benutzerliste25/Seite,
  maximal100, stabile UUID, keine Tokens/Passwörter/Auditpayloads.
- Drei rein optionale Einführungen. Keine automatische Wiederholung, keine
  personenbezogene Tour-Persistenz, keine Trackingbibliothek. Jederzeit Hilfe,
  Weiter/Zurück, Überspringen, Schließen und Escape.
- Vorhandener Einladungslifecycle erweitert: genau eine Rolle Intern, Coach
  oder Kalenderprüfung. Coach nur mit expliziter vorhandener UUID. Transaktionale
  Sperre verhindert doppelte Belegung; abweichende bestehende Rollen kollidieren.
- Inaktiv bis zur Einmal-Aktivierung, danach Passwort/MFA/Recovery und native
  Session. Neuer Link widerruft alte offene Links; Idempotenz bindet auch UUID.
- `COMPETENCE_HUB_INVITATION_DELIVERY_ENABLED=false` ist der Runtime-Standard.
  Nur exakt`true` nach separater Zustellfreigabe aktiviert Einladung/Reset;
  Worker/Scheduler werden dadurch **nicht** installiert oder gestartet.
- Paket enthält eigenständige Ansicht `/portal/calendar-public.html` und den
  **gleichen** Monatsrenderer/Controller wie die lokale CAL-0.1-Vorführung.
  Öffentliche native Monats-API, Freigabegrenze, ICS und Anfrageentwurf; keine
  Testzugänge/Demohilfen in dieser Seite. Tatsächlich hinterlegte Profilpfade
  werden validiert, nicht aus Personenbezeichnungen abgeleitet.

## Konten und Zustellgrenzen

Kein reales Konto angelegt/aktiviert, keine Einladung verschickt. Manuel ist
vorgesehener Admin-only; bestätigter Login liegt im bestehenden privaten
Operatorprozess, nicht in diesem öffentlichen Bericht. Das bestehende erste
Admin-CLI setzt das persönliche Passwort interaktiv, nicht per Startpasswort.
Ein tokenbasierter Erst-Admin-Bootstrap ist durch diese Erweiterung **nicht**
neu implementiert; seine genaue Aktivierung muss vor realem Betrieb abgeglichen
werden, nicht durch einen fiktiven Admin ersetzt werden.
Janay ist vorgesehene fachliche Prüferin, keine hart codierte Identität oder
automatische zusätzliche Intern-/Adminrolle. Persönlichen Login, Empfänger und
Zustellweg bestätigen. Für jeden Coach fehlt bis zur eigenen Freigabe die
verbindliche User-/UUID-Zuordnung; fehlende Registry-Zeilen blockieren nur
dieses Konto. COACH-3B REAL APPLY und Migration0007–0009 sind hier nicht enthalten.

## Ein geordnetes Betriebsfenster nach Freigabe der fehlenden Inputs

1. Aktuellen Kandidat/SHA, Staging-Ziel, finalen HTTPS-Origin und entweder
   eingeschränkten Nginx-Zugang oder privaten Tunnel verbindlich festlegen.
   Keine IP-/Basic-Auth- oder Zertifikatsausnahme still als öffentliche Lösung.
2. In einem geschützten Operatorfenster sudo authentisieren; aktuelle Schema-
   Versionen, Eigentümer, minimale App-Rechte, Counts, freie Ports, Konfigurations-
   Metadaten und vier Dienstzustände prüfen. Keine Secrets in die Ausgabe.
3. Vor Mutation realer Daten/Konfiguration: aktuell nachweislich geschützter
   Snapshot einschließlich erforderlicher Konfiguration/Anwendungsschlüssel,
   Integrität und erfolgreiche isolierte Restoreprobe. Ein VPS-Dateipfad oder
   0600-Dump allein ist kein Verschlüsselungs-/Recovery-Nachweis. Gleichwertiger
   vorhandener Snapshotweg zulässig, kein R2-Neubau. Fehlt er: nur Mutation stoppen.
4. Prüfsummengebundenes Paket in inaktives eigenes Release-Verzeichnis, eigene
   venv/Identität, bestehende Schlüssel erhalten. Keine Migration für diesen
   Slice erforderlich; vorhandene0001–0006 nicht blind wiederholen.
5. Nur eigenen Dienst auf freiem Loopback-Port starten, Health/Ready prüfen.
   Nginx-Konfiguration nur nach Syntaxcheck und passender Freigabe laden.
   Exakte Origin-/Forwarded-Header-/TLS-/Cookie-/CSRF-Abnahme durchführen.
6. Synthetische Testkonten strikt von realen Erstzugängen trennen. Vollständigen
   Workflow, Restart, Rechte, Aktivierungsablauf, Ablauf/Einmaligkeit, Audit und
   öffentliche Datenminimierung remote prüfen. Exakte synthetische UUIDs bereinigen;
   bei realen Daten **kein** globaler Zero-/DELETE-Runner.
7. Erst nach Empfangs-/Kanal-/Empfängerfreigabe benannte inaktive Erstzugänge
   vorbereiten. SMTP/Worker gesondert freigeben; keine Linkausgabe als Ersatz.
8. Postflight: vier fremde Dienste unverändert aktiv, PG/App loopback, eigene
   Gesundheitsüberwachung/Fehlerweg, Recovery-/Rollbacknachweis und Release-Record.

## Rückkehr und STOP

Erstinstallation hat keinen früheren produktiven Portalstand. Rollback bedeutet
eigene API deaktivieren und nur zuvor gesicherte eigene Unit/vhost/Release-Link-
Änderungen zurücknehmen; Nginx vor jedem erlaubten Reload prüfen. Fremde Dienste
niemals neu starten. Kein automatisches Down-Migrate oder DB-Restore; Datenreparatur
braucht eine eigene Entscheidung wegen zwischenzeitlicher Schreibvorgänge.
Bestehende Schlüssel und Backups nie löschen. Stoppen bei Hashabweichung,
fehlender aktueller Restorefähigkeit, unbekannter Schema-/Datenlage, falschem
Origin/TLS, fremder Portbelegung, Berechtigungsleck oder Dienstverschlechterung.

## Eine konsolidierte MANUEL ACTION REQUIRED-Entscheidung

Manuel hat am 09.11 geantwortet: keine bestätigte externe Domain/TLS-Konfiguration,
kein aktueller realer Backup-/Restorenachweis und kein verfügbares Netzlaufwerk.
GPG-/USB-Neuanlage bleibt pausiert. Private SSH-Zwischenlösung lokal prüfen,
unabhängige Tests abschließen und **einen** Vorschlag vorlegen. Keine realen
Migrationen oder Benutzeraktivierungen. Die frühere Rückfrage ist beantwortet;
nicht erneut nach denselben noch nicht vorhandenen Inputs fragen.

## Ein Vorschlag: begrenzter privater technischer Pilot

Ein einziges **gesondert freizugebendes** Betriebsfenster, in dieser Reihenfolge:

1. Einmal erhöht unter demselben Windows-Benutzer BitLocker-Schutz, Zielidentität,
   Kapazität und exklusive ACLs prüfen. Vorgeschlagen, **nicht angelegt oder
   freigegeben**: `%LOCALAPPDATA%\CompetenceHub\pilot-snapshots`. Kein USB-/SMB-
   Fallback. Im selben privaten Ablauf per sudo aktuelle VPS-Schema-/Daten-/
   Konfigurationsmetadaten prüfen; vorhandene Anwendungsschlüssel erhalten.
2. PostgreSQL-Custom-Dump über SSH im Prozessspeicher übernehmen, vor jeder
   Dateischreibung mit Windows-CurrentUser-DPAPI schützen. SHA-256 nach Schließen
   und erneutem Einlesen vergleichen. Keine Klartextdumpdatei, PowerShell-
   Textpipeline, Credential-Argumente, GPG-Abfrage oder neues Passwort. Die lokale
   Probe ist auf 64 MiB begrenzt; größere reale Daten brauchen einen separat
   geprüften Streamingweg, keinen unverschlüsselten Fallback.
3. Genau die wieder eingelesene Kopie in frischem Prozess entschlüsseln und in
   eine neue, nur für den Operator zugängliche Probe-DB restaurieren. Alle
   Tabellen-/Datenhashes, Schema, Besitzer und effektiven Rechte vergleichen.
   Quelle unverändert lassen und nur die eigene Probe-DB entfernen.
4. **Erst nach akzeptierter echter Sicherung/Restoreprobe** den eigenen API-Dienst
   auf erneut geprüftem 127.0.0.1:8001 und einen eigenen loopbackgebundenen TLS-
   Proxy aktivieren. Fremde Nginx-Hosts nicht ändern; Syntaxcheck und gesondert
   erlaubter Reload statt Dienstneustarts. Ausschließlich SSH-LocalForward zum
   TLS-Endpunkt, exakter Origin einschließlich Clientport. Passendes Zertifikat
   über den bestehenden host-key-geprüften SSH-Kanal binden; der technische
   Client validiert Zertifikat **und** Hostname. Kein öffentliches HTTP,
   `-k`/`verify=False` oder pauschaler Browser-Zertifikatsbypass.
5. Nur synthetische Konten/Termine technisch auf dem Server abnehmen. Reale
   Benutzer, Admin-Bootstrap, Coachzuordnungen und Versand bleiben gesperrt.
   Der normale Browserzugang für echte Nutzer wartet weiterhin auf bestätigte
   Domain/TLS und die langfristigen Recovery-/Betriebsgates. Janays bereits
   vorführbare lokale Browserdemo ist davon unabhängig.

**Begrenzung:** CurrentUser-DPAPI ist üblicherweise an Benutzer und Rechner
gebunden. Diese Zwischenkopie wäre nur ein kurzfristiger Rückweg bei einem
Deploymentfehler, kein alleiniger Geräteverlust-/Katastrophenschutz und keine
portable Schlüsselsicherung. Rechnerverlust/Neuinstallation oder administrative
Passwortrücksetzung können die Nutzbarkeit gefährden. Vor realen Konten ist ein
unabhängig wiederherstellbarer, genehmigter und tatsächlich geprüfter Sicherungsweg
erforderlich. Bestehende automatische Jobs, Schlüssel und Backups bleiben erhalten.

## Lokaler Nachweis der Folgeentscheidung

Bericht `release-artifacts/private-pilot-local-20261109/report.json`:
**14 Sicherungs-/Restoreprüfungen + 5 SSH-/TLS-Prüfungen + 37 native Proxy-/MFA-
Prüfungen PASS**. Echte OpenSSH-Verbindung innerhalb eines isolierten lokalen
Containers, strikte Host-Key-Prüfung, falscher Host-Key abgewiesen. Native MFA,
Cookie-/CSRF-/Session-/Logoutprüfung durch diesen Tunnel mit verifiziertem TLS.
Unbekanntes Zertifikat und falscher Hostname werden abgewiesen. Dies beweist
keinen ohne zusätzliche Vertrauenskonfiguration nutzbaren öffentlichen Browser-
Zugang. Keine Windows-Vertrauensstelle installiert.

Synthetischer 175418-Byte-Dump, 175638-Byte-DPAPI-Datei: exklusive Benutzer-ACL,
erneutes Lesen, Fresh-Process-Entschlüsselung ohne Dialog, Manipulation abgewiesen;
separate Restore-DB, alle 40 Tabellen/Zeilenhashes/Schema/Rechte geprüft. Gleiche
Triggernamen auf verschiedenen Tabellen werden nach vollständiger Identität,
Definition und Enabled-Status verglichen, nicht nach instabiler Katalogreihenfolge.
ACLs werden strukturiert nach effektiven Grants verglichen. Quelle unverändert;
Probe-DB, synthetische verschlüsselte Arbeitskopie und eigener Container entfernt.
Kein Hostmount, veröffentlichter Port, echter Schlüsselzugriff oder VPS-Write.
11 neue Tests und 159 fokussierte Regressionsprüfungen PASS. Das Anwendungsrelease
0080195 und sein ZIP bleiben unverändert; keine unnötige Neuerstellung.

Bericht-SHA-256:
`b56ceb39d4ef5071b9b4c321775179f9e32708fe361cc3738f0eb0d0552dde6a`.
Die neuen Skripte sind **synthetische Testwerkzeuge**, keine freigegebenen
Operator-Werkzeuge für echte Backups oder Deployments.

Speichermetadaten 09.11: C: NTFS/fest/Healthy, 467163213824 Bytes frei;
BitLocker-Abfrage nicht erhöht verweigert, **kein qualifiziertes reales Ziel**.
D: Removable/FAT32/Warning beobachtet, nicht als früherer Stick identifiziert,
nicht verwendet; kein Entsperr-/Reparaturversuch. VPS-Postflight 18:49 UTC:
vier Dienste weiter aktiv, PG 5432/Chatbot 8000 loopback, 8001 frei, kein Portal.

Grundlagen: [Microsoft DPAPI](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata),
[pg_dump](https://www.postgresql.org/docs/16/app-pgdump.html),
[pg_restore](https://www.postgresql.org/docs/16/app-pgrestore.html),
[OpenSSH](https://man.openbsd.org/ssh.1),
[verifizierender TLS-Kontext](https://docs.python.org/3/library/ssl.html#ssl.create_default_context).

## Kurzanleitungen

[Manuel](pilot-admin-guide.md) · [Janay](pilot-janay-guide.md) ·
[Coaches](pilot-coach-guide.md) · [Erstaktivierung/Support](pilot-first-activation.md).
Die Janay-Anleitung ist bewusst kurz (sechs Schritte, keine technischen
Betriebsanweisungen). Echte Screenreader-Produktabnahme und Outlook-Desktop-
Import/Reimport bleiben separat offen; Semantik/Keyboard/Datei sind lokale Tests.

## Genau nächster Block

**Geschütztes Staging-Betriebsfenster**: Eingaben sind bestätigter Zugangsweg,
Snapshot-/Restoreverfahren, sichere Konfiguration und gebundener Kandidat.
Ergebnis: nachgewiesener Preflight/Recovery, eigene Installation und synthetische
remote End-to-End-Abnahme. DoD: tatsächliche Serverbelege, keine fremden Änderungen,
benannte offene Konten-/Mailgates; kein Coachimport und kein Website-Deployment.
