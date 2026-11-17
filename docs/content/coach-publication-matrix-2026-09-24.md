# Coach-Veröffentlichungsmatrix

Stand: 17.11.2026. Historische Freigaben bleiben dokumentiert. Gülcans bestehende
IONOS-Rechte werden im lokalen Releasekandidaten berücksichtigt, noch kein Upload.
Neueste Owner-Entscheidung: Carolin Hupp pausiert; siehe unten.

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
| Frau Susanne Klemm | Konkreter Quellenordner07, Profil und beide Porträts von Manuel am23.10.2026 ausdrücklich für die öffentliche GitHub-Preview freigegeben; [Quellenprüfung/QA](susanne-klemm-preview-2026-10-23.md) | _DSC5321 als proportional verkleinerte, metadatenfreie WebP; zweites Bild nicht ausgeliefert |

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

## Zusätzliche Rechtefreigabe Gülcan Vom 29.10.2026

Manuel bestätigt ausdrücklich **Gülcan Elmas-Brandes: Vorschau und IONOS**,
nach konkreter Rückfrage zu Profil, Porträt und kurzen öffentlichen
Angebotsdarstellungen. Damit ist Gülcan zusätzlich zu den beiden historischen
Production-Profilen für diese Inhalte freigegeben. Die ausgelieferte IONOS-
Website bleibt unverändert; diese Rechtefreigabe ist kein ausgeführter Release.

| Gegenstand | Preview | IONOS / Production | Grenzen |
| --- | --- | --- | --- |
| Bestehendes Gülcan-Profil und Porträt guelcan-elmas-brandes.png | APPROVED | APPROVED | Vorhandene verifizierte Bildbytes und belegte Profildaten; keine neue Qualifikation erfinden |
| Kurze öffentliche Darstellungen der drei Angebotsfamilien / fünf belegten Formatkandidaten | APPROVED | APPROVED | Titel, Format, Zielgruppe, belegte Dauer/Durchführung, grobe Schwerpunkte und belegte Boundary; nur tatsächlich extrahierte Fakten |
| Vollständige Konzepte, Abläufe, Übungen, Arbeitsblätter und Originaldateien | NOT_APPROVED_BY_THIS_SCOPE | NOT_APPROVED_BY_THIS_SCOPE | Bleiben geschützt, kein vollständiger Abdruck aus einer pauschalen Coach-Freigabe |
| Noch unlesbare Tagesworkshop-/Reflexionsreihendetails | UNKNOWN | UNKNOWN | Ersatzquellen folgen später; keine Details ergänzen oder Lesbarkeit behaupten |

Freigebender: Manuel; bekanntes Datum29.10.2026, Uhrzeit nicht festgehalten.
Für die spätere Registry konkrete Revision/Assethash/Angebotsinhalt und Umgebung
gesondert binden; unbekannte ursprüngliche Einwilligungszeitpunkte nicht erfinden.
Keine Accounts, echten DB-Imports, Migrationen, Pages- oder IONOS-Uploads dadurch
ausgeführt oder im aktuellen Vorbereitungsslice freigegeben.

## Aktueller Veröffentlichungsumfang17.11

| Personengruppe | Öffentliche Preview | IONOS ab17.11 | Benutzeraktivierung |
| --- | --- | --- | --- |
| Christian Galvano, Manuela Rodríguez | APPROVED | bestehender freigegebener Umfang | Separat gated |
| Gülcan Elmas-Brandes | APPROVED | Profil, genaues vorhandenes Porträt, drei kurze Familien/fünf Formate gemäß29.10 | Separat gated |
| Elisabeth Schwabauer, Susanne Klemm, Goran Celic, T. Wegner-Ney, Dr. Stefanie Becker | bestehender APPROVED-Umfang, keine neuen Becker-Angebote | NOT_APPROVED | Separat gated |
| Carolin Hupp | PAUSED per Manuel17.11; keine Karte, Route, Suchtreffer oder öffentlichen Profildaten | NOT_APPROVED / PAUSED | ON_HOLD; kein Konto angelegt |

Hupps vorhandene Quellen/Profiltexte bleiben unverändert für eine spätere
ausdrücklich freigegebene Rückkehr erhalten. Kein Löschen einer fachlichen
Identität, kein neuer Ersatzdatensatz und kein personenbezogener Redirect.
Interne Gründe erscheinen nicht auf der Website. Die ursprüngliche Neuner-
Reviewmatrix ist ein historischer Fachnachweis, keine aktuelle Veröffentlichungsliste.

Ergebnis: acht aktive reale Preview-Profile; Produktion seit17.11 mit drei echten
Profilen und den sechs unverändert fiktiven Demo-Profilen. Produktions-Finder verwendet
ausschließlich Gülcans drei freigegebene Familien/fünf Formate. Der allgemeine
Finder und seine Navigation ändern keine inhaltlichen Rechte. Die übrigen24
Finder-Einträge bleiben Preview-only. Kein privates Registry-/Kalender-API.
Die separate11cb1ea-Freigabe und tatsächliche Veröffentlichung sind im
[Betriebsrecord](../operations/website-ionos-release-2026-11-17.md) geschlossen.
Jeder spätere neue Release braucht weiterhin seine eigene konkrete Freigabe.
