# Integrierter Staging-Pilot: Release und Betriebs-Gate

Stand: 09.11.2026. Quelle vor diesem Batch: d8cd664. Aktueller Kandidat wird im
abschließenden Release-Nachweis gebunden. **Nicht auf dem VPS installiert.**
Der neue Auftrag erlaubt den bedingten Piloten, ersetzt aber keine fehlenden
Betriebsnachweise. IONOS/Pages, Coachimport und R2/GPG bleiben unangetastet.

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

Noch keine Passworteingabe: zuerst endgültigen Staging-Zugangsweg inklusive
TLS/Zugriffsschutz und den bereits nutzbaren geschützten Snapshot-/Restoreweg
bestätigen. Danach **ein** abgestimmtes sudo-/Konfigurations-/Releasefenster mit
gebundenem Paket. Niemals Passwörter, Tokens, Schlüssel oder Recovery-Codes im
Chat senden. Benannte Einladungen bleiben ohne bestätigten Zustellweg aus.

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
