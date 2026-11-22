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
