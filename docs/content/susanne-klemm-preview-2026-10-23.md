# Susanne Klemm: Quellenprüfung Und Preview

Stand: 23.10.2026. Freigabe für Profil und beide Porträts durch Manuel in dieser
Sitzung ausdrücklich bestätigt. **Nur GitHub-Pages-Preview; keine IONOS-Freigabe.**

## Quellen Und Datenschutz

Ausschließlich gelesen: `Quellen/Coach/07. Susanne Klemm`.
Keine benachbarten Quellenordner, keine weitere Recherche zu dieser Person.

| Datei | Verwendeter öffentlicher Inhalt |
| --- | --- |
| Seminarangebote Donner-Partner.pdf | Acht Workshopangebote; Kommunikation/Fragetechniken, Selbst-/Fremdwahrnehmung, Körpersprache, Führungsrolle/-haltung, Abgrenzung und Stress; einzelne Angebote mit Pflegebezug |
| Zertifikate zu Qualifizierungen Gesamt.pdf | Acht Seiten visuell geprüft, da überwiegend gescannt; acht konkret benannte Aus-/Weiterbildungen |
| _DSC5321.jpeg | Ausgewähltes, freigegebenes Porträt; vorhandene WebP-Pipeline, proportional1200x1800, keine Retusche und kein Zuschnitt |
| _DSC5266.jpeg | Ebenfalls angesehen/freigegeben; nicht zusätzlich ausgeliefert |

Nicht übernommen: Signaturen, Dokumentnummern, Aussteller-Kontaktdaten und
sonstige nicht erforderliche Angaben. Keine Zertifikat-Scans oder Originalfotos
im öffentlichen Artefakt. WebP ohne EXIF/ICC-Quellmetadaten:352.732Bytes,
SHA-256 `d494f308dbc4f3a1e95d3f31dd17072ca543bfe18de036a53553cd281eeac21e`.

Keine widersprüchlichen Profilfassungen gefunden. Die Supervisions-Weiterbildung
ist ausdrücklich eine kompakte44-Stunden-Weiterbildung, keine behauptete
DGSv-Zertifizierung. Die Angabe DGSv/Mediation im Zertifikatsfuß gehört zur
Dozentin, nicht zu Susanne. Keine akademischen Titel, Berufsjahre, psychologische
Beratungs- oder Mediationsqualifikation aus fremder Urheberschaft abgeleitet.
Hypnose Coach wird nur als belegte Qualifikation genannt, nicht als Therapieangebot.

## Kanonische Vorschau-Daten

`apps/website/src/preview/susanne-klemm.ts` besitzt Kurzprofil, Kompetenzen,
acht Qualifikationen und acht Workshop-Titel. Kein zweiter manuell gepflegter
Backend-Datensatz und keine echte Coach-UUID/Accountzuordnung angelegt.
Route: `/coaches/susanne-klemm/`; vorhandene Profilkomponenten/CI.
Porträt: `src/preview/portraits/susanne-klemm.webp`, außerhalb des Production-public.

Bestehende Themen: Führung, Teams & Konflikte, Gesundheit & Prävention.
Bestehende redaktionelle Kategorien: Personalentwicklung und
Persönlichkeitsentwicklung. Keine neue Themen-Dublette oder eigene Kategorie;
keine eigenständige Karriere-/Mediationszuordnung. Kompetenzen und acht
Workshopformate bleiben getrennt von Themen und Taxonomiekategorien.
Kein erfundener Lebenslauf, persönliches Zitat, Region, Preis oder Termin.

## Tatsächliche Prüfung

- Modelltests9/9: bestehende Profile/Porträts unverändert, KategorienM:N,
  Quelle/Qualifikation, komplette eindeutige Routenmenge statt festem8er-Count.
- Astro check:0 Fehler/Warnings/Hints; Previewbuild34HTML und1280interne
  Referenzen geprüft; noindex und leere Sitemap bleiben, keine falsche Canonical.
- Bestehende breite Edge-Prüfung:1255checks, keine Browser-/Ressourcenfehler,
  Fremdnetzwerk- oder Schreibzugriffe. Hub-Regression134checks über
  2048/1440/1280/960/390CSS-px sowie echte200-%-Browservergrößerung.
- Neue Onboarding-Abnahme89checks: Übersicht/Profil Desktop1440/390,
  echtes200-%-Zoom, Themenfilter in beiden Kategorien, Tastatur-Kontaktweg,
  sichtbarer Fokus, geladenes Bild, tatsächliche Textrechtecke, Abschneiden
  durch Vorfahren und Überschneidung separater Textblöcke.
- Native Zoom-Aufnahme kalibriert: Edge liefert703CSS-px/1406physischepx.
  Standard-Screenshot clipte trotz korrekter DOM-Geometrie das Bild halb ab;
  korrigierte CDP-Aufnahmen verwenden physische Maße und prüfen PNG-Breite.
  Kein Layoutfix nötig. Hero-/Workshopbilder Desktop/Mobil und Zoom visuell geprüft.
- Production vollständig neu gebaut/verifiziert: alle52Dateien bytegleich
  zum Stand vor der Integration,1237Links geprüft; Susanne dort ausgeschlossen.

Lokale Evidence unter `apps/website/release-artifacts/susanne-20261023`,
`preview-qa` und `hub-ux-20261022`; nur aktuelle ausgeführte Ergebnisse zählen.
Falsche Zoom-Diagnosebilder sind keine Abnahmebelege; die endgültigen
Zoom-Bilder wurden mit kalibrierten physischen Maßen neu aufgenommen.

## Veröffentlichung Und Weiterführung

Die getrennt freigegebenen Änderungen sind committed und gepusht.
Pages veröffentlichte ausschließlich die Vorschau aus
`3e99e8e6151d78e281e17ed54d6c435bf4e9d740`:
[Actions39932275108](https://github.com/DP-Manuel/CompetenceHub/actions/runs/39932275108),
Build und Deployment erfolgreich am23.10.2026.

[Susannes öffentliches Profil](https://dp-manuel.github.io/CompetenceHub/coaches/susanne-klemm/)
wurde danach im echten Edge erneut geprüft:89 Onboardingchecks einschließlich
Desktop1440,390CSS-px, echtem200-%-Zoom, geladenem Porträt, acht Workshops,
noindex/fehlender Canonical, Textgeometrie, Tastatur-Kontaktweg und beiden
Themenfiltern bestanden. Zusätzlich134 öffentliche Hubchecks über fünf Breiten
und echtes200-%-Zoom bestanden. Öffentliche Mobil-/Zoom-Aufnahmen visuell geprüft.

Onboarding-Evidence separat unter
`apps/website/release-artifacts/susanne-public-20261023/acceptance.json`;
dafür wurde derselbe unveränderte lokale Runner mit öffentlichem Ursprung
statt lokalem Static-Server ausgeführt. Hub-Evidence:
`apps/website/release-artifacts/hub-ux-20261022/public-acceptance.json`
(Ordnername historisch; aktueller Lauf23.10). Alle eigenen Browserkontexte,
temporären Zoomprofile und Testcontainer beendet beziehungsweise entfernt.

Keine Produktionsfreigabe, serverseitige Migration oder reale UUID-Zuordnung.
COACH-1 definiert die spätere Registry-Projektion; dieser Quellenfall ersetzt
keinen freigegebenen Import-/Mappingprozess.
