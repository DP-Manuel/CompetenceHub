# COACH-3: Bestandsinventur Und Migrationsplan

Stand:29.10.2026. **Inventur, synthetischer COACH-3A-Nachweis und COACH-3B-
Vorbereitung; kein realer Import.** Die Bestandsinventur wurde nach lokaler COACH-2-
Abnahme aus kanonischen, bereits öffentlichen Projektinhalten ermittelt.
`Quellen/` wurde in diesem Block nicht geöffnet. Keine echten Personen-UUIDs,
DB-Einträge, Accounts, Kalenderrollen oder Veröffentlichungen erzeugt.
Die spätere COACH-3A-Freigabe erlaubt ausschließlich lokale Migration0008 und
synthetische Testeinträge in einer anschließend vollständig entfernten Datenbank.

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

## Zusammenhängendes Künftiges COACH-3B-Runbook

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

## Ein Empfohlener Nächster Block

**Verlustfreien Zielvertrag lokal mit synthetischen Daten umsetzen und abnehmen.**
Zweck: die hier belegten technischen Field-Loss-Blocker vor Echtdaten schließen.
Inputs: bestätigte29.10-Entscheidungen, Reviewmatrix und minimaler Modellvorschlag.
Deliverables: kompatible Domain-/DB-/Editor-/Import-/Projektionsfelder und ein
gesamter synthetischer Parity-/Evidence-/Familientest. Done: kein stiller Verlust,
öffentliche/interne Trennung und korrekte Boundaries; noch kein realer Import,
keine Servermigration oder Veröffentlichung. Ersatzquellen und konkrete
konkrete Nachweisbindungen können parallel vorbereitet werden. Für COACH-3B APPLY
bleibt es bis dahin bei **NO-GO**, nicht nur „Ausführung noch nicht angeklickt“.
