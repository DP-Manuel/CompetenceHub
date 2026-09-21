# CAL-1 UI Security Review

Stand: 18.09.2026

Scope: lokale CAL-1-Coach-/Reviewer-Portaloberfläche, Capability-/Themenprojektion,
synthetische Browserfixture und angrenzende Protected-API-Verträge.

## Ergebnis

Keine offenen High- oder Critical-Findings im geprüften lokalen Slice.

## Geprüfte Grenzen

| Risiko | Evidenz | Ergebnis |
| --- | --- | --- |
| Nur clientseitige Autorisierung | Capability-Endpunkt steuert Darstellung; alle Endpunkte prüfen Session, Rolle und Coachownership erneut | kein Finding |
| IDOR/fremde Coach-ID | Coachlisten werden über `portal_user_id` begrenzt; fremde Detail-ID liefert generisches `404`; UI sendet keinen Coachfilter | kein Finding |
| Reviewer-Eskalation | Reviewer erhält Queue/Entscheidung, aber keine Create-/Draft-Rechte; negative API-/Fixture-Tests | kein Finding |
| Versteckte Aktionen | nicht autorisierte Coach-/Reviewer-Knoten werden aus dem aktiven DOM entfernt | kein Finding |
| Stale overwrite | Detail-ETag bleibt flüchtig; jede Mutation sendet `If-Match`; `409` verlangt bewusstes Nachladen | kein Finding |
| Doppelauslösung | Form-Busy-Guard und Aktionsschlüssel; Create besitzt Request-UUID; keine automatische Mutationswiederholung | kein Finding |
| XSS/DOM injection | dynamische Werte ausschließlich über `textContent`, `value` und DOM-APIs; kein `innerHTML` | kein Finding |
| CSRF/Origin | vorhandener Same-Origin-Requestpfad, Session-CSRF und exakte serverseitige Originprüfung | kein Finding |
| Cache/Token leakage | authentifizierte API/Portalantworten `no-store`; kein Local-/Session-Storage; Tokens nicht in URLs/DOM | kein Finding |
| Rollen-/Sitzungswechsel | flüchtige Listen, Details, Dialoge und getrennte DOM-Knoten werden bei Logout, Ablauf und Re-Login geleert | Finding lokal behoben |
| Fehlerdetails | Problemcodes werden auf generische deutsche Meldungen abgebildet; keine Exceptions oder Datenbankdetails | kein Finding |

## Verbleibende Gates

- Manuelle Browserprüfung von Accessibility Tree, Fokus, 390 Pixel und 200 Prozent.
- Native Staging-UI-Abnahme erst nach separater Freigabe; keine realen Rollen oder Daten.
- Reale Rollenvergabe, Coachmapping, öffentliche Website und Produktion benötigen
  weiterhin ihre eigenen Security-, Datenschutz- und Betriebsfreigaben.
