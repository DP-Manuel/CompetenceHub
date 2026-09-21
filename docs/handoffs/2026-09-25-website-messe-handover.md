# Website Messe-Handover

Stand: 21.09.2026

Zweck: secret-freie Uebergabe der statischen Competence-Hub-Website fuer den
kontrollierten Live-Test am 24.09. und einen stabilen Messestand am 17.10.
Dieses Handover autorisiert keinen Upload.

## Ziel und Grenzen

- Repository: `https://github.com/DP-Manuel/CompetenceHub.git`
- Branch: `main`
- Website: `apps/website`
- Kanonische Domain: `https://competencehub.donner-partner.de`
- Gemeldeter Webroot:
  `/kunden/homepages/16/d101506010/htdocs/competencehub`
- Read-only-Inventur: bestanden; SFTP-Chroot `/`, ausschliesslich
  `index.php` mit 64 Byte vorhanden
- Host-Key-Gate: ED25519-Fingerprint
  `SHA256:1gx2w8Rtv3wCgi7Jh8myf/KVd72cRQbow03UP8P095Q`
- Keine Portal-/API-Aktivierung, keine realen Konten, keine Echtdaten und keine
  SMTP-Aenderung im Website-Release.

## Vor jedem Upload

1. EDV bestaetigt, dass `phpinfo()` entfernt oder gesperrt ist.
2. SFTP-Fingerprint exakt vergleichen; die Inventur vom 21.09. zeigte nur die
   64-Byte-`index.php`-Diagnosedatei.
3. Bei neu hinzugekommenen Providerdateien, Symlinks oder `.htaccess` stoppen.
4. Die vorhandene `index.php` als datiertes Rollback-Artefakt sichern.
5. Nur ein sauberes, gehashtes und explizit freigegebenes Website-Artefakt
   verwenden.
6. Thomas-Go/No-Go und Manuels separate Uploadfreigabe dokumentieren.

## Lokaler Build

Aus `apps/website` in PowerShell:

```powershell
$env:PATH = "..\..\tools\node-v22.16.0-win-x64;$env:PATH"
npm run build
npm run verify:dist
```

Anschliessend aus dem Repository-Root:

```powershell
.\scripts\build-website-release.ps1
```

Erwartung: Build und Referenzpruefung gruen; Manifest meldet `dirty: false`,
`deployment_authorized: false`; ZIP-Hash stimmt mit dem Manifest ueberein.

## Upload und Sofort-Smoke

- Nur den Inhalt des freigegebenen `dist`-Artefakts in den bewiesenen Webroot
  uebertragen; keine unbekannte Remote-Datei blind loeschen.
- Danach HTTPS-Status, Seitentitel, Navigation, Bilder, Kontakt-Mailto,
  Kalender-Vorschau, zentrale D+P-Rechtslinks, Mobilansicht und Browserkonsole
  pruefen.
- HTTP soll auf HTTPS, die Bindestrich-Domain auf die kanonische Domain
  weiterleiten.
- Es darf weder `phpinfo()` noch ein Review-Banner oder oeffentlicher Loginlink
  sichtbar sein.

## Aktueller Clean-Kandidat

- Source: `a8d034c`
- Artefakt:
  `competence-hub-website-a8d034cef825-20260921T182550Z.zip`
- SHA-256: `15a1ae6b330f358afa97ae23205904fd83f097d2cb93af16cbf27d1466996300`
- Manifest: `dirty: false`, `deployment_authorized: false`

Vor einem spaeteren Website-Codewechsel wird dieser Kandidat verworfen und aus
dem neuen sauberen Source-Checkpoint erneut gebaut.

## Rollback und Stop-Regeln

- Bei falschem Webroot, unbekannter Providerkonfiguration, fehlenden Assets,
  5xx/403, Sicherheitsbefund oder unklarer Redirectschleife sofort stoppen.
- Das datierte Remote-Backup wiederherstellen, Kernrouten erneut pruefen und
  Befund sowie Uhrzeit protokollieren.
- Waehrend Manuels Abwesenheit keine Portal-, Datenbank-, Konto-, SMTP- oder
  Kalenderaktivierung mit diesem Runbook verbinden.

## Nach dem Live-Test

- Kleinere optische und redaktionelle Korrekturen duerfen kontrolliert
  nachgereicht werden.
- Vor der Messe am 17.10. nochmals Kernrouten, Mobilansicht, Kontaktweg,
  Zertifikat und Redirects pruefen.
- Der Backend-/Portal- und CAL-1-Stand bleibt bis zu einem eigenen Gate
  unveraendert.
