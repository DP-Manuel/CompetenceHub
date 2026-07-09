# Competence Hub Website - Projektbrief fuer externe KI

Stand: 2026-07-09

Zweck dieser Datei: schnelle, sichere Projektuebersicht fuer eine zweite KI, die Prompts oder Umsetzungsvorschlaege schreiben soll. Diese Datei enthaelt bewusst keine Zugangsdaten, keine Secrets und keine Inhalte aus dem gesperrten Quellen-Ordner.

## Kurzfassung

- Projekt: Competence Hub Website
- Lokaler Projektpfad: `C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website`
- Neues Ziel-Repo laut Manuel: `https://github.com/DP-Manuel/CompetenceHub`
- Aktuelles lokales Git-Remote zeigt noch auf: `https://github.com/DP-Manuel/Firmenschulung.git`
- Deadline Website-MVP: 2026-07-23
- Ziel: schnell sichtbarer, professioneller, wartbarer Website-MVP.
- Fokus: Livecoaching- und Businesscoaching-Angebote, Firmenkunden, Coach-Netzwerk, Kontakt/Anfrage.
- Nicht-Fokus jetzt: Project Cockpit, echtes Backend, Login, Buchungssystem, Datenbank, Deployment-Automatisierung.

## Sicherheitsgrenzen

Nicht oeffnen, nicht lesen, nicht indexieren:

- `C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\Quellen`
- Word-Dokument mit dem Namen `Zugangsdaten Server und Datenbank`
- `.env`, `.env.*`, Zugangsdaten, Passwoerter, Tokens, Secrets

Keine Secrets in Code, Docs, Prompts oder Commits schreiben.

Keine sensiblen Daten an externe Dienste senden.

Kein Deployment ohne ausdrueckliche Freigabe.

Keine externen Provider fuer das Projekt einfuehren.

Kein OpenRouter.

Kein Hermes.

Kontaktformular zunaechst nur sicher planen: ENV-/Konfigurationsplatzhalter, keine echten Zugangsdaten.

## Was bisher geschehen ist

1. Projektstruktur wurde als Website-first Workspace angelegt.
2. Astro wurde als statischer Website-Stack eingerichtet.
3. Eine erste moderne Stakeholder-Prototyp-Website wurde gebaut.
4. Vorhandene Routen:
   - `/`
   - `/unternehmen`
   - `/seminare`
   - `/qualifizierung`
   - `/system`
   - `/login`
   - `/kontakt`
   - `/coaches`
   - `/coaches/christian-galvano`
5. Die Seite ist aktuell noch auf eine fruehere Positionierung ausgerichtet:
   - Firmenschulungen
   - KMU in Tauberfranken/Wuerzburg
   - Personalqualifizierung
   - Vermittlungsperspektive
   - spaeterer Systemausblick
6. Ein erstes echtes Coach-Profil fuer Christian Galvano wurde integriert.
7. Login und Kontakt sind visuelle Demos ohne Authentifizierung, Datenbank oder echte Formularverarbeitung.
8. Astro Build wurde geprueft:
   - `astro check`: 0 Fehler, 0 Warnungen, 0 Hinweise
   - Build in Sandbox kann mit `spawn EPERM` scheitern
   - derselbe Build ausserhalb der Sandbox lief erfolgreich und erzeugte 9 statische Seiten
9. Am 2026-07-09 wurde entschieden, daraus einen Deadline-Sprint fuer den Website-MVP "Competence Hub" zu machen.

## Aktuelle technische Basis

Stack:

- Astro `^5.18.2`
- TypeScript `^6.0.3`
- `@astrojs/check`
- Statische Website
- Kein WordPress
- Kein Backend
- Keine Datenbank
- Keine echte Authentifizierung

Wichtige Datei:

- `apps/website/package.json`

Scripts:

```json
{
  "dev": "astro dev --host 127.0.0.1",
  "build": "astro check && astro build",
  "preview": "astro preview --host 127.0.0.1"
}
```

Lokale Entwicklung:

```powershell
$env:PATH = "..\..\tools\node-v22.16.0-win-x64;$env:PATH"
cd apps\website
npm run dev
```

Build:

```powershell
$env:PATH = "..\..\tools\node-v22.16.0-win-x64;$env:PATH"
$env:ASTRO_TELEMETRY_DISABLED = "1"
cd apps\website
npm run build
```

Falls Astro/Vite wegen Windows-Sandbox mit `spawn EPERM` oder AppData-Telemetrieproblemen scheitert: erst als Umgebungsproblem behandeln, nicht sofort als Codefehler.

## Lokale Version der Website

Eine lokale Version ist sehr sinnvoll und sollte beibehalten werden.

Grund:

