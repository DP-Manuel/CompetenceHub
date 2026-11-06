# CAL-1: lokale synthetische Kalender-Demo

Neuester Ausbau06.11: [native PostgreSQL-Pilotvariante, ICS/Anfrage und aktuelle
Gates](2026-11-06-cal1-pilot-readiness.md). Der Integrationsstand und die später
genannten offenen SQL-Gates unten sind der erhaltene frühere Zwischenstand;
native SQL-Prüfung inzwischen lokal erfolgt, nicht auf bestehendem Staging.

Stand: 05.11.2026. Ziel: fachliche Vorführung für Janay ab Woche 16.11.2026.
Eigenständiger lokaler Block neben COACH-5; kein Deployment, kein realer Betrieb.

**Aktuell 06.11: lokale CAL-1/CAL-0.1-Integration ausführbar.** Der unten
dokumentierte ursprüngliche getrennte Stand ist durch den
[Integrationsabschluss](#gemeinsame-lokale-kalenderdemo-06112026) ergänzt.

06.11: Manuel bestätigt den vollständigen Coach-/Reviewer-/Freigabeablauf als
erfolgreich manuell geprüft. Vorheriger Darstellungsfix, vor dem Integrationsblock:
[Mehrtägige Veranstaltungen](#mehrtägige-veranstaltungen-06112026).

## Gemeinsame lokale Kalenderdemo 06.11.2026

- Derselbe Startbefehl baut jetzt zusätzlich genau eine lokale Astro-Seite aus
  dem vorhandenen `CalendarPrototype.astro`. Voraussetzungen: vorhandene
  Website-`node_modules` und mitgeliefertes Node, keine Installation oder Secrets.
- `https://127.0.0.1:8446/demo/public/` ist die lokale öffentliche CAL-0.1-Sicht;
  `/demo/` bleibt die CAL-1-Demo mit Testzugängen. Beide verwenden exakt
  `calendar.js`, `calendar-month.mjs` und `calendar-month.css`.
- Öffentliche Daten stammen ausschließlich aus der letzten freigegebenen
  Revision desselben In-Memory-Bestands. Der vorhandene Public-DTO-Serializer
  wird wiederverwendet. Kein Zugriff auf persönliche Verfügbarkeit, Reviewer-
  Notizen, Schwelle, Benutzer-/Coach-IDs, geschützte Zusammenfassungen oder Rollen.
- Der lokale GET-Adapter `/demo/api/public-calendar?month=YYYY-MM` akzeptiert
  nur aktuellen Berliner Monat plus drei Folgemonate, signierte Cursor und
  maximal 100 Datensätze pro Seite. Überlappung: `start < windowEnd` und
  `end > windowStart`, also `[start,end)`. Auch zuvor begonnene Veranstaltungen
  erscheinen; Ende exakt Monatsbeginn bleibt ausgeschlossen. Ein Datensatz,
  mehrere Darstellungssegmente, keine zusätzlichen Veranstaltungen.
- Beide Ansichten lesen anonym, ohne Session-Cookie und ohne Web Storage.
  Sichtbare Tabs aktualisieren alle fünf Sekunden und beim Wiederanzeigen.
  Unveränderte Daten lösen kein Rendering aus; Änderungen erhalten Fokus und
  Anfrageeingabe, Rücknahmen entfernen Details. Ausfälle zeigen keinen
  scheinbar aktuellen Altbestand. Anfragen bleiben reine lokale Simulation.
- Der native API-/SQL-Vertrag, Planungshorizont für Schreibzugriffe, RBAC,
  Revisionen und Auth bleiben unverändert. Der lokale Monatsadapter ist keine
  bereits ausgelieferte Korrektur des nativen PostgreSQL-Abfragewegs. Vor echtem
  Betrieb muss dieser überlappungsfähige Lesevertrag dort eigens übernommen
  und mit realer Persistenz geprüft werden.
- Separater Astro-Source-Root und `.tmp/cal1-public` verhindern Entdeckung durch
  normale Production-/Preview-Builds. Kein Portal-/API-Endpoint oder Testzugang
  im Pages-Artefakt, kein Pages-Aufruf zur lokalen Demo, kein Deployment.

**Verifikation:** 50 fokussierte Python-Verträge, 26 Kalender-JS-Tests, 34
Website-Verträge; Astro 82 Dateien ohne Diagnose. Production 1237 und Preview
1407 interne Referenzen geprüft. Gesamte lokale Backend-pytest-Suite ebenfalls
erfolgreich, externe Opt-in-Gates übersprungen. Tatsächliche Browserabnahme: 229 Checks PASS,
Desktop,390px, native200%, Tastatur/Fokus/Reduced Motion, Rollen/CSRF/stale409,
Freigabe ohne Reload, private Revision, Rücknahme, Kalendergrenzen und DST.
Native-Zoom-Screenshots zusätzlich pixelgeprüft und visuell angesehen; ein
falscher CDP-Zuschnitt wurde vor Abschluss korrigiert, nicht als QA akzeptiert.
Die echte Monatsüberlappung wurde mit der tatsächlichen lokalen HTTP-Abfrage
in beiden Ansichten geprüft; weitere Grenzfallprojektionen sind ausdrücklich
Darstellungstests mit eingespeisten Antworten. Kein vollständiger NVDA-Test.

Bereinigte lokale Belege (nicht versioniert):
`release-artifacts/cal1-cal01-integration-20261106/browser-report.json`,
`cal01-desktop-multiday.png`, `cal01-mobile-390-public.png`,
`cal01-native-200-multiday.png`. Browser/Server/temporäre TLS- und Zoomprofile
wurden vollständig beendet/entfernt. Der lokale Demo-Build lässt das vorhandene
52-Dateien-Productionverzeichnis unverändert. Separater normaler Neubuild:
50 Dateien bytegleich zum Sprintbeginn, zwei Kalender-HTMLs nur in
Whitespace/Boolean-Attributschreibweise abweichend; normalisierte Markups gleich,
CSS/JS-Bytes unverändert. Nicht als52 bytegleiche Vor-Sprint-Dateien ausgeben.

**Simulation bleibt:** Auth/MFA-Fixture, flüchtige Persistenz, keine echten
Accounts, Kundendaten, freien Platzzahlen, E-Mails, Reservierungen oder Zahlungen.
IONOS bleibt auf `1b4e33efa5e1`, Pages auf `78c3470`; kein VPS-/GPG-/Backup-Block.

**Bis echt:** native überlappungsfähige Monatsabfrage mit PostgreSQL-Nachweis,
separat freigegebene sichere Backend-Betriebsbereitschaft, persönliche Konten
mit MFA und expliziten Coach-/Reviewer-Zuordnungen, reale Inhalts-/Datenschutz-
und Veröffentlichungsgates. CAL-2-Vormerkungen, Mail/Schwellenmeldungen und
Kalendereinladungen sind eigene spätere Inkremente, keine Demo-Zusagen.

**Genau nächster Block:** Janays fachliche Demoabnahme. Inputs: diese startbare
Demo und sechs Schritte unten. Deliverable: priorisierte Bedienungsbefunde,
keine erneute Entscheidung bereits akzeptierter CAL-D/T-Regeln. DoD: Janay kann
Freigabe, Mehrtagesanzeige, Rücknahme und unverbindliche Anfrage nachvollziehen;
nur tatsächlich geprüfte Punkte abhaken. Kein automatisches Betriebsgate.

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

**Ursprüngliche Grenze 05.11, am 06.11 für den lokalen Integrationsblock ersetzt:**
CAL-0.1 war zunächst nicht die Laufzeitansicht dieser Demo.
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

1. **Coach:** Zuerst `https://127.0.0.1:8446/demo/public/` in einem Browser-Tab
   offen lassen. Im zweiten Browser-Tab über „Coach / Reviewer“ als
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
6. **Öffentliche Sicht:** Zum bereits geöffneten Kalender-Tab wechseln; nach
   Freigabe erscheint der Workshop automatisch binnen etwa fünf Sekunden.
   Ggf. Monat wählen, Details,
   Kapazität und fiktives Coachprofil ansehen. „Anfrage
   simulieren“ mit zwei Plätzen zeigt ausdrücklich: nichts gesendet/reserviert.

Der Rollenwechsel erfordert bewusst Abmelden, keine Rollenumschaltung mit
ungeprüften Rechten. Namen wie Janay stehen nicht in der Autorisierungslogik.

Für die Mehrtagesvorführung bei Schritt 2 das Ende auf den Folgetag setzen.
Alle Tagessegmente öffnen dasselbe Angebot. Eine Rücknahme nach Schritt 6
entfernt den Termin automatisch; eine noch ungeprüfte Ersatzrevision ändert
die letzte veröffentlichte Fassung nicht.

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

## Mehrtägige Veranstaltungen 06.11.2026

Geprüfter Implementierungscommit: `84f8e78`. Nur lokale Demo-/Testskripte und
komponentenbezogene Assets, kein Backend-Kern oder Website-Artefakt geändert.

**Befund reproduziert:**28.11.2026 17:18 MEZ bis29.11.2026 17:18 MEZ erschien
nur am28.11. Ursache: Tages- und Monatsfilter prüften allein `starts_at`.
Die Darstellung beachtet nun das vollständige halboffene Intervall `[Beginn, Ende)`.
Der letzte belegte Berliner Kalendertag stammt aus `Ende minus1Millisekunde`;
keine Addition fester24-Stunden-Schritte über eine Zeitumstellung.

- Durchgängige türkisfarbene Tagessegmente mit stabiler Spur je Veranstaltung
  und Kalenderwoche. Gleiche Spuren teilen ihre Zeilenhöhe; parallele Buttons
  überschneiden sich nicht. Am Wochen-/Monatsrand wird das Band sinnvoll umgebrochen.
- Beginn mit Uhrzeit, Fortsetzung und Ende mit Uhrzeit sind sichtbar benannt.
  Titel und Thema bleiben an jedem Segment lesbar. Ende00:00 erscheint nicht am
  nächsten Tag; die Beschriftung sagt nötigenfalls „Folgetag“.
- Alle Segmente verwenden dasselbe Originalobjekt und öffnen dieselbe Detailregion.
  Keine zusätzlichen Termine/Revisionen, kein Schreibpfad durch die Visualisierung.
- Mobil und bei200% wird dieselbe Datensicht als Tagesagenda dargestellt;
  native Buttons, Fokus, `aria-controls`, vollständige zugängliche Namen mit
  Tagesdatum/Phase/Gesamtzeitraum. Bei wechselndem Offset unterscheiden MEZ/MESZ
  auch die im Herbst doppelt vorkommende Uhrzeit.
- `calendar-month.mjs` trennt reine Intervall-/Spurlogik und `renderMonth`
  von Fetch, Auth, Detailformular und Speicherung. `calendar-month.css` ist
  komponentenbezogen. Diese Module können nach einem expliziten CAL-0.1-Read-
  Adapter dieselbe Darstellung liefern; keine solche Anbindung jetzt aktiviert.
  Der minimale View-Vertrag benötigt `id`, `title`, `starts_at`, `ends_at` und
  `topic.name`; Monat, Detail-Callback und Zielregion werden übergeben. CAL-0.1
  muss dafür konkrete Start-/Endinstants liefern, keine Endzeit aus unbekanntem
  Freitext raten. Gemeinsamer Asset-Ort/Adapter gehört erst zum Anschlussblock.
- Der Demo-Assetpfad liefert `.mjs` ausdrücklich mit JavaScript-MIME aus:
  Die Windows-MIME-Registry lieferte zunächst `text/plain`, wodurch das Modul
  nicht startete. Zusätzlicher HTTP-Vertragstest und Browser-Initialisierungs-
  assertion verhindern eine scheinbar erfolgreiche leere Oberfläche.

**Aktuelle Nachweise:**26 Node-Regressionstests PASS; derselbe Satz auch mit
Prozesszeitzone America/Los_Angeles und Pacific/Kiritimati PASS.38 fokussierte
Python-Service-/API-/Demo-Tests PASS, davon ein neuer MIME-Vertrag.134 tatsächliche
Browserchecks PASS, Chromium149.0.7827.55, Desktop1440,390px und echter nativer200%-Zoom.
Konkreter28./29.11.-Fall, ein-/mehrtägig, Ende00:00, Wochen-/Monats-/Jahreswechsel,
Frühjahrs-/Herbstumstellung bei fremder Browserzeitzone, parallele Spuren,
gleiche Details, Fokus, Text-Range-Geometrie und unveränderter Freigabeworkflow
sind geprüft. ARIA-/Tastaturprüfung, keine behauptete NVDA-Sprachausgabe-Abnahme.
Alle eigenen Testserver/Profile/TLS-Verzeichnisse beendet/entfernt;52 lokale
Produktionsdateien vor/nach dem Lauf bytegleich. Kein Websitebuild/Deployment nötig.

Belege (ignoriert): `release-artifacts/cal1-multiday-20261106/browser-report.json`,
`before-desktop.png`, `desktop-multiday.png`, `mobile-390-multiday.png`,
`native-200-multiday.png`. Datums-/DST-Frontendtests injizieren ausdrücklich nur
synthetische Read-Antworten; sie behaupten keine erweiterten API-Leserechte.

**Grenze bleibt bestehen:** Die CAL-1-Liste liefert Starts innerhalb ihres
zukünftigen Abfragefensters (`from >= now`). Bereits davor begonnene laufende
Veranstaltungen können nach einem Reload deshalb fehlen. Dieser Fix verteilt
die tatsächlich gelieferten freigegebenen Datensätze korrekt, erweitert aber
bewusst weder API noch Abfrageberechtigung. Vor echter Kalendernutzung muss
diese bereits vorhandene Read-Vertragsfrage separat geprüft werden.

**Neustart:** Ein bereits laufendes Demo-Terminal mit `Strg+C` beenden, danach
denselben oben dokumentierten Ein-Terminal-Befehl starten und im Browser
`Strg+F5` drücken. Dadurch wird auch die neue statische Modulroute registriert.
Nur der flüchtige synthetische Demostand wird zurückgesetzt; echte Daten und
Benutzer existieren hier nicht. Keine persönlichen Passwörter erforderlich.

Gezielte Prüfbefehle aus dem Repository-Root, PowerShell:

```powershell
& .\tools\node-v22.16.0-win-x64\node.exe --test apps/webapp/scripts/test-calendar-month.mjs
```

Die oben dokumentierten Python-Prüfungen bleiben gültig; Browserbelege liegen
jetzt im06.11.-Ordner. API/DTOs, RBAC, Review/Revision und Schema bleiben unverändert.
Keine GPG-/Backup-/VPS-/IONOS-/Pages-Aktion, keine echten Konten oder DB-Änderung.
