# Portal Domain Model v0.1

Stand: 13.08.2026

## Zweck und Quellenrang

Dieses Modell ist die sichere, implementierungsnahe Uebernahme der
Product-Owner-Arbeitsmappe
`Competence_Hub_Datenmodell_Portalplanung_v0.2.xlsx` aus dem freigegebenen
Tagesordner vom 13.08.2026. Bei Widerspruechen hat die bearbeitete Excel vor den
abgeleiteten Begleitdokumenten Vorrang.

Die erste Ausbaustufe ist B2B-first. Sie bildet noch keinen vollstaendigen
Coaching-, Vertrags-, Termin- oder Abrechnungsprozess ab.

## Statusbegriffe

- **Bestaetigt:** fachlich belastbar und fuer Schema/API/Wireframes verwendbar.
- **Provisorisch:** technisch vorbereitbar, aber noch nicht als unveraenderliche
  Fachregel behandeln.
- **Deferred:** bewusste Anschlussstelle fuer eine spaetere Phase.

## Kernobjekte

| Objekt | Status | Zweck | Datenschutzklasse |
| --- | --- | --- | --- |
| Benutzer | Bestaetigt | Portalidentitaet, Aktivstatus und Audit-Akteur | Personenbezogen, `NO_CACHE` |
| Rolle | Bestaetigt | Buendel serverseitig gepruefter Rechte | Intern |
| Unternehmen | Bestaetigt | B2B-Kundenstamm fuer Kontakte und Anfragen | Intern, teilweise personenbeziehbar |
| Ansprechpartner | Bestaetigt | Geschaeftlicher Kontakt eines Unternehmens | Personenbezogen, `NO_CACHE` |
| Coach | Bestaetigt | Interner Coachstamm plus kontrolliert freigegebene oeffentliche Daten | Personenbezogen, teilweise oeffentlich |
| Thema | Bestaetigt | Kanonische, wiederverwendbare Fachthemen | Oeffentlich/intern |
| Leistung | Bestaetigt | Angebot oder Format fuer Zielgruppen | Oeffentlich/intern |
| Coaching-Anfrage | Bestaetigte Struktur, provisorischer Ablauf | Zentraler B2B-Bedarfsvorgang | Vertraulich, `NO_CACHE` |
| Audit-Ereignis | Bestaetigt | Nachweis sicherheitsrelevanter Aenderungen | Personenbezogen, `NO_CACHE` |

## Beziehungen

### Bestaetigt

- Benutzer `n:m` Rolle; Mehrfachrollen sind ein Architekturprinzip.
- Coach `n:m` Thema.
- Coaching-Anfrage `n:m` Leistung.
- Unternehmen `1:n` Coaching-Anfrage im B2B-first Slice.
- Coaching-Anfrage `n:1` interne Zustaendigkeit, zunaechst optional.

### Belastbar, aber mit offener Detailfrage

- Unternehmen `1:n` Ansprechpartner; mehrere Kontakte sind fachlich sinnvoll,
  ein Primaerkontakt ist noch nicht beschlossen.
- Coaching-Anfrage `n:m` Thema; eine spaetere Prioritaet pro Thema ist offen.
- Coach `n:m` Leistung; Relation ist optional, bis die explizite Freigabe je
  Coach und Leistung entschieden ist.
- Coach und Ansprechpartner koennen optional mit einer Portalidentitaet
  verbunden werden. Die genaue Account-/Einladungslogik folgt aus dem Auth-ADR.

## Rollenmodell v0.1

Aktive Arbeitsrollen:

- `admin`
- `internal`
- `coach`
- `company_contact`

`participant` bleibt deferred. Die Rollenbezeichnungen sind als Arbeitscodes
verwendbar, aber bis zur formalen Rollenfreigabe nicht als dauerhaftes
externes Vertragsversprechen zu behandeln.

Zugriff wird deny-by-default und serverseitig durchgesetzt. Mehrfachrollen
vereinigen nur explizit erlaubte Rechte. Der Umfang "eigen", "eigene Firma"
oder "zugewiesen" muss aus fachlichen Beziehungen ermittelt werden und darf
nicht allein aus Frontendnavigation abgeleitet werden.

## Coaching-Anfrage

Bestaetigte Mindestinformationen:

- Erstellungszeitpunkt
- Betreff
- vertrauliche Beschreibung
- Statusfeld
- optionale interne Zustaendigkeit
- optionaler gewuenschter Zeitraum
- optionales bevorzugtes Format
- ein Unternehmen im B2B-first Slice
- null bis mehrere Themen und Leistungen

Die Excel enthaelt einen plausiblen Statusentwurf von `Neu` bis
`Abgeschlossen` sowie Ablehnung, kein passender Coach und Pause. Diese Werte
duerfen als Daten und Wireframe-Inhalte vorbereitet werden. Erlaubte
Transitionen, automatische Aktionen und die Reihenfolge von Coach-Anfrage,
Angebot und Auftrag bleiben bis zum Praxisdurchlauf mit Janay offen.

## Auditgrenze

Mindestens zu protokollieren sind:

- Benutzeranlage und Deaktivierung
- Rollenvergabe und Rollenentzug
- Publikationsfreigaben von Coachprofilen
- relevante Status- und Zustaendigkeitsaenderungen an Anfragen
- erlaubte Exporte
- sicherheitsrelevante Zugriffs- oder Autorisierungsereignisse, soweit fuer den
  Betrieb notwendig

Auditdaten enthalten keine Passwoerter, Tokens oder vollstaendigen
personenbezogenen Payloads. Retention und administrative Leserechte bleiben ein
Produktiv-Gate.

## PWA- und Cachegrenze

- Oeffentliche, freigegebene Assets duerfen `PUBLIC_STATIC` sein.
- Benutzer, Firmenkontakte, Coaching-Anliegen und Auditdaten sind `NO_CACHE`.
- Vertrauliche Dokumente sind spaeter `CONFIDENTIAL_DOCUMENT`.
- Eine installierbare PWA bedeutet nicht automatisch Offline-Fachdaten.
- Kein Service Worker darf authentifizierte Antworten oder vertrauliche
  Inhalte zwischenspeichern, bevor eine gesonderte Sicherheitsentscheidung
  vorliegt.

## Deferred

Noch nicht Teil des Kerns:

- Auftraege, Termine, Dokumente und Feedbacktabellen
- Reportingformeln und Coach-Auslastung
- B2C-/Mindforge-Portal
- Teilnehmer, Massnahmen, Praktikum/Vermittlung und Stellen
- Vertraege, Rechnungen und Dateiablage
- Kalenderintegration, Push und Offline-Fachfunktionen
- KI-Matching, Scores und automatische Benachrichtigungen
