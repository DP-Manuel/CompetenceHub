# Competence Hub - Projektübergabe für eine andere KI

Grundstand: 2026-07-30
Planungsnachtrag: 2026-08-11 (PWA-first; keine Implementierung)

Zweck: Diese Datei ist der kompakte, aber vollständige Einstieg für eine
weitere KI, die das Frontend analysieren, ein neues Gestaltungskonzept
ausarbeiten oder präzise Umsetzungsaufträge formulieren soll.

Die Datei enthält keine Zugangsdaten, Secrets, privaten Quelldokumente oder
vertraulichen Coach-Unterlagen.

## 1. Kurzfassung

- Projekt: `Competence Hub`
- Lokaler Pfad:
  `C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website`
- Repository: `https://github.com/DP-Manuel/CompetenceHub`
- Branch: `main`
- Website: statische Astro-Website in `apps/website`
- Öffentliche Review-URL:
  `https://dp-manuel.github.io/CompetenceHub/`
- Review-Deployment: nur manuell über GitHub Actions
- Aktuelle Produktphase: Frontend- und Inhaltsreview nach dem Website-MVP
- Hauptzielgruppen: Unternehmen und Privatpersonen
- Dachmarke: `Competence Hub`
- Angebotsbereich: `Mindforge` für Life Coaching
- Kein WordPress, kein Backend, keine Datenbankanbindung, keine echte
  Authentifizierung und keine echte Online-Buchung

Der bisher öffentlich veröffentlichte Review-Build basiert auf Commit
`a33ff12`. Ein Push auf `main` veröffentlicht nicht automatisch. Für eine
aktualisierte öffentliche Vorschau muss der manuelle Workflow
`Publish GitHub Pages review` ausdrücklich gestartet werden.

## 2. Produktidee und Positionierung

Der Competence Hub ist keine offene Coaching-Plattform und kein automatischer
Marktplatz. Er soll Unternehmen und Privatpersonen mit passender Expertise,
geeigneten Formaten und einer persönlichen Ansprechpartnerin verbinden.

Kernlogik:

```text
Anliegen -> Klärung -> passende Expertise -> passendes Format -> nächster Schritt
```

Zentrale Nutzenidee:

- Das Anliegen steht vor dem Produkt.
- Coaches werden kuratiert, nicht als endloser Katalog dargestellt.
- Die Verbindung zwischen Bedarf, Coach und Format wird persönlich begleitet.
- Janay Rappelt ist als vermittelnde Kontaktperson zwischen Unternehmen und
  Coaches vorgesehen. Ein vollständiges Profil und Foto liegen noch nicht vor.

## 3. Aktuell dargestellte Leistungsbereiche

### Competence Hub

- Coaching und Beratung für Unternehmen
- Businesscoaching
- Recruiting und Personalentwicklung
- Assessment Center für Personalauswahl und Entwicklung
- psychologische Beratung und Prävention
- Supervision, Workshops und Vorträge
- kuratiertes Coach-Netzwerk

### Mindforge

Mindforge ist ein eigener Angebotsbereich innerhalb des Competence Hub:

- Life Coaching, nicht „Livecoaching“
- Resilienz
- Mindset
- persönliche und berufliche Entwicklung
- Angebote für Privatpersonen und Unternehmen
- Präsenz, online oder hybrid
- kostenfreies Erstgespräch von 15 bis 20 Minuten
- 90-minütige Intensiv-Sessions
- Übungen, Arbeitsmaterialien und Transferimpulse

Die veröffentlichten Mindforge- und Assessment-Center-Preise sind fachlich
freigegeben und in
`docs/requirements/requirements-engineering-update-2026-07-29.md`
dokumentiert.

Wichtige Grenze:

- Mindforge ist Life Coaching.
- Über den Competence Hub wird aktuell keine Psychotherapie angeboten.
- Die Website darf kein Therapieversprechen formulieren.

## 4. Was die Website aktuell kann

### Technisch

- statische Seiten mit Astro erzeugen
- responsive Desktop-, Tablet- und Mobilansichten
- eigene Meta-Titel und Meta-Descriptions pro Seite
- zentrale Navigation mit Leistungs-Dropdown
- mobile Navigation über native `details`/`summary`
- interne, GitHub-Pages-kompatible Links mit dynamischem Base-Pfad
- interaktive Hub-Grafik mit Hover, Tastaturfokus und Klickzielen
- scrollabhängige Hub-Journey mit sichtbarer Fallback-Darstellung
- reduzierte Bewegungen bei `prefers-reduced-motion`
- manuell auslösbaren GitHub-Pages-Review-Build erzeugen

