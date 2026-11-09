# Staging Admin: Sicheres Operatorfenster

**Neueste Steuerung09.11:** R2/GPG bleibt pausiert. Der
[integrierte Staging-Pilot](integrated-staging-pilot-2026-11-09.md) erlaubt einen
gleichwertigen, bereits nutzbaren geschützten Snapshot-/Restoreweg, sofern er
aktuell nachgewiesen ist. Keine stille Wiederaufnahme alter Execute-/Keybefehle.
Der aktuelle Auftrag ist noch keine tatsächlich ausgeführte Admin-/Serveraktion.

**Neueste Steuerung04.11:** [kontrollierter Backup-Key-Rebase](controlled-backup-key-rebase-2026-11-04.md).
Nicht den August-Passphraseweg/alten Execute-Befehl fortsetzen. Neuer separater
GPG-Key, vorhandene DPAPI-Anwendungsschluessel bytegleich, unabhaengige Recovery
und aktueller verschluesselter Exact-Copy-Restore vor Admin. Das vorbereitete
Fenster verlangt jetzt explizite neue Custody/Home/Recipient-/Speicherzielbindung
und BACKUP/RESTORE/ADMIN getrennt; keine automatische Schluesselinitialisierung.
Manuel ist alleiniger technischer Operator; Janay kein Recovery-Key-Verwalter.
Keine echte Schluesselerzeugung, DB-/Adminaktion oder Importfreigabe hieraus.

**Aktueller enger Auftrag04.11:** Zuerst nur
[lokale Schluesselpruefung und verschluesselte Kopie](local-staging-keys-2026-11-04.md),
mit tolerantem VERIFY und ohne automatische Fortsetzung. Das echte Betriebs-
fenster in diesem Runbook bleibt separat; kein alter Execute-Befehl fuer die
Schluesselaufgabe und kein Backup auf ein ungeprueftes Ziel.

30.10.2026. Lokale Vorbereitung; **kein reales Konto und kein aktueller echter
Backup-/Restore-Nachweis aus diesem Bericht**. Der aktuelle Ausfuehrungsstand
steht im [aktiven Batch](../exec-plans/active/backend-sprint-2026-10-30.md).

**Aktueller Stand04.11:** Stick/Passwoerter wieder verfuegbar, Betriebsweg von
Manuel freigegeben. Lokale native Exportprobe bestanden und bereinigt; echte
Keyverifikation/Backup/Restore/Admin noch nicht ausgefuehrt. Neuer einziger
[Resume-Einstieg und Nachweise](staging-resume-2026-11-04.md) ersetzen den alten
Startbefehl: vorhandenes Paar nur verifizieren, dann jeden Betriebsblock im
privaten Terminal einzeln bestaetigen. Der folgende02.11-Aufschub ist Historie,
keine erneute Frage nach Stickverfuegbarkeit. REAL APPLY bleibt gesperrt.
Der [Quellenabgleich](../architecture/elisabeth-source-reconciliation-2026-10-30.md)
und der [Importvertrag](../architecture/coach-import-contract-v0.1.md) bleiben
separate fachliche und technische Grenzen.

## Bedienentscheidung und STOP am 02.11.2026

**Aktuell nicht erneut starten.** Manuel arbeitet nach eigener Angabe an einem
anderen Rechner, hat keinen Zugriff auf den Backup-Stick und verschiebt dieses
Backup-/Operatorfenster ausdruecklich bis zu seinem manuellen Signal. Kein
automatischer neuer Versuch, Backup-Bypass oder vorgezogene reale Admin-Anlage.
Bereits bestehende Backupjobs bleiben unveraendert; nur dieses Fenster wartet.

Zwei lokale, bereinigte Ergebnisbelege zeigen `status=STOP`,
`phase=local_readiness`, `account_creation=NOT_ATTEMPTED` und Remote-/Tunnel-
Bereinigung jeweils `NOT_NEEDED`. Metadatenpruefung: vorhandene lokale DPAPI-
und verschluesselte Keydatei, aber kein abgeschlossener Verifikationsvermerk
und kein Account-Anlageversuchsmarker. Dieser Codepfad liegt vor dem VPS-
Vorherbackup, Tunnel und ersten DB-Schreibzugriff. Kein aktueller DB-Nullstand
wird aus den lokalen Belegen abgeleitet oder neu auf dem Server abgefragt.

