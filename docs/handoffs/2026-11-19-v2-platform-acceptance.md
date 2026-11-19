# Competence Hub V2: Gesamtabnahme

**Status:** Lokal integriert, mit synthetischen Daten technisch geprüft. Die
gemeinsame fachliche Abnahme durch Manuel und Janay steht aus. Kein V2-Deployment,
keine Datenbankänderung auf dem VPS, keine echten Zugänge, kein Versand und keine
Änderung an IONOS oder GitHub Pages. Frau Hupp bleibt pausiert; veröffentlichte
Inhalte und Rechte bleiben unverändert.

## Was Zusammenarbeitet

| Rolle | Was sie im integrierten System sieht und tut |
| --- | --- |
| Besucher | Website-Angebot und Coachprofil führen zum gefilterten Kalender. Dort sind nur freigegebene Veranstaltungen sichtbar. Der öffentliche Anfrageentwurf schreibt keine Daten. Der Login übergibt nur die Angebots-ID. |
| Coach | Eigene anstehende Veranstaltungen, Entwürfe, eingereichte Angebote, Änderungsbedarf und veröffentlichte Termine. Kapazitätsstand der eigenen Angebote ohne Firmendetails. |
| Unternehmen | Verfügbare Veranstaltungen, eigene Vormerkungen und vergangene Vorgänge, Plätze, Fristen und Rückfragen. Ein konkreter Einstieg lässt sich auf alle Veranstaltungen zurücksetzen. |
| Reviewer | Ein Überblick für CAL-1 und CAL-2: Angebotsprüfung, entscheidungsreife Vormerkungen, Rückfragen, Fristen, Schwelle, Auslastung und betroffene Revisionen. Die Prüferrolle bleibt vom Admin getrennt. |
| Admin | Bestehende Benutzer-, Rollen-, Zuordnungs- und Einladungsübersicht, ergänzt um Betriebs- und Audit-Kategorien. Keine Anzeige von Zugangswerten oder Audit-Nutzlasten. |

Astro bleibt statisch. Nur der lokale Demonstrationsmodus bindet seinen eigenen
Build an dieselbe geschützte Loopback-Anwendung. CAL-1 und CAL-2 teilen sich
PostgreSQL, Angebotsrevisionen und die bestehende Ereignishistorie. Aufgaben
werden daraus abgeleitet; es gibt keine zweite Ereignistabelle. Die bestehenden
optionalen, erneut aufrufbaren Touren und die V1.2-Formularregeln bleiben nutzbar.
MFA, RBAC, Origin/CSRF, Session und Audit bleiben bestehen. Die neue Übersicht
liest einen konsistenten Snapshot; sie wird beim Öffnen/Neuladen aktualisiert.

## Demo Starten

