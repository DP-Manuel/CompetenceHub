# Website Messe-Readiness

Stand: 21.09.2026

Status: lokal technisch und als Clean-Artefakt gruen, Produktion durch externe
P0- und Freigabe-Gates gesperrt.
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
| P0 | Beide Produktionsdomains zeigen oeffentlich `phpinfo()` | EDV muss die Ausgabe vor Upload entfernen oder sperren; offen |
| P0 | Gemeldeter Webroot musste authentifiziert lesend bewiesen werden | bestanden: `/` als bestaetigter Chroot; nur 64-Byte-`index.php` vorhanden |
| P0 | Kein dokumentiertes Thomas-Go/No-Go und keine separate Remote-Change-Freigabe | vor Upload erforderlich |
| P1 | HTTP leitet nicht auf HTTPS um; Alias leitet nicht auf kanonische Domain um | bei EDV angefragt; offen |
| P1 | Sichtbarer Login fuehrte auf eine noch nicht produktive Vorschau | aus oeffentlicher Navigation entfernt |
| P1 | Kalender war nur ueber interne Prototyprouten erreichbar | ehrliche `/kalender/`-Vorschau ergaenzt und crawler-blockiert |
| P1 | Lokale Rechtsseiten behaupteten noch offene Betreiber-/Rechtsentscheidungen | auf bestaetigte zentrale D+P-Ziele umgestellt |
| P1 | Fehlendes Favicon erzeugte einen Browser-404 | lokales Marken-Favicon ergaenzt |
| P2 | Kein eigenes `og:image` | nach Live-Test mit freigegebenem Motiv nachziehen |

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
gebaut. Er bleibt bis zum Schliessen der externen P0- und Freigabe-Gates nicht
deployautorisiert.

## Go-Live-Stopper

1. Oeffentliche `phpinfo()`-Ausgabe entfernen oder sperren.
2. Vorhandene 64-Byte-`index.php` als Rollbackkopie sichern und erst mit
   separater Freigabe entfernen oder ersetzen.
3. Redirects oder einen dokumentierten Zwischenzustand bestaetigen.
4. Thomas-Go/No-Go und separate Uploadfreigabe dokumentieren.
5. Vor Replace datierte Remote-Sicherung erstellen; danach sofortige Smokes.

Kleinere optische oder textliche Korrekturen duerfen nach einem erfolgreichen
Live-Test nachgereicht werden. P0-Sicherheits-, Webroot- oder Rollbackbefunde
duerfen nicht auf nach dem Live-Test verschoben werden.
