# COACH-2: Local Admin Management

Stand:23.10.2026. Implementiert und lokal mit ausschließlich synthetischen Daten
abgenommen. Kein produktiver Betrieb und keine Änderung der öffentlichen Websites.
Fachliche Grundlage bleibt der [COACH-1-Vertrag](coach-registry-contract-v0.1.md).
Implementierungsstand: Commit `92bd042`; Dokumentation und COACH-3-Analyse sind
getrennt versioniert. Kein Deployment folgt aus diesen Commits.

## Bedienung Und Grenzen

Der bestehende Portal-Stack bleibt: modulare DOM-Oberfläche ohne neue Bibliothek,
gleiche Design-Tokens, native Formulare/Dialoge, Login/MFA, Session und CSRF.
Admin sieht den Bereich Coaches nur bei verfügbarem, ausdrücklich injiziertem
Registry-Lesedienst. Der normale Runtime-Start aktiviert diesen Dienst nicht.
Direkteinstieg `/portal/coaches/` ist bereits serverseitig geschützt.

| Bereich | Tatsächlicher Umfang |
| --- | --- |
| Liste | Anzeigename, Lifecycle, beide Veröffentlichungsstände, Themen-/aktive Angebotszahl, neuester Profilstand; seitenweise10 Einträge |
| Filter | Alle fünf Lifecycle-Zustände und Preview/Production/nicht veröffentlicht; serverseitig angewandt |
| Anlage | Nur Anzeigename; stabile zufällige Coach-UUID, initial draft, keine Publication, kein Account. Wiederholung nach verlorenem Antwortweg verwendet denselben Erstellungsauftrag |
| Übersicht | Sichere Account-Zustandsprojektion, vorhandene Kalenderrolle und separater Kalender-Profilpfad; laufende/künftige Angebote als Sperrhinweis |
| Profil | Bestehende COACH-1-Felder; expliziter ASCII-Profilpfad, keine Ableitung bei Namensänderung; optionale Porträt-Referenz/Hash/Alternativtext/Umgebung, kein Upload |
| Themen | Vorhandene kanonische Themen auswählen/abwählen; alle Kategoriezuordnungen sichtbar, kein exklusiver Radio-Modus; Auswahl bleibt beim Blättern erhalten |
| Kategorien | Mehrfachzuordnung wird aus dem kanonischen Thema gelesen. Keine Änderung am Thema im Profilformular, kein gespeichertes „Alle“ |
| Kompetenzen | Eigene versionierte Label-Liste, getrennt von Themen; keine neu erfundene Kompetenz-Entität |
| Angebote | Vortrag, Workshop, Coaching, individuelles Angebot, sonstiges; Titel/Beschreibung/aktiv/eindeutige Reihenfolge. Deaktivieren statt Hard Delete; kein Preis-/Finanzmodell |
| Revisionen | Draft editierbar; eingereichte/abgeschlossene Fassungen nur lesbar. Neue Revision kopiert Inhalte, niemals Freigaben. Historische Fassungen gezielt öffnbar |
| Lifecycle | Nur fachlich zulässige, serverseitig projizierte Aktionen. Pause/Deaktivierung/Archivierung bestätigen Konsequenzen und erhalten Historie/Accounts |
| Wiedereinstieg | Gleiche UUID; neue geprüfte Revision oberhalb der Sperrgrenze, frische Einwilligungs-/Umgebungsfreigaben, keine automatische Wiederveröffentlichung |
| Kalenderkonflikt | Laufendes/künftiges Angebot entfernt Pause-/Offboarding-Aktionen; manuell gefälschter Lifecycle-Aufruf wird ebenfalls abgewiesen |
| Freigaben | Inhalt, Einwilligungsnachweis, Preview und Production jeweils getrennt an der konkreten Revision; Nachweisreferenz erforderlich |
| Veröffentlichung | Preview und Production in getrennten Abschnitten mit Revision/Status; Aktionen ändern ausschließlich den lokalen DB-Status. Kein Build, Git, Pages, SFTP oder IONOS-Aufruf |
| Historie | Getrennt paginierte Revisionsliste und verständliche Statusereignisse; keine Actor-UUIDs, Roh-Auditpayloads oder Nachweisdokumente im Verlauf |