**Ein Terminal: PowerShell.** Voraussetzungen: Docker Desktop mit Linux-Engine
und vorhandenem Image `postgres:16-bookworm`, die lokale Webapp-Umgebung mit
Playwright/Firefox, Projekt-Node und installierte Astro-Abhängigkeiten.

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp'
.\.venv\Scripts\python.exe scripts/run-cal2-local.py
```

Bei `V2_PLATFORM=READY` öffnen sich fünf isolierte Firefox-Fenster: Coach,
Reviewer, Firma A, Firma B und Admin. Firma A hat zusätzlich den Website-Tab.
Die lokale URL wird ausgegeben. **Keine Zugangsdaten eingeben, weitergeben oder
in den Chat kopieren.** Das wegwerfbare Testzertifikat ist auf die lokalen
Testfenster beschränkt; die VPS- und System-Vertrauenseinstellungen bleiben
unverändert. **R + Enter** testet den Neustart mit Datenpersistenz. **Enter**
beendet die Sitzung; erwartet: `CAL2_CLEANUP=PASS`.

## Eine Gemeinsame Sitzung

1. **Coach:** In Kalenderangebote einen Workshop anlegen: online, Start in
   acht Tagen, Ende am Folgetag, fünf Plätze, Prüfschwelle drei,
   Entscheidungsfrist zwei Tage vor Beginn. Als Entwurf speichern und einreichen.
2. **Reviewer:** Unter Prüfliste veröffentlichen. Vor Veröffentlichung darf der
   Workshop nicht im Kalender oder bei Unternehmen erscheinen.
3. **Firma A:** Im Website-Tab über **Demo-Angebot**, **Coachprofil** und
   **Veranstaltungen im Kalender** navigieren. Titel, Mehrtagesansicht und Link
   zurück zum Coach prüfen. Anfrageentwurf und Portal-Vormerkung unterscheiden.
   Im Portal muss genau der gewählte Workshop vorausgewählt sein.
4. **Firmen A und B:** B öffnet das Formular zuerst. A merkt zwei Plätze vor.
   B versucht vier Plätze aus seinem offenen Formular, erhält eine verständliche
   Ablehnung und merkt danach zwei vor. B darf As Vorgang nicht sehen.
5. **Reviewer und A:** In **Vormerkungen prüfen** eine Rückfrage stellen.
   A antwortet im eigenen Vorgang, testet Abbrechen mit ungespeicherten
   Änderungen und speichert drei statt zwei Plätze. Übersicht neu laden.
6. **Reviewer:** As Vorgang positiv prüfen. Das ist keine Buchung. B zieht
   seine noch offene Vormerkung zurück. Beide Verläufe bleiben sichtbar. Optional
   mit einer erneuten B-Anfrage auch Ablehnung und den Filter dafür prüfen.
7. **Coach und Admin:** Coach prüft den eigenen Termin und die Belegung;
   keine Firmennachrichten. Admin prüft Rollen, Zuordnungen und Betriebsübersicht.
   Eine wesentliche neue Revision mit belegten Plätzen darf nicht still die alte
   Publikation ersetzen. Tour und Hilfe bei Bedarf erneut öffnen.
8. **Gesamtprüfung:** Auf 390 px oder bei 200 % nachsehen, dann mit **R + Enter**
   neu starten und Status/Verlauf wiederfinden. Beim Beenden muss die lokale
   Bereinigung erfolgreich sein.

## Testnachweise

Der zusammenhängende Prüflauf (`--verify`) verwendet echtes isoliertes
PostgreSQL und Firefox. Er deckt Website-Übergabe und Rücklink, CAL-1-Freigabe,
zwei Firmen, parallele Anfragen auf den letzten Platz, Idempotenz, Rechte,
Revisionen, Datenschutz und Persistenz nach einem unterbrochenen Schreibzugriff
ab. 390 px, nativer 200-%-Zoom, Tastatur, Fokus und zugängliche Namen wurden
geprüft; kein separater NVDA-/JAWS-Lauf. Für die öffentlichen Astro-Builds
wurden Byte-Parität zur Ausgangsbasis (Produktion 55/55; Preview 59/59), Links
und lokale Browser-Smokes nachgewiesen. Der versionsgebundene Nachweis liegt
beim Releasepaket unter `release-artifacts/v2-platform/`.

## Entscheidungen Für Janay Und Manuel

- Platzbindung, Fristablauf und Eskalation sowie Schwelle als Hinweis bestätigen.
- Festlegen, wann eine Termin-/Kapazitätsänderung eine Rückbestätigung oder
  Absage erfordert. Bis dahin keine automatische Umbuchung.
- Fachliche Vertretung und mögliche spätere Benachrichtigungen festlegen.
  Interne Aufgaben funktionieren bereits; es gibt keinen Versand.
- Aufbewahrung und Löschung vor echten Daten klären. Ein verbindlicher
  Buchungsschritt bleibt ein eigenes Vorhaben.

Die [ausführliche Fachliste](2026-11-19-cal2-pilot-acceptance.md#einmalige-entscheidungsliste)
hält verbindliche Beschlüsse und Demo-Regeln auseinander. Festhalten: wer
abgenommen hat, was bestätigt ist und welche Abweichungen offen bleiben.

## Privates Staging Und Echte Zugänge

Der [Paket- und Rollbackvertrag](../operations/portal-v2-private-staging.md)
bindet ZIP und Nachweis an den getesteten Commit. Letzter belegter VPS-Stand:
V1.2 `5a555e9a9aae`, Schema bis `0006`, 27 Tabellen, sechs gesunde Dienste und
das private Zertifikat bis **30.11.2026, 19:09:39 MEZ**. Kein neuer Live-Check
in diesem Sprint. Vor einem freigegebenen Staging-Lauf müssen aktueller TLS-,
Dienst- und Datenstatus sowie ein geeigneter aktueller Restore nachgewiesen sein.
`0007` bis `0011` sind nur für einen getrennten, geprüften Klon vorgesehen.
Die alte V1.2-Instanz samt Originaldaten bleibt der Rückfallstand. Keine
Rückmigration am Original. Echte Identitäten, Rollen, Coach-Import und
Einladungen benötigen weiterhin eigene Freigaben; App-DNS, dauerhaftes HTTPS
und SMTP bleiben extern offen.

**Ein nächster Block:** Manuel und Janay führen diese Gesamtabnahme in einer
Sitzung durch. Eingaben: lokal gebundener Bericht und Startbefehl. Ergebnis:
Bestätigung der beobachteten Wege, dokumentierte Fachentscheidungen und ein
gemeinsames Go/No-Go zur Vorbereitung des separaten geschützten Betriebsfensters.
