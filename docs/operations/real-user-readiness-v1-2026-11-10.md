# Persönliche Zugänge: Readiness V1

Stand: 10.11.2026. Owner: Manuel. Lokales synthetisches Update, keine echte
Benutzeraktivierung. Der zuvor abgenommene private VPS-Pilot bleibt Referenz.

## Umsetzung

- Adminliste: Aktivierung, MFA, letzte Anmeldung, offene/verbrauchte/widerrufene/
  abgelaufene Einladung, stabile Coach-UUID und gezielter Verwaltungsdialog.
- Fremde Konten sperren, deaktivieren, wieder freigeben oder genau eine Rolle
  zuweisen. Coach benötigt eine existierende, verfügbare und bestätigte UUID.
  Historische Coachidentitäten und Qualifikationen werden nicht verändert.
- Änderungen erfordern MFA-bestätigte Anmeldung innerhalb zehn Minuten,
  Same-Origin/CSRF, Ziel-UUID, aktuelle Kontoversion und ausdrückliche UI-Bestätigung.
  Eigener Adminzugang, letzter aktiver Admin und ausstehende Aktivierung geschützt.
- Rollenänderung/Sperre und Sitzungs-/Challenge-/Linkwiderruf sind atomar. Offene
  Zustellaufträge werden abgebrochen und ihre vertraulichen Nutzdaten entfernt.
  MFA-Abschluss und Kontozustand sind gegen gleichzeitige Änderungen gesperrt;
  Einladung prüft die aktuelle Adminberechtigung erneut innerhalb der Transaktion.
- Administrative Historie: höchstens20 minimale Einträge pro Ziel, keine Secrets.
  Die Liste ist kein vollständiges revisionssicheres Betriebsmonitoring.
- Einladung prüfen funktioniert ohne Zustellfreigabe und legt noch kein Konto an.
  Widerruf und erneute Vorbereitung nutzen die bestehende verschlüsselte Outbox;
  keine Aktivierungslinks oder Startpasswörter im Adminbereich.
- Rollenübersicht: eigene Status/nächster Termin, erneute Einreichungen, höchstens
  fünf zuletzt freigegebene Veranstaltungen, offene Aktivierungen/Coachzuordnungen.
- Rollentour startet nach erster MFA-Einrichtung, ist überspringbar und über Hilfe
  neu startbar. Sichtbarer Pfeil, Schrittzähler, Tastatur/Fokus und Fortsetzung nach
  Neuladen im selben Tab. Ausschließlich Rolle/Schritt/Status in Tab-History,
  keine Benutzerkennung, Web Storage, Cookies oder externe Nachverfolgung.
  Logout entfernt den Tourfortschritt; kein geräteübergreifender Fortschritt.

Keine Migration, neue Abhängigkeit, Registry-Aktivierung oder Änderung am
öffentlichen Kalendervertrag. Bestehende öffentliche Projektion bleibt getrennt.

## API-Delta

| Route | Zugriff / Ergebnis |
| --- | --- |
| `GET /api/v1/admin/users` | Bestehende begrenzte Liste, zusätzlich Kontoversion, MFA/Anmelde- und minimaler Einladungsstatus |
| `PATCH /api/v1/admin/users/{id}` | Frischer Admin, CSRF/Origin, `action`, `expected_version`, optional explizite `role`/`coach_id`;200 accepted |
| `GET /api/v1/admin/users/{id}/audit` | Admin, maximal20 minimale Einträge |
| `GET /api/v1/admin/coach-mappings` | Admin, maximal100 bestehende UUID-Kandidaten; keine automatische Zuordnung |
| `GET /api/v1/portal/pilot/overview` | Bestehender Rollenbereich; konsistenter Read-only-Snapshot, erneute Einreichungen und begrenzte Freigaben |

Aktionen: `suspend`, `deactivate`, `enable`, `set_role`, `revoke_invitation`.
Veraltete Version/gesperrte Zuordnung409, fehlende/frische Berechtigung403,
unbekanntes Ziel404, ungültige Eingabe400. Keine automatischen Wiederholungen.
`company_contact` liegt außerhalb dieser Verwaltung. Einladungen vergeben
weiterhin keine Adminrolle. Alle geschützten Antworten bleiben `no-store`.

## Zusammenhängendes Updatepaket

