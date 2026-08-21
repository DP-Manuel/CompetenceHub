# Wochenupdate Competence Hub

Zeitraum: 17.08. bis 21.08.2026

Hallo zusammen,

hier das kurze Wochenupdate zum Competence Hub:

## Diese Woche abgeschlossen

- Das interne Pilotportal ist als durchgaengiger Prototyp umgesetzt. Es umfasst
  den geschuetzten Login mit Zwei-Faktor-Anmeldung sowie die rollenbasierte
  Anzeige und Bearbeitung von Firmen und ersten Kontaktpersonen.
- Die Portaloberflaeche wurde im Browser vollstaendig geprueft. Alle 17
  vorgesehenen Bedien- und Sicherheitsfaelle wurden erfolgreich abgenommen.
- Der Einladungsweg per E-Mail ist technisch vorbereitet. Er ist noch nicht an
  den produktiven Mailversand angeschlossen und versendet keine echten Mails.
- Fuer Website und Portal gibt es reproduzierbare Releasepakete mit Pruefsumme,
  Versionsnachweis und klaren Rueckfallwegen.
- Fuer die Datenbank wurden verschluesselte Backup-, Kontroll- und
  Wiederherstellungsablaeufe vorbereitet. Auch der spaetere Website-Upload per
  SFTP ist mit einem verpflichtenden Webspace-Backup und Rollback abgesichert.
- Eine zentrale Readiness-Uebersicht zeigt jetzt sichtbar, was erledigt,
  bereit, extern ausstehend oder bis zu einer Freigabe blockiert ist.

## Qualitaetsstand

- 304 automatisierte Tests sind erfolgreich.
- 14 weitere Tests sind erwartungsgemaess nur mit einer aktiven
  Staging-Verbindung ausfuehrbar; die entsprechenden Staging- und Browsertests
  wurden zuvor erfolgreich abgeschlossen.
- Die Website wird weiterhin fehlerfrei gebaut: 38 gepruefte Astro-Dateien und
  28 statische Seiten.
- Es wurden keine echten Firmen- oder Personendaten verwendet.

## Aktueller Status

Der technische Stand ist gut und der Produktionspfad bleibt realistisch. Die
Ampel steht trotzdem bewusst auf Gelb, weil mehrere externe Freigaben und
Betriebsnachweise noch ausstehen.

Der 28.08. ist der technische Readiness-Meilenstein. Der kontrollierte
Produktionsstart bleibt fuer spaetestens 25.09. geplant.

## Noch offen

- Rueckmeldung der EDV zu App-Domain, TLS-/Proxy-Weg und Mailversand
- externer verschluesselter Backup- und Wiederherstellungstest in Wuerzburg
- finaler Vertragsprozess
- finaler Betreiber, Impressum und rechtliche Pruefung
- Termin fuer Janays Onboarding und Thomas Ross' Go/No-Go
- Regelung fuer Mailbox-Vertretung und Reaktionsweg

## Naechste Woche

- Backup auf den kontrollierten Wuerzburger Rechner uebertragen und aus genau
  dieser externen Kopie testweise wiederherstellen
- eine eingehende EDV-Antwort direkt in die Server- und Mailkonfiguration
  ueberfuehren und pruefen
- nach gesonderter Freigabe den SFTP-Zielpfad zunaechst nur lesend erfassen
- die offenen Gates fuer den 28.08. aktualisieren und terminlich nachhalten

Wichtig: Das interne Portal ist noch nicht produktiv geschaltet. Es gab diese
Woche keinen SFTP-Upload, keinen produktiven Mailversand und keine Verarbeitung
realer Kundendaten.
