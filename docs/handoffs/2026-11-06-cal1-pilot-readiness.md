# CAL-1: lokale Pilot-Readiness

Stand06.11.2026. Baut auf `d563e76` auf. Janays Vorführung ab Woche16.11 bleibt
ein eigenes fachliches Gate, kein Grund, die freigegebenen lokalen A–E-Arbeiten
anzuhalten. Keine echte Staging-/Produktionsänderung.

## Was jetzt funktioniert

- Reale PostgreSQL16.15-Tabellen, native Auth/MFA/Sessions und CalendarService;
  keine Ersatz-Portalarchitektur oder In-Memory-Veranstaltungsspeicherung im
  nativen Modus. Vorhandene Migrationen0001–0006 nur im eigenen lokalen Container.
- Öffentliche Monatsabfrage mit echter Intervallüberschneidung, Berlin-Monaten,
  begrenztem Planungshorizont und signierten Cursorseiten. Vor Monatsbeginn
  gestartete Ereignisse, exklusives Mitternachtsende, Jahreswechsel und DST
  wurden tatsächlich mit PostgreSQL ausgeführt.
- Coachliste chronologisch, Suche/Statusfilter, Kapazität und Fristen; Reviewer-
  Notizen, neue Revision und Rücknahme nach bestehendem Vertrag. Schutz vor
  ungespeichertem Verlassen und verständliche Zeit-/Versionskonflikte.
- Freigabe wird automatisch in derselben lokalen CAL-0.1-Sicht sichtbar.
  Mehrtagesrenderer und öffentliche Feldprojektion sind gemeinsam, nicht kopiert.
- Öffentlicher ICS-Snapshot mit stabiler UID, VTIMEZONE, exklusivem Ende und
  freigabegebundener SEQUENCE/Zeitstempel. Private Ersatzrevision ändert keine
  Exportbytes; erneute Freigabe aktualisiert dieselbe UID; Rücknahme ergibt404.
- Anfrageentwurf mit Titel, Thema, Coach, Zeitraum, Format, Ort und Platzanzahl.
  Kein Kundenformular, keine Speicherung oder Mail. Text kann bewusst kopiert
  werden; aktualisierte Termine verwerfen einen veralteten Entwurf.

## Genau ein Terminal: native Demo starten

Voraussetzungen: Docker Desktop mit Linux-Engine, vorhandene Projekt-`.venv`,
Website-`node_modules` und mitgeliefertes Node. Keine neue Installation durch
den Runner und kein fremdes Datenbankziel. Ein belegter Port55433 wird nicht
wiederverwendet. Alte eigene Demofenster vor erneutem Start mit `Strg+C` beenden.

**Terminal A: PowerShell, Arbeitsverzeichnis beliebig.** Keine persönlichen
Passwörter oder echten Personen-/Kundendaten eingeben.

```powershell
& 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp\.venv\Scripts\python.exe' 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp\scripts\run-cal1-pilot.py'
```

Erwartet: `LOCAL_POSTGRES_DEMO: https://127.0.0.1:8447/demo/public/`.
Fenster offen lassen. Kurzlebiges selbstsigniertes TLS nur für genau diese
Loopback-Adresse akzeptieren, keine globale Browser-/TLS-Ausnahme. Testzugänge
unter `/demo/#zugang`: ausschließlich synthetische Konten. Native MFA einmalig
mit einer Authenticator-App einrichten; **123456 gilt hier nicht**. Keine realen
Admin- oder Coachkonten entstehen. Für die bereits vertraute reibungsarme
Janay-Vorführung bleibt `run-cal1-demo.py` auf8446 mit simuliertem MFA nutzbar.
Beide Modi nutzen dieselbe Kalenderlogik, nicht zwei Kalenderimplementierungen.

Beenden mit `Strg+C`: synthetische Datensätze bereinigen, eigenen Container und
eigenes Docker-Volume entfernen; keine fremden Container/Volumes oder Dateien.
`LOCAL_CAL1=STOPPED` bestätigt dabei nur das Demoende mit Cleanup, keine Abnahme.
Diese Testumgebung ist absichtlich nicht die dauerhafte Pilotdatenbank. Ein
Anwendungs- und PostgreSQL-Neustart innerhalb der Abnahme wurde mit erhaltenem
eigenem Volume geprüft; das Beenden des gesamten Runners verwirft die Vorführung.

## Automatischer gesamter Nachweis

Statt interaktiver Demo im selben Terminal nur diesen Befehl verwenden:

```powershell
& 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp\.venv\Scripts\python.exe' 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp\scripts\run-cal1-pilot.py' --acceptance
```

Erwartet nach Browser-/SQL-/API-Prüfungen:
`LOCAL_CAL1=PASS POSTGRES_REMOVED=PASS ZERO_RESIDUE=PASS TEMP_CLEANUP=PASS`.
Vorhandener expliziter Chromium149 wird verwendet, kein Download oder persönliches
Browserprofil. Testpasswörter/MFA/Recovery bleiben ausschließlich im Prozess;
Report enthält nur bereinigte Status-/Geometriedaten, keine Zugangswerte.

## Vorführung in sechs Schritten

1. Öffentlichen lokalen Kalender in einem Browser-Tab offen lassen; im zweiten
   Tab `/portal/` als synthetischer Coach anmelden und ggf. native MFA einrichten.
2. Entwurf mit „Demo-Werte einsetzen“ anlegen; Beginn/Ende über einen Monatswechsel
   wählen, Kapazität und interne Prüfschwelle prüfen. Speichern und einreichen.
3. Als synthetischer Reviewer nach Abmeldung oder in getrenntem Browserkontext
   öffnen; Details prüfen und mit Hinweis eine Änderung anfordern.
