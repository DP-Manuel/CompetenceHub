# ADR 0003 - Interne Authentifizierung und Sitzungsmodell

Stand: 13.08.2026

## Status

Accepted by Manuel on 2026-08-13. Die Freigabe erlaubt den lokalen
Implementierungsslice mit ausschliesslich synthetischen Daten, aber keine
Serverinstallation, Mailanbindung, Echtdaten oder Deploymentfreigabe.

## Kontext

Der erste authentifizierte Competence-Hub-Slice richtet sich ausschliesslich an
interne Benutzer mit den Arbeitsrollen `admin` und `internal`. Coach-, Firmen-
und Teilnehmerzugriffe folgen spaeter als eigene Sicherheits- und
Anforderungsslices.

Die statische Website liegt auf dem IONOS-Webspace. Das spaetere FastAPI-
Backend und PostgreSQL laufen getrennt auf dem vorhandenen VPS. PostgreSQL ist
nur lokal erreichbar. Migration `0001` stellt ein leeres Portal-Kernschema mit
Mehrfachrollen bereit; Authentifizierungsdaten und Sitzungen sind noch nicht
modelliert.

Es wird kein externer Identity-Provider eingefuehrt. Der erste interne Slice
muss mit wenigen Konten sicher, wartbar und ohne dauerhafte Tokens im Browser
betrieben werden koennen.

## Entscheidung

### Identitaet und Einstieg

- Interne Konten werden nur durch berechtigte Administratoren eingeladen. Es
  gibt keine Selbstregistrierung und keine Standard- oder Demo-Zugangsdaten.
- E-Mail-Adresse und Passwort bilden den ersten Faktor. E-Mail-Adressen werden
  kanonisiert und eindeutig gespeichert.
- Der erste Administrator wird einmalig ueber einen interaktiven, auditierten
  Server-/CLI-Vorgang angelegt. Zugangsdaten stehen weder in Migrationen noch
  in Git, Logs oder Shell-Argumenten.
- Passwoerter werden mit Argon2id und einer etablierten Bibliothek gehasht.
  Eigene Kryptografie ist ausgeschlossen.
- Passwoerter haben mindestens 12 und duerfen mindestens 128 Zeichen haben.
  Leerzeichen und Passphrasen sind erlaubt. Es gibt keine starren
  Zeichenklassenregeln und keinen turnusmaessigen Wechsel ohne konkreten
  Sicherheitsanlass. Ein lokaler Block gegen verbreitete/kompromittierte
  Passwoerter ist verpflichtend; die Pruefung sendet kein Passwort an einen
  externen Dienst.

### Sitzungen

- Der Browser erhaelt eine zufaellige, opaque Sitzungskennung mit mindestens
  256 Bit Entropie. In PostgreSQL wird nur ein kryptografischer Hash dieser
  Kennung gespeichert.
- Die Sitzungskennung wird ausschliesslich in einem Host-only-Cookie
  `__Host-competence_hub_session` transportiert: `Secure`, `HttpOnly`,
  `SameSite=Lax`, `Path=/`, ohne `Domain`.
- App-Oberflaeche und API werden hinter derselben App-Origin bereitgestellt;
  API-Aufrufe laufen unter einem Pfad wie `/api`. Das vermeidet fuer den ersten
  Slice Cross-Origin-Cookies und eine breite CORS-Freigabe.
- Sitzungen laufen nach 30 Minuten Inaktivitaet und spaetestens nach 8 Stunden
  ab. Die Werte sind serverseitig konfigurierbar; es gibt kein dauerhaftes
  "Angemeldet bleiben".
- Die Sitzungskennung wird nach Login, erfolgreicher MFA, Passwortaenderung und
  sicherheitsrelevanter Rechteaenderung rotiert.
- Nutzer koennen die aktuelle oder alle eigenen Sitzungen beenden. Deaktivierung,
  Passwort-Reset und sicherheitsrelevante Rollenentziehung widerrufen alle
  Sitzungen des Kontos.

### CSRF, Browser- und API-Schutz

- Jede zustandsaendernde Browseranfrage benoetigt neben dem Cookie ein
  sitzungsgebundenes CSRF-Token. Der Server prueft zusaetzlich `Origin` und,
  falls erforderlich, `Referer` gegen eine enge Allowlist.
