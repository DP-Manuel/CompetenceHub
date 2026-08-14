# ADR 0005 - Auth-Token-Zustellung und Idempotenz

Stand: 14.08.2026

## Status

Accepted. Freigegeben durch Manuel am 14.08.2026.

Diese Entscheidung genehmigt die lokale Implementierung und Vorbereitung von
Migration `0004`. Sie genehmigt weder einen Mailanbieter, echte Konten,
Runtime-Secrets, Staging-Aenderungen noch ein Deployment. Die Anwendung von
Migration `0004` auf Staging bleibt eine eigene Freigabe.

Folgestatus 2026-08-14: Manuel hat Migration `0004` anschliessend separat fuer
das leere, synthetische Staging freigegeben. Migration, rollback-only Smoke,
13/13 Integrationspfade, Null-Rueckstaende, geschuetzte Pre/Post-Dumps und
unveraenderte Dienst-/Netzwerkgesundheit sind nachgewiesen. Mailanbieter,
Runtime-Secrets, echte Konten/Daten, persistente Dienste und Deployment bleiben
weiterhin nicht freigegeben.

## Kontext

ADR 0003 verlangt Einladungen und Passwort-Reset mit einmaligen, kurzlebigen
Tokens. Der lokale Lifecycle erzeugt 256-Bit-Tokens, speichert nur SHA-256-
Digests und kann Einladungen beziehungsweise Reset atomar annehmen. Produktiver
Mailversand ist weiterhin ausgeschlossen.

Der Admin-Vertrag verlangt fuer Einladungserzeugung einen `Idempotency-Key`.
Eine synchrone Zustellung nach dem Datenbank-Commit erzeugt zwei Fehlerfenster:

- Token gespeichert, Mailversand fehlgeschlagen
- Mail versendet, HTTP-Antwort verloren und Anfrage wiederholt

Roh-Tokens duerfen nicht in Logs oder der One-Time-Token-Tabelle erscheinen.
Ohne persistente Idempotenz und Zustellstatus waere eine scheinbar fertige
Adminroute daher betrieblich unzuverlaessig.

## Entscheidung

### Transaktionale Outbox

- Einladung beziehungsweise bekannter Reset erzeugt in derselben Transaktion
  Token-Digest, fachlichen Tokenzustand und einen Outbox-Eintrag.
- Der Outbox-Eintrag enthaelt nur die minimalen Zustelldaten. Der benoetigte
  Klartexttoken liegt ausschliesslich in einem versionierten AES-256-GCM-
  Umschlag mit eigenem, externem Schluesselring.
- Der Outbox-Schluessel ist von TOTP-, Recovery- und Rate-Limit-Schluesseln
  getrennt. Neue Nonce und gebundene Associated Data werden pro Nachricht
  verwendet.
- Ein spaeterer Worker beansprucht Eintraege atomar, begrenzt Wiederholungen,
  dokumentiert naechsten Versuch und Erfolg und entfernt den verschluesselten
  Payload nach bestaetigter Zustellung.
- Ohne konfigurierten Worker und freigegebenen Mailadapter bleibt die Runtime
  fuer Tokenanforderungen fail-closed.

### Idempotenz

- Der Admin-Einladungsendpunkt verlangt weiterhin `Idempotency-Key`.
- Persistiert werden nur ein HMAC-Digest des Schluessels, Actor, Scope,
  Request-Fingerprint, Ergebnisreferenz und Ablaufzeit.
- Gleicher Actor/Scope/Key und gleicher Request liefert das bereits festgelegte
  Ergebnis, ohne zweiten Token oder zweite Nachricht.
- Gleicher Key mit anderem Request wird als Konflikt abgewiesen.
- Idempotenz- und Outbox-HMAC-/Verschluesselungsschluessel bleiben ausserhalb
  von Git und PostgreSQL.

### Datenschutz und Aufbewahrung

- Unbekannte Reset-Adressen erzeugen keine Outbox-Nachricht und werden nicht
  persistiert; die HTTP-Antwort bleibt identisch.
- Empfaengeradresse, Templatekennung und verschluesselter Payload werden nur so
  lange wie fuer Zustellung und begrenzte Wiederholung erforderlich gehalten.
- Erfolgreich versendete verschluesselte Payloads werden geloescht; technische
  Metadaten erhalten eine noch festzulegende kurze Aufbewahrungsfrist.
- Mailinhalte, Links und Tokens erscheinen nie in normalen Logs oder Audit-
  Ereignissen.

## Schemafolge bei Freigabe

Eine separate lokale Migration `0004` wuerde voraussichtlich zwei Tabellen
einfuehren:

- `auth_idempotency_records`
- `auth_token_delivery_outbox`

Indizes werden auf Ablauf, Zustellstatus und naechsten Versuch begrenzt. Die
Runtime-Rolle erhaelt nur die fuer Erzeugung, Claim, Statuswechsel und
Bereinigung benoetigten Rechte. Migration und Staging-Anwendung bleiben eigene
Freigaben mit Pre-/Post-Dump, rollback-only Smoke und synthetischer Integration.

## Alternativen

### Synchroner Mailversand ohne Outbox

Einfacher, aber verworfen empfohlen: Commit und externer Versand koennen nicht
atomar werden; Retry- und Idempotenzverhalten bleiben fragil.

### Roh-Token in der Datenbank

Verworfen. Ein Datenbank- oder Backupzugriff wuerde aktive Einladungs- und
Resetlinks unmittelbar offenlegen.

### Kein eigener Mailfluss, manuelle Tokenweitergabe

Nur fuer rein synthetische Entwicklung denkbar, fuer reale privilegierte Konten
verworfen. Copy/Paste, Chat oder Tickets waeren kein kontrollierter
Zustellkanal.

## Konsequenzen und Gates

- Mehr Schema-, Worker-, Schluessel- und Monitoringaufwand als bei synchronem
  Versand.
- Dafuer reproduzierbare Zustellung, persistente Idempotenz, begrenzte Retries
  und kein Roh-Token in normaler Persistenz.
- Vor Implementierung: ADR-Freigabe.
- Vor Staging: separate Migrationfreigabe und synthetischer Outbox-/Retry-Test.
- Vor realer Zustellung: Mailanbieter, Absenderdomain, Templates,
  Aufbewahrungsfrist, Datenschutzpruefung, Monitoring und Notfallweg freigeben.
