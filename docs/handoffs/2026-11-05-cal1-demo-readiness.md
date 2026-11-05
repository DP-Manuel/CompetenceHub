# CAL-1: lokale synthetische Kalender-Demo

Stand: 05.11.2026. Ziel: fachliche Vorführung für Janay ab Woche 16.11.2026.
Eigenständiger lokaler Block neben COACH-5; kein Deployment, kein realer Betrieb.

## Wiederverwendung und bewusste Adaptergrenze

Unverändert wiederverwendet werden das tatsächliche Portal aus
`apps/webapp/src/competence_hub_api/portal_ui`, `CalendarService`, die öffentlichen
und geschützten CAL-1-Router, Rollenprüfung, Origin/CSRF, ETags, Formvalidierung,
Entwurfs-/Review-/Revisionsaktionen sowie die bestehenden synthetischen Login-
und Session-Fixtures. `native_calendar_fixture.py` wurde geprüft, aber bewusst
nicht gestartet: Die native Fixture benötigt PostgreSQL, diese Demo nicht.

Grundlage bleiben [ADR 0007](../decisions/0007-calendar-and-reservation-increments.md),
[CAL-D01 bis D08](../requirements/calendar-stakeholder-decisions-2026-09-11.md),
[CAL-T01 bis T06](../requirements/calendar-cal1-migration-decisions-2026-09-11.md),
[API](../architecture/calendar-cal1-api-contract-v0.1.md),
[Portal-UI](../architecture/calendar-cal1-portal-ui-contract-v0.1.md) und
[RBAC](../requirements/calendar-cal1-rbac-matrix-v0.1.md). Bereits angenommene
Fachregeln werden nicht erneut zur Entscheidung gestellt.

**CAL-0.1 bleibt unverändert, ist aber nicht die Laufzeitansicht dieser Demo.**
`CalendarPrototype.astro` koppelt seinen Renderer an sieben feste Beispielobjekte,
teilweise echte Coachlinks und erfundene Vormerkungszahlen mit lokaler Erhöhung.
Die CAL-1-Projektion liefert dagegen ausschließlich freigegebene Revisionen,
Kapazität, keinen freien Platzstand und hier nur fiktive Coachprofile. Eine
unveränderte Auslieferung des gebauten CAL-0.1 würde deshalb die falschen Termine
zeigen, keine tatsächliche Freigabe nachweisen und echte Personen mit der Demo
verbinden. Ein gemeinsamer Renderer-Umbau würde den produktiven Astro-Bundle-
Vertrag berühren und gehört nicht in diesen begrenzten Block.

Die ausdrücklich lokale Ergänzung ist deshalb eine kleine neue Leseansicht für
Monat, Themen-/Formatfilter und Details unter `/demo/`, keine behauptete
CAL-0.1-Integration. Sie liest den tatsächlichen anonymen CAL-1-Endpunkt derselben
In-Memory-App. Sie enthält keine zweite Freigabe-, Kapazitäts-, Revisions- oder
Berechtigungsentscheidung. Monatsseiten umfassen den aktuellen und bis zu drei
weitere Kalendermonate; nur die API-begrenzte rollierende Dreimonatsfrist liefert
Termine. Eine spätere gemeinsame View-Extraktion bleibt ein getrenntes Gate.

## Was ergänzt wurde

- Loopback-HTTPS-Runner, der keine DB-/Runtime-Konfiguration oder Secrets lädt.
- Demo-Banner auch beim direkten Portal-/Profilaufruf; Testzugänge sichtbar lokal.
- Schaltfläche „Demo-Werte einsetzen“ füllt nur das vorhandene Formular, ohne
  selbst ein Angebot anzulegen. Erstellen/Speichern nutzt weiter die Portal-API.
- Lokaler Read-Adapter: Monatsansicht, mehrere Angebote am selben Tag, Filter,
  Dauer aus Beginn/Ende, Details, fiktiver Profillink und Anfrage-Simulation.
- Flüchtiger, nach derselben Session und Angebotssichtbarkeit geschützter
  Statusverlauf. Er ersetzt weder persistente Revisionen noch produktives Audit.
- Demo-Repository erweitert die vorhandene Browser-Fixture um erhaltene letzte
  Veröffentlichung während einer neuen Revision, Topic-/Cursorfilter,
  Idempotenzkonflikte, Coach-Überschneidungsschutz und unveränderliche Rücknahmen.
  Diese Korrekturen betreffen nur die Demo-Fixture, nicht Backend-Kern oder SQL.

