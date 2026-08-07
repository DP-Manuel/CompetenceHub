# PostgreSQL 16 Installation Runbook

Stand: 07.08.2026

Status: Staging-Ausführung am Freitag, 07.08.2026 erfolgreich abgeschlossen.
ADR 0002 ist umgesetzt. Das ursprünglich für Samstag geplante Wartungsfenster
wurde in Manuels reservierten Freitag-Arbeitstag vorgezogen.

## Ziel

PostgreSQL 16 als lokale, eigenständige Datenbank für einen späteren
Competence-Hub-FastAPI-Dienst auf dem vorhandenen VPS installieren, ohne den
laufenden Chatbot oder dessen Daten zu verändern.

## Ausführungsergebnis 07.08.2026

- Ubuntu aktualisiert und in Kernel `6.8.0-137-generic` neu gestartet.
- Chatbot, Nginx und Fail2ban vor und nach dem Change aktiv; öffentlicher
  Chatbot-Healthcheck vollständig erfolgreich.
- UFW aktiv mit `deny incoming`; nur 22/80/443 öffentlich freigegeben.
- PostgreSQL 16.14 installiert, aktiviert und ausschließlich an
  `127.0.0.1:5432` gebunden.
- `competence_hub_staging` mit NOLOGIN-Owner, separatem Migrator und
  eingeschränkter App-Rolle angelegt. Passwörter ausschließlich interaktiv in
  `psql` gesetzt.
- Peer-Authentifizierung für lokale Sockets und SCRAM-SHA-256 für Loopback-TCP
  bestätigt.
- DDL-Verbot der App, kontrollierte Owner-Übernahme des Migrators sowie
  automatisch vergebene App-DML-Rechte erfolgreich getestet. Zukünftige
  Funktionen sind standardmäßig nicht für `PUBLIC`, sondern nur für die
  App-Rolle ausführbar.
- Lokaler Custom-Dump mit synthetischer Prüftabelle erstellt und in einer
  separaten Datenbank erfolgreich wiederhergestellt. Eigentümer, Datenzeile und
  App-Rechte stimmten; Testdatenbank und Prüftabelle wurden entfernt.
- Verbleibendes Gate: verschlüsselte Off-Server-Kopie und Restore aus genau
  dieser Kopie vor jeglichen realen Firmen- oder Personendaten.

## Verantwortlichkeiten

- Change-/Serveroperator: Manuel
- Produktionsfreigabe: Thomas Roß, EDV-Leiter
- Datenbank-/Backendprojekt: Competence Hub
- Mailbox: Janay Rappelt
- Rechtlicher Ansprechpartner: Lars Donner

## Harte Grenzen

- Keine echten Kunden-, Firmen- oder Coach-Daten während Installation und
  Stagingprüfung.
- Keine Passwörter in Shell-History, Git, diesem Runbook oder Chat.
- Kein PostgreSQL-Port im öffentlichen Firewall-Regelwerk.
- Keine Änderung am Chatbot-Service, Chatbot-Repository, Port 8000 oder dessen
  Python-Umgebung.
- Keine Datenbankinstallation vor einem abgestimmten Wartungsfenster für die
  bereits ausstehenden Systemupdates und den erforderlichen Neustart.

## Phase 0 - Entscheidungen und Restpunkte

1. Wartungsfenster am Freitag, 07.08.2026 vor dem für 15:22 UTC geplanten Crawl
   erfolgreich ausgeführt. Die öffentliche API wurde vor und nach dem Change
   geprüft.
2. Manuel gab das sudo-Passwort ausschließlich interaktiv ein.
3. Für Cloud/Object Storage liegt aktuell keine Freigabe vor. Deshalb bleibt die
   Installation staging-only: leere Datenbank, Migrationen und synthetische
   Testdaten. Lokaler Dump und Restore werden getestet. Vor produktiven Daten
   ist zusätzlich ein verschlüsselter Export auf einen D+P-kontrollierten,
   verschlüsselten Rechner, ein verschlüsseltes Wechselmedium oder eine interne
   Netzwerkfreigabe verpflichtend. Bevorzugter Kandidat ist Manuels
   D+P-Arbeitsrechner am Standort Würzburg; Verschlüsselung, Zugriff und Restore
   aus der heruntergeladenen Kopie sind noch nachzuweisen.
4. Aufbewahrung und Restore-Rhythmus bleiben vor Produktion festzulegen.
5. Reaktionsweg bei fehlgeschlagenem Chatbot-Healthcheck bleibt für das
   dauerhafte Betriebshandbuch festzulegen; beim Change trat kein Fehler auf.

## Phase 1 - Preflight

Read-only prüfen und protokollieren:

```bash
systemctl is-active dp-chatbot.service nginx.service fail2ban.service
systemctl show dp-chatbot.service -p NRestarts -p MemoryCurrent
ss -lntup
free -h
df -hT /
```

Zusätzlich:

- aktuellen Chatbot-Release/Commit als Rückfallpunkt dokumentieren;
- `https://chat-api.donner-partner.de/health` prüfen;
- aktuellen Nginx- und Zertifikatsstatus prüfen;
- bestätigen, dass keine produktive PostgreSQL-Datenbank existiert;
- Wartungsbeginn intern kommunizieren.

Stop-Kriterium: Chatbot oder Nginx ist vor dem Change nicht gesund. Dann keine
Installation beginnen, sondern zuerst den Ausgangszustand klären.

## Phase 2 - Betriebssystem warten

Mit interaktiver sudo-Eingabe:

```bash
sudo apt update
sudo apt full-upgrade
sudo reboot
```

Nach dem Neustart:

