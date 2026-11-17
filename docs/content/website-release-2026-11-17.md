# Website-Release und Coachstart

Stand17.11.2026. Website-Sprint und anschließend separat freigegebener IONOS-
Produktionsrelease **PASS**. Quelle11cb1ea/Paket c3169746… tatsächlich veröffentlicht;
frische geschützte Sicherung, Rückfallprobe, SFTP55/55 und öffentliches HTTP54/54
sowie Desktop-/Smartphone-Browserwege bestanden. Keine VPS-, Datenbank-, Schlüssel-,
Benutzer- oder Mailaktion. Die Vorher-/Kandidaten-Tabelle bleibt als Vergleich erhalten.

## Tatsächlicher Umgebungsvergleich

| Bereich | IONOS vor diesem Sprint | Bisherige Pages-Vorschau | Geprüfter lokaler Kandidat |
| --- | --- | --- | --- |
| Coaches | Galvano, Rodríguez; sechs ausdrücklich fiktive Demos | Neun freigegebene Vorschauprofile | IONOS-Kandidat: zusätzlich Gülcan; Preview: acht, Hupp pausiert |
| Finder | Noch nicht enthalten | 27 Angebote/29 Formate, Coachauswahl noch nicht veröffentlicht | Preview behält27/29; IONOS ausschließlich Gülcans3 Familien/5 Formate |
| Bedarf → Angebot | Generische Kontaktwege | Finder und Profile vorhanden | Workshops direkt zum Finder, Führung zu passenden Coaches, Profil zurück zum Angebot |
| Anfrage | Mailclient, kein Serverversand | Dasselbe Verfahren | Angebot/Coach im kodierten E-Mail-Entwurf; Mailclient-Hinweis und Telefon bleiben |
| Kalender | Klar gekennzeichnete Beispiele | Klar gekennzeichnete Beispiele | Kontextlinks zum Kalender/Kontakt; keine echten Termine, keine private API |
| Recht/SEO | Zentrale D+P-Rechtsseiten, Produktionscanonical/Sitemap | noindex/nofollow/noarchive, Robots blockiert, kein Sitemapindex | Umgebungsgrenzen bleiben; Gülcan nur im Produktions-Sitemap des Kandidaten |

Lesender HTTP-Abgleich: **51/51 öffentlich abrufbare Dateien** stimmen exakt mit
dem bekannten Produktions-ZIP überein. Die52. Datei `.htaccess` ist nicht per HTTP
prüfbar; ihr aktueller Remoteinhalt benötigt vor einem späteren Upload eine frische
SFTP-Inventur. Es gab weder SFTP-Verbindung noch Produktionsänderung.

Pages war vor dem Sprint auf `78c3470258ea034b677fffd1157d8da3e3fcde78`,
Workflowlauf `42060354587` vom05.11. Der lokale16.11-Navigationsstand war noch
nicht veröffentlicht. Quell-HEAD, neues Produktionspaket und tatsächlich
veröffentlichter Pages-HEAD werden getrennt gebunden, nicht gleichgesetzt.

## Rechte und minimale Nacharbeiten

- Produktionsfähig: vorhandene Galvano-/Rodríguez-Profile und die ausdrücklich
  am29.10 für IONOS bestätigten Gülcan-Kurzinhalte samt Originalporträt.
- Nur Vorschau: Schwabauer, Klemm, Celic, Wegner-Ney und das bisherige Beckerprofil.
  Neue ungeklärte Becker-Angebotskandidaten bleiben ausgeschlossen.
- Hupp: Owner-Pause17.11; kein aktives Profil, keine direkte Profilroute und keine
  Einladung. Quellen und historische Identität bleiben erhalten; keine DBänderung.
- Unklar bleibt jede weitergehende Produktions-/Konto-/Identitätsfreigabe. Kein
  fremdes Angebot, Preis, Abschluss oder persönlicher Termin wird ergänzt.
- Technisch: derselbe Finder rendert beide Datensätze; keine doppelte Suchlogik.
  Anfragen bleiben Entwürfe, Beispieltermine nicht buchbar, Registry-Projektion aus.

## Onboarding und CAL-2

Die [neun Zeilen der Aktivierungsmatrix](../operations/coach-account-mapping-v1-2026-11-10.md)
bleiben erhalten: acht spätere Kandidaten, Hupp ON_HOLD, keine realen Ziel-UUIDs
oder bestätigten Loginidentitäten erfunden. Websitefreigabe ist keine Kontofreigabe.
Der [sechsteilige Kurzstart](../operations/pilot-coach-guide.md) führt über Einladung,
Passwort, MFA/Recovery, Tour, ersten Entwurf und Einreichen. Die vorhandene
Einladungsvorschau wird weiterverwendet; kein echter Versand.

