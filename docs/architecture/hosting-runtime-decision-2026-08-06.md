# Hosting- und Runtime-Entscheidung

Stand: 06.08.2026

Status: Entscheidungsvorlage nach abgeschlossener read-only VPS-Inventur. Noch
keine Serveränderung, Datenbankeinrichtung oder Veröffentlichung.

Folgestatus 07.08.2026: Die hier empfohlene isolierte VPS-Stagingrichtung wurde
für PostgreSQL umgesetzt. Systemwartung, Firewallprüfung, localhost-only
PostgreSQL 16.14, getrennte Rollen und ein lokaler synthetischer Restore-Test
sind abgeschlossen. Der historische Inventurbefund unten bleibt unverändert;
aktuelle Nachweise stehen im `postgresql-16-installation-runbook.md`. Reale
Daten bleiben bis zum verschlüsselten Off-Server-Restore gesperrt.

## Anlass

Die EDV-Rückmeldung klärt, welche Teile des Competence Hub auf dem vorhandenen
IONOS-Webhosting betrieben werden können. Zusätzlich steht ein bereits für den
Donner-+Partner-Chatbot genutzter VPS unter Manuels administrativer Kontrolle
als mögliche separate Laufzeitumgebung zur Verfügung.

## Bestätigte Infrastruktur-Fakten

### IONOS-Webhosting

- Der Webspace ist die Produktionsumgebung.
- `competence-hub.donner-partner.de` und
  `competencehub.donner-partner.de` zeigen auf denselben Webspace.
- Ein Wildcard-TLS-Zertifikat für `*.donner-partner.de` deckt beide Subdomains
  ab.
- Der SFTP-Zugang führt direkt in das Startverzeichnis der Website.
- Statische Dateien und PHP sind vorgesehen.
- Dauerhaft laufende Node.js-, Python- oder andere Serverprozesse sind nicht
  möglich.
- Die IONOS-MySQL-Datenbank ist nur vom eigenen Webspace erreichbar. Ein
  Backend auf einem externen VPS kann diese Datenbank nicht direkt nutzen.
- Datenbank-Backups erfolgen täglich mit 14 Tagen Aufbewahrung. Langfristige
  Webspace- und Datenarchivierung bleibt eigene Verantwortung.
- IONOS-Cronjobs sind nur täglich, wöchentlich oder monatlich planbar;
  `cronjob.de` steht für feinere externe Zeitpläne zur Verfügung.
- Skriptbasierter E-Mail-Versand unterliegt einem nicht genau dokumentierten
  Ratenlimit.
- Ausgehende API-Aufrufe sind voraussichtlich möglich, aber noch nicht durch
  eine verbindliche IONOS-Auskunft bestätigt.

### Vorhandener VPS

- Der VPS ist keine leere Umgebung. Er betreibt bereits den Donner-+Partner-
  Chatbot mit FastAPI, systemd-Service, öffentlicher API und einem separaten
  systemd-Crawl-Timer.
- Manuel besitzt administrativen Zugriff und ist aktuell alleiniger Nutzer.
- Die read-only Inventur bestätigt 6 vCPUs, 7,7 GiB RAM, rund 228 GiB freien
  Speicher und sehr geringe Last. Die Kapazität reicht für einen kleinen,
  getrennten Pilotdienst.
- Nginx, Python, systemd, Fail2ban und unattended-upgrades sind vorhanden. Der
  Chatbot bindet seinen Uvicorn-Port nur lokal; öffentlich sind 22, 80 und 443.
- Es ist keine aktive Datenbank vorhanden. Eigene App-/Datenbankbackups und ein
  Restore-Test sind noch nicht nachgewiesen.
- System-/Kernelupdates und ein Neustart stehen aus. Firewalldetails konnten
  ohne interaktive sudo-Freigabe noch nicht vollständig geprüft werden.
- Manuel übernimmt Serverbetrieb, Patchen, Monitoring, Backups und
  Notfallreaktion. Ein zweiter kontrollierter Notfallzugang bleibt erforderlich.
- Die Chatbot-Datenquellen und eine künftige Competence-Hub-Datenbank müssen
  technisch und organisatorisch getrennt bleiben.

## Architektur-Optionen

