# Website first: Inventur und Vorschau-Sprint

Stand: 05.11.2026. Backup-Key-Rebase/R2 ist auf Manuels Entscheidung pausiert.
Keine Schlüssel-, USB-, Passwort-, Datenbank- oder Serveraktion in diesem Block.
Manuel hat zusätzlich das GitHub-Pages-Deployment dieser Website ausdrücklich beauftragt.
IONOS bleibt ausgeschlossen.

## Einmalige Versionsinventur

Gezählt werden unterschiedliche, sauber zuordenbare gebaute Websitezustände,
nicht Dateien, Git-Commits oder doppelte Arbeitskopien: **11 Zustände** einschließlich
des neuen lokalen Vorschau-Builds. Davon sind neun unterschiedliche saubere
Archivzustände, die bisherige Vorschau und der neue Vorschauzustand.
Historisch technisch wiederherstellbar bedeutet NICHT aktuell veröffentlichbar:
Rechteänderungen, alte Personenrouten und der behobene Mindforge-P0 gelten weiter.
Die zwei bisherigen maßgeblichen Rückkehrreferenzen sind IONOS `1b4e33efa5e1`
und die veröffentlichte Vorschau `3e99e8e6151d`.

| Speicherort | Inhalt | Commit/Hash | Stand | Wiederherstellbarkeit | Verwendungszweck |
| --- | --- | --- | --- | --- | --- |
| Lokales Repository, `apps/website` und `.git` | Vollständiger Website-Quellcode, Assets, Lockfile und Git-Historie; daneben separater Backend-Quellcode | Inventurbasis `44f4a9f729c28d02219817a7ed025c047ba31902` | 153 Commits, nicht flach; ein Worktree; fremde unversionierte Dateien erhalten | Saubere Commitstände erneut baubar; keine Datenbank-/Schlüsselsicherung | Entwicklung und Historie |
| GitHub `DP-Manuel/CompetenceHub`, `main` | Zweite Quellcode-/Git-Historienkopie | Bei Inventur gleich `44f4a9f729c2`; Sprint-Commit nach Push separat nachgewiesen | Remote gelesen | Clone und Build; keine ungeprüften lokalen Dateien enthalten | Quellcode-Rückkehr unabhängig vom Rechner |
| GitHub Pages `/CompetenceHub/` | Gebaute öffentliche Vorschau | Vor diesem Deployment `3e99e8e6151d78e281e17ed54d6c435bf4e9d740`, erfolgreicher Run `39932275108` | 23.10.; neun freigegebene Coaches | Git-Rebuild; kein dauerhaftes Actions-Artefakt für diesen Run nachgewiesen | Vorschau, NICHT IONOS |
| IONOS `competencehub.donner-partner.de` | Gebaute öffentliche Produktionswebsite | `1b4e33efa5e1`; ZIP-SHA unten | 25.09.; frische HTML/CSS-Stichproben stimmen | Aktuelles sauberes 52-Dateien-Release lokal vorhanden | Unveränderte Produktion |
| `apps/website/dist` | Gebaute Produktionskopie | Inhaltsmanifest `766464db64835925bac21f94ca64ad5b93a7fdc15354e720cd3288bb90438f05` | 52 Dateien; auch nach Sprint vollständig bytegleich | Identisch zum aktuellen sauberen IONOS-Paket, keine zusätzliche Version | Lokale Produktionsregression |
| `apps/website/dist-preview` | Neue gebaute Vorschau | Inhaltsmanifest `b63be15db8751ab741b859742bb211e5b90f1e636188944ee1373cfd3a6d3fad` | 59 Dateien; geprüfter Sprint | Aus aktuellem Sprint-Quellcode erneut baubar | Lokale Abnahme / Pages-Kandidat |
| `release-artifacts/website` | 14 ZIPs mit Metadaten | Alle 14 ZIP-SHA mit Sidecars verglichen | Zehn saubere Pakete = neun unterschiedliche Inhalte; vier Dirty-Pakete nicht als Rückkehrziel freigegeben | Saubere historische Pakete technisch vorhanden; aktuelle Rechte/Fehlerlage separat beachten | Archiv; bevorzugt aktuelles `1b4e33e` |
| `release-artifacts/website-sftp-rehearsal` | Fünf bekannte Upload-Arbeitskopien | `1b4e33e`, `9955e03`, `d051a2e`, `d493e19`, `e608158` | Bereits vorhandene Releasekopien | Duplikate, keine weiteren unabhängigen Versionen | Historischer Uploadkontext |
| `release-artifacts/website-sftp-rollback` | Fünf historische Download-/Restoreordner | `pre-9955e03`, `pre-d493e19`, `pre-1b4e33e`, `pre-d051a2e`, `safe-d493e195f80a` | Zwei Mischstände; `pre-1b4e33e` enthält alten P0-Stand | Nicht blind zurückspielen; sauberes aktuelles ZIP bevorzugen | Historische Belege, kein pauschales Rollbackziel |
| `release-artifacts/post-messe-preview-20261021` | Screenshots und öffentlicher Smokebericht | Kein vollständiges Websitepaket | 21.10. | Keine Website daraus wiederherstellbar | QA-Belege |
| VPS / `apps/webapp` | Laufendes historisch dokumentiertes Chatbot-/PostgreSQL-System; Portal-Quellcode separat | In diesem Block nicht auf Server geprüft | Keine Backend-Aktivierung oder DB-Aktion | Git ersetzt weder laufende Dienste noch Datenbankinhalte | Backend, NICHT Websitekopie |
| Bestehende Datenbankbackups / Schlüssel | Nicht geöffnet oder verändert | Keine neue Bestands- oder Restorebehauptung | Rebase pausiert; bestehende automatische Jobs unberührt | Nicht aus Git wiederherstellbar; eigene spätere Gates | Daten-/Schlüsselsicherung, NICHT statische Website |

