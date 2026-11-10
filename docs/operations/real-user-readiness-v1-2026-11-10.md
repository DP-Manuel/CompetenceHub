# Persönliche Zugänge: Readiness V1

Stand: 10.11.2026. Owner: Manuel. Lokales synthetisches Update, keine echte
Benutzeraktivierung. Der zuvor abgenommene private VPS-Pilot bleibt Referenz.

## Umsetzung

- Adminliste: Aktivierung, MFA, letzte Anmeldung, offene/verbrauchte/widerrufene/
  abgelaufene Einladung, stabile Coach-UUID und gezielter Verwaltungsdialog.
- Fremde Konten sperren, deaktivieren, wieder freigeben oder genau eine Rolle
  zuweisen. Coach benötigt eine existierende, verfügbare und bestätigte UUID.
  Historische Coachidentitäten und Qualifikationen werden nicht verändert.
- Änderungen erfordern MFA-bestätigte Anmeldung innerhalb zehn Minuten,
  Same-Origin/CSRF, Ziel-UUID, aktuelle Kontoversion und ausdrückliche UI-Bestätigung.
  Eigener Adminzugang, letzter aktiver Admin und ausstehende Aktivierung geschützt.
- Rollenänderung/Sperre und Sitzungs-/Challenge-/Linkwiderruf sind atomar. Offene
  Zustellaufträge werden abgebrochen und ihre vertraulichen Nutzdaten entfernt.
  MFA-Abschluss und Kontozustand sind gegen gleichzeitige Änderungen gesperrt;
  Einladung prüft die aktuelle Adminberechtigung erneut innerhalb der Transaktion.
- Administrative Historie: höchstens20 minimale Einträge pro Ziel, keine Secrets.
  Die Liste ist kein vollständiges revisionssicheres Betriebsmonitoring.
- Einladung prüfen funktioniert ohne Zustellfreigabe und legt noch kein Konto an.
  Widerruf und erneute Vorbereitung nutzen die bestehende verschlüsselte Outbox;
  keine Aktivierungslinks oder Startpasswörter im Adminbereich.
- Rollenübersicht: eigene Status/nächster Termin, erneute Einreichungen, höchstens
  fünf zuletzt freigegebene Veranstaltungen, offene Aktivierungen/Coachzuordnungen.
- Rollentour startet nach erster MFA-Einrichtung, ist überspringbar und über Hilfe
  neu startbar. Sichtbarer Pfeil, Schrittzähler, Tastatur/Fokus und Fortsetzung nach
  Neuladen im selben Tab. Ausschließlich Rolle/Schritt/Status in Tab-History,
  keine Benutzerkennung, Web Storage, Cookies oder externe Nachverfolgung.
  Logout entfernt den Tourfortschritt; kein geräteübergreifender Fortschritt.

Keine Migration, neue Abhängigkeit, Registry-Aktivierung oder Änderung am
öffentlichen Kalendervertrag. Bestehende öffentliche Projektion bleibt getrennt.

## API-Delta

| Route | Zugriff / Ergebnis |
| --- | --- |
| `GET /api/v1/admin/users` | Bestehende begrenzte Liste, zusätzlich Kontoversion, MFA/Anmelde- und minimaler Einladungsstatus |
| `PATCH /api/v1/admin/users/{id}` | Frischer Admin, CSRF/Origin, `action`, `expected_version`, optional explizite `role`/`coach_id`;200 accepted |
| `GET /api/v1/admin/users/{id}/audit` | Admin, maximal20 minimale Einträge |
| `GET /api/v1/admin/coach-mappings` | Admin, maximal100 bestehende UUID-Kandidaten; keine automatische Zuordnung |
| `GET /api/v1/portal/pilot/overview` | Bestehender Rollenbereich; konsistenter Read-only-Snapshot, erneute Einreichungen und begrenzte Freigaben |