Das Paket enthält Runtime, Portal und gemeinsame Kalenderansicht, exakte Locks,
Manifest und SHA-256. Es ist ein Updatekandidat, **kein erneuter Installerlauf**.
Keine Website-/Pages-Veröffentlichung und kein Kopieren privater Konfiguration.
Gebundener Quellstand: `bc53775b08dc6693bc9cf4780e026f4fdf2d1744`, gepusht.
125 explizit erlaubte Git-Eingaben, keine privaten/unversionierten Dateien.

| Nachweis | Tatsächlicher Stand |
| --- | --- |
| Paket | `release-artifacts/webapp/competence-hub-webapp-0.1.0-bc53775b08dc-20261110T184433Z.zip` |
| Paket-SHA-256 | `21849d1e2f33b6044e6a93fdc27fb3ab39f5b5bd7bea047ba73fed99e8d5df97` |
| Anwendungswheel-SHA-256 | `30b211b07a45ae99154808deb46092b19ddcc1caab22364d58fc6ac4eb299dcf` |
| Wiederholte Releasegates |1.635 Tests bestanden/30 erwartete Skips,298,63 Sekunden; exakte Locks, `pip check`, Wheelinstallation/Imports/Fail-closed-Konfiguration bestanden |
| Linux | `release-artifacts/webapp-linux/20261110T184522Z-4efed9db`, frische Ubuntu/Python3.12-Installation,25 exakte Linux-Abhängigkeiten, hashgebundene Offlineinstallation |
| Linux/Proxy |37 tatsächliche Prüfungen bestanden, PostgreSQL/Auth/MFA/Cookies/CSRF/Origin/Logout/Loopback, Nullrückstand und eigener Container entfernt |
| Linux-Summary-SHA-256 | `c72c68f76d71d2ef3a899493edd1373c8c251cdb220f74a333fa45070b1135ca` |
| Proxyreport-SHA-256 | `ebbd1fff13a5312a2cdd14e630492da858e3cc433bd9b79c4dd97a16cf4e3530` |

Linuxnachweis ist kein VPS-Systemd-/Update-Nachweis. Das Archiv enthält bereits
vorher vorhandene Migrationsdateien; keine davon darf durch diesen Updateblock
angewendet werden. Native V1-Browserabnahme lief ausdrücklich auf0001–0006.
Das bisherige Paket0080195 bleibt unveränderte VPS-Referenz und möglicher
Code-Rollback, erst nach bestätigtem tatsächlichem Runtimezustand.

## Tatsächliche Lokale Abnahme

- Gesamtsuite:1.635 bestanden,30 erwartete Opt-in-/Umgebungsauslassungen,
  312,67 Sekunden. JUnit `.tmp/onboarding-v1-final-tests.xml`, SHA-256
  `dbfb747c392a61acdcd996ea6e2b1b0083b54ab47451259356b72fc2af0064bb`.
- 86 fokussierte Auth/Admin-Tests und35 Releasequellentests bestanden.
- Native PostgreSQL16/Chromium:136 Onboarding-/Verwaltungsprüfungen und46
  vollständige CAL-Prüfungen bestanden; danach3 native PostgreSQL-API-Tests grün.
  Report `release-artifacts/onboarding-v1-20261110/135925408c984baa87c4564b5ca16dac/report.json`,
  SHA-256 `26ca83a736bc335c67f2bd57a87a77cc77610c27189c312256fed323e69decb7`.
- Tatsächlich geprüft: Einladung/Passwort/MFA/Recovery, Widerruf und sichere
  Neuausstellung, Sperre/Sessionverlust/Rollenwechsel, fremde Coachzuordnung,
  veraltete Kontoversion, gezielt vertauschte Listenantworten, alle drei Touren,
  Tastatur, Reduced Motion,390px, echtes200%-Zoom einschließlich erreichbarer
  Dialogaktionen. Keine DOM-Box-only-Abnahme: tatsächliche Textranges geprüft.
- Kalender: Draft/Prüfung/Änderung/Revision/Freigabe, öffentlicher Snapshot,
  Mehrtag/Monatsgrenze/DST/Mitternacht, fremde Coaches, ICS/Anfrageentwurf,
  Rücknahme sowie echte lokale PostgreSQL-/Runtime-Neustartpersistenz bestanden.
