# Veranstaltungsorte · Würzburg

Rein öffentliche GitHub-Pages-Vorschau. Die Standortseite ergänzt Coaching,
Workshops und Seminare; sie bietet keine Raumvermietung, Buchung oder
Zusage von Verfügbarkeit. IONOS, Portal, Kalender-API und Coach-Rollout
bleiben unverändert.

## Inhalt Und Bildauswahl

Der Owner bestätigte Würzburg als Region und erteilte die Foto-Freigabe für
die Vorschau. Alle 14 Originale wurden gesichtet und unverändert erhalten.
Veröffentlicht werden zwölf Ansichten: Tischinsel und offene Tischordnung,
Seminaransichten mit Tischreihen, kleiner Besprechungstisch, Vortragsreihen,
U-Form und weitere Perspektiven. Zwei gleich zuordenbare Seminarfotos
bleiben zusammen; bei den übrigen Varianten wurde keine Raumgleichheit
unterstellt. Zwei Motive mit ausdrücklichem Absprachevermerk in den
Quelldaten sind bis zum Nachweis der weiteren Bedingungen ausgeschlossen.

Fünf Ansichten stehen direkt in der Galerie, sieben weitere hinter einer
nativen Aufklappfunktion. Die Unternehmensseite zeigt nur drei Vorschaufotos
nach den Leistungswelten. Workshop-Themen und Leistungsübersicht verweisen
auf die Standortseite, ohne konkrete Angebots- oder Raumzuordnungen zu
behaupten. „Workshop in Würzburg anfragen“ setzt ausschließlich ein bekanntes
Thema im vorhandenen lokalen E-Mail-Entwurf voraus; kein Versand und keine
Speicherung.

## Datenmodell Und Veröffentlichung

- `src/data/venues.mjs`: Stadt → bestätigter Veranstaltungsort → Raum → Foto
  mit sichtbarer Bestuhlungsvariante und möglichen Formatbezügen. Für
  Würzburg sind die Raumansichten ohne bestätigte Gebäude- oder
  Betreiberzuordnung gespeichert; keine erfundenen Eigennamen.
- Ein weiterer Ort erfordert bestätigte Region, Zuordnung, nutzbare Medien,
  Alternativtexte und Freigabe. Weitere Städte werden durch freigegebene
  Datensätze ergänzt; erst ab zwei Städten erscheinen Sprunglinks.
- `src/media/venues/`: 72 abgeleitete WebP-/JPEG-Dateien in 480, 960 und
  1800 px, ohne EXIF, IPTC oder XMP. Die zwölf Originale umfassen 52,1 MB,
  alle Varianten zusammen 6,77 MB. Pro Bild lädt der Browser eine passende
  Variante; nur das Leitbild erhält hohe Priorität.
- Die getrennte Medien-Allowlist und der Routen-/Linktest schließen die
  Standortseite und Bilder aus dem Produktionsbuild aus. Die Vorschau
  bleibt nicht indexierbar, erhält ein Raumfoto als Open-Graph-Bild und
  verlinkt nicht kanonisch auf eine nicht vorhandene IONOS-Unterseite.

**Nächstes IONOS-Gate:** Produktionsumfang mit dem Zwei-Profil-Marketingstart
abgleichen. Standortseite und Bilder, Rechtebedingungen, bereinigten
Rückfallstand sowie Übernahme separat freigeben. Offene Sachangaben:
offizielle Raumnamen, Gebäude, Betreiber, Ausstattung, Kapazität, Preise,
Verfügbarkeit und bestätigte Workshop-Zuordnungen.