Die erste Initialisierung wurde nicht vollstaendig verifiziert; ob Dialogabbruch,
Zeitablauf oder fehlender privater Keyzugriff der urspruengliche Ausloeser war,
ist aus den sicheren Metadaten nicht bestimmbar. Ein weiterer Lauf legt den
vorhandenen Ordner bewusst nicht neu an und erreicht deshalb keinen erneuten
Passwortdialog. Die lokalen Dateien werden weder gelesen, geloescht, ersetzt
noch automatisch importiert. Wiederaufnahme muss spaeter den bestehenden
Zustand pruefen, statt die Schluessel still neu zu erzeugen.

Die lokale Diagnosekorrektur erkennt diesen Teilzustand vor Key-/GPG-/Server-
Aktionen und nennt den festen Code
`CUSTODY_INCOMPLETE_REQUIRES_PRIVATE_RECONCILIATION`. Nach aussen gelangen nur
exakt erlaubte Fehlercodes; unbekannte Fehlertexte bleiben verborgen. Eine
vollstaendig aussehende Dateiliste ist weiterhin kein kryptographisches PASS.

Arbeitsplatzwechsel: DPAPI ist benutzer-/rechnergebunden. Die Existenz eines
GPG-Ordners allein beweist keinen nutzbaren privaten Schluessel. Kein Kopieren
privater Keydateien in Repository/Chat oder blinder Austausch der DPAPI-Ablage.
Manuels bestehende Login-Entscheidung bleibt gueltig und wird nicht erneut
abgefragt. Neue Daten-/Sicherheitsfreigaben sind aus dem Backupaufschub nicht
abzuleiten. Die Diagnosekorrektur bleibt lokal; kein neuer Commit/Push/Deploy.

Im ersten02.11 Diagnoseblock gezielt verifiziert:26 Window-/Custody-Tests PASS,
einschliesslich Teilzustandserkennung ohne Keyinhalt/GPG/Passwortdialog und
zulassungslistenbasierter Fehlerausgabe. Dokumentlinks/Archivintegritaet und
Diffpruefung PASS. Damals kein neuer Vollsuite-, nativer Staging- oder Restorelauf;
der nachfolgende lokale Wiederaufnahmeblock hat eigene Evidenz unten.

## Lokal vorbereitete Wiederaufnahme

Manuel bestaetigt am02.11 ausdruecklich: zunaechst **ohne Stick weiterarbeiten**.
Deshalb wird auch der neue Wiederaufnahmeweg nicht auf echten Dateien ausgefuehrt.
Backup-/Admin-/Importfenster bleiben zurueckgestellt; es gibt keinen Ersatz-
Schluessel, keine neue Schluesselerzeugung und keinen Backup-Bypass.

Der Initializer hat jetzt einen getrennten ausdruecklichen Modus
`-ResumeExisting` / `Complete-StagingOperatorConfig` fuer eine spaetere private
Bedienung. Er verlangt vorhandene geschuetzte DPAPI- und verschluesselte Dateien,
verweigert bestehende Metadaten oder einen vorherigen Account-Anlageversuch und
benutzt dieselbe typ-/versionsstrenge Payloadpruefung wie der normale Loader.
Nur beim spaeteren manuellen Lauf werden die vorhandenen Schluessel im lokalen
Prozess geladen; GPG-Pinentry vergleicht die vorhandene portable Kopie bytegenau
im Speicher. Keine neue Verschluesselung, kein Export, kein Plattformwechsel-
Fallback. Dateihashes/ACLs werden vor und nach der Pruefung kontrolliert.

Erst nach Erfolg wird ausschliesslich ein neuer nicht geheimer Verifikations-
Datensatz atomar und ohne Ueberschreiben veroeffentlicht. Abbruch, falscher
Benutzer/Rechner, unpassende Kopie oder geaenderte Dateien erzeugen kein READY;
die bestehenden beiden Keydateien bleiben erhalten. Das ist nur Key-Custody,
kein DB-Backup, Restore-Nachweis, Admin-Konto oder betriebsbereiter Backenddienst.
Echte Pinentry-/Key-/Stick-Pruefung bleibt ein manuelles offenes Gate. Noch
keinen Ausfuehrungsbefehl fuer diesen Rechner schicken oder automatisch starten.

