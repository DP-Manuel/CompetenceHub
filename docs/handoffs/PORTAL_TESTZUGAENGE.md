# Portal-Testzugänge

Fester Einstieg für Manuel. Keine echten Personen einladen oder zuordnen.
Passwörter, MFA-Seeds, Recovery-Codes und Tokens gehören niemals in diese Datei.

## Stand Und Adresse

Privater VPS: **V1.1 am13.11 tatsächlich installiert und abgenommen**,
Paket38153c1. `VPS_V11_UPDATE=PASS` und `PILOT_ACCESS=PASS` bestätigt.

V1.2 mit vereinfachter Datumsauswahl wird lokal vorbereitet; noch nicht auf dem
VPS. Der offene Tunnel und die vorhandenen Fenster zeigen deshalb weiter V1.1.
Keinen alten Updatebefehl starten. V1.2 benötigt ihr eigenes gebundenes Update-Gate.

Im freigegebenen Updatefenster genügt ein gebundener Befehl: Nach technischer
Abnahme öffnet es die vorhandenen Coach-/Prüfer-/Admin-Fenster bereits angemeldet.
Terminal offen lassen. Jetzt zu **Coach1** oder **Prüfer** wechseln; keine
Zugangsdaten suchen, keine Konten neu anlegen. Die nachfolgenden Starterangaben
betreffen ausschließlich spätere Wiederöffnung und sind auf die tatsächliche
V1.1-Receipt und neue Datumsoberfläche gebunden. Ein Update nicht bloß zum
Wiederöffnen erneut ausführen.

- Portal: `https://localhost:8447/portal/`
- Freigegebener Kalender: `https://localhost:8447/portal/calendar-public.html`
- Nur auf Manuels bisherigem Windows-Rechner/-Benutzer über den SSH-Tunnel.
- Die automatisch geöffneten Firefox-Fenster nutzen. Keine Zertifikatswarnung
  wegklicken, kein globales Zertifikat installieren. TLS gültig bis24.11.2026.

## Einmal Starten

1. PowerShell7 unter demselben Windows-Benutzer öffnen, kein Administrator nötig.
   Arbeitsverzeichnis beliebig. Ein altes wartendes Starterterminal zuvor mit
   Enter beenden; bereits geschlossene Terminals nicht wiederherstellen.
2. Den vollständig gebundenen Befehl in
   `release-artifacts/portal-v11-ux/START-TEST.txt` verwenden. Fehlt diese Datei,
   keinen alten Installer oder geratenen Commit starten, sondern den zuletzt
   geprüften vollständigen Befehl aus dem Projektabschluss anfordern.
3. Der Starter prüft Quellstand, ursprüngliches TLS und akzeptierte VPS-Version.
   Anschließend öffnet er vier bereits angemeldete Rollen und den Kalender.
   Für MFA wartet er gegebenenfalls bis zu31 Sekunden. Kein Passwort eingeben.
4. Erwartet: `PILOT_ACCESS=PASS ...` und `PRIVATE_ACCESS_GUIDE=...`.
   Der letztgenannte lokale Leitfaden enthält die tatsächlichen bestätigten
   synthetischen Login-Adressen. Nur lokal öffnen; nicht an Chat/Git senden.
5. Terminal offen lassen. Enter schließt lokale Testfenster/eigenen Tunnel,
   niemals VPS-Dienste. Ein fremder vorhandener Tunnel bleibt unverändert.

## Welche Rolle?

| Fenster | Bestätigte Kennung im Starter | Zweck |
| --- | --- | --- |
| Admin | `admin` | Zugangsliste und Administration, zusätzlich Kalenderprüfung |
| Coach1 | `coach` | Eigene Termine anlegen, bearbeiten und einreichen |
| Coach2 | `coach_two` | Unabhängiger Coach zur Zugriffstrennung |
| Prüfer | `reviewer` / Rolle `calendar_reviewer` | Änderungen anfordern, Revision freigeben |

Diese Kennungen sind Starter-Zuordnungen, keine geratenen E-Mail-Adressen.
Die tatsächlichen zufälligen synthetischen Login-Adressen stehen ausschließlich
im privaten Leitfaden `PORTAL_TESTZUGAENGE.local.md`, dessen vollständiger Pfad
nach erfolgreichem Start angezeigt wird. Datei wird neu, ohne Überschreiben und
mit geprüftem Windows-Zugriff nur für Manuel/SYSTEM angelegt.

## Anmeldung, MFA Und Wiederaufnahme

Der Starter verwendet die vorhandenen vier Konten und deren normalen Passwort-/
TOTP-Ablauf. Er liest nur die zwei ursprünglichen CurrentUser-DPAPI-Dateien in
`%LOCALAPPDATA%/CompetenceHub/pilot-runs/e89ce1ef18b14ad38bff9fcbf0199854/`:
`synthetic-logins.json.dpapi` und `synthetic-mfa-recovery.json.dpapi`.
Diese sind die getrennte geschützte lokale Zugangskopie, nicht Teil von Git.
Keine Klartext-Passwortliste, keine Recovery-Verwendung oder Schlüsselrotation.

Zwischen Rollen über die getrennten Fenster wechseln. Abmelden über **Abmelden**.
Für erneuten Login die Testfenster mit Enter schließen und denselben geprüften
Starter erneut verwenden. Passwörter müssen nicht manuell rekonstruiert werden.

Wenn eine Originalkopie fehlt, DPAPI nicht zum Benutzer/Rechner passt oder ein
Login abgewiesen wird: STOP. Nur `PILOT_ACCESS_STEP`-/STOP-Zeilen weitergeben.
Kein automatischer Passwortversuch, Recoveryverbrauch, neuer Benutzer oder Reset.
Eine Erneuerung synthetischer Zugänge ist ein gesondert geprüfter Betriebsblock;
aktuell sind die vorhandenen Kopien wiederverwendbar, kein Reset erforderlich.

## Vollständiger Test Nach V1.1-Update

1. Coach1: Kalenderangebote öffnen und einen Entwurf mit Thema/Titel anlegen.
   Beispiel20.11.2026 09:00–16:00, Europe/Berlin, Kapazität10, Prüfschwelle5,
   Entscheidungsfrist19.11.2026 12:00, Preishinweis „Preis nach Abstimmung“.
   Nur verwenden, solange Datum/Frist noch künftig sind; sonst neu wählen.
   Kurzbeschreibung optional; bei Präsenz/Hybrid einen öffentlichen Ort angeben.
2. **Entwurf speichern**, danach **Zur Prüfung einreichen**.
3. Im Prüferfenster Prüfliste aktualisieren, **Angebot prüfen**, Änderungen mit
   Hinweis anfordern. Coach aktualisiert und bearbeitet eine **Neue Revision**.
4. Coach reicht erneut ein; Prüfer veröffentlicht die überarbeitete Revision.
5. Kalender öffnen/aktualisieren, Veranstaltung wählen und
   **Zum Kalender hinzufügen (.ics)** herunterladen. **Anfrageentwurf vorbereiten**
   erstellt nur einen Text, keine Buchung, Reservierung oder E-Mail.
6. Portal: **Hilfe** → Coach-/Prüfer-/Admin-Einführung starten. Kalender:
   **Kalender-Einführung starten**. Jede Tour lässt sich schließen/überspringen
   und erneut starten; sie speichert oder veröffentlicht selbst nichts.

[Technische Zugangsprüfung und Grenzen](../operations/pilot-test-access.md).