- schnelle Aenderungen ohne Deployment
- weniger Tokenverbrauch, weil Code lokal geprueft werden kann
- bessere visuelle Kontrolle vor Push/Deploy
- sicherer Umgang mit Secrets, weil keine Zugangsdaten an Chat-KIs geschickt werden muessen

Empfohlener Arbeitsmodus:

1. Lokal in `apps/website` arbeiten.
2. `npm run dev` fuer schnelle Vorschau nutzen.
3. Vor groesseren Uebergaben `npm run build` ausfuehren.
4. Erst nach Freigabe ins Repo pushen.
5. Serverdaten niemals in Prompts kopieren.

## Repo-Empfehlung

Das neue Repo `DP-Manuel/CompetenceHub` macht Sinn.

Empfohlen:

- Competence Hub als neues kanonisches Repo verwenden.
- Aktuellen Website-Code und sichere Dokumentation dorthin ueberfuehren.
- Nicht uebernehmen:
  - `Quellen/`
  - `.env`, `.env.*`
  - Zugangsdaten-Dokumente
  - `node_modules/`
  - `dist/`
  - `.astro/`
  - lokale Logs
  - private Rohmaterialien ohne Freigabe

Wichtig: lokal zeigt `origin` derzeit noch auf `DP-Manuel/Firmenschulung.git`. Vor einem Push ins neue Repo muss das Remote bewusst angepasst oder ein neues Remote gesetzt werden. Nicht blind pushen.

Moegliche Strategie:

- `origin` auf `https://github.com/DP-Manuel/CompetenceHub.git` umstellen, wenn das alte Repo nicht mehr Ziel sein soll.
- Alternativ ein zweites Remote wie `competencehub` anlegen, wenn das alte Repo vorerst erhalten bleiben soll.

Keine Git-Aenderung wurde in diesem Schritt automatisch vorgenommen.

## Server-Stand

Manuel hat neue Daten fuer einen neuen Server, der noch blank ist.

Empfehlung:

- Zugangsdaten nicht an ChatGPT oder andere KI schicken.
- Erst Repo und lokalen Build sauber machen.
- Dann Deployment-Plan schreiben.
- Erst danach Server initialisieren.
- Serverzugangsdaten lokal halten, idealerweise in Passwortmanager oder sicherer lokaler Dokumentation, nicht im Repo.

Bis zur Freigabe kein Deployment.

## Aktuelle Ordnerstruktur

Root:

