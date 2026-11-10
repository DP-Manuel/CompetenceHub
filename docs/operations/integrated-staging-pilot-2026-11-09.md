# Integrierter Staging-Pilot: Release und Betriebs-Gate

Stand: 10.11.2026. Quelle vor diesem Batch: d8cd664. **Privater synthetischer
VPS-Pilot installiert und tatsächlich abgenommen**, Operatorquelle52d7ddb und
unverändertes Anwendungspaket0080195755e3. Keine öffentliche/Realnutzer-Freigabe.
IONOS/Pages, Coachimport und R2/GPG bleiben unangetastet.

## Aktuelle Freigabe und tatsächlicher Ausführungsstand

### Echter VPS-Pilot abgenommen am 10.11.2026

**18:23:31 MEZ /17:23:31 UTC: Installation und native Abnahme PASS.**
Der tatsächlich gespeicherte, bereinigte Bericht
`release-artifacts/vps-pilot/e89ce1ef18b14ad38bff9fcbf0199854.json`
wurde unabhängig gelesen und gegen Umfang, Gates und Originalartefakt geprüft.
SHA-256: `2becd577f08e3e13cb8e429ec2f8451f50bdabe479be33e4866950f1fd80b5fa`.
Operatorquelle: `52d7ddba19d300a3e8a14b601cfcdc2d84e3c00b`.
Paket SHA-256 bleibt `f3478fc34de4647fd182a9c7262678b8de2e6b194428ec7dbcc0a116d9c51c41`;
25 gebundene Offline-Abhängigkeiten. Alte STOP-/NOT_RUN-/Next-install-Einträge
weiter unten sind datierte Vorgeschichte, keine erneut offenen Gates.

| Abschluss | Tatsächlich nachgewiesen |
| --- | --- |
| VPS-Deployment | JA, eigene API-/TLS-Proxy-systemd-Dienste aktiv und enabled |
| Geschützter Zugang | `https://localhost:8447/portal/`, öffentliche Ansicht im selben privaten Origin unter `/portal/calendar-public.html` |
| CAL-1 Ende-zu-Ende | PASS: Entwurf, Einreichen, Änderungsanforderung, Revision, Freigabe, öffentliche Projektion, ICS und Anfrageentwurf |
| MFA/RBAC | PASS: vier synthetische Konten, genaue Rollen, Coach-Isolation, CSRF/Origin, Cookies, Logout, Ablauf und Recovery |
| PostgreSQL-Persistenz | PASS: Veröffentlichung und Sitzung nach eigenem API-Neustart erhalten |
| Neustart | PASS, nur eigener API-Dienst; kein PostgreSQL-/fremder Neustart |
| Andere VPS-Dienste | Unverändert aktiv: Chatbot, Nginx, Fail2ban, PostgreSQL; vorherige Listener erhalten |
| Restore/Rollback | Echter09.11-Restore wiederverwendet, frische0006-Baseline vor Eingriff identisch, Runtime verschlüsselt rücklesbar; kein Restore/Rückbau während erfolgreicher Installation |
| Migrationen | Keine, weiterhin0001–0006/27 Tabellen |
| Persönliche Erstzugänge | Keine realen Konten/Einladungen; weiterhin eigener Freigabe- und Betriebsblock |
| Interaktive Führung | Admin-, Coach- und Reviewer-Touren tatsächlich auf dem VPS geprüft; optionale Hilfe, keine automatische Zwangstour |
| Nächster Block | Fachliche Abnahme/Vorführung mit Manuel und Janay in den bestehenden synthetischen Rollenfenstern |

**61 tatsächliche Remoteprüfungen**, Firefox155: Mehrtage/Monatsüberschneidung,
parallele Coaches, Konfliktvermeidung, stale edit in getrennten Sitzungen,
Revision3 mit stabiler ICS-UID, öffentliche Datenschutzgrenze, echte Downloads,
390px, native200%-Tastatur/Fokus und Rücknahme. Kein Screenreader-/Outlook-Desktop-
Produktnachweis behauptet. Keine Buchung, Kundendaten, Mail, Registry-Migration,
COACH-3B REAL APPLY oder Website-Aktion.

