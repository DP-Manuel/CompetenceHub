# Website: interaktives Hub-Netz

Basis: [Website Evolution](website-evolution-2026-11-24.md), Pages-Stand
`e62960c`. Dieser Gestaltungsschritt ist ausschließlich für GitHub Pages
freigegeben. IONOS, VPS, Portal, Datenbank, DNS und E-Mail bleiben unverändert.

## Bedienen und gestalten

- Die acht Außenknoten bleiben normale Links. Ab 1024 CSS-Pixeln und mit
  Maus lassen sie sich auf der Startseite auch ziehen. Sie bleiben bis zum
  Zurücksetzen oder Neuladen an der neuen Position. Auf Touchgeräten ist
  Ziehen deaktiviert; Scrollen und Navigation bleiben unverändert möglich.
- Die sichtbaren Positionen und SVG-Endpunkte stammen aus denselben
  relativen Koordinaten. Pointer Capture hält die Geste bis zum Loslassen.
  Nach sieben CSS-Pixeln wird die Geste zum Drag; der zugehörige Klick
  navigiert dann nicht mehr. Eine begrenzte Kollisionsprüfung hält die
  Kreise im Feld und schützt den Mittelpunkt. Bei Resize wird die
  Anordnung übernommen, sofern sie noch passt, sonst zurückgesetzt.
- Die Positionen sind flüchtig. Keine externe Bibliothek, Datenspeicherung
  oder API. SVG-Linien sind dekorativ; Tastatur- und Touch-Navigation
  funktionieren unabhängig vom Drag. Keine Daueranimation im neuen Netz.
- Die zwei Startseitenporträts nutzen dasselbe Raster und Seitenverhältnis
  mit individuellem Bildfokus. Die Profile behalten Qualifikationen,
  Angebote und Kontakt; kompakte Vorschauen führen zu aufklappbaren Details.
- Unternehmensleistungen stehen gleich beim Einstieg; Anlässe und Ablauf
  sind als offene Listen organisiert. Angebotsfinder und Leistungssprünge
  bleiben vorhanden. Auf Pages liefert „Rhetorik & Vertrieb“ einen
  Kontaktweg statt eines zurückgestellten Profils; die bestehende Zuordnung
  im separaten Produktionsbuild bleibt erhalten.
- Die kompakte Prozessstrecke auf der Startseite hat eine scrollabhängige
  Linie und genau einen aktiven Schritt nach Erreichen der ersten Station.
  Dieselben Abstände steuern Ankersprünge und Fortschritt. Beim
  Zurückscrollen läuft der Fortschritt zurück; Reduced Motion betrifft nur
  die Übergänge. Der [Browsertest](../../apps/website/scripts/run-visual-recovery-browser.py)
  prüft echte Scroll-Eingaben, Teilfüllung, Anker, Resize und Zoom.

## Prüfen und veröffentlichen

1. `npm run test:preview`; anschließend für `production` und
   `preview` je `npm run build` und `npm run verify:dist`.
2. [Browserprüfung](../../apps/website/scripts/run-website-evolution-browser.py)
   in Firefox und Edge über das lokale Artefakt. Breiten 320 bis 1920,
   200 % nativer Firefox-Zoom, Maus-Drag, Resize, Reset, Klick, Tastatur und
   Touch. Vergleichsscreenshots unter `release-artifacts/website-interactive/`.
   Die Prüfung vergleicht echte Kreisgrenzen und die SVG-Endpunkte;
   überlappende Rechtecke allein beweisen bei Kreisen keine Kollision.
3. [Pages-Workflow](../../.github/workflows/pages-review.yml) manuell starten,
   dann dieselben Checks gegen die [öffentliche Vorschau](https://dp-manuel.github.io/CompetenceHub/).
   Nicht ausgewählte Profilrouten und Porträts müssen dort 404 liefern.
4. Nächster Schritt: Owner-Abnahme der neuen Vorschau. Design und Interaktion
   können unverändert in ein separat freigegebenes IONOS-Paket; Sichtbarkeit,
   Sitemap und Bereinigung früherer Routen bleiben Entscheidungen je Ziel.