Die neun sauberen Archiv-Inhaltsstände gehören zu `1b4e33e`, `4c3cb2f`,
`5d126cb`, `9342e5d`, `9955e03`, `a8d034c`, `d051a2e`, `d493e19`, `db96b95`.
Das saubere `e608158` ist inhaltlich gleich `4c3cb2f` und wird nicht doppelt gezählt.
Das frühere lokale Vorschau-Manifest war
`e8e851f9637cba7f001e6de321508a85c8a19b3d2dff67b5a696437390d4897c`.
Inhaltsmanifest: nach relativem Pfad sortierte Zeilen `Pfad SHA256`, LF, UTF-8;
ein anderer Algorithmus/Sortiervertrag ist nicht direkt vergleichbar.

## Einfache Website-Rückkehr

Aktuelles sauberes Paket:
`release-artifacts/website/competence-hub-website-1b4e33efa5e1-20260925T121142Z.zip`.
ZIP-SHA-256: `d80bd25977dfabf5d3ecf9892ed1747ff18b69a485d6b631ea0a0a459226dd5f`.
Quellcommit und Paket sind zugeordnet; [P0-Handoff](../handoffs/2026-09-25-mindforge-notice-layout-p0-handoff.md)
und [SFTP-Vertrag](../architecture/website-sftp-release-rehearsal-runbook.md) bleiben verbindlich.
Eine spätere freigegebene Rückkehr muss das komplette passende Dateiset inklusive
Assets und `.htaccess` berücksichtigen, nicht nur `index.html`.
Kein altes personenbezogenes Paket und kein bekannter P0-Stand als Standardrollback.

Die Vorschau kann aus einem zulässigen Git-Commit über den bestehenden manuellen
Pages-Workflow erneut gebaut werden. Push allein veröffentlicht nichts:
`pages-review.yml` besitzt nur `workflow_dispatch`, keine Push-Auslösung.
Für die statische Website fehlt derzeit kein GPG-Baustein zur Rückkehr.
Eine zusätzliche externe Kopie des aktuellen öffentlichen ZIPs wäre sinnvoll,
ist aber noch nicht nachgewiesen und blockiert Websiteentwicklung nicht.

Git sichert versionierte Quellen, Assets, Abhängigkeiten und Historie, NICHT
Datenbankinhalte, Schlüssel, Passwörter, Laufzeitkonfiguration, unversionierte
Dateien, private Quelldokumente oder einen laufenden Server. Eine gebaute Website
ist kein vollständiges Backend-/Datenbankbackup. Keine neue Backupinfrastruktur.

## Umgesetzter Website-Sprint

- Coach-Suche nach Name, Thema und bereits freigegebenem aktivem Angebot;
  kombinierbar mit Themennavigation, zurücksetzbar und per URL wiederaufrufbar.
