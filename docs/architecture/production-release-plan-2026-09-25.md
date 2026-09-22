# Competence Hub Production Release Plan - Rebaselined

Stand: 22.09.2026

Status: Die statische Website wurde am 22.09.2026 kontrolliert veroeffentlicht
und technisch abgenommen. Portal/API, DNS-Aenderung, Serverinstallation,
Kontoerstellung und Echtdaten bleiben davon getrennt. Zugangsdaten und Secrets
bleiben ausserhalb des Repositories.

Der Dateiname bleibt als Verweis auf die operative Manuel-Cutline erhalten.
Der 25.09.2026 ist keine automatische Produktionsfreigabe, aber die
verbindliche Frist fuer eine messefertige, reproduzierbar gebaute und an einen
autorisierten Techniker uebergabefaehige statische Website. Manuel ist ab
26.09. fuer drei Wochen abwesend; der stabile Messe-Demostand wird am
17.10.2026 benoetigt.

## Ziel und Releasegrenze

Das technische Readiness-Paket fuer den 28.08. ist gruen. Messe-Readiness des
oeffentlichen Frontends hat bis 25.09. Vorrang vor CAL-1-Ausbau. Thomas Ross
bestaetigte den IONOS-Document-Root
`/kunden/homepages/16/d101506010/htdocs/competencehub` fuer beide Domains und
den SFTP-Zugriff auf diesen Pfad; der aktuelle Inhalt wird vor jeder Aenderung
read-only verifiziert. Am 22.09. entfernte er die temporaere `index.php` und
gab die Umsetzung der Domain- und HTTPS-Weiterleitungen per `.htaccess` frei.
Der anschliessende oeffentliche Gegencheck zeigt keine Diagnoseausgabe mehr.
Ohne finale Produktionsfreigabe entsteht nur das
vollstaendig deploybare Handover-Paket, kein Upload.

Der Release besteht aus zwei getrennten Artefakten:

1. statische Astro-Website auf dem IONOS-Webspace;
2. Same-Origin-Portal und API plus E-Mail-Worker auf dem bestehenden VPS.

Ein erfolgreicher Website-Upload aktiviert nicht automatisch das Portal. Der
SFTP-Zugang zum Website-Startverzeichnis kann keine dauerhaften Python-Prozesse
bereitstellen.

## Bekannte Ziele

| Bereich | Ziel | Status |
| --- | --- | --- |
| Website kanonisch | `https://competencehub.donner-partner.de` | LIVE; HTTPS und Kernrouten geprueft |
| Website Redirect | `https://competence-hub.donner-partner.de` auf kanonische Domain | LIVE; HTTP/HTTPS liefern `301` auf kanonisches HTTPS |
| Portal/API | vorgeschlagen `https://competencehub-app.donner-partner.de` | DNS auf VPS, TLS und Freigabe offen |
| PostgreSQL | VPS, nur `127.0.0.1:5432` | Staging vorhanden und verifiziert |
| Kontaktmail | `competencehub@donner-partner.de` an Janay | fachlich bestaetigt; Routing-Smoke offen |
| Technikalias | `admin@competencehub.donner-partner.de` an Manuel | EDV-Bestaetigung offen; kein Login |
| Portallogins | persoenliche D+P-Adressen von Manuel und Janay | Adressen/Rollen bestaetigt; Konten nicht erstellt |
| Einladungen | E-Mail | SMTP-Vertrag und Absender offen |
| Betreiber | Donner + Partner; verantwortlich Lars Donner | bestaetigt 21.09. |
| Impressum / AGB | bestehende zentrale D+P-Seiten | bestaetigt 21.09. |
| Datenschutz | bestehende zentrale D+P-Seite | bestaetigt 21.09.; bei neuer Datenerhebung erneut pruefen |

## Releasephasen

### Phase 1 - bis 28.08.: Technical Readiness

- Produktionskonfiguration als geheimnisfreien Vertrag dokumentieren.
- Backend- und Worker-Start muessen bei fehlenden/unsicheren Werten scheitern.
- Statisches Website-Artefakt reproduzierbar bauen, hashen und inventarisieren.
- systemd-, Nginx-, Verzeichnis-, Rechte-, Log- und Rollbackvorlagen erstellen.
- SMTP-Adapter mit lokaler Testzustellung und minimierten Fehlercodes pruefen.
- Keine DNS-Aenderung, kein SFTP-Upload, kein reales Konto und kein Echtdatum.

### Phase 2 - bis 22.09.: Webroot und Messe-Gap-Analyse

- Korrigierten IONOS-Webroot nur lesend mit `pwd` und `ls -la` beweisen.
- Alle oeffentlichen Kernrouten, Links, CTAs, Metadaten, Legal-Flaechen und den
  synthetischen Kalender als P0/P1/P2 bewerten.