Die fachlich notwendige Warnung vor Rücknahme/Offboarding stellt klar:
Bereits ausgelieferte statische Webseiten ändern sich erst durch einen separat
freigegebenen Release. Die UI verspricht keine sofortige Remote-Löschung.

## Minimaler Lesevertrag

`/api/v1/admin/coach-management` ergänzt nur autorisierte Leseprojektionen;
Schreibaktionen verwenden weiterhin `/api/v1/admin/coaches`.

| GET | Projektion / Begrenzung |
| --- | --- |
| Basis | Zusammenfassung und Filter; limit1–50, offset0–10000, has_more; keine Profile pro Listenzeile nachladen |
| `/topics` | Aktive kanonische Themen samt M:N-Kategorien; limit1–100, paginiert |
| `/{coach_id}` | Ein ausgewähltes Profil, Publication-Zusammenfassungen, sichere Verknüpfungszustände und Capabilities; optional revision_id innerhalb genau dieses Coaches |
| `/{coach_id}/revisions` | Revisionsmetadaten ohne Inhalte; limit1–25 |
| `/{coach_id}/history` | Nur Aktion/Zeit aus bestehendem payloadfreien Audit; limit1–25 |

Listen verwenden eine begrenzte SQL-Abfrage, keine N+1-Detailabfragen.
Der Detail-Lader benötigt höchstens sechs Revisionen: neueste zwei, letzte für
Aktivierung geeignete Revision, maximal zwei Publication-Referenzen und eine
explizit gewählte historische Revision. Die Antwort enthält nur deren gewähltes
Profil. Eine ältere gültige Aktivierungsfreigabe bleibt trotz neuerer ungeprüfter
Fassungen erhalten. Lesesnapshot und Capabilities sind konsistent in REPEATABLE READ.

Die Schreib-API akzeptiert optional `Prefer: return=minimal`; dann erhält die UI
nur Identität/Version/letzte Revisionsreferenz und lädt den begrenzten Lesestand.
Der bisherige COACH-1-Antwortvertrag ohne diesen Header bleibt unverändert.
Die internen Schreibtransaktionen laden weiterhin das bestehende Aggregat;
Langzeit-Lasttests und eine gezielte Schreibpfad-Optimierung bleiben vor einem
großen produktiven Bestand nötig. Die UI lädt keine unbegrenzte Historie.

## Sicherheit Und Konflikte

Alle neuen Lesewege und der Direkt-URL-Aufruf benutzen dieselbe serverseitige
Admin-Prüfung. Intern ohne Admin:403. Die bestehende engere Admin-Sessionaufnahme
weist reine Coach-/Reviewer-Sessions mit401 ab. Firmenkontakt wird bereits vor
MFA am Portal-Login abgewiesen. Fake-Session-API-Tests prüfen zusätzlich403 für
alle vier nicht berechtigten Rollen; daraus wird keine native Session behauptet.
Keine Aufnahmeberechtigung wurde erweitert.

Schreiben: unveränderte Origin-/CSRF-Prüfung,32KiB, strikt erlaubte Felder,
MFA-Session, erwartete Coach-Version und Zeilensperre. Ein zweiter Tab kann den
gemeinsamen CSRF-Token rotieren: COACH-2 erneuert ihn einmal unmittelbar vor dem
Schreibversuch, sendet aber die ursprünglich geladene Version. Kein automatisches
Wiederholen von Schreibaktionen. Ein weiterer Verifikationskonflikt erhält die
Eingaben; Rollenverlust entfernt den lokalen Zustand und führt zur Anmeldung.

Bei409 bleiben die Formulare erhalten; Fokus geht auf die verständliche Meldung.
„Aktuellen Stand laden“ verwirft erst nach Bestätigung und lädt die neue Version.
Dirty-State schützt Bereichswechsel, Abbrechen und Schließen/Reload des Fensters.
Clientvalidierung fokussiert ungültige Felder und öffnet gegebenenfalls deren Tab.
SQL-Details/Server-Stacktraces werden nicht an die Oberfläche weitergegeben.

