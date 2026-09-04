# Standard für Competence-Hub-Wochenupdates

## Zweck und Zielgruppe

Das Wochenupdate ist ein direkt in Microsoft Teams einsetzbarer Kurzbericht für Kolleginnen und Kollegen. Es zeigt Fortschritt, Qualität, Status und nächste Schritte, ohne technische Projektdokumentation zu ersetzen.

## Verbindliches Format

1. Titel: `Wochenupdate Competence Hub | TT.MM. bis TT.MM.JJJJ`
2. Begrüßung: `Hallo zusammen, hier das kurze Wochenupdate zum Competence Hub:`
3. `Fortschritt`: höchstens fünf Aufzählungspunkte
4. `Qualitätsstand`: höchstens drei Aufzählungspunkte
5. `Status`: höchstens drei Aufzählungspunkte
6. `Nächste Schritte`: höchstens vier Aufzählungspunkte

## Schreibregeln

- Jeder Aufzählungspunkt besteht aus genau einem kurzen Satz und steht in der Quelldatei in einer Zeile.
- Richtwert sind höchstens 120 Zeichen pro Punkt; unvermeidbare Eigennamen dürfen den Wert geringfügig überschreiten.
- Keine Unterpunkte, Commit-IDs, Befehle, internen Fehlerverläufe oder nicht entscheidungsrelevanten Implementierungsdetails.
- Ergebnisse werden aus Sicht der Kolleginnen und Kollegen beschrieben: sichtbarer Nutzen vor technischer Umsetzung.
- Offene externe Abhängigkeiten, Produktionsstatus und Umgang mit realen Daten werden immer ehrlich genannt.
- Nur belegte Ergebnisse aufnehmen; geplante Arbeiten gehören ausschließlich unter `Nächste Schritte`.
- Bei einem Zeitraum über sieben Tage bleibt dasselbe Format bestehen; der genaue Zeitraum steht im Titel.

## Vorlage

```text
**Wochenupdate Competence Hub | TT.MM. bis TT.MM.JJJJ**

Hallo zusammen, hier das kurze Wochenupdate zum Competence Hub:

**Fortschritt**
- [Wichtigstes sichtbares Ergebnis]

**Qualitätsstand**
- [Wichtigster Qualitätsnachweis]

**Status**
- [Ampel, Termin oder zentrale Abhängigkeit]

**Nächste Schritte**
- [Nächster konkreter Schritt]
```

## Ablage

Fertige Updates werden unter `docs/updates/wochenupdate-JJJJ-MM-TT.md` gespeichert. Vor dem Versand werden Zeitraum, Einzeiligkeit, Abschnittsgrenzen, Produktionsstatus und Real-Daten-Aussage geprüft.
