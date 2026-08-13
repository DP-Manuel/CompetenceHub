# Interne Authentifizierung v0.1

Stand: 13.08.2026

Grundlage: der am 13.08.2026 freigegebene ADR 0003. Diese Anforderungen gelten
fuer den ersten internen Slice mit `admin` und `internal`. Die Freigabe umfasst
die lokale Grundlage mit synthetischen Daten, aber keine Serverinstallation,
Echtdaten oder Veroeffentlichung.

## Umfang

### Enthalten

- Einladung interner Konten
- Passwortsetzung und Login
- TOTP-MFA und Recovery-Codes
- serverseitige Sitzungen, Logout und Widerruf
- Passwort-Reset
- serverseitige RBAC-Grundpruefung und Auth-Audit
- synthetische lokale und Staging-Tests

### Nicht enthalten

- Selbstregistrierung
- Coach-, Firmenkontakt- oder Teilnehmerlogin
- SSO, Social Login, Passkeys oder native App-Authentifizierung
- produktive Mailintegration
- produktive Personen- oder Unternehmensdaten
- Fach-CRUD ausserhalb eines minimalen geschuetzten Testendpunkts

## Funktionale Anforderungen

- **AUTH-001:** Das System erlaubt keine oeffentliche Selbstregistrierung.
- **AUTH-002:** Ein Admin kann ein aktives internes Konto per einmaligem,
  kurzlebigem Token einladen; offene aeltere Einladungen werden widerrufen.
- **AUTH-003:** Das System speichert Passwoerter ausschliesslich als Argon2id-
  Hash und speichert keine wiederherstellbaren Passwoerter.
- **AUTH-003a:** Das System akzeptiert Passphrasen von 12 bis mindestens 128
  Zeichen einschliesslich Leerzeichen, erzwingt keine Zeichenklassen oder
  turnusmaessigen Wechsel und lehnt lokal erkannte verbreitete beziehungsweise
  kompromittierte Passwoerter ab.
- **AUTH-004:** Nach korrektem ersten Faktor verlangt das System fuer interne
  Staging-/Produktionskonten einen eingerichteten und bestaetigten TOTP-Faktor.
- **AUTH-005:** Nach erfolgreicher Authentisierung erstellt das System eine
  serverseitige Sitzung und uebermittelt nur die opaque Sitzungskennung im
  sicheren Host-only-Cookie.
- **AUTH-006:** Das System beendet Sitzungen nach 30 Minuten Inaktivitaet oder
  acht Stunden absoluter Laufzeit.
- **AUTH-007:** Nutzer koennen die aktuelle und alle eigenen Sitzungen
  widerrufen.
- **AUTH-008:** Deaktivierung, Passwort-Reset und sicherheitsrelevante
  Rollenentziehung widerrufen alle Sitzungen des betroffenen Kontos.
- **AUTH-009:** Ein Passwort-Reset verwendet ein einmaliges Token mit maximal
  30 Minuten Laufzeit und liefert kontoneutrale Antworten.
- **AUTH-010:** Jede zustandsaendernde Browseranfrage wird durch CSRF-Token und
  Origin-Pruefung geschuetzt.
- **AUTH-011:** Jede geschuetzte API-Aktion prueft serverseitig aktive Identitaet,
  explizite Rolle und Datensatzscope deny-by-default.
- **AUTH-012:** Nur ein Admin mit MFA und frischer Authentisierung darf die
  Adminrolle oder Adminkonten veraendern.
- **AUTH-013:** Ein `internal`-Benutzer kann weder sich selbst noch andere zu
  `admin` machen.
- **AUTH-014:** Das System verhindert, dass die letzte wirksame Adminberechtigung
  regulaer entfernt wird.
- **AUTH-015:** Authentifizierte Antworten werden mit `Cache-Control: no-store`
  ausgeliefert und nicht offline gespeichert.
- **AUTH-016:** Login, Reset, Einladung und MFA-Pruefung werden konto- und
  IP-bezogen begrenzt; Startwert sind fuenf Fehler in 15 Minuten mit
  progressiver Verzoegerung.
- **AUTH-017:** Sicherheitsrelevante Konto-, Rollen-, Sitzungs- und Resetaktionen
  werden ohne Secrets oder vollstaendige Payloads auditiert.
- **AUTH-018:** Ein initialer Admin wird ausschliesslich ueber einen
  interaktiven Server-/CLI-Prozess ohne Default-Credentials angelegt.

## Nichtfunktionale Anforderungen

- **AUTH-NF-001:** Sitzungstoken besitzen mindestens 256 Bit Entropie; nur ihr
  kryptografischer Hash wird persistiert.
- **AUTH-NF-002:** Passwoerter, Session-IDs, CSRF-Token, Reset-/Einladungstoken,
  TOTP-Secrets und Recovery-Codes erscheinen nie in Anwendungslogs.
