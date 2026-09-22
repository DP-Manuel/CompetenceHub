# Website Messe-Readiness

Stand: 22.09.2026

Status: lokal technisch und als Clean-Artefakt gruen; der externe Diagnose-P0
ist geschlossen. Produktion bleibt durch Inhalts- und Freigabe-Gates gesperrt.
Ziel ist ein kontrollierter Live-Test am Donnerstag, 24.09.2026. Dieses
Dokument autorisiert keinen Upload.

## Releasegrenze

- Betreiber: Donner + Partner
- Verantwortlich: Lars Donner
- Rechtliche Ziele: zentrale D+P-Seiten fuer Impressum, AGB und Datenschutz
- Kanonische Domain: `https://competencehub.donner-partner.de`
- Redirectziel: HTTP auf HTTPS und Bindestrich-Domain auf die kanonische Domain
- Kalender: sichtbare, klar als Beispiel gekennzeichnete Vorschau; `noindex`
- Nicht enthalten: Portal-/API-Aktivierung, reale Konten, Echtdaten, SMTP oder
  produktive Kalenderangebote

## Befunde und Korrekturen

| Prioritaet | Befund | Massnahme / Status |
| --- | --- | --- |
| P0 | Beide Produktionsdomains zeigten oeffentlich `phpinfo()` | geschlossen 22.09.: Thomas Ross entfernte die temporaere `index.php`; alle vier HTTP/HTTPS-Varianten liefern `403` ohne Diagnoseausgabe |
| P0 | Gemeldeter Webroot musste authentifiziert lesend bewiesen werden | bestanden: `/` als bestaetigter Chroot; nur 64-Byte-`index.php` vorhanden |
| P0 | Kein dokumentiertes Thomas-Go/No-Go und keine separate Remote-Change-Freigabe | vor Upload erforderlich |
| P1 | HTTP leitet nicht auf HTTPS um; Alias leitet nicht auf kanonische Domain um | EDV erlaubt Umsetzung per `.htaccess`; Regeln sind im Artefakt enthalten, Produktionsnachweis folgt unmittelbar nach Upload |
| P1 | Sichtbarer Login fuehrte auf eine noch nicht produktive Vorschau | aus oeffentlicher Navigation entfernt |
| P1 | Kalender war nur ueber interne Prototyprouten erreichbar | ehrliche `/kalender/`-Vorschau ergaenzt und crawler-blockiert |
| P1 | Lokale Rechtsseiten behaupteten noch offene Betreiber-/Rechtsentscheidungen | auf bestaetigte zentrale D+P-Ziele umgestellt |
| P1 | Fehlendes Favicon erzeugte einen Browser-404 | lokales Marken-Favicon ergaenzt |
| P2 | Kein eigenes `og:image` | nach Live-Test mit freigegebenem Motiv nachziehen |
| Content | Siebtes Coach-Profil Guelcan Elmas-Brandes neu geliefert | Manuel gab Name, Text, Portraet, belegte berufliche Daten und Aufnahme in den Release am 22.09. frei; Metadaten-minimiertes Bild und Profil lokal gruen |

## Lokale Nachweise

- Astro-Produktionsbuild: 44 Dateien geprueft, 31 Seiten erzeugt
- Link-Gate: 1.233 interne Referenzen in 31 HTML-Dateien bestanden
- Messe-Browsergate: 722 Checks in Edge `153.0.4234.32` bestanden
- Ansichten: Desktop, Tablet, exakt 390 CSS-Pixel und 200-Prozent-Aequivalent
- Bedienung: Tastatur, Fokus, Mobile-Menue, Reduced Motion, FAQ, Coach-Laufband,
  Use Cases, Concept Clean, Kontaktweg und Kalender-Vorschau geprueft
- Routen: Start, Unternehmen, Leistungen, Mindforge, Businesscoaching, Coaches,
  sechs Coachprofile, Kalender, Ueber uns, Kontakt, lokale Rechtspfade und 404
- Sicherheit des Release-Archivs: 53 Eintraege, keine unsicheren Pfade,
  Pflichtdateien und Hash vorhanden

## Releasekandidat

- Source-Basis: `a8d034c`
- ZIP: `release-artifacts/website/competence-hub-website-a8d034cef825-20260921T182550Z.zip`
- SHA-256: `15a1ae6b330f358afa97ae23205904fd83f097d2cb93af16cbf27d1466996300`
- Manifest: gleichnamige JSON-Datei
- Kennzeichnung: `dirty: false`, `deployment_authorized: false`
- Archivpruefung: 53 Eintraege, keine unsicheren Pfade; `index.html`,
  `404.html`, `.htaccess` und `favicon.svg` vorhanden

Der Kandidat ist reproduzierbar und aus einem sauberen Source-Checkpoint
gebaut und bleibt als Rueckfalloption erhalten. Die freigegebene neue
Coach-Seite ist lokal separat geprueft; fuer den Upload wird nach Commit ein
neuer sauberer Kandidat gebaut.

## Go-Live-Stopper

1. Neuen sauberen Source-Checkpoint und exakten Releasekandidaten inklusive
   des freigegebenen Coach-Profils erstellen.
2. Unmittelbar vor dem Upload eine aktuelle Remote-Inventur und datierte
   Rollbacksicherung erstellen.
3. Nach Replace sofort HTTPS-, Alias-/Kanonisch-, Kernrouten-, Mobile-, Legal-
   und Kontakt-Smokes ausfuehren; bei Fehlern zurueckrollen.

Kleinere optische oder textliche Korrekturen duerfen nach einem erfolgreichen
Live-Test nachgereicht werden. P0-Sicherheits-, Webroot- oder Rollbackbefunde
duerfen nicht auf nach dem Live-Test verschoben werden.
