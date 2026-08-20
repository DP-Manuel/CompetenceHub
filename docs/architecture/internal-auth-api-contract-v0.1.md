# Internal Auth API Contract v0.1

Stand: 14.08.2026

Status: Implementierungsvertrag auf Grundlage des freigegebenen ADR 0003.
`POST /api/v1/auth/login`, `GET /api/v1/auth/session`,
`POST /api/v1/auth/session/csrf` und `DELETE /api/v1/auth/session` sind lokal
mit PostgreSQL-Repositories,
deny-by-default Verdrahtung und synthetischen Tests umgesetzt.
Runtime-Konfiguration und sieben isolierte Session-Staging-Pfade sind
verifiziert; Cleanup und Service-Health waren erfolgreich. Der neue Login- und
Rate-Limit-Pfad ist lokal und in 11/11 kombinierten Auth-Staging-Pfaden
verifiziert; Cleanup und Service-Health waren erfolgreich. TOTP enrollment,
verification, recovery verification and full-session rotation are now
implemented locally with synthetic tests. ADR 0004 was accepted on 14.08.2026;
migration `0003` and the complete 12/12 MFA harness are verified on isolated
Staging. Migration `0004` and the expanded 13/13 Outbox/Auth harness are also
verified there after separate approval. Deployment is not authorized. The
focused reviews are in
`session-runtime-security-review-2026-08-14.md` und
`first-factor-login-security-review-2026-08-14.md`; the MFA review is in
`mfa-runtime-security-review-2026-08-14.md`.

## Grenze

- Consumer: interne Browser-App fuer `admin` und `internal`
- Provider: eigenstaendiges Competence-Hub-FastAPI-Backend
- Transport: HTTPS, JSON, gleiche Origin fuer App und `/api/v1`
- Auth: opaque Host-only-Cookies; keine Bearer-Tokens im Browser
- Fehler: `application/problem+json`, keine Stacktraces oder Kontoenumeration
- Cache: alle Auth-Antworten `Cache-Control: no-store`

## Cookies

| Cookie | Zweck | Eigenschaften |
| --- | --- | --- |
| `__Host-competence_hub_login` | maximal 5 Minuten gueltige Pre-Auth-Challenge | `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`, keine Domain |
| `__Host-competence_hub_session` | vollstaendige MFA-Sitzung | wie oben; maximal 8 Stunden, 30 Minuten idle |

CSRF-Token werden nicht im Cookie transportiert. Der Client sendet das zur
jeweiligen Challenge/Sitzung gehoerende Token fuer mutierende Aufrufe im Header
`X-CSRF-Token`; der Server prueft Token und Origin.

## Fehlerformat

```json
{
  "type": "https://competencehub.donner-partner.de/problems/authentication-failed",
  "title": "Anmeldung nicht moeglich",
  "status": 401,
  "code": "authentication_failed"
}
```

`code` ist stabil und maschinenlesbar. `detail`, Debugdaten, Kontoexistenz,
Aktivstatus, Rolle oder MFA-Status werden bei oeffentlich erreichbaren
Einstiegsendpunkten nicht offengelegt.

## Endpunkte

### `POST /api/v1/auth/login`

Request: `email`, `password`. Antwort bei korrektem ersten Faktor: `202` mit
`state` (`mfa_required` oder `mfa_enrollment_required`), CSRF-Token im Body und
Pre-Auth-Cookie. Falsche oder deaktivierte Konten: generisches `401`. Der
Endpunkt ist konto- und IP-limitiert.

Lokaler Stand: implementiert. Die HTTP-Grenze akzeptiert ausschliesslich JSON
bis 32 KiB und weist unbekannte Felder ab. Unbekannte, inaktive und nicht fuer
den internen Zugang freigegebene Konten erhalten dieselbe Antwort und
durchlaufen jeweils einen Argon2id-Vergleich. Konto- und Netzwerk-Peer-Buckets
werden mit einem externen HMAC-Schluessel pseudonymisiert; ab dem fuenften
Fehler innerhalb von 15 Minuten greift eine progressive Sperre. Nach korrektem
Passwort entsteht nur eine fuenf Minuten gueltige Pre-Auth-Challenge, keine
vollstaendige Sitzung. `X-Forwarded-For` wird vor einer separaten
Reverse-Proxy-Trust-Entscheidung nicht ausgewertet.

