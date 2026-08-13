# Internal Auth API Contract v0.1

Stand: 13.08.2026

Status: Implementierungsvertrag auf Grundlage des freigegebenen ADR 0003. Die
Endpunkte werden erst mit dem Datenbank-Repository umgesetzt; der aktuelle
FastAPI-Grundrahmen stellt nur Healthchecks und Sicherheitsprimitive bereit.

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

### `POST /api/v1/auth/mfa/totp/verify`

Request: `code`; Pre-Auth-Cookie und CSRF-Header erforderlich. Erfolg: `204`,
Pre-Auth-Cookie wird geloescht, ein rotiertes Session-Cookie gesetzt und das
neue Session-CSRF-Token einmalig im Response-Header `X-CSRF-Token` geliefert.
Fehler: generisches `401`; abgelaufene Challenge: `401`; Rate Limit: `429`.

### `POST /api/v1/auth/mfa/totp/enrollment`

Nur fuer eine gueltige Challenge mit `mfa_enrollment_required`. Erzeugt ein
verschluesseltes, noch nicht aktiviertes TOTP-Credential und liefert einmalig
eine `otpauth`-URI. Antwort: `201`, `no-store`.

### `POST /api/v1/auth/mfa/totp/enrollment/confirm`

Request: erster TOTP-Code. Erfolg aktiviert TOTP, erzeugt einmalig anzuzeigende
Recovery-Codes und schliesst die MFA-Challenge ab. Ein nicht bestaetigtes Secret
gewaehrt keinen Portalzugang.

### `GET /api/v1/auth/session`

Erfordert eine aktive MFA-Sitzung. Antwort: interne Benutzer-ID, Anzeigename,
explizite Rollen, Authentisierungszeit und Ablaufzeiten. Keine Passwort-, Token-
oder TOTP-Felder.

### `DELETE /api/v1/auth/session`

Widerruft die aktuelle Sitzung idempotent und loescht das Cookie. Antwort:
`204`, auch wenn die Sitzung bereits ungueltig ist.

### `DELETE /api/v1/auth/sessions`

Widerruft alle eigenen Sitzungen. Aktive Sitzung und CSRF-Header erforderlich.
Antwort: `204`.

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
