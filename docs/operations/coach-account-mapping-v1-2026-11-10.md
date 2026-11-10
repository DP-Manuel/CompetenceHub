# Coachprofile und persönliche Portalzugänge

Stand10.11.2026. Keine personenbezogenen Daten aus privaten Quelldokumenten neu
gelesen. Grundlage ist die abgeschlossene kanonische9er-Reviewmatrix im
[Importvertrag](../architecture/coach3-existing-content-migration-plan-2026-10-23.md#exakte-dry-mapping-zahlen).
Fachliche READY-Freigabe ist weder Registry-Import noch Benutzeraktivierung.

Im akzeptierten VPS-Piloten existieren nur zwei synthetische Coachzeilen. Keine
der folgenden realen Personen wird ihnen zugeordnet; weder ihre UUID noch ein
Portal-Login dürfen aus Namen, Website-Slugs oder E-Mail-Konventionen abgeleitet werden.

| Geprüftes Profil | Stabile reale Coach-UUID im Ziel | Bestätigte Loginidentität | Vorgesehene Rolle | Aktivierung |
| --- | --- | --- | --- | --- |
| Christian Galvano | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |
| Manuela Rodríguez, M.A. | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |
| Elisabeth Schwabauer | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |
| Carolin Hupp | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |
| Gülcan Elmas-Brandes | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |
| T. Wegner-Ney | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |
| Goran Celic | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |
| Dr. Stefanie Becker | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |
| Susanne Klemm | Nicht zugeteilt/importiert | Offen | coach | Nicht angelegt |

## Getrennte Zugänge

- Manuel: bereits privat bestätigter Login, ausschließlich `admin`; noch nicht
  real angelegt. Die Loginadresse bleibt im geschützten Operatorverfahren.
  Sein späteres öffentliches Coachprofil ist
  eine eigene fachliche Identität, kein automatischer Rollenaufschlag.
- Janay: vorgesehen `calendar_reviewer`, kein `admin`. Eine Kontakt-/Weiterleitungs-
  adresse allein ist noch kein bestätigter persönlicher Login. Reale Aktivierung
  und Zustellung bleiben offen.
- Personen-/UUID-Zuordnung erst nach tatsächlich genehmigtem Import oder separat
  freigegebenem regulären Coach-Onboarding. COACH-3B REAL APPLY bleibt separat.
- Administration nutzt vorhandene UUID-Kandidaten, zeigt die bestehende Belegung
  und verweigert Übernahme fremder Coaches. Entfernen einer Coachrolle löscht
  keine historische Coachidentität und überträgt keine Termine auf andere Personen.

## Freigabe pro Person

Erforderlich sind Profil/UUID im tatsächlichen Ziel, bestätigte persönliche
Loginadresse, genau eine freigegebene Rolle, für Coach dieselbe bestehende UUID,
geeigneter Recovery-/Zustellweg und explizite Owner-Freigabe. Danach Einladung,
eigene Passwortvergabe, MFA/Recovery und persönliche Abnahme. Keine Startpasswörter,
geteilten Accounts, Tokenkopien oder Rollen aus Namensähnlichkeit.
