# COACH-5: Angebotsfinder und getrennte Kalender-Demo

Stand: 05.11.2026. WEBSITE FIRST; Rebase/R2 bleibt pausiert.
Scope: öffentliche GitHub-Vorschau mit bereits freigegebener Kurzfassung;
zusätzlicher CAL-1-Auftrag ausschließlich lokal/synthetisch, siehe späteren
[Demo-Handoff](../../handoffs/2026-11-05-cal1-demo-readiness.md).
Keine IONOS-/VPS-/DB-/Schlüssel-/Admin-Aktivierung.

## Entscheidungen

- Vorhandene Leistungsroute erweitern, keine neue Navigationsebene. Finder direkt
  unter dem bestehenden Einstieg; Preview-Menü und Coach-Verzeichnis verlinken ihn.
- Statische Angebotsquelle: Elisabeths16 aktive Titel (Therapie ausgeschlossen),
  Susannes8 Workshops und Gülcans3 Familien/5 Formate. **27 Hauptzeilen,29 Formate**,
  optionale Ergänzungen keine zusätzlichen Angebote. Andere Coachbiografien und
  Becker-Neukandidaten erzeugen keine erfundenen Katalogeinträge.
- Themen/Kategorien aus `preview/topics.ts`. Titelbezogene Zuordnung dient der
  Navigation, nicht als neue Coachqualifikation. Zielgruppen/Formatlabels sind
  eine Ansicht belegter öffentlicher Kurztexte, keine zweite fachliche Datenbank.
- Keine belegten spezifischen Privatpersonenangebote in diesen drei Listen:
  Privatfilter liefert ehrlich leer und verweist auf Bedarfsklärung/Mindforge.
  Individuelle Angebote werden nicht pauschal als Beratungs-/Projektformat umetikettiert.
- Dauer nur für belegte Gülcan-Formate; ansonsten Rahmen nach Abstimmung. Keine
  Preise, echten Termine, Verfügbarkeit, Therapie-/Mediationsbuchung.
- Komponente nimmt ein öffentliches Viewmodel als Props, keine Datenbank/Registry
  und keine privaten Evidenzfelder. COACH-4 kann später eine geprüfte Adapterquelle
  liefern; dieser Sprint aktiviert sie nicht.
- Filter: Dimensionen AND; mehrere Themen OR. Alle Dimensionen müssen auf demselben
  Familienformat zutreffen. Nur passende Formate im geöffneten Treffer zeigen.
- Acht kompakte Zeilen zunächst, schrittweise mehr; ohne JS alle27 native Details.
  Keine Suchtexte in URL, Web Storage, Serveranfrage oder Kundenakte speichern.

## Ausführung

| Schritt | Stand | Nachweis / Gate |
| --- | --- | --- |
| Bestehende Quellen, Komponenten und Rechte abgleichen | DONE | Öffentliche Listen/Publication-Matrix, keine privaten Quellen gelesen |
| Viewmodel, bestehende Leistungsseite, Filter und Anfragewege | IMPLEMENTED |27/29, drei vorhandene Coachprofile, bestehender Mailto-Helfer |
| Vertrags-/Filter-/Dubletten-/Datenschutztests | PASS |34 Website-Verträge, sechs neue Finderfälle |
| Browser, Mobil, native200%, Fokus, No-JS, Suchregression | PASS |1555 Checks,34 Routen, Chromium149.0.7827.55, Exit0; einschließlich bestehender Coachsuche |
| CAL-1 lokale synthetische Vorführung | PASS |37 fokussierte Tests,76 Browserchecks; echte lokale Domain/API, synthetische Auth/Persistenz/Anfrage |
| Gesamtdiff/Produktionshashes, Commit/Push, manuelle Pages-Abnahme | PENDING | Kein IONOS; nur public-allowlisted Vorschau |

## Tatsächliche QA und Grenzen

