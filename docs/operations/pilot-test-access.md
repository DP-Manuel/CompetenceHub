# Testzugang Zum Privaten V1.1-Piloten

Stand:13.11.2026. Technischer VPS-Pilot abgenommen. Manuel hat Admin und wesentliche
Coachfunktionen auf V1 positiv geprüft; V1.1 ist jetzt tatsächlich installiert,
technisch abgenommen und vier Rollenfenster sind bereits angemeldet geöffnet.
Manuels erneute Bedienabnahme ist der nächste Block.
[Fester Einstieg für alle künftigen Tests](../handoffs/PORTAL_TESTZUGAENGE.md).
Keine echten Zugänge, neuen Rollen, Installation oder Datenübernahme.

Wiederöffner bindet tatsächliche V1.1-Receipt6554531a…/SHAd25223b0… und
`calendar-form.mjs`/SHA51b456dd…; vollständige Werte im Code und
[V1.1-Abschluss](portal-v11-ux-2026-11-13.md#v11-tatsächlich-abgenommen).
Frühere V1-Pins/Timeouts unten sind historische Befunde. Kein erneutes Update.

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

## Starter-Timeout Am 13.11.

Manuels erster gemeldeter Starterlauf erreichte die Browserphase und stoppte mit
`TimeoutError`. Die alte Meldung enthält weder Rolle noch Einzelschritt; daraus
lässt sich nicht bestimmen, ob und welche Anmeldung bereits abgeschlossen war.
Keine erneute Anmeldung durch den Assistenten, kein Reset oder Recovery-Versuch.
Frische Prüfung ohne Anmeldung: ursprüngliche CA/Hostname/Leaf, V1-Asset und
Firefox-Loginseite PASS; initiale Sitzung401, keine JavaScript-Fehler.

Ein konkreter Starterfehler ist mit der unveränderten paketierten V1-Oberfläche
und einem rein synthetischen lokalen HTTP-Server reproduziert: Die statische
Loginmaske ist schon sichtbar, während die initiale Sitzungsabfrage noch läuft.
Eine späte401 nach erfolgreichem Passwortschritt schließt die MFA-Maske wieder.
Dies erklärt einen möglichen Timeout, beweist aber nicht den genauen Schritt des
alten uninstrumentierten Benutzerlaufs.

Korrektur nur im lokalen Browserstarter: erst initiale GET-Sitzungsantwort401 und
die anschließende Fokussierung der Loginmaske abwarten, dann einmal Passwort und
einmal TOTP senden (vertragsgemäß HTTP202/204). Codes erst nach sichtbarer MFA-Eingabe erzeugen. HTTP-Fehler
stoppen sofort ohne Wiederholung. Feste Meldungen `PILOT_ACCESS_STEP ROLE=... STEP=...`
benennen Start, Sitzungsprüfung, Passwort, MFA, Portal und öffentlichen Kalender.
Browser-Timeouts nennen Rolle/Schritt statt vertraulicher Browser-Fehlerdetails.
Keine Screenshots, Traces, Zugangswerte oder Response-Inhalte protokollieren.

Die neue lokale Browserregression prüft den verspäteten401-Rücksprung sowie
Passwort-/MFA-401/429 und Session503; keine Verbindung zur echten Datenbank und
keine echten Zugangskopien. Ein korrigierter manueller Starterlauf bleibt der
nächste Prüfblock, nicht eine bereits behauptete Bedienabnahme.

Abschluss13.11:140 gezielte Regressionen PASS. Erneute native lokale
PostgreSQL-/TLS-/Firefox-Probe PASS: vier echte synthetische Passwort202-/
TOTP204-Logins, genaue UUID/Rolle, öffentlicher Kalender,16 fachliche Tabellen
unverändert, vier Konten erhalten. Normale Auth-/Sitzungs-/Auditänderungen,
keine ursprünglichen privaten Schlüssel-/Login-Dateien gelesen, kein VPS-Eingriff.
Eigener Container entfernt und unabhängig nicht mehr vorhanden. Report
`.tmp/ch-pilot-proof-cba4ffac48044e82bfec77abe0d01632/result.json`, SHA-256
`982241442bba790d7463f3af63d6240c4ed1e420381390f153d101db957a1948`.
Kontext-/Linkprüfung und `git diff --check` PASS. Pages wird nur manuell
veröffentlicht; ein Push dieser lokalen Korrektur löst kein Deployment aus.
