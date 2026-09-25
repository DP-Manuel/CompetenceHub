# Mindforge Notice Layout P0 Handoff

Stand: 25.09.2026

## Befund und Ursache

Produktion und das lokale Release `d051a2e27f22` zeigen denselben Fehler im
Mindforge-Abschnitt `Klare Grenze`. Die zweite Zeile der Ueberschrift wurde mit
`white-space: nowrap` erzwungen, waehrend die linke Grid-Spalte nur rund
445 bis 446 Pixel breit war. Der echte Text war 527 bis 560 Pixel breit und
kollidierte bei 2048, 1440 und 1280 CSS-Pixeln mit zwei Zeilen des rechten
Erklaerungstextes.

Cache-deaktivierte Abrufe bestaetigen den Produktionsstand:

- Produktions-HTML SHA-256:
  `fe0d0b5ce52d76c0556916dc65aa17f576b3624d8d661139696db6d572203f5d`
- Produktions-CSS SHA-256:
  `0fc146ab917c5da2e6a4b40c84ff6d64d1bd04e22bcbafee126a4f84f8cbc104`
- Veroeffentlichte Regel: `white-space: nowrap`

Damit sind Browsercache und ein abweichender Upload als Ursache ausgeschlossen.

## Lokale Korrektur

Geaendert wurden nur:

- `apps/website/src/styles/global.css`
- `apps/website/scripts/run-messe-browser-acceptance.py`

Beide Grid-Kinder erhalten `min-width: 0`; die zweite Ueberschriftenzeile darf
normal umbrechen. Wortlaut, Farben, Typografie, Spaltenverhaeltnis, Abstand und
der bestehende 980-Pixel-Stapelbreakpoint bleiben unveraendert. Es gibt keine
feste Hoehe; der Abschnitt waechst mit seinem Inhalt.

## Screenshots und Browserpruefung

Die lokale Vergleichsablage liegt unter `.tmp/mindforge-layout-p0`:

- `before-2048.png`: sichtbare Ueberlagerung.
- `after-2048.png`: drei saubere Ueberschriftenzeilen und lesbarer rechter Text.
- `after-1440.png`, `after-1280.png`, `after-960.png`, `after-390.png`.
- `after-1280-at-200-percent.png`: sauberer 200-Prozent-Reflow.
- `before-measurements.json` und `after-measurements.json`: Messdaten.

Der Regressionstest nutzt echte Textzeilenrechtecke per
`Range.getClientRects()`. Er prueft, dass Ueberschrift und Erklaerung in ihren
Spalten bleiben, keine Textzeilen kollidieren oder abgeschnitten werden, die
Abschnittshoehe ausreicht und kleine Breiten stapeln.

## Nachweise

- Astro: 41 Dateien, 0 Fehler, 0 Warnungen, 0 Hinweise.
- Build: 33 Seiten.
- Interne Referenzen: 1.237 bestanden.
- Edge-Gesamtabnahme: 865/865 bestanden.
- Pflichtbreiten: 2048, 1440, 1280, 960 und 390 CSS-Pixel.
- 200 Prozent: 1280 physische Pixel als 640 CSS-Pixel bei DPR 2.

## Releasezustand und Rollbackvertrag

Der vorbereitete Kandidat ist absichtlich nicht deploybar:

- Artefakt:
  `competence-hub-website-d051a2e27f22-20260925T120603Z-dirty.zip`
- Umfang: 52 Dateien.
- SHA-256:
  `9f2325ec0a6cf73c206fc904fb4fe444ce851c20ba81813e29da2bd90364f5a9`.
- Manifest: `dirty: true`, `deployment_authorized: false`.

Nach Freigabe sind erforderlich: nur die zwei SB-54-Dateien committen und
pushen, ein Clean-Artefakt mit neuem Commit erzeugen, die aktuelle Produktion
`d051a2e27f22` frisch und vollstaendig sichern und inventarisieren, das
bereinigte SFTP-Paket erzeugen, gezielt aktualisieren und danach den
Textgeometrie-, Kernrouten-, Redirect-, Asset- und Sicherheitsheader-Smoke auf
Produktion ausfuehren. Die frische Sicherung von `d051a2e27f22` ist der
Notfall-Rollback; sie bringt im Rueckrollfall den bekannten visuellen P0 zurueck
und darf daher nur bei einem schwereren Releasefehler verwendet werden.

## Stop und erforderliche Freigabe

Es erfolgte kein Commit, Push oder Produktionsupload. Das naechste Gate braucht
Manuels ausdrueckliche Freigabe fuer Commit, Push und den kontrollierten
Produktionsupload dieses P0-Fixes. CAL-1, Backend, Coachprofile und alle anderen
Websitebereiche bleiben unveraendert und pausiert.