Fuer die neue Funktion werden ausschliesslich frisch erzeugte synthetische
DPAPI-Dateien mit einem GPG-Testersatz verwendet. Ein unabhaengiger begrenzter
Code-Review findet keine wesentlichen Sicherheits-/Korrektheitsbefunde; er
oeffnet keine privaten Artefakte und ersetzt keine echte GPG-Abnahme. Die
Aenderungen bleiben lokal, ohne neuen Commit/Push oder Deployment.

Tatsaechliche neue Verifikation02.11: **1097 PASS,29 erwartete Opt-in-Skips** in
der vollstaendigen lokalen Suite;14 neue Wiederaufnahme-/Payloadfaelle umfassen
Erfolg, abgebrochenen Dialog, unpassende Kopie, DPAPI-Verweigerung, geaenderte
Dateien, vorherigen Anlageversuch, fehlende Bestaetigung, Metadatenkollision und
ungueltige Schluesselformate/-versionen. Synthetischer Erfolg wird auch vom
vorhandenen Loader akzeptiert; Originaldateihashes bleiben unveraendert.
Keine echte GPG-/Stick-/Staging-Abnahme oder neue Restoreprobe daraus ableiten.
Keine neuen Eingaben fuer Manuel, solange ohne Stick weitergearbeitet wird.

## Freigabe und Grenzen

Manuel ist ausdruecklich als genau ein aktiver Staging-Admin genehmigt. Die
einmal bestaetigte Login-Adresse liegt nur im privaten lokalen Operatorinput
`.tmp/backend-sprint-20261030/operator-login.json`. Keine erfundene Identitaet,
kein zusaetzliches Coach-/Internal-/Reviewer-/Contact-Recht, keine Coach- oder
Calendar-Zuordnung. Gruene lokale Vorbereitung einschliesslich voriger Phase A
darf committet/gepusht werden. Das ist keine Deployment- oder Importfreigabe.

Das Fenster erstellt keine Migration, keinen Coach, kein Thema und keinen
Kunden. Es installiert/aktiviert keinen Backenddienst und veraendert weder
Website noch DNS, TLS-Vertrauen, SSH-Konfiguration, Rollenrechte oder Chatbot.
Der oeffentliche echte Coach-APPLY-Einstieg bleibt hart deaktiviert.

## Ablauf und Schutz

1. Exakter freigegebener Git-Commit muss HEAD und im kanonischen Remote gepusht
   sein; alle Backend-Quell-/Import-/Schema-/Abhaengigkeitspfade muessen sauber
   und verfolgt sein. Nicht aus experimentellem Arbeitsstand starten.
   Beide Einstiege verweigern Debug-/Protokollumgebungen einschliesslich DEBUGP,
   DEBUG_FILE und Playwright-/Node-Treibern vor Eingabe von Secrets.
2. Bestehender lokaler GPG-Keyhome, betriebliche Passwort-Pruefliste, geschuetzte
   Verzeichnisse und gecachtes PostgreSQL16-Image werden zuerst geprueft.
   Neue langlebige Konfiguration wird nur einmal angelegt, niemals ersetzt.
3. Fuenf voneinander getrennte kryptographisch zufaellige256-Bit-Schluessel:
   TOTP, Outbox, Recovery-HMAC, Rate-Limit und Idempotenz. Versionierte
   Windows-DPAPI-Ablage nur fuer Benutzer/SYSTEM, zusaetzlich GPG-verschluesseltes
   portables Schluesselbackup mit lokalem Entschluesselungsvergleich im Speicher.
   Keine Klartextdatei, kein DB-Passwort im Store, keine Schluesselwerte in Git,
   Chat, Prozessargumenten oder Rueckgabewerten. GPG-Pinentry bleibt lokal.
4. VPS nur ueber vorhandenen SSH-Key und striktes known-host-Verfahren. Vier
   Dienste und ausschliesslich PG-Loopback werden geprueft, nicht neu gestartet.
   Einmalige verdeckte sudo-Abfrage fuer einen geprueften, eng begrenzten Batch.