### Nicht vorhanden

- kein Backend
- keine API
- keine Datenbankverbindung
- keine Benutzerkonten
- keine echte Anmeldung
- keine Formularübertragung oder Speicherung
- keine Terminbuchung
- keine Coach-Kalender
- kein CMS
- kein automatisches Matching
- keine Vertrags- oder Rechnungsautomatisierung

Loginseiten und Kontaktformular sind sichtbare Strukturvorschauen. Sie dürfen
nicht als produktive Funktion beschrieben werden.

## 5. Aktuelle Seiten

| Route | Zweck und aktueller Inhalt |
| --- | --- |
| `/` | Startseite mit zentralem Connected-Core-Hub, anklickbaren Themenknoten, scrollender Journey, Coach-Spotlight und Kontakt-CTA |
| `/leistungen` | Gesamtübersicht für Mindforge, Businesscoaching, Recruiting, Assessment Center, Gesundheit und Gruppenformate |
| `/mindforge` | Hauptseite für Life Coaching, Formate, Prozess, offizielle B2C-/B2B-Preise, Assessment-Verbindung und Therapieabgrenzung |
| `/lifecoaching` | erklärende Life-Coaching-Seite mit Einsatzfeldern, Vorgehen und fachlicher Grenze |
| `/livecoaching` | Kompatibilitätsseite; erklärt, dass Life Coaching jetzt unter Mindforge geführt wird |
| `/businesscoaching` | Führung, Teams, Kommunikation, Rollenklärung und Veränderung |
| `/unternehmen` | B2B-Einstieg, Anlässe, Assessment Center, Auswahl/Entwicklung, Prozess und FAQ |
| `/coaches` | kuratiertes Coach-Netzwerk mit vier vorhandenen Profilen |
| `/coaches/christian-galvano` | Coach-Profil für Leadership, Konflikt, Stress- und Burnoutprävention |
| `/coaches/carolin-hupp` | Coach-Profil für Gesundheitsförderung, Bewegung, Prävention und Entspannung |
| `/coaches/elisabeth-schwabauer` | Psychologin; Beratung, psychische Belastung, Team- und Konfliktklärung; kein Therapieangebot |
| `/coaches/wegner-ney` | Workshops und Vorträge zu Führung, Teamstärkung, Recruiting und Personalentwicklung; KI-Angebote wurden bewusst nicht übernommen |
| `/kontakt` | statische Anfragevorschau für Unternehmen und Privatpersonen; keine Übertragung |
| `/login` | Vorschau geplanter Bereiche für internes Team, Coaches und Unternehmen |
| `/login/intern` | statische Vorschau für den späteren internen Bereich |
| `/login/coaches` | statische Vorschau für einen späteren Coach-Bereich |
| `/login/unternehmen` | statische Vorschau für einen späteren Unternehmensbereich |
| `/impressum` | lokale Hinweis-/Platzhalterseite mit Link zum zentralen Donner-Partner-Impressum |
| `/datenschutz` | lokale Hinweis-/Platzhalterseite mit Link zum zentralen Datenschutz |
| `/seminare` | entschärfte Archiv-/Perspektivseite, nicht Hauptnavigation |
| `/qualifizierung` | entschärfte Archiv-/Perspektivseite, nicht Hauptnavigation |
| `/system` | klar gekennzeichneter späterer Systemausblick |

Footer-Rechtslinks:

- `https://donner-partner.de/dp/impressum/`
- `https://donner-partner.de/dp/datenschutz/`
- `https://donner-partner.de/dp/agb/`

Öffentliche Kontaktadresse:

- `competencehub@donner-partner.de`

## 6. Zentrale Frontend-Elemente

### Connected Core

Datei: `apps/website/src/components/CompetenceHubMap.astro`

- großer zentraler Competence-Hub-Kreis als Startknoten
- kleinere Knoten für Unternehmen, Coaches, Leistungen, Recruiting, Kontakt,
  Mindforge, Businesscoaching, Gesundheit sowie Workshops/Vorträge
- Verbindungen werden bei Hover, Fokus oder Aktivierung sichtbar
- Außenknoten sind echte Links
- Mobil wird die Grafik stabiler und einfacher dargestellt
- keine Behauptung von automatischem Matching

### Hub Journey

Datei: `apps/website/src/components/HubJourney.astro`

