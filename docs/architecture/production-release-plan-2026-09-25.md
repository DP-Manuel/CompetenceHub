# Competence Hub Production Release Plan - Rebaselined

Stand: 25.08.2026

Status: Vorbereitung. Dieser Plan autorisiert weder Upload noch DNS-Aenderung,
Serverinstallation, Kontoerstellung oder Echtdaten. Zugangsdaten und Secrets
bleiben ausserhalb des Repositories.

Der Dateiname bleibt als historischer Verweis auf den frueheren Zieltermin
erhalten. Der 25.09.2026 ist nicht mehr die Produktionsdeadline. Aktueller
Planungskorridor fuer einen ersten kleinen kontrollierten Start ist fruehestens
die zweite Oktoberhaelfte nach Manuels Rueckkehr; ein exaktes Datum ist offen.

## Ziel und Releasegrenze

Das technische Readiness-Paket fuer den 28.08. ist gruen. Nach EDV-Antwort,
Vertragsabschluss und Legal folgen Infrastrukturabnahme, persoenliches
Onboarding und kontrollierter Produktivstart. Der fruehere 25.09.-Termin ist
aufgehoben; der neue Pilottermin wird erst mit den Stakeholdern bestaetigt.

Der Release besteht aus zwei getrennten Artefakten:

1. statische Astro-Website auf dem IONOS-Webspace;
2. Same-Origin-Portal und API plus E-Mail-Worker auf dem bestehenden VPS.

Ein erfolgreicher Website-Upload aktiviert nicht automatisch das Portal. Der
SFTP-Zugang zum Website-Startverzeichnis kann keine dauerhaften Python-Prozesse
bereitstellen.

## Bekannte Ziele

| Bereich | Ziel | Status |
| --- | --- | --- |
| Website kanonisch | `https://competencehub.donner-partner.de` | DNS/Webspace/TLS laut EDV vorhanden |
| Website Redirect | `https://competence-hub.donner-partner.de` auf kanonische Domain | Ziel bestaetigt; Redirect noch zu pruefen |
| Portal/API | vorgeschlagen `https://competencehub-app.donner-partner.de` | DNS auf VPS, TLS und Freigabe offen |
| PostgreSQL | VPS, nur `127.0.0.1:5432` | Staging vorhanden und verifiziert |
| Kontaktmail | `competencehub@donner-partner.de` an Janay | fachlich bestaetigt; Routing-Smoke offen |
| Technikalias | `admin@competencehub.donner-partner.de` an Manuel | EDV-Bestaetigung offen; kein Login |
| Portallogins | persoenliche D+P-Adressen von Manuel und Janay | Adressen/Rollen bestaetigt; Konten nicht erstellt |
| Einladungen | E-Mail | SMTP-Vertrag und Absender offen |

## Releasephasen

### Phase 1 - bis 28.08.: Technical Readiness

- Produktionskonfiguration als geheimnisfreien Vertrag dokumentieren.
- Backend- und Worker-Start muessen bei fehlenden/unsicheren Werten scheitern.
- Statisches Website-Artefakt reproduzierbar bauen, hashen und inventarisieren.
- systemd-, Nginx-, Verzeichnis-, Rechte-, Log- und Rollbackvorlagen erstellen.
- SMTP-Adapter mit lokaler Testzustellung und minimierten Fehlercodes pruefen.
- Keine DNS-Aenderung, kein SFTP-Upload, kein reales Konto und kein Echtdatum.

### Phase 2 - September: Infrastruktur- und Betriebsabschluss

- App-DNS auf den VPS vorbereiten und TLS ausstellen, noch ohne Fachfreigabe.
- Getrennte Backend-/Worker-Dienste installieren und mit synthetischen Daten
  gegen Staging pruefen.
- Website-Webstand vor einem Testupload extern sichern; Upload und Ruecknahme
  mit freigegebenem Artefakt proben.
- Den bereits bestandenen externen Restore als Produktionsverfahren einplanen;
  Backup-/Monitor-Timer und Alarmweg erst nach expliziter Freigabe aktivieren.
- Chatbot vor/nach jedem VPS-Schritt pruefen; kein gemeinsamer Restart.

### Phase 3 - bis zur Rueckkehr: Legal und Terminierung

- Finalen Betreiber, Impressum, Datenschutz-/AGB-Anwendbarkeit und
  Kontaktprozess freigeben.
- Finalen Pilottermin, Janay-Onboarding und Thomas-Ross-Go/No-Go fuer die Zeit
  nach Manuels Rueckkehr terminieren.

### Phase 4 - fruehestens zweite Oktoberhaelfte: Kontrollierter Pilot

- Freigegebene Website und Portalversionen mit Commit/Artefakthash festhalten.
- Website mit vorherigem Webspace-Backup per SFTP veroeffentlichen.
- Backend/Worker aktivieren, Health/Readiness, TLS, Header, Rollen, Audit und
  Mailzustellung pruefen.
- Erst nach geschlossenem Daten-Gate den ersten freigegebenen Firmenrecord
  erfassen.
- Bei einem Stop-Kriterium Rollback oder dokumentiertes No-Go ohne Echtdaten.

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