```text
C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website
├─ .agents/
├─ .github/
├─ .git/
├─ .tmp/
├─ apps/
├─ docs/
├─ new-project-starter/
├─ scripts/
├─ tools/
├─ .gitignore
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

Website:

```text
apps/website
├─ public/images/
├─ public/images/coaches/
├─ scripts/serve-dist.mjs
├─ src/layouts/BaseLayout.astro
├─ src/pages/
├─ src/pages/coaches/
├─ src/styles/global.css
├─ astro.config.mjs
├─ package.json
├─ package-lock.json
├─ README.md
└─ tsconfig.json
```

Website-Seiten:

```text
apps/website/src/pages/index.astro
apps/website/src/pages/unternehmen.astro
apps/website/src/pages/seminare.astro
apps/website/src/pages/qualifizierung.astro
apps/website/src/pages/system.astro
apps/website/src/pages/login.astro
apps/website/src/pages/kontakt.astro
apps/website/src/pages/coaches.astro
apps/website/src/pages/coaches/christian-galvano.astro
```

Webapp:

```text
apps/webapp/README.md
```

Status: reserviert fuer spaetere Webanwendung, aktuell nicht gescoped.

Docs:

```text
docs/assets/brand-design-notes.md
docs/decisions/0001-subdomain-independent-system-database.md
docs/design/homepage-wireframe-concept.md
docs/requirements/content-briefing-colleague-prototype.md
docs/requirements/future-system-ideas-backlog.md
docs/requirements/product-discovery-brief.md
docs/requirements/stakeholder-prototype-2026-07-01.md
docs/requirements/website-maintenance-handover-and-editor-workflows.md
docs/requirements/website-outline.md
docs/research/b2b-design-benchmark.md
```

## Wichtige Projektdateien

`AGENTS.md`

- verbindliche Arbeitsregeln fuer Codex/KI
- enthaelt Sicherheitsgrenzen
- enthaelt Skill-Routing und Projektstruktur

`PROJECT_PLAN.md`

- Projektvision, Scope, Roadmap, Risiken, Entscheidungen
- aktuell noch stark auf Stand 2026-06-30 / Stakeholder-Prototyp bezogen
- muss fuer Competence-Hub-Deadline-Sprint aktualisiert werden

`PROJECT_STATUS.md`

- kompakter Status und Restart-Handoff
- aktuell Stand 2026-06-30
- muss ebenfalls auf 2026-07-09 / Deadline 2026-07-23 aktualisiert werden

`PROJECT_LOG.md`

- chronologisches Projektlog, neueste Eintraege zuerst
- dokumentiert Setup, Prototyp, Deployments, Entscheidungen und Skill-Themen

`PROJECT_AI_POLICY.md`

- KI-Sicherheitsregeln
- Hard Deny Paths
- Datenklassen
- Logging- und Stop-Regeln

`SKILL_FEEDBACK_LOG.md`

- Sammlung von Verbesserungen fuer CodexSkills
- wichtige Punkte:
  - visuelle UI-Handoffs brauchen lokale Vorschau/Screenshots
  - Sandbox/Astro EPERM-Fehler dokumentiert
  - Anforderungen sollen automatisch persistiert werden
  - Windows-/Umlaut-/Toolchain-Probleme wurden als Skill-Learning erfasst
  - GitHub Pages Aktivierung und Deployment-Checklisten wurden als Learning erfasst

## Vorhandene Ressourcen

Bildassets:

```text
apps/website/public/images/start.png
apps/website/public/images/firmenseminare.png
apps/website/public/images/qualifizierung.png
apps/website/public/images/vermittlung.png
apps/website/public/images/recruiting.png
apps/website/public/images/partnerschaft.png
apps/website/public/images/digitale-lernplattform.png
apps/website/public/images/coaches/christian-galvano.webp
```

Code-Ressourcen:

- gemeinsames Layout: `apps/website/src/layouts/BaseLayout.astro`
- globales Styling: `apps/website/src/styles/global.css`
- keine separaten Komponenten bisher
- Inhalte aktuell direkt in Astro-Seiten als Arrays/Markup gepflegt

Deployment-Ressource:

- `.github/workflows/deploy.yml`
- GitHub Pages Workflow fuer Astro
- aktuell fuer altes Setup gedacht

Astro-Konfiguration:

```js
site: "https://dp-manuel.github.io"
base: "/Firmenschulung"
```

Bei neuem Repo `CompetenceHub` muss `base` wahrscheinlich auf `/CompetenceHub` angepasst werden, falls GitHub Pages unter `https://dp-manuel.github.io/CompetenceHub/` genutzt wird. Bei eigener Domain/Subdomain waere die Konfiguration anders.

## Aktueller Git-Status

`git status --short` zeigt viele unversionierte Dateien, unter anderem:

```text
?? .tmp/
?? AGENTS.md
?? MEETINGS.md
?? PROJECT_AI_POLICY.md
?? PROJECT_LOG.md
?? PROJECT_PLAN.md
?? PROJECT_STATUS.md
?? SKILL_FEEDBACK_LOG.md
?? apps/webapp/
?? docs/
?? new-project-starter/
?? scripts/
```

Interpretation:

- Das Projekt wirkt lokal noch nicht sauber als neues Repo konsolidiert.
- Vor einem Push nach `DP-Manuel/CompetenceHub` sollte bewusst entschieden werden, welche Dateien versioniert werden.
- `.gitignore` schliesst wichtige Dinge bereits aus:
  - `node_modules/`
  - `dist/`
  - `.astro/`
  - `tools/node-*`
  - `tools/*.zip`
  - `Quellen/`
  - `*.log`
  - `.env`, `.env.*`

## Ziel bis 2026-07-23

Professioneller Website-MVP fuer "Competence Hub".

Muss:

- Marke: `Competence Hub`
- moderne Startseite
- klare Angebote:
  - Livecoaching
  - Businesscoaching
- Zielgruppe Unternehmen klar ansprechen
- Coach-/Netzwerkseite sinnvoll einordnen
- Kontakt-/Anfrageseite professionell
- SEO/KI-Suchmaschinenoptimierung beruecksichtigen
- Mobile-first
- wartbar
- statisch buildbar
- keine Secrets
- kein echtes Backend

Sollte:

- Angebotsuebersicht `/leistungen` oder `/angebote`
- Einzelseiten `/livecoaching` und `/businesscoaching`
- Seite `/unternehmen`
- Seite `/coaches` oder `/netzwerk`
- optionale Seite `/ueber-uns`
- Impressum und Datenschutz klaeren
- interne Verlinkung und Meta-Descriptions
- strukturierte FAQ-Bloecke fuer Suchmaschinen/KI-Antwortsysteme

Spaeter:

