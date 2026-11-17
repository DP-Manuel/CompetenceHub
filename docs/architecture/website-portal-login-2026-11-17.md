# Website: Gemeinsamer Portal-Login

Stand 17.11.2026. LOCAL_READY; eigener Git-Abschluss gemäß Owner-Auftrag,
keine Veröffentlichung und keine Änderung an IONOS, Pages, VPS, Konten oder
Authentifizierung. EDV-Adresse fehlt. STOP bis zur EDV-Rückmeldung.

## Oberfläche und gemeinsamer Einstieg

`apps/website/src/components/PortalLogin.astro` verwendet das vorhandene `log-in`-
Icon und die D+P-Farben: dunkles Türkis/Weiß,44px-Mindestziel (tatsächlich46px),
sichtbarer Tastaturfokus und4px-Ecken. Desktop rechts neben der bestehenden
Kontaktaktion; mobil erster Menüeintrag. Bei engerem Header wechselt nur die
Variante mit Login früher ins native Menü; keine Überlagerung oder horizontale
Überbreite. Lange Menüs bleiben scrollbar und per Tastatur erreichbar.

Später führt genau ein normaler Link nach `/portal/` am bestätigten Backendhost.
Keine vorgeschaltete Rollenauswahl, kein `/login/intern`-Prototyp, kein lokales
Formular, Fetch/CORS, Token, Cookie oder neuer Sicherheitsmechanismus. Die
[bestehende Portal-App](../../apps/webapp/src/competence_hub_api/portal_ui/app.js)
steuert nach ihrer nativen Anmeldung/MFA die Admin-/Reviewer-/Coachansicht;
der [Backend-Mount](../../apps/webapp/src/competence_hub_api/main.py) bleibt unverändert.

## Genau Eine Spätere Konfiguration

Zentrale Auflösung in `apps/website/config/environment.mjs`:

| Einstellung | Verhalten |
| --- | --- |
| `WEBSITE_PORTAL_URL` fehlt/leer | Kein Login-Element und keine zugehörigen Styles in öffentlichen Builds |
| Bestätigte vollständige HTTPS-Adresse mit Pfad `/portal/` gesetzt | Desktop und Mobil erhalten denselben nativen Link; keine zweite Enable-Einstellung |
| `WEBSITE_PORTAL_DESIGN_PREVIEW=true` bei Astro dev | Ohne Zieladresse nur lokale Designschaltfläche, als noch nicht verfügbar beschriftet, ohne href/Anmeldeaktion |
| Derselbe Designschalter bei `astro build` | Wird ignoriert, sowohl Production als auch öffentliche GitHub-Vorschau; kein funktionsloser Link |

Keine feste, erratene oder lokale Pilotadresse als Fallback. Ungültige/non-HTTPS-
Adressen, Rollenprototypen, Anmeldedaten, Query-/Fragmenttokens und lokale Ziele
werden als Konfigurationsfehler abgewiesen, ohne den Inhalt in Fehlertexte zu
kopieren. `.env`-Dateien werden weiterhin nicht geladen. Nur die explizite
Build-/Dev-Konfiguration wird verwendet. Der URL-Wert ist später öffentliches
Linkziel, kein Ort für Passwörter oder andere Secrets.

### Aktivierung Nach EDV-Bestätigung

1. Die bestätigte vollständige HTTPS-Adresse mit dem gemeinsamen Backend-Einstieg
   `/portal/` übernehmen. Tatsächliches DNS, Zertifikat, Hostname und Zugriffsschutz
   prüfen; keine Pilotadresse oder Browserausnahme als Ersatz verwenden.
2. Im vorgesehenen Buildkontext **nur `WEBSITE_PORTAL_URL` setzen**. Desktop und
   Mobil müssen genau denselben nativen Einstieg ohne Rollen-, Token- oder
   Zugangsdatenparameter öffnen. Astro implementiert keine Anmeldung.
3. Lokal im Preview-Build Link, Tastatur und Mobilmenü prüfen. Am bestätigten
   Portal die vorhandenen HTTPS-/MFA-/Session-/Rollenprüfungen risikobasiert
   durchführen; keine echten Konten oder Einladungen nebenbei aktivieren.
4. Den Preview-Stand prüfen. Eine öffentliche GitHub-Pages-Veröffentlichung nur
   im autorisierten manuellen Workflow auslösen; ein Git-Push allein veröffentlicht
   nichts. Dieser Abschlussauftrag löst keinen Workflow aus.
5. Für IONOS ein neues Paket mit Manifest und SHA-256 vorbereiten und **separate
   Produktionsfreigabe** einholen. Danach Sicherung, Rückfallweg und Produktions-
   Smokes gemäß bestehendem SFTP-Runbook. Die frühere 11cb1ea-Freigabe gilt nicht
   für diesen neuen Release.

