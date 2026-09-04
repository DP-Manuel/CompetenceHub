# Wochenupdate Competence Hub

Zeitraum: 22.08. bis 04.09.2026

Hallo zusammen,

hier das kurze Wochenupdate zum Competence Hub:

## Diese Woche abgeschlossen

- Der externe Backup- und Wiederherstellungsweg für die PostgreSQL-Datenbank
  wurde vollständig erprobt. Ein verschlüsseltes Backup wurde auf den
  BitLocker-geschützten Würzburger Datenträger übertragen und aus genau dieser
  Kopie zweimal erfolgreich in einer isolierten Umgebung wiederhergestellt.
- Der Backup-Datenträger wird im Safe aufbewahrt; Janay ist als
  Notfallverantwortliche benannt. Passwörter, Wiederherstellungscodes und
  private Schlüssel wurden nicht in das Projekt übernommen.
- Die technische Readiness-Prüfung für Website und Portal wurde aktualisiert.
  Releasepakete, Prüfsummen, Backupkontrolle und Rückfallwege sind reproduzierbar
  vorbereitet.
- Die Website wurde anhand des letzten internen Feedbacks weiter überarbeitet.
  Unter anderem sind die Angebotsstruktur, Mindforge-Navigation, FAQ-Darstellung,
  Abstände und die interaktiven Themenbereiche klarer und ruhiger geworden.
- Auf der Unternehmensseite gibt es jetzt zwei anschauliche Anwendungswege, die
  den möglichen Ablauf einer Zusammenarbeit Schritt für Schritt zeigen.
- Das freigegebene Feedback von Concept Clean wurde als eigener Bereich für
  Kundenstimmen sichtbar eingebunden. Logo, Thema der Zusammenarbeit und ein
  kurzes Zitat sind so aufgebaut, dass später weitere Kundenstimmen ergänzt
  werden können.
- Für die fünf wichtigsten Seiten wurden eine Inhaltsübersicht und eine
  Quellen-/Evidenzmatrix erstellt. Damit ist dokumentiert, welche Zielgruppen,
  Anwendungsfälle, fachlichen Informationen und Handlungsaufforderungen bereits
  vorhanden sind und wo noch Entscheidungen fehlen.
- Für diese offenen Inhaltsentscheidungen liegt ein kompaktes Abstimmungspaket
  als Word- und PDF-Datei vor.
- Das technische Website-Paket für den späteren IONOS-Webspace ist vorbereitet,
  einschließlich Prüfsumme, Fehlerseite, Sicherheitsgrundlagen und Rückfallweg.

## Qualitätsstand

- 305 automatisierte Webapp-Tests sind erfolgreich; die zusätzlichen
  Staging-Prüfungen bleiben bewusst an eine kontrollierte Verbindung gebunden.
- Die aktuelle Website-Prüfung läuft ohne Fehler, Warnungen oder Hinweise durch.
- 29 statische Seiten werden erfolgreich erzeugt.
- Desktop- und Mobilansichten wurden geprüft; bei 390 Pixel Breite besteht kein
  horizontaler Überlauf.
- Die aktuelle Review-Version ist online, aber weiterhin für Suchmaschinen
  gesperrt.
- Es wurden keine echten Firmen- oder Personendaten verwendet.

## Aktueller Status

Der sichtbare Website-Stand ist gut vorangekommen und kann intern weiter geprüft
werden. Die Produktionsampel bleibt bewusst auf Gelb, weil der endgültige
Webspace-Zugang, Mailversand, rechtliche Angaben und interne Freigaben noch offen
sind. Ein erster kleiner kontrollierter Start ist derzeit frühestens für die
zweite Oktoberhälfte vorgesehen.

## Noch offen

- Die EDV muss das fehlende SFTP-Startverzeichnis beziehungsweise den korrekten
  Document Root auf dem IONOS-Webspace bereitstellen.
- Der automatische produktive Backup-Zeitplan und der Alarmierungsweg müssen
  vor der Verarbeitung echter Daten noch freigegeben werden.
- App-Domain, SMTP-/Mailversand und Kontaktformular müssen abschließend technisch
  bestätigt und getestet werden.
- Für die fünf Kernseiten stehen noch einige fachliche Entscheidungen und
  Zuständigkeiten aus.
- Betreiberangabe, Impressum und rechtliche Freigabe sind noch nicht final.
- Janays Abnahme, die ersten namentlichen Portalzugänge und der spätere
  Go/No-Go-Termin müssen noch abgestimmt werden.

## Als Nächstes

- kleine optische Korrektur an den Anführungszeichen der Kundenstimme
- Abstimmungspaket für die Kernseiten versenden und Rückmeldungen einarbeiten
- EDV-Rückmeldung ab dem 14.09. nachhalten
- nach Korrektur des SFTP-Zugangs zunächst eine rein lesende Webroot-Prüfung
  durchführen
- anschließend Upload, Mailversand und Rückfallweg ohne echte Kundendaten
  kontrolliert proben

Wichtig: Die IONOS-Produktionsseite und das interne Portal sind noch nicht
produktiv geschaltet. Es gab keinen produktiven Mailversand und keine
Verarbeitung realer Kundendaten.