Quellpakete: Finder `50aed83`, getrennte lokale CAL-Demo `d6bf0f9`. Nur diese
geprüften Implementierungen und bereinigte Dokumentation werden gepusht; keine
erzeugten Testprofile, Screenshots, Tokens oder temporären TLS-Dateien.

Astro:79 Quelldateien, null Fehler/Warnungen/Hinweise. Production1237 und
Preview1407 interne Referenzen geprüft. Gesamtes52-Dateien-Productionmanifest
bleibt bytegleich; Build-Alias verhindert auch einen unbenutzten Finder-JS-Bundle.
Eine rein bedingte HTML-Ausgabe reichte dafür nicht aus. Das erste Browser-Reset
war tatsächlich fehlerhaft (Render vor nativem Reset); jetzt synchron zurückgesetzt
und durch Browserprüfungen sämtlicher Filterdimensionen geschützt.

Generierte Belege: `apps/website/release-artifacts/coach5-finder-chromium-20261105/browser-report.json`,
21 Screenshots inklusive390px und echter nativer200% (707CSS-px/DPR2, kein CSS-Zoom).
Keine Drittanbieter-/Schreibrequests, Konsolen-/Ressourcenfehler; alle27 Angebote
erreichbar,29 Anfrageformate, Familienfilter ohne falsche Geschwistertreffer,
leere Privat-/Mediation-Auswahl und vollständige No-JS-Grundansicht tatsächlich geprüft.

Edge156 lieferte88 fokussierte Checks und native Screenshots, blieb im breiten
Lauf aber bei Browser-Teardown hängen; dieser Versuch wird NICHT als bestandener
Gesamtlauf gezählt. Der vorhandene explizit gewählte Chromium149 schloss den
vollständigen Lauf erfolgreich ab. Keine Browser-/Abhängigkeitsinstallation,
Windows-ACL-Änderung oder Sicherheitsausnahme am echten Browserprofil.
Ein explorativer eigener CDP-Profillauf schlug beim Teardown fehl; sein
ignorierter Rest unter `apps/website/release-artifacts/coach5-cdp-probe` bleibt
erhalten, nachdem die angebotene Löschung vom Werkzeug blockiert wurde. Keine
weiteren Löschversuche. Eigener Debug-Port52194 geschlossen; keine aktive Demo-
oder QA-Verbindung aus diesem Versuch. Keine Schlüssel-/Backupdaten enthalten.

Die aktuelle lokale CAL-Demo ist ausdrücklich eine separate Leseansicht für die
tatsächliche CAL-1-API, noch NICHT CAL-0.1-Laufzeitintegration oder Pages-Anbindung.
CAL-0.1 bleibt unverändert. Siehe die nachvollziehbare Grenze und sechs Schritte
im [Demo-Handoff](../../handoffs/2026-11-05-cal1-demo-readiness.md).

## Rollender Horizont

1. Aktuellen Finder visuell und mit Tastatur/Mobil/native200% abnehmen; tatsächliche
   Textrechtecke und Leermeldung prüfen, bestehende Coachsuche darf nicht regressieren.
2. Lokale CAL-1-Demo über vorhandene Rollen/Revisionskontrollen zusammenführen und
   in sechs fachlich verständlichen Schritten vorführen; alle Simulationen benennen.
3. Nur geprüfte Quellen logisch committen/pushen, bestehenden manuellen Pages-Prozess
   für freigegebene statische Änderungen nutzen und öffentlich nachprüfen.
4. Vor Janays Rückkehr in der Woche ab16.11. Feedback zur Demo sammeln; keine erneute
   Entscheidung zu bereits akzeptierten CAL-D/T/ADR-Regeln erfragen. Echte Nutzung
   bleibt von eigenen Betriebs-/Identitäts-/Datengates abhängig.

Spätere Schritte sind Planung, keine Aktivierungsfreigabe. Genau ein empfohlener
nächster CAL-1-Ausbaublock folgt nach tatsächlicher Demo-Abnahme.