| Option | Vorteile | Nachteile | Bewertung |
| --- | --- | --- | --- |
| Statische Astro-Website auf IONOS, kein Backend | schnell, wartungsarm, vorhandene Domains und TLS nutzbar | kein Login, keine Datenbank-Workflows, Kontakt bleibt E-Mail/Weiterleitung | geeignet für den aktuellen Website-MVP |
| Astro plus PHP-Backend und IONOS-MySQL | nutzt vorhandenen Webspace und die erreichbare MySQL-Datenbank | neuer PHP-Stack, eingeschränkte Jobs/Prozesse, langfristige App-Roadmap wird enger | nur sinnvoll, wenn bewusst ein PHP-System gewählt wird |
| Astro auf IONOS, Backend und eigene DB auf vorhandenem VPS | klare Trennung, dauerhafte API möglich, vorhandenes FastAPI/systemd-Betriebswissen wiederverwendbar | Co-Hosting-Risiko für Chatbot und Competence Hub; Governance, Kapazität, Backup und DNS müssen geklärt werden | bevorzugte Pilotoption nach Freigabe und Inventur |
| Astro auf IONOS, Backend und DB auf neuem dedizierten VPS | beste Isolation und klarer Lebenszyklus | zusätzliche Kosten und Betriebsverantwortung | Rückfalloption bei fehlender Freigabe oder Kapazität |

## Vorläufige Empfehlung

1. Die öffentliche Astro-Website wird als statisches Build-Artefakt auf dem
   IONOS-Webspace betrieben.
2. GitHub Pages bleibt ausschließlich eine manuell gestartete, mit `noindex`
   markierte Review-Umgebung.
3. Das spätere Backend und seine unabhängige Datenbank werden nicht in das
   öffentliche Astro-Frontend und nicht in die bestehende Chatbot-Anwendung
   eingebaut.
4. Die read-only Inventur ergibt ein Conditional Go für ein getrenntes Staging
   mit Testdaten. Produktivdaten bleiben bis Patch-, Firewall-, Backup-,
   Restore-, Rechte- und Datenschutzgate gesperrt.
5. Nach Erfüllung dieser Gates erhält Competence Hub eigene Services,
   Verzeichnisse, Systembenutzer, Konfigurationen, Datenbankrollen, Backups,
   Logs und Subdomains. Gemeinsame Secrets oder Datenbanken mit dem Chatbot sind
   ausgeschlossen.

## Zielbild

```text
Browser
  |
  +-- competencehub.donner-partner.de
  |     -> statische Astro-Website auf IONOS
  |
  +-- app.<finale-domain> / api.<finale-domain>
        -> TLS + Reverse Proxy auf freigegebenem VPS
        -> eigenständiges Competence-Hub-Backend
        -> lokale/private Competence-Hub-Datenbank

Interne Review
  -> manuell gestartete GitHub-Pages-Version mit noindex
```

Die Nutzung eigener App-/API-Subdomains ist durch Manuel grundsätzlich
freigegeben. Konkrete Namen, DNS-Einträge und TLS-Inbetriebnahme werden vor der
Änderung dokumentiert.

Details: `vps-read-only-inventory-2026-08-06.md` und
`versioning-and-operations-plan.md`.

## Entscheidungen vor Umsetzung

### Durch Manuel und Fachseite

1. Kanonische Website-Domain ist `competencehub.donner-partner.de`; die zweite
   Domain soll dauerhaft umleiten.
2. Soll die statische Website vor dem Backend live gehen? Empfehlung: ja, nach
   Rechts-, Inhalts- und Kontaktprozess-Freigabe.
3. Was ist der erste echte Webapp-Slice? Empfehlung: interne Bedarfserfassung,
   Coach-/Service-Zuordnung und Statuspflege, noch ohne Firmen- oder Coachlogin.
4. Janay Rappelt verantwortet die Mailbox. Reaktionszeit und Abwesenheits-
   vertretung sind noch festzulegen; Contentpflege und fachliche Freigaben
   bleiben beim zuständigen Fachbereich.

### Mit EDV/Organisation

1. Manuel hat den vorhandenen VPS als Kandidaten sowie die spätere Verarbeitung
   von Competence-Hub-Unternehmens- und personenbezogenen Daten grundsätzlich
   freigegeben. Technische und datenschutzbezogene Produktivgates bleiben
   verpflichtend.
2. Manuel übernimmt Patchen, Monitoring, Backup und Incident-Reaktion. Vertrag,
   Abrechnung und Nachfolgezugriff sind noch organisatorisch festzuhalten.
