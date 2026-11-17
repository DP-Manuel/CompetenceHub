# Website-Release und Coachstart

Stand17.11.2026. Website-Sprint mit freigegebener Pages-Veröffentlichung; IONOS
bleibt unverändert. Keine Server-, Datenbank-, Schlüssel-, Benutzer- oder Mailaktion.

## Tatsächlicher Umgebungsvergleich

| Bereich | IONOS vor diesem Sprint | Bisherige Pages-Vorschau | Geprüfter lokaler Kandidat |
| --- | --- | --- | --- |
| Coaches | Galvano, Rodríguez; sechs ausdrücklich fiktive Demos | Neun freigegebene Vorschauprofile | IONOS-Kandidat: zusätzlich Gülcan; Preview: acht, Hupp pausiert |
| Finder | Noch nicht enthalten | 27 Angebote/29 Formate, Coachauswahl noch nicht veröffentlicht | Preview behält27/29; IONOS ausschließlich Gülcans3 Familien/5 Formate |
| Bedarf → Angebot | Generische Kontaktwege | Finder und Profile vorhanden | Workshops direkt zum Finder, Führung zu passenden Coaches, Profil zurück zum Angebot |
| Anfrage | Mailclient, kein Serverversand | Dasselbe Verfahren | Angebot/Coach im kodierten E-Mail-Entwurf; Mailclient-Hinweis und Telefon bleiben |
| Kalender | Klar gekennzeichnete Beispiele | Klar gekennzeichnete Beispiele | Kontextlinks zum Kalender/Kontakt; keine echten Termine, keine private API |
| Recht/SEO | Zentrale D+P-Rechtsseiten, Produktionscanonical/Sitemap | noindex/nofollow/noarchive, Robots blockiert, kein Sitemapindex | Umgebungsgrenzen bleiben; Gülcan nur im Produktions-Sitemap des Kandidaten |

Lesender HTTP-Abgleich: **51/51 öffentlich abrufbare Dateien** stimmen exakt mit
dem bekannten Produktions-ZIP überein. Die52. Datei `.htaccess` ist nicht per HTTP
prüfbar; ihr aktueller Remoteinhalt benötigt vor einem späteren Upload eine frische
SFTP-Inventur. Es gab weder SFTP-Verbindung noch Produktionsänderung.

Pages war vor dem Sprint auf `78c3470258ea034b677fffd1157d8da3e3fcde78`,
Workflowlauf `42060354587` vom05.11. Der lokale16.11-Navigationsstand war noch
nicht veröffentlicht. Quell-HEAD, neues Produktionspaket und tatsächlich
veröffentlichter Pages-HEAD werden getrennt gebunden, nicht gleichgesetzt.

## Rechte und minimale Nacharbeiten

- Produktionsfähig: vorhandene Galvano-/Rodríguez-Profile und die ausdrücklich
  am29.10 für IONOS bestätigten Gülcan-Kurzinhalte samt Originalporträt.
- Nur Vorschau: Schwabauer, Klemm, Celic, Wegner-Ney und das bisherige Beckerprofil.
  Neue ungeklärte Becker-Angebotskandidaten bleiben ausgeschlossen.
- Hupp: Owner-Pause17.11; kein aktives Profil, keine direkte Profilroute und keine
  Einladung. Quellen und historische Identität bleiben erhalten; keine DBänderung.
- Unklar bleibt jede weitergehende Produktions-/Konto-/Identitätsfreigabe. Kein
  fremdes Angebot, Preis, Abschluss oder persönlicher Termin wird ergänzt.
- Technisch: derselbe Finder rendert beide Datensätze; keine doppelte Suchlogik.
  Anfragen bleiben Entwürfe, Beispieltermine nicht buchbar, Registry-Projektion aus.

## Onboarding und CAL-2