## Start: genau ein Terminal

**Terminal A: PowerShell, Arbeitsverzeichnis beliebig.** Voraussetzung: vorhandene
Projekt-`.venv` mit installierter Anwendung. Keine echten Zugangsdaten eingeben.

```powershell
& 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp\.venv\Scripts\python.exe' 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp\scripts\run-cal1-demo.py'
```

Erwartet: `SYNTHETIC LOCAL DEMO: https://127.0.0.1:8446/demo/`. Fenster offen
lassen und die Adresse im Browser öffnen. Das kurzlebige, selbstsignierte
Loopback-TLS-Zertifikat verursacht im normalen Browser einen Zertifikatshinweis;
die Ausnahme ausschließlich für diese lokale `127.0.0.1:8446`-Demo zulassen,
keine globale Zertifikats-/Browser-Sicherheit abschalten. Kein zweites Terminal,
Tunnel, USB-Stick, persönliches Passwort oder GPG nötig. Bei belegtem Port
abbrechen, vorhandenen Dienst nicht stoppen; der Runner unterstützt `--port`.

Beenden: `Strg+C` in Terminal A. Eigene temporäre TLS-Dateien werden entfernt;
In-Memory-Zustand entfällt. Ein neuer Start beginnt wieder mit fünf synthetischen
Ausgangsangeboten, davon zwei öffentliche, gleichzeitig stattfindende Gruppen-
angebote unterschiedlicher Demo-Coaches. Niemals echte Personen/Kundendaten
eingeben. Keine Anwendungs- oder GPG-Schlüssel werden erzeugt oder verändert.

## Sechs Schritte für Janay

1. **Coach:** Über „Coach / Reviewer“ als
   `synthetic.coach@example.invalid` anmelden. Demo-Passwort
   `Synthetic-Portal-2026!`, synthetischer MFA-Code `123456`.
2. **Entwurf:** „Neuer Entwurf“ öffnen, „Demo-Werte
   einsetzen“, Datum/Ende, Format, Ort, Kapazität 12 und interne Prüfschwelle 6
   ansehen; „Entwurf anlegen“, dann „Zur Prüfung einreichen“. Noch nicht öffentlich.
3. **Prüfung:** Abmelden und als `synthetic.reviewer@example.invalid` mit
   denselben Demo-Werten anmelden. Das Teamworkshop-Angebot prüfen und mit
   Hinweis „Demo-Ort genauer beschreiben“ Änderungen anfordern.
4. **Revision:** Abmelden, wieder Coach A; „Neue Revision bearbeiten“, Ort
   konkretisieren, speichern und erneut einreichen. Revision 2 und Status prüfen.
5. **Freigabe:** Wieder als Reviewer anmelden, dasselbe Angebot prüfen und
   veröffentlichen. „Statusverlauf“ zeigt die tatsächlich ausgeführten Schritte.
6. **Öffentliche Sicht:** „Demo-Kalender“ öffnen/aktualisieren, ggf. Monat wählen,
   Workshop, Details, Kapazität und fiktives Coachprofil ansehen. „Anfrage
   simulieren“ mit zwei Plätzen zeigt ausdrücklich: nichts gesendet/reserviert.

Der Rollenwechsel erfordert bewusst Abmelden, keine Rollenumschaltung mit
ungeprüften Rechten. Namen wie Janay stehen nicht in der Autorisierungslogik.

## Echt ausführbar versus simuliert

| Teil | Tatsächliche Demo-Grenze |
| --- | --- |
| Portal-Formulare und Workflow | Echter vorhandener Client, Domain-Service und API, aber flüchtige synthetische Repository-Daten |
| Anmeldung/MFA/Recovery | Bestehende synthetische Fixture, feste Testwerte; kein neuer kryptographischer oder nativer Auth-Nachweis |
| Reviewer | Tatsächliche Rollen-/Scopeprüfung für `calendar_reviewer`, keine reale Rolle zugewiesen |
| Veröffentlichung | Echter API-Übergang und anonym gelesene freigegebene Projektion innerhalb des lokalen Prozesses |
| Öffentliche Website | Nicht angebunden: weder Pages noch IONOS lesen diesen lokalen Prozess |
| Coachprofile | Nur zwei explizite fiktive lokale Routen, keine Zuordnung realer Coaches |
| Plätze | Kapazität, nicht freier Bestand. Prüfschwelle intern, keine verbindliche Mindestgruppe/Buchung daraus abgeleitet |
| Anfrage | Nur sichtbare Browserbestätigung, kein Request-Schreibzugriff, Mail, Reservierung oder Speicherzustand |
| Verlauf | Flüchtige Präsentationshilfe mit Zugriffskontrolle, kein persistentes Audit |
| Angebotsfinder | Kein Link zu erfundenen Realterminen. Bestehende echte Coach-/Anfragewege bleiben unabhängig |

