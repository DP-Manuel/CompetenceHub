# Competence Hub – PWA- und App-Distributionsstrategie

Status: Proposed / Architektur- und Produktplanung  
Stand: 2026-08-11

## 1. Anlass

Für den späteren Competence-Hub-Portal- und App-Ausbau soll geprüft werden, wie
Nutzer die Anwendung auf Android, iPhone/iPad und Desktop verwenden können,
ohne für die primäre Nutzung zwingend von Google Play oder dem Apple App Store
abhängig zu sein.

Diese Entscheidung betrifft die spätere `apps/webapp` und **nicht** die
öffentliche statische Astro-Website.

## 2. Aktueller Projektkontext

Bereits entschieden beziehungsweise vorbereitet:

- öffentliche Website bleibt ein getrenntes Astro-Frontend
- hinter dem Login ist eine eigenständige Webapp vorgesehen
- spätere Rollen:
  - internes Team
  - Coaches
  - Unternehmen
  - später gegebenenfalls Teilnehmende
- Backend und Datenbankzugriff werden serverseitig gekapselt
- PostgreSQL 16 ist für die Backend-/Staging-Richtung freigegeben
- Authentifizierung und Autorisierung gehören in das Backend-/Portalprojekt
- keine direkte Datenbankanbindung aus öffentlicher Website oder Client
- reale personenbezogene Daten bleiben bis zur vollständigen Betriebsfreigabe gesperrt

## 3. Strategische Empfehlung

### PWA-first statt sofort separate Android- und iOS-App

Die spätere Competence-Hub-Webapp soll von Beginn an so geplant werden, dass sie
als Progressive Web App (PWA) installierbar werden kann.

Zielbild:

```text
Öffentliche Astro-Website
        │
        └── Einstieg / Login
                │
                ▼
        Competence-Hub-Webapp / PWA
                │
                ▼
             Backend API
                │
                ▼
            PostgreSQL
```

Die PWA soll dieselbe Anwendung auf folgenden Plattformen nutzbar machen:

- Desktop-Browser
- Android
- iPhone / iPad
- installierter App-Modus, soweit Browser und Betriebssystem dies unterstützen

Dadurch entsteht zunächst nur **eine fachliche Client-Anwendung** statt
getrennter Android-, iOS- und Web-Implementierungen.

## 4. Warum PWA-first für Competence Hub sinnvoll ist

Die bisher geplanten Portalaufgaben sind überwiegend webtypisch:

- Login
- rollenabhängige Dashboards
- Firmenverwaltung
- Coachverwaltung
- Anfragen
- Aufträge
- Termine
- Feedback
- Dokumente
- Statistiken
- Kalender-/Booking-Anbindungen
- Benachrichtigungen
- später Teilnehmerzugänge

Für diese Funktionen ist eine native App nicht automatisch erforderlich.

Vorteile:

- gemeinsamer Funktionsstand auf Web, Android und iOS
- geringerer Wartungsaufwand
- keine zwingende Store-Veröffentlichung für die Grundnutzung
- Updates können serverseitig ausgerollt werden
- bestehende Backend-/API-Architektur bleibt unabhängig vom Client
- spätere native Apps können dieselbe API weiterverwenden
- schrittweise Einführung möglich

## 5. Distribution

### 5.1 PWA

Bevorzugter erster Installationsweg.

Eine installierbare PWA benötigt unter anderem:

- HTTPS
- Web App Manifest
- geeignete App-Icons
- definierte Display-/Startparameter
- browserabhängige Installationsfähigkeit
- saubere responsive Oberfläche

Auf unterstützten Plattformen kann eine PWA als eigenständige Anwendung mit
eigenem Icon und eigenem Fenster installiert werden.

Der konkrete Installationsdialog unterscheidet sich nach Browser und
Betriebssystem.

### 5.2 Android – direkte native Distribution als spätere Option

Android unterstützt weiterhin die Verteilung signierter APKs über eine eigene
Website oder einen Unternehmensserver.

Dabei müssen Nutzer Installationen aus der jeweiligen externen Quelle zulassen.