Unabhängiger lesender SSH-Nachcheck **18:27 MEZ /17:27 UTC**: beide eigenen Dienste
aktiv/enabled, vier fremde Dienste aktiv. Nur127.0.0.1:8001/8443 zusätzlich;
PostgreSQL5432/Chatbot8000 weiterhin Loopback, öffentliche22/80/443 unverändert.
Frische HTTPS-Readiness über den bestehenden Tunnel mit CA- UND Hostnamenprüfung:
**200**, ausgeliefertes Leaf identisch zum Bericht. TLS-Leaf gültig bis
**24.11.2026,18:20:45 MEZ /17:20:45 UTC**; kein dauerhaftes externes Domain-/TLS-Gate
geschlossen, keine automatische Zertifikatserneuerung versprochen.

Runtime-Ciphertext ausschließlich per Hash nachgeprüft, nicht entschlüsselt:
`a13655ca3fff01cd967b6882d48aa576ed8306369b6c0ca8b7f6283c67392cbb`.
CA SHA `14827c63424b87f7b40aa04019e720872e241e5a8f7a4a5b495cdcb3c89b302d`,
Leaf SHA `aecd310881202f9438b14a9d57d7f3e033bf947416a460fa3263fa44cf71d27a`.
Dateien unter dem bekannten privaten Laufverzeichnis werden nicht versioniert
und bleiben erhalten. Original-Anwendungsschlüssel laut Operator unverändert;
keine neue GPG-/Sicherungsaktion. Der bestätigte Server-Commit und geordnete
Kanalschluss sind beide ACKNOWLEDGED; der Pilot wurde nicht zurückgerollt.

Postflight vor Öffnung der Vorführfenster:4 synthetische Benutzer,4 Angebote,
6 Revisionen,4 Entscheidungen. Diese Testdaten sind **bewusst erhalten**, nicht
Nullrückstand oder echte Coaches. Die drei Rollenfenster und der Kalender wurden
automatisch geöffnet (`interactive_role_windows=OPEN`). Nur diese isolierten
Firefox-Kontexte verwenden, kein Zertifikatswarnungs-Bypass im normalen Browser.
Terminal/Tunnel für die Vorführung offen lassen. Enter schließt lokale Fenster
und Tunnel, nicht die serverseitigen Dienste; danach ist localhost8447 nicht
erreichbar. **Installer nicht zum Wiederverbinden erneut ausführen.**

DoD des jetzt geschlossenen Blocks: tatsächliche Installation,61 native Remote-
Checks, Neustart/Persistenz, geschützter nutzbarer Zugang, gesicherte Runtime und
unveränderte Co-Hosts mit bestätigtem Bericht. Ein nächster Block: vorhandene
Vorführung fachlich abnehmen; Inputs sind Rollenfenster/accepted CAL-Verträge,
Ergebnis ist nachvollziehbares Feedback zu Coach/Prüfer/öffentlichem Anfrageweg,
DoD ist dokumentierte fachliche Abnahme oder konkrete Restbefunde. Keine neuen
Accounts, Migration, Datenimporte, Sicherungsläufe oder Freigaben dabei auslösen.

### VPS-Installation und native Abnahme: ein privater Operatorlauf

**Operator-STOP aus091afdb lokal behoben:** Bericht
`release-artifacts/vps-pilot/6c756c8d8cec413eaf7a5f77fcbc31a7.json` bestätigt
`phase=local_preflight`, `failure_type=KeyError`, Installation/Abnahme NOT_RUN.
Reproduzierbare Ursache: der alte, unverändert akzeptierte Restorebericht enthält
noch kein `baseline_ciphertext_sha256`; der Installer hatte dieses spätere Feld
mit direktem Dictionary-Zugriff vorausgesetzt. Kein Passwortfehler, keine
Serververbindung, Sicherungswiederholung oder verschlüsselte Neuanlage.

