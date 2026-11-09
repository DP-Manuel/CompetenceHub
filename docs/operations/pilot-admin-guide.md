# Portaladministration für Manuel

Stand: 09.11.2026. Lokaler Kandidat, noch kein freigegebener VPS-Betrieb.

- **Zugänge:** Gesamtzahl, Aktivierungsstand, Rollen und stabile Coach-UUID
  kontrollieren. Aktiver Datensatz bedeutet nicht automatisch abgeschlossene MFA.
- **Einladen:** bestätigten Anzeigenamen, persönliche Arbeits-E-Mail und genau
  eine Rolle wählen: Intern, Kalenderprüfung oder Coach. Für Coach ist eine
  bestätigte bestehende Coach-UUID zwingend. Kein Abgleich nur anhand des Namens.
- Ohne freigegebene Zustellung bleibt die Aktion serverseitig gesperrt. Ein
  vorgemerkter Outbox-Eintrag ist noch kein Empfangsnachweis.
- Bereits aktive Konten werden nicht erneut eingeladen. Eine neue Einladung
  widerruft offene ältere Links; eine geänderte Rolle benötigt einen getrennten
  geprüften Verwaltungsvorgang, keine stille Neuzuordnung.
- **Hilfe:** Admin-Einführung freiwillig starten; Escape beendet sie ohne Speichern.
- Die Übersicht bestätigt nur die aktuelle Datenbankabfrage. Sie ist weder
  vollständiger Auditviewer noch Nachweis für TLS, Sicherung oder VPS-Gesundheit.
- Der erste reale Admin bleibt ein gesonderter gesicherter Bootstrap-Schritt.
  Die neue Einladungsoberfläche vergibt niemals die Adminrolle.

## Störung

Zeitpunkt, betroffenen Bereich und bereinigten Fehlertext notieren. Keine
Passwörter, Cookies, Aktivierungslinks, MFA-Seeds oder Recovery-Codes weitergeben.
Bei verdächtiger Freigabe betroffene Veröffentlichung zurückziehen, nicht die
Datenbank zurückspielen. Für Betriebsstörungen gilt der
[gebündelte Freigabe-/Rollbackplan](integrated-staging-pilot-2026-11-09.md).
