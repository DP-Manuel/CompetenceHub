# CAL-1 Migration Decision Gate

Stand: 11.09.2026

Zweck: dokumentierte technische Entscheidungen fuer Migration `0005`.
Manuel hat CAL-T01 bis CAL-T06 am 11.09.2026 freigegeben. Die Freigabe
autorisiert nur die lokale SQL-/Smoke-Test-Vorbereitung, nicht die Anwendung
auf Staging, Konten, Echtdaten, Nachrichten oder Produktion.

## Entscheidungspaket

| ID | Empfehlung | Begründung | Status |
| --- | --- | --- | --- |
| CAL-T01 | Entwürfe dürfen sich überschneiden; Absenden und Veröffentlichen werden bei Überschneidung desselben Coaches abgewiesen. Direkt anschließende Termine sind erlaubt. | Coaches können Varianten vorbereiten, ohne versehentlich doppelt verbindlich verfügbar zu erscheinen. Parallele Termine verschiedener Coaches bleiben erlaubt. | Freigegeben 11.09.2026 |
| CAL-T02 | Pilotformate sind `online`, `praesenz` und `hybrid`; die Oberfläche zeigt deutsche Bezeichnungen. | Kleiner kontrollierter Katalog ohne Freitext; spätere Erweiterung bleibt möglich. | Freigegeben 11.09.2026 |
| CAL-T03 | Kapazität liegt zwischen 1 und 500; Prüfschwelle zwischen 1 und Kapazität. Titel 160, Kurzbeschreibung 1.200, öffentlicher Ort 200 und Preishinweis 200 Zeichen. | Technische Missbrauchs-/Fehlergrenzen, ohne den bestätigten Wert 25 hart zu codieren. Eine unerreichbare Schwelle oberhalb der Kapazität wird verhindert. | Freigegeben 11.09.2026 |
| CAL-T04 | Rücknahme eines veröffentlichten Angebots entfernt es sofort aus der öffentlichen Ansicht und schreibt Audit. Benachrichtigungen folgen erst mit CAL-2/CAL-4. | Verhindert weitere Interessen an einem nicht mehr verfügbaren Termin, ohne vorzeitig Mail-/Buchungslogik einzubauen. | Freigegeben 11.09.2026 |
| CAL-T05 | Im Pilot keine harte Löschung. Review-Notizen sind optional, intern, maximal 1.000 Zeichen; echte Aufbewahrung/Löschung bleibt bis Legal geklärt und Echtdaten bleiben gesperrt. | Revisions- und Freigabenachweis bleibt konsistent, ohne eine unbelegte rechtliche Frist zu erfinden. | Freigegeben 11.09.2026 |
| CAL-T06 | Neue additive Rolle `calendar_reviewer`; im Pilot nur durch Admin zuweisbar. `internal` allein darf nicht veröffentlichen. | Least Privilege und spätere Vertretung mit eigenem Konto; Janays Name wird nicht technisch fest verdrahtet. | Freigegeben 11.09.2026 |

## Umsetzungsstand

Migration `0005` und der rollback-only Smoke-Test sind lokal unter
`apps/webapp/database` vorbereitet und durch drei Vertragstests abgesichert.
Die Anwendung auf Staging benoetigt eine eigene ausdrueckliche Freigabe.
