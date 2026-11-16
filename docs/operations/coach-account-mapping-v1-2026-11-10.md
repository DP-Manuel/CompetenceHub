# Coachprofile und persönliche Portalzugänge

Stand16.11.2026. Keine personenbezogenen Daten aus privaten Quelldokumenten neu
gelesen. Grundlage ist die abgeschlossene kanonische9er-Reviewmatrix im
[Importvertrag](../architecture/coach3-existing-content-migration-plan-2026-10-23.md#exakte-dry-mapping-zahlen).
Fachliche READY-Freigabe ist weder Registry-Import noch Benutzeraktivierung.

Im akzeptierten VPS-Piloten existieren nur zwei synthetische Coachzeilen. Keine
der folgenden realen Personen wird ihnen zugeordnet; weder ihre UUID noch ein
Portal-Login dürfen aus Namen, Website-Slugs oder E-Mail-Konventionen abgeleitet werden.

| Coach | UUID im tatsächlichen Ziel | Bestätigte Loginidentität | Portalrolle | Aktivierungsstatus | Freigaben | Offene Angaben |
| --- | --- | --- | --- | --- | --- | --- |
| Christian Galvano | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |
| Manuela Rodríguez, M.A. | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |
| Elisabeth Schwabauer | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |
| Carolin Hupp | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |
| Gülcan Elmas-Brandes | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |
| T. Wegner-Ney | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |
| Goran Celic | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |
| Dr. Stefanie Becker | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |
| Susanne Klemm | Nicht zugeteilt/importiert | Nicht bestätigt | coach, vorgesehen | Nicht angelegt | Profilreview READY; persönliche Aktivierung offen | A–D |

Offene Angaben: **A** bestätigte persönliche Arbeits-E-Mail und Identität;
**B** belegte reale Ziel-UUID nach separat genehmigtem Registry-Import oder
regulärem Onboarding; **C** ausdrückliche personenbezogene Rollen-/Zustellfreigabe;
**D** freigegebene App-Adresse/SMTP und persönlicher Empfangs-/MFA-Nachweis.
Vor Einladung müssen A–C und die Infrastruktur aus D vorliegen; Empfang/MFA
werden danach nachgewiesen. Kein erneuter fachlicher Profiltermin nötig.

Die neun READY-Profile sind keine neun Portalbenutzer. Die Freigabespalte betrifft
den bereits dokumentierten Profilreview, nicht pauschale Veröffentlichungsrechte;
deren jeweilige Umgebungsgrenze bleibt in der Publikationsmatrix. Bei Becker
werden insbesondere keine neuen ungeklärten Angebotskandidaten freigegeben.

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

## Kurzer Administrationsablauf Nach Geschlossenen Gates

1. **Zugänge** öffnen, bestätigten Anzeigenamen und persönliche E-Mail eingeben.
2. Rolle **Coach** wählen und die bereits bestätigte reale UUID aus den vorhandenen
   Vorschlägen übernehmen; Name und UUID gegen die freigegebene Zuordnung prüfen.
3. **Einladung prüfen** verwenden: lokale Zusammenfassung, noch kein Konto/Versand.
4. Erst bei freigegebener Zustellung **Einladung vormerken** wählen. Der bestehende
   Versandweg liefert den einmaligen Link; kein Kopieren von Tokens oder Passwörtern.
5. Coach setzt eigenes Passwort, richtet MFA ein und verwahrt zehn Recovery-Codes.
   Anzeige von Rolle, eigener Angebotsliste und Erstzugang gemeinsam bestätigen.

Fehlt die reale UUID oder ist sie bereits anders belegt: stoppen, nicht aus
Website-Slug/Namen ableiten und nicht die synthetische Demoidentität übernehmen.
Die vorhandene Oberfläche und Prüfung bleiben erhalten; keine neue Import- oder
Einladungsplattform, kein echter Versand in diesem Vorbereitungsblock.
