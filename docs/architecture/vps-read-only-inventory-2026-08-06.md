# Read-only VPS Inventory

Stand: 06.08.2026

Status: Abgeschlossen ohne Systemänderung. Es wurden keine Secrets,
Umgebungsvariablen, Konfigurationsinhalte, Logs, Datenbanken oder Nutzdaten
geöffnet.

## Zweck und Freigabe

Manuel hat als operativer Serververantwortlicher die rein lesende Inventur des
bereits für den Donner-+Partner-Chatbot genutzten VPS freigegeben. Ziel war ein
Go/No-Go für eine getrennte Competence-Hub-Laufzeit, nicht deren Einrichtung.

## Festgestellter Zustand

| Bereich | Befund |
| --- | --- |
| Betriebssystem | Ubuntu 24.04 LTS, Linux 6.8, KVM |
| Laufzeit | 111 Tage; Systemuhr und NTP aktiv, Zeitzone UTC |
| CPU | 6 vCPUs; Last bei der Inventur praktisch 0 |
| Arbeitsspeicher | 7,7 GiB gesamt; rund 6,8 GiB verfügbar |
| Swap | nicht eingerichtet |
| Speicher | 232 GiB Root-Dateisystem; rund 228 GiB frei |
| Reverse Proxy | Nginx 1.24 aktiv; vorhandene Site für die Chatbot-API |
| Chatbot | eigener systemd-Dienst aktiv, 0 Neustarts, rund 44 MiB RAM |
| Externe Ports | 22, 80 und 443 |
| Interner App-Port | Uvicorn ausschließlich auf `127.0.0.1:8000` |
| Schutzdienste | Fail2ban und unattended-upgrades aktiv |
| Laufzeiten | Python 3.12 vorhanden; Node.js, Docker und Caddy nicht installiert |
| Datenbank | PostgreSQL, MariaDB und MySQL nicht als aktive Dienste vorhanden |
| Zeitpläne | wöchentlicher Chatbot-Crawler sowie System-, Zertifikats-, Update- und Log-Timer aktiv |
| Updates | mehrere System- und Kernelupdates ausstehend; Neustart ist erforderlich |

## Findings und Gates

### Blocker vor produktiven personenbezogenen Daten

1. **Anwendungs- und Datenbankbackup nicht nachgewiesen.** In den sichtbaren
   systemd-Timern ist kein Competence-Hub- oder allgemeiner App-/Datenbankbackup
   erkennbar. Cron-Inhalte wurden wegen möglicher Secrets bewusst nicht gelesen.
   Vor Produktivdaten sind ein verschlüsseltes Off-Server-Ziel, Aufbewahrung,
   Monitoring und ein erfolgreicher Restore-Test erforderlich.
2. **Rechte- und Datenschutzkonzept fehlt noch.** Die organisatorische Freigabe
   durch Manuel ersetzt nicht die technische Prüfung von Datenminimierung,
   Rollen, Löschung, Protokollierung, Auskunft und Aufbewahrung.

### Vor Installation zu beheben oder zu bestätigen

1. **Wartungsstand:** Sicherheits-/Kernelupdates sind verfügbar und
   `/var/run/reboot-required` ist vorhanden. Updates und Neustart brauchen ein
   angekündigtes Chatbot-Wartungsfenster mit anschließendem Healthcheck.
2. **Firewallprüfung:** Von außen wurden nur 22, 80 und 443 beobachtet. Der
   detaillierte UFW- und Fail2ban-Status konnte ohne interaktive sudo-Freigabe
   nicht gelesen werden. Regeln und aktive Jails müssen administrativ bestätigt
   werden, bevor ein weiterer Dienst eingerichtet wird.
3. **Betriebsübergabe:** Manuel ist derzeit alleiniger Operator. Für Urlaub,
   Ausfall und Übergabe werden ein zweiter kontrollierter Zugang, Runbook und
   klarer Incident-Kontakt benötigt.
4. **Swap/Memory-Schutz:** Aktuell ist kein Swap eingerichtet. Wegen der großen
   RAM-Reserve ist das kein unmittelbarer Engpass, aber ein kontrolliertes
   Memory-Limit je Dienst und eine bewusste Swap-/OOM-Entscheidung sind nötig.

## Kapazitätsbewertung

Die gemessenen CPU-, RAM- und Speicherreserven reichen deutlich für einen
kleinen Competence-Hub-Pilot. Nginx, Python, systemd, Zertifikatsautomation und
die interne Bindung des bestehenden Uvicorn-Dienstes bilden ein brauchbares
Betriebsmuster.

Das Ergebnis ist ein **Conditional Go**:

- Go für Architekturarbeit, lokale Entwicklung und später ein strikt getrenntes
  Staging mit synthetischen Testdaten.
- Noch kein Go für produktive personenbezogene oder Unternehmensdaten.
- Kein gemeinsamer Prozess, Systembenutzer, Port, Verzeichnis, Secret,
  Python-Environment oder Datenbankbereich mit dem Chatbot.

## Empfohlene technische Richtung

- Eigenständiges FastAPI-Backend in separatem Python-Virtual-Environment, weil
  dieser Betriebsweg auf dem VPS bereits bekannt ist.
- Eigener systemd-Systembenutzer `competencehub`; nicht der vorhandene Benutzer
  des Chatbot-Dienstes.
- Eigene relationale Datenbank nur auf localhost/private Socket, ohne
  öffentlichen Datenbankport.
- Eigenständige Nginx-Site und API-/App-Subdomain.
- Ressourcenlimits, Healthcheck, getrennte Logs, Backup und Rollback je Dienst.
- Datenbankentscheidung als ADR; IONOS MySQL beeinflusst diese Entscheidung
  nicht, weil es vom VPS nicht erreichbar ist.

## Noch offene technische Entscheidungen

- PostgreSQL oder MySQL/MariaDB für den eigenständigen Backend-Slice.
- Separate Staging-Instanz auf demselben VPS oder später eigener Staging-Server.
- Backupziel, Aufbewahrung, Verschlüsselung, RPO/RTO und Restore-Rhythmus.
- Monitoring/Alarmierung und zweiter administrativer Notfallzugang.
- Konkrete API-/App-Subdomains und DNS-/TLS-Changeprozess.