- Keine Remote-Datei veraendern und keine Backend-/CAL-1-Arbeit beginnen.

Status 22.09.: abgeschlossen. Webroot und Inhalt wurden read-only bewiesen,
die EDV entfernte die temporaere Diagnose-Datei, und vier oeffentliche
HTTP/HTTPS-Pruefungen zeigen nur den erwarteten leeren Webspace (`403`) ohne
`phpinfo()`.

### Phase 3 - 23.09. bis 24.09.: Frontend Freeze und Live-Test-Kandidat

- Alle P0 und wesentlichen P1 Website-Befunde lokal korrigieren.
- Desktop, Tablet, 390 CSS px, 200 Prozent, Tastatur, Fokus, Reduced Motion und
  horizontale Ueberbreite im echten Browser pruefen.
- Astro Check/Build, interne Referenzen, 404, robots/Sitemap, Canonical/OG und
  Release-Archive-Sicherheitspruefungen ausfuehren.
- Finales Artefakt mit Manifest und SHA-256 erzeugen; Freigabeflag bleibt
  `false`.
- Das Profil von Guelcan Elmas-Brandes ist fuer den Erst-Release vorgesehen;
  Manuel gab Name, Text, Portraet, belegte berufliche Profildaten und
  Veroeffentlichung am 22.09. frei. Private Kontaktdaten bleiben ausgeschlossen.
- Bei bestandenem visuellen und technischen Gate ist der kontrollierte
  Website-Live-Test fuer Donnerstag, 24.09., vorgesehen. Kleinere Korrekturen
  duerfen danach noch innerhalb der Woche nachgereicht werden.

### Phase 4 - 22.09. bis 25.09.: Live-Test, Nachbesserung und Handover

- Website-Feature-Freeze, geprueften Source-/Artefaktstand und ein
  secret-freies Techniker-Handover festhalten.
- Thomas schloss die EDV-Voraussetzung; Manuel autorisierte und bediente den
  kontrollierten Upload am 22.09.
- Falls beide Freigaben und alle technischen Stopper rechtzeitig schliessen:
  vor jedem Replace den
  bestehenden Webroot sichern und den kontrollierten statischen Release mit
  unmittelbarem Smoke/Rollback durchfuehren.

### Phase 5 - 26.09. bis 16.10.: Kontrollierte Vertretungsphase

- Kein geplanter Feature-Ausbau durch Manuel.
- Autorisierte Vertretung darf nur freigegebene Contentkorrekturen oder
  kontrollierte Fehlerbehebung anhand des Handover-Runbooks ausfuehren.
- App-DNS/SMTP, Backend, reale Konten/Rollen und Echtdaten bleiben eigene Gates.

### Phase 6 - 17.10.: Messe

- Stabilen oeffentlichen Website-Demostand verwenden.
- CAL-0.1 bleibt eine klar gekennzeichnete Vorschau und zeigt keine
  synthetischen Beispiele als echte buchbare Termine.

## Website-Release und Rollback

Vorbedingungen:

- finaler Betreiber und Rechtstexte freigegeben;
- Kontaktmail-Routing geprueft;
- Astro-Check/Build gruen;
- kanonische URL, Redirect, `robots.txt`, Sitemap und Altseiten-`noindex`
  geprueft;
- bestehender Webspace als datiertes Rollback-Artefakt gesichert.

Upload:

- SFTP interaktiv oder ueber ein lokal freigegebenes Werkzeug;
- Passwort niemals in Kommandozeile, Skript, Git oder Log;
- nur den Inhalt des geprueften `dist`-Artefakts uebertragen;
- unbekannte Remote-Dateien nicht ungeprueft loeschen.

Smokes:

- HTTPS und Redirect beider Website-Domains;
- Start, Leistungen, Unternehmen, Coaches, Mindforge, Kontakt, Ueber uns und
  Rechtspfade;
- Kontakt-Mailto und sichtbare Empfaengeradresse;
- keine Review-Banner; keine Indexierung von Archiv/Login/Prototyp;
- mobile Kernansicht und Browserkonsole ohne blockierende Fehler.

Rollback: vorheriges Webspace-Artefakt wiederherstellen, Kernrouten erneut
pruefen und Ursache protokollieren.

Das lokale, nicht verbindende Vorbereitungspaket und die getrennten Gates fuer
Remote-Inventur, Webspace-Backup und Replace sind in
`website-sftp-release-rehearsal-runbook.md` beschrieben. Ohne bestaetigten
Remote-Webroot wird kein ausfuehrbarer Upload- oder Loeschplan erzeugt.

## Portal-/API-/Worker-Release und Rollback

