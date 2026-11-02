# COACH-3: Bestandsinventur Und Migrationsplan

Stand:29.10.2026. **Inventur, synthetischer COACH-3A-Nachweis und COACH-3B-
Vorbereitung; kein realer Import.** Die Bestandsinventur wurde nach lokaler COACH-2-
Abnahme aus kanonischen, bereits öffentlichen Projektinhalten ermittelt.
`Quellen/` wurde in diesem Block nicht geöffnet. Keine echten Personen-UUIDs,
DB-Einträge, Accounts, Kalenderrollen oder Veröffentlichungen erzeugt.
Die spätere COACH-3A-Freigabe erlaubt ausschließlich lokale Migration0008 und
synthetische Testeinträge in einer anschließend vollständig entfernten Datenbank.

Aktueller Gate nach dem separat freigegebenen **COACH-3B-Reviewabschluss**:
**9 READY / 0 REVIEW_REQUIRED / 0 BLOCKED**, **0 unbeabsichtigter kanonischer
Feldverlust**. **GO FOR COACH-3B APPLY, pending separate Manuel approval.**
Keine DB-Verbindung, UUID-Vergabe, Migration oder Veröffentlichung in diesem
Review. Die früheren0/9/0- und0008-Befunde unten bleiben datierte Historie.
[Aktueller Reviewabschluss, Zahlen und Runbook](#coach-3b-reviewabschluss-2910)
gelten vor historischen Empfehlungen. Der
[COACH-3C-Zielvertrag](coach-registry-contract-v0.1.md#coach-3c-additive-target-contract)
bleibt technisch unverändert;0009 ist weiterhin nur lokal getestet.

## Reproduzierbare Inventur

Read-only Werkzeug: [coach3-static-inventory.mjs](../../scripts/coach3-static-inventory.mjs).
Es lädt die vorhandenen TypeScript-Modelle über die bereits installierte Vite-
Toolchain mit envDir:false, prüft Routen-/Themenreferenzen und hasht die konkreten
Profiltemplates und acht Porträtdateien. Keine Website wird gebaut oder geändert.
Ausgabe: `.tmp/coach3-static-inventory-2026-10-23.json` (ignoriert), SHA-256:
`a112259c62b4ad194a3baf215e220c5be3f0e7e2da0ff1ca650f30098bae0461`.

Quelle der tatsächlichen Profilmenge:
[Preview-Modell](../../apps/website/src/preview/coaches.ts),
[aktuelle Stammdaten](../../apps/website/src/data/coaches.ts),
[historische freigegebene Profile](../../apps/website/src/preview/historical-coaches.ts)
und [Susanne](../../apps/website/src/preview/susanne-klemm.ts).
Der historische doppelte Galvano-Eintrag wird bereits im Preview-Modell
ausgeschlossen; neun Personen, nicht zehn. Die sechs Produktions-Demoprofile
sind keine realen Coaches und kein Importkandidat.

| Profil / bestehender Slug | Themen-IDs | Angebote / weitere Quellstruktur | Asset / Umgebungsrecht |
| --- | --- | --- | --- |
| Christian Galvano / christian-galvano | fuehrung, teams-konflikte, gesundheit-praevention | Kein strukturierter Angebotskatalog; Fach-/Qualifikationstexte im Astro-Profil, nicht automatisch Angebote | christian-galvano.webp; Preview und bestehendes Production-Profil |
| Manuela Rodríguez, M.A. / manuela-rodriguez | ki-transformation, fuehrung, psychologische-beratung | Profil, acht Qualifikationspunkte, persönliches Zitat, externer Advisory-Link; Themenkarten sind kein expliziter Angebotskatalog | manuela-rodriguez.webp; Preview und bestehendes Production-Profil |
| Elisabeth Schwabauer / elisabeth-schwabauer | psychologische-beratung, gesundheit-praevention, teams-konflikte |17 Titel in vier Gruppen:3 Vorträge,7 Workshops,5 individuelle Angebote,2 Coaching/weitere; zusätzlich Qualifikationen und Leistungsgrenze | elisabeth-schwabauer.webp; nur Preview |
| Carolin Hupp / carolin-hupp | gesundheit-praevention | Qualifikationen/Themen-/Profiltext; kein strukturierter Angebotskatalog | Kein Porträt vorhanden, bestehendes Monogramm; nur Preview |
| Gülcan Elmas-Brandes / guelcan-elmas-brandes | recruiting-potenziale, gesundheit-praevention, teams-konflikte | Qualifikationen, Sprachen, Formathinweise und Profiltext; nicht als neue Workshops interpretieren | guelcan-elmas-brandes.png; nur Preview |
| T. Wegner-Ney / wegner-ney | fuehrung, teams-konflikte, recruiting-potenziale | Qualifikationen, Vortrags-/Workshopformate und Profiltext; keine einzelnen Katalogtitel inferieren | wegner-ney.jpg; nur Preview |
| Goran Celic / goran-celic | rhetorik-vertrieb | Qualifikationen/Erfahrungsangaben, Formathinweise und Profiltext; kein strukturierter Titelkatalog | goran-celic.png; nur Preview |
| Dr. Stefanie Becker / stefanie-becker | fuehrung, teams-konflikte | Qualifikationen, Organisations-/Coachingformate und Profiltext; kein strukturierter Titelkatalog | stefanie-becker.webp; nur Preview |
| Susanne Klemm / susanne-klemm | fuehrung, teams-konflikte, gesundheit-praevention |8 explizite Workshops und8 Qualifikationen, getrennte Listen | susanne-klemm.webp; nur Preview, konkret freigegebenes verarbeitetes Porträt |

Alle besitzen im gemeinsamen Modell Name, Rolle/previewRole, Fokusliste,
Themenreferenzen, Kurztext, expliziten Profilpfad und Initialen; acht zusätzlich
Bildpfad/-maße. Lange Profiltexte, Themenkarten, Qualifikationen, Formatgruppen,
Grenzhinweise und Zitat liegen überwiegend in getrennten Astro-Templates.
Eine gemeinsame Record-Übernahme allein wäre daher **nicht verlustfrei**.

Themen/Kategorien stammen ausschließlich aus der
[bestehenden Taxonomie](../../apps/website/src/preview/topics.ts): acht Themen,
drei Kategorien,18 M:N-Zuordnungen. Mediation existiert als kanonisches Thema,
ist aber keinem der neun Profile zugeordnet; daraus darf keine neue Qualifikation
oder Zuordnung abgeleitet werden. „Alle“ bleibt berechnet.

## Veröffentlichungsevidenz Stand 23.10

Die [Freigabematrix](../content/coach-publication-matrix-2026-09-24.md) besitzt
die pro Umgebung zulässige Veröffentlichung. Preview: Post-Messe-Freigabe21.10,
Namensbestätigung Elisabeth, Susanne-Freigabe23.10 einschließlich beider Porträts.
Der [Susanne-Bericht](../content/susanne-klemm-preview-2026-10-23.md) und
[Preview-Vertrag](github-pages-preview-2026-10-21.md) belegen Pages39932275108,
Quelle3e99e8e6151d und öffentliche Prüfungen. Production behält SB-54 und die
beiden dort freigegebenen echten Profile. Die sieben weiteren echten Profile
werden durch eine künftige Registry-Aufnahme nicht für Production freigegeben.

Diese vorhandenen Projektfreigaben sind Eingaben für eine kontrollierte Prüfung,
keine automatisch erzeugten DB-Einwilligungsattestationen. Referenz, geprüfter
Umfang, konkrete Revision, Umgebung, tatsächlicher Prüfer und Zeitpunkt müssen
vor einer echten Publication sauber zugeordnet werden. Keine Nachweise erfinden.

## Modelllücken Und Entscheidungen

| Bestand | COACH-1-Abbildung / offene Entscheidung |
| --- | --- |
| Name, Kurztext, Hintergrund, Zielgruppen | Bestehende Felder nutzbar; Abschnittszuordnung und Kürzung nur nach Review, keine stillen Inhaltsverluste |
| Titel/Anrede/akademischer Zusatz | Explizit normalisieren; nicht aus Namen raten, M.A./Dr. nicht doppelt ergänzen |
| Rolle/previewRole und Fokus | Keine eigenen Rollen-/Teaserfelder. Fokus nicht ungeprüft zu bescheinigten Kompetenzen machen; Rollen-/Darstellungsverlust vor Import entscheiden |
| Qualifikationslisten | Kein typisiertes Qualifikationsfeld. Als geprüfter beruflicher Hintergrund verlustfrei bewahren oder gezielt modellieren; nicht als operative Rolle oder neue Kompetenz umdeuten |
| Themen-/Formatkarten, Zitat, Sprachen, Advisory-Link und Grenzhinweise | Im aktuellen Public-DTO nicht vollständig abgebildet. Expliziter Rendering-/Feldvertrag nötig, nicht in beliebige Freitextfelder oder other-Angebote quetschen |
|17 Elisabeth-Angebote | Gruppen-/Typzuordnung fachlich prüfen. „Psychotherapie (HeilprG)“ ist wegen bestehender Leistungsgrenze kein still aktivierbares Competence-Hub-Angebot; gesonderte Darstellung/Abgrenzung entscheiden |
|8 Susanne-Workshops | Explizite Titel passen in Offering(workshop), Reihenfolge erhalten. Die Qualifikation „Systemische Supervision kompakt“ bleibt eine44-Stunden-Weiterbildung, keine DGSv-Zertifizierung oder Mediationsqualifikation |
| Profilpfad | Führenden/abschließenden Slash normieren auf `/coaches/<slug>/`; vorhandenen Slug bewahren, nie neu aus Namen ableiten |
| Assets | Acht konkrete Bytehashes verfügbar. Preview-Dateien teils außerhalb public; kontrollierte Exportablage und bytegenaue SHA-Prüfung fehlen noch. Carolin darf ohne Porträt bleiben |
| Kanonische Themen | Frontend-Slugs sind keine DB-UUIDs. Explizite geprüfte Zuordnung nötig, redaktionelle Navigation ist keine automatische CAL-1-Themenberechtigung |
| Accounts / Kalenderpfade | Nicht Bestandteil dieses Imports. Keinen Personen-/Account-/Coach-UUID-Abgleich aus Name, Mail oder Route erraten |
| Revision / Publication | Bestehende Seiten sind kein bereits migriertes Registry-Aggregat. Initialer Import darf keinen Live-Status, Freigaben oder aktiven Lifecycle vortäuschen |

**Ein echter Bulk-Import ist damit noch nicht freigabereif.** Zuerst müssen
verlustfreie Feld-/Rendering-Abbildung, Therapiegrenze, explizite Themen-/Identitäts-
Zuordnung und Nachweisführung entschieden werden. Externe DNS-/SMTP-Antworten
sind für einen rein synthetischen Import-Dry-Run keine Voraussetzung.

## Geplanter Ablauf Mit Getrennten Gates

1. **Static Coach Content:** eingefrorener Git-Stand, genaue kanonische Inputs,
   Template-/Assethashes, vorhandene Public-Freigaben und Ausschluss der Demoprofile.
2. **Validation:** typisierte Normalisierung mit Längen-/Pfad-/Asset-/Feldverlust-
   Bericht. Unabbildbare Abschnitte und Therapie-/Qualifikationsfragen stoppen
   den Record, statt Felder fallenzulassen oder Inhalte zu erfinden.
3. **Canonical Topic Matching:** Slug-Referenzliste gegen freigegebenes Mapping.
   NFC/Casefold/Leerzeichen-/Bindestrichnormalisierung nur für ausdrücklich
   kuratierte Aliase; keine automatische semantische Zusammenlegung. Neue Themen benötigen einen
   eigenen freigegebenen Vertrag mit normalisierter Eindeutigkeit.
4. **Coach UUID:** vor echtem Schreiben manuell bestätigte Personenidentität und
   separates Importledger. Neue UUID zufällig, bestehende bestätigte UUID bewahren;
   kein Hash aus Name, E-Mail oder Route als Personenidentität.
5. **Profile Revision:** vollständiger geprüfter Draft über den Registry-Vertrag,
   erwartete Version, neue Revision nur bei bewusst geändertem Inhaltsmanifest.
   Keine Bearbeitung eingereichter Inhalte; keine automatische Zustimmung.
6. **Offerings:** explizite Typen, eindeutige Quellreihenfolge, aktive/inaktive
   Einträge und Leistungsgrenzen übernehmen. Keine Kalendertermine/Preise/FIN-Felder.
7. **Assets:** echte Exportbytes gegen festgehaltene SHA-256 prüfen, Alttexte und
   Freigabescopes zuordnen. Keine Originalquellen oder EXIF-Daten nachladen.
8. **Publication Evidence:** fachlicher Review/Einwilligung/konkrete Umgebung
   getrennt dokumentieren; danach explizit aktivieren und lokale Preview-Projektion.
9. **Preview Projection:** zunächst nur lokal erzeugtes Artefakt gegen alten
   Bestand vergleichen: Personenmenge, Routen, Texte, Angebote, Themen, Assets,
   noindex und kein Production-Übertritt. Pages-Deployment bleibt eigenes Gate.

Vorstufen sind Analyse und synthetischer Dry-Run. Echte DB-Übernahme,
Servermigration, Rollen und Website-Umschaltung benötigen jeweils eigene Freigabe.

## Idempotenzvertrag Für Den Künftigen Importer

- Ein bestätigter Importrecord erhält einen unveränderlichen, nicht aus aktuellen
  Personendaten abgeleiteten Quellschlüssel und einen einmal gespeicherten
  client_request_id. Wiederholung verwendet denselben Schlüssel/dieselbe UUID.
- Ledger-Eindeutigkeit für Importquelle/Record, geprüfte Coach-Zuordnung und
  kanonischen Inhalts-/Assetmanifesthash; kein erneuter Personenabgleich bei jedem Lauf.
- Erstanlage und Ledger müssen atomar beziehungsweise eindeutig wiederaufnehmbar
  sein. Ein verlorener Antwortweg darf keinen zweiten Coach erzeugen. Ein früherer
  Anlageauftrag mit geändertem Namen darf nicht als neue Person wiederholt werden.
- Unverändertes Manifest: keine neue Revision, Themenanlage oder zusätzliche
  Angebote. Draft-Kinder werden als vollständige versionierte Menge ersetzt,
  nicht bei jedem Lauf angehängt; Reihenfolge und aktive Flags bleiben identisch.
- Geändertes Manifest: genau eine beabsichtigte neue Draft-Revision mit neuem
  Reviewbedarf. Keine Freigaben erben; Paralleländerung führt zu409/Review statt
  Überschreiben. Angebotsidentität wird innerhalb des Quellmanifests festgehalten,
  nicht durch zufällige neue IDs pro Wiederholung erzeugt.
- Zweiter synthetischer Lauf muss dieselbe Personen-/Revisions-/Themen-/Angebotszahl
  und dieselbe kanonische Projektion liefern. Tests zusätzlich für Antwortverlust,
  Rename bei gleicher Person, Doppelnamen verschiedener Personen, Teilabbruch,
  Konflikt mit vorhandenen Daten und veränderte Assetbytes.
- Pause/Ausscheiden2027 und Wiedereinstieg2028 behalten die2026 angelegte UUID.
  Neue Revision und frische Freigaben; kein Duplikat und kein automatisches Publishing.
  Dieser Lifecycle ist bereits synthetisch durch COACH-2 abgesichert, nicht mit
  realen Personen durchgeführt.

Die statische Inventur allein ist **kein** Nachweis eines DB-Importers. Der
nachfolgende, separat freigegebene COACH-3A-Block ergänzt diesen Nachweis nur
synthetisch. Verlustfreies Rendering aller realen Profile bleibt ein offenes Gate.

## COACH-3A-Nachweis

Verbindlicher [Importvertrag](coach-import-contract-v0.1.md), typisierte Records,
reine Validierung, schreibfreier DB-Dry-Run und kontrollierter Fixture-APPLY sind
implementiert. Keine neue HTTP-API und kein Standardruntime-Schalter.
Migration0008 ergänzt nur Quellbindung, logische Itemidentität und datierte/
undatierte Nachweise;0007 allein enthielt diese Importinformationen nicht.

| Tatsächlich geprüft | Ergebnis |
| --- | --- |
| Alpha/Beta/Gamma/Delta | Vier synthetische Coaches: vollständiges Preview-Profil, bewusst ohne Porträt, explizite synthetische Therapiegrenze, getrennte Rollen/Qualifikationen |
| Leerer Fachbestand, DB-Dry-Run | CREATE4; alle Tabellen einschließlich xmin unverändert |
| Paralleler Erstanlauf | Ein CREATE4, ein NO-OP; keine doppelte UUID/Revision |
| Zweiter und dritter identischer Lauf | UNCHANGED4, null Mutationen; alle Tabellen einschließlich Ledger/Audit/xmin identisch, Projektion bytegleich |
| Taxonomie | Acht bestehende Themen, drei Kategorien,18 M:N-Links; nur kuratierte Aliase, keine Anlage von „Alle“ oder inferierten Kompetenzen |
| Namens-/Kurztextänderung Alpha | Gleiche UUID und Route; genau neue Draft-Revision2, keine Freigaben übernommen, veröffentlichte Revision1 unverändert |
| Angebote | Zwei fachliche Alpha-Angebote bleiben über logische IDs stabil; neue Revision kopiert Snapshots. Explizite Änderung/Deaktivierung/Ergänzung in importer-eigenem Draft, Wiederholung NO-OP |
| Fehlende Items | Konflikt statt Löschen; gesamter Batch unverändert |
| Assetbytes | Hashprüfung; neue Bytes unter alter Referenz blockiert, neue explizite Versionsreferenz im Draft möglich, alter veröffentlichter Verweis erhalten |
| Themen-/Kategoriesnapshot | Bestandteil des Profilhashs; kanonische Themenumbenennung aktualisiert nur den Draft, nicht die veröffentlichte Fassung |
| Nachweise | Preview/Production getrennt, unbekannte historische Zeitpunkte bleiben NULL, bekannte UTC-Zeit getrennt von Import-/Attestationszeit |
| Technische Provenienzänderung | Nur Ledger-Metadaten; keine Profilrevision und kein fachlicher Audit |
| Pause/Ausscheiden/Wiederkehr | Active2026 -> inactive2027 -> frisch geprüft active2028 mit derselben UUID; Import nach manueller Zustandsänderung blockiert, keine stille Reaktivierung |
| Hard Conflict / Abbruch | Pfad-/Identitäts-/Freigabekonflikte ohne Teilpersistenz; vollständiger Rollback auch bei Ausnahme, Cancellation und SQL-Fehler nach bereits begonnenen Writes |
| DB-Schutz / CLI | Unveränderliche Bindung/Item-IDs, eindeutige Pfade/FKs, Evidence-Umgebung und eingeschränkte Grants direkt geprüft; Defaults schreibfrei, synthetischer Scope und DB-Admin überprüft |

Verifikation23.10.2026: **559 lokale Tests bestanden,19 vorgesehene Skips**
(17 Staging, je ein dedizierter lokaler Registry-/Import-PG-Test).
Beide opt-in-PG-Szenarien separat wirklich ausgeführt und bestanden. Der neue
Importlauf wurde wiederholt; CLI-Dry-Run und expliziter synthetischer CLI-APPLY
gegen die laufende Testdatenbank ergaben NO-OP. Compileall, pip check,
PowerShell-Syntax, Dokumentlinks/Archivintegrität und git diff --check bestanden.
Kein JS geändert; kein neuer Browser-/Website-Abnahmeclaim.

Testdateien: [Unit/CLI](../../apps/webapp/tests/test_coach_import.py),
[echtes PostgreSQL](../../apps/webapp/tests/test_coach_import_postgres_local.py).
Der Testbestand wird durch vollständiges Entfernen des eigenen tmpfs-Containers
gelöscht; keine Historienguards abgeschaltet. Keine Quellenordner, echten
Porträts, realen Coach-UUIDs, Accounts oder Kalenderzuordnungen eingelesen.
Pages, VPS und IONOS unverändert; weder Paketbau noch Deployment durchgeführt.

## Historische Entscheidungsmatrix Vom 23.10

| Bereich | Bereits technisch entschieden | Noch fachlich zu bestätigen |
| --- | --- | --- |
| Qualifikationen | Getrennte typisierte Eingabe; niemals Kompetenz/operative Rolle inferieren. Öffentlich wörtlich nur nach explizitem Hintergrund-Mapping; intern aktuell nicht unterstützt | Für reale Listen: vollständige öffentliche Darstellung als eigener Hintergrundabschnitt oder eigener strukturierter Feld-/Renderingvertrag? Welche Angaben bleiben intern? |
| Rollenbezeichnungen / Darstellung | Eigener Source-Typ; ungeprüfte Zuordnung stoppt. Keine automatische Zerlegung zusammengesetzter Rollen | Reale Rollen/previewRole und Fokus sowie Zitat, Sprachen, Formatgruppen und Advisory-Link verlustfrei und in vorgesehenen Abschnitten darstellen; kein pauschaler Freitextdump |
| Therapie-/Coachinggrenze | Unmapped blockiert; nur ausdrücklich freigegebener Wortlaut, synthetisches Beispiel nie buchbar | Exakte öffentliche Einordnung insbesondere Elisabeths „Psychotherapie (HeilprG)“ und der17 Angebotsgruppen; nicht still als aktives Coaching übernehmen |
| Freigabeevidence | Revision/Coach/Art/Umgebung/Quelle getrennt; unknown bleibt NULL, aktuelle Attestation separat, keine Vererbung | Welche vorhandenen konkreten Nachweise decken Inhalt, Person/Porträt und jeweilige Umgebung ab? Prüfer und bekannte Zeitpunkte/Umfang explizit zuordnen |
| Porträt fehlt | Zulässig, kein Ersatzbild erzwingen; keine neue Entscheidung erforderlich | Keine |
| Fehlendes Angebot/Item | Gesamter Batch stoppt; keine automatische Löschung. Explizit active:false ist unterstützt | Nur bei einem konkreten späteren Konflikt Quelle vervollständigen oder Deaktivierung freigeben |
| Identität/Themen/Assets | Keine Namenszuordnung, kein Legacy-Adopt, keine unfreigegebenen UUID-Mappings oder Assetbytes | Eigene reale Mapping-/Ausführungsfreigabe bleibt vor jedem COACH-3B-Schreibschritt erforderlich |

## Bestätigte Entscheidungen Vom 29.10

Manuels COACH-3B-Preparation-Auftrag und Gülcan-Addendum bestätigen:

- Qualifikationen erhalten kanonisches Label, Public-Flag/Public-Display,
  interne Evidence-Referenz und Verifikationsstatus; öffentliche Darstellung
  kompakt unter „Qualifikationen & beruflicher Hintergrund“.
- Rollen, Themen, Kompetenzen, Qualifikationen und Angebote bleiben getrennt.
  Zusammengesetzte Rollenbeschreibungen bleiben als Originalanzeige erhalten.
- Psychotherapie bleibt fachlich Psychotherapie; Elisabeths Originaltitel und
  bestehende Grenze bleiben, keine Zuordnung zu Mindforge oder Buchbarkeit.
- Profilinhalt, Porträt, konkrete Angebotsinhalte und beide Veröffentlichungs-
  umgebungen benötigen unterscheidbare Nachweise. Unbekannte Prüfer/Zeitpunkte
  werden nicht ergänzt; eine Tagesangabe wird nicht zu Mitternacht umgedeutet.
- Keine leeren Profilabschnitte; Kontakt bleibt Plattformfunktion. Private
  Dokumente, Kontakte, Nummern, Prüfnotizen und unbestätigte Preise bleiben außen.

Diese Entscheidungen ersetzen die **fachlichen Grundsatzfragen** der historischen
Matrix oben. Sie implementieren keine fehlenden Persistenz-/Projektionsfelder
und stellen keine neue Veröffentlichungsfreigabe für Workshopkonzepte dar.

## Aktueller Matrixstatus Und Reproduzierbarkeit

**9/9 Profile analysiert. Faktenzuordnung9 READY; aktuelles ausführbares
Zielmapping0 READY /0 REVIEW_REQUIRED /9 BLOCKED. NO-GO für APPLY.**
Alle neun verlieren im heutigen COACH-1/3A-Ziel strukturierte Rollen,
Darstellungsabschnitte und genaue Evidence-Bindungen; acht zusätzlich strukturierte
Qualifikationen. BLOCKED bezeichnet diese wirklichen technischen Lücken, nicht
fehlende Analyse oder ein pauschales Verbot ihrer bestehenden Preview.
Fehlende Production-Freigabe blockiert **nicht** das Preview-Faktenmapping.
Die reinen Vorbereitungstests sind grün, nicht der künftige reale Import.

Werkzeuge, ohne DB-Verbindung oder Websitebuild:
[kanonischer AST-Leser](../../scripts/coach3b-canonical-inputs.mjs),
[explizite Reviewzuordnung](../../scripts/coach3b-review-map.json),
[reine Mappingprüfung](../../scripts/coach3b_preparation.py).
Astro-/TypeScript-Parser lesen tatsächliche Profilabschnitte, Credential-Listen,
Angebote, Zitate und Linkausdrücke. Dynamische Ausdrücke und Komponenten bleiben
als Rendering-Eingaben erfasst; es wird kein angeblich vollständiges neues
Website-DTO aus einfachen Textfragmenten behauptet. Abhängige öffentliche
Dateien/Freigabedokumente und alle acht Assetbytes sind hashgebunden.

Der read-only Inventurhash bleibt
`a112259c62b4ad194a3baf215e220c5be3f0e7e2da0ff1ca650f30098bae0461`.
Kanonischer29.10-Input unter `.tmp/coach3b-canonical-inputs-2026-10-29.json`:
`e3feda67b2bdb681b080e2336d82fd9c9eb39128735f2955c47773fed5e743a9`.
Die Reviewzuordnung akzeptiert nur genau diesen Stand; eine spätere Änderung
stoppt den CLI-Lauf und erfordert überprüfte Zuordnung, kein blindes Neu-Hashen.
Report `.tmp/coach3b-dry-mapping-2026-10-29.json` bleibt ignoriert und wird
deterministisch neu erzeugt. Weder reale UUIDs noch Zugangsdaten darin.

## Coachmatrix

Quelle für alle Source Identities: `website-preview`. Die folgenden Schlüssel
werden **einmalig zugewiesen und danach unveränderlich** beibehalten; bei Namens-
oder Routenänderung nicht erneut ableiten. Keine Personen-UUID vergeben. Kein
bestehender Coach allein nach Name, Mail oder Route gematcht. Quelle jeweils
aktuelles gemeinsames Modell plus das in der Inventur genannte Astro-Profil.

| Kürzel / Anzeigename exakt | source_key | Profilpfad | Themen | Kategorien | Q / K / Angebote | Porträt |
| --- | --- | --- | --- | --- | --- | --- |
| CG / Herr Christian Galvano | coach/christian-galvano | /coaches/christian-galvano/ | fuehrung, teams-konflikte, gesundheit-praevention | PE, PKE |4/0/0 | vorhanden |
| MR / Manuela Rodríguez, M.A. | coach/manuela-rodriguez | /coaches/manuela-rodriguez/ | ki-transformation, fuehrung, psychologische-beratung | PE, PKE, KK |3/0/0 | vorhanden |
| ES / Frau Elisabeth Schwabauer | coach/elisabeth-schwabauer | /coaches/elisabeth-schwabauer/ | psychologische-beratung, gesundheit-praevention, teams-konflikte | PE, PKE, KK |3/3/17 | vorhanden |
| CH / Frau Carolin Hupp | coach/carolin-hupp | /coaches/carolin-hupp/ | gesundheit-praevention | PE, PKE |1/3/0 | NOT_APPLICABLE |
| GE / Frau Gülcan Elmas-Brandes | coach/guelcan-elmas-brandes | /coaches/guelcan-elmas-brandes/ | recruiting-potenziale, gesundheit-praevention, teams-konflikte | PE, PKE, KK |7/2/0 | vorhanden |
| WN / Herr T. Wegner-Ney | coach/wegner-ney | /coaches/wegner-ney/ | fuehrung, teams-konflikte, recruiting-potenziale | PE, PKE, KK |3/3/0 | vorhanden |
| GC / Herr Goran Celic | coach/goran-celic | /coaches/goran-celic/ | rhetorik-vertrieb | PE, PKE, KK |0/3/0 | vorhanden |
| SB / Frau Dr. Stefanie Becker | coach/stefanie-becker | /coaches/stefanie-becker/ | fuehrung, teams-konflikte | PE, PKE |1/0/0 | vorhanden |
| SK / Frau Susanne Klemm | coach/susanne-klemm | /coaches/susanne-klemm/ | fuehrung, teams-konflikte, gesundheit-praevention | PE, PKE |8/0/8 | vorhanden |

PE=Personalentwicklung; PKE=Persönlichkeitsentwicklung; KK=Karrierecoaching.
Q=explizite Qualifikationseinträge; K=hier konkret fachlich zugeordnete Kompetenz-
labels, keine aus Themen/Fokus generierten Bescheinigungen. Null bedeutet keine
zusätzlichen strukturierten Einträge aus dieser Zuordnung, nicht fehlende Expertise.
GE hat zusätzlich fünf **zurückgehaltene** neue Formatkandidaten, siehe unten.
Alle neun Gesamtmappings: BLOCKED durch noch nicht implementierten Zielvertrag.
BLOCKED hat Vorrang vor REVIEW_REQUIRED; die13 offenen Review-Subjects werden
zusätzlich geführt und verschwinden nicht durch den Gesamtstatus.

## Themenmatrix

| Kanonischer Slug / Name | Kategorien | Coaches | Zuordnung |
| --- | --- | --- | --- |
| fuehrung / Führung | PE, PKE | CG, MR, WN, SB, SK | READY redaktionell |
| teams-konflikte / Teams & Konflikte | PE, PKE | CG, ES, GE, WN, SB, SK | READY redaktionell |
| gesundheit-praevention / Gesundheit & Prävention | PE, PKE | CG, ES, CH, GE, SK | READY redaktionell |
| ki-transformation / KI & Transformation | PE, KK | MR | READY redaktionell |
| mediation / Mediation | PE, PKE | keine | READY, keine neue Zuordnung |
| recruiting-potenziale / Recruiting & Potenziale | PE, KK | GE, WN | READY redaktionell |
| rhetorik-vertrieb / Rhetorik & Vertrieb | PE, PKE, KK | GC | READY redaktionell |
| psychologische-beratung / Psychologische Beratung | PE, PKE, KK | MR, ES | READY redaktionell |

Acht kanonische Lookup-Referenzen,18 Kategoriebeziehungen,22 Profil-Themenlinks.
Keine DB-UUIDs erfunden: tatsächliche UUID-Auflösung und vorhandener Zielkatalog
sind **NOT_READ**, vor APPLY zu prüfen. Fehlende DB-Themen benötigen einen eigenen
freigegebenen Bootstrap, nicht automatische Anlage durch den Importer. Frontend-
Aliases sind die obigen Slugs/Namen; keine Stressmanagement-/Modul-Dubletten.

## Rollenmatrix

| Coach / Source Label | Kanonische Konzepte / öffentliche Anzeige | Review |
| --- | --- | --- |
| CG: Dozent, Fachtrainer und Coach | lecturer/Dozent; trainer/Fachtrainer; coach/Coach | READY; Buchautor als weiterer belegter Descriptor |
| MR: KI-Managerin, Leitung Digitalstrategie, Dozentin und Coach | ai_manager/KI-Managerin; digital_strategy_lead/Leitung Digitalstrategie; lecturer/Dozentin; coach/Coach; moderator/Moderatorin; speaker/Speakerin aus Profil | READY, Quellenanzeige erhalten |
| ES: Psychologin (M.Sc.) | psychologist/Psychologin (M.Sc.) | READY; akademischer Zusatz nicht verdoppeln |
| CH: Diplom-Sportwissenschaftlerin | sports_scientist/Diplom-Sportwissenschaftlerin | READY; Diplom zusätzlich Qualifikation |
| GE: Coach, Trainerin und Diplom-Betriebswirtin (VWA) | coach/Coach; trainer/Trainerin; Abschluss separat | READY; Elmas Consulting als belegte Organisation, keine neue Rechtsform ableiten |
| WN: Unternehmensberater, Speaker, Workshop-Leiter und Coach | consultant/Unternehmensberater; speaker/Speaker; workshop_leader/Workshop-Leiter; coach/Coach | READY |
| GC: Coach für Rhetorik und Vertrieb | coach/Coach für Rhetorik und Vertrieb | READY; Fachbeschreibung nicht in neue operative Rolle zerlegen |
| SB: Executive Coach und Team- und Organisationsentwicklerin | executive_coach/Executive Coach; organisation_developer/Team- und Organisationsentwicklerin | READY |
| SK: Coach und Trainerin | coach/Coach; trainer/Trainerin | READY; kein zusätzlicher Supervisorinnen-/Mediationstitel |

Das sind Profilrollen/Descriptors, keine Portal-RBAC-Rollen. Keine neue Account-
oder CAL-1-Berechtigung; genderkorrekte Anzeige und ganze Quellbezeichnung bleiben.

## Qualifikationsmatrix

Für jede Zeile: canonical_label=unverändertes Source Label; Public=yes;
Public Display=gleiches Label, keine Aufwertung. Evidence ist der bereits
freigegebene öffentliche Profilbestand, **kein** erneut geprüftes Originalzeugnis.
S=SOURCE_ASSERTED; V=PRIOR_REVIEW_RECORDED nach Susannes dokumentierter23.10-
Quellenprüfung. V behauptet keine erneute Sichtung ihrer privaten Originaldateien.
Neue interne Qualifikationen nur mit Public=no und ohne Public Display exportieren.
Dokumentnummern, Signaturen und Originaldokumente werden nicht übernommen.

| Coach / stabiler Bootstrap-Itemkey | Source Label = Canonical Label = Public Display | Evidence / Verifikation |
| --- | --- | --- |
| CG credential/1 | Master in Neurowissenschaften (M.Sc. Tech) | öffentliches Profil, S |
| CG credential/2 | Studium der biologischen Psychologie | öffentliches Profil, S; kein zusätzlicher Abschluss behauptet |
| CG credential/3 | Personal- und Business Coach (IHK) | öffentliches Profil, S |
| CG credential/4 | Trainer (IHK) in der Erwachsenenbildung | öffentliches Profil, S |
| MR credential/1 | Studium der Psychoanalyse und Mediävistik an der Goethe-Universität Frankfurt | öffentliches Profil, S |
| MR credential/2 | Zertifizierte KI-Managerin mit Fokus auf Human Intelligence | öffentliches Profil, S |
| MR credential/6 | Zertifizierte Gutachterin für Erwachsenenbildung (GRETA) | öffentliches Profil, S |
| ES credential/1 | Master of Science in Psychologie | öffentliches Profil, S |
| ES credential/2 | Bachelor of Science in Angewandter Psychologie | öffentliches Profil, S |
| ES credential/7 | Heilpraktikerin, eingeschränkt für Psychotherapie | öffentliches Profil, S; kein aktives Hub-Therapieangebot |
| CH credential/1 | Diplom-Sportwissenschaftlerin | öffentliches Profil, S |
| GE credential/1 | Diplom-Betriebswirtin (VWA) | öffentliches Profil, S |
| GE credential/2 | Ganzheitliche Ernährungsberaterin (IHK) | öffentliches Profil, S |
| GE credential/3 | NLP-Practitioner nach DVNLP und INLPTA | öffentliches Profil, S |
| GE credential/4 | Systemisches Denken und Beraten | öffentliches Profil, S; kein zusätzlicher Zertifikatstitel |
| GE credential/5 | Zertifizierte MIKA-Trainerin | öffentliches Profil, S |
| GE credential/6 | Kursleiterin Nordic Walking | öffentliches Profil, S |
| GE credential/7 | Qualitätsmanagerin, Qualitätsbeauftragte und interne Auditorin | öffentliches Profil, S |
| WN credential/1 | Staatlich geprüfter Techniker Druck- und Medientechnik | öffentliches Profil, S |
| WN credential/2 | Zertifizierter Qualitätsbeauftragter | öffentliches Profil, S |
| WN credential/3 | Ausbilder nach AEVO | öffentliches Profil, S |
| SB credential/1 | Promotion in Rechtswissenschaften | öffentliches Profil, S |
| SK credential/1 | Kinder- und Jugendcoach | Susanne-Bericht / qualifications[0], V |
| SK credential/2 | Selbstbehauptungs- und Resilienztrainerin | Susanne-Bericht / qualifications[1], V |
| SK credential/3 | Licensed Business Practitioner of NLP | Susanne-Bericht / qualifications[2], V |
| SK credential/4 | Licensed Business Master Practitioner of NLP | Susanne-Bericht / qualifications[3], V |
| SK credential/5 | Hypnose Coach | Susanne-Bericht / qualifications[4], V |
| SK credential/6 | NLS Stage Master | Susanne-Bericht / qualifications[5], V |
| SK credential/7 | Weiterbildung „Systemische Supervision kompakt“ (44 Zeitstunden) | Susanne-Bericht / qualifications[6], V; nicht DGSv |
| SK credential/8 | Fachfortbildung zur ganzheitlichen Mobbingpräventionstrainerin | Susanne-Bericht / qualifications[7], V |

Die credential/n-Keys beziehen sich auf die **eingefrorene** Source-Liste, nicht
auf zukünftig beliebig verschobene Positionen. Nach Erstanlage unveränderliche
Itemidentitäten pflegen; Listenänderung stoppt den Hash-Gate zur Review.

Weitere Listeninhalte bleiben erhalten, aber anders klassifiziert:

| Coach | Kompetenzen ausdrücklich zugeordnet | Sonstige erhaltene Inhalte |
| --- | --- | --- |
| CG | keine zusätzlichen | Dozent/Fachtrainer und Buchautor als Rollen; bestehende Fokuslabels bleiben Fokus |
| MR | keine zusätzlichen | Leitung/Dozentin/Moderatorin/Speakerin als Rollen; Lehraufträge und methodischer NLP-/Hypnotherapie-/Bildercoachingbezug als Hintergrund, nicht Heilkundeberechtigung |
| ES | Psychologische Beratung im beruflichen Kontext; Team- und Konfliktklärung; Psychische Gefährdungsbeurteilung nach §5 ArbSchG | Erfahrung in Neuropsychologie als Hintergrund |
| CH | Personal Gesundheits- und Fitnesstraining; Rücken- und Bewegungskonzepte; Entspannungsverfahren | Gesundheits-/Trainingsmanagement und ZPP-geprüfte Kurse als Hintergrund, keine neu behauptete personenbezogene Zertifizierung |
| GE | Internationales und agiles Projektmanagement; Financial Controlling und Prozessoptimierung | Deutsch/Englisch/Türkisch als Sprachen; neue allgemeine Ausbildungs-/Erfahrungsangabe separat SOURCE_ASSERTED, nicht neues Zertifikat |
| WN | Qualitätsmanagement und Prozessoptimierung; Projektleitung und Führungskräfteentwicklung; Konzeption von Workshops und Fachvorträgen | Allgemeine Formathinweise bleiben Formathinweise |
| GC | Rhetorik und überzeugender Auftritt; Präsentations- und Gesprächstraining; Storytelling für erklärungsbedürftige Angebote | Berufsjahre/Teilnehmendenzahl als Quell-Hintergrund, Impulsvorträge/Workshops als allgemeine Formate |
| SB | keine zusätzlichen | Hypnosystemisches Coaching, Organisationsentwicklung, Konfliktmanagement, Facilitation und Großgruppenprozesse als Methoden-/Praxishintergrund, keine erfundenen Abschlüsse |
| SK | keine aus Fokus automatisch erzeugten | Kommunikation/Rollen/Stress bleiben belegte Schwerpunkte; die acht Workshops bleiben separat |

Zielgruppen bleiben soweit belegt in den jeweiligen öffentlichen Absatz-/Karten-
texten erhalten: CG Unternehmen/Führungskräfte/Teams; MR Unternehmen/Menschen;
ES Unternehmen/Führungskräfte/Teams; CH Unternehmen/Gruppen; GE Menschen/
Organisationen; WN Unternehmen/Führungskräfte/Mitarbeitende; GC Unternehmen/
Vertriebsteams/Fachleute; SB Organisationen/Führungsteams; SK Führungskräfte/
Mitarbeitende mit teils Pflegebezug. Keine zusätzliche Einsatzregion/Verfügbarkeit.

## Angebotsmatrix Des Bestehenden Bestands

Scope aller folgenden Titel: bestehende Preview-Freigabe. Registry-Evidence muss
noch an die konkrete neue Revision gebunden werden; keine Buchungsaktivierung.
Active=yes bedeutet nur fachlich vorhandener Katalogtitel, nicht Kalendertermin.
Explizite Source-Gruppen und Reihenfolge bleiben erhalten. Keine Angebote aus
allgemeinen Themen-/Formatkarten der anderen sieben Coaches konstruieren.

| Coach / Key | Originaltitel | Format / fachliche Grenze | Active |
| --- | --- | --- | --- |
| ES vortraege/1 | Psychische Gesundheit und gesund führen | lecture, kein Therapieangebot | yes |
| ES vortraege/2 | Positive Leadership – Mitarbeiter stärken und Potenziale entfalten | lecture | yes |
| ES vortraege/3 | Positive Psychologie im Arbeitsalltag | lecture | yes |
| ES workshops/1 | Belastungen frühzeitig erkennen und handeln | workshop | yes |
| ES workshops/2 | Gesund Führen | workshop | yes |
| ES workshops/3 | Umgang mit psychisch belasteten Mitarbeitenden | workshop | yes |
| ES workshops/4 | Wiedereingliederung nach psychischer Erkrankung | workshop | yes |
| ES workshops/5 | Mentale Gesundheit im Homeoffice und hybriden Arbeiten | workshop | yes |
| ES workshops/6 | Stressmanagement und Burnout-Prävention | workshop | yes |
| ES workshops/7 | Positive Psychologie | workshop | yes |
| ES individuell/1 | Resiliente und leistungsfähige Teams entwickeln | individual | yes |
| ES individuell/2 | Psychische Gefährdungsbeurteilung verstehen und umsetzen | individual | yes |
| ES individuell/3 | Psychische Belastungen verstehen | individual | yes |
| ES individuell/4 | Gefährdungsbeurteilung in der Praxis | individual | yes |
| ES individuell/5 | Kurzanalyse im Team (KiT) | individual | yes |
| ES weitere/1 | Coaching | coaching | yes |
| ES weitere/2 | Psychotherapie (HeilprG) | psychotherapy, Anzeige separat, nicht über Hub angeboten, nicht Mindforge | no |
| SK workshop/1 | Mit den richtigen Fragetechniken erfolgreich zum Ziel – Reden kann jeder, fragen will gelernt sein! | workshop | yes |
| SK workshop/2 | Selbstwahrnehmung trifft Fremdwahrnehmung – Spiegelkabinett oder klares Bild? | workshop | yes |
| SK workshop/3 | Zwischen den Zeilen – Was wird (nicht) gesagt? Wahrnehmungsschulung & Körpersprache verstehen | workshop | yes |
| SK workshop/4 | Zwischen Mama und Chefin: Wer hat hier eigentlich das Sagen? Rollenbewusstsein stärken & im Berufsalltag klar führen | workshop | yes |
| SK workshop/5 | Dein Stress, nicht meiner! Warum soll ich mich eigentlich mit aufregen? | workshop | yes |
| SK workshop/6 | Vom Kollegen zur Führungskraft | workshop | yes |
| SK workshop/7 | Führungshaltung und Führungsstil | workshop | yes |
| SK workshop/8 | Von Elefanten im Raum und anderen Missverständnissen | workshop | yes |

## Gülcan Neue Quellen Und Angebotsfamilien

**Identität bestätigt:** neuer Dokumentabsender und kanonischer Bestand stimmen
auf Gülcan Elmas-Brandes überein, Organisation Elmas Consulting. Kein neuer Coach,
keine Namensverkürzung auf „Gülcan Elmas“, keine Änderung späterer UUID.
Nur `Quellen/20261029` wurde zusätzlich gelesen; keine Nachbarordner.
Neue Source Facts aus Konflikt-TagesworkshopP10: systemische Ausbildung und über
25 Jahre Erfahrung in Projektsteuerung, Kundenberatung und Teamarbeit, national
und international. SOURCE_ASSERTED; kein abgeleiteter Zertifikatstitel/Verband.

| Dokument-ID / Datei | Technische Prüfung | Extrahierbarer Umfang |
| --- | --- | --- |
| guelcan-health / Gesundheit-im-Unternehmensalltag-Halbtag-10-14Uhr.docx | ZIP/CRC und Haupt-XML gültig | vollständige fachliche Analyse; kein vollständiger Konzeptabdruck |
| guelcan-balance-six-weeks / Gülcan Elmas_Business-Balance-6-Wochen-Programm_60 Minuten.docx | ZIP/CRC und Haupt-XML gültig | sechs Wochen, Rahmen/Zielgruppe/Boundary; Tagesformat nur durch Querverweis belegt |
| guelcan-balance-day / Gülcan Elmas_Business-Balance-Tagesworkshop für Unternehmerinnen.docx | kein gültiger DOCX-ZIP-Container | SOURCE_READ_ERROR / SOURCE_REPLACEMENT_REQUIRED, keine Details ergänzt |
| guelcan-conflict-day / Gülcan Elmas_Konfliktklaerung-Teamreflexion-Tagesworkshop.docx | ZIP/CRC und Haupt-XML gültig | Tagesformat, Ausbildungs-/Erfahrungsangaben, harte Leistungsgrenze |
| guelcan-reflection-series / Gülcan Elmas_Konfliktklaerung-Teamreflexion-Reflexionsreihe.docx | kein gültiger DOCX-ZIP-Container | SOURCE_READ_ERROR / SOURCE_REPLACEMENT_REQUIRED, keine Details ergänzt |

Die Fehlerursache der beiden nicht lesbaren Container ist nicht bewiesen;
keine Entschlüsselungs-/Reparaturversuche oder Interpretation zufälliger Bytes.
Manuel bestätigt am29.10: **Ersatzdateien folgen später**. Das blockiert nicht die
Analyse der anderen Quellen, wohl aber erfundene Detailfelder und den vollständigen
neuen Fünf-Formate-Umfang. Dateihashes stehen in der Reviewzuordnung unter source_quality.
Die gültigen DOCX wurden strukturell/inhaltsbezogen, nicht als Layoutabnahme geprüft.

Der zusätzliche Scan `Document_261029_073807.pdf` hat zwei Bildseiten, beide
visuell geprüft. Seite1: Gülcan-Notizen; Seite2: Susanne-Notizen. Preise/
Vergütungsvermerke sind unbestätigt und keiner öffentlichen Leistung eindeutig
zugeordnet: kein Preisimport. Susannes handschriftliche Supervisions-/Vortrags-
ideen sind **nicht** neue Qualifikationen oder bestätigte zusätzliche Titel.
Die acht kanonischen Workshops und44-Stunden-Einordnung bleiben unverändert.
Briefbogenlogo begründet keine neue Arbeitgeber-/Kooperationsbehauptung.

| Familie / stabiler Key | Format / Key | Tatsächlich belegter Rahmen | Status |
| --- | --- | --- | --- |
| Business & Balance / family/business-balance | Tagesworkshop / business-balance/day |10:00–16:30 nur aus Format2P14; weiterer Ablauf unbekannt | REVIEW_REQUIRED, Ersatz nötig |
| Business & Balance / family/business-balance |6-Wochen-Vertiefungsprogramm / business-balance/six-weeks |6 Wochen,1 Session/Woche,60 Minuten; „online oder live“; eigenständig oder Vertiefung; Community optional | Fakten READY; kurze Public Copy Preview/Production APPROVED29.10, Registry-Bindung offen |
| Gesundheit im Unternehmensalltag / family/gesundheit-im-unternehmensalltag | Halbtagsworkshop / gesundheit/half-day |10:00–14:00,240 Minuten, Präsenz im Unternehmen/extern, Teams jeder Größe | Fakten READY; kurze Public Copy Preview/Production APPROVED29.10, Registry-Bindung offen |
| Konfliktklärung & Teamreflexion / family/konfliktklaerung-teamreflexion | Konfliktklärung im Team – Ein Tag der Klärung / konfliktklaerung/day |10:00–16:00, akutes Konfliktthema; Anpassung an Team/Anliegen | Fakten READY; kurze Public Copy Preview/Production APPROVED29.10, Registry-Bindung offen |
| Konfliktklärung & Teamreflexion / family/konfliktklaerung-teamreflexion | Reflexionsreihe / teamreflexion/series | Existenz aus autorisiertem Addendum; Dauer/Frequenz/Details unbekannt | REVIEW_REQUIRED, Ersatz nötig |

Business & Balance: Unternehmerinnen als Hauptzielgruppe, alleinerziehende
Unternehmerinnen als besonderer Fokus, **nicht** Ausschluss aller anderen.
Untertitel „Struktur, Klarheit & Energie für Unternehmerinnen“. Sechs Module
bleiben Programmstruktur, keine neuen globalen Themen. „Live“ bleibt bewusst
unbestimmt; weder Präsenz noch ausschließlich synchrones Onlineformat behaupten.

Gesundheit: vier Kernbereiche Bewegung, Ernährung, Stressregulation, mentale
Gesundheit. Ganztag ist Variante ohne erfundene Dauer; vertiefende Übungen sind
Option, Follow-up nach4–6 Wochen und Ergonomie-Begehung vorab sind Add-ons.
Keine vier neuen unabhängigen Katalogangebote daraus erzeugen. Community ist
ein optionales Add-on des Business-&-Balance-Programms. Keine Kalenderdaten.

| Familie | Source Boundary exakt nachzulesen | Verbindlich getrennt halten |
| --- | --- | --- |
| Business & Balance | guelcan-balance-six-weeks, HaupttextP12 | Coaching + Training; keine Therapie/ärztliche oder psychotherapeutische Behandlung/Rechts-/Steuerberatung |
| Gesundheit | guelcan-health, HaupttextP13 | Gesundheitsförderung + Training; keine ärztliche/psychotherapeutische/heilkundliche Behandlung, Diagnosen oder individuelle Ernährungstherapie |
| Konfliktklärung & Teamreflexion | guelcan-conflict-day, HaupttextP12 | Coaching + Moderation; keine Mediation im Sinne des Mediationsgesetzes, ausgebildete Supervision, Rechtsberatung oder rechtsverbindliche Streitbeilegung |

Diese Tabelle ist eine Scope-Zusammenfassung für die Vorbereitung, kein neu
formulierter öffentlicher Disclaimer. Eine spätere Public Copy muss den tatsächlich
freigegebenen Originalabsatz referenzieren und dessen Umfang verlustfrei erhalten.
Nichts begründet eine Mediatorinnen-/Supervisorinnenqualifikation für Gülcan.

Kategorien neuer Familien: bestehende Coach-Zuordnung unverändert. Gesundheit
zum kanonischen Gesundheitsthema und Konfliktformate zu Teams & Konflikte sind
**PROPOSED** für die neuen Angebote; Business & Balance benötigt konsolidierte
fachliche Themenzuordnung. Keine bloße Schlagwortzuordnung oder Modultaxonomie.

**Copyright-/Public-Copy-Gate:** Unterlagen enthalten ausdrückliche Nutzungs-
vorbehalte. Analysezugriff ist erlaubt, kein vollständiger Konzept-/Übungs-/
Arbeitsblatt-/Ablaufplanabdruck in Git oder Website. Vorgesehen sind nur Titel,
Format, Zielgruppe, Dauer, Durchführungsart, grobe Schwerpunkte, kurze neue
Zusammenfassung und belegte Leistungsgrenze. Manuel bestätigt nach konkreter
Rückfrage am29.10 ausdrücklich **Gülcan: Vorschau und IONOS**, einschließlich
Profil, Porträt und kurzer öffentlicher Angebotsdarstellungen. Für die tatsächlich
belegten Kurzangaben der fünf Formatkandidaten: OFFERING_CONTENT=APPROVED;
für die drei Familien Public-Copy-Recht=APPROVED, Scopes preview/production.
Das ist eine neue konkrete Freigabe, nicht aus der alten Profilfreigabe abgeleitet.
Die [ergänzte Rechtematrix](../content/coach-publication-matrix-2026-09-24.md#zusätzliche-rechtefreigabe-gülcan-vom-29102026)
belegt die Entscheidung. Vollständige geschützte Konzepte und unlesbare Details
sind nicht umfasst; keine Inhalte erfinden. Registry-Subjectbindung und jeder
Website-Release bleiben separate Schritte, jetzt kein Upload.

## Assetmatrix

Stabiler Itemkey je Coach `asset/portrait`, Referenz jeweils `images/coaches/<Datei>`.
Alternativtexte werden aus dem jeweiligen bestehenden img-alt übernommen, keine
Person erfunden. Alle acht tatsächlichen Bytehashes erneut mit Inventur verglichen.
Approved-Quellbytes bleiben unverändert; keine BLOBs, Originalporträts oder neue
Bilddateien geschrieben. Current processed asset wird referenziert, nicht erraten.

| Coach | Datei / Alttext | SHA-256 | Preview / Production |
| --- | --- | --- | --- |
| CG | christian-galvano.webp / Porträt von Herrn Christian Galvano |67c0a7ca915c66bcf1c2b130b0bc952e2248dc975c38c58cb5a7f2a4d9afbfa5 | APPROVED / APPROVED |
| MR | manuela-rodriguez.webp / Porträt von Manuela Rodríguez |1bba4ca4fe8ab94b6e30ff6d725681e013d4f3fe748a67feba1e24700bd4d0a9 | APPROVED / APPROVED |
| ES | elisabeth-schwabauer.webp / Porträt von Frau Elisabeth Schwabauer |56b1fd0062b00edec5707d2cae0baf7950c788522e698cadfb452721611e4e64 | APPROVED / UNKNOWN |
| CH | kein Porträt, vorhandenes Monogramm | NOT_APPLICABLE | NOT_REQUIRED / NOT_REQUIRED für Bild |
| GE | guelcan-elmas-brandes.png / Porträt von Frau Gülcan Elmas-Brandes |f94067e10356696e82b2d76288e6f2d3cde2a656c17f2d7b6f07a86d880c563b | APPROVED / APPROVED29.10 |
| WN | wegner-ney.jpg / Porträt von Herrn T. Wegner-Ney |bc4a7d0615ad1650d5dab3cb2df3fccafea40a2c908a65ef3a3ae2e0ea1dfc72 | APPROVED / UNKNOWN |
| GC | goran-celic.png / Porträt von Herrn Goran Celic |f56f85630cd1fd183a9eb32e05a56d8ce8700a1fe1b9b83d965890fdc547e246 | APPROVED / UNKNOWN |
| SB | stefanie-becker.webp / Porträt von Frau Dr. Stefanie Becker |aed9aaabddeeed539d826e83f5345c2828072a856b8125619e36c83dc1e0d3c2 | APPROVED / UNKNOWN |
| SK | susanne-klemm.webp / Porträt von Frau Susanne Klemm |d494f308dbc4f3a1e95d3f31dd17072ca543bfe18de036a53553cd281eeac21e | APPROVED / UNKNOWN |

WN hat unterschiedliche bereits vorhandene Dimensionsangaben im Kartenmodell
und Profiltemplate. Kein neuer Person-/Assetkonflikt, sondern presentation-only:
im Parity-Manifest separat erhalten und beim späteren Rendering prüfen, nicht
in diesem Vorbereitungsslice heimlich am öffentlichen Layout korrigieren.

## Evidencematrix

APPROVED bedeutet hier **bestehende dokumentierte Projekt-Veröffentlichungs-
freigabe**, nicht automatisch neu attestierte persönliche Einwilligung oder
Registry-Publication. Zentrale Quelle: [Freigabematrix](../content/coach-publication-matrix-2026-09-24.md),
für SK zusätzlich [Quellen-/Freigabebericht](../content/susanne-klemm-preview-2026-10-23.md).
Bekannter Freigebender im Projekt ist Manuel. Zeitpräzision DAY für Preview:
21.10 für die acht bestehenden Profile,23.10 für Susanne; Uhrzeit unbekannt.
Historische Originalfreigaben bleiben UNKNOWN, soweit nicht explizit dokumentiert.
MR hat separate Profil-/Porträtfreigabe24.09 und Namens-/Abschlussbestätigung25.09;
daraus keine Uhrzeit und keine Freigabe neuer Inhalte konstruieren.

| Coach | PROFILE_CONTENT | PORTRAIT_ASSET | PREVIEW_PUBLICATION | PRODUCTION_PUBLICATION | Neue Registry-Bindung |
| --- | --- | --- | --- | --- | --- |
| CG | APPROVED bisheriger Inhalt | APPROVED bestehende Bytes | APPROVED | APPROVED bisheriger Umfang | REVIEW_REQUIRED |
| MR | APPROVED bisheriger Inhalt | APPROVED bestehende Bytes | APPROVED | APPROVED bisheriger Umfang | REVIEW_REQUIRED |
| ES | APPROVED bisheriger Inhalt | APPROVED bestehende Bytes | APPROVED | UNKNOWN | REVIEW_REQUIRED |
| CH | APPROVED bisheriger Inhalt | NOT_REQUIRED | APPROVED | UNKNOWN | REVIEW_REQUIRED |
| GE | APPROVED einschließlich bestätigter kurzer Angebotsdarstellungen29.10 | APPROVED bestehende Bytes29.10 | APPROVED bestätigter Umfang29.10 | APPROVED bestätigter Umfang29.10 | REVIEW_REQUIRED für konkrete Subjects; Rechtefreigabe vorhanden |
| WN | APPROVED bisheriger Inhalt | APPROVED bestehende Bytes | APPROVED | UNKNOWN | REVIEW_REQUIRED |
| GC | APPROVED bisheriger Inhalt | APPROVED bestehende Bytes | APPROVED | UNKNOWN | REVIEW_REQUIRED |
| SB | APPROVED bisheriger Inhalt | APPROVED bestehende Bytes | APPROVED | UNKNOWN | REVIEW_REQUIRED |
| SK | APPROVED bisheriger Inhalt | APPROVED bestehende Bytes | APPROVED | UNKNOWN | REVIEW_REQUIRED; neue Scanideen nicht eingeschlossen |

Die neun persönlichen Einwilligungs-/Rechteattestationen sind als eigenständige
DB-Voraussetzung **UNKNOWN**, nicht aus einer vorhandenen Website oder generischem
approved=true erfunden. Das verlangt keine pauschale Wiederholung aller bereits
erteilten Freigaben: ein konsolidiertes Review kann die vorhandenen Nachweise
unter Wahrung ihres Umfangs an Manifest/Revision/Assethash/Umgebung binden.
Fehlender Name/Zeitpunkt bleibt unbekannt. Aktueller attestierender Operator und
technische recorded_at sind getrennt von historischen approved_by/at/date.

## Field Loss Und Kleinstmöglicher Zielvertragsvorschlag

| Feldgruppe / betroffen | Heutiges Modell | Nötige vorbereitete Abbildung |
| --- | --- | --- |
| Rollen/Descriptors, alle9 | keine eigene öffentliche Rolle; operative Rollen ungeeignet | versionierte role_code + source/public_display-Liste; Quellanzeige erhalten |
| Öffentliche/interne Qualifikationen,8 Coaches/30 Einträge | nur gemischter Hintergrundtext; kein Public-/Verification-/Evidence-Feld | versionierte Qualification-Snapshotzeilen mit stabilem Source-Itemkey, kanonischem Label, Public-Flag/Display; Admin-Nachweise getrennt |
| Profilabschnitte, Teaser/Fokus/Karten, alle9 | scalar description verliert Abschnitts-/Kartenstruktur | optional typisierte public_sections/topic_cards/focus_labels/teaser, keine HTML-Payloads; keine leeren Bereiche |
| Sprachen GE, Zitat MR, externe Links CG/MR/CH/GC | nicht vollständig darstellbar | optionale typisierte Felder; Linkziele je Umgebung erhalten, erlaubte https-Ziele ohne eingebettete Zugangsdaten |
| ES Psychotherapie | Offering.type kennt nur fünf Formattypen | separates service_domain=psychotherapy und bookable=false, Originaltitel/Boundary; Format darf nicht als coaching ausgegeben werden |
| GE Angebotsfamilien/Varianten | Offering hat keinerlei Parent-/Group-/Optionsfelder | stabile family_key an Formaten, versionierter Familienkopf, optionale typisierte Rahmen-/Modul-/Options-/Boundary-Metadaten |
| Profil-/Porträt-/Angebotsevidence, alle9 |0008 bindet nur Coach/Revision/kind, nicht genaues Asset/Angebot oder historische Status/Approver/Datumspräzision | subject_type + subject_key + subject_content_hash + scope/status, historical approved_by/at/date nullable und precision; tatsächlicher Operator getrennt |
| Maße/Monogramme / WN-Unterschied | Renderingmetadaten | harmless presentation-only, in späterer Parity-/Browserprüfung erhalten |
| Noch unbestimmte Live-Bedeutung / neue Quellen | keine sichere fachliche Aussage | manual decision / UNKNOWN, keine stillen Defaults |
| Privatdaten / interne Preise / vollständige Konzepte | nicht öffentliche Registry-Domain | intentionally excluded private data; kein Field Loss |

**Minimale Persistenzvorbereitung, keine neue Migration erstellt:** COACH-1-
Revisionen bleiben Owner. Relationale Qualifikations-/Rollen-Snapshots statt
zweiter Coach- oder Zertifikatsverwaltung; optionale typisierte Präsentations-
felder. Ein versionierter Familienkopf ist fachlich gerechtfertigt, weil der
bestehende Offeringdatensatz keinerlei Gruppenidentität hat und Boundary/
Zielgruppe/Optionen sonst je Format dupliziert oder verloren würden. Bestehende
Offerings erhalten nullable family_key; flache Katalogtitel bleiben kompatibel.
Varianten/Add-ons sind Metadaten unter der Familie, keine neuen Einzelangebote,
keine Preis-/Buchungs-/CAL-2-Tabellen und kein globaler Qualifikationskatalog.

Format und Leistungsdomäne bleiben orthogonal: bestehende Formattypen erhalten;
psychotherapy/consulting/coaching/training/moderation/health_promotion nur als
belegte Leistungsdomäne, mehrere explizite Domänen möglich. Nicht aus Modulnamen
oder Methoden schließen. Therapeutische Anzeige darf nicht aktiv buchbar sein.

Ein eigener späterer, synthetisch getesteter Erweiterungsslice muss dazu
Domain/API/Admin-Editor/Persistenz/Importhash/Public-DTO konsistent erweitern.
Insbesondere darf der jetzige Scalar-Editor zusätzliche Felder bei einer neuen
Revision nicht verlieren. Freigaben/Submitted-Snapshots bleiben unveränderlich;
Public-Export enthält weder interne Qualifikationen noch Nachweisreferenzen,
Prüfzustände, Originalquellen, historische Genehmiger oder operative UUIDs.
0008 allein reicht für das29.10-Ziel **nicht**; keine still ausgeführte Migration0009.

## Bedingter Importumfang Und Dry Mapping

Dies ist eine In-Memory-Planung gegen einen **angenommenen, ausdrücklich noch zu
bestätigenden leeren Zielbestand**, keine SQL-Preflightbehauptung. Tatsächliche
DB-Identitäten und bestehende Datensätze sind NOT_READ. Bei gefundenen bestehenden
Quellbindungen wird erst mit dem echten schreibfreien DB-Dry-Run neu gezählt;
keine Namenszuordnung oder stilles Legacy-Adopt. Alle Zahlen stammen aus der Matrix.

| Geplanter Umfang nach geschlossenem Technik-/Evidence-Gate | Anzahl |
| --- | --- |
| Neue Coaches / bestehende Coaches matchen |9 /0 nur unter Empty-Target-Voraussetzung |
| Initiale Draft-Profilrevisionen |9 |
| Kanonische Themen-Lookups / vom Import neu erzeugte Themen |8 /0 |
| Redaktionelle Themenlinks / zusätzliche Kompetenzlabels |22 /14 |
| Öffentliche Qualifikations-Snapshotrecords |30 |
| Bestehende explizite Angebotskatalogtitel |25, davon24 aktiv im Katalog und1 separate nicht buchbare Therapieanzeige |
| Assetreferenzen / bewusst ohne Bild |8 /1 |
| Automatische Preview-/Production-Publications im Basisschreibplan |0 /0 |
| Beabsichtigte Preview-Parity nach separater frischer Revisionsattestation |9; noch nicht freigegeben/ausgeführt |
| Neue GE-Familien / Formatkandidaten zurückgehalten |3 /5, nicht in den25 Basistiteln enthalten |
| Noch zu bindende Personeneinwilligungsattestationen / unbekannte Production-Scopes |9 /6 |
| Detailquellen nachzuliefern |2 |
| Noch offene Review-Subjects in konsolidiertem Bericht |13:9 Personeneinwilligungsattestationen,2 Ersatzquellen,1 Live-Bedeutung,1 Susanne-Notizabgleich;8 neue Gülcan-Copy-/Angebotsrechte durch Bestätigung29.10 geschlossen |

Review-Subjects sind nicht13 einzelne Rückfragerunden. Quellenersatz und Live-
Bedeutung können für den bestehenden25-Titel-Basisumfang
ausdrücklich ausgeklammert werden; für den vollständigen neuen GE-Umfang nicht.
Die sechs unbekannten Production-Scopes benötigen für Preview keinen Nachtrag.
Gülcans jetzt erteilte IONOS-Rechte ändern weder die geplanten null automatischen
Production-Publications noch die unverändert ausgelieferte Website mit zwei echten Profilen.
Die Auswertung meldet WOULD_CREATE_IF_GATES_PASS9, WOULD_MATCH_CANONICAL_TOPICS8,
WOULD_LINK_EDITORIAL_TOPICS22, WOULD_SKIP_PORTRAIT1, BLOCKED_CURRENT_TARGET9.
Tatsächliche Business-Mutationen und Veröffentlichungseffekte: **je0**.

## Historischer Vorbereitungsstand Des COACH-3B-Runbooks

**Vorbereiteter Plan, jetzt nicht ausführen.** Die existierende COACH-3A-CLI
akzeptiert absichtlich nur synthetische Fixtures. Es gibt noch keinen echten
Import-APPLY-Schalter und keinen Aufruf, der diesen Schutz umgehen soll.

1. Vor dem einen Operatorfenster: Zielumgebung/Owner/Zeitraum und exakter
   Git-/Schema-/Feldvertragsstand freigegeben;0 BLOCKED, alle in Scope liegenden
   Review-Subjects geschlossen; neue GE-Inhalte entweder vollständig freigegeben
   oder ausdrücklich aus dem Batch ausgeschlossen. Quellen-/Rechtehashmanifest
   fixieren, fachlichen Parity-Stand separat vom neuen Contentumfang festhalten.
2. Ein Preflight: Zustand/Migrationen/Owner/Grants/gebundene Source IDs read-only
   erfassen, laufende Dienste/PG-Loopback und Co-Host schützen. Vollständiges
   geschütztes DB-Backup mit Hash, Schema-/Rollenbestand und Restoreprobe vorhalten.
   Keine App-/Migratorpasswörter in Skriptargumenten, Reports oder Chat.
3. Migrationen nur im genehmigten Ziel und Umfang: bisheriger VPS-Stand0006
   benötigt bereits0007 vor0008; der neue Verlustfrei-Vertrag zusätzlich seine
   noch zu implementierende/prüfende Erweiterung. Nicht isoliert0008 auf ein
   unbekanntes Schema anwenden. Bei Abweichung STOP, kein Schema-Autoupgrade.
4. Ein gesamter VALIDATE-/DB-READ-ONLY-Dry-Run gegen das exakte Manifest:
   Source Identity/erwartete Versionen, echte Themen-UUIDs, Bytehashes, unveränderliche
   Pfade, Qualifikationen/Rollen, Missing Items und jede Evidence-Bindung prüfen.
   Bericht konsolidiert einmal durch zuständigen Menschen bestätigen. Geänderte
   Daten/Hashes/Grants invalidieren den Bericht, kein Coach-für-Coach-Dialog.
5. Erst separat freigegebener realer APPLY: ein begrenzter Gesamtbatch in einer
   Transaktion, persistente technische Run-ID mit Quell-/Vertragshashes und
   Zählwerten, kein personenbezogener Rohpayload im Runlog. Bei Fehler alles
   zurückrollen; Erfolgsresponse erst nach bestätigtem Commit. Zunächst Drafts,
   keine impliziten Accounts, CAL-1-Themenrechte oder Website-Veröffentlichung.
6. Gleichen Batch zweimal erneut lesen/vergleichen: null zusätzliche Coaches,
   Revisionen, logische Offerings/Assets oder Business-Audits; alle Domänen-/
   Ledgerzeilen einschließlich xmin und kanonische Projektion identisch.
   Technische Runmetadaten separat. Änderungen durch Menschen führen zu Conflict.
7. Freigabereview/Einwilligung/Asset/Scope an konkrete Revision attestieren;
   erforderliche Preview-Projektion nur lokal in privatem QA-Artefakt erzeugen,
   sofern dieser Scope separat genehmigt ist. Vollständige Neun-Profil-Parity kann nicht aus
   ungeprüften Drafts oder leeren Veröffentlichungen behauptet werden.
8. Gesamte Parity-/Browsermatrix, Audit-/Privatdaten-/Cleanup-/Co-Host-Nachweise
   erfassen. Freigegebenen dauerhaften Import nicht als Testdaten löschen;
   nur temporäre Operatorreports/Verbindungen entfernen, minimale Evidence
   geschützt behalten. Ein separates Publication-Go entscheidet Pages/IONOS.

## Parity Und Recovery Gate

Baseline bleibt der vorhandene kanonische Preview-Stand mit neun Personen,
ihren Routen/Namen,22 Themenlinks,25 Katalogtiteln, acht Bildhashes und vollständigen
sichtbaren Absätzen/Karten/Qualifikations-/Hintergrundlisten/Zitat/Links/Boundaries.
Vergleich muss sowohl Daten als auch tatsächlich gerenderte Textabschnitte
erfassen; nicht nur Personenanzahl. Neue GE-Inhalte getrenntes freigegebenes Delta,
kein unerklärter Parity-Unterschied. Linkziel MR bleibt umgebungsabhängig;
gemeinsame Kontaktfunktionen, noindex/keine Production-Durchlässigkeit erhalten.
Spätere Browser-QA:2048/1440/1280/960/390CSS-px, echtes200%-Zoom, Tastatur/Fokus,
Reduced Motion, Bildladen und tatsächliche Textüberlagerung/Abschneiden.
Jetzt keine neue Browser-/Website-Abnahme, da keine Oberfläche geändert wurde.

Rollback vor Commit: gesamte Importtransaktion abrollen, keine partiellen Coaches.
Nach Commit: keine Hard Deletes/History-Guard-Abschaltung als Reparaturtrick;
kontrollierter Restore des hashverifizierten Pre-Import-Backups in isolierte DB,
Schema/Owner/Grants/Migrationen/Quellbindungen/Audit/Asset-/Themenzuordnung prüfen.
Nur im eigenen genehmigten Wartungsfenster auf das freigegebene Ziel zurückführen;
keinen bestehenden Chatbot oder andere Änderungen überschreiben. Bei späteren
unabhängigen Writes kein blinder Vollrestore, separater Repair-/Incident-Gate.
Run-ID bindet Backup, Manifest, Transaktionsausgang und Recovery-Nachweis.
Keine Assetdatei vor separatem Release überschreiben, keine externen Publication-
Side-Effects im Import: Pages und IONOS bleiben vom DB-Rollback unberührt.

## Verifikation Der Vorbereitung

Reine Tests: öffentliche/interne Qualifikation, Rollen-/Themen-/Kompetenztrennung,
Therapie versus Coaching, genaue Profil-/Porträt-/Revisions-/Umgebungsbindung,
Unknown/Datum-ohne-erfundene-Uhrzeit, fehlendes Porträt, Familien/Optionen,
unlesbare Quellen, vier Field-Loss-Klassen und deterministischer Trockenlauf
ohne Datei-/Netzwerkzugriffe oder Inputmutation. Änderungen am unbekannten
Quellstand und neue nicht klassifizierte Felder stoppen statt stillen Verlusts.
Die vorbereiteten Projektionstests sind **kein** Beweis einer bereits erweiterten
COACH-1-Public-Projection oder Datenbankmigration.
Tatsächlich am29.10 ausgeführt: **25 fokussierte neue Tests**, gesamte lokale
Suite **584 PASS /19 vorgesehene Skips** (17 Staging,2 dedizierte lokale PG-Gates).
Die PG-Gates wurden in diesem reinen Vorbereitungsslice nicht erneut ausgeführt;
kein Runtime-/SQL-Code geändert. Compileall, pip check, Node-Syntax, aktuelle
Dokumentlinks/Archivintegrität und git diff --check PASS. Quelle/Report zweimal
erzeugt: identisch; finaler Report-SHA-256:
`eec21f2bf22048b719cc89db9058bb1d11db564028514552af0b3e5a665db29c`.
Nur Quelldateianalyse und hypothetische Planung, keine DB-Verbindung oder
Registry-/Website-Ausgabe. Kein Runtime-/Browser-/Server-Abnahmeclaim daraus.

Reproduktion in **einem PowerShell-Terminal**, Arbeitsverzeichnis Repositorywurzel,
keine Passwörter/Secrets erforderlich, keine APPLY-Option:

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website'
& '.\tools\node-v22.16.0-win-x64\node.exe' '.\scripts\coach3-static-inventory.mjs'
& '.\tools\node-v22.16.0-win-x64\node.exe' '.\scripts\coach3b-canonical-inputs.mjs'
& '.\apps\webapp\.venv\Scripts\python.exe' '.\scripts\coach3b_preparation.py' --validate
```

Erwartet: validation=PASS, go_no_go=NO_GO_APPLY, BLOCKED9,
business_mutations=0. Der separate Status ist absichtlich kein Exitfehler der
korrekt abgeschlossenen Vorbereitung. Generierte Reports unter `.tmp` bleiben
ignoriert; private Scan-Renderbilder nach Sichtprüfung entfernt. Kein neuer
Source-Dokumentdump, Zertifikat oder Porträt im Commit. Globale Skills unverändert.

## Historischer Nächster Block Nach Der Vorbereitung

**Verlustfreien Zielvertrag lokal mit synthetischen Daten umsetzen und abnehmen.**
Zweck: die hier belegten technischen Field-Loss-Blocker vor Echtdaten schließen.
Inputs: bestätigte29.10-Entscheidungen, Reviewmatrix und minimaler Modellvorschlag.
Deliverables: kompatible Domain-/DB-/Editor-/Import-/Projektionsfelder und ein
gesamter synthetischer Parity-/Evidence-/Familientest. Done: kein stiller Verlust,
öffentliche/interne Trennung und korrekte Boundaries; noch kein realer Import,
keine Servermigration oder Veröffentlichung. Ersatzquellen und konkrete
konkrete Nachweisbindungen können parallel vorbereitet werden. Für COACH-3B APPLY
bleibt es bis dahin bei **NO-GO**, nicht nur „Ausführung noch nicht angeklickt“.

## COACH-3C Recheck Des Realen Bestands

Nur VALIDATE/in-memory, keine DB-Verbindung oder echten UUIDs: Alle9 kanonischen
Profile werden tatsächlich als `ProfileContent.target_version=1` validiert.
Ein rekonstruktiver Leaf-Audit vergleicht827 Quellfelder mit dem Ziel; unbekannte
Felder, veränderte Werte und ungelöste Ausdrücke blockieren statt als „gemappt“
durchzugehen. Die22 Themenlabels bleiben erhalten, ohne8 fachliche Themen-IDs
in erfundene PostgreSQL-UUIDs umzuwandeln. Die14 Kompetenzlabels,30 öffentlichen
Qualifikationseinträge,25 bisherigen Katalogtitel und8 Porträtreferenzen bleiben
darstellbar. Quellen-/Template-Metadaten sind ausdrücklich nicht öffentliche
Profilfelder. Interne/private Inhalte und unbestätigte Preise sind Policy-
Ausschlüsse, keine versehentlich verworfenen Felder.

| Gate | Ergebnis |
| --- | --- |
| Tatsächliche Zielmodellvalidierung |9 PASS /0 FAIL |
| Unbeabsichtigter kanonischer Feldverlust |0,827 geprüfte Felder |
| Fachlich freigabefertig für echten APPLY |0 READY /9 REVIEW_REQUIRED /0 technisch BLOCKED |
| Echte DB-Verbindung / Mutationen |0 /0 |
| Echte öffentliche Registry-Projektion / Veröffentlichung |Keine; nur in-memory Kandidat |

Die neuen Gülcan3 Familien/5 Formate sind separat erfasst und bleiben inaktiv.
Das synthetische Gegenstück beweist, dass das Zielmodell sie vollständig tragen
kann; es erfindet nicht die noch fehlenden echten Detailtexte. Offen bleiben
genaue Boundary-Kurztexte, Modulbezeichnungen, Standalone-/Erweiterungsentscheidung,
die genaue Bedeutung von „Live“ und die2 angekündigten Ersatzquelldateien.
Diese offenen Reviewfelder sind getrennt vom0-Verlust-Audit des bisherigen
kanonischen Bestands ausgewiesen.

Vor realem APPLY müssen weiterhin kanonische Themen-UUID-Zuordnungen, genaue
Objekt-/Revisions-/Hash-/Umgebungsnachweise und das separate Ziel-/Backup-/Rollback-
Ausführungsfenster genehmigt werden. Frühere Gülcan-Rechte für beide Websites
bleiben gültig; sie werden nicht in erfundene historische Registry-Nachweise
umgewandelt. Unbekannte historische Person/Datum bleiben NULL.

Reproduktion nach vorhandenem kanonischem Snapshot, **ein PowerShell-Terminal**,
Repositorywurzel; keine Passwörter, keine APPLY-Option:

```powershell
$env:PYTHONPATH = (Resolve-Path '.\apps\webapp\src').Path
& '.\apps\webapp\.venv\Scripts\python.exe' '.\scripts\coach3b_preparation.py' --validate
Remove-Item Env:PYTHONPATH
```

Erwartet: validation=PASS,9 Modellvalidierungen,0 Verlust,9 REVIEW_REQUIRED,
NO_GO_APPLY und business_mutations=0. Deterministischer Report-SHA-256:
`1e4336dd8abb95e7ee23babb5da503aecdd26a4ba341594b3bf566c4a2736b71`.

**Ein empfohlener nächster Gate: COACH-3B Reviewabschluss ohne APPLY.**
Zweck: die verbliebenen Nachweis-/Mapping-/Quellenentscheidungen gemeinsam
abschließen. Inputs: neue Zielvalidierung, bestehende Reviewmatrix und verfügbare
Ersatzquellen. Deliverable: freigegebene konkrete Zuordnungs-/Evidence-Matrix mit
begründeten verbleibenden Ausschlüssen. Done: jeder Reviewpunkt ausdrücklich
entschieden; ein echter Import benötigt danach weiterhin seine eigene Freigabe.

## COACH-3B Reviewabschluss 29.10

Manuels neuer Reviewauftrag erlaubt ausdrücklich, vorhandene belegte Freigaben,
kanonische Zuordnungen und bereits entschiedene Regeln selbstständig zu schließen.
Ein optionales UNKNOWN ist kein zusätzlicher Entscheidungsbedarf. Werkzeug:
[coach3b_review_closure.py](../../scripts/coach3b_review_closure.py); ausschließlich
VALIDATE/DRY-MAPPING im Speicher. Source-/Review-/Rechtedokumente,9 Templates und
8 Assetbytes sind hashgebunden; geänderte Dateien stoppen den Lauf.

### Finale Field- Und Evidence-Matrix

Identitäten/Pfade bleiben exakt wie in der Coachmatrix. Künftige Personen-UUIDs
werden erst vom genehmigten Import erzeugt. Alle22 redaktionellen Themenlinks
und18 Kategoriebeziehungen sind durch den bestehenden Bestand entschieden;
„Alle Themen“ bleibt berechnet. Der spätere technische MATCH_ONLY löst echte
UUIDs gegen8 eindeutige kanonische Referenzen auf, ohne Fuzzy-Matching oder
automatische Themenanlage. Keine neue Zuordnung aus Lebenslauf/Modulnamen.

| Coach | Gate | Themen / Kompetenzen / Q / Formate | Porträt | Preview | Production | Objekt-Evidence Preview / Production |
| --- | --- | --- | --- | --- | --- | --- |
| Christian Galvano | READY |3 /0 /4 /0 | vorhanden | APPROVED21.10 | APPROVED bestehender Umfang |7 /7 |
| Manuela Rodríguez, M.A. | READY |3 /0 /3 /0 | vorhanden | APPROVED21.10 | APPROVED24.09, Name/Abschluss25.09 |6 /6 |
| Elisabeth Schwabauer | READY |3 /3 /3 /17 | vorhanden | APPROVED21.10 | UNKNOWN, nicht vorgesehen |23 /0 |
| Carolin Hupp | READY |1 /3 /1 /0 | NOT_REQUIRED | APPROVED21.10 | UNKNOWN, nicht vorgesehen |3 /0 |
| Gülcan Elmas-Brandes | READY |3 /2 /7 /5 | vorhanden | APPROVED29.10 | APPROVED29.10 |18 /18 |
| T. Wegner-Ney | READY |3 /3 /3 /0 | vorhanden | APPROVED21.10 | UNKNOWN, nicht vorgesehen |6 /0 |
| Goran Celic | READY |1 /3 /0 /0 | vorhanden | APPROVED21.10 | UNKNOWN, nicht vorgesehen |3 /0 |
| Dr. Stefanie Becker | READY |2 /0 /1 /0 | vorhanden | APPROVED21.10 | UNKNOWN, nicht vorgesehen |4 /0 |
| Susanne Klemm | READY |3 /0 /8 /8 | ausgewählte WebP | APPROVED23.10 | UNKNOWN, nicht vorgesehen |19 /0 |

Profile, Rollen,30 öffentliche Qualifikationen und14 Kompetenzlabels sind anhand
der vorhandenen kanonischen Texte getrennt bestätigt. Public Label bedeutet
keine zusätzliche Urkundenprüfung; SOURCE_ASSERTED/alte Prüfhinweise bleiben
intern. Kompakte öffentliche Sammelüberschrift künftig bevorzugt:
„Qualifikationen & beruflicher Hintergrund“. Keine aktuelle Websiteänderung.

Belege: [datierte Veröffentlichungsmatrix](../content/coach-publication-matrix-2026-09-24.md)
und [Susannes konkrete Freigabe](../content/susanne-klemm-preview-2026-10-23.md).
Nicht bloße Sichtbarkeit, sondern dokumentierte Projektentscheidungen tragen
Profil-, Bild-, bisherige Titel-/Qualifikations- und Umgebungsfreigaben.
Bekannte Projekttage bleiben DAY-Präzision; CGs ursprüngliches Production-Datum
und alle unbekannten persönlichen Originaleinwilligungen bleiben NULL.
Die spätere `person_consent`-Zeile ist eine **aktuelle Operatorattestation der
dokumentierten Projektrechte**, keine erfundene Unterschrift des Coaches.

Die120 Objekt-Nachweispläne binden Source Identity, konkretes Objekt, Inhaltshash
und Umgebung. Profilhashes berücksichtigen fachliche Themenreferenzen; sie heißen
absichtlich `candidate_subject_sha256`, **nicht** ausführbarer `subject_hash`.
Reale Revisions-/Themen-UUIDs, Operator und recorded_at fehlen weiterhin bewusst.
Beim genehmigten Lauf: exakt aufgelöste Inhalte/UUIDs erneut hashen, mit dem
fachlichen Reviewmanifest vergleichen und erst dann Runtime-Nachweise binden.
Ein geänderter Inhalt invalidiert die Bindung; Preview ist keine Production-
Freigabe. Die6 unbekannten Production-Scopes bleiben geschlossen, nicht blockiert.

### Gülcan Und Fachliche Grenzen

Die3 Familien/5 Formate sind für den belegten Kurzumfang READY. Die beiden
Ersatzdateien bleiben **optional für diesen Umfang**, für vollständige Detail-
konzepte später weiterhin erforderlich. Kein Pflichtfeld erfordert deren Inhalt:
Reflexionsreihe bleibt generischer Formattyp `other`, konkrete Dauer unbekannt;
„online oder live“ bleibt `live_unspecified`, keine erfundene Ortsentscheidung.
Modultexte bleiben leer; „eigenständig oder Vertiefung“ begründet keine zweite
Variante oder Buchungsbehauptung. Alle Formate bleiben bookable=false.

| Familie | Formate | Optionen, keine zusätzlichen Hauptangebote | Leistungsgrenze |
| --- | --- | --- | --- |
| Business & Balance | Tagesworkshop,6-Wochen-Programm | Community zwischen Sessions | Coaching/Training; keine Therapie, ärztliche/psychotherapeutische Behandlung, Rechts-/Steuerberatung |
| Gesundheit im Unternehmensalltag | Halbtagsworkshop | Ganztagsvariante, vertiefende Übungen, Follow-up, Ergonomie-Begehung | Gesundheitsförderung/Training; keine ärztliche Behandlung, Psychotherapie, Heilbehandlung, Diagnostik oder individuelle Ernährungstherapie |
| Konfliktklärung & Teamreflexion | Tagesworkshop,Reflexionsreihe | keine zusätzlichen Optionen | Coaching/Moderation; keine Mediation, Supervision, Rechtsberatung oder rechtsverbindliche Streitbeilegung |

Die öffentlichen Boundary-Kurztexte setzen ausschließlich die im neuen Auftrag
verbindlich vorgegebenen Regeln um. Geschützte Konzepte, Programme, Ablaufpläne,
Übungen, Arbeitsblätter und unbestätigte Preise werden **nicht importiert** und
nicht öffentlich projiziert. Interne Ausschlusspolitik ist kein Preisdatensatz.
Susannes Scanideen bleiben außerhalb der8 bestätigten Workshops und erzeugen
keine neue Supervisionsqualifikation. Elisabeths Psychotherapie bleibt separat,
inaktiv/nicht buchbar und nicht Mindforge/Coaching zugeordnet.

### Exakte Dry-Mapping-Zahlen

Voraussetzung: später nachgewiesenes leeres Ziel ohne Source-Bindungen. Kein
aktueller DB-DRY-RUN und keine Zusage über den heute unbekannten Serverbestand.

| Planposition | WOULD, nicht ausgeführt |
| --- | --- |
| Coaches / Profilrevisionen / bestehende Coaches matchen |9 /9 /0 |
| Themen-Lookups / Kategoriebeziehungen / Profil-Themenlinks |8 /18 /22 |
| Kompetenzlabels / Rollenlabels / öffentliche Qualifikationen |14 /22 /30 |
| Interne Qualifikationen neu |0; Nachweis-/Prüfinformationen bleiben separat intern |
| Angebotsfamilien / Formatrecords / Varianten-Add-ons |3 /30 /5 |
| Aktive Katalogformate / inaktive separate Therapieanzeige |29 /1 |
| Porträtreferenzen / bewusst ohne Porträt |8 /1 |
| Geplante Registry-Preview-/Production-Publications |9 /3; Production nur CG/MR/GE, kein Website-Upload |
| Objekt-Evidence / aktuelle generische Attestationen |120 /30, zusammen150 interne Domänen-Nachweisrecords |
| Zusätzliche historische Import-Evidence-Ledgerzeilen |30 technische Referenzen; nicht als150 weitere Rechte zählen |
| Unbekannte Production-Scopes |6, keine positive Freigabe |
| Geschützte Langtexte / Preisrecords / erfundene optionale Details |0 /0 /0 |
| Tatsächliche DB-Mutationen / neue UUIDs / Uploads |0 /0 /0 |

Die25 bisherigen Katalogtitel bleiben separat von5 neuen Gülcan-Formaten.
Elisabeths4 vorhandene Darstellungsgruppen bleiben Präsentation, keine4 neu
erfundenen Angebotsfamilien. Die inaktive Therapiebezeichnung bleibt zusammen mit
der bestehenden Nicht-Hub-Therapiegrenze sichtbar, ohne aktives Therapieangebot.

### Projection Parity Und Aktueller Gate

Quell-Leaf-Audit plus Public-DTO-Vergleich prüfen9 Pfade/Namen,22 Themenlabels,
30 öffentliche Qualifikationen,25 alte Titel,8 Porträts und bestehende Grenzen:
**0 unbeabsichtigter Verlust**. Freigegebenes erwartetes Delta: Gülcan3 Familien/
5 kurze Formatdarstellungen/5 Optionen und explizite Grenzen. Keine geänderten
bestehenden Namen, Pfade, Qualifikationen, Porträts oder erfundene Termine.
Das ist semantische Dry-Projection-Parity, keine Abnahme eines neuen Astro-
Renderers. Ein späterer Website-Rebuild benötigt separate gerenderte Parity.

**DECISIONS REQUIRED FROM MANUEL: 0.** Fehlende optionale Angaben bleiben
UNKNOWN/NOT_IMPORTED. Keine neun erneuten Einzelfreigaben verlangen.
**GO FOR COACH-3B APPLY, pending separate Manuel approval.**
Einziger empfohlener nächster Block: **COACH-3B REAL APPLY**, nur nach separater
Freigabe des konkreten Ziels, Operators, Manifests und Backup-/Rollbackumfangs.

### Finales Späteres Ein-Fenster-Runbook

Noch nicht ausführen. Die bestehende Import-CLI bleibt **synthetic-only**; dieses
Review ergänzt weder echten File-Reader noch Real-APPLY-Schalter. Vor dem späteren
Serverfenster ist ein explizit freigegebener echter Runner lokal vorzubereiten
und zu prüfen; keinen synthetischen Guard umgehen. Fachliches GO ist nicht die
Behauptung, dieser Real-Runner sei bereits implementiert oder der VPS geprüft.

| Schritt | Prüfung / Stop-Regel |
| --- | --- |
| 1 Preflight | Zielumgebung, Source-Bindungen/Versionen, Owner/Grants, freie Betriebsgrenzen und Co-Host-Dienste lesen; kein Namens-/E-Mail-Match |
| 2 Backup | Vollständiges geschütztes, verschlüsseltes Ziel-DB-Backup, Hash/Restorepfad und Recovery-Verantwortlichen verifizieren; keine Secrets in Logs |
| 3 Schemastand | Tatsächlichen Stand lesen;0006 ist letzter dokumentierter Stand, kein aktueller Serverclaim |
| 4 Migrationen | Nur freigegebene fehlende0007/0008/0009 in Reihenfolge; lokal geprobt, Pool-Reconnect nach DDL; bei Abweichung STOP |
| 5 VALIDATE | Unveränderte Quellen-/Rechte-/Assetbytes und geschlossene Pflichtfelder;8 Themen/18 Kategorien exakt auflösen |
| 6 DB-DRY-RUN | Read-only echte Source-Bindungen/Versionen/UUIDs prüfen; bei anderem Bestand Mengen neu berechnen und STOP zur konsolidierten Bestätigung |
| 7 Bericht | Ein gesamtes freigegebenes Manifest mit realen technischen Bindungen und150 Nachweisplänen; keine Coach-für-Coach-Passwortserie |
| 8 APPLY einmal | Ein atomarer Batch:9 initiale Revisionen, exakte Nachweise und nur ausdrücklich genehmigte Registry-Zustände; keine Accounts/CAL-1-Rechte |
| 9 Wiederholung | Exakt gleicher freigegebener Input; kein blindes Wiederholen nach unklarem Commit-Ausgang |
| 10 Nullmutation |0 fachliche Mutationen, Domänen-/Ledger-/Auditzeilen und xmin unverändert; technische Runmetadaten getrennt |
| 11 Public Projection | Nur lokales geschütztes QA-Artefakt für explizite Umgebung, keine automatische Pages-/IONOS-Publikation |
| 12 Parity |9 Baselineprofile,25 alte Titel,3 Familien/5 neue Formate als erlaubtes Delta; keine privaten Felder |
| 13 Admin-Smoke | Echte freigegebene native Admin-Session; neue Ansicht nur lokal, keine still angelegten Realaccounts |
| 14 CAL-1-Sicherheit | Bestehende Regression, public_profile_path/coach_topics/Portal-Mappings unverändert |
| 15 Health | Dienste, PG localhost-only und Co-Host unverändert; keine zusätzliche öffentliche API |
| 16 Evidence | Source-/Migrations-/Backup-/Report-/Projektionshashes und geprüfte Counts geschützt sichern; nur eigene temporäre Ressourcen entfernen |
| 17 STOP | Vor Website-Deployment und jeder nicht ausdrücklich freigegebenen Aktivierung |

Fehlende kanonische Themen brauchen einen im Real-Block ausdrücklich genehmigten
Bootstrap von höchstens8 Themen/18 Kategoriezuordnungen; der Coach-Importer bleibt
MATCH_ONLY und erzeugt sie nicht selbst. Das ist ein technischer Ausführungs-
Preflight, keine erneut offene redaktionelle Themenentscheidung.

Rollback: Vor Commit komplette Transaktion zurückrollen. Nach bestätigtem Commit
keine DELETE-Reparatur gegen unveränderliche Historie: getrennt validierter
Ziel-DB-Restore oder freigegebene Vorwärtskorrektur mit denselben Source-IDs.
Keine Cluster-/Chatbot-DB restaurieren oder fremde Writer überschreiben. Vor dem
Fenster Restoreprobe/Schreibpause und Owner bestätigen; aktuelles Backup wurde
in diesem Review nicht erzeugt. Migrationen0007-0009 und Backup-/Rollbackplan vorbereitet,
reale Durchführung und Restore-Nachweis bleiben Ausführungsbedingungen.

### Tatsächliche Verifikation Des Reviewabschlusses

| Prüfung29.10 | Ergebnis |
| --- | --- |
| Gesamte lokale Suite |739 PASS,21 vorgesehene Integrations-Skips; keine DB-Verbindung in diesem Slice |
| Neue reine Review-/Parity-Tests |64 PASS:19 Closure- und45 Public-Parity-Tests |
| Neun-Profil-Dry-Mapping |9 READY/0 REVIEW_REQUIRED/0 BLOCKED,0 Feldverlust/zusätzliche Manuel-Entscheidungen;0 Mutationen/UUIDs |
| Determinismus | Zwei identische tatsächliche Closure-Läufe liefern denselben Reporthash |
| Live-Preview GET-only |18 Antworten: Index,9 Profile,8 Bilder;9 Namen/30 öffentliche Qualifikationen/25 bisherige Titel/8 Bytehashes/9 Routen/22 Themenlinks PASS |
| Negative Regression | Fehlende Rechte, vertauschte Umgebung, ungültige Pflichtfelder, geänderte öffentliche Labels, unbekannte Ausdrücke, veränderte Nachweise/Eingaben und verwaiste Familien stoppen; optionale UNKNOWNs blockieren nicht |
| Weitere Prüfungen | compileall, pip check, Dokumentlinks/Archivintegrität, git diff --check |

Aktuelle öffentliche Gegenprobe:
[Coaches-Preview](https://dp-manuel.github.io/CompetenceHub/coaches/), ausführbar
mit [coach3b_preview_parity.py](../../scripts/coach3b_preview_parity.py).
Festes HTTPS-Ziel, GET-only, begrenzte Antworten, Redirect-Zielprüfung vor dem
Folgen, keine Authdaten, kein HTML-/Bilddump und keine lokalen Berichtswrites.
Fehlende/zusätzliche Karten, falsche Themen oder geänderte Bildbytes scheitern.
Die5 neuen Gülcan-Formate sind freigegebenes Dry-Delta, keine aktuelle Live-
Erwartung. Der fehlgeschlagene Web-Tool-Zugriff wurde nicht als Websitefehler
gewertet; der direkte HTTPS-Abgleich lief erfolgreich und wiederholbar.

Closure-Report-SHA-256:
`7d79a9d1b91d959459e2c3a525a6c5763024dc15656c6f5890dfc89562dd0f59`.
Live-Response-Manifest-SHA-256 (URLs/Status/Bytehashes, kein HTML):
`93e48e1581c57d0a6daf64c854007564fda77c525b8722f6097428ad68c02aca`.
Auch der programmatische Closure-Einstieg prüft den tatsächlichen normalisierten
Payload gegen den eingefrorenen Quell-/Reviewstand, nicht nur dessen behauptetes
Hashfeld. Synthetische Policy-Auswertung kann keinen Real-Input-GO ausgeben.
Alle Familien müssen eindeutig einem der geprüften Coaches gehören. Beide
Reviewbefunde behoben, unabhängig mit19 Closure-Tests nachgeprüft; keine offenen
High-/Medium-Befunde im überprüften Review-Werkzeug-Scope.

Dieser reine Review ändert keine Domain/API/UI/SQL-Datei. Frühere native165/
109- und lokale PostgreSQL-Gates bleiben datierte COACH-3C-Nachweise und wurden
hier nicht erneut ausgeführt. Kein Live-Backend-/Restore-/Deployment-Abnahmeclaim.

Reproduktion in **einem PowerShell-Terminal**, Repositorywurzel; keine Passwörter
oder Secrets erforderlich, keine APPLY-Option in beiden Werkzeugen:

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website'
$env:PYTHONPATH = (Resolve-Path '.\apps\webapp\src').Path
& '.\apps\webapp\.venv\Scripts\python.exe' '.\scripts\coach3b_review_closure.py' --validate
& '.\apps\webapp\.venv\Scripts\python.exe' '.\scripts\coach3b_preview_parity.py' --verify
Remove-Item Env:PYTHONPATH
```

Erwartet:9 READY, GO_FOR_COACH_3B_APPLY_PENDING_SEPARATE_APPROVAL,
business_mutations=0/database_snapshot=NOT_READ/uuid_allocation=false; Public-
Parity status=PASS und gaps={}. Ein später geänderter öffentlicher Stand darf
die Gegenprobe fehlschlagen lassen; nicht automatisch Erwartungswerte ändern.

## COACH-3B Real Apply Vorbereitung 30.10

**EXECUTION STOP: kein bestehender Admin.** Fachlicher Review bleibt9 READY.
Manuel hat Ziel `competence_hub_staging` auf dem bekannten VPS, die neun geprüften
Coachdatensätze, erforderliche additive0007-0009 und verschlüsseltes Vorher-Backup
mit isolierter Restoreprobe ausdrücklich bestätigt. Anschließend ausdrücklich:
**„Es gibt noch keinen Admin; vor Import stoppen“**. Kein Konto/keine Rolle als
Import-Workaround anlegen; kein realer DB-Schreibzugriff erfolgte.

Der bestehende Vertrag verlangt eine aktive DB-bestätigte Admin-Identität:
Revision `created_by`, Approval `actor_id` und Object Evidence `recorded_by`
referenzieren unveränderlich `portal_users`. SSH-/DB-Rolle ist keine Portal-
Identität. Ein erfundener UUID-/MFA-Principal, synthetisches Ersatzkonto oder
temporäre Rolle mit anschließend verwaister Historie wäre kein zulässiger Ersatz.
Das erfordert einen separaten Admin-Onboarding-/Bootstrap-Gate, keine erneute
Freigabe der neun fachlich bereits geschlossenen Profile.

### Lokaler Kandidat Und Unveränderliches Manifest

- [Manifest/Binder](../../scripts/coach3b_real_manifest.py): exakter Reviewhash,
  Quellidentitäten, öffentliche Inhalte/Assethashes, logische Themen und getrennte
  Nachweise. Manipuliertes Businesspayload kann auch mit neu berechnetem Hash
  nicht freigegeben werden. Unbekannte historische Daten bleiben NULL.
- [Separater echter Operator-Kandidat](../../scripts/coach3b_real_apply.py):
  Default offline VALIDATE; ausdrückliche Modi preflight/dry-run/apply. Der
  bisherige synthetische Importpfad und seine Ziel-/Namespaceguards bleiben
  unverändert. Kein Import-HTTP-Endpoint und keine Runtime-Aktivierung.
- Tatsächliche acht Themen werden ausschließlich MATCH_ONLY anhand geprüfter
  Referenzen/Aliasse/Kategorien und vorhandener aktiver DB-UUIDs aufgelöst.
  Profil-Subjecthash erst aus normalisiertem Zielinhalt samt tatsächlichen
  Themen-Snapshots berechnen; logische Candidatehashes werden nicht übernommen.
- APPLY-Kandidat verlangt Ziel-/Schema-/Owner-/Quellbindung, bestehenden Admin,
  frisches exaktes Window-Proof-Artefakt mit Backup-/Restorebindung sowie den
  unveränderten DB-Dry-Run-Plan. Gemeinsame bestehende Domainwriter und eine
  Gesamttransaktion, keine neuen Accounts, Themen oder Kalenderzuordnungen.
- Der öffentliche APPLY-Einstieg ist zusätzlich **hart deaktiviert**, ohne
  Freischaltparameter: manuell verfasstes und korrekt gehashtes Proof-JSON kann
  keinen echten Lauf ermöglichen. Nur der private Transaktionskandidat wird im
  nachweislich eigenen synthetischen Container getestet. Der künftige tatsächliche
  Backup-/Restore-/Source-/Target-Prüfer ist noch nicht implementiert.
- MVCC-/Count-Vergleich ohne Authfeld-/Credential-Payloads schützt angrenzende
  Tabellen. Erste Anlage oder identischer Neun-Coach-Batch, keine stillen
  Revisionen/Metadata-Reparaturen. Parity/Counts prüfen vor Transaktionscommit;
  unsicherer Fehler bedeutet STOP, kein automatischer Wiederholungsversuch.

Tatsächliches, ignoriertes Phase-A-Artefakt:
`.tmp/coach3b-real-2026-10-30/manifest.json`, Quellenstand
`30d69d999401701f0d71d8fb49dbfe492004eac3`.
Datei-SHA-256:
`872b4df0610ae54ceec1688f323e4d99001befd87d7a3d2395a0001fc82c02fc`.
Das ist der Quellen-/Reviewstand, **kein gepushter neuer Runner-Release**.
Manifest enthält operative Nachweiszuordnungen und bleibt privat/ignoriert.
Counts stimmen mit dem abgeschlossenen Review überein;0 echte UUID-Zuteilungen
und0 DB-Mutationen. Keine Preise/geschützten Langtexte als öffentliche Daten.

### Betriebsgrenzen Vor Wiederaufnahme

Das eine echte Serverfenster wurde nicht eröffnet. Der vollständige echte
Window-Orchestrator/Proof-Erzeuger ist noch nicht implementiert oder abgenommen;
den erwarteten Proof niemals manuell als PASS-JSON erzeugen. Der geprüfte lokale
Adapter allein ist **nicht ausführungsbereit**. Nach Admin-Gate fehlen weiterhin
aktueller DB-/Themen-/Migrationsstand, sauber gepushter Runner, tatsächlicher
Backup-/Restore-Nachweis und nativer Admin-Smoke gegen das reale Ziel.

Private GPG-Schlüssel bleiben außerhalb des VPS. Restore lokal in isoliertem
PostgreSQL mit exaktem verschlüsseltem Dump, Baseline-/Migrations-/Countvergleich
und bestätigter Container-/Temporärdaten-/Klartextbereinigung. Historische
25.08-Restoreprobe ist kein aktueller Vorher-Backup-Nachweis. Der Tagesbackup-
Aufruf verweigert ein zweites Tagesziel und führt Retention aus; nicht löschen,
überschreiben oder still als unmittelbaren Pre-Import-Stand wiederverwenden.
Ein späterer eigener Pre-Import-Stand muss diese Grenzen explizit erfüllen.

30.10 tatsächlich rein lesend geprüft: SSH-Schlüssel/known-host-Verbindung zum
bekannten VPS, Hostname `ubuntu`, vier Dienste jeweils `active`, PG-Listener nur
`127.0.0.1:5432`. Nichtinteraktiver `sudo -n`-Metadatenversuch scheiterte mit
„a password is required“; keine DB-Abfrage ausgeführt, kein Passwort abgefragt.
Keine aktuellen DB-Counts, Backupdaten oder Restore-PASS daraus ableiten.

**Nicht durchgeführt:** reales Backup/Restore,0007-0009 auf VPS, DB-DRY-RUN,
echter APPLY/No-op, neue reale Public Projection, nativer Admin/API-Smoke und
CAL-1-Staging-Regressionslauf. Keine Websites/Backenddienste/Portalrollen/
Calendar-Mappings verändert. Kein Rollback nötig, weil keine realen DB-Writes.
Kein Commit/Push dieses lokalen Kandidaten; der Auftrag erlaubt nach realem
Erfolg Evidence-/Context-Updates, kein implizites Pushen unvollständiger Runner.

Einziger nächster empfohlener Block: **ADMIN OPERATOR READINESS**, mit separater
Freigabe für die benannte Identität/Bootstrap-Prozedur, aktuellem Auth/MFA- und
Recovery-Vertrag. DoD: genehmigter, tatsächlich nutzbarer Admin und nachvollzieh-
bare UUID-Bindung, ohne Coach-/Calendar-Onboarding. Danach den hier pausierten
Import samt vollständigem Ein-Fenster-Orchestrator erneut auf Ausführbarkeit
prüfen; kein jetzt ausgeführter Import und keine neue Website-Freigabe.

### Verifikation Des Lokalen Kandidaten

| Tatsächlich30.10 geprüft | Ergebnis / Grenze |
| --- | --- |
| Offline echtes eingefrorenes Manifest | PASS; exakter Reviewhash/alle acht Assetbytes, erwartete9er-Counts,0 UUIDs/DB-Writes |
| Neue reine Schutz-/Manifesttests |72 PASS: Ziel-/Scope-/Payload-/Themen-/Evidencebindung, unbekannte historische Daten, handgeschriebener Window-Proof kann APPLY nicht aktivieren |
| Neues eigenes PG16-Adapter-Gate |2 PASS; neun ausschließlich synthetische Coaches, fehlender Admin/Proof und stale Plan stoppen, Fehler im zweiten Record rollt Gesamtbatch zurück, identische Läufe2/3 erhalten alle Zeilenversionen/Counts und Projektionen9/3 |
| Bestehendes Target-Upgrade-/Import-Gate |30 PASS;0008->0009 erhält Altzeilen/xmin und alte Projektion, bestehende Rich-Import-/Revisions-/No-op-Verträge unverändert |
| Vollständige lokale Suite |812 PASS,22 erwartete opt-in Skips; darunter der separat tatsächlich ausgeführte neue PG-Test, kein Staginglauf |
| Weitere Checks | compileall, pip check, PowerShell-Parser, Dokumentlinks/Archivintegrität und diff-Prüfung |

[Lokaler Harness](../../scripts/run-coach3b-real-local.ps1) prüft freien55432,
benutzt nur einen exakt eigenen tmpfs-Container mit gecachtem Image (`--pull
never`) und markiert die DB mit einer zufälligen prozessinternen Ownership-Nonce.
Der Test bestätigt diesen Marker **vor jeder synthetischen Mutation**; der
gleiche Loopback-Port allein beweist kein lokales Testziel. Keine Wiederverwendung
eines VPS-Tunnels. Schema/Owner/Grants entsprechen dem echten Vertrag, ohne
UPDATE auf `roles` zu erlauben; Operator sperrt nur zulässige `portal_users`/
`user_roles`-Zeilen. Containerentfernung und Abwesenheit tatsächlich bestätigt.

Die synthetische Policy-/Window-Substitution bleibt ausschließlich im Test und
erteilt keine echte Freigabe. Kein echter Schlüssel, kein aktueller Backupdump,
keine lokale Kopie echter Registry-Daten und keine native Real-Admin-Abnahme.
Read-only Preflight darf bei null Admins nur STOP/NOT_COMPLETE melden, nicht eine
erfolgreiche Ausführungsbereitschaft. Drei Reviewbefunde (Proof-Vertrauen,
Role-Lock-Rechte, falsches Preflight-PASS) wurden entsprechend abgesichert.

## Incremental Source Recheck 02.11

The newly authorized20261030 folder is reconciled incrementally:1 unchanged known
concept,2 new inputs for an existing Coach,0 modified/unreadable files. Private
new details/rights/qualification/service-boundary questions remain an annex, not
new public copy. Exact nine-Coach manifest, existing counts and9 READY/0 reviews/
0 blockers stay unchanged.0 canonical loss;1 additional semantic service gap is
explicitly deferred, not silently mapped. [Current source/diff evidence and limits](source-ingestion-20261030-2026-11-02.md).
No real import, server, key or Website operation. The dated30.10 evidence below
remains intact and is not a claim to cover every new detailed source field.

## Backend Sprint Addendum 30.10: Neuer Aktueller Stand

Die vorstehende Phase A bleibt datierte Vorbereitung. Der spaetere Auftrag
genehmigt Manuel als genau einen realen Staging-Admin, admin only, mit einmal
gewaehltem privatem Login; keine Coach-/Internal-/Reviewer-/Contact-Rolle oder
Calendar-Zuordnung. Neue sichere Konfiguration vorbereiten und den gruenen
lokalen Vorbereitungsstand einschliesslich Phase A committen/pushen ist jetzt
ausdruecklich erlaubt. Die frueheren Aussagen "kein Bootstrap/kein Push" sind
damit fuer diesen begrenzten neuen Block ueberholt, nicht die Importguards.

[Elisabeths Quellenabgleich](elisabeth-source-reconciliation-2026-10-30.md) ist
vollstaendig:13 Seiten,3 Familien/12 Konzepte/21 Detailformate,9 referenzierende
Pakete,2 Erweiterungen und8 optionale Quellenkonflikte.17 vorhandene Titel
erhalten; neue Details bleiben im hashgebundenen privaten Anhang statt neuer
oeffentlicher Copy oder realer Daten. Vier echte neue Modellluecken sind
zurueckgestellt, kein stiller Field Loss im bestehenden Importumfang. Keine
weitere Migration. Der eingefrorene Kurzbatch bleibt **9 READY/0 REVIEW_REQUIRED/
0 BLOCKED**,0 Verlust, mit unveraenderten bisherigen Counts und Rechteumfaengen.
Die8 Detailkonflikte sind kein fachliches GO fuer diese Detailfelder.

[Aktueller Betriebsnachweis und Grenzen](../operations/staging-admin-bootstrap-2026-10-30.md):
dauerhafte DPAPI/GPG-Key-Custody, betriebliche Passwort-Pruefliste, eindeutiger
verschluesselter Vorher-Snapshot und exakter isolierter Restorevergleich vor
erstem echten Konto. Lokaler nativer Operator mit synthetischer PostgreSQL/MFA/
Edge und separate Restore-Orchestrierung tatsaechlich geprueft; letztere mit
bewusstem GPG-Testersatz, nicht echtem verschluesseltem VPS-Dump. Aktuelle echte
Backup-/Restore-/Admin-Gates bleiben NOT EXECUTED. Kein Passwort/Key wurde durch
den Agenten gelesen oder echter Zugang improvisiert.

Das private Adminfenster migriert keine Tabellen und importiert keine Coaches
oder Themen. Die echte APPLY-CLI bleibt hart deaktiviert. Anschliessend fehlen
weiterhin aktueller Themen-/Schema-/Dry-Run-Nachweis und ein gesondert abgenommener
vollstaendiger Import-Orchestrator. MATCH_ONLY darf bei leerem Themenbestand
nicht durch stilles Anlegen oder erfundene UUIDs umgangen werden.

Business-Milestone19.11.2026 ohne Kundendaten dokumentiert; Manuel ist ein
spaeterer standardisierter Post-Migrations-Onboardingfall, nicht Coach10 im
neuner Manifest. FIN-01/Kundenmodul und alle Website-/Backenddeployments bleiben
ausserhalb. Naechster Block ist ausschliesslich das vorbereitete private
Admin-/Backup-/Restorefenster aus geprueftem gepushtem Quellstand.