Aktionen: `suspend`, `deactivate`, `enable`, `set_role`, `revoke_invitation`.
Veraltete Version/gesperrte Zuordnung409, fehlende/frische Berechtigung403,
unbekanntes Ziel404, ungültige Eingabe400. Keine automatischen Wiederholungen.
`company_contact` liegt außerhalb dieser Verwaltung. Einladungen vergeben
weiterhin keine Adminrolle. Alle geschützten Antworten bleiben `no-store`.

## Zusammenhängendes Updatepaket

Das Paket enthält Runtime, Portal und gemeinsame Kalenderansicht, exakte Locks,
Manifest und SHA-256. Es ist ein Updatekandidat, **kein erneuter Installerlauf**.
Keine Website-/Pages-Veröffentlichung und kein Kopieren privater Konfiguration.
Konkrete Paketbindung und Testergebnisse werden im Abschluss ergänzt.

## Tatsächliche Lokale Abnahme

- Gesamtsuite:1.635 bestanden,30 erwartete Opt-in-/Umgebungsauslassungen,
  312,67 Sekunden. JUnit `.tmp/onboarding-v1-final-tests.xml`, SHA-256
  `dbfb747c392a61acdcd996ea6e2b1b0083b54ab47451259356b72fc2af0064bb`.
- 86 fokussierte Auth/Admin-Tests und35 Releasequellentests bestanden.
- Native PostgreSQL16/Chromium:136 Onboarding-/Verwaltungsprüfungen und46
  vollständige CAL-Prüfungen bestanden; danach3 native PostgreSQL-API-Tests grün.
  Report `release-artifacts/onboarding-v1-20261110/135925408c984baa87c4564b5ca16dac/report.json`,
  SHA-256 `26ca83a736bc335c67f2bd57a87a77cc77610c27189c312256fed323e69decb7`.
- Tatsächlich geprüft: Einladung/Passwort/MFA/Recovery, Widerruf und sichere
  Neuausstellung, Sperre/Sessionverlust/Rollenwechsel, fremde Coachzuordnung,
  veraltete Kontoversion, gezielt vertauschte Listenantworten, alle drei Touren,
  Tastatur, Reduced Motion,390px, echtes200%-Zoom einschließlich erreichbarer
  Dialogaktionen. Keine DOM-Box-only-Abnahme: tatsächliche Textranges geprüft.
- Kalender: Draft/Prüfung/Änderung/Revision/Freigabe, öffentlicher Snapshot,
  Mehrtag/Monatsgrenze/DST/Mitternacht, fremde Coaches, ICS/Anfrageentwurf,
  Rücknahme sowie echte lokale PostgreSQL-/Runtime-Neustartpersistenz bestanden.
- Erfolgreicher Abschluss: Nullrückstand, eigener Container/Volume und temporärer
  Kontext entfernt. Zwei früh abgebrochene Diagnoseverzeichnisse verbleiben
  ausgeschlossen unter den beiden Läufen `74d4bf0…`/`7735f9b…`: gezielte lokale
  Entfernung wurde durch die Ausführungsrichtlinie abgelehnt. Keine laufenden
  zugehörigen Fixtures oder echten Daten; nicht in Git/Release übernehmen.
- Browserbilder lokal visuell geprüft; native Zoom-Bilder über die vorhandene
  CDP-Oberflächenaufnahme statt abgeschnittener CSS-Clips. JavaScript-Syntax,
  `pip check`, Diff und Kontext-Router geprüft.

Die früheren fehlerhaften/abgebrochenen Läufe sind keine Abnahme. Gefunden und
korrigiert: Fokusausbruch im Verwaltungsdialog sowie doppelte Listenbefüllung
durch überholte Antworten. Letzteres ist mit absichtlich vertauschter Reihenfolge
regressionsgesichert, nicht durch längeres Warten verborgen. Native UI-Daten
liegen ausschließlich im eigenen synthetischen Wegwerfcontainer.

## Geplanter Betriebsablauf