Inhalte werden ausschließlich als Text/DOM-Eigenschaften eingesetzt. Keine HTML-
Interpolation, Token in Web Storage, externen Skripte oder Release-Befehle.
Unbekannte IDs, fremde Revisionszuordnung und Publication-Eskalation scheitern.

## Tatsächliche Abnahme

| Prüfung | Ergebnis |
| --- | --- |
| Neue fokussierte COACH-2-Tests |10 PASS: Rollen/Direkt-URL, optionaler Dienst, minimaler Antwortvertrag, fachliche Capabilities, ID-Zuordnung, sichere DOM-Grenzen und2026→2027→2028 bei gleicher UUID |
| Komplette lokale Suite |498 PASS,18 bewusst nicht aktivierte Integrationsfälle:17 Staging und1 separate lokale Registry-Prüfung |
| COACH-1 echtes lokales PG16 |1 PASS: bestehende Transaktionen, Constraints, native Auth und Kalender-/Lifecycle-Grenzen bleiben erhalten |
| COACH-2 echtes lokales PG16/HTTPS/Edge |109 Checks PASS; native Anmeldung/MFA, sämtliche fachlichen Abläufe, Antwortverlust ohne Doppelanlage, Zwei-Tab-409, sichere Recovery, Rollen, Kalender-Sperre, Historie über13 Revisionen, lokale Public Projection |
| Responsive/A11y | Alle sieben Detailbereiche bei390CSS-px und nativem200-%-Zoom auf Überlauf, tatsächliches Abschneiden und Textüberlagerung geprüft; Tastatur-Anlage/Revision/Checkbox/Speichern, Pfeil-/Home-/End-Tabs, Dialogfokus und Fehlerfokus; Reduced Motion aktiv |
| Unveränderte CAL-1-Regression |142 native lokale Browserchecks und17 API-Prüfungen PASS; eigener0001–0006-Container, nicht als neue VPS-Abnahme umetikettiert |
| Weitere Gates | compileall, pip check, JS-Syntax und diff-Prüfung; genaue letzte Nachweise im Sitzungsabschluss |

Das ist keine vollständige assistive-Technologie-Zertifizierung: manueller NVDA-
oder JAWS-Lauf wurde nicht durchgeführt. Keine offenen High/Critical-Befunde im
geprüften lokalen Scope; keine Aussage über ungetesteten produktiven Betrieb.

Lokale JSON-/Bildbelege unter `release-artifacts/coach2-local-20261023` bleiben
ignoriert. Desktop/Mobil/native Zoom-Aufnahmen wurden visuell angesehen.
Finale `acceptance.json` (109 Checks), SHA-256:
`4bfce02765014cc309ec4ba43ddcf7e917ef5b226e768d51446995474560a13f`.
Vor Fullpage-Aufnahmen wird nach oben gescrollt, damit außerhalb des Viewports
versteckte fixe Skiplinks nicht als Screenshot-Artefakt mitten im Dokument landen.
Zoom verwendet physische CDP-Maße, nicht einen halbierten CSS-Ausschnitt.

Runner aus Repositorywurzel in PowerShell:

```powershell
.\apps\webapp\scripts\run-coach-registry-local.ps1 -PythonPath '.\apps\webapp\.venv\Scripts\python.exe' -ManagementBrowser
```

Voraussetzung: Docker Desktop, vorhandenes postgres:16-bookworm, freier55434.
Keine echten Passwörter: prozessintern erzeugte Testzugänge, temporäres Zertifikat,
Loopback-HTTPS, isoliertes PG-tmpfs ohne Hostdaten-Mount. Die Oberfläche ist während
des Tests unter dessen temporärer lokalen URL erreichbar; danach wird sie gestoppt.
Browser/Profile/HTTPS-Server beendet, gesamte eigene Testdatenbank durch Entfernen
des exakt eigenen Containers gelöscht. Kein VPS-, Pages- oder IONOS-Zugriff.

## Nicht Enthalten

Themen-Neuanlage und Kategorieänderung besitzen noch keinen COACH-1-Schreibvertrag;
keine semantische Dublettenprüfung wird vorgetäuscht. Kein Medienupload,
Account-/Kalenderrollenmanagement, echte Einwilligungserzeugung, Website-Importer,
realer Coachimport oder Servermigration. Dies sind keine verdeckten UI-Aktionen.