Der Installer bindet jetzt beide Ciphertexte an die oben bereits unabhängig
akzeptierten festen Hashes; die Ausnahme gilt nur nach Prüfung des exakten
unveränderten Original-Receipthashes. Vorhandene Receipt-Hashfelder müssen dazu
passen. Fehlende/falsche Pflichtfelder und veränderte Dateien stoppen mit einem
bereinigten Fehlercode vor Entschlüsselung. Originalbericht und beide Ciphertexte
erneut nur per SHA-256 geprüft: unverändert. Alte Laufverzeichnisse bleiben erhalten.
Die lokale Phase unterscheidet nun Restore-, Paket- und Anwendungsschlüsselprüfung.
UTF-8-Decodierung im PowerShell-Kindprozess korrigiert den verstümmelten REPORT-Pfad;
vorherige Konsolencodierung wird auch bei Fehlern wiederhergestellt.
**112 fokussierte Tests PASS**, einschließlich nachgewiesener Altformat-Reproduktion,
13 zusätzlicher Regressionen, Manipulationsabwehr und OEM850/UTF-8-Erfolg/Fehler.
Die bestehende Paket-/61-Browserprüfung bleibt datiert gültig; keine neue
Backendfunktion, Migration, Browser-Neuabnahme oder Installation behauptet.

Owner-Auftrag zur tatsächlichen Installation liegt vor. Kein erneutes
Freigabegespräch und keine weitere Backup-/Restoreausführung nötig. **Noch keine
VPS-Installation ausgeführt:** die gepinnte SSH-Verbindung funktioniert, aber
`sudo -n -- true` verlangt tatsächlich ein Passwort. Dieses wird nicht aus alten
Sitzungen ausgelesen. Letzte lesende Kontrolle **21:39:58 UTC**: vier fremde Dienste
aktiv, PostgreSQL/Chatbot weiter Loopback, 8001/8443 frei, öffentliche Ports unverändert.

Einziger ausführender Einstieg:
[`run-vps-pilot.ps1`](../../deploy/scripts/run-vps-pilot.ps1) mit `-Execute`
und `-ExpectedSourceCommit <vollständiger geprüfter HEAD>`. Ein frisches erhöhtes
PowerShell-7-Fenster, derselbe Windows-Benutzer; Arbeitsverzeichnis beliebig, wenn
der absolute Skriptpfad verwendet wird. Nur bestehendes PostgreSQL-App-Passwort
und einmal VPS-sudo verdeckt eingeben, niemals im Chat oder in Aufzeichnungen.
Keine Zwischenablagenbefehle, zweite Konsole, VERIFY- oder GPG-Abfrage.

Der Lauf installiert und prüft zusammenhängend, statt nach Vorbereitung zu stoppen:

1. Originalen akzeptierten Restorebeleg und beide vorhandenen Ciphertexte prüfen;
   nur die geschützte Baseline im privaten Prozess lesen. Frische native
   DB-Signatur muss vor Installation und unmittelbar vor Testkontenanlage passen.
2. Exaktes Paket `0080195755e3`/SHA `f3478fc34de4647fd182a9c7262678b8de2e6b194428ec7dbcc0a116d9c51c41`
   mit gebundenen Offline-Linux-Wheels installieren. **Keine Migration:** 0001–0006
   genügen. Paket enthält weitere Migrationen, führt sie aber nicht aus.
3. Nur vorhandene, validierte DPAPI-Anwendungsschlüssel verwenden und deren
   Dateihash unverändert nachweisen; keine GPG-Metadatenabhängigkeit, Rotation
   oder Neuanlage. Neue private Runtime-Kopie ausschließlich CurrentUser-DPAPI
   auf erneut qualifiziertem C:, CreateNew/ACL/Hash/Fresh-Process-Rückleseprüfung.
4. Eigene Namespaces `/opt/competence-hub-pilot`, `/etc/competence-hub-pilot`,
   `competence-hub-pilot-api.service` und `competence-hub-pilot-proxy.service`.
   API `127.0.0.1:8001`, separater Nginx-Prozess `127.0.0.1:8443`; kein globaler
   Nginx-Reload, kein fremder Neustart, kein zusätzlicher öffentlicher Port.
5. SSH-Tunnel `127.0.0.1:8447 -> VPS 127.0.0.1:8443`, exakter Origin
   `https://localhost:8447`. Dedizierte kurzlebige TLS-CA nur im Erzeugungsprozess;
   CA-Privatschlüssel nicht gespeichert. Localhost-Leaf 14 Tage, privater Schlüssel
   root0600/systemd-Credential. CA-Vertrauen nur im isolierten Firefox-Profil,
   kein Windows-Truststore-Eingriff und kein Zertifikats-/Hostnamen-Bypass.