```bash
systemctl is-active dp-chatbot.service nginx.service fail2ban.service
ss -lntup
```

Danach den öffentlichen Chatbot-Healthcheck wiederholen. Stop-/Rollbackkriterium:
Chatbot oder HTTPS ist nicht gesund. In diesem Fall noch kein PostgreSQL
installieren.

## Phase 3 - Firewall und Schutzdienste prüfen

```bash
sudo ufw status verbose
sudo fail2ban-client status
```

Erwartung:

- öffentlich nur die bewusst freigegebenen Ports 22, 80 und 443;
- keine Regel für 5432;
- SSH-Schutz durch einen aktiven Fail2ban-Jail oder gleichwertige Maßnahme.

## Phase 4 - PostgreSQL installieren

Status: abgeschlossen und gemäß Ausführungsergebnis verifiziert.

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

Version und Bindung prüfen:

```bash
psql --version
sudo systemctl status postgresql --no-pager
ss -lntp
```

Erwartung: PostgreSQL 16 ist aktiv; Port 5432 ist höchstens an localhost
gebunden und nicht öffentlich erreichbar.

## Phase 5 - Rollen und leere Staging-Datenbank

Status: abgeschlossen. Das reproduzierbare, geheimnisfreie Skript liegt unter
`apps/webapp/database/bootstrap-staging.sql`.

Rollen werden getrennt angelegt:

- `competence_hub_owner`: NOLOGIN-Eigentümerrolle
- `competence_hub_migrator`: LOGIN für kontrollierte Migrationen
- `competence_hub_app`: LOGIN mit nur den benötigten Laufzeitrechten
- Datenbank: `competence_hub_staging`

Die Rollennamen können über ein lokales, geheimnisfreies SQL-Skript erstellt
werden. Passwörter werden anschließend ausschließlich interaktiv über `psql`
gesetzt. Sie werden nicht als Argument in einem Shellbefehl übergeben.

Vor der ersten Migration werden Schema-Owner, Default Privileges und das
Verbot unnötiger Rechte geprüft. Die öffentliche Astro-Website erhält keinen
Datenbankbenutzer.

## Phase 6 - Secret- und Dienstgrenzen

- Produktions-/Staging-Secrets in einem restriktiv berechtigten Systempfad,
  nicht im Git-Checkout.
- Eigener Systembenutzer `competencehub`.
- Eigenes Verzeichnis, Virtual Environment, systemd-Unit und eigener interner
  Backend-Port, beispielsweise `127.0.0.1:8001`.
- Chatbot und Competence Hub teilen keine ENV-Datei, Rolle, Datenbank oder Logs.

## Phase 7 - Backup und Restore-Test

Status: lokaler synthetischer Dump/Restore erfolgreich; externer verschlüsselter
Restore-Nachweis vor Produktivdaten weiterhin offen.

Für das erste Staging ohne Echtdaten:

1. Rollen/Globals mit `pg_dumpall --globals-only` sichern.
2. Datenbank mit `pg_dump --format=custom` sichern.
3. Dump in eine temporäre Restore-Datenbank zurückspielen.
4. Schema, Tabellenanzahl und einen synthetischen Testdatensatz prüfen.
5. Temporäre Restore-Datenbank nach erfolgreicher Prüfung kontrolliert löschen.

Zusätzlich vor produktiven Daten:

1. Dump clientseitig verschlüsseln; Passphrase nicht in Skript oder Shell-
   Argument speichern.
2. Verschlüsselten Dump per SSH/SCP auf einen D+P-kontrollierten, verschlüsselten
   Rechner, eine interne Freigabe oder ein verschlüsseltes Wechselmedium
   übertragen.
3. Prüfsumme und Übertragung dokumentieren.
4. Restore aus genau dieser externen Kopie erfolgreich testen.

Ein erfolgreich geschriebener Dump ohne externe Kopie und Restore-Test gilt
nicht als vollständiges Produktiv-Backup-Gate.

## Phase 8 - Abnahme

Status: Staging technisch abgenommen. Das Off-Server-Backup-Gate verhindert
weiterhin produktive Datenverarbeitung.

- Chatbot-Healthcheck weiterhin erfolgreich.
- Nginx, Fail2ban und PostgreSQL aktiv.
- Keine neuen öffentlichen Ports.
- PostgreSQL nur lokal erreichbar.
- Rollen nach Least Privilege geprüft.
- Leere Migration gegen Staging erfolgreich.
- Backup und Restore mit synthetischen Daten erfolgreich.
- Speicher- und RAM-Auslastung erneut dokumentiert.

## Rollback und Reparatur

### Vor Anlage produktiver Daten

- Bei Installationsfehlern PostgreSQL stoppen und deaktivieren.
- Keine Paketentfernung oder Datenbanklöschung ohne gesonderte Bestätigung.
- Angelegte leere Rollen/Datenbanken nur nach dokumentierter Prüfung entfernen.
- Chatbot und Nginx unabhängig prüfen; sie dürfen nicht Teil des PostgreSQL-
  Rollbacks sein.

### Nach späteren Migrationen

- Anwendung auf den vorherigen Release-Tag zurücksetzen.
- Datenbankschema nur über eine geprüfte Down-Migration oder Restore reparieren.
- Niemals eine produktive Datenbank spontan löschen oder überschreiben.

## Nachweise

Nach dem Change im Projektlog festhalten:

- Wartungszeit und Freigabeowner
- installierte PostgreSQL-Version
- öffentliche und lokale Ports
- Rollen ohne Secretwerte
- Healthcheck-Ergebnisse
- Backupziel nur als Systembezeichnung, nicht als Zugangsdaten
- Restore-Testergebnis
- verbleibende Risiken und nächster Schritt
