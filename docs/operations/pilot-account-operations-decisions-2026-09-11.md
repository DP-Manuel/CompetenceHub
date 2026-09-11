# Pilot-Zugangs- und Betriebsentscheidungen

Stand: 11.09.2026

Status: Grundentscheidungen durch Manuel bestaetigt; Aktivierung und Echtdaten
bleiben hinter den bestehenden Produktionsgates.

## Entscheidungen

| ID | Bereich | Entscheidung | Status / Folgegate |
| --- | --- | --- | --- |
| OPS-D01 | Erstes Adminkonto | Manuel nutzt seine persoenliche D+P-Adresse mit Rolle `admin`. | bestaetigt; Konto wird erst im kontrollierten Onboarding angelegt |
| OPS-D02 | Erstes internes Konto | Janay nutzt ihre persoenliche D+P-Adresse mit Rolle `internal`. | bestaetigt; Konto wird erst im kontrollierten Onboarding angelegt |
| OPS-D03 | Technischer Notfallzugriff | Thomas Ross wird als Break-glass-/Nachfolgeadmin vorgesehen, falls Manuel nicht verfuegbar ist. | bestaetigt; konkreter sicherer Einrichtungs-, Aufbewahrungs- und Testweg bleibt vor Produktion nachzuweisen |
| OPS-D04 | Funktionsmailbox | Janay ist Ownerin. Fuer Janays Abwesenheit ist derzeit keine Vertretung benannt; Manuel wird waehrend seines Urlaubs nicht vertreten. Thomas' Notfallrolle deckt nur technische Notfaelle ab. | bekannte Betriebsluecke; keine oeffentliche Reaktionszeit versprechen |
| OPS-D05 | Backup-Zeitplan | Verschluesseltes Backup taeglich um 02:15 UTC mit bis zu 15 Minuten Zufallsverzoegerung; Integritaets-/Frischepruefung um 08:00 UTC mit bis zu 10 Minuten Zufallsverzoegerung. | fachlich bestaetigt; Timeraktivierung bleibt separater VPS-Aenderungsschritt |
| OPS-D06 | Aufbewahrung | Vorerst 30 taegliche und 12 monatliche verschluesselte Sicherungssaetze. | als Pilotwert bestaetigt; Datenschutz-/Legal-Pruefung vor Echtdaten bleibt erforderlich |
| OPS-D07 | Benachrichtigung | Manuel erhaelt nach der automatischen Pruefung eine kurze Meldung ueber Erfolg oder Vorkommnisse. Der Kanal darf E-Mail oder ein spaeter freigegebener gleichwertiger Weg sein. | Anforderung bestaetigt; aktiver Kanal und Testzustellung warten auf EDV-/SMTP-Eingaben |
| OPS-D08 | Notfall- und Recovery-Verantwortung | Janay bleibt fuer den Backup-Notfall benannt; BitLocker-Recovery-Code und GPG-Passphrase sind sicher hinterlegt. | bestaetigt; keine Secrets im Repository |
| OPS-D09 | Onboarding / Go-No-Go | Bevorzugter Termin ist 17.09.2026, Ausweichtermin 24.09.2026, sofern die dafuer erforderlichen Gates rechtzeitig schliessen. | Terminanfrage/-bestaetigung offen; kein stillschweigendes Go-Live |

## Betriebsgrenze

- Die fehlende Mailboxvertretung wird nicht mit der technischen
  Break-glass-Rolle vermischt.
- Ein erfolgreicher Journaleintrag allein reicht fuer den spaeteren
  Produktivbetrieb nicht; der Benachrichtigungskanal muss einen Erfolgs- und
  einen synthetischen Fehlerfall nachweislich zustellen.
- Timer, reale Konten, produktive E-Mails und Echtdaten werden durch dieses
  Dokument nicht aktiviert.

## Noch offen

1. Sicherer Einrichtungs- und Testtermin fuer Thomas' Break-glass-Zugang.
2. Vertretungsregel fuer Janays Funktionsmailbox oder ausdrueckliche
   Akzeptanz eines Betriebs ohne Vertretung.
3. EDV-bestaetigter Benachrichtigungskanal samt Absender und Testempfaenger.
4. Bestaetigung des 17.09. oder 24.09. fuer Onboarding und Go/No-Go.

## Abnahmebeweis vor Echtdaten

- Thomas' Notfallzugriff wird mit persoenlicher Identitaet, MFA, Least
  Privilege und protokolliertem Test nachgewiesen.
- Backup und Monitor laufen automatisiert; Manuel erhaelt eine knappe
  Erfolgsmeldung sowie eine absichtlich ausgeloeste Fehlermeldung.
- Janay und Manuel bestehen den beaufsichtigten Login-/MFA-Smoke.
- Offene Vertretungs- und Reaktionsgrenzen sind im Go/No-Go sichtbar.
