# COACH-3: Bestandsinventur Und Migrationsplan

Stand:23.10.2026. **Nur Analyse und Plan, kein Import.** Nach lokaler COACH-2-
Abnahme aus kanonischen, bereits öffentlichen Projektinhalten ermittelt.
`Quellen/` wurde in diesem Block nicht geöffnet. Keine echten Personen-UUIDs,
DB-Einträge, Accounts, Kalenderrollen, Migrationen oder Veröffentlichungen erzeugt.

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
   NFKC/Casefold/Leerzeichen-/Bindestrichnormalisierung nur zur Kollisionswarnung;
   keine automatische semantische Zusammenlegung. Neue Themen benötigen einen
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

Die statische Inventur selbst ist bereits deterministisch; das ist **kein**
Nachweis eines implementierten idempotenten DB-Importers. Ledger, Importer und
verlustfreies Rendering sind noch nicht gebaut. Keine DB- oder Websiteänderung
folgt aus dieser Analyse.

## Ein Empfohlener Nächster Block

**COACH-3A: Verlustfreier Importvertrag und synthetischer Dry-Run.**
Zweck: die offenen Inhalts-/Identitätsfragen vor einem echten Import auflösen.
Inputs: diese Inventur, COACH-1/2, bestätigte Feld-/Rendering- und Therapiegrenzen
sowie separate Slice-Freigabe. Deliverables: verbindliche Abbildung, typisierte
Validierung, getestetes Idempotenzledger/-verhalten und lokale synthetische
Projektion. Done: zwei Wiederholungen ohne Duplikate oder neue Revisionen,
Konflikt-/Asset-/Datenschutztests, vollständiger Verlustbericht, keine echten
DB-Records und keine Änderung von Pages/IONOS/VPS.
