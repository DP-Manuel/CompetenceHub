# CAL-1 Portal UI Contract v0.1

Stand: 18.09.2026

Status: lokal mit ausschließlich synthetischen Identitäten und In-Memory-Daten
implementiert. Echte Browserabnahme, native Staging-UI-Abnahme, reale Rollen,
reale Coachprofile und Deployment bleiben offen.

## Grenze

Die CAL-1-Oberfläche ist Teil des bestehenden frameworkfreien Same-Origin-
Portals. Sie verwendet dieselbe MFA-Sitzung, CSRF-Rotation, Origin-Prüfung und
`no-store`-Grenze. Die bestehende interne Loginauflösung bleibt unverändert;
Kalenderrechte werden ausschließlich über die getrennte serverseitige
CAL-1-Session-/Rollenauflösung ermittelt.

Die Oberfläche leitet keine Rechte aus Namen oder E-Mail-Adressen ab. Eine
Person wird nicht als Sonderfall codiert. Nicht freigegebene Coach- oder
Reviewer-Bereiche werden aus dem aktiven DOM entfernt. Die API prüft jede
Lese- und Schreibaktion dennoch unabhängig von der UI.

## Arbeitsbereiche

- `internal`: Firmenbereich, keine Kalenderverwaltung und keine Prüfliste.
- `company_contact`: kein geschützter CAL-1-Arbeitsbereich.
- `coach`: eigene Angebote, Themen des verknüpften Coachprofils, Entwurf,
  Bearbeitung, Einreichung, Rücknahme und Revision.
- `calendar_reviewer`: getrennte Prüfliste und ausschließlich die Entscheidungen
  `published` oder `changes_requested`.
- `admin`: dokumentierter CAL-1-Gesamtscope und Prüfliste; ein neuer eigener
  Entwurf wird nur angeboten, wenn zusätzlich eine Coachrolle vorliegt.

Mehrere Rollen kombinieren nur ausdrücklich gewährte Bereiche. Der vorhandene
Firmen-/Kontaktbereich erhält dadurch keine zusätzlichen Rechte.

## Coach Workflow

Die Liste zeigt Titel, Thema, Zeitraum, Revision und Status als Text. Die UI
sendet ausschließlich die im API-Vertrag definierten Draft-Felder. Technische
IDs werden nicht als sichtbarer Inhalt ausgegeben; notwendige Datensatz- und
Themenreferenzen bleiben nur im flüchtigen JavaScript-Zustand beziehungsweise
in Optionswerten.

Ein Draft ist direkt editierbar. Nach einer Änderungsanforderung oder einer
Veröffentlichung wird die serverseitige Revisionslogik über denselben
Draft-Endpunkt ausgelöst. Eine eingereichte Fassung bietet keine Bearbeitung
an. Änderungsnotizen werden dem besitzenden Coach angezeigt.

Mutationen verwenden den letzten `ETag` als `If-Match`. Ein `409` wird sichtbar
gemeldet und bietet ein bewusstes Nachladen; die fehlgeschlagene Mutation wird
nicht automatisch wiederholt. Formwerte werden vor dem Busy-/Disable-Zustand
erfasst, Formulare und Einzelaktionen blockieren Doppelauslösung.

## Reviewer Workflow

Die Prüfliste enthält nur eingereichte Angebote. Sichtbar sind Coach-Anzeigename,
Thema, Titel, Zeitraum, Format, öffentliche Angebotsdaten, Revision und Status.
Reviewer können Inhalte oder Stammdaten nicht bearbeiten. Eine
Änderungsanforderung verlangt einen begrenzten Hinweis.

## Zustände Und Accessibility

Coach- und Reviewer-Bereich besitzen jeweils Loading-, Empty-, Fehler- und
Erfolgszustände. Labels sind vollständig, Fehler erhalten Fokus, Status wird
nicht nur farblich vermittelt und native Dialoge bleiben per Tastatur und
Escape bedienbar. Das Layout wechselt unter 900 Pixel auf eine Spalte, nutzt
mindestens 44 Pixel hohe Hauptziele und respektiert `prefers-reduced-motion`.

Verbindliche manuelle Nachweise stehen in
`docs/architecture/calendar-cal1-browser-acceptance-checklist-2026-09-18.md`.
