# Janay-Kalenderfeedback - 2026-09-10

## Zweck und Quellgrenze

Dieses Dokument überführt Janays freigegebene Rückmeldung vom 10.09.2026 in
prüfbare Produktanforderungen. Die private Word-Datei bleibt außerhalb von Git;
hier stehen nur die für Umsetzung, Entscheidung und Abnahme notwendigen Punkte.

## Triage

| ID | Rückmeldung | Klasse | Priorität | Umsetzung / Gate |
| --- | --- | --- | --- | --- |
| CAL-FB-01 | Der Coachname im Kalender soll zum vorhandenen Coachprofil führen | Usability / Navigation | Hoch | CAL-0.1: mit bereits veröffentlichten Profilen und klar als Beispiel markierten Terminen umsetzen |
| CAL-FB-02 | Das öffentliche Coachprofil soll später freigegebene Termine zeigen; der persönliche Pflegekalender ist nur für den Coach bestimmt | Anforderung / Rechte | Hoch | Öffentliche und authentifizierte Ansicht strikt trennen; produktiv erst mit CAL-1, RBAC und serverseitiger Prüfung |
| CAL-FB-03 | Parallel oder überlappend stattfindende Termine, besonders am Wochenende, müssen unterstützt werden | Geschäftsregel / Datenmodell | Hoch | CAL-0.1 visuell nachweisen; später keine globale Eindeutigkeit auf Datum oder Zeitraum einführen |
| CAL-FB-04 | Der Kalender zeigt geplante Vorträge und Gruppenangebote; individuelle Termine werden direkt angefragt | Inhalts- und Prozessgrenze | Hoch | CAL-0.1 erhält sichtbaren Kontakt-Hinweis; Individualtermine werden nicht als freie öffentliche Slots behauptet |
| CAL-FB-05 | Coaches tragen ihre eigene Verfügbarkeit ein | Rollenanforderung | Hoch | CAL-1: nur eigene Einträge; Änderung und Rücknahme serverseitig autorisieren und auditieren |
| CAL-FB-06 | Janay prüft nach ausreichender Nachfrage und schaltet das Angebot frei | Freigabeworkflow | Hoch | Initiale fachliche Ownerin bestätigt; technische Berechtigung rollenbasiert statt personencodiert, Vertretung und Kanal offen |
| CAL-FB-07 | Administratoren benötigen umfassende Steuerungsmöglichkeiten | Rollenanforderung | Mittel | Admin darf Kalenderoperationen ausführen, bleibt aber an Authentifizierung, Audit und Geschäftsstatus gebunden |

## Architekturgrenze

- Öffentlicher Kalender und Coachprofile dürfen nur ausdrücklich veröffentlichte
  Angebote zeigen.
- Der persönliche Coachkalender gehört in die authentifizierte Webapp und darf
  nicht durch `noindex`, versteckte Links oder reine Frontendlogik geschützt
  werden.
- Janay wird initial der Freigabeberechtigung zugeordnet; Code und Datenmodell
  referenzieren eine Berechtigung beziehungsweise Rolle, nicht ihren Namen.
- Adminrechte sind kein Audit- oder Status-Bypass. Jede Freigabe und relevante
  Änderung bleibt einer handelnden Person zuordenbar.

## Abnahme CAL-0.1

- Ein Coachname öffnet das passende bereits veröffentlichte Profil.
- Die Seite kennzeichnet alle sichtbaren Termine weiterhin eindeutig als
  Beispieldaten und behauptet keine echte Verfügbarkeit.
- Zwei zeitlich überlappende Wochenendangebote verschiedener Coaches werden im
  selben Kalendertag ohne Überlagerung oder Informationsverlust dargestellt.
- Ein sichtbarer Hinweis trennt geplante Vorträge/Gruppenangebote von
  individuellen Terminanfragen und führt zum Kontaktweg.
- Tastaturbedienung, 390-Pixel-Darstellung, `noindex` und fehlende
  Netzwerkschreibzugriffe bleiben nachgewiesen.

