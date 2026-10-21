# Coach-Veröffentlichungsmatrix

Stand: 21.10.2026. Production-Regel vom 24.09. bleibt bestehen; Preview-Freigabe siehe unten.

Die folgende historische Production-Matrix begrenzt den öffentlichen Messeauftritt. Sie ersetzt frühere
Einzelfreigaben, soweit sie mehr als die beiden unten genannten echten Profile
vorsahen.

| Öffentliche Darstellung | Status | Zulässiger Umfang | Bildstatus |
| --- | --- | --- | --- |
| Herr Christian Galvano | echtes Profil freigegeben | bestehender, bereits dokumentiert freigegebener Profilumfang | bestehendes freigegebenes Portrait |
| Manuela Rodríguez, M.A. | echtes Profil durch Manuel am 24.09.2026 freigegeben; Schreibweise und Abschluss am 25.09.2026 durch Manuela bestätigt | Name, Rolle, die von Manuel gelieferten Qualifikationen, Positionierungstext und Verweis auf D+P AI Advisory | offizielles D+P-Advisory-Portrait am 24.09.2026 durch Manuel freigegeben; lokal auf 1.200 x 1.200 Pixel verkleinert und ohne Quellmetadaten neu kodiert |
| Demoprofil 01 bis 06 | fiktive Demonstrationsdaten | generische Themen, Filter und Plattformdarstellung ohne reale Biografie, Referenz oder Kontaktangabe | einheitliche abstrakte Monogramme |

Bildquelle für Frau Rodriguez: offizieller D+P-Advisory-Medienbestand,
`https://advisory.donner-partner.de/wp-content/uploads/2026/08/1_MRa1.jpg`,
abgerufen und lokal verarbeitet am 24.09.2026. Die öffentliche Website bindet
die externe Datei nicht ein.

## Entfernte Identitäten

Die sechs früheren personenbezogenen Routen werden nicht weiter erzeugt. Ihre
Namen, Portraitdateien, Metadaten und individuellen Profiltexte sind aus dem
Website-Build entfernt. Aufrufe der alten Routen enden kontrolliert auf der
404-Seite; es gibt keine personenbezogene Weiterleitung.

## Technische Sicherung

- Sitemap enthält nur die beiden freigegebenen echten Profilrouten.
- Demoprofile tragen `noindex` und einen sichtbaren Fiktivhinweis.
- Der Kalender verwendet ausschließlich Christian Galvano oder ausdrücklich
  benannte Demoprofile und bleibt vollständig als Beispieldaten gekennzeichnet.
- `verify:dist` bricht ab, wenn entfernte Namen, Slugs oder Portraitpfade im
  erzeugten Artefakt auftauchen.
- Ein späteres echtes Profil benötigt erneut eine dokumentierte Freigabe für
  Name, Text, Rolle, Qualifikationen, Bild und Veröffentlichungszeitpunkt.

## Preview-Freigabe 21.10.2026

Manuels geliefertes Post-Messe Product Addendum gibt alle derzeit vorgesehenen
Coaches mit vorhandenen freigegebenen Namen, Kompetenzen, Texten und Bildern
für die öffentliche GitHub-Pages-Preview frei. Keine Übernahme in IONOS ist
damit freigegeben. Die obige Production-Matrix und ihr Privacy-Gate bleiben
unverändert wirksam.

| Preview-Profil | Freigegebene Quelle / Umfang | Portrait |
| --- | --- | --- |
| Herr Christian Galvano | aktuelles bestehendes Profil | bestehende WebP |
| Manuela Rodríguez, M.A. | aktuelles bestehendes Profil; Advisory-Ziel in Preview https://advisory.donner-partner.de/ | bestehende WebP |
| Frau Elisabeth Schwabauer | Git 53a89a8, Route elisabeth-schwabauer; Angebotsgruppen aus geliefertem Addendum | unveränderte Git-WebP |
| Frau Carolin Hupp | Git 53a89a8, Route carolin-hupp | kein Portrait vorhanden; vorhandenes Monogramm |
| Frau Gülcan Elmas-Brandes | Git 53a89a8, Route guelcan-elmas-brandes | unveränderte Git-PNG |
| Herr T. Wegner-Ney | Git 53a89a8, Route wegner-ney | unveränderte Git-JPG |
| Herr Goran Celic | Git 53a89a8, Route goran-celic | unveränderte Git-PNG |
| Frau Dr. Stefanie Becker | Git 53a89a8, Route stefanie-becker | unveränderte Git-WebP |

Neueste explizite Namenskorrektur am 21.10.2026: Manuel bestätigt
**Elisabeth Schwabauer (bisheriges Profil)**. Diese Bestätigung überschreibt
die abweichende Schreibweise im gelieferten Addendum. Sichtbarer Name,
Portraitidentität und bestehender Profilpfad bleiben konsistent. Kein neuer
Personenrecord, keine UUID-Zuordnung und keine personenbezogene Weiterleitung.

Die vier Angebotsgruppen enthalten ausschließlich die 17 gelieferten Titel.
Psychotherapie (HeilprG) wird gesondert als Quellenangebot genannt, nicht als
über Competence Hub buchbare Therapie; bestehende Leistungsgrenzen bleiben.
Themenkategorien sind redaktionelle Navigation, keine neu behaupteten
Coachqualifikationen. Insbesondere wird niemand neu Mediation zugeordnet.

Es wurde kein privater Quellenpfad gelesen. Es liegt aktuell kein weiteres
Messefeedback vor. Technische Trennung und QA:
[GitHub-Pages-Preview](../architecture/github-pages-preview-2026-10-21.md).