6. Vier zufällige synthetische Konten: Admin, Reviewer, zwei getrennte Coaches.
   Keine echten Personen oder Rollen. Native Anmeldung/MFA/Recovery, RBAC,
   Coach-Isolation, CSRF/Origin/Cookies, Revision/Freigabe/Monatsüberschneidung,
   ICS/Anfrageentwurf, Paralleltermine, stale edit, Rücknahme und Sessionablauf.
7. Nur eigenen API-Dienst neu starten; DB-Veröffentlichung und Sitzung müssen
   erhalten bleiben. Fremde Dienste, sämtliche vorherigen Listener, DB-Rechte,
   Eigentümer und Migrationen unverändert; eigene Logs ohne Geheimniswerte.
8. Erst nach bestandener Abnahme eigene Dienste aktivieren. Explizit bestätigtes
   Betriebsende darf keinen angenommenen Pilot zurückrollen. Bei Fehlern vor
   Annahme eigene Dienste unabhängig stoppen und ihren Stillstand prüfen, danach
   ausschließlich eigene synthetische IDs entfernen. Dateien behalten; keine
   improvisierte DB-Restoreaktion, keine Zählerrücksetzung, kein automatischer Retry.

Nach PASS bleibt das Terminal für den Tunnel offen. Separat angemeldete
Coach-/Reviewer-/Admin-Fenster und öffentlicher Kalender werden automatisch
geöffnet, soweit der grafische Browserstart gelingt. Keine Zugangsdaten im Chat;
Logins/MFA/Recovery bleiben verschlüsselt im privaten Operator-Laufverzeichnis.
Erst Enter schließt den lokalen Tunnel und die Vorführfenster; die privaten
VPS-Dienste bleiben installiert. Bei STOP nur bereinigte Status-/REPORT-Ausgabe
melden, nicht blind erneut starten oder vorhandene Dateien löschen.

#### Tatsächliche lokale Prüfung dieses Betriebshelfers

**1.580 Tests PASS, 30 erwartete externe Skips; 60 fokussierte Betriebs-/Transporttests
PASS.** Aktuelle Ubuntu-Probe: **61 native Prüfungen PASS**, Firefox155, tatsächliches
Paket, PostgreSQL0006, eigener TLS-Proxy, 390px, native Firefox-Vollzoom200% und
Tastatur/Fokus. Zertifikat und Hostname geprüft; unbekannte CA und falscher Host
werden abgewiesen. Vollständiger Workflow inklusive Änderungsanforderung,
Revision3/ICS-UID-Stabilität, parallelen Coaches, abgewiesenem stale edit,
eigenem API-Neustart und Recovery-Anmeldung. Alle Tabellenzeilen und Schemahash
nach Cleanup identisch zur lokalen Baseline, Zähler bewusst nicht zurückgedreht;
Container nachweislich entfernt. Restriktive Ausgangs-umask0077 geprüft;
öffentliche Runtime-Dateien bleiben lesbar, private Konfiguration bleibt geschützt.

**Abgrenzung:** systemd-Units wurden mit `systemd-analyze verify` geprüft; im
Wegwerfcontainer ersetzt ein ausdrücklich lokaler Prozess-Shim den fehlenden
systemd-PID1. Echte systemd-/DynamicUser-Ausführung und fremde VPS-Dienste sind
erst im Operatorlauf abnehmbar. Zoom-Navigation wurde per Tastatur geprüft;
keine Behauptung eines bestandenen automatisierten Maus-Koordinatentests im
Firefox-Zoomprofil. Bildschirmleser/Outlook-Desktop wurden nicht vorgetäuscht.
390px-Restbefund: lange Kalenderüberschrift bricht unschön am letzten Buchstaben
um; keine Funktionsblockade, das gebundene Anwendungspaket bleibt unverändert.

