# Portaladministration für Manuel

Stand: 10.11.2026. Der private synthetische VPS-Pilot ist abgenommen.
Die folgenden erweiterten Verwaltungsaktionen gehören zum lokalen V1-Update;
sie sind noch nicht auf dem VPS installiert. Keine echten Konten aktivieren.

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
- **Verwalten:** Konto auswählen, Änderung und gegebenenfalls die bestätigte
  Rolle/Coach-UUID wählen, prüfen und bestätigen. Sperren oder Rollenwechsel
  beenden alle Sitzungen und offenen Zugangslinks. Wiederfreigeben erfordert
  eine neue Anmeldung; eine Erstaktivierung wird dadurch nicht ersetzt.
- **Schutz:** Der eigene Adminzugang bleibt unverändert. Der letzte aktive
  Administrator darf nicht entfernt werden. Bei einem Konflikt aktuellen
  Kontostand laden, bei abgelaufener Bestätigung erneut mit MFA anmelden.
- **Einladung widerrufen:** Für noch nicht aktivierte Konten den offenen Link
  ungültig machen. Neu vorbereiten übernimmt die bestätigten Angaben in das
  Formular; Versand bleibt bis zur separaten Freigabe gesperrt.
- **Nachvollziehen:** Im Verwaltungsdialog administrative Änderungen laden.
  Gezeigt werden nur Zeitpunkt, Aktion und Ergebnis, keine Zugangsdaten.
- **Hilfe:** Die erste Einführung startet nach abgeschlossener MFA-Einrichtung.
  Überspringen und Neustart unter Hilfe sind jederzeit möglich. Fortschritt gilt
  nur im selben Browser-Tab; Abmelden entfernt ihn. Kein Tracking.
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