- **AUTH-NF-002a:** TOTP-Secrets werden mit einem ausserhalb der Datenbank
  gehaltenen Schluessel authentifiziert verschluesselt; Recovery-Codes und
  Rate-Limit-Identifier werden mit einem getrennten externen HMAC-Schluessel
  pseudonymisiert.
- **AUTH-NF-003:** Alle Auth-Flows laufen ausschliesslich ueber HTTPS; Cookies
  sind `Secure`, `HttpOnly`, `SameSite=Lax`, host-only und `Path=/`.
- **AUTH-NF-004:** App und API verwenden im ersten Slice dieselbe Origin; CORS
  ist standardmaessig nicht breit freigegeben.
- **AUTH-NF-005:** Laufzeitsecrets liegen ausserhalb von Git in einer nur fuer
  den Competence-Hub-Systembenutzer lesbaren Konfiguration.
- **AUTH-NF-006:** Staging und Produktion verwenden getrennte Origins, Secrets,
  Cookies und Datenbanken.
- **AUTH-NF-007:** Alle Fehlermeldungen vermeiden Konto-, Aktivstatus-, Rollen-
  oder MFA-Enumeration.
- **AUTH-NF-008:** Externe Nutzerrollen bleiben durch Feature- und Policygrenzen
  deaktiviert, bis eigene Anforderungen und Tests freigegeben sind.

## Akzeptanzkriterien

| ID | Bezug | Pruefung | Erwartung |
| --- | --- | --- | --- |
| AUTH-AC-001 | AUTH-001 | Aufruf einer Registrierungsroute | Route fehlt oder antwortet mit kontrolliertem 404/405 |
| AUTH-AC-002 | AUTH-002, AUTH-009 | Token zweimal verwenden | erste Nutzung moeglich, zweite abgewiesen |
| AUTH-AC-003 | AUTH-003 | Datenbank und Logs nach Passwortsetzung pruefen | nur Argon2id-Hash, kein Klartext/Token |
| AUTH-AC-003a | AUTH-003a | lange Passphrase, Leerzeichen, verbreitetes Passwort und Wechselintervall pruefen | Passphrase erlaubt, verbreitetes Passwort abgewiesen, kein grundloser Zwangswechsel |
| AUTH-AC-004 | AUTH-004 | korrektes Passwort ohne MFA | keine vollstaendige Sitzung |
| AUTH-AC-005 | AUTH-005, AUTH-NF-003 | Login-Cookie inspizieren | alle festgelegten Attribute, kein Token im Body/Storage |
| AUTH-AC-006 | AUTH-006 | Idle- und Absolutzeit simulieren | Sitzung wird serverseitig ungueltig |
| AUTH-AC-007 | AUTH-007, AUTH-008 | Logout-all, Reset und Deaktivierung | bestehende Sitzungen sofort abgewiesen |
| AUTH-AC-008 | AUTH-010 | POST ohne/mit falschem CSRF oder Origin | 403 ohne Zustandsaenderung |
| AUTH-AC-009 | AUTH-011 | unbekannte Aktion und fremder Scope | 403 ohne Datenleck |
| AUTH-AC-010 | AUTH-012, AUTH-013 | Intern vergibt Adminrolle | 403 und Auditereignis |
| AUTH-AC-011 | AUTH-014 | letzte Adminrolle entfernen | kontrolliert abgewiesen |
| AUTH-AC-012 | AUTH-015 | geschuetzte Antwort inspizieren | `Cache-Control: no-store`; kein Service-Worker-Cache |
| AUTH-AC-013 | AUTH-016 | wiederholte Fehlversuche | Limit/Verzoegerung greift, Antwort bleibt generisch |
| AUTH-AC-014 | AUTH-017, AUTH-NF-002 | Audit/Logs nach allen Flows pruefen | Ereignisse vorhanden, keine Auth-Secrets |
| AUTH-AC-015 | AUTH-NF-006 | Staging-Cookie gegen Produktion | ungueltig und nicht mitsendbar |
| AUTH-AC-016 | AUTH-NF-008 | Coach-/Firmenrolle versucht Login | kontrolliert deaktiviert, kein Portalzugang |
| AUTH-AC-017 | AUTH-NF-002a | TOTP-, Recovery- und Rate-Limit-Speicher pruefen | TOTP authentifiziert verschluesselt; Recovery-/Bucketwerte nur als HMAC-Digest |

## Definition of Done fuer den Implementierungsslice

- ADR 0003 ist explizit freigegeben.
- Auth-Schema und API-Vertraege sind versioniert und reviewt.
- Alle obigen Akzeptanzkriterien sind automatisiert oder mit begruendeter
  manueller Pruefung nachgewiesen.
- Security-Review findet keine offene hohe oder kritische Schwachstelle.
- Tests verwenden ausschliesslich synthetische Konten und Daten.
- Keine Secrets, `.env`, Tokens oder Testzugangsdaten sind versioniert.
- Backend-Deployment und produktive Mailintegration bleiben getrennte,
  ausdruecklich freizugebende Schritte.