### `POST /api/v1/auth/mfa/totp/verify`

Request: `code`; Pre-Auth-Cookie und CSRF-Header erforderlich. Erfolg: `204`,
Pre-Auth-Cookie wird geloescht, ein rotiertes Session-Cookie gesetzt und das
neue Session-CSRF-Token einmalig im Response-Header `X-CSRF-Token` geliefert.
Fehler: generisches `401`; abgelaufene Challenge: `401`; Rate Limit: `429`.

Lokaler Stand: implementiert. Der akzeptierte TOTP-Zeitschritt wird in derselben
Transaktion wie Challenge-Verbrauch, Session-Rotation und Audit aktualisiert;
ein gleicher oder aelterer Schritt wird abgewiesen.

### `POST /api/v1/auth/mfa/totp/enrollment`

Nur fuer eine gueltige Challenge mit `mfa_enrollment_required`. Erzeugt ein
verschluesseltes, noch nicht aktiviertes TOTP-Credential und liefert einmalig
eine `otpauth`-URI. Antwort: `201`, `no-store`.

Lokaler Stand: implementiert mit AES-256-GCM, benutzergebundener Associated
Data und extern versioniertem Keyring.

### `POST /api/v1/auth/mfa/totp/enrollment/confirm`

Request: erster TOTP-Code. Erfolg aktiviert TOTP, erzeugt einmalig anzuzeigende
Recovery-Codes und schliesst die MFA-Challenge ab. Antwort: `200` mit
`recovery_codes`, rotiertem Session-Cookie und neuem Session-CSRF-Header. Ein
nicht bestaetigtes Secret gewaehrt keinen Portalzugang.

Lokaler Stand: implementiert. Plaintext-Codes verlassen nur diesen einmaligen
Erfolgsbody; Persistenz erhaelt HMAC-Digest und Key-Version.

### `POST /api/v1/auth/mfa/recovery/verify`

Request: einzelner Recovery-Code; Pre-Auth-Cookie, exakte Origin und
Challenge-CSRF erforderlich. Erfolg verbraucht genau einen unbenutzten Code,
verbraucht die Challenge und rotiert in eine neue Vollsession. Antwort: `204`
mit Session-Cookie und neuem Session-CSRF-Header. Wiederverwendung oder Fehler:
generisches `401`; Rate Limit: `429`.

Lokaler Stand: implementiert. Die atomare Einmalverwendung ist im vollstaendigen
MFA-Staging-Harness gegen PostgreSQL belegt.

### `GET /api/v1/auth/session`

Erfordert eine aktive MFA-Sitzung. Antwort: interne Benutzer-ID, Anzeigename,
explizite Rollen, Authentisierungszeit und Ablaufzeiten. Keine Passwort-, Token-
oder TOTP-Felder.

Lokaler Stand: implementiert. Die Abfrage akzeptiert nur aktive Benutzer mit
aktiver Rolle `admin` oder `internal`, gueltigem MFA-Level sowie gueltiger Idle-
und Absolutzeit. Sie aktualisiert die Idle-Zeit atomar, speichert und uebergibt
aber nur den Hash des Browser-Tokens an die Persistenzschicht.

### `POST /api/v1/auth/session/csrf`

Erfordert eine aktive MFA-Sitzung und die exakt konfigurierte Browser-Origin.
Der Endpunkt rotiert den sitzungsgebundenen CSRF-Digest atomar und liefert das
neue Klartext-Token einmalig im Response-Header `X-CSRF-Token`. Antwort: `204`.
Der Client nutzt dies nach einem Seiten-Reload, weil CSRF-Material gemaess ADR
0006 nicht in Browser-Speichern persistiert wird. Fehlende/falsche Origin:
`403`; ungueltige oder abgelaufene Sitzung: `401` ohne Token-Header.

Stand 20.08.2026: implementiert und durch Repository-, API- und synthetische
Portaltests belegt. Der reale PostgreSQL-Pfad bestand im vollstaendigen
Staging-Harness gemeinsam mit den uebrigen 13 Pfaden; Cleanup und vier
Service-Healthchecks waren erfolgreich.