## Prüfung und Nachweise

Fokussierter Aufruf im Verzeichnis `apps/webapp`:

```powershell
& .\.venv\Scripts\python.exe -m pytest scripts/test_cal1_demo.py tests/test_calendar_service.py tests/test_calendar_api.py
& .\.venv\Scripts\python.exe scripts/run-cal1-demo-acceptance.py --browser chromium --browser-executable "$env:LOCALAPPDATA/ms-playwright/chromium-1228/chrome-win64/chrome.exe"
```

37 fokussierte Tests PASS: 11 neue Demo-Verträge und 26 bestehende Service-/API-
Prüfungen. Letzter vollständiger Browserlauf: **76 Checks PASS**, Chromium
`149.0.7827.55`, Exitcode 0, `SERVER_STOPPED=PASS`, `TEMP_CLEANUP=PASS` und alle
52 Produktionsdateien unverändert. Das explizit benannte vorhandene Chromium
wurde ohne Download/Installation verwendet; die aktuell installierte Playwright-
Version erwartet sonst einen hier noch nicht vorhandenen neueren Chromium-Build.
Die eigene Browserabnahme prüft den vollständigen
Erstellen-/Änderungs-/Revision-/Freigabe-/Leseablauf, tatsächlichen `409` bei
staler Bearbeitung, keine Self-Publication, fremde Coachdaten nicht sichtbar,
Reviewer ohne Coach-Schreibrecht und Internal ohne Prüfrecht. Öffentliche DTOs
enthalten keine Prüfschwelle, Reviewer-Notizen, Drafts oder privaten IDs. Eine
veröffentlichte Fassung bleibt während ihrer neuen privaten Revision unverändert;
Rücknahme entfernt sie sofort aus der öffentlichen API.

Desktop 1440 px, Smartphone 390 px, tatsächlicher nativer Chromium-Zoom 200 Prozent
(707 CSS-px, DPR 2, kein CSS-Zoom), Tastatur/Fokus/Escape/erreichbare Formularaktion,
Reduced Motion, Text-Range-Überlauf statt nur Containermaße und Loading-/Empty-/
Error-Recovery werden im Browser geprüft. Fehler und leere Antwort für einzelne
Zustandsprüfungen sind ausdrücklich injizierte Read-Antworten, keine behaupteten
nativen Ausfälle. Anfrage-Simulation erzeugt null Netzwerkschreibvorgänge.

Generierte lokale, nicht versionierte Belege:
`release-artifacts/cal1-demo-20261105/browser-report.json`, `desktop-public.png`,
`mobile-390-public.png`, `mobile-390-form.png`, `native-200-public.png` und
`native-200-form.png`. Der Abschlussreport gilt nur mit aktuellem `status=PASS`.
Der letzte grüne Lauf hat Test-Server, Browserprofile und eigenes temporäres
TLS-/QA-Verzeichnis nachweislich beendet/entfernt; danach kein CAL-Demo-QA-Runner
mehr aktiv. Ein früherer Edge-156-Lauf war ebenfalls vollständig grün; spätere
Edge-Nachläufe hingen beim Browserabschluss. Diese gelten nicht als bestanden.
Nur eigene, über Eltern-PIDs nachgewiesene Testprozesse wurden beendet, keine
persönlichen Browser oder die parallel laufende Finder-Abnahme.

