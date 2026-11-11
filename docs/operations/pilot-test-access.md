# Testzugang Zum Privaten V1-Piloten

Stand:11.11.2026. Technischer VPS-Pilot abgenommen; Manuels Bedienabnahme folgt
später. Keine echten Zugänge, neuen Rollen, Installation oder Datenübernahme.

## Für Manuel

Der Starter `deploy/scripts/open-vps-pilot.ps1` öffnet die vier vorhandenen
synthetischen Konten automatisch. Die Anmeldung nutzt die normalen Passwort-/
MFA-Prüfungen, keine Umgehung. Du musst keine Passwörter oder Codes kennen.

1. Auf demselben Rechner unter deinem bisherigen Windows-Benutzer PowerShell7
   verwenden. Administratorrechte sind nicht nötig. Ein noch wartendes altes
   Updatefenster vorher einmal mit Enter beenden; danach dasselbe Fenster nutzen.
   Enter schließt nur dessen lokalen Tunnel, nicht die VPS-Dienste.
2. Den im Abschluss vollständig angegebenen, geprüften Starterbefehl mit `-Open`
   und seinem exakten `-ExpectedSourceCommit` ausführen. Arbeitsverzeichnis beliebig.
   Nicht den Installer oder das V1-Resume erneut ausführen.
3. Bis zu31 Sekunden wird ein frisches MFA-Zeitfenster abgewartet. Es erscheinen
   vier getrennte Firefox-Rollenfenster und ein öffentlicher Kalender. Die Titel
   heißen Admin, Prüfer, Coach1 und Coach2; tatsächliche Sitzung/UUID/Rolle werden
   geprüft, nicht aus der Reihenfolge der Browserfenster geraten.
4. Das Starterterminal während des Tests offen lassen. Erfolgszeile:
   `PILOT_ACCESS=PASS ADMIN=OPEN REVIEWER=OPEN COACH_1=OPEN COACH_2=OPEN PUBLIC_CALENDAR=OPEN`.
   Einmal Enter beendet diese Testfenster und nur einen vom Starter selbst
   geöffneten Tunnel. Ein vorher vorhandener fremder Tunnel wird nicht beendet.

Kein sudo-, Datenbank-, GPG-, USB- oder Testpasswort eingeben. Keine Sitzung
aufzeichnen oder transkribieren. Bei STOP nur den bereinigten Fehlertext melden,
keine privaten Dateien, Cookies, Passwörter oder Recovery-Werte schicken.

## Testrollen Und Adressen

| Fenster | Wofür |
| --- | --- |
| Admin | Zugänge, Rollen, Sperren, Audit und Übersicht prüfen |
| Prüfer | Eingereichte Kalenderangebote prüfen, Änderungen anfordern/freigeben |
| Coach1 | Eigene Entwürfe und Termine bearbeiten/einreichen |
| Coach2 | Unabhängiger Coach zur Prüfung der Zugriffstrennung |
| Öffentlicher Kalender | Nur freigegebene Veranstaltungen, Details, ICS und Anfrageentwurf |

Portal: `https://localhost:8447/portal/`.
Kalender: `https://localhost:8447/portal/calendar-public.html`.
Für den Test die automatisch geöffneten Firefox-Fenster verwenden. Deren
Zertifikatsvertrauen gilt nur in den isolierten Testprofilen. Keine Warnung im
normalen Browser wegklicken oder das Zertifikat global installieren.

Die früheren festen lokalen Demo-Adressen und `123456` gelten hier nicht.
Der Starter liest ausschließlich die zwei originalen, privaten DPAPI-Kopien aus
dem bestätigten Pilotlauf `e89ce1ef18b14ad38bff9fcbf0199854`, prüft unveränderte
Dateien/private Zugriffsrechte und verarbeitet Werte nur im lokalen Prozess.
Keine Ausgabe, Zwischenablage oder neue Klartext-Zugangsliste. Recovery-Codes
werden nicht verbraucht; keine Schlüsselrotation/Neuerzeugung oder GPG-Aktion.
Nach Abmeldung kannst du die Fenster schließen und nur den Starter erneut nutzen.

## Test Für Später

- Admin: Übersicht und Zugangsverwaltung ansehen; keine echten Personen einladen.
- Coach1: synthetischen Entwurf erstellen/bearbeiten und zur Prüfung einreichen.
- Prüfer: Änderungen anfordern, danach die überarbeitete Fassung freigeben.
- Coach2: prüfen, dass fremde Coachangebote nicht bearbeitbar sind.
- Kalender: Veröffentlichung, Details, mehrtägige Darstellung, ICS/Anfrage prüfen.

Der Starter selbst verändert nur normale Anmelde-/MFA-/Sitzungs-/Auditzustände.
Keine neuen Benutzer, Rechte, Coachzuordnungen oder Geschäftsdaten. Manuelle
Teständerungen an vorhandenen synthetischen Angeboten bleiben bewusst erhalten.
Einladungsversand bleibt geschlossen; reale Aktivierung ist ein separates Gate.
Privates Zertifikat unverändert bis24.11.2026 gültig; danach nicht umgehen.

## Technischer Nachweis

133 gezielte Regressionen inklusive private Kopien unverändert, synthetische
Identitäten, genaue Rollen trotz vertauschter Browserkontexte, kein Passwort-
Dialog, keine Installer-/Root-/GPG-Aufrufe und Ablehnung einer falschen Runtime.
Aktuelles V1-Asset und ursprüngliche CA/Hostname/Leaf müssen vor Lesen der
Anmeldedaten passen. Temporäre Browserdateien liegen im eigenen privaten
Operatorverzeichnis; kein globaler Vertrauensspeicher oder bestehendes Profil.

Native Ubuntu/PostgreSQL-/Firefox-Probe mit vollständig synthetischen Daten:
vier echte Passwort-/TOTP-Logins, genaue Sitzung/UUID/Rolle, fünf getrennte
Browserkontexte,16 fachliche Tabellen/Zuordnungen unverändert, weiterhin vier
Konten. Erwartete Auth-/Sitzungs-/Auditzustände verändert, kein Nullrückstand
behauptet. Eigener Container vollständig entfernt. Report
`.tmp/ch-pilot-proof-d8632d33687449e5ab7044456e109bf6/result.json`, SHA-256
`982241442bba790d7463f3af63d6240c4ed1e420381390f153d101db957a1948`.
Die tatsächlichen VPS-Zugangskopien wurden dafür nicht entschlüsselt. Manuels
Starterlauf/Bedienabnahme ist noch offen; technische V1-Abnahme bleibt gültig.
