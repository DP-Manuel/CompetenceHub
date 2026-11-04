# Lokaler Schluesselblock

**Spaetere Entscheidung04.11:** Der August-Passphraseweg wird nicht fortgesetzt.
Der [kontrollierte Rebase](controlled-backup-key-rebase-2026-11-04.md) ersetzt
diesen aktuellen Bedienpfad; keine erneute VERIFY/GPG-Abfrage. Manuel allein
verantwortet technische Keys/Backups, nicht Janay. Vorige Diagnose/Tests unten
bleiben datierte Evidenz, keine aktuelle Aufforderung zur alten Wiederaufnahme.

Stand:04.11.2026. Aktueller Auftrag: vorhandene Schluessel pruefen und genau die
bestehende verschluesselte Kopie auf den bereits entsperrten Stick uebernehmen,
erst nach expliziter lokaler Bestaetigung. Keine echte Ausfuehrung durch diese
Codevorbereitung. Kein PostgreSQL-Backup, Restore, Admin, Coachimport oder Server.

## Ein Einstieg, Ein Ende

Kanonisch: [verify-staging-keys.ps1](../../apps/webapp/scripts/verify-staging-keys.ps1).
Der alte [Resume-Pfad](../../apps/webapp/scripts/resume-staging-admin-window.ps1)
ist nur noch ein kompatibler Weiterleiter auf denselben **lokalen** Block; auch
ein alter Aufruf kann nicht mehr automatisch in Backup/Admin weiterlaufen.
Das separate Adminfenster wird hier weder geladen noch aufgerufen.

Ohne `-Execute` nur `STAGING_KEYS=NOT_EXECUTED`, keine Dialoge/Keyzugriffe/Dateien.
Mit Execute: exakter lokal gepruefter Commit und saubere ausfuehrbare Quellpfade,
privater diagnostikfreier Windows-Prozess, vorhandenes geschuetztes Paar,
kein frueherer Admin-Anlageversuch, erlaubter USB-Pfad und Speicherplatz.
Keine Netzwerkabfrage, SSH-/Docker-/DB-/Logininput-Abhaengigkeit. Der Quellstand
wird lokal per Git geprueft; der ausgelieferte Stand wird vor dem Handover gepusht.
Der eine Bedienbefehl im Sessionabschluss nutzt den vollen geprueften Commit und
absoluten Skriptpfad und braucht keinen vorherigen Verzeichniswechsel.

## Bestaetigung

Genau eine Eingabeaufforderung. `VERIFY`, `verify`, Mischschreibung und
versehentliche aeussere Leerzeichen/Tabulatoren sind gleichwertig; Umsetzung:
Trim plus ordinaler Vergleich ohne Gross-/Kleinschreibung. Keine Teilstrings,
keine weiteren Woerter, kein `yes`. Ungueltige Eingaben nennen verstaendlich
VERIFY/verify und warnen, kein Passwort einzugeben; sie werden nicht erneut
ausgegeben oder protokolliert. Leer/Whitespace oder unterbrochener Dialog:
erklaerter Abbruch, keine Schluesselpruefung/Kopie, keine automatische Schleife.
Feste Codes `KEY_CONFIRMATION_INVALID` / `KEY_CONFIRMATION_CANCELLED` und eigene
Phase `confirmation` ersetzen den nichtssagenden frueheren Preflight-STOP.

Der gemeldete fruehere STOP war vor Beginn der eigentlichen Pruefung. Er war
kein BitLocker-, Speicherplatz- oder GPG-Passwortbefund. Kein Entsperrungsbefehl
und kein erneuter Versuch eines Passworts wegen dieser Bestaetigungskorrektur.

## Bestehende Schluessel Und GPG

Reuse der vorhandenen [Resume-/Verifikationsfunktionen](../../deploy/scripts/initialize-staging-operator-config.ps1).
Fehlt der Verifikationsbeleg: `Complete-StagingOperatorConfig`, vorhandenes
DPAPI/GPG-Paar, gleicher geschuetzter lokaler Prozess und gepruefter Corpus.
GPG entschluesselt nur in einen Speicherpuffer; bytegenauer Vergleich mit der
vorhandenen DPAPI-Payload, Struktur-/Versions-/ACL-/Hashpruefung. Kein Klartext-
Export und keine Schluesselwerte in Ausgabe, Argumenten, History oder Reports.
Nur dieser erste notwendige GPG-Aufruf kann einen privaten Pinentry-Dialog
benoetigen. Kein sudo-, DB- oder persoenliches Adminpasswort in diesem Block.