- Erfolgreicher Abschluss: Nullrückstand, eigener Container/Volume und temporärer
  Kontext entfernt. Zwei früh abgebrochene Diagnoseverzeichnisse verbleiben
  ausgeschlossen unter den beiden Läufen `74d4bf0…`/`7735f9b…`: gezielte lokale
  Entfernung wurde durch die Ausführungsrichtlinie abgelehnt. Keine laufenden
  zugehörigen Fixtures oder echten Daten; nicht in Git/Release übernehmen.
- Browserbilder lokal visuell geprüft; native Zoom-Bilder über die vorhandene
  CDP-Oberflächenaufnahme statt abgeschnittener CSS-Clips. JavaScript-Syntax,
  `pip check`, Diff und Kontext-Router geprüft.

Die früheren fehlerhaften/abgebrochenen Läufe sind keine Abnahme. Gefunden und
korrigiert: Fokusausbruch im Verwaltungsdialog sowie doppelte Listenbefüllung
durch überholte Antworten. Letzteres ist mit absichtlich vertauschter Reihenfolge
regressionsgesichert, nicht durch längeres Warten verborgen. Native UI-Daten
liegen ausschließlich im eigenen synthetischen Wegwerfcontainer.

## Geplanter Betriebsablauf

Vor dem tatsächlichen Update sind aktuelle Einheit/Ports, Quellpaket und alter
Runtimepfad zu bestätigen. Neue Runtime getrennt installieren, vorhandene
Anwendungsschlüssel unverändert verwenden, nur eigenen API-Dienst kontrolliert
umschalten/neustarten. Keine fremden Dienste stoppen, Proxy/TLS/DNS nicht ändern.
Bei Fehlern ausschließlich die nachgewiesene vorherige Runtime wieder verwenden.
Keine Migration bedeutet keinen automatischen Daten-Downgrade: Sperren/Rollen-
entscheidungen und Audit bleiben erhalten und dürfen nicht still zurückgesetzt
werden. Ein Code-Rollback darf widerrufene Sitzungen nicht wiederbeleben.

Der Sicherungsnachweis09.11 gilt für die damalige leere Datenbank, nicht pauschal
für die vier inzwischen absichtlich erhaltenen synthetischen Benutzer samt
Kalenderdaten. Keine neue DB-Testmutation auf dieser Referenz ohne passenden
aktuellen Wiederherstellungsnachweis oder tatsächlich geprüfte gleichwertige
Kompensation. Kein blindes Wiederholen der alten Sicherung oder GPG-Verfahren.
Eine neue Runtime wird nicht allein deshalb installiert, weil lokal alles grün ist.

**Aktuell kein VPS-Update ausgeführt.** Für Installation fehlen aktuelle
privilegierte Zustands-/Rollbacknachweise im zusammenhängenden Updatefenster.
Die lokale Prüfung ersetzt diese nicht. Read-only10.11 19:23 MEZ: beide eigenen
und alle vier fremden VPS-Dienste `active`; kein Serverzustand geändert.
Zusätzliche reine Leseprüfung19:44 MEZ: `sudo -n systemctl show` scheitert
an erforderlicher interaktiver Berechtigung. Kein Passwortdialog gestartet,
keine neue Owner-Freigabe für bereits autorisierte technische Schritte verlangt.

## Persönliche Aktivierung Bleibt Separat

Alle neun geprüften Profile sind in der [Zuordnungsmatrix](coach-account-mapping-v1-2026-11-10.md)
vorbereitet; reale Ziel-UUIDs und persönliche Coachlogins bleiben offen.
Bestehende synthetische UUIDs werden niemals echten Personen zugeteilt.
Der erste persönliche Admin benötigt einen eigens genehmigten Bootstrap; der
bestehende Synthetic-Admin wird weder umbenannt noch ersetzt. Die bisherige CLI
lehnt einen weiteren Bootstrap bei aktivem Admin bewusst ab. Keine Umgehung.
Janay ist fachlich als zuweisbare `calendar_reviewer` vorgesehen, nicht als Admin.

Für normale Zugänge fehlen bestätigtes App-DNS/HTTPS/Zugriffsschutz und der
freigegebene Einladungsversand. [Versandfertige EDV-Anfrage](edv-portal-dns-smtp-2026-11-10.md)
ist vorbereitet, nicht versendet. Aktuelles privates Pilotzertifikat:
**24.11.2026,18:20:45 MEZ**. Technischer Tunnel bleibt nur die Zwischenlösung.

