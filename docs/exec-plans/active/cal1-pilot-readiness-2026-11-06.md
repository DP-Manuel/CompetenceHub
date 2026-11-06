# CAL-1 Next Level: lokaler Pilotnachweis

Stand06.11.2026. Auftrag: A bis E eigenständig ausführen, vor Janays Rückkehr
ab16.11 nicht auf fachliche Vorführung warten. Basis `d563e76`.

## Grenze

Nur isolierter lokaler PostgreSQL-Wegwerfcontainer und synthetische Personen.
Bestehendes Staging, VPS, IONOS, Pages, echte Konten und Coachzuordnungen bleiben
unverändert. Kein GPG/Backup, keine Reservierung oder Mail. Bestehende CAL-D/T-
Regeln und ADR0007 gelten. Quellcode/Docs nach grünen Tests committen/pushen.

## Ausführung und Horizont

1. DONE A: native Intervallüberschneidung, begrenzte Monatsabfrage,
   öffentliche Projektion/Revisionen, vorhandene SQL-Indizes; echter isolierter
   PostgreSQL-Speicher- und Wiederabfragenachweis. Keine bestehende DB verwenden.
2. DONE B: bestehende Coach-/Reviewer-Oberfläche verbessern; Status/Fristen,
   Bearbeitung/Überschneidungen, Schutz ungespeicherter Eingaben. Kein Parallelportal.
3. DONE C lokal: öffentlicher ICS-Snapshot mit stabiler UID, revisionsgebundener
   Aktualisierungssemantik und standardsicherer Serialisierung. Keine Einladung
   oder Graph-/E-Mail-Verbindung; tatsächlichen Outlook-Clienttest separat nennen.
4. DONE D: Anfrageentwurf aus öffentlichen Termindaten, ohne Kundenspeicherung
   oder Netzwerk-Schreibaktion. Echte Empfänger/Zustellung nicht erfinden.
5. DONE E: gemeinsamer echter SQL-/API-/Browserlauf einschließlich Neustart,
   Revision/Rücknahme/Konkurrenz,390px/native200%, Datensparsamkeit und Cleanup.
6. DONE F lokal: präzise Pilotmatrix, Demoablauf, Git/Tests und verbleibende Gates;
   keine Architekturstudie und keine automatische Betriebsfreigabe.

## Evidence

Docker Desktop war zunächst nicht gestartet. Bekannte lokale Installation
gestartet; Engine29.4.3 erreichbar. Kein Server-/Staging-Eingriff.
Native46 SQL-/Browserchecks und3 zusätzliche echte PostgreSQL-API-Tests PASS.
PostgreSQL16.15 aus vorhandenem `postgres:16-bookworm`; tatsächlicher Anwendungs-
UND Datenbankneustart mit eigenem persistentem Docker-Volume. Session, Revision,
alte Freigabe und ICS danach neu gelesen. Eigenen Container, Volume und Test-
Kontext entfernt; Nullrückstand verifiziert. Kein Staging-/Serverzugriff.
83 fokussierte Verträge PASS; finale ergänzende72 nach dem zusätzlichen UTC-
Herbststundenfall grün. Gesamte lokale Regression1451 PASS/30 erwartete Opt-in-
Skips,237 weitere Browserchecks samt Reviewer-Mobil/Zoom,26 Renderer-JS-/34
Website-Verträge, Astro82 ohne Diagnose und `pip check` grün. Alle52 normalen
Productiondateien bytegleich; Production-/Preview-Link- und Isolationschecks grün.
Quelle/Docs dürfen gemäß Auftrag committed/gepusht werden; kein Deployment.

[Praktischer Start, Vorführung, Statusmatrix und offene Gates](../../handoffs/2026-11-06-cal1-pilot-readiness.md).
Fachliche Janay- und konkrete Outlook-Desktop-Abnahme bleiben offen; keine
Graph-/Einladungs-/Betriebsaktivierung aus dem lokalen Nachweis ableiten.