READY-Metadaten werden nur nach Erfolg neu, atomar und ohne Ueberschreiben
veroeffentlicht. Vorhandener Beleg wird nicht ersetzt. Bei Wiederaufnahme werden
der Beleg, beide Dateihashes, ACL, Corpus und DPAPI-Payload erneut geprueft;
gueltiger gebundener GPG-Nachweis unveraenderter Dateien wird wiederverwendet.
Kein unnoetiger erneuter GPG-Dialog. Ein geaenderter/ungueltiger Beleg fuehrt
zu STOP, nicht zu Neuanlage, Rotation, Loeschen oder automatischem Reparieren.
Dieser Nachweis beweist keinen spaeteren Zugriff auf einem anderen Rechner.

Die vorangegangene **echte**, einmalige, nichtinteraktive DPAPI-Zuordnungsprobe
bestand im aktuellen Windows-Kontext; sie gab nur PASS zurueck, keinen Klartext,
startete kein GPG und schrieb nichts. Das ist kein voller GPG-Paarvergleich.
Der echte Paarvergleich/die echte USB-Kopie bleiben bis zur privaten Bedienung
offen; synthetische Tests werden nicht als echter Custody-PASS ausgegeben.

## Aktueller STOP: GPG-Profil Und Passphrase

Spaeter04.11: Manuel meldet unbekannte Passphrase und bricht die echte
GPG-Pruefung ab. Kein erneuter Execute-/Entsperrversuch empfohlen. Die erfolgreiche
DPAPI-Zuordnungsprobe bleibt davon getrennt; READY/USB-Nachweis bleiben offen.

Der lokale Einstieg waehlt explizit
`%LOCALAPPDATA%\CompetenceHub\backup-gnupg`, also unter dem Windows-Benutzerprofil
in `AppData\Local`, nicht `AppData\Roaming`.
Initialize, Complete und die Restorepfade verwenden dieses bestehende GPG-Home
per `--homedir`; der lokale Block setzt weder GNUPGHOME noch einen temporaeren
Keyring und importiert keinen privaten OpenPGP-Schluessel. Das interaktive
Standardprofil `%APPDATA%\gnupg` ist eine andere Ablage. Ein negatives Listing
dort beweist keinen fehlenden Schluessel im expliziten Projektprofil.

Nur Metadaten geprueft: im Projektprofil genau1 Datei unter `private-keys-v1.d`,
4024 Byte; im Standardprofil0 Dateien. Projekt-Keyring-Metadaten stammen vom
25.08.2026. Keine privaten Inhalte, GPG-/Agent-Aufrufe oder Passwortversuche.
Dateiexistenz allein beweist weder den Fingerprint noch Entschluesselbarkeit;
Manuels voriger Dialog nennt den erwarteten Backup-Schluessel. Sein gemeldeter
Gpg4win/../GnuPG-Binarypfad normalisiert auf denselben Pfad wie das Skript.

Die DPAPI-Datei enthaelt versionierte zufaellige **Portal-Anwendungsschluessel**
(TOTP, Outbox, Recovery-HMAC, Rate-Limit und Idempotenz), keinen OpenPGP-Private-Key
und keine GPG-Passphrase. `staging-operator.keys.json.gpg` ist die portable
verschluesselte Kopie dieser Payload, nicht der private OpenPGP-Schluessel.
GPG/Agent verwendet den bereits eingerichteten privaten Schluessel im separaten
Home; der Initializer legt nur Anwendungsschluessel an, keine OpenPGP-Identitaet.

Exakter Dialogpfad jetzt: verify-staging-keys -> Phase key_verification ->
Complete-StagingOperatorConfig -> Import-Clixml/DPAPI-Payloadpruefung ->
Invoke-StagingGpg Mode Decrypt -> `--pinentry-mode ask --decrypt` -> lokaler
Pinentry. Beim urspruenglichen Initialize erfolgte derselbe Dialog nach dem
Verschluesseln beim ersten Vergleich. Der getrennte spaetere Adminlauf und
Restore besitzen eigene Entschluesselungsschritte; sie sind hier nicht aktiv.

Kein funktionaler Pfad-/Resumefehler nachgewiesen; deshalb keine Codeaenderung,
kein Wechsel aufs leere Standardprofil und keine Wiederholung/Neuanlage. Ein
sicherer naechster Block: die am25.08 bestaetigte Passphrase-Hinterlegung mit
Manuel/benannter Recovery-Verantwortlicher Janay klaeren, ohne Werte in Chat
oder Projektdokumente zu uebertragen. Safe ist fuer Stick/BitLocker-Recovery
benannt; der genaue GPG-Passphrase-Ablageort wurde nicht dokumentiert.
Siehe [historische Custody-Evidenz](sb23-wuerzburg-execution.md).
Keine automatische Wiederaufnahme, solange diese Voraussetzung fehlt.