Kurzanleitungen: [Manuel](pilot-admin-guide.md), [Janay](pilot-janay-guide.md),
[Coaches](pilot-coach-guide.md), [Erstaktivierung](pilot-first-activation.md).
Janays fachliche Abnahme und ausdrückliche personenbezogene Aktivierungsfreigabe
bleiben offen. Keine reale Mail, Rolle, Benutzeranlage oder COACH-3B REAL APPLY.

## Geschütztes V1-Updatefenster 11.11

Der Owner-Auftrag genehmigt das technische Update innerhalb der nachstehenden
Grenzen. Keine erneute pauschale Freigabe und kein Wiederholen des Installers.
V1 ist bis zum tatsächlichen PASS des neuen Operatorlaufs **nicht installiert**.

Einstieg: `deploy/scripts/run-vps-v1-update.ps1`, gebunden an einen geprüften
vollen Operator-Commit. Das unveränderte Anwendungspaket bleibt `bc53775b08dc`
mit dem oben genannten ZIP-Hash. Keine Migration: weiterhin0001–0006.

1. Ein privates, erhöhtes PowerShell7-Fenster unter demselben Windows-Benutzer.
   Bestehender Tunnel darf offen bleiben; vorhandene Pilotfenster während des
   Updates nicht bedienen. Kein Protokollieren oder Aufzeichnen der Sitzung.
   Nur das VPS-sudo-Passwort wird verdeckt abgefragt, kein DB-/GPG-/USB-Passwort.
2. Aktueller BitLocker-C-Schutz, freie Kapazität und private Operator-/SYSTEM-ACL
   müssen nachweisbar sein. Neuer eindeutiger externer Laufordner, CreateNew,
   keine bestehende Datei überschreiben. Kein unverschlüsselter Dump auf Platte.
3. Exakte ursprüngliche Einheiten/Runtime/Leaf/Origin und vier synthetische
   Referenzkonten prüfen; alle sechs Dienste und minimale DB-Rechte gesund.
   Der vorhandene Lauf `e89ce1ef…` bindet CA/Leaf und Ausgangspaket, ersetzt aber
   keine Sicherung der inzwischen gefüllten Datenbank.
4. Aktuelle27 Tabellen unter exportiertem Read-only-Snapshot sichern. Dump,
   Baseline und die vier exakt erlaubten ursprünglichen Konfigurationsdateien
   ausschließlich über den privaten Prozesskanal DPAPI-geschützt ablegen.
   SHA-256, erneutes Lesen, Entschlüsselung im frischen Prozess und abgewiesene
   Manipulation prüfen. Exakt diese wieder gelesene Dumpkopie in einer eigenen
   gesperrten Probe-DB restaurieren; Schema/Daten/Rechte/Zähler vergleichen,
   Probe entfernen und unveränderte Quelle bestätigen. Maschinen-/benutzer-
   gebundene Übergangssicherung, kein portabler Disaster-Recovery-Nachweis.
5. V1 getrennt unter `/opt/competence-hub-pilot/releases/bc53775b08dc` offline
   installieren. Alten Runtimepfad, originale Einheiten, Schlüssel, TLS und
   Konfiguration unverändert erhalten; nur eigener API-ExecStart-Drop-in.
   Vor Umschalten tatsächliche systemd-Konfiguration prüfen.
6. Eigene additive synthetische Kohorte, niemals die alten Konten übernehmen.
   Für native Einladungsabnahme kurzzeitig ausschließlich Outbox-Erfassung mit
   `example.invalid`, ohne SMTP-Konfiguration oder Zustellworker. Tokens bleiben
   im privaten Prüfprozess; keine Admin-UI-Ausgabe/Versand. Danach eigene Kohorte
   exakt entfernen und temporären Capture-Drop-in entfernen. Zustellung wieder
   geschlossen, Port/Proxy/TLS unverändert.
7. Referenzvergleich:26 Tabellen zeilenidentisch; fremde Rate-Limit-Buckets
   identisch. Gemeinsam genutzte synthetische IP-Schutzwerte bleiben erhalten,
   nicht zurückgesetzt; Sequenzen niemals zurückdrehen. Unbekannte Änderungen
   führen zu STOP/Review, nicht zu einem automatischen Quell-DB-Restore.
