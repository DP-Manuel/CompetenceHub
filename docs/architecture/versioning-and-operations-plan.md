# Versioning and Operations Plan

Stand: 07.08.2026

Status: Vorschlag. Keine Deployment-Automation oder Serveränderung umgesetzt.

## Vier getrennte Sicherungsebenen

1. **Quellcode:** Git und GitHub versionieren Website, Webapp, Migrationen,
   Deploymentskripte und geheimnisfreie Konfigurationsvorlagen.
2. **Release:** Tags und Build-Artefakte machen eine konkret veröffentlichte
   Version reproduzierbar und rücksetzbar.
3. **Anwendungsdaten:** Verschlüsselte Datenbank- und Dateibackups liegen
   außerhalb von GitHub und außerhalb des einzigen VPS.
4. **Betrieb:** Patchstand, Monitoring, Runbooks, Restore-Tests und
   Notfallzugänge halten den Dienst tatsächlich wiederherstellbar.

GitHub ersetzt weder Datenbankbackups noch ein Server-Backup.

## Git- und Release-Modell

- Das vorhandene Repository `DP-Manuel/CompetenceHub` bleibt die zentrale
  Quellcodequelle.
- `main` ist jederzeit buildbar und grundsätzlich releasefähig.
- Größere Backend-, Datenbank- oder Deploymentänderungen erfolgen über kurze
  Feature-Branches und Review vor dem Merge.
- Website und Webapp erhalten nachvollziehbare Release-Tags, beispielsweise
  `website-v0.2.0` und später `webapp-v0.1.0`.
- Abhängigkeiten werden gelockt; Datenbankschemaänderungen werden als
  versionierte Migrationen gespeichert.
- Secrets, reale Exporte, Datenbankdumps, private Schlüssel, `.env*` und
  Produktionslogs werden niemals committed.

## Website-Deployment

### Erste sichere Stufe

1. Lokal oder in GitHub Actions den Astro-Build ausführen.
2. Das fertige statische Artefakt mit Commit-ID und Zeitstempel archivieren.
3. Vorhandenen IONOS-Webstand als Rollback-Artefakt sichern.
4. Nach Freigabe durch den IT-Leiter manuell per SFTP veröffentlichen.
5. HTTPS, kanonische Domain, Weiterleitung, Kernrouten, Rechtstexte und Kontakt
   prüfen.
6. Bei Fehlern das vorherige statische Artefakt wiederherstellen.

### Spätere Automatisierung

- Manueller GitHub-Workflow mit geschützter Produktionsumgebung und expliziter
  Freigabe; kein automatisches Deployment bei jedem Push.
- SFTP-/SSH-Zugang ausschließlich als GitHub Environment Secret.
- Derselbe Build-, Smoke-Test- und Rollbackablauf bleibt verpflichtend.

## Backend-Deployment

Für den Pilot passt ein systemd-/Python-Virtual-Environment-Modell zum
vorhandenen Serverbetrieb. Ein Deployment soll nicht durch ein unkontrolliertes
`git pull` im laufenden Prozess enden.

1. Tests und Migrationstest gegen eine leere Testdatenbank ausführen.
2. Freigegebenen Tag beziehungsweise Commit auf dem VPS abrufen.
3. Abhängigkeiten reproduzierbar in einem eigenen Virtual Environment
   installieren.
4. Backup-/Restore-Gate prüfen; danach notwendige Migration ausführen.
5. Eigenständigen Competence-Hub-Dienst neu starten.
6. Healthcheck, Rechteprüfung und zentrale Workflow-Smoke-Tests ausführen.
7. Bei einem Fehler auf den dokumentierten vorherigen Release-Stand
   zurückgehen; Datenmigrationen benötigen einen eigenen Repair-/Rollbackplan.

Die erste Durchführung bleibt manuell und dokumentiert. Eine spätere
`workflow_dispatch`-Automation ist sinnvoll, sobald mindestens ein manueller
Release und Rollback erfolgreich geprobt wurden.

## Serverkonfiguration und Secrets

- Nginx- und systemd-Vorlagen dürfen geheimnisfrei im Repository liegen.
- Installierte Konfigurationen und Secrets liegen außerhalb des Repositorys in
  restriktiv berechtigten Systempfaden.
- Competence Hub erhält einen eigenen Systembenutzer, eigene Verzeichnisse,
  eigenes Virtual Environment, eigene Datenbankrolle und eigene Logs.