4. Als Coach Hinweis lesen, neue Revision bearbeiten und erneut einreichen.
   Unsaved-Abbruch zunächst ablehnen, dann bewusst speichern.
5. Als Reviewer veröffentlichen. Im offenen öffentlichen Kalender erscheint der
   Termin automatisch; dieselben Details über jedes Mehrtagessegment öffnen.
6. ICS herunterladen und unverbindlichen Anfrageentwurf erzeugen. Keine Buchung,
   kein Versand. Danach Rücknahme prüfen: Termine verschwinden, neuer ICS-Abruf404.

Ein Rollenwechsel weist keine Rechte zu; nur die vorhandenen synthetischen
Fixturekonten erhalten ihre fest definierten Testrollen. Janay ist nicht im Code
als Reviewer fest verdrahtet. Native Statusseite zeigt einen persistierten
aktuellen Stand, keine behauptete vollständige chronologische Auditoberfläche.

## Nachweise und offene Gates

| Bereich | Tatsächlicher Stand |
| --- | --- |
| Kalenderworkflow | Native PostgreSQL/Auth/API/Browser erfolgreich mit synthetischen Daten |
| Persistenz | Neue FastAPI-Anwendung/Engine UND PostgreSQL-Neustart, gleiches eigenes Volume; gespeicherte Session und Revision wiederabgefragt |
| SQL | Neun tatsächliche Intervall-/Monats-/Jahres-/DST-Fälle, vorhandener partieller Zeitindex im EXPLAIN genutzt; kein neuer Index erforderlich |
| Konkurrenz/RBAC | Stale-Edit abgewiesen; gleicher Coach überschneidet nicht; verschiedene Coaches dürfen parallel; fremder Coach erhält404 |
| Export/Anfrage | ICS-Download samt tatsächlichem Dateivergleich, Parser/Zeitzone/UID/SEQUENCE; Anfrage nur Text, keine Netzwerkschreibaktion |
| Mobil/Zoom | Native SQL-Sicht390px und echte200% (707CSS-px/DPR2), tatsächliche Textrechtecke und Screenshots |
| Outlook | RFC-/Struktur-/Zeitzonenvertrag geprüft, kein Graph; persönliches Outlook-Profil nicht angerührt, konkreter Desktop-Import/Reimport noch offen |
| Staging | Frühere Basisnachweise bleiben historisch gültig; dieses neue Inkrement NICHT auf bestehendem Staging abgenommen |
| Fachlich | CAL-D/T und ADR0007 unverändert; neue Bedienung noch nicht von Janay vorgeführt/abgenommen |
| Produktiv | Nicht aktiviert, keine Website-/VPS-/Rollen-/Datenänderung |

Native Belege: `release-artifacts/cal1-pilot-20261106/report.json` mit46 erfolgreichen
SQL-/Browserchecks und3 zusätzlich echten PostgreSQL-API-Integrationstests.
SQL-Plan verwendete u.a. `calendar_offer_revisions_public_time_idx`; gemessene
Laufzeit ist ausschließlich Fixture-Evidenz, kein Produktions-Lastversprechen.
`desktop-public.png`, `mobile390-public.png`, `mobile390-edit.png`,
`native200-public.png` bleiben lokale, nicht versionierte synthetische Belege.
Weitere UI-Regression:237 tatsächliche Browserchecks PASS, einschließlich
Reviewer-Notizen/Unsaved-Schutz bei390px und echter200%-Vergrößerung; kein
vollständiger Screenreader-Produkttest. Gesamte lokale Suite:1451 PASS/30
erwartete externe Opt-in-Skips, einmaliger Gesamtlauf. Nach zusätzlicher Prüfung
der wiederholten Herbststunde ergänzende72 fokussierte Verträge PASS; der
UTC-Export erhält beide tatsächlich verschiedenen Zeitpunkte. Nicht als1452
erneut ausgeführte Gesamttests ausgeben.83 fokussierte Verträge waren zuvor grün.
26 Renderer-JS-/34 Website-Verträge, Astro82 ohne Diagnose und `pip check` grün.
Production1237/Preview1407 Links geprüft. Alle52 normalen Productiondateien
bytegleich zum Beginn dieses Pilot-Inkrements; normale Production-/Pages-Builds
enthalten weder lokale Endpoints noch Testzugänge oder Demo-Laufzeitlinks.
Kein Pages-/IONOS-/VPS-Deployment; alter öffentlicher Stand bleibt unberührt.

Bis echt fehlen: separat freigegebene Staging-Bereitstellung und dortige Abnahme
dieses Quellstands/der neuen Runtime-Abhängigkeiten, dauerhaft freigegebene
Betriebs-/Schlüssel-/Recovery-Konfiguration ohne hier einen Backupblock zu starten,
persönliche Konten/MFA und explizite Coach-/Reviewerzuordnungen, freigegebene reale
Inhalte sowie Janays Bedienungsabnahme. Öffentliche API-/Website-Anbindung und
Release einschließlich Abuse-/Lastschutz für Monats-/ICS-Abfragen bleiben eigene
Gates. Reservierungen, Mail/Schwellenmeldungen, echte
Einladungen/Absagen und Outlook-Synchronisation sind eigene spätere Inkremente.

**Genau nächster Block:** kleines CAL-1-Staging-Abnahmepaket. Inputs: geprüfter
Commit, diese native Evidenz und bestehende Betriebsverträge. Deliverable:
abgegrenzter Prüf-/Rückfallablauf mit Abhängigkeiten, keine Serveraktion.
DoD: technische Freigabegrenzen, neue Runtime-Abhängigkeiten und benötigte
Operatorinputs sind eindeutig; Ausführung erst nach separater konkreter Freigabe.