5. Eindeutiges verschluesseltes Vorher-Set unter
   `/var/backups/competence-hub/prechange-admin-<nonce>`, nicht der bestehende
   Tagesjob: keine Kollision, Ueberschreibung, Retention oder Serviceinstallation.
   Datenbankdump und vollstaendige Baseline teilen einen exportierten MVCC-
   Snapshot. Ruhige Datenbank/DDL-/Rollenlage muss vom Operator bestaetigt sein;
   sie wird nicht durch Stoppen fremder Dienste erzwungen.
6. Nur die fuenf definierten Dateien werden nach extern kopiert: zwei
   verschluesselte Payloads, METADATA, SHA256SUMS und COMPLETE. Dateiliste und
   Hashes muessen exakt stimmen; es gibt keinen Klartextexport per SSH/SCP.
7. Isolierte Restoreprobe der exakten Kopie: gecachtes gepinntes Image, kein
   Netzwerk/Port, eigene tmpfs-Datenbank, Original-Owner/ACL beim Restore nicht
   abgeschaltet. Nur bekannte drei DB-Rollen lokal NOLOGIN; Passwort-freie
   Globals werden **nicht** auf den ko-gehosteten Cluster zurueckgespielt.
   Vollstaendige Schema-/Relations-/Eigentuemer-/Migrations-/Zeilenmengengleichheit
   statt bloss positiver Tabellenzahl. Der Nachweis ersetzt keine komplette
   Cluster-Rollen-/Credential-Wiederherstellung und prueft ACLs nicht separat.
8. PASS-Datei erst nach nachgewiesener Entfernung der eigenen Restore-DB,
   ihres Containers und aller eigenen temporaeren Klartextdateien. Originalset
   und geschuetzte verschluesselte Kopie bleiben erhalten. Private Keys bleiben
   immer ausserhalb des VPS. Der Restoreprozess kann keine echte APPLY-Freigabe
   erzeugen oder aktivieren.
9. Erst danach verdeckte App-/Migrator-Passwoerter und neues persoenliches
   Admin-Passwort. Eigener SSH-Tunnel auf55432; ein vorhandener Listener wird
   weder uebernommen noch beendet. Ziel exakt `competence_hub_staging`.
   Baseline/Counts und maximal vier Stunden alte Snapshot-/Restorebindung werden
   nach den Passwortabfragen erneut geprueft. Kontoanlage sperrt den leeren
   User-/Rollen-/Coach-Bestand transaktional und prueft die Frist per DB-Uhr.
10. Geschuetzter, dauerhafter Pending-Beleg **vor** erstem Schreibversuch;
    danach ATTEMPTED_CHECK_REQUIRED bzw. CONFIRMED mit privater UUID. Fehler
    nach moeglichem Commit fuehren nicht zu blindem Wiederholen/Loeschen.
11. Eigener lokaler HTTPS-/Edge-Kontext: Mensch richtet Authenticator ein und
    sichert Recovery-Codes privat. Danach Login, MFA-Challenge, Session-Resume,
    Logout, einmalige Recovery und bewusste Ablehnung desselben Codes nochmals.
    Ein Code wird verbraucht, neun bleiben nutzbar. Echtes MFA-Material wird
    weder aus dem DOM gelesen noch als Screenshot/Trace/Storage-State erfasst.
12. Exakt eine Admin-Rolle, keine Business-/Schema-/Migrationsveraenderung,
    Abschlussgesundheit und eigene Tunnel-/Remote-Temp-Bereinigung. Account,
    Konfiguration, verschluesselte Backups und private Ergebnisbelege bleiben.

Die bisherige Bootstrap-Abfrage `FOR SHARE` auf der fuer die App nur lesbaren
Rollentabelle wurde entfernt; Serialisierung bleibt per Advisory Lock erhalten.
Es werden keine weitergehenden Grants eingefuehrt. Zusaetzliche leere-Ziel- und
Deadline-Pruefungen sind nur fuer diesen bewusst strengen Operatorpfad aktiviert.