- `GET`, `HEAD` und `OPTIONS` veraendern keine Fachdaten.
- Authentifizierte Antworten tragen mindestens `Cache-Control: no-store` und
  werden nicht durch Service Worker oder Shared Caches gespeichert.
- Eine enge Content-Security-Policy, `frame-ancestors`, MIME-Sniffing-Schutz und
  weitere Security-Header werden am Reverse Proxy beziehungsweise Backend
  zentral gesetzt.
- Fehlermeldungen bei Login, Einladung und Reset verraten nicht, ob ein Konto
  existiert, aktiv ist oder welche Rolle es besitzt.

### MFA und erneute Authentisierung

- TOTP ist der erste zweite Faktor, weil es ohne externen Provider betrieben
  werden kann. SMS und E-Mail gelten nicht als zweiter Faktor.
- MFA ist fuer `admin` und `internal` vor Produktivbetrieb mit echten Daten
  verpflichtend. Ein rein synthetischer lokaler Entwicklungsmodus darf MFA
  explizit deaktivieren; Staging und Produktion duerfen diesen Schalter nicht
  akzeptieren.
- Einmalige Recovery-Codes werden nur als schluesselgebundener HMAC-Digest
  gespeichert, bei Verwendung verbraucht und nie erneut vollstaendig angezeigt.
- Das fuer TOTP technisch wieder benoetigte Secret wird mit einem ausserhalb
  der Datenbank gehaltenen Schluessel authentifiziert verschluesselt. Es steht
  nie im Klartext in Datenbank, Logs, Backups ausserhalb deren Verschluesselung
  oder API-Antworten.
- Passwort- oder MFA-Reset, Adminrollenvergabe, Export und andere besonders
  privilegierte Aktionen verlangen eine frische Authentisierung. Das konkrete
  Reauth-Fenster wird im Backend konfiguriert und standardmaessig auf 10 Minuten
  gesetzt.
- WebAuthn/Passkeys koennen TOTP spaeter ergaenzen oder ersetzen, sind aber kein
  Gate fuer den ersten internen Slice.

### Einladung und Reset

- Einladungs- und Reset-Token sind zufaellig, einmalig, kurzlebig und nur
  gehasht gespeichert. Baseline: Einladung 24 Stunden, Reset 30 Minuten.
- Ein neues Token widerruft aeltere offene Tokens desselben Typs. Erfolgreiche
  Nutzung, Deaktivierung oder Ablauf macht das Token unbrauchbar.
- Reset und erstmalige Passwortsetzung erfolgen ausschliesslich ueber HTTPS.
- E-Mail-Versand ist eine getrennte Integration. Bis zur freigegebenen
  Mailanbindung duerfen Links in einem lokalen synthetischen Testmodus nur
  kontrolliert angezeigt, aber nie in Produktionslogs geschrieben werden.

### Rate Limits und Missbrauchsschutz

- Login, Einladung, Reset und MFA-Pruefung erhalten serverseitige Rate Limits
  auf Konto- und IP-Basis. Als Startwert gelten maximal fuenf Fehlversuche in
  15 Minuten mit progressiver Verzoegerung; Werte bleiben konfigurierbar.
- Konto-/IP-Buckets werden normalisiert und mit einem ausserhalb der Datenbank
  gehaltenen HMAC-Schluessel pseudonymisiert. Ein einfacher Hash niedriger
  Entropie ist unzureichend.
- Rate Limits ersetzen keine generischen Antworten und duerfen kein
  Konto-Enumerationssignal erzeugen.
- Wiederholte Fehler und administrative Aufhebungen werden datensparsam
  auditiert. Passwoerter, Token, Cookies, TOTP-Secrets und vollstaendige
  Request-Payloads werden nie protokolliert.

### Autorisierung und privilegierte Rollen

- Authentifizierung identifiziert den Benutzer; jede API-Aktion prueft danach
  serverseitig Rolle, Datensatzscope und explizite Policy deny-by-default.
- UI-Ausblendung ist keine Autorisierung.
- Nur `admin` darf die Rolle `admin` vergeben oder entziehen sowie Adminkonten
  deaktivieren. Diese Aktionen verlangen MFA und frische Authentisierung.
- `internal` darf niemals sich selbst oder andere zu `admin` machen. Eine
  spaetere Verwaltung nicht privilegierter Rollen durch `internal` benoetigt
  eine explizite Policy und eigene Tests.