3. Eigene App-/API-Subdomains sind grundsätzlich freigegeben; konkrete DNS- und
   TLS-Änderungen werden separat umgesetzt.
4. Welche Backup-Aufbewahrung, Verschlüsselung, externe Ablage und
   Wiederherstellungszeit werden verlangt?
5. Ist eine getrennte Staging-Umgebung erforderlich oder reicht zunächst eine
   logisch getrennte Staging-Instanz auf dem VPS?

### Technisch nach read-only Inventur

1. CPU, RAM und Speicher reichen für einen kleinen Pilot. Die Auslastung wird
   nach einem Staging-Start erneut geprüft.
2. Welche Reverse-Proxy-, Firewall-, Container-/systemd- und Monitoring-
   Standards sind bereits vorhanden?
3. Welche Datenbank wird auf dem VPS betrieben? Die IONOS-MySQL-Vorgabe legt
   die VPS-Datenbank nicht fest.
4. Welcher Backend-Stack ist langfristig wartbar? FastAPI ist wegen des
   vorhandenen Betriebswissens eine plausible Option, aber noch kein Beschluss.

## Nächste Arbeitsblöcke

### Arbeitsblock 1 - Entscheidungen und Inventurfreigabe (weitgehend erledigt)

- kanonische Website-Domain festlegen
- EDV-Freigabe für den VPS-Einsatzzweck einholen
- Betriebs- und Backup-Verantwortung benennen
- read-only VPS-Inventur ausdrücklich freigeben

Erledigt: Domain, VPS-Grundfreigabe, operativer Owner und Inventur. Offen:
konkrete Betreiber-Gesellschaft, Mailbox-Owner, Backupziel und Nachfolgezugriff.

Ergebnis: unterschriftsfreie technische Entscheidung, noch keine Änderung.

### Arbeitsblock 2 - Read-only VPS-Inventur und ADR (Inventur erledigt)

- Betriebssystem, Ressourcen, Dienste, Ports, Reverse Proxy, Firewall,
  Datenbanken, Speicher und Backupmöglichkeiten prüfen
- Chatbot-Auslastung und Konfliktrisiko dokumentieren
- Backend-Stack, Datenbank, Staging-Form und Subdomains entscheiden
- ADR und umsetzbaren Change-/Rollback-Plan erstellen

Erledigt: Kapazität, Dienste, Ports, Laufzeiten und sichtbare Timer. Offen:
administrative Firewallprüfung, Datenbank-/Staging-ADR und Backup-/Restoreplan.

Ergebnis: Go/No-Go für Co-Hosting auf dem bestehenden VPS.

### Arbeitsblock 3 - Statische Website produktionsbereit machen

- kanonische `site`-URL und Domainumleitung konfigurieren
- Produktion von GitHub-Pages-Review trennen
- Cache-/Security-Header, Fehlerseiten, robots/sitemap und rechtliche Links
  prüfen
- manuelles SFTP-Deployment mit lokalem Rollback-Artefakt vorbereiten
- erst nach Freigabe deployen und HTTPS-/Routing-/Kontakt-Smoke-Tests ausführen

Ergebnis: veröffentlichungsfähige statische Website ohne Backendabhängigkeit.

### Arbeitsblock 4 - Backend-Grundlage mit Testdaten

- eigenständiges Backend-Projekt, Migrationen und lokale Testdaten aufsetzen
- interne Rollen `admin` und `staff` absichern
- Company, Coach, Service und CoachingRequest als ersten Slice umsetzen
- keine produktiven personenbezogenen Daten vor Datenschutz-, Backup- und
  Restore-Gate speichern

Ergebnis: lokal beziehungsweise in freigegebenem Staging prüfbarer erster
Webapp-Slice.

## Deployment-Gates

- Kein Produktivdeployment ohne benannten Freigabeowner.
- Keine Secrets in Git, Dokumentation oder gemeinsamer Chat-Historie.
- Kein öffentlicher Datenbankport.
- Kein Co-Hosting ohne Ressourcen- und Ausfallrisikoprüfung für den Chatbot.
- Keine echten Kunden-/Coachdaten vor Rollen-, Datenschutz-, Backup- und
  Restore-Prüfung.
- Nach jedem Deployment: Healthcheck, Kernrouten, Login-/Rechteprüfung,
  Fehlerlogkontrolle und dokumentierter Rollbackpunkt.
