# Competence Hub

## Abstimmung zum Coach-Kalender

**Entscheidungsvorlage - Stand: 10.09.2026**

## Worum es geht

Die sichtbare Kalender-Vorschau ist fertig. Sie zeigt beispielhaft drei Monate,
Themen, Coaches, parallele Angebote und unverbindliches Interesse. Sie speichert
noch keine Daten und nimmt noch keine Buchungen an.

Bevor Coaches echte Termine pflegen und Unternehmen Plätze vormerken können,
brauchen wir acht kurze Entscheidungen. Die Empfehlungen beschreiben einen
vorsichtigen Start; Änderungen und ausdrücklich offene Punkte sind willkommen.

## Kurze Sichtprüfung

Bitte in der aktuellen Vorschau besonders darauf achten:

- Führt der Coachname verständlich zum jeweiligen Profil?
- Sind zwei Angebote am selben Wochenende gut unterscheidbar?
- Ist klar, dass der Kalender Vorträge und Gruppenangebote zeigt, während
  individuelle Termine persönlich angefragt werden?

Review: <https://dp-manuel.github.io/CompetenceHub/prototyp/kalender/>

## Entscheidungen

### CAL-D01: Wer darf Angebote sehen und Interesse vormerken?

**Empfehlung:** Angebote sind öffentlich sichtbar. Im ersten Pilot können nur
angemeldete Firmenkontakte Plätze vormerken. Privatpersonen und nicht
angemeldete Interessierte nutzen zunächst den persönlichen Kontaktweg.

**Antwort:**

[ ] Empfehlung freigegeben

[ ] Änderung: ___________________________________________________________

### CAL-D02: Was bedeutet die Zahl 25?

**Empfehlung:** `25` ist höchstens ein änderbarer Prüfschwellenwert je Angebot,
nicht automatisch die Kapazität oder eine feste Mindestgröße für alle Formate.
Kapazität und Prüfschwelle werden getrennt gepflegt.

**Antwort:**

[ ] Empfehlung freigegeben

[ ] Andere Bedeutung / Werte: __________________________________________

### CAL-D03: Wie lange gilt eine Vormerkung?

**Empfehlung:** Jedes Angebot zeigt eine Frist. Interessierte dürfen bis zur
internen Entscheidung stornieren. Findet das Angebot nicht statt oder ändert
sich die Kapazität, werden Betroffene informiert; es entsteht nie automatisch
ein Vertrag.

**Antwort:**

[ ] Empfehlung freigegeben

[ ] Gewünschte Standardfrist / Änderung: ________________________________

### CAL-D04: Welche Angaben sind notwendig?

**Empfehlung:** Im Firmenpilot werden vorhandene Firmen- und Kontaktdaten
verwendet. Neu abgefragt werden nur Platzzahl und eine Bestätigung der
Kontaktperson. Telefonnummer und zusätzliche Nachricht bleiben freiwillig.

**Antwort:**

[ ] Empfehlung freigegeben

[ ] Weitere Pflichtangaben: _____________________________________________

### CAL-D05: Welche Themen sollen auswählbar sein?

**Empfehlung:** Mit wenigen Oberthemen aus den bereits sichtbaren
Coach-Schwerpunkten starten. Janay prüft Bezeichnungen und Zuordnung; neue
Themen werden kontrolliert ergänzt statt frei eingetippt.

**Antwort:**

[ ] Empfehlung freigegeben

[ ] Gewünschte Oberthemen / Änderungen: _________________________________

### CAL-D06: Wer erhält die Meldung und wer vertritt?

**Empfehlung:** Janay erhält die fachliche Aufgabe im Portal und zusätzlich
eine E-Mail. Eine benannte Vertretung kann dieselbe Aufgabe übernehmen, ohne
Janays persönliches Konto zu verwenden.

**Antwort:**

[ ] Empfehlung freigegeben

Vertretung: _____________________________________________________________

### CAL-D07: Was muss vor Veröffentlichung geprüft sein?

**Empfehlung:** Coach, Thema, Datum, Uhrzeit, Format, Ort beziehungsweise
Online-Angabe, Kapazität und Preis oder Preishinweis werden je Angebot geprüft.
Nur ausdrücklich freigegebene Angaben erscheinen öffentlich.

**Antwort:**

[ ] Empfehlung freigegeben

[ ] Änderungen / weitere Prüfpunkte: ___________________________________

### CAL-D08: Wer verwaltet den verbindlichen Termin?

**Empfehlung:** Der bestätigte Termin wird im Competence Hub geführt. Die
Kalendereinladung wird im Namen des Competence Hub versendet und funktioniert
mit Outlook sowie anderen üblichen Kalendern. Eine spätere direkte
Outlook-Verknüpfung bleibt eine eigene Erweiterung.

**Antwort:**

[ ] Empfehlung freigegeben

[ ] Anderer Absender / andere Regel: ___________________________________

## Technische Grundentscheidung

Die Umsetzung soll in kleinen, einzeln prüfbaren Schritten erfolgen:

1. Coaches pflegen eigene Verfügbarkeiten; intern wird geprüft und
   veröffentlicht.
2. Firmen können unverbindlich Plätze vormerken.
3. Aus ausreichendem Interesse entsteht zunächst eine interne Aufgabe, keine
   automatische Buchung.
4. Erst ein bestätigter Termin erzeugt eine Kalenderdatei für Outlook und
   andere Kalenderprogramme.

**Antwort:**

[ ] Vorgehen freigegeben

[ ] Änderungswunsch: ____________________________________________________

## Rücklauf

Für den nächsten Umsetzungsschritt genügt, wenn jede Entscheidung
`freigegeben`, `geändert` oder `noch offen` markiert ist. Noch offene Punkte
bleiben sichtbar und werden nicht durch technische Annahmen ersetzt.