Private lokale Evidenz: `.tmp/ch-pilot-proof-accca8cbc1324e73b9e20b709451cd74/`.
`result.json` SHA `891eb52aaf1708eb6cf8dc56a865a2d8d964aa051360c652279bd997000c8daf`;
`mobile390.png` SHA `5416fe1ad7367b88f9808c8f4bc0aa8f172f9725c1ef9da5d649b0edb07b54a4`;
`native200.png` SHA `840d1653604f1b8e8adde3750290f04149b0223758af73246ec1c47591a304ec`.
Screenshots visuell geprüft; keine dieser Dateien wird versioniert.

| Geforderter Abschluss | Tatsächlicher Status vor Operatorlauf |
| --- | --- |
| VPS-Deployment | NEIN, sudo-Interaktion ausstehend |
| Geschützter Zugang | Vorbereitet: HTTPS localhost8447 über gepinntes SSH, noch nicht aktiv |
| CAL-1 Ende-zu-Ende | Lokal PASS; VPS NOT_RUN |
| MFA/RBAC | Lokal PASS; VPS NOT_RUN |
| PostgreSQL-Persistenz | Lokal PASS; VPS NOT_RUN |
| Backend-Neustart | Lokal PASS; VPS NOT_RUN |
| Andere VPS-Dienste | Lesend unverändert/gesund21:39 UTC |
| Restore/Rollback | Echter bestehender Restore PASS, wiederverwendet; eigener Rückbau lokal geprüft |
| Ausgeführte VPS-Migrationen | Keine |
| Persönliche Erstzugänge | Nicht aktiviert; separate Identitäts-/Recovery-/Betriebsfreigaben bleiben nötig |
| Interaktive Benutzerführung | Admin/Coach/Reviewer-Touren lokal tatsächlich geprüft; VPS NOT_RUN |
| Ein nächster Block | Den einen freigegebenen Installations-/Abnahmelauf im privaten Terminal ausführen |

DoD des nächsten Blocks: tatsächlicher VPS-Beleg `VPS_PILOT=PASS CAL1=PASS
MFA_RBAC=PASS PERSISTENCE=PASS RESTART=PASS FOREIGN_SERVICES=PASS`, geprüfter
REPORT und nutzbare geschützte Vorführung. Kein persönlicher Coach-Pilot,
COACH-3B REAL APPLY, Website-Deployment oder öffentlicher Zugang impliziert.

### Echter Sicherungs- und Restorenachweis akzeptiert

**09.11., 20:48:37 UTC: echter VPS-Sicherungs-/Restoreblock PASS.** Manuels
Schlussmeldung wurde nicht allein als Beweis verwendet. Der tatsächlich erstellte
bereinigte Bericht `release-artifacts/protected-staging-backup/6db91e37eaac4cc8a87c430d1ca7a462.json`
wurde vollständig geprüft, SHA-256:
`ffb7a809b25e3e4b72d8961e874d9d6de3fb5bff8d51e39c108cbecb35093710`.
Gebundener Operator-Quellstand: `eee2523a0c2ad521fc0825b244448fd4cbc8cc3f`.

Die vorhandenen Dateien unter dem freigegebenen externen Laufverzeichnis
`%LOCALAPPDATA%\CompetenceHub\pilot-snapshots\6db91e37eaac4cc8a87c430d1ca7a462`
wurden anschließend ausschließlich per ACL/Metadaten/SHA-256 nachgeprüft, nicht
entschlüsselt oder ersetzt. Verzeichnis und Dateien: korrekter Operatorbesitz,
vorgesehene Operator-/SYSTEM-Rechte. Tatsächliche Bindungen:

| Artefakt | Bytes | SHA-256 |
| --- | ---: | --- |
| Native Quellarchive im geschützten Prozess | 110885 | `f2210c314f3bf977700b030e679527823bfe4f9a6b398d8df669c1e37be67024` |
| `database.dump.dpapi` | 111110 | `21a6c7f82b466beb5599bba534ee6669af55fcdc88693cc9ac431c6debf5a66e` |
| `baseline.json.dpapi` | 9158 | `8a37b094d1f7d8692680cd055878f648fca46ae6d9228a2e848cd9db57e18bb4` |