- vier Schritte: Anliegen, Expertise, Format, Begleitung
- alle vier Kreise sind klickbar
- Ziele: Unternehmen, Coaches, Leistungen und Kontakt
- Desktop: haftende Grafik mit scrollabhängig aktivem Schritt
- Mobil: normale Lesereihenfolge ohne unzugängliche Animation

### Mindforge-Signal

Datei: `apps/website/src/pages/mindforge.astro`

- zentraler Mindforge-Kreis
- Satelliten: Resilienz, Mindset und Entwicklung
- Satelliten berühren den Kern nur an der Kontur und überlagern ihn nicht
- die Darstellung skaliert proportional

### Buttons

Datei: `apps/website/src/styles/global.css`

- Primärbutton: Kaminrot/Orange mit dunkler Schrift
- Sekundärbutton: Weiß mit türkiser Kontur
- Sekundärbutton wird bei Hover oder Tastaturfokus orange
- in Primär-/Sekundärgruppen wird der Primärbutton gleichzeitig weiß
- einzelne Buttons behalten Orange und erhalten eine sichtbare türkise
  Hover-/Fokusbetonung
- das Verhalten gilt projektweit für vorhandene Button-Gruppen, Coach-CTAs,
  Header-CTA und Formularbutton

### Mindforge-Prozess

- vier nummerierte Schritte auf einer horizontalen Linie
- Nummer: orange Innenfläche, weißer Rahmen, dünne türkise Außenlinie
- zusätzlicher Abstand zwischen Nummernkasten und Text
- mobil wird daraus eine vertikale Timeline

## 7. Designsystem

Verbindliche digitale Arbeitsgrundlage:

`docs/assets/designstyle.md`

Kurzfassung:

- viel Weiß und helle Ruheflächen
- Pantone-Türkis als Rahmen, Linie, Icon und Orientierung
- Kaminrot/Orange als aktiver Akzent
- Dunkelgrau für normalen Text
- Gelb nur sehr sparsam
- klare Raster und begrenzte Inhaltsbreite
- kleine Kartenradien, meist 0 bis 8 Pixel
- zurückhaltende Schatten
- keine dekorativen Farbblasen oder generische Startup-Optik
- keine vollflächige Türkis-auf-Türkis- oder Orange-auf-Orange-Komposition
- Inhalte bevorzugt über Symbole, kurze Aussagen, Prozesse und scanbare
  Module vermitteln
- Kreise sind für Hub, Beziehungen und Menschen vorgesehen
- Rechtecke/Karten strukturieren Leistungen, Preise und Prozesse

Farbrollen:

| Rolle | Wert |
| --- | --- |
| Pantone-Türkis | `#009CA6` |
| Kaminrot/Orange | `#FF7F57` |
| kontraststärkeres Orange für kleinen Text | `#C14D2C` |
| Dunkelgrau | `#333132` |
| Gelb | `#FFB758` |
| Weiß | `#FFFFFF` |
| helle Ruhefläche | `#F3F8F8` |
| Trennlinie | `#D8E4E5` |

Wichtige Kontrastregel:

Die Markenfarben sind nicht in jeder Kombination für kleinen Text geeignet.
Normaler Text bleibt dunkelgrau. Lesbarkeit und Barrierefreiheit haben Vorrang
vor einer rein dekorativen Farbanwendung.

Responsive Breakpoints im aktuellen CSS:

- `980px`
- `640px`
- `420px`

## 8. Technischer Stack

```text
Astro                5.18.2
TypeScript           6.0.3
@astrojs/check       0.9.9
Rendering            statisch
Frontend-JavaScript  klein, nativ und komponentennah
Styling              ein zentrales global.css
WordPress            nein
Frontend-Framework   keines zusätzlich
Backend              keines
```

Scripts in `apps/website/package.json`:

```text
npm run dev      Astro-Dev-Server auf 127.0.0.1
npm run build    astro check && astro build
npm run preview  statische Astro-Vorschau
```

Lokale Entwicklung:

```powershell
cd C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\website
$env:PATH = "..\..\tools\node-v22.16.0-win-x64;$env:PATH"
$env:ASTRO_TELEMETRY_DISABLED = "1"
npm run dev
```

Build:

```powershell
cd C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\website
$env:PATH = "..\..\tools\node-v22.16.0-win-x64;$env:PATH"
$env:ASTRO_TELEMETRY_DISABLED = "1"
npm run build
```

Letzter geprüfter Build vor dieser Übergabe:

- 27 Astro-Dateien geprüft
- 0 Fehler
- 0 Warnungen
- 0 Hinweise
- 22 statische Seiten erzeugt

Windows-Hinweis:

Astro/Vite kann in einer Sandbox mit `EPERM`, AppData- oder `spawn`-Fehlern
scheitern. Dann denselben Build mit deaktivierter Telemetrie beziehungsweise
nach Freigabe außerhalb der Sandbox prüfen, bevor der Code als fehlerhaft
bewertet wird.

## 9. Projektstruktur

Sensible und generierte Bereiche sind bewusst nicht vollständig aufgelistet.

```text
Website/
├─ .github/
│  └─ workflows/
│     └─ pages-review.yml
├─ apps/
│  ├─ website/
│  │  ├─ public/
│  │  │  └─ images/
│  │  │     └─ coaches/
│  │  ├─ scripts/
│  │  │  └─ serve-dist.mjs
│  │  ├─ src/
│  │  │  ├─ components/
│  │  │  │  ├─ CompetenceHubMap.astro
│  │  │  │  ├─ HubJourney.astro
│  │  │  │  └─ Icon.astro
│  │  │  ├─ layouts/
│  │  │  │  └─ BaseLayout.astro
│  │  │  ├─ pages/
│  │  │  │  ├─ coaches/
│  │  │  │  ├─ login/
│  │  │  │  └─ *.astro
│  │  │  └─ styles/
│  │  │     └─ global.css
│  │  ├─ astro.config.mjs
│  │  ├─ package.json
│  │  ├─ package-lock.json
│  │  ├─ README.md
│  │  └─ tsconfig.json
│  └─ webapp/
│     └─ README.md
├─ docs/
│  ├─ architecture/
│  │  ├─ initial-data-model.md
│  │  └─ server-database-bootstrap.md
│  ├─ assets/
│  │  ├─ brand-design-notes.md
│  │  └─ designstyle.md
│  ├─ decisions/
│  ├─ design/
│  ├─ requirements/
│  └─ research/
├─ new-project-starter/
├─ scripts/
│  └─ codexskills-update-check.ps1
├─ AGENTS.md
├─ CHATGPT_PROJECT_BRIEF.md
├─ MEETINGS.md
├─ PROJECT_AI_POLICY.md
├─ PROJECT_LOG.md
├─ PROJECT_PLAN.md
├─ PROJECT_STATUS.md
├─ README.md
└─ SKILL_FEEDBACK_LOG.md
```

Absichtlich nicht darstellen oder verarbeiten:

- `Quellen/`
- `.tmp/`
- `.git/`
- `.env` und `.env.*`
- `node_modules/`
- `dist/`
- `.astro/`
- lokale portable Node-Binärdateien

## 10. Öffentliche Bildressourcen

Aktuell im Website-Projekt:

```text
apps/website/public/images/
├─ start.png
├─ firmenseminare.png
├─ qualifizierung.png
├─ vermittlung.png
├─ recruiting.png
├─ partnerschaft.png
├─ digitale-lernplattform.png
└─ coaches/
   ├─ christian-galvano.webp
   ├─ elisabeth-schwabauer.webp
   └─ wegner-ney.jpg
```

Nicht jedes ältere Bild wird im aktuellen Frontend prominent verwendet.
Bildrechte, Freigabe und inhaltliche Passung müssen vor Produktionsnutzung
weiterhin geprüft werden. Keine Bilder aus Quelldokumenten extrahieren oder
ohne Freigabe neu veröffentlichen.

## 11. Navigation

Desktop:

- Start
- Leistungen als Dropdown
- Für Unternehmen
- Coaches
- Login
- CTA `Bedarf besprechen`

Leistungs-Dropdown:

- Alle Leistungen
- Mindforge · Life Coaching
- Businesscoaching
- Recruiting & Personalentwicklung
- Psychologische Beratung & Prävention
- Supervision, Workshops & Vorträge

Mobil:

- native aufklappbare Navigation
- dieselben inhaltlichen Ziele
- Kontakt und Login zusätzlich im Menü

## 12. Kontakt und Recht

- Öffentliche E-Mail: `competencehub@donner-partner.de`
- Das Formular ist rein statisch.
- Es werden aktuell keine Formulardaten übertragen, gespeichert oder
  verarbeitet.
- Kein Secret oder Mailprovider ist eingebunden.
- Impressum, Datenschutz und AGB verlinken auf die Mutterseite.
- Die konkrete verantwortliche Rechtseinheit und die Anwendbarkeit der
  zentralen Rechtstexte müssen vor dem finalen Livegang bestätigt werden.