Vorbedingungen:

- eigene Linux-Identitaet, Verzeichnisse, Virtual Environment, Ports und Logs;
- externe Environment-Datei mit Modus `0600`, niemals aus Git;
- PostgreSQL weiterhin loopback-only und Runtime-Rolle least privilege;
- App-Origin/TLS/DNS und SMTP-Absender freigegeben;
- verschluesselter externer Restore und Notfallzugriff nachgewiesen;
- lokale und Staging-Tests gruen, keine offenen hohen/kritischen Befunde.

Smokes:

- `/health/live`, `/health/ready`, Portal-HTML und Security Header;
- Login, MFA, Session-Rotation, Logout und negative Origin/CSRF/Rollenpfade;
- E-Mail-Einladung mit nicht-produktivem Testkonto;
- Firma plus Erstkontakt einmalig anlegen, suchen, lesen und korrigieren;
- Audit ohne Payload und Cleanup ohne Rueckstaende;
- Chatbot, Nginx, Fail2ban und PostgreSQL bleiben gesund.

Rollback: Dienst auf vorheriges Release-Verzeichnis umschalten und neu starten.
Migrationen werden nicht blind rueckwaerts ausgefuehrt; bei Schemaaenderungen
gilt ein eigener Repair-/Restore-Entscheid. Reale Daten werden erst nach
erfolgreichem Restore-Gate zugelassen.

## Stop-Kriterien

- finaler Betreiber oder rechtliche Freigabe fehlt beim Website-Go-Live;
- kein verschluesselter Restore aus einer externen Kopie;
- App-DNS/TLS, SMTP-Absender oder Secretbetrieb nicht eindeutig;
- offene hohe/kritische Sicherheitsfeststellung;
- Chatbot-/Nginx-/PostgreSQL-Gesundheit verschlechtert sich;
- Rollbackpfad oder verantwortliche Person ist nicht verfuegbar.

## Noch benoetigte Angaben

1. EDV-Bestaetigung fuer Portal-DNS auf den VPS.
2. SMTP-Host, Port, TLS-Modus, Benutzeridentitaet und erlaubte Absenderadresse.
3. Gewuenschter Systemabsender; Empfehlung:
   `portal@donner-partner.de` mit Reply-To
   `competencehub@donner-partner.de` statt eines unueberwachten `noreply`.
4. Bestaetigung und Routing des Technikalias; nicht als Login verwenden.
5. Janay-Onboarding und Thomas-Ross-Go/No-Go fuer den bestaetigten Pilottermin.
6. Datentraegerverschluesselung, Restoretermin und Nachfolgezugriff.
7. Finaler Betreiber und freigegebene Rechtstexte.

## Technischer Einladungsstand

Lokal umgesetzt und automatisiert geprueft sind:

- Runtime-Konfiguration fuer getrennte Idempotenz-/Outbox-Schluessel und eine
  externe kompromittierte-Passwort-Fingerprintquelle;
- Account-Lifecycle-Repository und Service in der konfigurierten App-Factory;
- TLS-only SMTP-Adapter, begrenzter One-Shot-Worker und systemd-Timerbeispiele;
- HTTPS-Aktionslinks mit Token nur im URL-Fragment und sofortiger Entfernung
  aus der Adresszeile;
- Passwort-Reset, Einladungsannahme, anschliessende MFA-Einrichtung und eine
  Admin-only, idempotente Einladung fuer die Rolle `internal` im Portal.

Der aktuelle Clean-Source-Stand besteht 305 Tests bei 14 absichtlich opt-in
Staging-Skips; Compileall, Abhaengigkeiten und JavaScript-Syntax sind sauber. Der komplette
synthetische Onboarding-Pfad bestand anschliessend 14/14 Staging-Tests und
hinterliess keine Nutzer-, Session-, Outbox- oder Audit-Reste. Es wurde keine
externe SMTP-Verbindung aufgebaut.

Das Webapp-Release wird als versionsfixiertes Wheel-Bundle mit internem
Dateiinventar, externem Manifest und SHA-256-Pruefsumme erzeugt. Zwei
vollstaendige lokale Wiederholungsbuilds lieferten bytegleich denselben
ZIP-Hash. Der saubere Release-Nachweis von Commit `70e92ba` ist nicht als
`dirty` markiert; der aktuelle Projektcheckpoint ist `ea276b9`. Vor realer
Einladung fehlen weiterhin
App-DNS/TLS, die freigegebenen SMTP-/Absenderwerte, ein gepruefter Linux-
Wheelhouse- oder Paketquellenweg, Monitoring/Retention sowie die beaufsichtigte
Abnahme. Die Worker-Konfiguration bleibt bis dahin fail-closed.
