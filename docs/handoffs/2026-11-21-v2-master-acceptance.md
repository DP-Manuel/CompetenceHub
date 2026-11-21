# Competence Hub V2: gemeinsame Gesamtabnahme

**21.11.2026. Lokal, synthetisch.** Ausgangspunkt ist der am 20.11.
abgenommene [Produktstand](2026-11-20-feedback-platform.md). Die öffentliche
Website, Pages, der private VPS, echte Daten, Konten und Zustellung wurden
nicht verändert. Dieser Nachweis ist keine Betriebsfreigabe.

## Was wir gemeinsam prüfen

- **Coach:** Eigene Entwürfe, eingereichte Angebote, Änderungsbedarf und
  freigegebene Termine mit belegten Plätzen. Der Einstieg führt direkt zur
  entsprechenden Liste oder zum Angebot. Der vorhandene Editor bleibt.
- **Reviewer:** Eine Übersicht für CAL-1-Prüfliste und CAL-2-Vormerkungen.
  Aufgaben, Rückantworten, Fristen, belegte Plätze und Revisionskonflikte
  führen zu den vorhandenen Listen, ohne Administratorrechte.
- **Firma und Admin:** Firma sieht nur ihren Vorgang, Frist und Verlauf.
  Die Kundensuche und das separate Privatkundenregister bleiben intern.
  Zugriff, Einladungsstatus und Audit bleiben in der bestehenden Administration.
  Ein Privatkundendatensatz ist kein Portalzugang.
- **Website/CAL-1/CAL-2:** Dieselbe freigegebene Veranstaltung ist über Coach,
  öffentliche Kalenderansicht und angemeldeten Firmenbereich erreichbar.
  Entwürfe, interne Platzbindung und Kundenhistorien erscheinen dort nicht.
  Keine statische Website-Kopie der Portal-Datenbank. Lokal sind Orte und
  Daten als Demo gekennzeichnet; produktive Builds bleiben unverändert.
- **Kommunikation:** Die CAL-2-Vorbereitung liest die vorhandenen Ereignisse
  mit dauerhafter Ereignis-ID und Firmen-/Rollengrenze, ohne zweite Tabelle,
  Nachrichtentexte, Empfängerliste, Versand oder Zustellzusage. Für einen
  Newsletter sind nur die bereits freigegebenen öffentlichen Fakten als
  mögliche Eingabe vorgesehen. Einwilligung, Vorlagen und Zustellung sind offen.

## Eine Vorführung, fünf Fenster

