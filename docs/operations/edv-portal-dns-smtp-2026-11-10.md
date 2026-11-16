# Versandfertige EDV-Anfrage

Status16.11.2026: zum Nachfassen aktualisiert, nicht durch die KI versendet.
Manuel bestätigt ausdrücklich: noch keine EDV-Rückmeldung; die gegenteilige
Auswahl war ein Verklicken. Hostname unten bleibt ein Vorschlag, keine Freigabe.
DNS-A-Abfrage10.11 war negativ; heute wurde keine neue DNS-Abfrage ausgeführt.

## Betreff

Competence Hub: Portaladresse und Einladungsversand für den Benutzerstart

## Nachricht

Hallo Herr Roß,

unser geschützter Competence-Hub-Pilot läuft erfolgreich auf dem VPS und Janay
hat den Kalenderablauf inzwischen fachlich freigegeben. Anmeldung und Rollen
sind mit Testkonten geprüft. Die öffentliche Website bleibt unverändert bei IONOS.

Für die ersten persönlichen Zugänge fehlen uns noch zwei Punkte:

**1. Eine eigene Portaladresse**

Als Vorschlag hatten wir `competencehub-app.donner-partner.de` vorgesehen.
Können Sie diesen Namen bestätigen und den A-Record auf `217.160.255.86` setzen?
Bitte direkt auf den VPS, nicht auf den Website-Webspace oder eine Weiterleitung.
Einen AAAA-Record bitte nur bei tatsächlich freigegebenem IPv6 setzen.

Bitte bestätigen Sie außerdem, ob ein automatisch erneuertes Let's-Encrypt-
Zertifikat auf dem VPS zulässig ist und ob DNS-/CAA-Vorgaben zu beachten sind.
Die technische Einrichtung übernehmen wir anschließend kontrolliert neben den
bestehenden Diensten. Für eine zunächst eingeschränkte Staging-Freigabe benötigen
wir die dafür vorgesehenen Zugriffsregeln beziehungsweise bestätigten Quell-IP-
Adressen; bitte keine allgemeine öffentliche Freischaltung vornehmen.

**2. E-Mail-Zustellung für Einladungen und Passwort-Reset**

Benötigt werden SMTP-Server, Port, TLS-Vorgabe, technische Versandidentität,
zulässige Absender-/Antwortadresse und die Bestätigung, dass dieser VPS senden
darf. Bitte auch Versandlimits und die Abdeckung durch SPF/DKIM/DMARC bestätigen.
Ein SMTP-Passwort bitte nicht per normaler E-Mail senden; dafür stimmen wir einen
separaten sicheren Übergabeweg ab. Solange das nicht geklärt ist, versenden wir
keine echten Einladungen und verwenden keinen Ersatzversand.

Unser aktuelles Zertifikat für den geschützten Testzugang gilt nur bis zum
**24.11.2026**. Können Sie uns bitte zeitnah den Stand beziehungsweise die noch
fehlenden Angaben mitteilen? Falls die Einrichtung länger dauert, hilft uns
bereits ein verbindlicher Ansprechpartner mit einem realistischen Termin.

Vielen Dank und viele Grüße

Manuel Rödel

## Technische Umsetzungsgrenze

Bis zur bestätigten Domain/TLS-/Zugriffsfreigabe nur vorhandenes privates
SSH/HTTPS verwenden. Keine DNS-, Firewall-, Zertifikats- oder Nginx-Änderung durch
diese Vorbereitung. Kandidat: eigener Host-Serverblock auf vorhandenem443,
Same-Origin `/portal` und `/api`, bestehendes Loopback-Backend; kein offener8001
oder PostgreSQL-Port. HTTP-01 benötigt erreichbaren80 für die ACME-Challenge,
nicht eine öffentlich freigegebene Portaloberfläche. Erneuerung und geschützter
Zugriff müssen tatsächlich geprüft werden, bevor normale Benutzer eingeladen
werden. [Let's Encrypt Challenge-Dokumentation](https://letsencrypt.org/docs/challenge-types/),
[Nginx Proxy-Header](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header).
