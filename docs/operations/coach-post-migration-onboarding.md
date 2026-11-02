# Coach-Onboarding Nach Der Bestandsmigration

Stand: 02.11.2026. Kanonischer Bedienablauf fuer autorisierte Admins **nach**
abgenommener real9-Migration, keine Aussage ueber deren Vollzug. Aktuell bleiben
reale Key-/Backup-/Restore-/Admin- und Importnachweise offen. Dieses Dokument
erteilt keine Daten-, Quellen-, Runtime- oder Releasefreigabe und enthaelt keine
jetzt auszufuehrenden Befehle.

## Einstieg Und Voraussetzungen

Manuels spaeteres Coach10-Profil durchlaeuft ausschliesslich den normalen,
autorisierten Admin-Workflow wie jedes weitere Profil. Kein zehnter Datensatz
im eingefrorenen Neuner-Manifest, kein Sonderimport, keine persoenlichen
Vorbelegungen und keine aus seinem Adminstatus abgeleiteten Qualifikationen,
Coachrechte oder Calendar-Zuordnungen.

- Vorherige Betriebsfenster nach [Stick-Checkliste](staging-stick-resume-checklist.md)
  und [Admin-Runbook](staging-admin-bootstrap-2026-10-30.md) tatsaechlich abschliessen;
  den real9-Import separat freigeben, ausfuehren und abnehmen. Die unveraenderte
  [Importplanung](../architecture/coach3-existing-content-migration-plan-2026-10-23.md#backend-sprint-addendum-3010-neuer-aktueller-stand)
  besitzt dessen Nachweise. Kein Importer-Rerun als normales Onboarding.
- Fuer das konkrete neue Profil muessen Identitaet, erlaubter Datenumfang und
  Quellenzugriff separat autorisiert sein. Nur konkret erlaubte Quellen lesen;
  eine Publikationsfreigabe erlaubt keinen Zugriff auf ein Quellenverzeichnis.
- Benannter Admin mit persoenlichem Login, MFA, gueltiger Session und CSRF;
  ausdruecklich freigegebene Registry-Aktivierung und passendes Schema einschliesslich
  0009. Ein Bootstrap-Admin allein aktiviert die Registry nicht. Bei
  `registry_unavailable` STOP, kein direkter SQL-/Import-/Rollen-Bypass.
- Zielumgebung und aktuelle Betriebs-/Recovery-Freigabe pruefen. Die drei
  [Umgebungen](../architecture/environment-policy.md) bleiben getrennt.
  Ein Staging-Profil ist weder produktiver Portalbetrieb noch Website-Publikation.

## Was Die Vorhandene Oberflaeche Kann

Massgeblich sind [Registry-Vertrag](../architecture/coach-registry-contract-v0.1.md),
[Admin-UI-Vertrag](../architecture/coach-admin-ui-contract-v0.1.md#coach-3c-erweiterung)
und [Importvertrag](../architecture/coach-import-contract-v0.1.md).
Die folgende Zuordnung ist gegen den lokalen
[Editor](../../apps/webapp/src/competence_hub_api/portal_ui/coach-management.js)
und die [typisierte Admin-API](../../apps/webapp/src/competence_hub_api/web/coach_registry.py)
geprueft, nicht gegen eine bereitgestellte Serveroberflaeche.

| Aufgabe | Vorhanden / Voraussetzung |
| --- | --- |
| Anlage | Coaches -> Anlage nur mit Anzeigename; zufaellige stabile UUID, Entwurf, kein Konto. Danach Profilrevision anlegen. Kein Onboarding-Wizard. |
| Profil | Anzeigename, akademischer Zusatz, Kurzbeschreibung, Profiltext, beruflicher Hintergrund, Zielgruppen, ausdruecklicher ASCII-Profilpfad. Nicht aus Namensaenderung ableiten. |
| Themen / Kompetenzen | Kanonische Themen auswaehlen; M:N-Kategorien nur lesen. Kompetenzen als eigene Label-Liste. Keine Themenneuanlage oder Kategorieaenderung. |
| Erweiterte Felder | Im Entwurf "Erweiterte Profilfelder aktivieren" (`target_version=1`); Rollen/Darstellung/Profilabgrenzungen im Profil, Qualifikationen und Angebotsfamilien in eigenen Bereichen; Formatdetails unter Angebote. Kein Roh-JSON-Editor. |
| Schluessel | UI erzeugt stabile Itemkeys und zeigt sie schreibgeschuetzt. Ein zwingend vorgegebener externer Itemkey erfordert vorab einen geprueften typisierten API-Arbeitsschritt, keinen Titeltrick oder SQL-Eingriff. |
| Portraet | Referenz, SHA-256, Alternativtext, aktiv und Umgebungsscope; kein Upload, Bildbearbeitung oder automatischer Byte-/Rechtecheck. Freigegebene Assetbereitstellung ist Voraussetzung. Ohne Portraet ist ein Profil moeglich. |
| Nachweise | Fuer eingereichte Rich-Revision: Serverobjekt und Hash auswaehlen; Art, Umgebung, Scope, Status, Referenz, bekannte freigebende Person, historischer Tag und interne Notiz erfassen. |
| Zeitpraezision | UI erfasst `approved_on` (Tag), zeigt vorhandenes `approved_at` an, bietet aber keine Eingabe dafuer. Ein belegter genauer Zeitpunkt mit Zeitzone braucht den typisierten API-Weg vor der Freigabe; niemals auf Tag verkuerzen oder Mitternacht erfinden. |
| Freigaben / Lifecycle | Revisionsfreigaben, Aktivierung, getrennte Preview-/Production-Publikation, Ruecknahme, Pause/Offboarding und Historie. Nur DB-Status, kein Website-Build. |

Fehlt ein erforderliches Feld in der tatsaechlich verfuegbaren Version: STOP und
Voraussetzung klaeren. Der autorisierte Admin-API-Weg bleibt derselbe Workflow
mit MFA, Origin/CSRF, `expected_version`, strikt typisierten Vollsnapshots und
32-KiB-Grenze. Keine beliebige JSON-Ablage und keine direkte Uebergabe des
Arbeitsblatts. Nicht bearbeitete strukturierte Felder ausdruecklich erhalten;
ein Rich-Profil nicht auf Version0 zuruecksetzen. Die UI ist kein Ersatz fuer
Quellen-, Datenschutz- oder Rechtspruefung.

## Praktischer Ablauf

1. **Review vorbereiten.** Das leere
   [JSON-Arbeitsblatt](../content/coach-onboarding-template.json) dient nur der
   strukturierten Besprechung, ist **kein direkt importierbarer Payload**.
   Listen sind leer; `item_templates` beschreibt wiederholbare Zeilenformen,
   nicht bereits erfasste Eintraege. `null` bedeutet offen, `unknown` ist keine
   Freigabe, `false` keine Zustimmung. Nur benoetigte Formen uebernehmen;
   Kategorien mit bestehenden kanonischen Themen abgleichen. Ausgefuellte
   Arbeitsblaetter mit Personendaten/Nachweisreferenzen gehoeren in die genehmigte
   private Ablage, nicht in diese universelle Vorlage oder externe Notizen.
2. **Identitaet klaeren und Entwurf anlegen.** Autorisiert auf vorhandenen Coach
   pruefen; gleiche Namen sind kein Identitaetsbeweis. Bei bestehendem Profil
   dessen UUID behalten, bei ungeklaerter Zuordnung stoppen. Nur fuer wirklich
   neue Identitaet einmal anlegen. Nach Antwortverlust keinen zweiten Auftrag
   erzeugen; den vorhandenen Erstellungsauftrag aufklaeren. UUID/Revision nur
   intern nachhalten, nie aus Name, Mail oder Pfad konstruieren. Neue Revision
   anlegen, Rich-Felder aktivieren und Pflichttexte vervollstaendigen.
3. **Typisiert erfassen und speichern.** Nach der Feldpruefung unten alle
   benoetigten Inhalte einschliesslich Assets speichern und frisch laden.
   Keine geschuetzten Originale, Privatadressen, E-Mails, Vertraege, Zertifikat-
   Dateien, Preise, Kunden- oder Rechnungsdaten aufnehmen. Bei Konflikt409
   Eingaben pruefen und bewusst aktuellen Stand laden; kein blindes Wiederholen
   oder Ueberschreiben. Unklare Quelle/Behauptung bleibt offen und unveroeffentlicht.
4. **Einreichen und Nachweise binden.** Erst gespeicherten Vollstand pruefen,
   dann "Zur Pruefung einreichen". Submission friert Text, Themenname/-kategorien
   und Assethashes ein. Auf dieser konkreten Revision Objekt-Evidence und
   Revisionsfreigaben getrennt dokumentieren (siehe unten). Aenderungen nach
   Submission brauchen eine neue Revision mit neuen Nachweisen/Freigaben.
5. **Gezielt aktivieren und publizieren.** Erst nach frischem `content_review`
   und `person_consent` aktivieren; je gewuenschter Umgebung zusaetzlich deren
   Freigabe und saemtliche erforderliche Objekt-Evidence pruefen, dann genau
   diese Revision publizieren. Unbekannte Production-Rechte bleiben ausgeschlossen,
   auch bei freigegebenem Preview. Keine Freigabe aus vorhandener Webseite,
   Dateiname oder technischem Status ableiten. Ein eigener Website-Release-Gate
   muss danach Projektion, Assets, Darstellung und erlaubten Zielumfang pruefen;
   die [COACH-4-Pipeline](../architecture/coach-public-projection-contract-v0.1.md)
   ist nur als lokaler Parallelvergleich vorbereitet, kein aktivierter Liveexport
   oder kanonischer Websiteeingang. Kein Release durch
   diese Adminaktion.
6. **Abschluss kontrollieren.** UUID, Revisionsnummer, Lifecycle und beide
   Publikationsstaende im Admin neu laden; nur freigegebene oeffentliche Felder
   in der zielbezogenen Projektion erwarten. Keine UUIDs, Nachweisreferenzen,
   Pruefnotizen, Quellenpfade oder internen Titel exportieren. Nachweise intern
   revisions-/umgebungsbezogen ablegen; Calendar, Accounts und ausgelieferte
   Websitebytes bleiben unveraendert. Offene Rechte oder Felder als STOP fuer
   den betroffenen Publikationsumfang vermerken, nicht als implizite Zustimmung.

## Feldpruefung Vor Submission

| Bereich | Fachliche Pruefung |
| --- | --- |
| Rollen | `public_roles`: stabile Keys, Code, oeffentliches Label und eindeutige Reihenfolge. Redaktionelle Rollen sind keine Portalberechtigungen, Qualifikationen oder Kompetenznachweise. |
| Qualifikationen | Eigener stabiler Key je Coach; kanonischer interner Titel, explizites oeffentliches Label, Aussteller/Art, Reihenfolge, `public`, `active`/`historical`. `verification_state`, Referenz und Notiz bleiben separat intern. Keine Qualifikation aus Erfahrung/Rolle ableiten. Oeffentlich aktive Qualifikation braucht eigenes Public-Evidence; interne Verifikation genuegt nicht. |
| Themen / Kompetenzen | `topic_ids` nur bestaetigte kanonische UUIDs mit gelesenen Kategorien; keine erfundenen Zuordnungen, kein gespeichertes "Alle". Kompetenzen, Zielgruppen, Rollen und Qualifikationen getrennt erfassen. Leerer/abweichender Themenkatalog ist ein eigener Prerequisite-Gate. |
| Familien / Formate | Familie mit stabilem Key, Titel, kurzer Beschreibung, Reihenfolge, aktiv; Formate als `offerings` mit eigenem Key, passendem `family_key` oder bewusst ohne Familie. Typen: lecture/workshop/coaching/individual/other. Keine doppelte Darstellung gruppierter Formate als Standalone; inaktive Familien/Formate werden nicht projiziert. |
| Varianten / Details | Varianten, Optionen und Add-ons (`variant`/`option`/`add_on`) unter Familie oder Format, nicht als duplizierte Hauptangebote. Zielgruppen/-fokus, Leistungsbereiche, Dauer, Durchfuehrung und kurze Programmmodule ausdruecklich pruefen. Schluessel bei Umbenennung erhalten; inaktive Eintraege historisch erhalten. |
| Dauer / Durchfuehrung | Vollstaendiges gleichentags Uhrzeitfenster oder Minuten bzw. Wochen mit Terminen/Termindauer. Unbestimmtes "Live" bleibt `live_unspecified`, nicht geratenes Online/Praesenz. `bookable` ist kein Calendar-Angebot und erteilt keine Berechtigung. |
| Abgrenzungen | Profil, Familie und Format: ausdruecklicher Text und ausgeschlossene Leistungscodes. Konfliktarbeit ist nicht automatisch Mediation/Supervision; Gesundheitsfoerderung keine medizinische Behandlung. Psychotherapie ist ein eigener Bereich, nie Coachingformat und bleibt nicht buchbar. Geschuetzte Quellreferenz nur opak, keine Originaltexte. |
| Darstellung | Teaser, Labels, Sprachen, Abschnitte, Themenkarten, Zitat, Initialen, Bilddimensionen und getrennte HTTPS-Linkziele nur soweit belegt und freigegeben; kein HTML oder Ersatz fuer fehlende strukturierte Qualifikationen. |
| Portraet | Hoechstens ein Asset: explizite `images/coaches/...`-Referenz, SHA-256 der tatsaechlichen freigegebenen Bytes, Alttext, aktiv, erlaubte Scopes. Austausch braucht neue versionierte Referenz/Hash und neue Revision/Freigaben, keine geaenderten Bytes unter historischer Referenz. Alte publizierte Assets erhalten. |

## Evidence Und Freigaben

Revisionsfreigaben `content_review`, `person_consent`, `preview`, `production`
haben jeweils einen echten Nachweisbezug. Der technische Erfassungsakteur und
Zeitpunkt sind keine erfundene historische Unterschrift. Einwilligung wird
dokumentiert, nicht durch einen Button erzeugt.

Rich-Objektnachweise binden Coach, Revision, stabilen Objektschluessel,
**serverberechneten** `subject_hash`, Art, Umgebung, Scope und Entscheidung.
Format heisst im API-Subject `offering`; Profil und Portraet haben ihre eigenen
Subjects. Der Portraet-Subjecthash umfasst das typisierte Assetobjekt und ist
nicht mit dem SHA-256 der Bildbytes gleichzusetzen. Keine Kandidatenhashes aus
einem Arbeitsblatt als Runtime-Bindung uebernehmen.

Pro Zielumgebung erforderlich: Profilinhalt und Profil-Publikation, aktives
Portraet sofern vorhanden, oeffentliche aktive Qualifikationen sowie sichtbare
Familien und Formate. Die Serverpruefung entscheidet die genaue Objektmenge.
`public_content`, `internal_verification` (nur Qualifikation) und
`protected_source_content` bleiben getrennt. Freigabe eines Originals erlaubt
nicht die Kurzfassung und umgekehrt. `unknown`/`rejected` erfuellen kein Gate;
Preview-Nachweise erfuellen niemals Production.

Referenzen sind opak, keine Quellenansicht. Historische Person/Tag/Zeit bleiben
bei Unkenntnis `null`; nur belegte Genauigkeit erfassen, Tag und Zeitpunkt nicht
gleichzeitig, keine Zukunftsdaten. Objekt-Evidence ist append-only; eine neue
passende Entscheidung ergaenzt Historie. Ablehnung erforderlicher Zustimmung
zieht die betroffene Umgebung zurueck. Neue Revisionen erben keine Evidence
oder Freigaben; alte Belege bleiben fuer ihre alte Revision erhalten.

## Pause, Offboarding Und Rueckkehr

Publikation zuruecknehmen, Lifecycle ueber die angebotenen Adminaktionen auf
paused/inactive/archived setzen; keine Identitaet oder Historie loeschen. Laufende
oder kuenftige Calendar-Angebote sperren Pause/Offboarding: zuerst separat im
bestehenden CAL-1-Prozess abstimmen/zuruecknehmen, niemals historische Termine
loeschen. Registry-Onboarding vergibt weder `coach_topics`-Rechte, Portalrolle,
Account noch den separaten Calendar-Profilpfad.

Rueckkehr von inactive: **gleiche UUID**, neue Revision oberhalb der Sperrgrenze,
frische Inhaltspruefung, Einwilligung, Objekt-Evidence und Umgebungsfreigaben,
dann active und bewusst publizieren. Bei archived zuerst zulaessig nach inactive.
Pause schliesst offene Entwuerfe als abandoned und zieht beide Umgebungen zurueck;
keine automatische Wiederveroeffentlichung. Auch nach Ruecknahme nur einer
Umgebung erfordert erneute Publikation dort eine neuere freigegebene Revision.

Eine Ruecknahme entfernt das Profil erst aus dem **naechsten** statischen
Artefakt. Bereits ausgelieferte Preview-/Production-Bytes verschwinden erst nach
separat freigegebenem Rebuild und Deployment. Accounts und Calendar bleiben
eigene Freigabe-/Betriebsprozesse; keine Zusage sofortiger Remote-Loeschung.

## Nachweis Und Naechster Block

Dieser Slice liefert nur Ablauf, leere Vorlage und lokale Strukturtests, keine
reale Bedienabnahme. Wiederverwendbares Workflow-Learning: kein neues ueber die
bestehenden Vertragsgrenzen hinaus; die UI-/API-Zuordnung ist hier festgehalten.

Empfohlener naechster Block bleibt erst nach Manuels manuellem Signal die
[geschuetzte Wiederaufnahme](staging-stick-resume-checklist.md), nicht Coach10.
Zweck: Betriebsgrundlage herstellen. Inputs: geeigneter Arbeitsplatz/Stick,
bestehende Keys, gepruefter freigegebener Quellstand und private Operatorinputs.
Deliverables/DoD: echte Custody, aktueller exakter Backup-/Restorebeleg und genau
ein admin-only Konto mit MFA/Recovery/RBAC/Bereinigung; danach Import separat.
Dieser Dokumentslice: kein Commit/Push, Deployment, Datenimport oder Serverzugriff.
