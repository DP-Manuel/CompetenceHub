# Website Evolution: erste Coach-Etappe

**24.11.2026.** Freigabe: ausschließlich die öffentliche GitHub-Pages-Vorschau.
Die laufende IONOS-Website, VPS, Portal, SMTP und DNS sind nicht Teil des Releases.

## Gestaltung und Nutzerwege

- Der interaktive Hub bleibt erhalten. Intro, Knoten und Handlungslinks
  haben eigene Layoutbereiche; unter 1024 CSS-Pixeln werden die Knoten zu
  normalen Links in einem Raster. Der vierstufige Ablauf ist ohne Scroll-
  Inszenierung lesbar.
- Die Startseite zeigt Herr Christian Galvano und Manuela Rodríguez, M.A.
  mit vorhandenen Porträts, direkt verlinkten Namen und kurzen Schwerpunkten.
  Frau Rappelt bleibt als Ansprechpartnerin mit Foto und Kontaktweg sichtbar.
- An den bestehenden Profil-URLs stehen Porträt, Schwerpunkte und Anfrage
  zuerst. Angebots- und Qualifikationsdetails lassen sich bei Interesse
  aufklappen. Keine veröffentlichten Termine: sichtbarer Leerzustand.
- Leistungen sind als offene Zeilen gegliedert. Recruiting, Personalentwicklung
  und Workshops behalten ihre direkten Anker; Finder und Profil verlinken
  einander. Anfragen öffnen weiterhin einen E-Mail-Entwurf, kein Versand.

## Veröffentlichungsregel

Die [zentrale Auswahl](../../apps/website/config/active-coach-publication.mjs)
trennt historisch genehmigte Profile von der je Ziel sichtbaren Auswahl und
den Startseitenplätzen. Bestand und historisch genehmigte Portraitdateien
bleiben unverändert. Ein vorbereitetes, noch nicht genehmigtes Profil gehört
nicht in `approvedCoachProfiles`. Ein genehmigtes, nicht für diese Etappe
ausgewähltes Profil fehlt im Ziel-Array. Eine Pause hat Vorrang vor einer
Auswahl; Frau Hupp bleibt pausiert. Demos werden nicht öffentlich gebaut.

Für die nächste Etappe zuerst Freigabe für Profil, Bild, Angebote und Ziel
belegen, dann den freigegebenen Slug in `rollout.preview` aufnehmen.
`featuredCoachSlugs` nur ändern, wenn ein Startseitenplatz beschlossen ist.
Verzeichnis, Suchdaten, Finder, statische Profilrouten und ausgelieferte
Porträts folgen der Auswahl. Der Finder zeigt für die erste Etappe vier
bereits beschriebene Schwerpunkte als individuell zu klärende Anfragen,
nicht als terminierte oder buchbare Formate. Kein privater Kalenderabruf.

Pages indexiert weiterhin nicht und liefert eine leere Sitemap. Aufgeschobene
Routen und Porträts werden **nicht** ausgeliefert; das ist keine rückwirkende
Löschung von bereits veröffentlichten Git-Ständen, IONOS-Seiten oder
Drittcaches. Keine nichtöffentlichen Inhalte in das öffentliche Repository
aufnehmen. Historische Einträge und Freigaben nicht umschreiben.

## Prüf- und Releaseweg

1. `npm run test:preview`, für `production` und `preview` jeweils
   `npm run build` und `npm run verify:dist`. Der Produktionsbuild bleibt
   eine separate Regression mit den acht historisch freigegebenen Profilen
   im Verzeichnis; er wird in diesem Fenster nicht veröffentlicht.
2. [Browserprüfung](../../apps/website/scripts/run-website-evolution-browser.py)
   am lokalen Vorschauartefakt und nach manueller Auslösung von
   [Pages Review](../../.github/workflows/pages-review.yml) gegen
   [die öffentliche Vorschau](https://dp-manuel.github.io/CompetenceHub/).
   Screenshots und Logs liegen lokal unter
   `release-artifacts/website-evolution-2026-11-24/`. Automatische
   Browserprüfungen sind kein gesprochener Screenreader-Test.
3. Nächster Block: Manuels Abnahme der öffentlichen Vorschau, insbesondere
   Portraitpräsentation, Einstieg für beide Zielgruppen und gestaffelte
   Sichtbarkeit. Für IONOS anschließend einen eigenen Freigabeumfang je
   Profil, Ziel-Sitemap und Bereinigung früherer Routen festlegen.
   Kein automatischer Produktionsrelease.