Die [neun Zeilen der Aktivierungsmatrix](../operations/coach-account-mapping-v1-2026-11-10.md)
bleiben erhalten: acht spätere Kandidaten, Hupp ON_HOLD, keine realen Ziel-UUIDs
oder bestätigten Loginidentitäten erfunden. Websitefreigabe ist keine Kontofreigabe.
Der [sechsteilige Kurzstart](../operations/pilot-coach-guide.md) führt über Einladung,
Passwort, MFA/Recovery, Tour, ersten Entwurf und Einreichen. Die vorhandene
Einladungsvorschau wird weiterverwendet; kein echter Versand.

Der [kleine CAL-2-Vorschlag](../requirements/cal2-small-slice-2026-11-17.md)
übernimmt D01–D08/ADR0007; nur Zeitpunkt der Kapazitätsbindung und Fristwirkung
brauchen Präzisierung. Keine Implementierung oder erneute CAL-1-Gesamtabnahme.

## Gezielte Prüfung

-37 Node-Modell-/Projektionsprüfungen bestanden: Rechte,8/3-Profilgrenzen,
  Finder27/3, zugelassene Formate, unveränderte Porträtbytes, keine gehaltenen Inhalte.
-15 fokussierte Pythonprüfungen bestanden: öffentliche SHA-/ZIP-Differenz und
  bestehender sicherer, nicht ausführender SFTP-Rehearsalvertrag; Bilder/Styles
  vor abhängigen Seiten und Startseite zuletzt, ohne Remoteausführung.
- Astro in beiden Modi:82 Dateien, keine Fehler/Warnungen/Hinweise.
  Produktionslinks1365, Previewlinks1398 bestanden.
- Acht tatsächliche lokale Browserwege: beide Modi bei1440px,390px, ohne
  JavaScript und nativen200%; Tastatur, Fokus, Reduced Motion, Finder/Leerzustand,
  fünf Anfragewege, geladene Bilder, Formgültigkeit und Rechtslinks.
- Kein HTTP-Schreibaufruf, externe Ressource oder JavaScriptfehler in diesen
  Wegen; Hupp-Direkteinstieg404. Formular wurde nicht versendet.
- Native200-Prüfung verwendet Fokus/Enter; automatisierter Firefox-Pointerklick
  wurde nicht als belastbarer Nachweis gezählt. Smartphone/Desktop-Pointer und
  bestehende Finderbeweise bleiben separate Nachweise, keine erfundene Abnahme.
- Screenshots unter `release-artifacts/website-release-20261117/`, öffentliche
  Vorher-Metadaten unter `.tmp/website-release-20261117/public-before.json`.
  Keine Wiederholung des Backend-Gesamttests oder von Kalender-Datumsreihen.

## Release und Rückfall

Sauberes, unveränderliches Kandidatenpaket und Pages-Lauf werden nach Commit
gebunden. Bis dahin kein IONOS-Freigabestatus aus einer Builddatei ableiten.

Zulässiger bekannter Rückfall ist das tatsächlich veröffentlichte P0-korrigierte
ZIP `competence-hub-website-1b4e33efa5e1-20260925T121142Z.zip`, SHA-256
`d80bd25977dfabf5d3ecf9892ed1747ff18b69a485d6b631ea0a0a459226dd5f`.
Es liegt unter `release-artifacts/website/`. Frühere personenbezogene Releases
und das vor dem P0-Fix liegende `d051a2e` sind keine zulässigen Rückfallziele.
Zusätzlich braucht der tatsächliche Upload eine aktuelle vollständige
Webrootkopie mit Hashinventar; unbekannte Remote-Dateien niemals automatisch löschen.

IONOS-Freigabe umfasst erst ein konkret benanntes neues ZIP/Hash, dessen Dateidelta,
SFTP-Inventur/Backup, asset-first/index-last Aktivierung und öffentliche Smokes.
Das ist genau ein späterer Betriebsblock, keine Aufforderung zum Upload jetzt.
Mailbox-Endzustellung ist durch einen Mailto-Browsertest nicht nachgewiesen.
EDV-App-DNS/TLS/SMTP und persönliche Identitäts-/Rollen-/Registrygates bleiben
von dieser statischen Websitefreigabe getrennt.