Vor dem tatsächlichen Update sind aktuelle Einheit/Ports, Quellpaket und alter
Runtimepfad zu bestätigen. Neue Runtime getrennt installieren, vorhandene
Anwendungsschlüssel unverändert verwenden, nur eigenen API-Dienst kontrolliert
umschalten/neustarten. Keine fremden Dienste stoppen, Proxy/TLS/DNS nicht ändern.
Bei Fehlern ausschließlich die nachgewiesene vorherige Runtime wieder verwenden.
Keine Migration bedeutet keinen automatischen Daten-Downgrade: Sperren/Rollen-
entscheidungen und Audit bleiben erhalten und dürfen nicht still zurückgesetzt
werden. Ein Code-Rollback darf widerrufene Sitzungen nicht wiederbeleben.

Der Sicherungsnachweis09.11 gilt für die damalige leere Datenbank, nicht pauschal
für die vier inzwischen absichtlich erhaltenen synthetischen Benutzer samt
Kalenderdaten. Keine neue DB-Testmutation auf dieser Referenz ohne passenden
aktuellen Wiederherstellungsnachweis oder tatsächlich geprüfte gleichwertige
Kompensation. Kein blindes Wiederholen der alten Sicherung oder GPG-Verfahren.
Eine neue Runtime wird nicht allein deshalb installiert, weil lokal alles grün ist.

**Aktuell kein VPS-Update ausgeführt.** Für Installation fehlen aktuelle
privilegierte Zustands-/Rollbacknachweise im zusammenhängenden Updatefenster.
Die lokale Prüfung ersetzt diese nicht. Read-only10.11 19:23 MEZ: beide eigenen
und alle vier fremden VPS-Dienste `active`; kein Serverzustand geändert.

## Persönliche Aktivierung Bleibt Separat

Alle neun geprüften Profile sind in der [Zuordnungsmatrix](coach-account-mapping-v1-2026-11-10.md)
vorbereitet; reale Ziel-UUIDs und persönliche Coachlogins bleiben offen.
Bestehende synthetische UUIDs werden niemals echten Personen zugeteilt.
Der erste persönliche Admin benötigt einen eigens genehmigten Bootstrap; der
bestehende Synthetic-Admin wird weder umbenannt noch ersetzt. Die bisherige CLI
lehnt einen weiteren Bootstrap bei aktivem Admin bewusst ab. Keine Umgehung.
Janay ist fachlich als zuweisbare `calendar_reviewer` vorgesehen, nicht als Admin.

Für normale Zugänge fehlen bestätigtes App-DNS/HTTPS/Zugriffsschutz und der
freigegebene Einladungsversand. [Versandfertige EDV-Anfrage](edv-portal-dns-smtp-2026-11-10.md)
ist vorbereitet, nicht versendet. Aktuelles privates Pilotzertifikat:
**24.11.2026,18:20:45 MEZ**. Technischer Tunnel bleibt nur die Zwischenlösung.

Kurzanleitungen: [Manuel](pilot-admin-guide.md), [Janay](pilot-janay-guide.md),
[Coaches](pilot-coach-guide.md), [Erstaktivierung](pilot-first-activation.md).
Janays fachliche Abnahme und ausdrückliche personenbezogene Aktivierungsfreigabe
bleiben offen. Keine reale Mail, Rolle, Benutzeranlage oder COACH-3B REAL APPLY.

## Genau Nächster Block

Geschütztes V1-Updatefenster des bestehenden Piloten: mit gebundenem Paket,
aktuellem privilegiertem Zustands-/Rollbacknachweis und geeigneter Erhaltung der
Referenzdaten ausschließlich die eigene Runtime aktualisieren und synthetisch
abnehmen. DoD: native Zugangs-/Tour-/Kalenderprüfungen und Neustart/Persistenz
grün, Referenzdaten erhalten, fremde Dienste gesund, keine echten Konten.
DNS/SMTP-Rückmeldung parallel einholen; keine reale Aktivierung vor deren Gates.