Der [kleine CAL-2-Vorschlag](../requirements/cal2-small-slice-2026-11-17.md)
übernimmt D01–D08/ADR0007; nur Zeitpunkt der Kapazitätsbindung und Fristwirkung
brauchen Präzisierung. Keine Implementierung oder erneute CAL-1-Gesamtabnahme.

## Gezielte Prüfung

- 37 Node-Modell-/Projektionsprüfungen bestanden: Rechte,8/3-Profilgrenzen,
  Finder27/3, zugelassene Formate, unveränderte Porträtbytes, keine gehaltenen Inhalte.
- 15 fokussierte Pythonprüfungen bestanden: öffentliche SHA-/ZIP-Differenz und
  bestehender sicherer, nicht ausführender SFTP-Rehearsalvertrag; Bilder/Styles
  vor abhängigen Seiten und Startseite zuletzt, ohne Remoteausführung.
- Astro in beiden Modi: keine Fehler/Warnungen/Hinweise; isolierter Releasecheck80 Quelldateien.
  Produktionslinks1365, Previewlinks1398 bestanden.
- Acht tatsächliche lokale Browserwege: beide Modi bei1440px,390px, ohne
  JavaScript und nativen200%; Tastatur, Fokus, Reduced Motion, Finder/Leerzustand,
  fünf Anfragewege, geladene Bilder, Formgültigkeit und Rechtslinks.
- Kein HTTP-Schreibaufruf, externe Ressource oder JavaScriptfehler in diesen
  Wegen; Hupp-Direkteinstieg404. Formular wurde nicht versendet.
- Native200-Firefox-Prüfung verwendet Fokus/Enter; dessen automatisierter
  Pointerklick wurde nicht als belastbarer Nachweis gezählt. Zusätzliche gezielte
  Edge-Probe mit echtem200%-Profil: Workshoplink → Coachfilter → Aufklappen →
  Profillink per normalem Mausclick PASS, ohne Forceclick oder CSS-Zoom.
- Screenshots unter `release-artifacts/website-release-20261117/`, öffentliche
  Vorher-Metadaten unter `.tmp/website-release-20261117/public-before.json`.
  Keine Wiederholung des Backend-Gesamttests oder von Kalender-Datumsreihen.

## Release und Rückfall

