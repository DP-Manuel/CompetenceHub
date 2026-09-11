# CAL-1 Migration Decision Gate

Stand: 11.09.2026

Zweck: technische Restentscheidungen vor dem Entwurf von Migration `0005`.
Die Empfehlungen erweitern nicht den fachlichen Umfang aus ADR 0007. Eine
Freigabe autorisiert nur die lokale SQL-/Smoke-Test-Vorbereitung, nicht die
Anwendung auf Staging, Konten, Echtdaten, Nachrichten oder Produktion.

## Entscheidungspaket

| ID | Empfehlung | Begründung | Status |
| --- | --- | --- | --- |
| CAL-T01 | Entwürfe dürfen sich überschneiden; Absenden und Veröffentlichen werden bei Überschneidung desselben Coaches abgewiesen. Direkt anschließende Termine sind erlaubt. | Coaches können Varianten vorbereiten, ohne versehentlich doppelt verbindlich verfügbar zu erscheinen. Parallele Termine verschiedener Coaches bleiben erlaubt. | Freigabe Manuel offen |
| CAL-T02 | Pilotformate sind `online`, `praesenz` und `hybrid`; die Oberfläche zeigt deutsche Bezeichnungen. | Kleiner kontrollierter Katalog ohne Freitext; spätere Erweiterung bleibt möglich. | Freigabe Manuel offen |
| CAL-T03 | Kapazität liegt zwischen 1 und 500; Prüfschwelle zwischen 1 und Kapazität. Titel 160, Kurzbeschreibung 1.200, öffentlicher Ort 200 und Preishinweis 200 Zeichen. | Technische Missbrauchs-/Fehlergrenzen, ohne den bestätigten Wert 25 hart zu codieren. Eine unerreichbare Schwelle oberhalb der Kapazität wird verhindert. | Freigabe Manuel offen |
| CAL-T04 | Rücknahme eines veröffentlichten Angebots entfernt es sofort aus der öffentlichen Ansicht und schreibt Audit. Benachrichtigungen folgen erst mit CAL-2/CAL-4. | Verhindert weitere Interessen an einem nicht mehr verfügbaren Termin, ohne vorzeitig Mail-/Buchungslogik einzubauen. | Freigabe Manuel offen |
| CAL-T05 | Im Pilot keine harte Löschung. Review-Notizen sind optional, intern, maximal 1.000 Zeichen; echte Aufbewahrung/Löschung bleibt bis Legal geklärt und Echtdaten bleiben gesperrt. | Revisions- und Freigabenachweis bleibt konsistent, ohne eine unbelegte rechtliche Frist zu erfinden. | Freigabe Manuel offen |
| CAL-T06 | Neue additive Rolle `calendar_reviewer`; im Pilot nur durch Admin zuweisbar. `internal` allein darf nicht veröffentlichen. | Least Privilege und spätere Vertretung mit eigenem Konto; Janays Name wird nicht technisch fest verdrahtet. | Freigabe Manuel offen |

## Antwortformat

Bei Zustimmung genügt:

`CAL-T01 bis CAL-T06 freigegeben.`

Änderungen können direkt mit ID genannt werden. Erst danach wird Migration
`0005` samt Rollback-Smoke lokal entworfen und zur separaten Staging-Freigabe
vorgelegt.
