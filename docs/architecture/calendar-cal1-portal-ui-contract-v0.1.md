# CAL-1 Portal UI Contract v0.1

Stand: 18.09.2026

## V1.1 UX-Korrektur 13.11.2026

Kalendereingaben verwenden ausdrücklich `TT.MM.JJJJ HH:mm`, Europe/Berlin und
24-Stunden-Zeit, nicht das Browser-Locale. Viertelstunden sind Auswahlangebote,
keine Rundungsregel; direkte eindeutige Minuten und vorhandene Sekunden bleiben
erhalten. Neue DST-Lücken/doppelte Uhrzeiten werden erklärt statt still verschoben.
Kurzbeschreibung bleibt optional. Strukturell unvollständige Entwürfe sind nach
bestehendem Fachvertrag nicht zulässig; kein neues Partial-Draft-Modell.

Client- und allowlistbasierte API-Feldfehler werden unter dem Feld mit Beispiel,
`aria-invalid`/Beschreibung und Fokus in visueller Reihenfolge dargestellt;
Werte bleiben erhalten. Verspätete Portalstart-/Kalenderantworten werden nach
Sessionwechsel verworfen; Logout darf keine privaten Ansichten wiederherstellen.
Coach-Tour umfasst jetzt9 Schritte, Reviewer7; öffentlicher Kalender3. Dieselbe
freiwillige Tour-Komponente, keine Mutation/Tracking. Öffentlicher ICS-Link heißt
„Zum Kalender hinzufügen (.ics)“. Private Zugänge bleiben getrennt von Git.
[Aktuelle Abnahme, Paket und Remote-Gate](../operations/portal-v11-ux-2026-11-13.md).

## Additives integriertes Pilot-Inkrement 09.11.2026

Rollenbegrenzter Arbeitsüberblick liest native SQL-Statuszähler, keine Buchungs-
oder Teilnehmerstatistik. Admin erhält eine paginierte, tokenfreie Zugangsliste;
Coach-/Reviewer-Views bekommen keine fremden Account-/Firmenangaben.
Drei freiwillige Einführungen unter Hilfe, niemals automatisch angezeigt,
ohne Web-Storage-/Trackingdaten. Native Dialogsemantik, Weiter/Zurück,
Überspringen, Schließen/Escape, Fokus zurück zu Hilfe; fehlende Ziele bleiben
kontrolliert überspringbar. Mobile, nativer200%-Zoom und Reduced Motion gehören
zur Abnahme. Keine Mutation wird durch eine Tour ausgelöst.
Die gebaute Runtime-Kalenderseite verwendet denselben Renderer wie die lokale
CAL-0.1-Demo; sie enthält keine Testzugänge oder Dummy-MFA.
[Betriebs-/Erstzugangsgrenzen und kurze Rollenleitfäden](../operations/integrated-staging-pilot-2026-11-09.md).

Lokales Pilot-Inkrement06.11: Coachliste nach Beginn sortiert, Suche und
Statusfilter, sichtbare Kapazität/Entscheidungsfrist; ursprüngliche Indizes
bleiben für Aktionen erhalten, auch bei gefilterter/umsortierter Darstellung.
409-Zeitkonflikte werden nicht mehr als Versionsfehler umgedeutet. Reviewer-
Änderungsnotizen und reale Revisions-/RBAC-Grenzen bleiben maßgeblich.

Ungespeicherte Coach-/Reviewer-Formulare fragen vor Escape, Abbrechen,
Hintergrundklick oder explizitem Verlassen nach. Laufende Übertragung wird nicht
weggeklickt; erfolgreiche Speicherung schließt ohne zusätzliche Bestätigung.
Browser-Verlassen nutzt den nativen `beforeunload`-Schutz. Filter und private
Formular-/Feedback-Inhalte werden beim Sessionreset verworfen. Keine lokale
Speicherung von Entwürfen, Tokens oder Notizen.

Öffentliche lokale Ansichten teilen weiterhin dieselben Renderer/Controller.
ICS-Download liest anonym und prüft Erfolg/MIME vor dem Blob-Download; bei Fehler
keine JSON-Fehlerdatei. Anfrageentwurf enthält ausschließlich öffentliche
Termindaten und gewünschte Platzanzahl, ohne Kundenspeicherung oder Versand.
Kopieren ist ausdrücklich nutzerinitiiert. Bei neuer Veröffentlichung wird ein
veralteter Anfrageentwurf zurückgesetzt. Keine Vormerkungs-/Verfügbarkeitszusage.
[Aktueller Nachweis und Grenzen](../handoffs/2026-11-06-cal1-pilot-readiness.md).

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