Die Prozess-Umgebung `TEMP`/`TMP` wird ausschließlich während der QA auf einen
eigenen Projekt-Testordner verlegt und danach wiederhergestellt. Dessen ACL-
Metadaten zeigen normale Vererbung, fünf Regeln; keine globale ACL, Systemeinstellung
oder Dependency geändert. Trotzdem gab es beim abgebrochenen Edge-Lauf eine
gesperrte `Collections/collectionsSQLite`-Testdatei. [Playwright #42109](https://github.com/microsoft/playwright/issues/42109)
beschreibt eine mögliche Windows-Cleanup-Fehlerklasse, ist aber kein Beweis für
die Ursache dieses konkreten Datei-Locks. Native Zoom-Bitmaps werden über die
tatsächliche Browseroberfläche erfasst, ohne CSS-Zoom/Viewport-Manipulation.

**Ältere Testreste, nicht Teil des grünen Cleanup-Nachweises:**
`release-artifacts/cal1-demo-20261105/run-temp-fisyq46u` (gesperrtes Edge-Testprofil)
sowie die eigenen vorherigen `%TEMP%/competence-hub-cal1-browser-d9fvbzrv` und
`%TEMP%/competence-hub-cal1-browser-jj8nrgjo` (kurzlebige synthetische TLS-Fixtures).
Keine Anwendungs-/GPG-Schlüssel, DB-Dumps oder realen Zugangsdaten darin. Eine
angefragte manuelle Löschung des ersten alten TLS-Testverzeichnisses wurde vom
Tool blockiert und nicht über einen anderen Weg umgangen. Testreste erhalten;
keine pauschale Bereinigung/ACL-Änderung vorgenommen. Der letzte grüne Lauf hat
seine eigenen neu erzeugten Testverzeichnisse vollständig entfernt.

Production-Manifest: alle 52 Dateien vorher/nachher identisch; parallele Website-
Builds dürfen nicht in diese Messung fallen. Kein Website-Quelltext geändert.

## Feedback und spätere echte Nutzung

Janay prüft Verständlichkeit der Eingabebezeichnungen, Status, Änderungsnotiz,
öffentlichen Darstellung und der unverbindlichen Anfrage. Keine erneut offenen
CAL-D/T-Entscheidungen; insbesondere keine Umdeutung von Prüfschwelle zu Kapazität
oder verbindlicher Mindestteilnehmerzahl.

Vor echter Nutzung fehlen weiterhin gesonderte Aktivierung des abgesicherten
Portal-Betriebs, freigegebene persönliche Coach-/Reviewer-Konten und explizite
Mappings/Topics, echte geprüfte Termine/Profile, öffentliche Read-Anbindung und
Produktionsfreigabe. Persistenz-/Backup-/Restore-Gates gelten dann nach ihrem
Vertrag, sind aber keine Voraussetzung für diese lokale Demo. Firmenvormerkung,
Nachrichten, ICS/Outlook, Buchung und Zahlung werden hier nicht aktiviert.

## Übergabe und nächster Block

Der koordinierende Sprint hat die geprüfte lokale Implementierung getrennt als
`d6bf0f9` committet und mit dem Finder-Paket `50aed83`/Checkpoint `78c3470` gepusht. Keine Demo- oder
Backend-Veröffentlichung durch den Pages-Workflow: dort wird nur die statische
Website gebaut. Keine Server-/DB-/GPG-/Admin-/Coachimport-Aktion ausgeführt.

Der zusätzliche CLI-Aufruf im Werkzeug-PTY konnte keinen Prozess anlegen
(Windows-Zugriff auf die PTY-Shell verweigert); kein Umgehungsversuch. Der
tatsächliche Server/HTTPS/UI/API-Lauf ist durch die76 Browserchecks mit derselben
App belegt, nicht als PTY-Start ausgegeben. Der obige Ein-Terminal-Befehl ist
für Manuels normale lokale PowerShell vorgesehen; keine Passworteingabe nötig.

Genau ein empfohlener nächster CAL-1-Block: **gemeinsame lokale View-/Projektionsbrücke**.
Inputs: bestehendes CAL-0.1 und diese synthetische API-Demo. Deliverable: gemeinsam
nutzbare öffentliche Darstellung mit explizitem synthetischen Read-Adapter,
ohne doppelte Workflowlogik. Done: dieselbe fachliche Demo für Janay bleibt
ausführbar, CAL-0.1-Default und alle 52 Produktionsdateien byte-identisch,
keine realen Konten/Daten, Veröffentlichung oder Backend-Aktivierung erforderlich.

Wiederverwendbare Lernnotiz: Statische Beispielansicht und echte lokale
API-Veröffentlichung nie als dieselbe Integration ausgeben. Native Zoom-Bitmap-
Erfassung und DOM-Geometrie getrennt prüfen; parallelen Build nicht als
Produktionsregression einer unveränderten Demo-Quelle fehlklassifizieren.
