# ANALYTICS-01: Besucher- und Nutzungsanalyse

Stand: 21.10.2026. Status: Discovery und Architekturvorschlag, keine Implementierungs- oder Aktivierungsfreigabe.
Auftrag: Manuels Post-Messe Product Addendum; [Produktentscheidungen](post-messe-product-2026-10-21.md).
Entscheidungsrecord: [PRIV-ANALYTICS-01](../decisions/PRIV-ANALYTICS-01.md).

## Ergebnis Und Empfehlung

Fuer Level 1 empfehle ich eine kleine, eigene Aggregation im vorhandenen FastAPI/PostgreSQL-Stack.
Dies ist eine begruendete Architektur-Empfehlung, keine bereits getroffene Toolentscheidung.
Sie passt zum strengeren Projektziel ohne Besucherkennungen und vermeidet einen zweiten Datenbank-/Runtime-Stack.
Der Preis ist eigene Entwicklung, Sicherheitspruefung, Wartung und bewusst weniger Kennzahlen.
Falls die benoetigten Kennzahlen spaeter echte Sessions voraussetzen, muss zuerst das Privacy-/Produkt-Gate neu entschieden werden.

Cookielos bedeutet technisch nicht automatisch kennungslos: Matomo dokumentiert einen kurzlebigen, attributbasierten config_id; Plausible beschreibt taegliche, aus IP/User-Agent abgeleitete Kennungen.
Die Anbieter verwenden teils engere Fingerprinting-Begriffe. Fuer dieses Projekt ist die entscheidende technische Grenze: keine solche Besucher-Verknuepfung in Level 1.
[Matomo config_id](https://matomo.org/faq/general/how-is-the-visitor-config_id-processed/), [Plausible Datenverarbeitung](https://plausible.io/data-policy).

## Reale Optionen

| Kriterium | A: eigene Aggregation | B: Matomo On-Premise, minimiert | C: Plausible Community Edition |
| --- | --- | --- | --- |
| Datenschutz / Standardumfang | Nur explizit zugelassene Zaehler; keine Besucherkennung | Viel konfigurierbar; Standardumfang muss deutlich reduziert werden | Schlanker Produktumfang, aber Kennungen fuer Besucher/Sessionstatistik |
| Cookies | Fuer oeffentliche Messung nicht vorgesehen | Standard-Tracker verwendet Cookies; abschaltbar | Laut Datenpolicy keine Tracking-Cookies |
| Browser Storage | Kein Local-/SessionStorage, keine Service-Worker-Persistenz | Exakte Tracker-/Plugin-Konfiguration im POC pruefen | Laut Policy kein LocalStorage; exakte CE-Version pruefen |
| Fingerprint-/ID-Grenze | Keine IP-/UA-Hashes fuer Besucher, keine Session-ID | config_id bleibt ein eigener Pruefpunkt; disableCookies allein genuegt nicht | Taegliche IP-/UA-basierte Kennung erfuellt die strengere Projektgrenze nicht |
| IP-Verarbeitung | Transport/Sicherheitszweck kurzzeitig; nicht in Statistik speichern | Anonymisierung konfigurierbar; Hash-/Logpfad gesondert pruefen | Policy nennt transiente Verarbeitung; keine gespeicherte Roh-IP |
| Infrastruktur / Datenabfluss | D+P-kontrollierter VPS; vorhandenes FastAPI/PostgreSQL erweitern | Zusaetzliche PHP- und MySQL/MariaDB-Installation | Docker/Compose, Anwendung, PostgreSQL und ClickHouse |
| Ressourcen | Vor POC messen; keine neue Kapazitaetszusage | Zusaetzliche Datenbank und Archivierungsjobs; Kapazitaet pruefen | CE-Anleitung empfiehlt mindestens 2 GB RAM; keine Freigabe fuer den belegten VPS |
| Pageviews / Clicks | Explizite Pageview-/CTA-/Coach-/Themen-/Filter-/Kontakt-/External-IDs | Tracking API bietet Seitenaufrufe und Events | Produkt bietet Pageviews und Custom Events; CE-Verfuegbarkeit/version pruefen |
| Visits / Ein-/Ausstieg | Keine verlaesslichen Sessions/Unique Visitors | Besuchsstatistik nutzt Verknuepfung; nicht ungeprueft uebernehmen | Taegliche Kennungen/Sessionaufzeichnung fuer solche Auswertungen |
| Verweildauer | Im MVP nicht als verlaessliche Durchschnittskennzahl | Heartbeat vorhanden, zusaetzliche Verarbeitung | Engagement-Metriken in Produktpolicy; Cloud/CE nicht gleichsetzen |
| Herkunft / Geraete | Nur spaeter freigegebene grobe Gruppen | Standardfelder stark minimieren | Standarddimensionen ueber Projektminimum hinaus; konfigurieren/pruefen |
| API / Portal | Bestehende serverseitige Admin-Autorisierung; eigene Aggregat-API | Reporting API vorhanden; Token nur serverseitig | Cloud-Stats-API belegt keine CE-Paritaet; CE-POC vor Integrationszusage |
| Retention / Loeschung | Explizite Tagesaggregate und Loeschjob; kein Rohdatenarchiv | Roh-/Reportbestand, Loeschjobs und Backups konfigurieren/pruefen | ClickHouse-/Postgres-Aufbewahrung und Loeschbarkeit im POC nachweisen |
| Backup / Restore | Aggregattabellen separat klassifizieren; vorhandene verschluesselte Restorekette erweitern | Zusaetzlichen DB-/Konfigurationsbestand sichern und restoren | Beide Datenbanken und Konfiguration konsistent sichern/restoren |
| Export | Nur erlaubte Aggregate, Admin, begrenzter Zeitraum/Zeilen; CSV-Formelrisiko beachten | Reporting/Export verfuegbar; minimierter Datensatz und Rechte pruefen | CE-Funktionen/Retention/Export nicht aus Cloud-Marketing ableiten |
| Kosten / Wartung | Keine zusaetzliche Analyticslizenz, aber eigene Entwicklungs-/Betriebskosten | Kostenloser Core, moegliche kostenpflichtige Plugins; weiterer Stack | Kostenlos selbst hostbar, aber eigener Betrieb; AGPL-Pflichten pruefen |
| Sicherheit | Eigene oeffentliche Ingestion braucht robuste Begrenzung; kleines Schema | Groessere konfigurierbare Angriffs-/Updateflaeche | Zusaetzliche Dienste/Ports/Updates; keine ungeprueften Compose-Defaults uebernehmen |
| Eignung Level 1 | Bevorzugt unter begrenztem Scope und Review | Reserve, falls ein konkreter POC die strengere Kennungsgrenze belegt | Standardansatz wegen Kennungskonzept ausgeschlossen; kein stiller Fork |

PHP/MySQL-Anforderungen und Matomos GPLv3-or-later-Core sind primaer dokumentiert.
Matomo bietet Cookie-/Browserfeature-Schalter sowie Tracking-/Reporting-APIs; das beweist keine fertige kennungslose Konfiguration.
[Anforderungen](https://matomo.org/faq/on-premise/matomo-requirements/), [Lizenz](https://matomo.org/free-software/), [Tracker](https://developer.matomo.org/guides/tracking-javascript), [Reporting](https://developer.matomo.org/api-reference/reporting-api), [Cookies](https://matomo.org/faq/how-to/how-do-i-enforce-tracking-without-cookies/).

Plausible CE hat einen eigenen Release-/Betriebsumfang. Die Compose-Anleitung und Vendor-Seite belegen Self-Hosting und AGPL; die MIT-Lizenz des Compose-Beispielrepos ist nicht die Anwendungslizenz.
[CE-Anleitung](https://github.com/plausible/community-edition), [Compose](https://github.com/plausible/community-edition/blob/v3.2.1/compose.yml), [Self-Hosting](https://plausible.io/self-hosted-web-analytics), [Stats API](https://plausible.io/docs/stats-api).
Die Ressourcen-/Wartungsbewertung ist eine Schlussfolgerung aus den Stacks, kein Benchmark oder Preisangebot. Keine Software wurde installiert.

## Bevorzugter Datenfluss

Oeffentliche Produktionsseite -> expliziter Event-Collector -> Schemapruefung/Rate Limit -> Minimierung -> atomare Tageszaehler -> geschuetzte Admin-Aggregat-API.
Kein dauerhaftes Raw-Event-Lager. Kein Versand in Preview, Portal, Login oder fremden Seiten.

IONOS und VPS sind verschiedene Origins. Ein spaeterer eigener, kontrollierter Ingestion-Endpunkt benoetigt DNS/TLS/CORS und eine passende CSP-Freigabe.
Fetch mit credentials=omit, keepalive und Referrer-Policy no-referrer ist der zu pruefende Weg; sendBeacon darf nicht ungeprueft Ambient-Cookies mitsenden.
Ein oeffentlich eingebetteter API-Key waere kein Geheimnis und kein wirksamer Eventschutz.
Die Analytics-Funktion muss abschaltbar sein und Website/Portal bei Ausfall nicht blockieren.

### Minimales Eventkonzept, noch kein implementierter API-Vertrag

| Feld | Zulassung / Begrenzung |
| --- | --- |
| schema_version | Fester kleiner Versionswert |
| event_type | Enum: page_view, cta_click, coach_open, topic_open, category_filter, contact_click, external_click |
| page_id / target_id | Serverseitige Allowlist bestehender oeffentlicher Routen/CTA-/Coach-/Themen-IDs, keine freien Titel |
| category_id | Optionaler kanonischer Kategorie-Schluessel; All als eigene Filteraktion, nicht als Themenkategorie |
| Zeit | Serverzeit, Aggregation auf Kalendertag mit festgelegter Zeitzone; keine vertrauenswuerdige Clientzeit |
| environment | Serverseitig production; Preview-Origin ablehnen |
| Herkunft / Viewport | Zunaechst aus; optional nur nach Privacy-Pruefung grobe feste Gruppen |
| Ausgeschlossen | Raw-URL, Query, Fragment, UTM-Freitext, E-Mail, Telefonwert, Formularinhalt, User-/Session-ID, IP, User-Agent, freie properties |

Kontaktklicks zaehlen beispielsweise contact_email, nicht die Mailadresse oder den Nachrichtentext.
Coach-IDs bezeichnen freigegebene oeffentliche Profile; es werden keine Besucheridentitaeten oder Portal-UUIDs erfasst.
Clientangaben bleiben manipulierbare Messsignale. Events zeigen Nutzungsschaetzungen, keine abrechnungsfaehigen oder vollstaendigen Besucherzahlen.

### Aggregation Und Retention, Vorschlag Zur Freigabe

Pro Tag, Eventtyp und erlaubter Route/Dimension nur count; feste Kombinationen und Kardinalitaetsgrenzen.
Im MVP getrennte eindimensionale Auswertungen statt beliebig kombinierbarer feingranularer Besuchersegmente.
Raw Payload nur waehrend der Requestverarbeitung im Arbeitsspeicher, kein Queue-/Disk-/Fehlerlog mit Payload.
Vorgeschlagen: Tagesaggregate 90 Tage; anschliessend loeschen. Kein automatisches Langzeitarchiv.
Fuer seltene Aufschluesselungen eine Mindestmenge, vorgeschlagen 5 Ereignisse, vor Anzeige/Export; Differenzangriffe bei freien Filtern vermeiden.
Schwellenwert und 90 Tage sind Architekturvorschlaege, noch keine fachlich oder rechtlich akzeptierten Fristen.
Backups duerfen abgeloeschte Aggregate nur gemaess freigegebener Backup-Retention enthalten; Restore muss Retention erneut anwenden.
IP-basierte Abuse-Limits getrennt und hoechstens kurzzeitig im RAM, Vorschlag maximal 10 Minuten; nie zur Besucherverknuepfung.
Betrieb muss Reverse-Proxy-, IONOS- und Anwendungslogs separat pruefen; keine pauschale Zusage, dass nirgendwo IP-Adressen verarbeitet werden.

## Messgrenzen Und Cockpit

Pageviews sind Seitenaufruf-Ereignisse, keine Menschen. Keine Kennzahlen zu eindeutigen/wiederkehrenden Besuchern, echten Sessions, verlaesslichen Ein-/Ausstiegsseiten oder Journeys in Level 1.
Verweildauer ist zunaechst nicht verfuegbar. Ein spaeterer, nur im Tab-Speicher gehaltener Aktivzeit-Summenwert braeuchte eine eigene Messspezifikation: Sichtbarkeit, Verluste bei Tabende, Doppelsendungen, Obergrenzen und Nenner.
Keinen Mittelwert aus fehlenden oder nicht vergleichbaren Daten darstellen.
Bot-/Adblocker-/Offline-/Mehrfachklickanteile und Erfassungsbeginn im Dashboard offen ausweisen; keine Behauptung vollstaendiger Botfreiheit.

Das spaetere Portal-Cockpit zeigt Heute / 7 Tage / 30 Tage / benutzerdefinierter begrenzter Zeitraum, Pageviews und CTA-Aktionen.
Zeitreihe, Top-Seiten, Themen, Coaches, Kontakt- und externe Aktionen; Filter nach Route/Kategorie/Event mit sinnvollen Leer-/Fehlerzustaenden.
Herkunft/Geraete nur nach Freigabe; Sessions/Verweildauer ausgeblendet oder klar nicht verfuegbar.
Ruhige, bestehende Portalgestaltung und zugaengliche Diagramme mit Texttabelle; keine Einzelbesucherliste.
Admin serverseitig erlaubt; internal, Coach, reviewer und Firmenkontakt ohne globale Analyticsrechte. Spaetere Reportingrolle nur nach eigener RBAC-Entscheidung.
Keine Vendor-Tokens oder ungeprueften externen Dashboard-Iframes im Browser; Abfragen und Export nur ueber den geschuetzten Server.

## Sicherheits- Und Abnahmekriterien

- Ingestion nur definierte POST-JSON-Nachrichten, maximal vorgeschlagen 1 KiB, feste Enum-/Laengen-/Schemafelder; unbekannte Felder ablehnen.
- Keine beliebigen URLs, Strings oder HTML speichern/anzeigen; strukturierte Logcodes, keine Request-/Token-/Query-/Payloadlogs.
- Origin-Allowlist, passende CORS-Regeln ohne Credentials und Content-Type-Pruefung; Origin ist kein Authentizitaetsbeweis gegen direkte Clients.
- Reverse-Proxy-/Prozesslimits, globale Raten, Requesttimeouts und begrenzte DB-Kardinalitaet verhindern Storage-Wachstum; Aggregation atomar, keine Transaktion pro freiem Label.
- Bekannte Bots nach minimalen transienten Merkmalen ausschliessen, ohne persistentes UA-/IP-Profil; Qualitaet der Statistik als Schaetzung kennzeichnen.
- Event-Retries im MVP aus, um keine versteckte Event-ID/Deduplizierung einzufuehren; moegliche Verluste akzeptieren und dokumentieren.
- Browser-POC beweist keine Cookies/Storage/Identifiers, keine Form-/URL-Geheimnisse, keine Requests in Preview und keine Messung geschuetzter Portalrouten.
- API-Tests fuer Admin/MFA sowie 401/403 aller anderen Rollen, no-store, Zeit-/Zeilenlimits, Exportrechte und Leerdaten.
- Retention-, Backup-/Restore-, Last-, Ausfall-/Kill-Switch-, Abuse- und Loeschtests gehoeren zum spaeteren Implementierungsgate.
- Kein Client-Event oder Browserheader darf einen privilegierten Portalvorgang ausloesen.

## Umsetzungsplan Und Offene Entscheidungen

1. Product Owner bestaetigt Kennzahlumfang, Messgrenzen, Aufbewahrung, Betriebskosten und Datenverantwortliche.
2. Datenschutz/Legal prueft [PRIV-ANALYTICS-01](../decisions/PRIV-ANALYTICS-01.md), Endgeraetezugriff, IP/Logs und Datenschutzhinweis; Consent bleibt OFFEN.
3. Separat freigegebener synthetischer lokaler POC: Schema, Minimierung, Zaehler, Abuse- und Rollen-Negativtests; noch keine oeffentliche Produktion.
4. Nach Review/Ressourcenmessung Staging-Abnahme einschliesslich Betrieb/Restore und privater Admin-Oberflaeche.
5. Erst eigener Produktionsgate fuer DNS/CSP/Script/Endpoint, Benachrichtigung, Notice/Consent falls erforderlich und kontrollierte Aktivierung.
6. Rollback: Collector per Konfiguration aus, Script aus Produktionsartefakt entfernen, Ingestion sperren; Loesch-/Backup-Regeln weiter ausfuehren.

Bei erforderlicher Einwilligung folgt ein eigener CMP-Block mit vorheriger Sperre, Widerruf und Nachweisstrategie.
Kein vorsorglicher Cookiebanner und keine Aktivierung durch dieses Dokument.
CAL-1 bleibt der bestehende naechste Backend-Abnahme-Kandidat; Analytics ist hier ein vorbereiteter spaeterer Slice, CAL-2 und FIN-01 werden nicht vorgezogen.

## Quellenstand

Primaerquellen am 21.10.2026 abgerufen; Links stehen direkt bei den unterstuetzten Aussagen.
Aussagen zur eigenen Loesung sind Projektentwurf, nicht getestete Implementierung.
Vendor-Rechtsbewertungen werden nicht als deutsche Datenschutzfreigabe uebernommen. Keine produktiven Events wurden erhoben.
