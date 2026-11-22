# Portal-Pilot: NVDA-Smoke am Testdesktop

**Stand: 22.11.2026. Status: gesprochen NICHT AUSGEFÜHRT.** Die lokalen
Browserprüfungen messen Fokus, Tastatur und zugängliche Namen/Beschreibungen.
Sie hören weder NVDA noch weisen sie nach, welche Live-Meldung NVDA ausgibt.
Der automatisierte Lauf hatte keinen nachweislich kontrollierbaren
Vordergrund-Desktop; NVDA und Windows-Sprachausgabe wurden nicht gestartet.

## Vorbereitung

- Manuel öffnet am sichtbaren Windows-Testdesktop Firefox und NVDA selbst.
  Eingabe und Audio müssen ihm eindeutig zugeordnet sein. Browser- und
  NVDA-Version, Zoom und Testrevision notieren. Zuerst bei 100 %, dann
  Geschäftsanfrage und Tour kurz bei echtem Browserzoom 200 % wiederholen.
- In die **bereits laufende** lokale Demo `run-cal2-local.py` wechseln:
  Das Terminal zeigt `V2_PLATFORM=READY`, Firefox hat die bereits angemeldeten
  Fenster Reviewer, Admin, Coach, Firma A und Firma B geöffnet. Der
  [Ablauf der V2-Vorführung](2026-11-21-v2-next-level.md#gemeinsame-vorführung)
  beschreibt Rollen und Testdaten. Die Demo gibt keine Anmeldedaten aus.
  Nicht abmelden oder eine zweite Demo starten. Den gemeinsamen Docker-Port
  `55433` nicht anfassen. Fehlt die passende laufende Demo, `BLOCKED`
  notieren und nicht auf VPS oder Staging ausweichen.
- Nur in den bereitgestellten Loopback-Fenstern arbeiten; bei unbekannter
  Herkunft oder TLS-Warnung stoppen. Keine Kennwörter, MFA-/Recovery-Codes
  oder vollständige Mitschnitte in den Nachweis übernehmen.
- Im NVDA-Menü (`NVDA+N`) unter **Werkzeuge** den **Sprachausgaben-Betrachter**
  öffnen, dann den Fokus zum Portal zurückgeben. Während eines Schritts
  zuhören, den Betrachter nicht überfahren oder fokussieren. `H` springt im
  Lesemodus zu Überschriften, `D` zu Landmarken. `NVDA+Leertaste` wechselt
  bei Bedarf zwischen Lese- und Fokusmodus. `Tab`, `Umschalt+Tab`,
  Pfeiltasten, `Enter`, `Leertaste` und `Esc` reichen für die Bedienung.
  [NVDA-Handbuch](https://download.nvaccess.org/releases/stable/documentation/de/userGuide.html)

## Kernpfad: Anfrage und Reviewer-Tour

Direkt im laufenden Reviewer-Fenster mit NVDA beginnen. Für eine Wiederholung
einen neuen fiktiven Betreff verwenden; einen eventuell geöffneten Tourdialog
zuerst mit `Esc` schließen.

1. Als Reviewer unter der Landmarke „Portalbereiche“ **Anfragen** per
   Tastatur öffnen. Fokus auf „Anfragen“, danach die Überschrift „Übersicht“
   und im Lesemodus die Liste finden. „Status filtern“ auswählen und
   „Filtern“ auslösen: Fokus auf „Übersicht“, Ergebniszahl hörbar. Für die
   folgenden Schritte wieder alle Status wählen.
2. „Anfrage erstellen“ öffnen. Fokus auf „Neue Anfrage“. Betreff und
   Beschreibung als Pflichtfelder prüfen; einmal leer absenden und prüfen,
   ob das erste fehlende Feld auffindbar ist. Dann Betreff und Beschreibung
   fiktiv ausfüllen, aber weder Unternehmen noch Privatkunde wählen.
   Absenden: Fokus auf „Unternehmen“; hörbar ist, dass genau eines der
   beiden Felder gewählt werden muss. Auswahl korrigieren und speichern.
   „Anfrage gespeichert“ und der Betreff als neue Detailüberschrift müssen
   wahrnehmbar sein. „Zur Übersicht“ liegt vor der Detailüberschrift
   (`Umschalt+Tab`); zurück in der Liste ist genau der zugehörige
   „Details öffnen“-Button fokussiert, mit Betreff und Status.
3. Im selben Reviewer-Fenster unter „Hilfe“ die „Prüfer-Einführung starten“.
   Titel, „Schritt 1 von 7“ und Beschreibung hören. „Weiter“ aktivieren:
   neuer Titel, „Schritt 2 von 7“ und neue Beschreibung. Einmal vorwärts
   und rückwärts tabben; keine Aktion hinter dem Dialog darf Fokus erhalten.
   `Esc` schließt, Fokus und Ansage kehren zu „Hilfe“ zurück. Bei 200 %
   die Tour bis „Weiter“ und das Anfrageformular bis zur Fehlermeldung
   wiederholen: kein abgeschnittener Text oder unerreichbarer Fokus.

## Vertiefung: Konflikt und Rollen

1. Dieselbe Anfrage in **Reviewer- und Admin-Fenster** öffnen; beide öffnen
   „Bearbeiten“, bevor jemand speichert. Als Reviewer eine Wiedervorlage
   speichern, dann als Admin eine andere. Im Admin-Fenster muss die
   Datenstandmeldung hörbar und fokussiert sein, die Eingabe bleiben und
   „Änderungen speichern“ deaktiviert sein. Das nächste `Tab` erreicht
   „Aktuellen Stand laden“. Beim ersten Verwerfen-Dialog mit `Esc`
   abbrechen: Eingabe bleibt. Erneut laden und Verwerfen bestätigen:
   Die vom Reviewer gespeicherte Wiedervorlage ist sichtbar.
2. Coach zuordnen, fiktiven Coach-Freigabetext speichern und je eine interne
   und eine für den Coach freigegebene Notiz hinzufügen. „Sichtbarkeit“,
   „Notiz“, „Notiz gespeichert“ und den aufklappbaren „Verlauf“ prüfen.
   Firma A hört Status, aber keine internen Notizen oder Bearbeitungsaktionen;
   Firma B findet diese Anfrage nicht. Der zugeordnete Coach hört nur den
   Freigabetext und die freigegebene Notiz, auch im Lesemodus. Keine
   vertrauliche Information darf allein in der Ansage auftauchen.

3. Unter „Hilfe“ auch im Coach-, Admin- und Firmenfenster die Einführung
   starten. Je den Anfang und den Wechsel zum zweiten Schritt hören:
   Dialogtitel, Fortschritt und Beschreibung. Mit `Tab` und `Umschalt+Tab`
   alle Dialogaktionen einschließlich
   „Einführung schließen“ erreichen. Portalaktionen hinter dem Dialog
   dürfen weder per Tab noch im Lesemodus bedienbar sein. „Zurück“ gibt den
   ersten Schritt wieder. `Esc` schließt, Fokus und Ansage kehren zu „Hilfe“
   zurück. Für eine Rolle zusätzlich „Überspringen“ und in einem Neustart
   „Abschließen“ probieren; beide geben den Fokus zu „Hilfe“ zurück.

## Optional: gesprochene Anmeldung und MFA

Nur durchführen, wenn die Moderation eine **separate isolierte synthetische
Login-Fixture** mit gültigen Zugangsdaten bereitstellt. Andernfalls
`NICHT AUSGEFÜHRT (keine Login-Fixture)` protokollieren. Keine Demo-Rolle
abmelden; dieses Ergebnis ändert den Status des Kernpfads nicht.

1. Mit `H` die Loginüberschrift lesen. Beim Tabben sollen Arbeits-E-Mail
   und Passwort als beschriftete Pflichtfelder erkennbar sein. „Passwort
   anzeigen“ bleibt aus. Falsches synthetisches Passwort absenden:
   Fehlermeldung hörbar und fokussiert, nächstes `Tab` auf „Anmelden“.
2. Korrekt anmelden. Fokus auf „Sechsstelliger Code“. `Umschalt+Tab` zur
   Bestätigungsart, `Pfeil rechts` zu „Recovery-Code“, `Pfeil links` zurück.
   NVDA meldet die Auswahl, Fokus bleibt auf dem jeweiligen Optionsfeld.
   `Tab` erreicht das passend benannte Eingabefeld. Keinen Recovery-Code
   verbrauchen.
3. Einmal einen falschen synthetischen TOTP eingeben: Fehler hörbar und
   fokussiert, dann `Tab` zu „Bestätigen“. Gültigen Code verwenden:
   Portalüberschrift auffindbar. Nur aus dieser Fixture wieder abmelden:
   Bestätigung hörbar, Fokus auf „Arbeits-E-Mail“.

## Nachweis und Abschluss

Pro Abschnitt `PASS`, `FAIL` oder `BLOCKED`, Rolle, Aktion, erwarteten und
tatsächlichen Fokus und einen kurzen bereinigten Wortlaut notieren. Ein
verpasster Ladehinweis ist nur aussagekräftig, wenn der Ladezustand lange
genug sichtbar war; Ergebniszahl und gespeicherte Änderungen separat
beurteilen. Abweichende Ansagereihenfolge ist akzeptabel, solange die
Information verständlich, ohne störende Wiederholung und vor der nächsten
Aktion verfügbar ist. Ein sichtbarer Hinweis oder der Accessibility-Baum
allein reicht für `PASS` nicht. Schwere oder reproduzierbar verpasste
Ansagen mit Tastenfolge melden. Die Demo-Rollen angemeldet lassen und den
Owner am Ende der gemeinsamen Abnahme die eigenen Testressourcen beenden
lassen.

**Automatisiert:** Die Tests für [Anmeldung](../../apps/webapp/tests/test_portal_auth_accessibility_browser.py),
[Anfragen](../../apps/webapp/tests/test_business_requests_browser.py) und
[Einführungen](../../apps/webapp/tests/test_portal_tour_feedback_browser.py)
verwenden Firefox und synthetische Loopback-APIs ohne Docker. Gemessen
werden unter anderem Fehlerfokus, erreichbarer Konflikt-Reload, Feldbeschreibungen,
rollenbezogene Schaltflächennamen sowie Name und Schrittbeschreibung des
Tourdialogs. Das ist technische Regressionsevidenz, kein Sprachnachweis.