- Ein Benutzer darf die eigene letzte wirksame Adminberechtigung nicht
  entfernen. Ein Break-glass-/Nachfolgeprozess bleibt vor Produktion zu
  dokumentieren.

### Secret- und Betriebsmodell

- Laufzeitsecrets liegen ausserhalb des Repositories in einer nur fuer den
  dedizierten Competence-Hub-Systembenutzer lesbaren Konfigurationsdatei,
  Zielmodus `0600`. Der konkrete Pfad wird im Deployment-Runbook festgelegt.
- Chatbot und Competence Hub teilen weder Systembenutzer noch Secrets,
  Datenbankrollen, Konfigurationsdateien oder Sitzungen.
- Staging und Produktion verwenden getrennte Schluessel, Cookies, Datenbanken
  und Origins. Ein Staging-Cookie ist in Produktion ungueltig und umgekehrt.
- Schluesselrotation und Notfallwiderruf muessen ohne Datenbankneuanlage
  moeglich sein. Aktive Sitzungen duerfen bei einem Vorfall global widerrufen
  werden.

## Vorgesehene technische Bausteine

Eine spaetere Migration soll getrennte Tabellen fuer folgende Zwecke anlegen:

- Passwort-Credentials je Portalbenutzer
- serverseitige Sitzungen mit Hash, Ablauf und Widerruf
- einmalige Einladungs-/Reset-Token
- TOTP-Credential und Recovery-Codes

Die genauen Tabellen und API-Vertraege entstehen im Implementierungsslice.
Token und Session-ID duerfen nie im Klartext persistiert werden. TOTP-Secrets
werden authentifiziert verschluesselt; Recovery-Codes und niedrig-entropische
Rate-Limit-Identifier werden mit einem extern geschuetzten HMAC-Schluessel
pseudonymisiert.

## Abgelehnte Alternativen

### JWT in Local Storage

Abgelehnt fuer den ersten Browser-Slice: langlebige Client-Tokens erschweren
Widerruf und erhoehen bei XSS das Expositionsrisiko, ohne fuer wenige interne
Konten einen Nutzen zu liefern.

### Externer Identity-Provider

Zurueckgestellt: derzeit nicht freigegeben und fuer den kleinen internen Pilot
operativ unverhaeltnismaessig. Eine spaetere D+P-SSO-Entscheidung bleibt
moeglich.

### HTTP Basic Auth oder geteilte Konten

Abgelehnt: keine individuelle Rollensteuerung, kein belastbarer Lifecycle und
keine ausreichende Auditierbarkeit.

### Firmen- und Coachlogin im ersten Slice

Abgelehnt fuer Phase 1: externe Identitaeten, Einladungen, Support, Datenschutz
und Scopes vergroessern die Angriffs- und Prozessflaeche erheblich. Sie folgen
nach einem stabilen internen Pilot.

## Konsequenzen

- Vor Login-Code ist keine weitere Produktentscheidung erforderlich; die
  konkrete Python-Bibliotheksauswahl wird im Implementierungsslice gegen
  Wartbarkeit und aktuelle Sicherheit geprueft.
- Das bestehende `portal_users`-Modell bleibt Identitaetsstamm; Auth-Credentials
  werden separat gehalten.
- Die bisherige RBAC-Aussage "Intern darf Rollen zuweisen" wird sicher
  eingeschraenkt: niemals Adminrolle oder Adminkonten ohne Adminpolicy.
- Eine eigene App-Origin und ein Reverse-Proxy-Pfad fuer die API werden Teil des
  spaeteren Staging-Deployments.
- Reale Unternehmens- oder Personendaten bleiben bis Off-Server-Restore,
  Retention/Loeschung und Betriebsfreigabe gesperrt.

## Offene Betriebsentscheidungen

- Benennung der finalen App-Origin, beispielsweise
  `app.competencehub.donner-partner.de`
- kontrollierte Mailanbindung fuer Einladung und Reset
- zweiter Notfall-/Nachfolgeadmin und Break-glass-Aufbewahrung
- konkrete Aufbewahrungsdauer von Auth- und Auditereignissen

Diese Punkte blockieren die lokale Implementierung mit synthetischen Daten
nicht, aber den Produktivbetrieb.

## Referenzen

- OWASP Session Management Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html>
- OWASP Password Storage Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html>
- OWASP CSRF Prevention Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html>
- OWASP Multifactor Authentication Cheat Sheet:
  <https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html>
