# Website Coach Privacy Correction

Stand: 24.09.2026

Status: lokal korrigiert, mit dem freigegebenen Portrait vollständig geprüft
und durch Manuel für Commit, Push und Korrektur-Deployment freigegeben.

## P0-Befund

Die seit 22.09.2026 öffentliche Website enthält sechs Coachidentitäten, die
nach Manuels neuer Messe-Freigaberegel nicht mehr personenbezogen veröffentlicht
werden sollen. Öffentliche Gegenproben bestätigten am 24.09.2026 HTTP 200 für
die Coachübersicht und beispielhafte alte Detailrouten.

## Korrekturgrenze

- Echte Profile: Herr Christian Galvano und Manuela Rodríguez, M.A.
- Fiktive Profile: Demoprofil 01 bis 06 mit sichtbarem Transparenzhinweis.
- Keine Änderung an Portal, API, Datenbank, Accounts, SMTP oder produktiven
  Kalenderangeboten.
- Das offizielle D+P-Advisory-Portrait von Frau Rodriguez ist seit 24.09.2026
  durch Manuel freigegeben. Die Website verwendet nur eine lokal verkleinerte,
  ohne Quellmetadaten neu kodierte WebP-Fassung.
- Keine personenbezogene Weiterleitung von entfernten Profilpfaden.

## Lokale Nachweise

- Astro: 41 Dateien, 0 Fehler, 0 Warnungen, 0 Hinweise.
- Produktionstypischer Build: 33 Seiten.
- Link- und Privacy-Gate: 1.302 interne Referenzen; keine entfernte Identität
  und kein alter Portraitpfad im Build.
- Microsoft Edge 153: 800/800 Checks über Desktop, Tablet, 390 CSS-Pixel,
  200-Prozent-Reflow, Tastatur/Fokus und Reduced Motion.
- Geprüft: zwei echte Profile, sechs sichtbare Demokennzeichnungen,
  KI-Filter, Manuela-Detailseite, Demo-Detailseite, Kalenderidentitäten und
  kontrollierte 404-Antworten für alle sechs entfernten Routen.
- Das freigegebene Portrait wird als lokal neu kodierte WebP-Datei mit
  1.200 x 1.200 Pixeln geladen; die Browserprüfung bestätigt die natürlichen
  Bildmaße.
- Visuelle Sichtprüfung: Coachübersicht und Manuela-Profil auf Desktop und
  390-Pixel-Mobilansicht ohne Überlauf oder überdeckte Inhalte; jeweils
  `0 px` horizontaler Überlauf.
- SFTP-Rehearsal-Regression: 8/8 fokussierte Tests bestanden.

## Release-Regel

Manuel erteilte die separate Freigabe für Bild, Commit, Push und
Korrektur-Deployment am 24.09.2026. Nach Commit und Push muss aus dem sauberen
Commit ein neues `dirty: false`-Artefakt gebaut werden. Das aktuell produktive
Archiv darf wegen der neuen
Freigabeentscheidung nicht als Rollbackziel für Coachinhalte verwendet werden.

Rollback ist für diesen P0 als datensparsame Reparatur auszuführen: zuerst das
exakte korrigierte Artefakt erneut vollständig hochladen. Ist das nicht
möglich, muss die Website beziehungsweise mindestens ihre personenbezogene
Coachdarstellung vorübergehend fail-closed deaktiviert werden. Das Remote-
Backup des 22.09.-Stands dient nur der technischen Beweissicherung und darf
nicht wieder öffentlich aktiviert werden.

Ein lokales Prüfarchiv wurde aus dem uncommitted Stand erzeugt:

- Datei: `competence-hub-website-53a89a8442dd-20260924T055419Z-dirty.zip`
- Einträge: 51
- SHA-256: `cb928eaa61d38f3ebffec590c26427decf3900bdcdd6249254b0859bdcc8784d`
- Manifest: `dirty: true`, `deployment_authorized: false`

Dieses Archiv belegt Reproduzierbarkeit und Inhalt, ist aber ausdrücklich kein
Produktionskandidat.