8. Native Abnahme, eigener Neustart, sechs Dienste, unveränderte Listener und
   Originalkonfiguration, bereinigte Logprüfung, striktes HTTPS/Hostname/Leaf,
   exakt ausgeliefertes V1-Asset sowie geschlossene Zustellung vor endgültigem
   Commit-Acknowledge. Bei Fehlern nur eigene Testdaten kompensieren und den
   eigenen Runtime-Drop-in zurücknehmen. Staged Dateien zur Diagnose erhalten.

Lokale Update- und Rückrollprobe sind am11.11 grün; der vollständige Operatorbefehl
wird mit dem endgültigen geprüften Commit übergeben. Reales Resultat unter
`release-artifacts/vps-v1-update/<lauf>.json`; vor dessen Prüfung keine Remote-
Abnahme behaupten. Bei STOP nicht automatisch wiederholen, sondern den konkreten
Phase-/Fehlercode prüfen. Originale/private Artefakte bleiben außerhalb von Git.

DNS/externes TLS/SMTP bleiben offen, Zertifikatsfrist24.11 unverändert. Der
vorbereitete [EDV-Text](edv-portal-dns-smtp-2026-11-10.md) ist noch nicht versendet.
Persönliche Aktivierung, reale Coachzuordnungen und COACH-3B bleiben gesperrt.

### Lokale Betriebsnachweise 11.11

- Ubuntu/Python3.12/PostgreSQL16, exaktes altes und V1-Wheel, striktes privates
  HTTPS/Firefox:61 CAL-Prüfungen und33 V1-Zugangsprüfungen bestanden. Zusätzlich41
  Prüfungen beim Aufbau der absichtlich erhaltenen Vier-Konten-Referenz.
  Native MFA/Session/Role/RBAC, Einladungswiderruf/Neuausstellung/persönliches
  Passwort, Sperre/Rollenwechsel/Audit, drei Touren/Dashboards, fremde Coaches,
  echter Versionskonflikt mit bewusstem Neuladen, ICS/Kalender/Neustart grün.
- Aktuelle gefüllte DB aus exportiertem Snapshot gesichert und exakt isoliert
  restauriert, eigene Probe entfernt. Nach Update/Cleanup26 Tabellen identisch,
  fremde Rate-Limits gleich, gemeinsame IP-Schutzwerte erhalten, Sequenzen nicht
  zurückgedreht. Abschließendes V1-Asset und geschlossene Zustellung bestätigt.
  Report `.tmp/ch-pilot-proof-0a260e22565e43839479cb78c8772f77/result.json`, SHA-256
  `fac7eee10877bf6927d4500abd1379b65ead7ebe15ffc63c52c069a3fec0e751`.
- Separater Rückrolllauf: alter Code wieder erreichbar, originale Referenzdaten
  erhalten, keine Quell-DB restauriert. Report
  `.tmp/ch-pilot-proof-e5231ba121d94801a8830785e55521e2/result.json`, SHA-256
  `ee6b54fbeb30658d8cba9c21651c4a121b117620e87612db2f3e015d039a56f1`.
  Beide eigenen Container nachweislich entfernt; keine VPS-Aktion.
- Grenze: Container ersetzt systemd durch einen eigenen Prozessmanager und
  Windows-DPAPI durch synthetisches AES-GCM. Dies ist ausdrücklich **kein echter
  VPS-/DPAPI-/Sechs-Dienste-Nachweis**. Diese Gates laufen privat im Operatorlauf.
- Gesamtsuite1.663 bestanden/31 ausgelassen,314,27 Sekunden.30 bekannte Opt-in-/
  Umgebungs-Skips plus ein nicht übernommener belegter lokaler Testport55433.
  JUnit `.tmp/vps-v1-update-final-tests.xml`, SHA-256
  `667f180f872903b0d95403f3142d365ca7730b918574529c3774ed26acaad4a4`.
  Danach103 gezielte Betriebs-/Sicherungs-/Installerregressionen grün, darunter
  PowerShell-Argumente/UTF-8, bestehende Daten/Dateien schützen, aktuelle Restore-
  Pflicht, Rate-Limit-Namespace und zeitlich begrenzte Bereitschaftsprüfung.