- Buchungssystem im Backend fuer Firmen und Coaches
- zunaechst ca. 5 Coaches
- spaeter einzelne Teilnehmer
- Coach-Kalender
- evtl. Outlook Booking Integration
- Vertragsautomatisierung
- Handy-taugliche Vertragserstellung fuer Kollegin Rappelt
- E-Mail an Buchhaltung/Kollegin
- MySQL-Datenbank
- Mobile-App nach August 2026 fuer Auftraege, Termine und Rechnungen

Nicht jetzt:

- Project Cockpit weiter ausbauen
- echter Login
- echte Datenbank
- echte Buchung
- Vertragsautomatisierung
- Deployment ohne Freigabe
- neue Frameworks einfuehren
- grosse Refactorings ohne Deadline-Nutzen

## Empfohlene Seitenstruktur fuer MVP

```text
/                       Startseite
/leistungen             Angebote im Ueberblick
/livecoaching           Livecoaching-Angebot
/businesscoaching       Businesscoaching-Angebot
/unternehmen            Fuer Unternehmen
/coaches                Fuer Coaches / Netzwerk
/kontakt                Kontakt / Anfrage
/ueber-uns              optional
/impressum              Pflichtseite, Inhalt klaeren
/datenschutz            Pflichtseite, Inhalt klaeren
```

Bestehende Seiten koennen umgebaut werden:

- `/seminare` kann zu `/leistungen` oder einem Angebotsbereich werden.
- `/qualifizierung` kann fuer spaeter geparkt oder reduziert werden.
- `/system` und `/login` sollten fuer den MVP in der Navigation zuruecktreten oder entfernt werden, damit die Website nicht wie eine unfertige App wirkt.
- `/kontakt` sollte von Demo-Formular zu serioeser Anfrage-Seite weiterentwickelt werden, aber ohne echte Verarbeitung, solange keine sichere Konfiguration vorhanden ist.

## Naechste konkrete Umsetzungsschritte

Arbeitsblock 1: sichtbare MVP-Umstellung

- `[Submarke]` durch `Competence Hub` ersetzen.
- Navigation auf MVP-Seitenstruktur umstellen.
- Startseite auf Livecoaching + Businesscoaching ausrichten.
- Hero, CTAs und Angebotskacheln ueberarbeiten.
- System/Login-Ausblick aus der Hauptnavigation entfernen oder stark nachrangig machen.

Arbeitsblock 2: Angebotsseiten

- `/livecoaching` erstellen.
- `/businesscoaching` erstellen.
- `/unternehmen` auf Firmenkunden-Nutzen ausrichten.
- `/coaches` als Netzwerk-/Vertrauensseite ueberarbeiten.
- Kontaktseite als Anfrageprozess formulieren.

Arbeitsblock 3: Qualitaet und Repo

- SEO-Titel und Meta-Descriptions pro Seite.
- strukturierte H1/H2 und FAQ-Bloecke.
- Mobile Layout pruefen.
- `npm run build` pruefen.
- neues Repo `DP-Manuel/CompetenceHub` bewusst als Ziel einrichten.
- nur sichere Dateien committen.

## Hinweise fuer die Prompt-KI

Bitte keine Prompts schreiben, die verlangen:

- `Quellen/` zu lesen
- Zugangsdaten zu kopieren
- `.env` zu oeffnen
- Serverdaten in den Chat zu schicken
- Deployment ohne Freigabe zu starten
- externe Provider einzubauen
- WordPress einzufuehren
- OpenRouter oder Hermes zu nutzen

Gute Prompt-Richtung:

- "Arbeite nur mit sicheren Dateien ausserhalb von `Quellen/`."
- "Baue zuerst lokal einen sichtbaren MVP."
- "Halte den bestehenden Astro-Stack."
- "Keine neuen Frameworks ohne technische Notwendigkeit."
- "Keine Backend- oder Login-Funktionalitaet vortaeuschen."
- "Kontaktformular nur als sichere, noch nicht angebundene Anfrage vorbereiten."
- "Nach jeder sichtbaren UI-Aenderung Build und lokale Vorschau/Screenshot einplanen."

## Kompakter Arbeitsauftrag fuer die naechste KI

Du arbeitest im Projekt:

`C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website`

Ziel:

Bis 2026-07-23 einen modernen, mobilen, wartbaren Website-MVP fuer `Competence Hub` liefern.

Stack:

Astro static site in `apps/website`.

Nicht lesen:

`Quellen/`, `.env*`, Zugangsdaten, Serverdaten, Secrets.

Erster sinnvoller Umsetzungsschritt:

`apps/website/src/layouts/BaseLayout.astro` und `apps/website/src/pages/index.astro` auf `Competence Hub` umstellen: Marke, Navigation, Hero, CTAs und Angebotskacheln fuer Livecoaching und Businesscoaching. Danach Build pruefen.
