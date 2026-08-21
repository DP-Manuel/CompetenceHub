# EDV-Anfrage: App-DNS und SMTP

Stand: 21.08.2026

Status: Am 21.08.2026 an die EDV versendet; Antwort ausstehend.

## Betreff

Technische Angaben fuer Competence-Hub-Portal: App-DNS und SMTP

## Nachricht

Hallo Herr Roß,

fuer den naechsten technischen Schritt beim Competence Hub benoetige ich bitte
noch die DNS- und SMTP-Rahmendaten. Die oeffentliche Website bleibt auf
`https://competencehub.donner-partner.de`. Das geschuetzte Portal mit Login,
Einladungen und Passwort-Zuruecksetzung soll getrennt auf dem bereits von mir
verwalteten VPS laufen.

Koennten Sie bitte folgende Punkte pruefen beziehungsweise bestaetigen?

**1. DNS fuer Portal und API**

- Gewuenschter Hostname: `competencehub-app.donner-partner.de`
- Bitte einen A-Record auf die oeffentliche IPv4-Adresse des bestehenden VPS
  vorbereiten. Die Ziel-IP kann ich bei Bedarf getrennt mitteilen.
- Einen AAAA-Record bitte nur setzen, wenn IPv6 fuer den VPS tatsaechlich
  eingerichtet und freigegeben ist.
- Der Hostname soll direkt auf den VPS zeigen und nicht auf den IONOS-Webspace
  oder eine Weiterleitung.
- Kann das TLS-Zertifikat auf dem VPS automatisiert per Let's Encrypt
  ausgestellt und erneuert werden? Bitte auch kurz bestaetigen, ob bestehende
  DNS-/CAA-Vorgaben dem entgegenstehen.

**2. SMTP fuer Systemnachrichten**

Das Portal versendet ausschliesslich transaktionale Nachrichten wie
Einladungen und Links zum Zuruecksetzen eines Passworts. Bitte teilen Sie mir
dafuer mit:

- SMTP-Hostname und Port;
- vorgeschriebener TLS-Modus, bevorzugt STARTTLS oder alternativ implizites
  TLS;
- Authentifizierungs-Benutzername beziehungsweise technische Identitaet;
- ob der Versand vom bestehenden VPS erlaubt ist;
- erlaubte Absenderadresse und gegebenenfalls Versand-/Rate-Limits;
- ob SPF, DKIM und DMARC fuer diesen Absender bereits korrekt abgedeckt sind.

Als Systemabsender schlage ich `portal@donner-partner.de` vor. Antworten sollen
ueber `Reply-To: competencehub@donner-partner.de` bei der betreuten
Kontaktadresse landen. Falls ein anderer technischer Absender vorgesehen ist,
bitte ich um eine kurze Empfehlung.

Ein SMTP-Passwort bitte nicht per normaler E-Mail senden. Dafuer stimmen wir
anschliessend einen getrennten sicheren Uebergabeweg ab.

**3. Adressrouting**

- Bitte bestaetigen, dass `competencehub@donner-partner.de` eingerichtet ist
  und an Janay Rappelt beziehungsweise `rappelt.wue@donner-partner.eu`
  zugestellt wird.
- Fuer technische Meldungen ist
  `admin@competencehub.donner-partner.de` mit Weiterleitung an
  `roedel.kg@donner-partner.eu` vorgesehen. Falls Adressen unter dieser
  Subdomain nicht unterstuetzt werden, waere
  `competencehub-admin@donner-partner.de` eine passende Alternative.

Die Angaben werden zunaechst nur fuer Konfiguration und einen synthetischen
Abnahmetest verwendet. Eine produktive Freischaltung oder Verarbeitung realer
Firmen- und Personendaten erfolgt erst nach separatem Go/No-Go.

Vielen Dank und viele Gruesse

Manuel Rödel