**Terminal: lokale PowerShell.** Docker Desktop (Linux) muss laufen; das
vorhandene `postgres:16-bookworm`-Image sowie Projekt-Python, Astro und
Playwright-Firefox werden wiederverwendet.

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp'
.\.venv\Scripts\python.exe scripts/run-cal2-local.py
```

`V2_PLATFORM=READY` öffnet Coach, Reviewer, Firma A, Firma B und Admin.
Die Website liegt im Firmenfenster von A. Keine echten Zugangsdaten eingeben
oder teilen. Kein externer Zugang nötig.

1. **Coach:** Workshop für einen Termin in acht Tagen anlegen, Präsenz am
   `Demo-Ort A`, fünf Plätze, Prüfschwelle drei, Frist vor Beginn. Entwurf
   speichern und danach einreichen. Er ist noch nicht öffentlich.
2. **Reviewer:** Übersicht aktualisieren und über den Workshop-Titel in die
   Prüfliste wechseln. Nach Freigabe ist der Workshop im Website-Tab unter
   „Aktuelle Termine“ und im Kalender sichtbar. Umkreissuche und Coach-Link
   ausprobieren.
3. **Firmen:** A merkt zwei Plätze vor. B versucht vier; das Portal lehnt ab,
   weil nur drei verfügbar sind. B prüft, dass der Vorgang von A nicht sichtbar
   ist. Keine Aktion erzeugt eine verbindliche Buchung.
4. **Reviewer/Firma A:** „Vormerkungen prüfen“ öffnen, Rückfrage stellen,
   als A beantworten, die Antwort im Cockpit finden und den Vorgang positiv
   prüfen. Status und Verlauf im Firmenfenster nachvollziehen.
5. **Coach/Admin:** Als Coach neue Fassung mit geänderter Zeit einreichen.
   Vorhandene Vormerkungen bleiben an die bisherigen Bedingungen gebunden.
   Admin prüft zulässige Übersicht und legt bei Bedarf einen fiktiven
   Privatkunden ohne Firmenpflicht an.
6. **Persistenz:** Im Terminal `R` und Enter. Nach `CAL2_RESTART=PASS`
   denselben Vorgang und die Rollengrenzen prüfen; Enter beendet die Demo.
   `CAL2_CLEANUP=PASS` bestätigt die Entfernung der Testressourcen.

## Entscheidungen vor echten Daten

1. Preise und Veranstaltungsdaten: genehmigte Zuordnung zwischen Coach,
   Angebotsvariante und Termin; belegte Orte; getrennte interne Honorare und
   freigegebene Einzel-/Gruppenpreise. Die Prüfschwelle ist keine Mindestbuchung.
2. Geschäftsprozess: Platzbindung, Kommunikation bei Terminänderung,
   verbindlicher Übergang, Rechnungen und Service für Privatkunden festlegen.
   Die positive Prüfung bleibt unverbindlich; keine Zahlung oder Buchung.
3. Datenschutz: Aufbewahrung und Löschung, zulässige Daten je Kundenart,
   Empfängerregeln, Mailvorlagen, Einwilligung und Abmeldung separat abnehmen.
4. Betrieb und Rechte: [EDV, TLS, Restore und Onboarding](../operations/portal-v2-pilot-gates-2026-11-21.md).
   Frau Hupp bleibt pausiert; Frau Rappelts Personalvermittlungsprofil bleibt
   unveröffentlicht. Bis zu bestätigten EDV-Daten bleibt `WEBSITE_PORTAL_URL`
   im öffentlichen Betrieb ungesetzt.

Die fachliche Abnahme durch Manuel und Frau Rappelt ist noch offen. Vor dem
geschützten technischen Pilotfenster braucht es separat einen aktuellen
Live-Nachweis, einen unabhängig wiederherstellbaren Sicherungsstand und eine
ausdrückliche, auf Paket und Ziel begrenzte Freigabe.

## Nachweise und Paket

| Prüfung | Ergebnis |
| --- | --- |
| Gesamtablauf Firefox + PostgreSQL 16 | **37 PASS**, einschließlich echter Formularerfassung und Veröffentlichung, Tastatur/Fokus, 390 px, nativer 200-%-Zoom, zwei Firmen, ICS, Revision, parallele letzte Plätze, Datenschutz, Persistenz und Neustart während einer gesperrten Operation. Keine externen Browserzugriffe oder Versand-Outbox; eigener Container und Volume entfernt. |
| Gezielte Regression | **102 Portaltests** und **41 Website-Vertragstests** bestanden. Öffentliche Website-Quellen und Pages-Workflow bytegleich im Git-Vergleich. Kein eigener assistiver Screenreader-Durchlauf. |
| Isolierte Linux-Migrationsprobe | **6 Tests** bestanden. Synthetisch gefüllten V1.2-Stand `0006` als Custom-Dump gesichert, nach SHA-256-Prüfung in eine eigene Datenbank eingelesen, Daten, Schema, Objekt-ACLs und Sequenzstände verglichen. `0007` bis `0012` erfolgreich; Fehler erzwingt transaktionalen Rollback. Original bleibt gleich. Kein Nachweis eines unabhängig entschlüsselbaren *VPS*-Backups. |
| Exaktes V2-Paket | **PASS**, zweimal bytegleich aus derselben Git-Quelle gebaut; vollständige Installation im netzlosen Linux-Container inkl. Paketprüfung, Abhängigkeitscheck, Quellparität und Unit-Syntax. Keine Dienstaktivierung. |

Quellstand: `cb3fb06c442a6459aa2115acc7e5a6451a6a954a`.
Lokal: `release-artifacts/v2-master-20261121/<Quellstand>/private-vps/`
mit `competence-hub-private-v2-<Quellstand>.zip` und SHA-256-Datei.
ZIP-SHA-256: `925ca2c4e4489719b972000929b3f48b367a26d6f62424f95d96701831800876`.
SHA-256 von `tested-source.json`:
`54ebca2bc023ee00a9ed6782e3d7939334414c4c9cf73c43b5a0e30b3a76695b`.
Bericht und Receipt liegen eine Ebene darüber. Kein Paket, Dump oder
Test-Zugang im Git. Das Manifest enthält die geordnete SQL- und Dateiliste
mit Einzelprüfsummen und `deployment_authorized: false`.

Rollback für das spätere, separat freigegebene V2-Fenster: nur den getrennten
V2-Dienst beenden und auf den unveränderten V1.2-Zugang wechseln; keine
Rückmigration am Original. Befehle, Zustände und Abbruchbedingungen stehen
im [Betriebshandbuch](../operations/portal-v2-private-staging.md).