Der echte Bericht bestätigt Fresh-Process-Recovery, Manipulationsabwehr und
Wiederherstellung genau dieser zurückgelesenen Kopie in einer eigenen gesperrten
VPS-Probe-DB. Alle 27 Tabellen/Zeilenhashes, Schema/Rechte, Formate und Zähler
identisch; App/Migrator ohne CONNECT, Quelle unverändert, Probe nachweislich
entfernt, PostgreSQL-Daten-/WAL-Kapazität geprüft und Postflight PASS. Migrationen
bleiben 0001–0006. Keine realen Konten, Anwendungsschlüsselzugriffe oder Installation.
Zusätzlicher lesender SSH-Postflight **20:52:49 UTC**: vier bestehende Dienste
aktiv, PG/Chatbot Loopback, 8001 weiter frei, keine neuen externen Ports.

**Dieses konkrete temporäre Sicherungs-/Restore-Gate ist geschlossen.** Keine
Wiederholung der Sicherung und kein neuer GPG-/Passwortprozess für diese Abnahme.
Die Einschränkungen bleiben: CurrentUser-DPAPI an Rechner/Benutzer gebunden,
Restore im selben Cluster, keine unabhängige Dauer-/Maschinenverlustsicherung,
globale Rollenpasswörter nicht exportiert. Reale Benutzer weiterhin nicht freigegeben.
Die folgenden vorherigen `NOT_RUN`-/fehlender-Beweis-Angaben sind historisch.

Kleiner lokaler Operatorfix: `exit (Funktion)` hatte native Python-stdout-Zeilen
einschließlich REPORT-Pfad eingesammelt, während Write-Host-Schlussmeldung sichtbar
blieb. Mit synthetischem Kindprozess reproduziert und durch explizites Out-Host
bei erhaltener Exitcode-Prüfung behoben. Künftiges Wrapper-PASS prüft zusätzlich
den tatsächlichen JSON-Beleg gegen Lauf-ID, Commit, beide Datei-Hashes, Restore-
und Cleanup-Flags. Neue Belege enthalten Lauf-ID und Baseline-Ciphertexthash;
der obige alte Originalbeleg bleibt unverändert und wurde separat geprüft.
224 fokussierte Tests PASS, darunter 11 neue Ausgabe-/Exitcode-/Receipt-Fälle.
Kein neuer echter Backup-/Restorelauf durch diese Korrektur.

**Ein nächster Block:** eigene private VPS-Pilotinstallation mit dem unveränderten
gebundenen Paket 0080195755e3, vorhandenen Anwendungsschlüsseln und verifiziertem
SSH-/HTTPS-Origin. Inputs sind dieser akzeptierte Rückfallstand, Paket/Hashes und
geschützter Operatorzugriff für Runtime-Konfiguration. Ergebnis/DoD: eigener
Loopback-Dienst, tatsächlich geprüfte TLS-/Cookie-/MFA-/RBAC-/CAL-1-Kette,
Restart/Persistenz und unveränderte fremde Dienste; vorher kein Remote-UI-PASS
behaupten. Kein neues Owner-Freigabegate, keine realen Konten oder Websiteänderung.

### Tatsächlicher Preflight bestanden, Sicherung und Restore vorbereitet

**20:13 UTC: Operator-Preflight PASS.** Manuels Bericht
`release-artifacts/protected-staging-preflight/20261109T2013097595103Z.json`
wurde gelesen und unabhängig hashgeprüft:
`1a939f60b7a0e9fd91d6a84e70072bfb5f2ca343de1858865903941a97e37124`.
C: FullyEncrypted/On/Unlocked, XtsAes128, 464462270464 Bytes frei. Staging:
PostgreSQL 16.15, 0001–0006, 27 Tabellen, fünf statische Rollen; alle dynamischen
Tabellen leer, keine fremde DB-Session. Eigentümer und minimale App-Rechte korrekt,
PG Loopback, Nginx-Syntax gültig, vier Dienste aktiv. Portal/Unit/Runtime-env fehlen.
Keine Mutationen. Volume-/Inventurgate geschlossen, Ziel-ACL und echter Restore
weiter **unbewiesen**. Ältere fehlende Preflight-Belege unten sind historisch.