- Die GitHub-Pages-Seite ist eine öffentliche Review-Version, kein privater
  Testraum.

## 13. GitHub Pages und Deployment

Workflow:

`.github/workflows/pages-review.yml`

Eigenschaften:

- nur `workflow_dispatch`
- kein automatischer Deploy bei Push
- Buildpfad `apps/website`
- Review-Umgebungsvariablen:
  - `GITHUB_PAGES_REVIEW=true`
  - `PUBLIC_REVIEW_MODE=true`
- sichtbarer Review-Banner
- `noindex, nofollow, noarchive`
- Base-Pfad `/CompetenceHub`

Review-URL:

`https://dp-manuel.github.io/CompetenceHub/`

Wichtig:

- Ein Push aktualisiert die öffentliche Seite nicht.
- Ein manueller Workflow-Lauf ist ein echtes öffentliches Deployment und
  benötigt eine ausdrückliche Freigabe.
- Die finale Domain und der spätere Produktivserver sind noch nicht bestätigt.

## 14. Webapp-, Login- und Datenbankstatus

`apps/webapp` ist nur ein reservierter Arbeitsbereich.

Vorbereitet:

- erste Architekturhinweise
- ein initiales Datenmodell
- Server-/Datenbank-Bootstrap-Dokumentation
- Rollenidee für internes Team, Coaches und Unternehmen
- Platzhalterkonfiguration für eine spätere lokale Umgebung

Nicht entschieden oder umgesetzt:

- Backend-Sprache und Framework
- API
- ORM/Migrationswerkzeug
- Authentifizierung
- Autorisierung
- Datenbankinstallation
- Serverkonfiguration
- Backup und Restore
- TLS/Reverse Proxy
- produktive Benutzerrollen

Architekturgrenze:

Die öffentliche Astro-Website darf niemals direkt auf MySQL/MariaDB zugreifen.
Ein späteres Backend muss Datenbankzugriff, Rollen, Validierung, Audit und
Datenschutz kapseln.

Serverstatus:

- kein Serverlogin in diesem Arbeitsstand
- keine Serveränderung
- IT-Rückmeldung zu Hosting, Laufzeit und Datenbankdetails steht noch aus
- keine Zugangsdaten in Git, Dokumentation oder KI-Chat übernehmen

## 15. Geplante spätere Ausbaustufen

- interner Login für Manuel und Kollegin
- später Coach- und Unternehmenszugänge
- Firmenfeedback
- Coach-Kalender
- mögliche Outlook-Booking-Integration
- Buchungssystem
- Vertragsautomatisierung
- Benachrichtigungen an Kollegin/Buchhaltung
- Aufträge, Termine und Rechnungen
- spätere installierbare Webapp als PWA-first; native Android-/iOS-Clients
  bleiben optional und bedarfsabhängig
- editorfreundliche Inhaltspflege ohne Git für nichttechnische Kolleginnen

Diese Punkte gehören nicht in den aktuellen statischen Frontend-Slice.

## 16. Aktuelle offene Punkte

### Inhalt und Freigabe

- weiteres Coach-Profil beziehungsweise Daten für insgesamt etwa fünf Coaches
- Zitat, Formate, Einsatzregion und Verfügbarkeit für Elisabeth Schwabauer
- finale Freigaben und Bildrechte für alle Profile
- vollständiges Profil und Foto für Janay Rappelt
- freigegebene Referenzen, Kennzahlen oder Kundenbeispiele
- abschließende Formulierungen zu psychologischer Beratung und Supervision

### Betrieb und Recht

- verantwortliche Donner-Partner-Rechtseinheit
- finale Domain
- Freigabe von Impressum, Datenschutz und AGB
- Verantwortlichkeit und Reaktionsprozess für die öffentliche Mailbox
- Serverzweck: Entwicklung, Staging oder Produktion
- Hosting-Laufzeit, Datenbanktyp und Version
- Backup-, Restore- und Wartungsverantwortung

### Frontend

- neues mögliches Gesamtkonzept wird von einer weiteren KI vorbereitet
- aktuelles Frontend zuerst als Referenz und Vergleichsbasis bewerten
- keine funktionierende Interaktion oder fachlich freigegebene Information
  versehentlich zurückbauen
- finaler Content-Proofread
- abschließende echte Browser-/Geräteprüfung
- Canonical URL und strukturierte Daten erst mit finaler Domain abschließen