- Screenshotprüfung390px und native200: keine Text-/Tabüberlagerung, Dialog und
  Aktionen durch Fokus/Scroll erreichbar. Firefox/Playwright-Mauskoordinaten
  drifteten bei nativen200%; stattdessen echte Tastatur plus DOM-Textrange/
  Trefferflächenprüfung, niemals Force-Click. Viewportaufnahmen statt irreführender
  Full-page-Aufnahme des nativen Dialogs. Frühere abgebrochene lokale Läufe sind
  keine Abnahme; eigene Ressourcen jeweils entfernt, Originaldateien unberührt.
- Frische reine SSH-Leseprüfung11.11: alle sechs VPS-Dienste aktiv. Keine sudo-
  Eingabe, Änderung oder Wiederholung des ursprünglichen Installers. Pages-
  Workflow ausschließlich manuell; dieser Code-Push veröffentlicht keine Website.

### Operator-STOP Vor Dem Betriebsblock

Manuels tatsächlicher Lauf mit `bb7794c` endete am11.11 mit `TimeoutExpired`;
Receipt `release-artifacts/vps-v1-update/da6b2342c1dd49ca91ceaadcd4c66c07.json`,
SHA-256 `42b4df672e5ce1c7f9945c1b2da9a26e969ae2efacf0824040877a2763b564e4`.
Phase `local_preflight`, Backup/Restore/Deployment jeweils `NOT_RUN`, keine
Migration/Account-/Websiteaktion. Der Timeout liegt laut Codepfad in einem der
beiden SSH-Unterprozesse vor dem privaten Root-Kanal; dort wird noch kein Agent
übergeben. Welcher der beiden Aufrufe hing und weshalb, ist aus dem damaligen
zu groben Bericht nicht nachträglich beweisbar. Kein Passwortproblem behaupten.

Beide reinen Vorprüfungen bekommen jetzt geschlossenen leeren stdin, nie das
interaktive Operator-Terminal. Zeitlimits bleiben20 Sekunden, keine stille
Wiederholung. SSH-Timeout und sudo-Probe-Timeout haben getrennte feste Codes;
SSH-Transportfehler der sudo-Probe führen nicht mehr zu einer Passwortabfrage.
Optionaler Fortschrittscallback hält die genaue Phase im bereinigten Bericht
fest. Der danach erforderliche private Passwort-/Bootstrapkanal behält seinen
eigenen offenen Prozesspipe; Geheimnisse werden nicht protokolliert.

108 fokussierte Regressionen bestanden einschließlich fünf neuer Fälle:
beide Timeoutstellen, sudo-Transportfehler, gültiger privater Kanal jeweils mit
und ohne erforderliche verdeckte Eingabe. Synthetische Werte, kein echtes sudo-
Passwort. Tatsächliche reine Diagnose am11.11: SSH und nichtinteraktive sudo-
Probe antworten; sudo verlangt erwartungsgemäß die lokale private Eingabe.
Strikte CA-/Hostname-/Leafprüfung über einen eigenen temporären Tunnel PASS;
dieser entfernt, alle sechs VPS-Dienste aktiv. Keine reale Servermutation oder
Sicherung ausgeführt. Ein erneuter isolierter Linux-Kalenderlauf ist für diesen
ausschließlich lokalen Verbindungsfix nicht erforderlich; Runtime, Paket, Agent,
Sicherungs-/Restore- und Rückrollverfahren sind unverändert.

Der korrigierte Operatorlauf benötigt einen neuen exakt gebundenen Code-Commit,
keine neue Owner-Freigabe für den bereits genehmigten Umfang. Nicht den alten
Installer und nicht den fehlgeschlagenen alten Befehl blind wiederholen.

## Genau Nächster Block

Geschütztes V1-Updatefenster des bestehenden Piloten: mit gebundenem Paket,
aktuellem privilegiertem Zustands-/Rollbacknachweis und geeigneter Erhaltung der
Referenzdaten ausschließlich die eigene Runtime aktualisieren und synthetisch
abnehmen. DoD: native Zugangs-/Tour-/Kalenderprüfungen und Neustart/Persistenz
grün, Referenzdaten erhalten, fremde Dienste gesund, keine echten Konten.
DNS/SMTP-Rückmeldung parallel einholen; keine reale Aktivierung vor deren Gates.
