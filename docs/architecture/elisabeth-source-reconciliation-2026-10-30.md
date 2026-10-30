# Elisabeth: Technischer Quellenabgleich 30.10

Status: lokale Quellenpruefung PASS, keine Import-/Publikationsfreigabe fuer neue
Detailinhalte. Dieser Git-Nachweis enthaelt keine neue Angebotscopy, Original-
Tabellen, Methodenablaeufe oder konkrete widerspruechliche Detailwerte.
Die ausfuehrliche Matrix und die Rueckfragen bleiben privat fuer die Abstimmung.

Kanonische Nachbarn: [Migrationsplan](coach3-existing-content-migration-plan-2026-10-23.md),
[Importvertrag](coach-import-contract-v0.1.md),
[Operatorvorbereitung](../operations/staging-admin-bootstrap-2026-10-30.md),
[aktiver Batch](../exec-plans/active/backend-sprint-2026-10-30.md).

## Bindung und Umfang

Nur die genehmigte Datei `Quellen/20261030/Konzept_Schwabauer.pdf` wurde fuer
diesen Abgleich gelesen. Alle13 Seiten textuell verarbeitet; Ansichten der
Seiten3,4,5,6,7,9,10,12 zusaetzlich visuell geprueft. Begrenztes unabhaengiges
Review von Text/Tabellen, alter Zuordnung, Kuratierung und Anhang ohne Befund.
Keine unabhaengige Wiederholung der visuellen Pruefung behaupten.

| Privater Eingang / Ergebnis | SHA-256 |
| --- | --- |
| PDF | `04805b6e6b96313e68f285d01c922d9342bd692ce4ec2cce68b9b124191f4620` |
| Kuratierung `.tmp/elisabeth-source-20261030/review.json` | `141320445920f0fd8f6f816cd6f1dca9f3744a0508996980a67f67cda77f6434` |
| Unveraendertes altes Importmanifest | `872b4df0610ae54ceec1688f323e4d99001befd87d7a3d2395a0001fc82c02fc` |
| Readiness-Anhang `.tmp/elisabeth-source-20261030/readiness-manifest.json` | `41566849a34db8179ee2a9ef2ebee17bbd050febffc9dfe70e1befa0af42c450` |
| Ausfuehrlicher privater Bericht `.tmp/elisabeth-source-20261030/detailed-reconciliation.md` | `2efaabeece23651b4ef2718dedbf07cab640338a5d0649cac2b7ff258c4b4c4a` |

Der CLI-Neulauf mit dem endgueltigen Evaluator erzeugt denselben Readiness-Hash.
Der Anhang bindet PDF/Kuratierung und den bisherigen Review getrennt, statt
den schon genehmigten Kurzpayload still zu ersetzen. Private Dateien und neue
Detailcopy bleiben ausserhalb von Git; Verarbeitung ist keine Publikation.

## Ergebnis Ohne Neue Angebotsveroeffentlichung

- 3 fachliche Familien,12 kanonische Konzepte,21 Formate in der privaten Matrix.
- 10 Vortrag-/9 Workshop-Formate,1 begleiteter Prozess,1 moderierte Analyse;
  keine falsche Workshop- oder Therapieklassifikation fuer Prozess/Analyse.
- 9 referenzierende Kombinationen,2 Erweiterungen,6 Prozessphasen und6
  Anpassungsmerkmale; keine duplizierten Fachthemen oder Firmendaten angelegt.
- 8 interne Quellenkonflikte bleiben optional fuer den unveraenderten Kurzimport:
  `SOURCE_CONFLICT / REVIEW_REQUIRED_SOURCE`, nicht aufgeloest/freigegeben.
  Konkrete Titel-/Dauer-/Zielgruppenrueckfragen stehen nur in der privaten Matrix
  und `.tmp/backend-sprint-20261030/Janay-Angebotsrueckfragen.txt`.
- 17 Alttitel erhalten:7 Format-,2 Konzept-,2 Familienzuordnungen,4 optionale
  unbelegte Zuordnungen,1 allgemeiner Bestand ausserhalb der neuen Quelle und
  1 weiterhin separate inaktive Therapiegrenze. Keine erzwungene Neuzuordnung.

Die bestehende fachliche/gesundheitliche Trennung und das Verbot erfundener
Qualifikationen, Rechtsberatung oder Compliance-Garantien bleiben erhalten.
Zielgruppen sind Metadaten, keine Themen oder operative Rollen.

## Modellgrenze und Import

Der aktuelle Typvertrag bildet die neue Detailstruktur nicht vollstaendig ab:
Paket-Komponentenreferenzen, geordnete Projektphasen, strukturierte Anpassungs-
faehigkeiten sowie typisierte Dauerintervalle/-grenzen fehlen. Der Wortlaut einer
Dauer kann bereits verlustfrei erhalten bleiben, ist aber kein typisiertes
Intervall. Alle vier neuen Strukturfelder sind explizit `deferred_not_imported`.
Keine zusaetzliche Migration oder scheinbar vollstaendige Detailuebernahme.

Der eingefrorene9-Coach-Kurzimport und seine oeffentliche Projektion bleiben
unveraendert:30 Formate/29 aktiv,3 bisherige Familien und5 Varianten/Zusatzformate.
READY9, REVIEW_REQUIRED0, BLOCKED0 fuer genau diesen alten Kurzumfang;
0 kanonischer Verlust und0 neu importierte Detailfelder. Die8 optionalen
Detailkonflikte sind kein globaler Importblocker und kein GO fuer die Detailwerte.
Bestehende9 Preview-/3 Production-Scope-Nachweise bleiben getrennt;6 unbekannte
Production-Scopes erhalten keine Freigabe durch den neuen Quellenzugriff.

16 reine Evaluatorregressionen plus tatsaechlicher lokaler CLI-/Hashvergleich.
Kein DB-Zugriff, UUID, Real-Import oder Website-Deployment in diesem Abgleich.
Real APPLY bleibt deaktiviert; naechster Block ist das gesondert vorbereitete
private Admin-/Backup-/Restorefenster, nicht die Veroeffentlichung dieses Konzepts.
