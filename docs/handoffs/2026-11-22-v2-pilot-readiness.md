# Competence Hub V2: Pilotbereitschaft

**22.11.2026.** Geschützter synthetischer Releasekandidat. Neue
Geschäftsfunktionen und Datenbankschema bleiben unverändert. Die vorhandene
V1.2-Fachabnahme bleibt gültig; V2 ist dadurch weder fachlich abgenommen
noch für einen VPS oder für echte Personen freigegeben.

## Betrieb und Entscheidungen

1. **V2-Fachabnahme:** Den bestehenden [Demoablauf](2026-11-21-v2-next-level.md#gemeinsame-vorf%C3%BChrung)
   mit Manuel und Frau Rappelt durchspielen. Die gesprochene Prüfung am sichtbaren
   Testdesktop gemäß [NVDA-Smoke](portal-screenreader-smoke.md) dokumentieren;
   Tastatur, Fokus und Accessibility Tree ersetzen die Sprachausgabe nicht.
2. **Zugang und EDV:** In den [Pilot-Startbedingungen](../operations/portal-pilot-launch-conditions.md)
   stehen aktueller Belegstand, Rollen und die einzige EDV-Entscheidungsliste.
   Der zuletzt verifizierte VPS-Stand ist V1.2/`0006` mit 27 Tabellen und sechs
   Diensten. Kein frischer Live-Abgleich. Das zuletzt belegte private
   TLS-Zertifikat endet am **30.11.2026, 19:09:39 MEZ**; gesondert über einen
   weiter gültigen Zugang oder Aussetzung entscheiden, nie Prüfung umgehen.
3. **Unabhängige VPS-Recovery:** Einen bereits zugelassenen Empfänger, ein
   geschütztes Ziel und getrennt nutzbaren Recovery-Zugang festlegen. Danach
   separat eine frische Sicherung und Restoreprobe mit Laufzeit und Parität
   autorisieren. Der GPG-R2-Arbeitsblock bleibt pausiert. Kein Export von
   VPS-Daten oder Wiederanlauf mit Echtdaten aus dieser Probe.
4. **Kontrollierter Pilot:** [Installationsreihenfolge, Migration und Smoke](../operations/portal-v2-private-staging.md)
   verwenden. Erst Ist-Stand, Sicherung und Restore belegen, dann getrennt
   freigegebenen Klon migrieren, isoliert abnehmen und nur eigene V2-Dienste
   aktivieren. Bei Fehlschlag V2 stoppen, den unveränderten V1.2-Zugang samt
   Ursprungsdaten und sechs Diensten prüfen. Kein Down-Migrate und kein Restore
   über die laufende Datenbank. Spätere persönliche Zugänge, SMTP, Datenimporte
   und Echtdaten sind getrennte Entscheidungen. Kein automatischer Übergang.

## Konfigurationsgrenze

Die [Konfigurationsreferenz](../../deploy/v2/runtime-config.example) enthält
nur Schlüsselnamen und feste, nicht geheime Pilotwerte. Leere Pflichtwerte
verhindern den Start. Der Operator verwaltet die tatsächliche Konfiguration
getrennt und root-geschützt, mit isolierter DB und genehmigter Schlüsselverwahrung.
Der Releasekandidat aktiviert weder SMTP noch Worker, echte Einladungen,
Personenimporte oder Website-Login. Frau Hupp und Frau Rappelts ungeprüftes
Profil bleiben unveröffentlicht.

## Lokaler Restore-Nachweis

Der [Recovery-Runner](../../scripts/verify-webapp-v2-recovery.ps1) verwendet
zwei frische Linux-/PG16-Instanzen und die bereits lokal vorhandenen,
gepinnten Images. Alle Container sind netzlos und ohne veröffentlichte Ports.
Nur synthetische Daten, flüchtige Docker-Volumes und temporäre OpenPGP-Keys
kommen zum Einsatz. Der Sender verschlüsselt nur mit dem öffentlichen
Schlüssel. Ausgangssystem und Klartext-Quelle werden vor der Wiederherstellung
entfernt. Ein frischer Schlüsselbund überprüft SHA-256 und entschlüsselt mit
der separaten synthetischen Verwahrung. Der Zielcontainer installiert dieselbe
ZIP und startet das Portal als unprivilegierter lokaler Prozess. Ein echter
VPN-/Proxy-/TLS- oder systemd-Start auf dem VPS wird dadurch nicht belegt.

Ziel der Probe: eigener PostgreSQL-System-Identifier, Daten-/Schema-/ACL- und
Sequenzparität, wiederhergestellte Anmeldung per MFA-Recovery, korrektes
Lesen/Schreiben einer Anfrage samt Notiz und Audit. Negative Prüfungen:
anonym, falscher Origin, falscher CSRF-Token, veraltete Version, Zugriff nach
Logout. Keine Windows-Identität, DPAPI oder realen Schlüssel benötigt.

## Prüfungen und Release

| Prüfbereich | Ergebnis |
| --- | --- |
| Integrierter Firefox-/PG16-Lauf | **45 PASS**: CAL-1, CAL-2, Kapazität, Rückfragen und revisionssichere Vormerkung, Kundenakte, Anfrage, Mandanten- und Notizgrenzen, Coachwechsel, parallele Aktionen, Neustart und Bereinigung. |
| Gezielte Regression | **101 PASS** für Auth, MFA, Session, Portal, Kunden und Anfragen. Fokussierbare Authfehler, Meldung am zugehörigen Anfragefeld und Tastaturweg zur Konfliktauflösung nachgeprüft. |
| Synthetisches Onboarding | **PASS**: Einladung in der lokalen Outbox erfasst und im Testprozess eingelesen, Aktivierung, Passwort, MFA, Einführung, Abmeldung und erneute Anmeldung bis zur richtigen Prüfliste. Kein externer Mailtransport gestartet. |
| Migration und Rückfall | **6 Linux-Prüfungen PASS**: vollständige Kette `0006` nach `0013`, Altwerte erhalten, fehlerhafte Kette atomar zurückgerollt, unzulässige Notizrechte blockieren Bereitschaft. Referenz bleibt erhalten; der echte V1.2-Dienstrückfall ist nur geplant. |
| Unabhängige synthetische Recovery | **PASS** mit exakt dem unten gebundenen ZIP. Installierte Anwendung im Zielprozess ausgeführt; Parität, wiederhergestelltes MFA-Recovery, exakte Reviewerrolle und geschütztes Schreiben belegt. Eigene Container und Volumes entfernt. |
| Echte Recovery und gesprochene Prüfung | **OFFEN**. Kein VPS-Export, kein Real-Restore, kein bestandener NVDA-/Narrator-Sprachnachweis. |

Paketquelle: `e948e8cd1ee90613b5c638cee44566c7ed755714`.
Das doppelt bytegleich gebaute ZIP und seine Begleitdateien liegen lokal unter
`release-artifacts/v2-pilot-readiness-20261122/<Paketquelle>/`.
ZIP: `private-vps/competence-hub-private-v2-<Paketquelle>.zip`.

- ZIP-SHA-256: `ace1f89995bd187e2db4c12a4c252ebffd88ac3c542065e4ac148c62da04fc2e`
- `tested-source.json` SHA-256: `1082e87b40283aab5ddd6594c122e9bd5daba9ee8318625bf73e83461ef2bee9`
- `operator-bundle.json` bindet die ZIP, Quellbestätigung,
  nicht geheime Konfigurationsreferenz und das lokale Recovery-Protokoll.
  `deployment_authorized: false`; Inhalt der ZIP: Wheel, gepinnte Linux-
  Abhängigkeiten, Migrationen `0007` bis `0013`, kontrollierte Clone-/Host-
  Helfer, Dienst- und Proxyvorlagen und Installationshandbuch.

IONOS, GitHub Pages und VPS wurden nicht verändert. Der Repo-Workflow für
Pages wird ausschließlich manuell ausgelöst; kein Push-Deployment.
