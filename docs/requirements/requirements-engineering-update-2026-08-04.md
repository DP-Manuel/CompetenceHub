# Requirements Engineering Update 2026-08-04

## Anlass

Neue freigegebene Coach-Unterlagen und visuelles Stakeholderfeedback erweitern
den Website-Stand. Private Rohunterlagen, Kontaktdaten, Nachweise und
Kundenreferenzen werden nicht in diese abstrahierte Projektanforderung
übernommen.

## Verbindliche Entscheidungen

- Mindforge ist im zentralen Hub der Oberbegriff für Life Coaching und
  Businesscoaching. Der separate Businesscoaching-Knoten entfällt, damit die
  Startseiten-Map acht Außenknoten in einer ruhigeren Komposition zeigt.
- Die eigenständige Businesscoaching-Seite bleibt erreichbar und wird von der
  Mindforge-Seite direkt verlinkt.
- Coach-Namen werden in sichtbaren Website-Texten mit Anrede geführt:
  Herr Christian Galvano, Frau Elisabeth Schwabauer, Frau Carolin Hupp,
  Herr T. Wegner-Ney, Herr Goran Celic und Frau Dr. Stefanie Becker.
- Die persönliche Kontaktperson wird als Frau Janay Rappelt bezeichnet.
- Mediation ist ein allgemeiner möglicher Kompetenzbereich des Coach-Netzwerks.
  Ein Coach darf diesem Bereich nur nach ausdrücklich belegter Qualifikation
  und fachlicher Freigabe zugeordnet werden.
- Frau Dr. Stefanie Beckers Profil ist für die Website freigegeben.
  Kundenreferenzen bleiben vorerst ausgeschlossen. Ein Porträt wird nicht aus
  dem gelieferten Profil-PDF extrahiert.
- Herr T. Wegner-Neys öffentliches Profil wird um Technologie- und
  Prozessveränderung, Qualitätsmanagement, Mitarbeiterbeteiligung, Führung und
  Fachkräftesicherung erweitert. KI darf als konkrete Technologie vorkommen,
  bleibt aber ein Nebenthema.

## Funktionale Anforderungen

1. Der zentrale Hub zeigt acht Außenknoten und keinen separaten
   Businesscoaching-Knoten.
2. Der Mindforge-Knoten und die Mindforge-Seite benennen Life Coaching und
   Businesscoaching gemeinsam; die vorhandene Businesscoaching-Seite bleibt
   direkt erreichbar.
3. Die Coach-Übersicht enthält Frau Dr. Stefanie Becker als sechstes Profil und
   eine eigene Profilseite ohne Kundenreferenzen.
4. Herr T. Wegner-Neys Listen- und Detailprofil spiegeln den neuen
   Portfolio-Schwerpunkt wider.
5. Der Themenfilter enthält Mediation. Solange kein Profil qualifiziert und
   freigegeben zugeordnet ist, zeigt die Auswahl einen verständlichen
   Leerzustand statt einer erfundenen Zuordnung.
6. Nach Auswahl eines Coach-Themas scrollt die Seite zum sichtbaren
   Ergebnisstatus. Das gewählte Thema und die Zahl passender Profile bleiben
   dort erkennbar.
7. Die drei bisherigen Qualitätskarten auf der Coach-Seite entfallen.
8. FAQ-Köpfe erhalten mehr vertikalen Raum, damit längere Fragen nicht gedrängt
   wirken.

## Qualitäts- und Sicherheitsanforderungen

- Keine privaten Kontaktdaten, Zeugnisse oder Kundenreferenzen veröffentlichen.
- Keine Mediationsqualifikation aus Konfliktmanagement oder ähnlichen Themen
  ableiten.
- Vor öffentlicher Veröffentlichung Profiltexte, Rechte und sichtbare
  Darstellung nochmals prüfen.
- Themenfilter bleiben per Tastatur bedienbar, kommunizieren Statusänderungen
  über eine Live-Region und respektieren reduzierte Bewegung beim Scrollen.
- Desktop- und Mobilansicht müssen ohne Textüberlauf oder abgeschnittene
  Hub-Knoten geprüft werden.

## Abnahmekriterien

- Astro Check meldet keine Fehler, Warnungen oder Hinweise.
- Der statische Build erzeugt die neue Route `/coaches/stefanie-becker/`.
- Startseite, Coach-Übersicht, Frau Dr. Stefanie Beckers Profil,
  Herr T. Wegner-Neys Profil, Mindforge und Kontakt liefern lokal HTTP 200.
- Die Startseite enthält acht Hub-Außenknoten und kein Element mit
  `data-node="businesscoaching"`.
- Der Mediationsfilter besitzt einen nachvollziehbaren Leerzustand ohne
  unqualifizierte Coach-Zuordnung.
- Öffentliche Veröffentlichung bleibt ein separater, ausdrücklich
  freizugebender Schritt.
