# CAL-1 Browser Acceptance Handoff

Stand: 18.09.2026

## Abschlusszustand

- Die lokale synthetische Browserfixture startet pro Lauf auf einem freien
  Loopback-Port und ist nach der Abnahme wieder beendet.
- Kein Commit, Push, Deployment, reales Konto, reale Rolle oder Echtdatum.
- Vollstaendige lokale Suite: 384 bestanden, 17 erwartete Staging-Skips.
- Wiederholbarer Edge-Lauf: 57/57 Browserpruefungen bestanden.
- Fokussierte Fixture/UI-Regression: 18/18 bestanden; `compileall` gruen.
- Migration/API-Staging-Gate bleibt 17/17 bestanden; keine erneute
  Staging-Ausfuehrung in dieser Browserrunde.

## Im Browser bestaetigt

- Loopback-Start und synthetische Zugangsdaten.
- Coach A sieht die vier Statusfaelle und kann einen Draft bearbeiten/speichern.
- Coach ohne Angebot zeigt den erwarteten Empty State.
- Reviewer A sieht Queue und vollstaendige Angebotsprojektion.
- Internal A sieht Firmen, aber keine Calendar-Review-Rechte.
- Firmenkontakt bleibt ohne geschuetzten CAL-1-Arbeitsbereich.
- MFA-Einrichtung und Recovery-Code-Hinweis funktionieren.

## Lokal behoben

1. Login -> MFA -> Portal brach ab, weil der Fehler-Cleanup auf aus dem DOM
   entfernte Sicherheitsknoten zugriff. Cleanup ist nun nulltolerant und leert
   auch gehaltene Knoten direkt.
2. Admin lud beim Bearbeiten keine Topics. Der Client laedt nun Topics auch
   fuer den dokumentierten Admin-Scope; Neuanlage bleibt Coach-spezifisch.

## Geschlossener Admin-Befund

Eine frische Fixture lieferte fuer Draft, Published und Changes Requested
jeweils `lifecycle_status=active` und Revision 1; die erwarteten Aktionen waren
im echten Browser vorhanden. Der fruehere Screenshot entstand nach Mutationen
in einer langlebigen Fixture: zurueckgezogene Karten behielten optisch nur den
alten Workflowstatus und boten deshalb richtigerweise keine Aktionen. Die
Karte priorisiert nun `lifecycle_status=withdrawn` und zeigt
`Zurueckgezogen`. Draft bleibt direkt editierbar; Published und Changes
Requested erzeugen Revision 2 als Draft; In Review bleibt unveraenderlich und
bietet nur die erlaubte Ruecknahme.

Die Admin-Themenauswahl wird vor den Angeboten geladen und nach dem Einfuegen
der Optionen explizit ueber den Topic-Wert gesetzt. API-Liste, Detailprojektion
und Dialogauswahl wurden im Edge-Lauf gegeneinander geprueft.

## Browserchecklisten-Stand

- Alle 26 Punkte sind mit manueller und/oder wiederholbarer Browser-Evidenz
  bestanden.
- 390 CSS Pixel, 200-Prozent-Layout, Tastatur, sichtbarer Fokus, Escape,
  Reduced Motion, generischer Fehlerzustand und stale-edit wurden ausdruecklich
  geprueft.
- Keine offenen lokalen Browserbefunde.

## Rollenentscheidung

- `internal`: Firmen-/Kontaktarbeit, keine Calendar-Freigabe.
- `calendar_reviewer`: Pruefliste und Reviewentscheidungen.
- Janay soll spaeter voraussichtlich `internal` plus `calendar_reviewer`
  erhalten; keine Person ist im Code fest verdrahtet.
- `admin`: technischer Vertretungs-/Notfallumfang, nicht zwingend der
  taegliche Freigabeprozess.

## Naechstes Gate

Genau ein empfohlener naechster Block: separat freizugebende native
Staging-UI-Abnahme mit ausschließlich synthetischen Identitaeten, Cleanup,
Nullrueckstand und unveraenderter Dienstgesundheit.

## Stop-Grenze

Vor Abschluss der lokalen Browserabnahme keine native Staging-UI, realen
Rollen, realen Coach-Mappings, Website-Kalenderanbindung oder Produktion.
