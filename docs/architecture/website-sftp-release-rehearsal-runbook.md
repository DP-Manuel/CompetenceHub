# Website SFTP Release Rehearsal

Stand: 2026-08-21

## Zweck

Dieses Runbook bereitet den spaeteren statischen Website-Release auf den
IONOS-Webspace reproduzierbar und reversibel vor. Es trennt lokale
Artefaktpruefung, Remote-Inventur, Webspace-Sicherung, Upload, Smoke-Test und
Rollback in eigene Gates.

Die lokale Vorbereitung verbindet sich nicht mit IONOS und fuehrt keine
Veroeffentlichung aus. Ein Git-Push ist ebenfalls kein Produktions-Release.

## Sicherheitsmodell

- SFTP-Passwort, Benutzername und sonstige Zugangsdaten bleiben ausserhalb von
  Git, Kommandozeilen, Skripten, Logs und Projektartefakten.
- Das Passwort wird spaeter ausschliesslich interaktiv in einem lokal
  freigegebenen SFTP-Client eingegeben.
- Der Zielvertrag enthaelt keine Zugangsdaten. Er pinnt Host, Port, kanonische
  Domain, den ueber einen zweiten Kanal geprueften Host-Key und den zuvor
  bestaetigten Remote-Webroot.
- Dirty Builds, falsche Domains, falsche Hashes, Platzhalter, unsichere
  Remotepfade, ZIP-Traversal und symbolische Links stoppen die Vorbereitung.
- Unbekannte Remote-Dateien werden nie automatisch geloescht.
- Vor jedem Replace muss eine vollstaendige datierte Webspace-Sicherung samt
  lokaler Hashliste vorhanden und lesbar sein.

## Phase A: Lokales Release-Paket

1. Nach einem freigegebenen Commit die Website mit
   `scripts/build-website-release.ps1` bauen. Ohne `-AllowDirty` arbeiten.
2. Nach Phase B `deploy/website/sftp-target.example.json` ausserhalb von Git
   kopieren und Host, geprueften Host-Key sowie den durch Remote-Inventur
   bestaetigten Webroot eintragen. `remote_web_root_verified` erst dann auf
   `true` setzen. Keine Zugangsdaten ergaenzen.
3. Das lokale Rehearsal-Paket mit
   `deploy/scripts/prepare-competence-hub-website-sftp-rehearsal.ps1` erzeugen.
4. `release-plan.json`, `release-files.sha256` und
   `OPERATOR-CHECKLIST.md` gemeinsam pruefen.

Ein erfolgreiches lokales Paket behaelt absichtlich folgende Werte:

- `remote_inventory_verified: false`
- `remote_backup_verified: false`
- `remote_change_authorized: false`
- `legal_release_gate_closed: false`

Sie duerfen nicht durch das Vorbereitungsskript auf `true` gesetzt werden.

## Phase B: Remote-Inventur

Nur nach einer ausdruecklichen Freigabe fuer die Verbindung:

1. SFTP-Host-Key ueber einen zweiten vertrauenswuerdigen Kanal verifizieren.
2. Interaktiv verbinden und zuerst `pwd` sowie eine vollstaendige Auflistung
   inklusive versteckter Dateien erfassen.
3. Den tatsaechlichen Document Root mit dem Zielvertrag vergleichen.
4. Vorhandene `.htaccess`, Fehlerseiten, Providerdateien und unbekannte Dateien
   klassifizieren. Bei Abweichungen stoppen.

Diese Phase veraendert keine Remote-Datei.

Der ED25519-Host-Key fuer den im privaten Zielvertrag hinterlegten IONOS-
Providerhost wurde am 2026-09-02 ohne Anmeldung beobachtet und gegen die
offizielle IONOS-Fingerprintliste verifiziert. Der bestaetigte Fingerprint lautet
`SHA256:1gx2w8Rtv3wCgi7Jh8myf/KVd72cRQbow03UP8P095Q`. Verbindungsablauf,
Stop-Regeln und noch offene Inventurfelder stehen in
`website-sftp-read-only-inventory-2026-09-02.md`.

## Phase C: Backup vor Replace

Nur nach bestaetigter Inventur und separater Aenderungsfreigabe:

1. Den gesamten bestaetigten Webroot inklusive versteckter Dateien in einen
   neuen datierten lokalen Rollback-Ordner herunterladen.
2. Lokal eine SHA-256-Inventarliste erstellen und Anzahl sowie Groesse mit der
   Remote-Inventur abgleichen.
3. Mindestens `index.html`, Rechtspfade, `.htaccess` und vorhandene Fehlerseiten
   aus der Sicherung oeffnen beziehungsweise pruefen.
4. Rollback-Owner, Ablageort und Wiederherstellungsentscheidung protokollieren.

Fehlt auch nur ein Teil der Sicherung, findet kein Upload statt.

## Phase D: Upload und Aktivierung

Der konkrete Replace-Mechanismus wird erst nach der Remote-Inventur festgelegt.
SFTP allein garantiert weder serverseitige Checksummen noch einen atomaren
Verzeichniswechsel. Deshalb darf vorab kein pauschales Sync- oder
Loeschkommando vorbereitet werden.

Fuer die Freigabe muessen feststehen:

- exakter Webroot und Verhalten des IONOS-Document-Roots;
- Behandlung vorhandener Provider- und Konfigurationsdateien;
- Uploadreihenfolge mit `index.html` zuletzt;
- Liste bewusst entfernter Altdateien;
- unmittelbarer HTTPS-Smoke und verfuegbarer Rollback-Owner.

## Phase E: Smoke und Rollback

Die verbindliche Smoke-Liste liegt im erzeugten `OPERATOR-CHECKLIST.md` und in
`production-release-plan-2026-09-25.md`. Bei falschem Host, TLS-/Redirectfehler,
fehlender Kernroute, falscher Kontaktadresse, Review-Modus, blockierendem
JavaScriptfehler oder fehlendem Rollback-Owner wird gestoppt und die datierte
Vorabkopie wiederhergestellt.

## Freigabegrenzen

Dieses Runbook und das Vorbereitungsskript autorisieren keine Verbindung,
keinen Upload und keinen Rollback. Produktionsfreigabe, rechtliche Freigabe,
Kontaktprozess und konkreter Remote-Change bleiben getrennte Gates.