Der Registry-Runtime bleibt unkonfiguriert: ohne Session401, als echter Admin
503 `registry_unavailable` nach bestandener Admin-Autorisierung. Das ist eine
bewusst gepruefte Grenze, **keine betriebsbereite Registry-API**. Bestehende
Firmenroute bleibt als native Session-/RBAC-Probe nutzbar. Kein Rollenwechsel
auf Nicht-Admin fuer diese echte Identitaet; negative Rollenproben sind lokal
synthetisch belegt, nicht durch Provisionieren weiterer echter Konten.

## Passwort-Pruefliste

Versionsgebundene oeffentliche SecLists-Negativliste, MIT, Commit
`cb6d7645abf4a2c467bc80f84cf70bda3d60c2d6`:
[Maintainer-Quelle](https://github.com/danielmiessler/SecLists/blob/cb6d7645abf4a2c467bc80f84cf70bda3d60c2d6/Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt).
99839 Eintraege ergeben97746 verschiedene Casefold-/UTF8-/SHA256-Fingerprints.
Nur Fingerprints/Lizenz/Herkunft liegen ausserhalb des Repositorys; keine echten
eingegebenen Passwoerter werden uebertragen. Keine vollstaendige oder laufende
Pruefung aller kompromittierten Passwoerter behaupten.

Datei-SHA256:
`80329796cebfd72be3dd68e8114ed91140f18d0ff60a98fe0123549dfcb8a8da`.
Neue Anlage mittels [oeffentlichem Vorbereitungstool](../../deploy/scripts/prepare-staging-password-corpus.py),
separater [Custody-Initializer](../../deploy/scripts/initialize-staging-operator-config.ps1).
Eine unabhaengige verschluesselte Off-Machine-Kopie des portablen neuen Keybackups
bleibt ein Betriebs-/Recovery-Gate; bloss lokale DPAPI- und GPG-Dateien beweisen
diese Kopie nicht. Sie duerfen insbesondere bei STOP nie neu generiert werden.

## Lokale Evidenz und noch offene echte Gates

| Tatsaechlich geprueft | Ergebnis / Grenze |
| --- | --- |
| Vollstaendige lokale Suite |1080 PASS,29 erwartete Opt-in-Skips;17 davon Staging. Diese Skips sind keine neuen echten Staginglaeufe |
| Benannter Bootstrap, reale lokale PostgreSQL16-Grants, Transaktionen und native Auth |7 PASS; konkurrierende Anlage, nichtleerer Bestand, Frist, Audit-Rollback und MFA/Recovery/Session ohne Zusatzrollen; nur synthetischer eigener Container |
| Zusaetzlicher neuer Operatorlauf mit echtem Edge/JS und lokaler DB |1 PASS, zusammen8 im Harness; menschliche Eingaben ausschliesslich synthetisch simuliert; keine echte MFA-Abnahme |
| Neuer Restore-Supervisor mit tatsaechlichem PostgreSQL16-Restore |1 PASS;9-Migrations-Baseline, Owner und Sentinel-Zeile exakt, DB/Container/Klartext entfernt; GPG bewusst ersetzt, **keine echte Verschluesselungs-/Pinentry-Evidenz** |
| DPAPI/ACL/Environment und negative Restore-/Window-Vertraege | Fokussierte automatisierte Pruefungen; echte Keys/GPG-Homes/DB-Zugaenge werden dabei nicht gelesen |
| Read-only VPS-Gesundheit30.10,15:26 UTC | Vier Dienste active, PG nur Loopback; kein aktueller DB-Baseline- oder Backupnachweis |
| Echter Admin, MFA, Recovery, aktuelles verschluesseltes Set/Restore | NOT EXECUTED; erfordern das private manuelle Fenster |
| Echte Coachmigration/APPLY, Websites, Backendaktivierung | NOT EXECUTED / ausserhalb dieses Fensters |

Zusaetzlich: Offline-VALIDATE des eingefrorenen echten Manifests PASS, DB NOT_READ,
0 Mutationen; Readiness-CLI-Neulauf erzeugt denselben Anhanghash. Compileall,
pip check und Dokument-/Archiv-/Linkpruefung PASS. Der vollstaendige echte
Coach-Import-Orchestrator bleibt nach dem Adminblock ein eigenes Gate, nicht
mit diesem Adminfenster verwechselt. Keine Kundendaten/FIN-Implementierung;
Business-Milestone19.11 und spaeteres separates Manuel-Coach-Onboarding dokumentiert.

Ein durch eine fruehe synthetische Windows-Testumgebung erzeugter Cache unter
`apps/webapp/%SystemDrive%` bleibt lokal, ausserhalb der Quell-Allowlist und des
Commits. Bereinigung wurde vom Ausfuehrungsschutz blockiert, nicht umgangen.
Unbekannte `.vscode`-/Wochenupdate-Dateien bleiben ebenfalls unangetastet.

Die isolierte Windows-Probe hat einen fehlenden LASTEXITCODE-Wert nach nativer
Ausfuehrung aufgedeckt: der Restore-Adapter verwendet jetzt eigene Prozess-
Exitcodes. Auch der temporaere initdb-Server gilt nicht mehr faelschlich als
fertiger PostgreSQL-Container; erst PID1=postgres und pg_isready schliessen das
Readiness-Gate. Browser-DB-Abfragen laufen getrennt vom Sync-Playwright-Loop.
Recovery-Radios werden ausdruecklich als Radios statt mehrdeutiger Labels gesucht.

## Einmalige Bedienung

Die nachfolgende Bedienung ist bis zu Manuels manuellem Wiederaufnahmesignal
zurueckgestellt; zuerst den Teilzustand im vorstehenden Abschnitt klaeren.

Superseded04.11: das Signal liegt vor. Ausschliesslich den neuen
[geschuetzten Resume-Einstieg](staging-resume-2026-11-04.md#ein-privates-terminalfenster)
mit aktuellem geprueftem/publiziertem Commit benutzen, nicht dieses alte
Execute-Schema wiederholen. Backup und Admin benoetigen getrennte Bestaetigungen.

Nur **ein Terminal A**, Repositorywurzel, PowerShell7 ueber `pwsh -NoProfile`.
Das [Fensterskript](../../apps/webapp/scripts/run-staging-admin-window.ps1)
bleibt ohne `-Execute` schreibfrei und startet nichts.
Den vollstaendigen Befehl mit dem tatsaechlich geprueften/gepushten40-stelligen
Commit erst aus dem Abschluss dieser Session verwenden, nicht HEAD raten.
Docker Desktop muss laufen; Authenticator und sichere Recovery-Ablage bereithalten.
Keine Transkripte, Bildschirmaufnahmen oder geteilten Bildschirm verwenden.

Nur lokale verdeckte Passwortabfragen/GPG-Pinentry beantworten. Im eigenen Edge
den Hinweisen im Terminal folgen; das Fenster nicht vor dem Abschluss schliessen.
Keine Passwoerter, Einrichtungsschluessel, Recovery-Codes, Cookies oder private
Ergebnisdateien in den Chat senden. Nur die bereinigte Schlussmeldung melden.
Erwartet: `status=PASS`, `real_coach_apply=DISABLED`, privater Ergebnisordner.
Bei STOP nichts blind wiederholen, keine Konten loeschen, keine Keys ersetzen.

## Einziger Naechster Block

Nach Manuels manuellem Signal geschuetzt wiederaufnehmen. Inputs: geeigneter
Arbeitsplatz/privater Keyzugriff, genehmigter Login, vorhandener unveraenderter
Teilzustand und gepruefter gepushter Quellstand. Deliverable: nachvollziehbar
verifizierte Key-Custody, aktueller echter Backup-/Restorebeleg und genau ein
nutzbarer Staging-Admin. DoD: alle nativen Auth-/Recovery-/RBAC-/Bereinigungs-/
Dienstpruefungen tatsaechlich bestanden, kein Backup-Bypass oder Key-Neuanlegen.
Erst danach reale Importbereitschaft neu bewerten. MATCH_ONLY-Themen bleiben
streng: ein weiterhin leerer Themenkatalog braucht eine eigene Bootstrap-
Entscheidung, nicht erfundene UUIDs oder still erzeugte Themen. Kein echter
Coach-Import in diesem Fenster, kein zehntes Profil und kein Website-Deployment.
