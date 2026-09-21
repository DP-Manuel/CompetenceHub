# CAL-1 Browser Acceptance Checklist

Stand: 18.09.2026

Status: lokale Abnahme abgeschlossen. Manuels bereits bestaetigte Rundgaenge
wurden durch einen frischen, wiederholbaren Edge-Lauf mit 57 Browserpruefungen
ergaenzt. Nur so tatsaechlich gepruefte Punkte sind markiert.

## Start

1. [x] In `apps/webapp` `powershell -ExecutionPolicy Bypass -File .\scripts\run-browser-acceptance.ps1` starten.
2. [x] Nur die im Terminal genannten `example.invalid`-Identitäten, das synthetische Passwort und den synthetischen MFA-Code verwenden.
3. [x] Prüfen, dass die Seite ausschließlich unter der angezeigten lokalen Loopback-URL läuft.

## Coach

4. [x] Als `synthetic.coach-empty@example.invalid` anmelden: Kalenderbereich sichtbar, Empty State verständlich, kein fremdes Angebot sichtbar.
5. [x] Als `synthetic.coach@example.invalid` anmelden: Draft, eingereichtes, veröffentlichtes und zur Änderung zurückgegebenes Angebot mit Textstatus sichtbar.
6. [x] Einen neuen Draft mit allen Pflichtfeldern anlegen; Doppelklick erzeugt nur einen Eintrag.
7. [x] Den Draft erneut öffnen, bearbeiten und speichern; Werte und Status bleiben korrekt.
8. [x] Draft einreichen; Bearbeiten verschwindet und Status lautet „Zur Prüfung eingereicht“.
9. [x] Ein zulässiges Angebot zurückziehen; Status und verfügbare Aktionen aktualisieren sich.
10. [x] Beim Änderungsfall die Reviewnotiz lesen, „Neue Revision bearbeiten“ wählen und Revision 2 als Draft erhalten.
11. [x] Beim veröffentlichten Angebot eine neue Revision beginnen; die dargestellte veröffentlichte Fassung wird nicht heimlich überschrieben.
12. [x] Stale-ETag-Fall mit zwei Fenstern erzeugen: zweites Speichern zeigt Konflikt, wiederholt nicht automatisch und „Aktuellen Stand laden“ stellt den Serverstand her.

## Reviewer Und Negative Rollen

13. [x] Als `synthetic.reviewer@example.invalid` anmelden: nur Prüfliste, keine Coach-Bearbeitung und keine Firmenverwaltung sichtbar.
14. [x] Eingereichtes Angebot öffnen: Coach-Anzeigename, Thema, Titel, Zeitraum, Format, öffentliche Daten, Revision und Status sind verständlich; keine UUID wird angezeigt.
15. [x] „Änderungen anfordern“ ohne Hinweis wird abgewiesen und fokussiert den Hinweis; mit Hinweis wird die Entscheidung genau einmal gespeichert.
16. [x] In einem frischen Lauf „Veröffentlichen“ prüfen; Angebot verschwindet aus der Queue und erhält den veröffentlichten Status.
17. [x] Als `synthetic.internal@example.invalid` anmelden: Firmenbereich vorhanden, keine Kalender-Prüfliste und keine versteckten Reviewer-Aktionen im Accessibility Tree.
18. [x] Als `synthetic.company-contact@example.invalid` anmelden: kein geschützter CAL-1-Arbeitsbereich nutzbar.
19. [x] Als `synthetic.admin@example.invalid` anmelden: Firmen, dokumentierter CAL-1-Administrationsscope und Prüfliste sichtbar; keine undokumentierten Rechte erscheinen.

## Bedienbarkeit Und Regression

20. [x] Coach- und Reviewer-Workflow vollständig nur per Tastatur bedienen; Fokus bleibt sichtbar und Dialoge schließen per Escape.
21. [x] Bei 390 CSS Pixel Breite prüfen: keine horizontale Seitenüberbreite, keine abgeschnittenen Texte, Hauptziele gut bedienbar.
22. [x] Bei 200 Prozent Browserzoom prüfen: keine Überlagerungen, Dialog und Aktionen bleiben erreichbar.
23. [x] Betriebssystem/Browser auf reduzierte Bewegung stellen: keine automatische oder störende Bewegung.
24. [x] Fehlerzustand durch kurzzeitiges Stoppen der lokalen Fixture beziehungsweise ungültige Eingabe prüfen: generische Meldung, keine technischen Details.
25. [x] Logout und Re-Login zwischen Coach, Reviewer und Internal prüfen; Bereiche und Fehlerzustände wechseln korrekt und CSRF-geschützte Änderungen funktionieren weiter.
26. [x] Bestehende Firmen-/Kontakt-, Login-, MFA-, Recovery- und Re-Login-Abläufe stichprobenartig prüfen.

## Ergebnis

- Durchgeführt von: Manuel (erster manueller Rundgang) und Codex (wiederholbarer
  lokaler Edge-Lauf).
- Datum: 18.09.2026.
- Browser/Version: Microsoft Edge 153.0.4234.32, headless ueber Playwright.
- Viewport/Zoom: 1440 x 1000; 390 x 844; 200-Prozent-Layout als 640-CSS-Pixel-
  Viewport bei Device Scale Factor 2.
- Evidenz: 57/57 Browserpruefungen, 18/18 fokussierte Fixture/UI-Tests und
  384 lokale Tests mit 17 erwarteten Staging-Skips.
- Geschlossene Befunde: Admin-Themenauswahl, irrefuehrender Status bereits
  zurueckgezogener Karten sowie ungenaue asynchrone Browser-Wartebedingungen.
- Offene Befunde: keine innerhalb dieser lokalen synthetischen Browserabnahme.
- Fixture/Temporaerkontext: nach dem Lauf gestoppt und entfernt.
- Go/No-Go fuer native Staging-UI-Abnahme: Go fuer einen separat freizugebenden,
  weiterhin rein synthetischen Staging-Gate; keine Freigabe fuer reale Rollen,
  Daten, Website-Anbindung oder Deployment.