## 17. Sicherheitsgrenzen für jede weitere KI

Nicht öffnen, lesen, listen, indexieren oder übertragen:

- `C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\Quellen`
- Zugangsdaten-Dokumente
- `.env` oder `.env.*`
- Passwörter, Tokens, SSH-Schlüssel, API-Schlüssel oder Sessiondaten
- private Coach-, Kunden-, Vertrags- oder Personaldaten
- `.tmp/`

Weitere Regeln:

- keine Secrets in Code oder Dokumentation schreiben
- keine sensiblen Daten an externe Dienste senden
- keine externen Provider ohne Freigabe
- kein OpenRouter
- kein Hermes
- keine GitHub-Actions-Secrets lesen
- kein Deployment ohne ausdrückliche Freigabe
- `.tmp/` niemals committen
- keine echte Backendfunktion vortäuschen
- keine Demo-Zugangsdaten veröffentlichen
- keine privaten Quelldokumente in Git übernehmen

Die sicheren, bereits abstrahierten Requirements in `docs/requirements` sollen
anstelle der privaten Quelldokumente verwendet werden.

## 18. Arbeitsregeln für Frontend-Anpassungen

1. Zuerst `AGENTS.md`, diese Datei und `docs/assets/designstyle.md` lesen.
2. Danach `PROJECT_STATUS.md` und den neuesten Eintrag in `PROJECT_LOG.md`
   prüfen.
3. Nur sichere Dateien außerhalb der gesperrten Bereiche verwenden.
4. Bestehenden Astro-Stack und aktuelle Komponentenlogik respektieren.
5. Kein Framework und keine Abhängigkeit ohne klaren Nutzen hinzufügen.
6. Neues Konzept zuerst lokal umsetzen.
7. Desktop und Mobil visuell prüfen.
8. Hover, Tastaturfokus, Kontrast, Textumbruch und reduzierte Bewegung prüfen.
9. Keine funktionslosen Features als produktiv darstellen.
10. Vor Commit `npm run build` ausführen.
11. Vor Push `git status` prüfen und `.tmp/`, Secrets sowie Rohquellen
    ausschließen.
12. Push und öffentliches Pages-Deployment als zwei getrennte Schritte
    behandeln.

## 19. Wichtigste Dateien für einen Frontend-Neustart

In dieser Reihenfolge:

1. `AGENTS.md`
2. `CHATGPT_PROJECT_BRIEF.md`
3. `docs/assets/designstyle.md`
4. `PROJECT_STATUS.md`
5. `PROJECT_LOG.md`
6. `apps/website/src/pages/index.astro`
7. `apps/website/src/components/CompetenceHubMap.astro`
8. `apps/website/src/components/HubJourney.astro`
9. `apps/website/src/layouts/BaseLayout.astro`
10. `apps/website/src/styles/global.css`
11. `apps/website/src/pages/leistungen.astro`
12. `apps/website/src/pages/mindforge.astro`
13. `apps/website/src/pages/unternehmen.astro`
14. `apps/website/src/pages/coaches.astro`
15. `apps/website/src/pages/kontakt.astro`

## 20. Empfohlener Auftrag an die nächste KI

```text
Analysiere den aktuellen Competence-Hub-Frontendstand anhand von
CHATGPT_PROJECT_BRIEF.md, docs/assets/designstyle.md und den sicheren
Astro-Dateien. Öffne keine Quellen-, .env-, Zugangsdaten- oder tmp-Dateien.

Bewerte zuerst:
- Informationshierarchie
- Besonderheit und B2B-/B2C-Wirkung
- Connected-Core-Hub und Scroll-Journey
- Navigation und schnelle Einstiege
- Textmenge und Scanbarkeit
- Konsistenz von Mindforge und Competence Hub
- mobile Nutzbarkeit
- Kontrast, Fokus und Bewegung
- Conversion für Unternehmen und Privatpersonen

Erstelle danach ein klares Frontend-Konzept mit:
- beizubehaltenden Elementen
- zu vereinfachenden Elementen
- neuer Seiten- und Abschnittsdramaturgie
- konkreten Komponenten
- Desktop-/Mobilverhalten
- visuellen Zuständen und Animationen
- schrittweiser Umsetzung ohne Backendvortäuschung

Noch keine Implementierung starten, bis Konzept, Auswirkungen auf bestehende
Seiten und Migrationsreihenfolge abgestimmt sind.
```