Einziger nächster Operatorlauf innerhalb der bestehenden Freigabe:
[`run-protected-staging-backup.ps1`](../../deploy/scripts/run-protected-staging-backup.ps1)
mit `-Execute -ExpectedSourceCommit <geprüfter Commit>` im bestehenden erhöhten
PowerShell-7-Fenster, gleicher Benutzer. Sicherung und Restore zusammenhängend,
bei Bedarf genau eine verdeckte VPS-sudo-Abfrage. Keine neue Owner-Freigabe,
Zwischenablage, zweite Konsole oder GPG-Abfrage. Frühere Passworteingaben werden
nicht gespeichert oder aus fremden Sitzungen ausgelesen.

Der Lauf prüft Quelle, Volume und aktuelle DB erneut. Nur neue private Dateien
unter `%LOCALAPPDATA%\CompetenceHub\pilot-snapshots\<eindeutige Lauf-ID>`, bestehende
Benutzer-/SYSTEM-ACL-Primitiven, kein Überschreiben. Ein Root-Prozess im Speicher
über gepinntes SSH erledigt die aktuelle Inventur und den gesamten Datenbankblock.
Read-only-Transaktion mit exportiertem MVCC-Snapshot bindet Zeilen-/Schemahashes
und `pg_dump -Fc --snapshot` an denselben Stand. Unbekannte Zustände oder mehr als
die geprüfte 64-MiB-Grenze stoppen, kein unsicherer Fallback.

Dump nur im RAM, vor Dateischreibung Windows-CurrentUser-DPAPI; auch Baseline
verschlüsselt. CreateNew, exklusive Besitzer-/ACL-Prüfung, SHA-256 nach erneutem
Lesen, Entschlüsselung genau dieser Kopie in frischem Prozess, Manipulationstest.
Erst danach neue zufällig benannte Probe-DB im selben VPS-Cluster, zunächst ohne
Verbindungen, danach PUBLIC/App/Migrator-CONNECT verweigert, Besitzer postgres.
Native Restore ohne `--create`/`--clean`/globalen Rollen-Replay. Vergleich aller
27 Tabellen/Zeilenhashes, Schema/Rechte, Funktionen/Trigger, Format und
Identitätszähler; freie PG-Daten-/WAL-Kapazität vor der Probe prüfen, Quelle
unverändert, nur eigene Probe entfernen und Löschung
prüfen. Probe-DB-Rechte sind absichtlich enger; bestehende globale Rollen und
Passwörter bleiben erhalten. Keine Migration, Konten- oder Dienständerung.

Vorhandene Anwendungsschlüssel werden nicht geöffnet. Die Abwesenheit einer
eigenen Unit/Runtime-Konfiguration und ursprüngliche DB-Eigenschaften werden
festgehalten, nicht als portable Schlüssel-/Konfigurationssicherung ausgegeben.
Bereinigter Betriebsbericht: `release-artifacts/protected-staging-backup/`.
Bei Fehlern Dateien erhalten; nur konkrete eigene Probe-ID für Aufklärung,
kein breites Cleanup. Bestehende Jobs, Backups, Schlüssel und Websites unverändert.

**Begrenzung:** temporärer rechner-/benutzergebundener Rückfallstand für die
Erstinstallation, keine unabhängige Dauersicherung und kein Maschinen-/Cluster-
Recoverybeweis. Original-DB nie ersetzen. Pilot bleibt bis zur Prüfung des echten
Sicherungs-/Restoreberichts uninstalliert; reale Konten weiterhin gesperrt.

Lokaler Ende-zu-Ende-Beleg: echtes isoliertes PG 16/0006, echte Windows-DPAPI-,
Datei-, ACL- und Fresh-Process-Kette sowie Restore PASS. Alle 27 Tabellen samt
Rechten/Format/Zählern gleich, Quelle unverändert, Probe/Container/Testdateien
entfernt. Systemd dabei simuliert, **kein** neuer VPS-Betriebsbeleg. Gesamtlauf
1545 PASS/30 erwartete externe Skips; abschließend 213 fokussierte PASS,
einschließlich 26 neuer Prüfungen und Git-Ausschluss von `.dpapi`-Dateien. Bericht
`release-artifacts/protected-backup-restore-local/889832df7dbc449f989888bfbfd71c11.json`,
SHA-256 `38977689877026d6b1c254ea1ff7d2abb0aa58b2009a95f83f04a60b569bc544`.

### Vorangegangene Freigabe und Vorbereitung

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
