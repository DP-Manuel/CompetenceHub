# Portal Schema Specification v0.1

Stand: 13.08.2026

## Ziel

Technische Uebersetzung des bestaetigten B2B-first Fachkerns fuer PostgreSQL
16. Die zugehoerige lokale Migration liegt unter
`apps/webapp/database/migrations/0001_portal_core.sql`. Sie ist noch nicht auf
dem VPS ausgefuehrt.

Alle Tabellen liegen im bestehenden Schema `competence_hub`. Primaerschluessel
sind UUIDs, ausgenommen die fortlaufende technische ID des Auditlogs.

## Tabellen

### `portal_users`

Zweck: Portalidentitaet ohne Vorfestlegung des Auth-Verfahrens.

- `id uuid`, PK
- `display_name text`, Pflicht, nicht leer
- `email text`, Pflicht; eindeutiger Index auf normalisierter Kleinschreibung
- `active boolean`, Pflicht, Default `true`
- `created_at`, `updated_at` als `timestamptz`

Kein Passwortfeld wird angelegt. Passwort, Identity Provider, Session und MFA
folgen aus dem Auth-ADR.

### `roles`

- `id uuid`, PK
- `code text`, Pflicht, technisch eindeutig
- `display_name text`, Pflicht
- `active boolean`, Pflicht

Die vier Arbeitsrollen werden als aenderbare Stammdaten geseedet. Konkrete
Permissions bleiben Code-/Policy-Verantwortung, bis die Auth-Architektur
entschieden ist.

Die Laufzeitrolle darf Rollendefinitionen nur lesen. Admin und Intern weisen
vorhandene Rollen zu, erzeugen aber keine neuen privilegierten Rollenstamme.

### `user_roles`

- zusammengesetzter PK `(user_id, role_id)`
- optionale Vergabeinformationen `assigned_at`, `assigned_by_user_id`
- FKs mit restriktivem Rollen-Loeschen und Kaskade beim Benutzer

### `companies`

- `id`, `name`, optional `industry`, Pflichtfeld `status`
- optionale vertrauliche `internal_notes`
- Zeitstempel

Rechtsname, Anzeigename, Anschrift und Kundennummer werden nicht vorweggenommen.
Statuswerte bleiben Textstamm statt Enum, bis die Fachwerte bestaetigt sind.

### `company_contacts`

- `company_id` Pflicht-FK
- optional `portal_user_id` als provisorische Accountbruecke
- Vorname, Nachname und geschaeftliche E-Mail als Pflichtfelder
- Telefon und Funktion optional
- Zeitstempel

Eine Primaerkontakt-Markierung wird noch nicht erzwungen.

### `coaches`

- optional eindeutige `portal_user_id`
- `display_name` Pflicht
- `public_profile_status` Pflicht
- optionale `internal_availability` und `region`
- Zeitstempel

Oeffentliche Marketinginhalte und interne Vertrags-/Kontaktdaten gehoeren nicht
ungeprueft in diese Kerntabelle.

### `topics` und `coach_topics`

- Themenname case-insensitive eindeutig, Aktivstatus Pflicht
- Join-PK `(coach_id, topic_id)`
- kein Qualifikationsscore oder Nachweisdokument im ersten Slice

### `services` und `coach_services`

- Leistung mit Name, Zielgruppe und Aktivstatus
- Leistungsname case-insensitive eindeutig
- optionale Join-Tabelle Coach/Leistung

Preise, Vertraege und Marketingtexte bleiben getrennt. Die Join-Tabelle
existiert optional, erzwingt aber keine Zuordnung.

### `coaching_requests`

- Pflicht-FK `company_id`
- optionale `responsible_user_id` und `created_by_user_id`
- `created_at`, `updated_at`
- Betreff, vertrauliche Beschreibung und Status als Pflichtfelder
- gewuenschter Zeitraum und bevorzugtes Format optional als Text

Der Status ist bewusst kein PostgreSQL-Enum. Die Statusmaschine ist noch nicht
fachlich freigegeben.

### `request_topics` und `request_services`

- zusammengesetzte PKs verhindern Dubletten
- Kaskadenloeschung nur fuer die Join-Zeile beim Entfernen der Anfrage
- keine Prioritaet oder Zuordnungsphase im ersten Schema

### `audit_events`

- `id bigint GENERATED ALWAYS AS IDENTITY`
- optionaler `actor_user_id` fuer Systemereignisse
- Zeitpunkt, Aktion, Objekttyp, optionale Objekt-UUID und Ergebnis
- keine Rohpayload-, Token-, IP- oder Devicefelder ohne spaetere Begruendung

Die App-Rolle darf Auditereignisse lesen und anlegen, aber nicht aktualisieren
oder loeschen. Zusaetzliche API-Autorisierung begrenzt die Lesesicht auf
Admin/Intern.

## Sichere Constraints

- Pflichttexte duerfen nach `btrim` nicht leer sein.
- E-Mails werden mindestens auf ein einfaches `@`-Format geprueft; vollstaendige
  Zustellbarkeit ist keine DB-Aufgabe.
- Join-Tabellen besitzen zusammengesetzte Primaerschluessel.
- FKs verhindern verwaiste Rollen-, Kontakt-, Themen- und Leistungsbeziehungen.
- Die App-Rolle besitzt kein `CREATE` auf dem Schema.
- Die App-Rolle darf Kernstammdaten und Anfragen nicht physisch loeschen;
  Deaktivierung beziehungsweise fachliche Statuswechsel sind der sichere
  Standard. Join-Zuordnungen duerfen kontrolliert entfernt werden.
- `updated_at` wird durch eine kleine `SECURITY INVOKER`-Triggerfunktion gesetzt.

## Bewusst offene Constraints

- finale Rollenbezeichnungen und Auth-Identitaet
- Unternehmensstatus und Requeststatus als kontrollierte Vokabulare
- Primaerkontakt je Firma
- Pflicht/Verifikation von Coach-Leistungen
- finale Statusuebergaenge und automatische Aktionen
- Retention, Loeschung und Archivierung
- Row-Level Security; erst nach festem Session-/Identity-Kontext entscheiden

## Indizes und bekannte Abfragen

- Benutzerlogin ueber `lower(email)`
- Firmen nach `lower(name)` und Status
- Kontakte nach Firma und `lower(email)`
- Coaches nach Profilstatus und Region
- Themen/Leistungen nach case-insensitive eindeutigem Namen
- Anfragen nach Firma, Status, Zustaendigkeit und Erstellungszeit
- Audit nach Zeitpunkt, Akteur und Objekt

## Migration und Rollback

- Migration nur mit `competence_hub_migrator`, internem Owner-Role-Switch und
  `ON_ERROR_STOP` ausfuehren.
- Vor Staging-Anwendung geschuetzten Dump erstellen.
- Verifikation verwendet ausschliesslich synthetische Daten und endet mit
  `ROLLBACK`.
- Vor realen Daten bleibt der externe verschluesselte Restore-Nachweis Pflicht.
- Bei Fehlern vor Realdata: Transaktion bricht ab; bei spaeter entdecktem Fehler
  Staging aus dem vorherigen Dump wiederherstellen. Keine spontane
  Tabellenloeschung auf produktiven Daten.