- Gülcan: drei freigegebene Angebotsfamilien, fünf Formate und fünf optionale
  Ergänzungen. Unbekannte Dauer/Preise nicht ergänzt; Leistungsgrenzen sichtbar.
  [Freigabe](coach-publication-matrix-2026-09-24.md#zusätzliche-rechtefreigabe-gülcan-vom-29102026),
  [Reviewabschluss](../architecture/coach3-existing-content-migration-plan-2026-10-23.md#coach-3b-reviewabschluss-2910).
- Kontextbezogene E-Mail-Anfragen für alle neun Coaches und Gülcans Formate;
  nur Mailclient-Entwurf, kein tatsächlicher Versand, Tracking oder neue API.
- Leere Suche führt zur persönlichen Abstimmung; ohne JavaScript bleiben alle
  Profile und Angebotsanfragen nutzbar. Elisabeths aufklappbare Angebotsgruppen
  strecken die Nachbargruppe nicht mehr mit.

Alle sichtbaren Änderungen sind Preview-only. Becker-Neukandidaten bleiben
unveröffentlicht; bestehende freigegebene Profile unverändert. Registry bleibt
optional/inaktiv; Familien-/Formatkennungen ermöglichen späteren Anschluss.
Keine echten Kundendaten, Buchungen, Rechnungsfunktionen oder Coach-Zuordnungen.

## Tatsächliche Prüfung

| Gate | Ergebnis |
| --- | --- |
| Website-Verträge | 28/28 PASS, davon drei neue Regressionstests |
| Astro Production und Preview | Je 75 geprüfte Quelldateien, null Fehler/Warnungen/Hinweise |
| Statische Linkprüfung | Production 1237, Preview 1280 Links PASS |
| Browser | 1377 Prüfungen PASS, Edge 156.0.4314.58, 34 Routen |
| Mobil / Zoom / Zugang | 390px, 640px-Reflow, echte native 200%, Tastatur/Fokus, Reduced Motion, ohne JS PASS |
| Inhalte / Layout | Drei Familien/fünf Formate, Mailto-Ziele, Such-/Themenkombination, Reload/Reset, unabhängige Details und tatsächliche Textrechtecke PASS |
| Browser-Nebenwirkungen | Keine externen Requests, Schreibrequests, Ressourcenfehler oder Konsolenfehler im lokalen Lauf |
| Produktionsisolation | Alle 52 Builddateien unverändert; öffentliche Startseite/Mindforge/CSS passen zum Paket; kein IONOS-Schreibzugriff |

Lokale Belege: `apps/website/release-artifacts/website-first-20261105/browser-report.json`
und 17 gelistete Screenshots; vier Vorherbilder in `.tmp/website-first-20261105`.
Diese erzeugten Belege bleiben außerhalb von Git. Kein Backend-/GPG-Testlauf
als Voraussetzung für diese statische Änderung.

## Abschluss und Horizont

Geprüfter Website-Quellstand: `195a41a` (05.11.). Enthält nur Website-Vorschau,
zugehörige Tests und README; keine Schlüssel-/Backend-/Produktionsänderung.

Inventur, Umsetzung und lokale Prüfung abgeschlossen. Git-Paketierung und das
jetzt ausdrücklich beauftragte manuelle Pages-Deployment sind der nächste
Abschlussschritt dieses Blocks; tatsächliche Run-/Public-Smoke-Ergebnisse werden
nach Ausführung ergänzt, nicht vorweggenommen. IONOS bleibt `1b4e33efa5e1`.

1. Geprüfte Website-/Dokumentationsänderungen gezielt committen und pushen.
2. Bestehenden Pages-Workflow für diesen Quellstand manuell starten.
3. Öffentliche geänderte Bereiche prüfen; IONOS-Stichproben unverändert bestätigen.
4. Empfohlener nächster Website-Sprint: freigegebene Angebote nach Zielgruppe,
   Thema und Format auffindbar machen. Inputs: bestehende aktive freigegebene
   Kurztexte; Ergebnis: kompakte Angebotsübersicht mit Coach-/Anfragewegen.
   DoD: keine neuen Rechteannahmen, klare Leistungsgrenzen, mobile/Tastatur-QA,
   Produktionsisolation; keine Registry-/Kalenderbuchungsabhängigkeit.