| Gegenstand | Tatsächlich gebundener Stand |
| --- | --- |
| Website-Quellcommit | `11cb1ea90fb5d72c38a5c9cd5c661285bcfdfbe5`, gepusht |
| Pages | [Lauf44149446991](https://github.com/DP-Manuel/CompetenceHub/actions/runs/44149446991), success17.11 um19:36 MEZ, genau derselbe Quellcommit |
| Veröffentlichte Vorschau | [GitHub Pages](https://dp-manuel.github.io/CompetenceHub/), vier Live-Browserwege PASS:1440/390/no-JS/native200; Hupp-Direktadresse404 |
| Endgültiges Produktions-ZIP | `release-artifacts/website/competence-hub-website-11cb1ea90fb5-20261117T184034Z.zip` |
| ZIP SHA-256 | `c3169746eaeaee9e4959cf8b67923d408a845aafce18d69c5659011db6695c05` |
| Quellbindung / Parität | Sauberer isolierter Git-Checkout, Manifest dirty=false;55/55 Dateien bytegleich zum lokal browsergeprüften Produktionsbuild |
| Dateidelta zum IONOS-ZIP |3 neu,34 geändert,0 entfernt,18 unverändert; alle bisherigen HTMLrouten bleiben |
| Manifest | Gleichnamige `.json` neben dem ZIP, deployment_authorized=false |
| Vorbereitung | `release-artifacts/website-sftp-rehearsal/20261117-final/website-11cb1ea90fb5-sftp-rehearsal/` |
| Dateiinventar | Dort `release-files.sha256`, SHA-256 `43a4f7068ab0b9117dc40177e948a46fe79497ed1896081e8b3c3819f38986bc` |
| Exaktes Delta | `release-artifacts/website-release-20261117/release-final.json`, SHA-256 `5c1fa953155a6f2f75a246e93e8f1a58fd3bf6d76ecbf7876f65f9c056fb7ca8` |

Neu sind nur Gülcans Profilseite/Porträt und das gemeinsame Finder-Skript. Die34
geänderten Dateien sind HTMLseiten mit gemeinsamer Navigation/gezielten CTAs
sowie das um Gülcan ergänzte Sitemap. Styles, Kalender-Skript, bestehende Bilder,
`.htaccess`, Favicon und Robots bleiben bytegleich. Windows-Checkout-Zeilenenden
wurden nur im eigenen isolierten Build auf den unveränderten Git-/Produktionsstand
gebracht; keine Repository-Konfiguration oder Produktionsdatei verändert.
Frühe lokale Pakete von18:36/18:37 mit bloßer Zeilenendabweichung sind ausdrücklich
**keine** Release-/Rückfallziele. Maßgeblich ist nur18:40:34Z / Hash oben.

Vorher-/Nachher-HTTPmetadaten in `.tmp/website-release-20261117/public-before.json`
und `release-artifacts/website-release-20261117/public-final.json`: erneut51/51
IONOS-Dateien unverändert, Pages-Finder-Coachauswahl jetzt tatsächlich vorhanden.
Live-Browserquittung `public-preview.json`, lokale `local-browser.json`; Screenshots
einschließlich `edge-native200-pointer.png` wurden visuell geprüft.

SFTP-Plan verwendet nur den früher bestätigten Chroot `/` und Host-Key als
Zielbindung. **Aktuelle** Inventur, Remote-Backup, Remote-Änderungsfreigabe,
Produktions-Smoke und Rückfallausführung stehen weiterhin auf false. Keine
frühere Freigabequittung übernommen, keine SFTP-Verbindung ausgeführt.

Zulässiger bekannter Rückfall ist das tatsächlich veröffentlichte P0-korrigierte
ZIP `competence-hub-website-1b4e33efa5e1-20260925T121142Z.zip`, SHA-256
`d80bd25977dfabf5d3ecf9892ed1747ff18b69a485d6b631ea0a0a459226dd5f`.
Es liegt unter `release-artifacts/website/`. Frühere personenbezogene Releases
und das vor dem P0-Fix liegende `d051a2e` sind keine zulässigen Rückfallziele.
Zusätzlich braucht der tatsächliche Upload eine aktuelle vollständige
Webrootkopie mit Hashinventar; unbekannte Remote-Dateien niemals automatisch löschen.

IONOS-Freigabe umfasst erst ein konkret benanntes neues ZIP/Hash, dessen Dateidelta,
SFTP-Inventur/Backup, asset-first/index-last Aktivierung und öffentliche Smokes.
Das ist genau ein späterer Betriebsblock, keine Aufforderung zum Upload jetzt.
Mailbox-Endzustellung ist durch einen Mailto-Browsertest nicht nachgewiesen.
EDV-App-DNS/TLS/SMTP und persönliche Identitäts-/Rollen-/Registrygates bleiben
von dieser statischen Websitefreigabe getrennt.

## Genau Ein Nächster Owner-Block

**Freigabe des oben gebundenen IONOS-Websitepakets11cb1ea / SHA-256c3169746… für
Gülcans bestehenden freigegebenen Profil-/Kurzangebotsumfang, den darauf begrenzten
Finder und die geprüften Navigations-/Anfragewege.** Nach dieser Entscheidung
ein zusammenhängendes Betriebsfenster: aktuelle lesende Webroot-Inventur, vollständige
datierte Rückfallkopie samt Hashprüfung, nur verifizierte Paketdateien hochladen,
Bilder/Styles vor Seiten und index.html zuletzt, Rechte und HTTP-Smokes prüfen.
Unbekannte Remote-Dateien erhalten, keine weitere Person/Privatdaten/API aktivieren.

DoD: freigegebene Inhalte unter beiden HTTPS-Domains, erwartete Weiterleitung,
Gülcan/Finder/Coachlinks, Mailto/Telefon, Mobile/Keyboard, zentrale Rechtslinks,
Canonical/Robots/Sitemap und P0-Mindforge-Abschnitt visuell korrekt; belegter
Rückfallweg. Kein Coachkonto, SMTP-Testversand, VPS-, Datenbank- oder CAL-2-Eingriff.
Bis zu dieser einen Entscheidung bleibt IONOS beim akzeptierten Septemberstand.

## Owner-Freigabe Erteilt17.11

Manuel hat den genau gebundenen IONOS-Release einschließlich frischer Inventur,
geschützter Webrootsicherung, Rückfallnachweis, Upload und Produktionsprüfung
ausdrücklich freigegeben. Keine neue Ownerentscheidung für diesen Umfang nötig.
Die Freigabe ist noch kein Uploadnachweis. Tatsächliche Ausführung, lokale
Anmeldeinteraktion und Ergebnis gehören in den
[Betriebsrecord](../operations/website-ionos-release-2026-11-17.md).

## Tatsächliche Veröffentlichung Abgeschlossen

Der anschließend ausgeführte Betriebsblock ist PASS; der Betriebsrecord bindet
frischen Webroot-Rückfallstand, lokalen52/52-Restorenachweis,37 gezielte Uploads,
SFTP55/55, HTTP54/54 und tatsächliche1440/390px-Browserabnahme. Die oben formulierte
Ownerentscheidung ist damit geschlossen, kein erneuter Uploadauftrag. Der genaue
Paket-/Quellhash bleibt unverändert. Fünf andere reale Profile bleiben Preview-only,
Hupp pausiert; keine neue Pages-Veröffentlichung oder Portalaktivierung.