- Die Datenbank hört nur lokal; ausschließlich das Backend erhält Zugriff.
- Der Chatbot wird durch Competence-Hub-Deployments weder neu gestartet noch
  verändert.

## Backup- und Restore-Vorschlag

- Aktuelle Entscheidung: keine Cloud-/Object-Storage-Beschaffung ohne interne
  Berechtigung. PostgreSQL startet deshalb nur als Staging mit synthetischen
  Daten; das Produktivdaten-Gate bleibt geschlossen.
- Praktische Nicht-Cloud-Zwischenlösung: verschlüsselte PostgreSQL-Dumps per SCP
  auf einen D+P-kontrollierten Rechner, eine interne Netzwerkfreigabe oder ein
  verschlüsseltes Wechselmedium übertragen. Ablage immer außerhalb des Git-
  Repositorys und außerhalb des Website-Webspaces.
- Kandidat 07.08.2026: Manuels D+P-Arbeitsrechner am Standort Würzburg im
  dortigen internen Netzwerk. Der Rechner initiiert den Download vom VPS; es
  wird kein eingehender Port am Standort geöffnet. Vor Freigabe sind
  vollständige Datenträgerverschlüsselung, eingeschränkter Nutzerzugriff,
  ausreichend Speicher, Aufbewahrungsort und Wiederherstellung aus der exakt
  heruntergeladenen verschlüsselten Kopie nachzuweisen.
- Zukünftige Option nach interner Freigabe: getrenntes IONOS Object Storage für
  logische PostgreSQL-Dumps mit clientseitiger Verschlüsselung,
  Versionierung/Object Lock und eigenem eingeschränkten Zugriffsschlüssel.
- Ebenfalls erst nach Freigabe: IONOS Cloud Backup für vollständige
  VPS-/Datei-Wiederherstellung.
  Das ersetzt den portablen PostgreSQL-Dump und seinen Restore-Test nicht.
- Zusätzliche periodische Kopie auf D+P-internem Speicher, damit VPS, Website
  und einzige Backups nicht vollständig von demselben Anbieter/Konto abhängen.
- Den IONOS-Webspace nur verwenden, wenn EDV einen nicht öffentlich erreichbaren
  Speicherbereich bestätigt. Keine Datenbankdumps im Website-Document-Root.
- Tägliches verschlüsseltes Datenbankbackup in ein getrenntes Off-Server-Ziel.
- Zusätzlich vor jeder produktiven Migration ein versioniertes Backup.
- Aufbewahrung zunächst 30 tägliche und 12 monatliche Wiederherstellungspunkte;
  endgültige Fristen müssen Datenschutz und Fachbereich bestätigen.
- Backupjobs überwachen und Fehler aktiv melden.
- Restore zunächst vor Produktivstart, danach mindestens quartalsweise in einer
  isolierten Umgebung testen und protokollieren.
- Website-Buildartefakte, Benutzerdateien und Datenbank getrennt sichern.

## Verantwortlichkeiten

| Aufgabe | Verantwortlich / Freigabe |
| --- | --- |
| Serverbetrieb, Patchen, Monitoring, Backup und Notfallreaktion | Manuel |
| Freigabe des Website-Produktionsdeployments | Thomas Roß, EDV-Leiter |
| Quellcode und Releasevorbereitung | Manuel mit Review-Unterstützung |
| Fachliche Inhalte und Coachfreigaben | zuständige Fachseite |
| Mailbox und Antwortprozess | Janay Rappelt |
| Rechtlicher Ansprechpartner | Lars Donner |
| Rechtlicher Betreiber und Datenschutzfreigabe | konkrete Gesellschaft und finales Impressum noch zu bestätigen |

## Nächster Betriebsblock

Der Wartungs-, Firewall- und PostgreSQL-Staging-Block wurde am 07.08.2026
erfolgreich ausgeführt. Details und Nachweise stehen im
`postgresql-16-installation-runbook.md`.

1. Den planmäßigen Freitagscrawl nach Abschluss prüfen.
2. Ein verschlüsseltes D+P-kontrolliertes Off-Server-Backupziel festlegen.
3. Den lokalen PostgreSQL-Dump verschlüsselt dorthin übertragen und aus genau
   dieser externen Kopie einen Restore nachweisen.
4. Aufbewahrung, Monitoring, Fehleralarm und Nachfolgezugriff festlegen.
5. Erst danach reale Daten zulassen; bis dahin bleibt PostgreSQL leer und
   staging-only.