Das Setzen der Websiteadresse aktiviert keine Konten, Rollen oder Einladungen.

### Git- Und Veröffentlichungsgrenze

Vor dem Abschluss geprüft: GitHub Pages hat `build_type=workflow`; der einzige
Pages-Workflow `.github/workflows/pages-review.yml` verwendet ausschließlich
`workflow_dispatch`. Kein Push- oder indirekter automatischer Pages-Trigger,
keine eigenen Git-Hooks. Der separate Commit darf deshalb nach Owner-Auftrag
gepusht werden, ohne die Website neu zu veröffentlichen. Der letzte erfolgreiche
Pages-Lauf bleibt `44149446991`, Quelle `11cb1ea90fb5d72c38a5c9cd5c661285bcfdfbe5`.
Ohne Portaladresse sind Production 55/55 und Preview 59/59 Dateien auch im
abschließenden SHA-256-Vergleich unverändert; keine Portalmarker oder Platzhalter.

## Lokale Ansicht

Designadresse nach lokalem Start: `http://127.0.0.1:4327/kontakt/`. Der eigene
Testserver wurde zum Abschluss beendet. Kein Passwort nötig. Login ist bewusst
inaktiv, aber fokussierbar mit verständlicher Screenreader-Beschreibung und Tooltip.
Kein Anspruch auf eine bereits erreichbare EDV-Anmeldung. Der Dev-Toolbar ist in
dieser Designansicht ausgeblendet; keine Einstellung am Browser verändert.

Bei späterem ausdrücklich gewünschtem Designstart, Terminal **PowerShell**,
Arbeitsverzeichnis `apps/website`:

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\website'
$env:PATH = "..\..\tools\node-v22.16.0-win-x64;$env:PATH"
$env:ASTRO_TELEMETRY_DISABLED = '1'
$env:WEBSITE_ENV = 'production'
$env:WEBSITE_PORTAL_URL = ''
$env:WEBSITE_PORTAL_DESIGN_PREVIEW = 'true'
npm run dev -- --host 127.0.0.1 --port 4327
```

Bestehenden Server nicht doppelt starten. Erwartet: nur localhost4327; kein
SFTP/VPS-/Passwortdialog. Die Kontaktseite dient als lokale Header-Designansicht,
nicht als vollständige Portal-/Coachvorschau oder Anmeldeersatz.

## Tatsächliche Prüfung

- 41 Node-Vertragstests PASS, davon4 neue Portal-Konfigurationsfälle.
- 14 lokale Browserfälle PASS in Firefox und Edge:1440/1280/1241/1240/1100/768/
  390/320px, natives200%, Reduced Motion und ohne JavaScript. Normaler Fokus-/
  Tab-/Shift-Tab-/Enter-/Space-Verlauf, Menü öffnen/schließen, Kontaktlink,
  Textrechtecke/Zielgrößen und Kontrast mindestens4,5:1; keine Überlagerung.
- Zwei aktivierte Linkfälle verwenden ausschließlich ein abgefangenes synthetisches
  HTTPS-Ziel: kein DNS-/Backend-/Kontoaufruf, kein tatsächlicher Login behauptet.
- Zusätzlicher isolierter Production-Testbuild mit genau einer synthetischen
  URL-Konfiguration:34/34 HTMLseiten enthalten genau zwei korrekte gemeinsame
  Links, keinen Designzustand. Output nur unter ignoriertem lokalen `.tmp`,
  ausdrücklich kein Release-/Uploadpaket.
- Öffentliche Builds mit absichtlich gesetztem Designschalter: Production55/55
  bytegleich zum tatsächlich veröffentlichten Webroot; Preview59/59 bytegleich
  zum vorherigen Vorschauartefakt. Astro ohne Fehler/Warnungen/Hinweise,
  interne Referenzen1365/1398 PASS. Buildverifikation verbietet lokale/inaktive
  Loginmarker. Kein Backend-Gesamttest nötig.

Belege/Screenshots: `.tmp/portal-login-20261117/browser.json` und
`build-isolation.json`. Beide lokalen Testserver 4327/4328 sind beendet.
Kein manueller Screenreaderlauf, keine echte
EDV-/MFA-/Rollenabnahme neu durchgeführt; vorhandene Backendbelege gelten weiter.

**Nächster Block:** bestätigte EDV-Zieladresse gegen DNS/HTTPS und den vorhandenen
gemeinsamen Login prüfen; eine URL-Konfiguration plus getrennte Releasefreigabe.
Keine neue Anmeldung oder Benutzeraktivierung als Nebenwirkung.