## Verschluesselte Kopie, Nicht Datenbankbackup

Genehmigtes Ziel: `D:\CompetenceHub\staging-operator-key-backups\<sha256>.keys.json.gpg`.
Nur die bestehende `staging-operator.keys.json.gpg`, keine DPAPI-Datei, keine
privaten GPG-Dateien, Recovery-Codes oder Dumps. Reparse-/Pfadkontrolle,
CreateNew statt Ueberschreiben; bereits vorhandene identische Kopie nur pruefen.
Quelle vor/nach Kopie und Ziel an denselben SHA-256 des validierten Belegs binden.
Abweichende oder unvollstaendige vorhandene Dateien bleiben erhalten und stoppen
den Lauf. Auch nach I/O-Fehler kein Loeschen/Blind-Neustart/Neuverschluesseln.

Letzte reine Groessenpruefung: Schluesselkopie1005 Byte; USB frei2012151808 Byte
(etwa1,87GiB), FAT, im Explorer zugaenglich/entsperrt. Das reicht problemlos.
Der Befehl kontrolliert die aktuellen Metadaten erneut, mit1MiB freiem Puffer
fuer Dateisystemverwaltung; er prueft keine Datenbankbackup-Groesse.

PostgreSQL bleibt konsequent separat und ausgeschaltet. Der NTFS-Kandidat C:
hatte zuletzt479511023616 Byte frei (rund447GiB), aber eine aktuelle BitLocker-
Volumenbestaetigung war mit den vorhandenen Rechten nicht moeglich. Daher hier
kein anderes Speichervolumen als freigegeben/verschluesselt ausgeben, keine
Ordner dafuer anlegen und keinen Datenbankdump auf den kleinen FAT-Stick kopieren.
Ein spaeteres DB-Ziel braucht eigene Groessen-/Schutz-/Freigabepruefung und
verschluesselte exakte Kopie/isolierten Restore vor irgendwelchen Adminwrites.

## Tests Und Handover

Implementierung: Commit `32b51ce` (lokaler Einstieg, kompatibler Weiterleiter,
Regressionstests). Dokumentation wird separat versioniert.

[Regression](../../apps/webapp/tests/test_staging_admin_resume_window.py):
Gueltige/ungueltige/abgebrochene Bestaetigung, beide CLI-Einstiege/Exitcodes,
Source-Gate vor privaten Zugriffen, vorhandene/abweichende USB-Kopie, Hashbindung,
unveraenderte Originaldateien und kompletter Ablauf nur in isolierten synthetischen
Pfaden. Echte Windows-DPAPI auf neuem Testmaterial, bewusst **GPG-Testersatz**:
GPG-Abbruch/manuelle Wiederaufnahme, Kopierfehler/READY-Wiederaufnahme, gueltiger
Beleg ohne wiederholten GPG-Aufruf, veraenderter Beleg stoppt. Admin-/Serverpfade
im Test mit harten Fehlersentinels abgesichert; keine echten Keys oder USB-Dateien.

Vollsuite:1333 PASS/30 erwartete Opt-in-Skips. Vorherige fokussierte57 PASS;
zwei CLI-Exitcodefaelle danach zusaetzlich in der gruenen Vollsuite enthalten.
PowerShell-Parser, Python-Kompilierung und pip check PASS; Dokument-/Diffpruefung
PASS (7 Archivdateien,21 Router,233 verlinkte Ziele). Default-CLI tatsaechlich
aus einem anderen Arbeitsverzeichnis ausgefuehrt: NOT_EXECUTED, keine Aktion.
Keine Browser-/PostgreSQL-Wiederholung noetig: keine Aenderung
an Website, API, Schema, Exportadapter oder DB-Verhalten. Vorige native SQL-Probe
bleibt datierte separate Evidenz. JUnit ignoriert: `.tmp/coach4/local-key-block-20261104.xml`.

Erwartete einzige Schlussmeldung nach echter erfolgreicher Bedienung:

```text
STAGING_KEYS=PASS KEY_COPY=PASS SERVER_ACTIONS=NONE REAL_COACH_APPLY=DISABLED
```

Bei STOP nur die bereinigte Meldung weitergeben, keine private Datei/Passphrase/
Schluesselwerte. Der zuvor empfohlene Custody-Klaerungsblock ist durch den oben
verlinkten Rebase ersetzt, nicht durch einen weiteren Aufruf. Historische DoD:
tatsaechlicher Paar-/Belegnachweis und USB-Hash
PASS, Originale erhalten, keine weitere Aktion. Backup/Admin/Import/Migration/
Deployment bleiben getrennt und werden hier nicht automatisch gestartet.