### `DELETE /api/v1/auth/session`

Widerruft die aktuelle Sitzung idempotent und loescht das Cookie. Antwort:
`204`, auch wenn die Sitzung bereits ungueltig ist.

Lokaler Stand: implementiert. Eine aktive Sitzung wird nur nach exakter Origin-
und sitzungsgebundener CSRF-Pruefung widerrufen. Der Widerruf und ein
datensparsames Logout-Auditereignis erfolgen in derselben Transaktion.

### `DELETE /api/v1/auth/sessions`

Widerruft alle eigenen Sitzungen. Aktive Sitzung und CSRF-Header erforderlich.
Antwort: `204`.

## Initialer Admin-CLI

`competence-hub-admin create-initial-admin` ist ein ausschliesslich
interaktiver Bootstrap-Prozess. E-Mail, Anzeigename, Passwort und
Passwortbestaetigung werden nicht als Kommandoargumente angenommen. Die
Datenbankverbindung und der absolute Pfad zu einer freigegebenen lokalen
SHA-256-Fingerabdruckdatei kommen aus externer Prozesskonfiguration. Der Prozess
verweigert nicht-interaktive Ausfuehrung, einen zweiten wirksamen Initial-Admin
und jede Ausfuehrung ohne Kompromittiert-Passwortquelle. Eine reale Ausfuehrung
bleibt ein separates Betriebs- und Datengate.

### `POST /api/v1/auth/password-reset/request`

Request: `email`. Antwort immer `202` mit identischem Body und vergleichbarem
Timing. Pro Konto/IP limitiert. Mailversand erfolgt spaeter ueber einen eigenen
Adapter; rohe Links erscheinen nicht in Produktionslogs.

### `POST /api/v1/auth/password-reset/confirm`

Request: einmaliges Reset-Token und neues Passwort. Erfolg: `204`; alle
Sitzungen und offenen Reset-Token werden widerrufen. Ungueltig/abgelaufen:
generisches `400`.

### `POST /api/v1/auth/invitations/accept`

Request: einmaliges Einladungstoken und neues Passwort. Erfolg erzeugt eine
Pre-Auth-Challenge fuer MFA-Enrollment. Wiederverwendung oder Ablauf: `400`.

### `POST /api/v1/admin/users/invitations`

Nur `admin` mit MFA und frischer Reauthentisierung. Request: `email`,
`display_name`, nicht privilegierte Anfangsrollen. `Idempotency-Key` ist
erforderlich. Erfolg: `202`. Eine Adminrollenvergabe ueber diesen Endpunkt ist
nicht erlaubt.

Status 14.08.2026: ADR 0005 ist akzeptiert. Der lokale Servicevertrag, die
transaktionale Outbox, persistente Idempotenz und die Admin-HTTP-Grenze sind
implementiert. Ohne konfigurierte Lifecycle-Runtime bleibt der Endpunkt
fail-closed. Es wird kein Roh-Token ueber die API ausgegeben. Migration `0004`,
und ihre 13/13 synthetischen Staging-Pfade sind nach separater Freigabe
verifiziert. Mailadapter, Runtime-Schluessel, persistente Dienste, echte Konten
und Deployment bleiben separat freizugebende Schritte.

## Allgemeine Regeln

- JSON-Requests sind standardmaessig auf 32 KiB begrenzt.
- Unbekannte Felder werden abgewiesen.
- Auth-Endpunkte setzen keine offenen CORS-Header.
- Mutierende Endpunkte pruefen CSRF und Origin, sofern eine Challenge oder
  Sitzung besteht.
- `401` bedeutet fehlende/ungueltige Authentisierung, `403` fehlende Policy oder
  Scope, `409` einen konfliktierenden Zustand und `429` Rate Limit.
- Audit protokolliert Ergebnis und stabile Ereignisart, niemals rohe Requests,
  Passwoerter, Cookies, Token, TOTP-Secrets oder Recovery-Codes.

## Noch nicht Teil dieses Vertrags

- Coach-, Firmenkontakt- und Teilnehmerlogin
- OAuth/OIDC/SSO, WebAuthn und native App-Tokens
- fachliche Company-, Coach- oder Request-APIs
- produktiver Mailanbieter