Zusätzlich ist die ab 2026/2027 schrittweise ausgerollte
Android-Developer-Verification in der Langfristplanung zu berücksichtigen. Für
professionelle Distribution außerhalb von Google Play können
Entwickleridentität und Paketregistrierung künftig relevant werden. Zeitplan,
Geltungsbereich und konkrete Anforderungen müssen vor einem späteren nativen
Android-Release anhand der dann aktuellen offiziellen Android-Dokumentation neu
geprüft werden; diese Planung ist kein dauerhaftes Distributionsversprechen.

Daher gilt:

- direkte APK-Verteilung bleibt technisch möglich
- sie ist **nicht** die bevorzugte erste Competence-Hub-Strategie
- Anforderungen zur Entwicklerverifikation sind vor einem späteren nativen
  Android-Release erneut anhand der dann aktuellen Google-Dokumentation zu prüfen

### 5.3 Apple – native Direktverteilung nicht als Basisstrategie

Apple erlaubt in der EU unter bestimmten Voraussetzungen die direkte
Web-Verteilung nativer iOS-/iPadOS-Apps.

Die derzeitigen Voraussetzungen für die allgemeine Web Distribution sind für
ein neues Competence-Hub-Projekt jedoch sehr hoch, unter anderem durch
Anforderungen an den Apple-Developer-Account und bisherige Installationszahlen.

Daher:

- native iOS-Webdistribution nicht als aktuellen Zielweg einplanen
- PWA als store-unabhängigen iPhone-/iPad-Weg bevorzugen
- App-Store- oder andere native Distribution erst bei echtem späterem Bedarf
  neu bewerten
- Apple-Zulassung, regionale Verfügbarkeit und Eligibility vor jedem späteren
  nativen Release anhand der dann aktuellen offiziellen Bedingungen neu prüfen

## 6. Kein Architektur-Lock-in

PWA-first bedeutet nicht „nie native Apps“.

Zielarchitektur:

```text
                 Backend API
                     │
        ┌────────────┼────────────┐
        │            │            │
       PWA       Android-App    iOS-App
        │            │            │
   primär zuerst   optional      optional
```

Native Clients werden nur ergänzt, wenn konkrete Anforderungen dies
rechtfertigen.

Mögliche Trigger:

- Funktionen stehen im Web nicht ausreichend zur Verfügung
- besondere Geräteintegration
- zwingende Hintergrundprozesse
- erhebliche UX-Vorteile
- organisatorische Vorgabe für Store-Verteilung
- nachgewiesener Nutzerbedarf

## 7. PWA-Readiness bereits bei der Webapp-Architektur berücksichtigen

Noch keine PWA implementieren.

Bei der Planung der `apps/webapp` jedoch berücksichtigen:

### Frontend

- mobile-first
- responsive Navigation
- Touch-Bedienung
- App-artige Informationshierarchie
- stabile URLs / Deep Links
- keine Funktionen, die ausschließlich Hover voraussetzen
- installierbares Layout später ohne grundlegenden Umbau möglich

### Backend

PWA und Browser verwenden dieselbe sichere API.

Keine PWA-spezifische direkte Datenbankverbindung.

### Authentifizierung

Vor Implementierung gesondert entscheiden:

- Session-/Tokenmodell
- sichere Speicherung
- Logout und Sessionablauf
- Geräteverlust
- Mehrgerätebetrieb
- Rollenwechsel / Mehrfachrollen
- CSRF/XSS-Schutz
- Auditnachweise

## 8. Offline- und Cache-Grenzen

PWA bedeutet **nicht automatisch Offline-Datenspeicherung**.

Für Competence Hub gilt zunächst:

- keine personenbezogenen Portal-/Firmendaten offline cachen
- keine Verträge oder sensiblen Dokumente ungeprüft in Browser-/Service-Worker-
  Caches speichern
- nur öffentliche beziehungsweise ausdrücklich freigegebene statische Assets
  dürfen in einem ersten Offline-Konzept enthalten sein
- Offline-Fachfunktionen erst nach Datenschutz-, Sicherheits- und
  Bedarfsentscheidung

Vor einem Service Worker muss eine Cache-Klassifikation dokumentiert werden:

