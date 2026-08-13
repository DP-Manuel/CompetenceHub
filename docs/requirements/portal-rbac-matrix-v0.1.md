# Portal RBAC Matrix v0.1

Stand: 13.08.2026

Quelle ist Blatt `04_Rollen_Rechte` der Product-Owner-Arbeitsmappe v0.2.
Autorisierung ist serverseitig und deny-by-default. UI-Ausblendung allein ist
keine Berechtigungspruefung.

## Bestaetigte Matrix

| Bereich / Aktion | Admin | Intern | Coach | Firmenkontakt |
| --- | --- | --- | --- | --- |
| Benutzer anlegen/deaktivieren | erlaubt | erlaubt | nein | nein |
| Rollen zuweisen | erlaubt; Adminaktionen mit Reauth/MFA | nur explizit freigegebene Nicht-Adminrollen | nein | nein |
| Unternehmen lesen | alle | alle | nur zugewiesene | nur eigene |
| Unternehmen anlegen | erlaubt | erlaubt | nein | nur eigene |
| Unternehmen bearbeiten | erlaubt | erlaubt | nein | eigene eingeschraenkt |
| Ansprechpartner lesen | alle | alle | nur zugewiesene | nur eigene |
| Ansprechpartner bearbeiten | erlaubt | erlaubt | nein | eigene eingeschraenkt |
| Coaches lesen | alle | alle | eigenes Profil und freigegebene | freigegebene |
| Coachprofil bearbeiten | erlaubt | erlaubt | eigenes eingeschraenkt | nein |
| Coachpublikation freigeben | erlaubt | erlaubt | nein | nein |
| Themen/Leistungen pflegen | erlaubt | erlaubt | nein | nein |
| Anfragen anlegen | erlaubt | erlaubt | nein | nur eigene |
| Anfragen lesen | alle | alle | nur zugewiesene | nur eigene |
| Anfragen bearbeiten | erlaubt | erlaubt | zugewiesen eingeschraenkt | eigene eingeschraenkt |
| Anfragestatus aendern | erlaubt | erlaubt | nur definierte Transitionen | nur definierte Transitionen |
| Feedback abgeben | erlaubt | erlaubt | eigen/zugeordnet | nur eigene |
| Feedback-Rohdaten lesen | erlaubt | erlaubt | nur zugewiesen | nur eigene |
| Statistik sehen | erlaubt | rollenabhaengig | eigene | eigene Firma |
| Daten exportieren | erlaubt | erlaubt | nein | nein |
| Audit lesen | erlaubt | erlaubt | nein | nein |

Die Teilnehmerrolle ist deferred.

ADR 0003 praezisiert die urspruenglich zu breite Rollenvergabe aus der
Product-Owner-Matrix: `internal` darf weder die Adminrolle vergeben/entziehen
noch Adminkonten verwalten. Die genaue Liste nicht privilegierter Rollen, die
`internal` spaeter zuweisen darf, benoetigt eine explizite Policy. Bis dahin
gilt deny-by-default.

## Scope-Regeln

- **Eigene Firma:** Portalnutzer ist ueber einen Firmenkontakt mit dem
  Unternehmen verbunden.
- **Eigenes Profil:** Coachprofil verweist auf denselben Portalnutzer.
- **Zugewiesen:** Eine spaetere explizite Vorgangszuordnung oder die interne
  Verantwortlichkeit verbindet Nutzer und Datensatz. Die genaue Coach-
  Request-Zuordnung ist Phase 2 und darf nicht improvisiert werden.
- **Freigegeben:** Nur fachlich zur Publikation freigegebene Coachdaten, nicht
  interne Verfuegbarkeit oder Notizen.
- **Eingeschraenkt:** Erlaubte Felder werden pro API-Use-Case festgelegt;
  Massenzuweisung kompletter DTOs ist verboten.

## Mehrfachrollen

- Explizite Erlaubnisse werden vereinigt.
- Ein Rollenwechsel erweitert keinen Datensatzscope ohne passende Beziehung.
- Ein explizites Sicherheitsverbot darf nicht durch eine zweite Rolle
  versehentlich aufgehoben werden.
- Deaktivierte Benutzer werden unabhaengig von Rollen abgewiesen.

## RBAC-Testszenarien

| ID | Szenario | Erwartung |
| --- | --- | --- |
| RBAC-001 | Unauthentifizierter Zugriff auf Portal-API | abgewiesen |
| RBAC-002 | Unbekannte Aktion ohne Policyeintrag | deny-by-default |
| RBAC-003 | Admin legt synthetischen Benutzer an | erlaubt und auditiert |
| RBAC-004 | Intern deaktiviert synthetischen Benutzer | erlaubt und auditiert |
| RBAC-005 | Coach weist Rollen zu | abgewiesen |
| RBAC-006 | Firmenkontakt liest fremde Firma | abgewiesen ohne Datenleck |
| RBAC-007 | Firmenkontakt liest eigene Firma | erlaubt, Feldsicht eingeschraenkt |
| RBAC-008 | Coach liest nicht zugewiesene Anfrage | abgewiesen |
| RBAC-009 | Coach bearbeitet fremdes Coachprofil | abgewiesen |
| RBAC-010 | Coach bearbeitet erlaubte Felder des eigenen Profils | erlaubt und auditiert |
| RBAC-011 | Firmenkontakt exportiert Daten | abgewiesen |
| RBAC-012 | Admin und Intern lesen Audit | erlaubt |
| RBAC-013 | Mehrfachrolle Intern+Coach | explizite Rechte vereinigt, Scope bleibt wirksam |
| RBAC-014 | Deaktivierter Mehrfachrollen-Nutzer | vollstaendig abgewiesen |
| RBAC-015 | Coach/Firmenkontakt versucht undefinierte Statusueberleitung | abgewiesen |
| RBAC-016 | Intern versucht Adminrolle zu vergeben oder Adminkonto zu aendern | abgewiesen und auditiert |
| RBAC-017 | Admin aendert Adminrolle ohne frische MFA/Reauth | abgewiesen |

## Noch nicht implementierbar

- finale Request-Transitionen
- externe Einladungs-, Reset- und MFA-Flows
- Coach-Zuweisung zu Anfragen
- Teilnehmerrechte
- Feedback- und Statistikfeldsicht im Detail
