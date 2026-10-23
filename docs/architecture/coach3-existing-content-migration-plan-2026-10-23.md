# COACH-3: Bestandsinventur Und Migrationsplan

Stand:23.10.2026. **Inventur plus abgeschlossener synthetischer COACH-3A-Nachweis;
kein realer Import.** Die Bestandsinventur wurde nach lokaler COACH-2-
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

## Veröffentlichungsevidenz

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

## Verbindliche Entscheidungsmatrix Vor COACH-3B

| Bereich | Bereits technisch entschieden | Noch fachlich zu bestätigen |
| --- | --- | --- |
| Qualifikationen | Getrennte typisierte Eingabe; niemals Kompetenz/operative Rolle inferieren. Öffentlich wörtlich nur nach explizitem Hintergrund-Mapping; intern aktuell nicht unterstützt | Für reale Listen: vollständige öffentliche Darstellung als eigener Hintergrundabschnitt oder eigener strukturierter Feld-/Renderingvertrag? Welche Angaben bleiben intern? |
| Rollenbezeichnungen / Darstellung | Eigener Source-Typ; ungeprüfte Zuordnung stoppt. Keine automatische Zerlegung zusammengesetzter Rollen | Reale Rollen/previewRole und Fokus sowie Zitat, Sprachen, Formatgruppen und Advisory-Link verlustfrei und in vorgesehenen Abschnitten darstellen; kein pauschaler Freitextdump |
| Therapie-/Coachinggrenze | Unmapped blockiert; nur ausdrücklich freigegebener Wortlaut, synthetisches Beispiel nie buchbar | Exakte öffentliche Einordnung insbesondere Elisabeths „Psychotherapie (HeilprG)“ und der17 Angebotsgruppen; nicht still als aktives Coaching übernehmen |
| Freigabeevidence | Revision/Coach/Art/Umgebung/Quelle getrennt; unknown bleibt NULL, aktuelle Attestation separat, keine Vererbung | Welche vorhandenen konkreten Nachweise decken Inhalt, Person/Porträt und jeweilige Umgebung ab? Prüfer und bekannte Zeitpunkte/Umfang explizit zuordnen |
| Porträt fehlt | Zulässig, kein Ersatzbild erzwingen; keine neue Entscheidung erforderlich | Keine |
| Fehlendes Angebot/Item | Gesamter Batch stoppt; keine automatische Löschung. Explizit active:false ist unterstützt | Nur bei einem konkreten späteren Konflikt Quelle vervollständigen oder Deaktivierung freigeben |
| Identität/Themen/Assets | Keine Namenszuordnung, kein Legacy-Adopt, keine unfreigegebenen UUID-Mappings oder Assetbytes | Eigene reale Mapping-/Ausführungsfreigabe bleibt vor jedem COACH-3B-Schreibschritt erforderlich |

## Ein Empfohlener Nächster Block

**COACH-3B-Vorbereitung: reale Feld-/Rendering- und Nachweismatrix abstimmen.**
Zweck: verbleibende fachliche Informationsverluste vor Echtdatenübernahme klären.
Inputs: diese Inventur, der Importvertrag, kanonische öffentliche Profile und
Manuels Entscheidungen zu Qualifikationen, Rollen/Darstellung, Therapiegrenze
und konkreter Freigabeevidence. Deliverables: bestätigte Zuordnungs-/Verlustmatrix
und begrenzter Ausführungsplan. Done: alle fachlichen Konflikte entschieden,
Identitäts-/Themen-/Asset-/Umgebungsumfang ausdrücklich dokumentiert; weiterhin
kein realer Import, keine Servermigration oder Veröffentlichung ohne eigenes Gate.