```text
PUBLIC_STATIC
AUTHENTICATED_NON_SENSITIVE
PERSONAL_DATA
CONFIDENTIAL_DOCUMENT
NO_CACHE
```

Default für authentifizierte Daten:

`NO_CACHE`, bis ausdrücklich anders entschieden.

## 9. Push-Benachrichtigungen

Push ist eine mögliche spätere PWA-Funktion, aber kein MVP-Gate.

Vor Einführung klären:

- fachlicher Nutzen
- Einwilligung
- welche Informationen in Push-Texten erscheinen dürfen
- Datenschutz auf gesperrten Smartphones
- Abmelde- und Widerrufsprozess
- Browser-/Plattformunterstützung

Keine sensiblen Inhalte in Push-Nachrichten als Default.

## 10. Installations-UX

Später kann die öffentliche Competence-Hub-Seite einen Bereich anbieten:

```text
Competence Hub für unterwegs

Nutzen Sie Ihren persönlichen Bereich auf Smartphone,
Tablet oder Desktop.

[ Web-App öffnen ]
[ App installieren ]
```

Die UI muss je Plattform erklären, welcher Installationsweg tatsächlich
unterstützt wird.

Keine Behauptung „im App Store verfügbar“, solange dies nicht stimmt.

## 11. Trennung Website / Portal / App

### Öffentliche Website

- Information
- Leistungen
- Coaches
- Kontakt
- SEO/GEO
- kein direkter Datenbankzugriff

### Webapp / PWA

- Authentifizierung
- personenbezogene Fachprozesse
- Firmen-/Coach-/interne Rollen
- Termine, Aufträge, Feedback, Dokumente

### Backend

- Authentifizierung
- Autorisierung
- Validierung
- Audit
- Geschäftslogik
- Datenbankzugriff

Diese Trennung bleibt auch bei einer installierten PWA verbindlich.

## 12. Geplante Phasen

### Phase A – jetzt

Nur Architekturwissen dokumentieren.

Keine PWA-Implementierung.

### Phase B – erster Webapp-Slice

- Authentifizierung
- serverseitige Autorisierung
- Mehrfachrollen
- Audit
- erster fachlicher Portalworkflow

PWA-Readiness bei UI- und Routingentscheidungen berücksichtigen.

### Phase C – PWA-Basis

Erst nach stabilem Webapp-Kern:

- Manifest
- Icons
- Installationsmetadaten
- Displaymodus
- Installations-UX
- technische Installierbarkeit testen

### Phase D – Service Worker / Cache

Nur nach eigener Cache- und Datenschutzentscheidung.

### Phase E – Benachrichtigungen

Nur bei bestätigtem Use Case.

### Phase F – Native App Evaluation

Erst prüfen, wenn reale Anforderungen mit PWA/Web nicht sinnvoll lösbar sind.

## 13. Entscheidungsstatus

### Proposed

- Competence Hub soll **PWA-first** geplant werden.
- App Stores sind für die erste installierbare Version nicht als
  Grundvoraussetzung vorgesehen.
- Native Apps bleiben spätere optionale Clients.
- PWA-Readiness soll in zukünftigen Webapp-Entscheidungen berücksichtigt werden.

### Noch nicht entschieden

- konkreter Frontend-Stack der Webapp
- Authentifizierungsverfahren
- Service-Worker-Strategie
- Offline-Funktionen
- Push
- native App-Technologie
- spätere Store-Veröffentlichung
- konkrete Plattform-/Browser-Baseline und Installationsanleitung je Zielgerät
- Zeitpunkt und Owner der erneuten Android-/Apple-Distributionsprüfung

## 14. Sicherheitsgrenzen

Unverändert:

- keine Secrets in Dokumentation oder Git
- keine `.env`-Dateien lesen oder committen
- `Quellen/` nur nach konkreter Freigabe
- `.tmp/` nicht verarbeiten oder committen
- keine realen personenbezogenen Daten im Entwicklungs-/Prototypbetrieb
- kein Deployment ohne ausdrückliche Freigabe
- keine native App oder PWA als produktiv darstellen, bevor sie implementiert
  und freigegeben ist
