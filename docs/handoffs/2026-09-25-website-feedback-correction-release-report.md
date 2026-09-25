# Abschlussbericht Website-Korrekturrelease

Stand: 25.09.2026

## Feedback und Ergebnis

Das Feedback vom 25.09. und das zweite KI-Review sind vollständig abgeglichen.
Bereits umgesetzt waren `Manuela Rodríguez, M.A.`, der Übersichts-Schwerpunkt
`Erwachsenenbildung`, getrennte Einstiege für Recruiting und
Personalentwicklung, Assessment Center, Supervision und qualifikationsgebundene
Mediation unter Personalentwicklung, eine allgemeine FAQ und die Entfernung der
Assessment-Center-Dopplung auf Mindforge.

Von den drei Abschlussprüfungen erforderte nur die Startseite eine minimale
Nacharbeit: Die bestehenden, unveränderten Links `Für Unternehmen` und
`Mindforge · Life Coaching` wurden in den ersten sichtbaren Hero-Bereich
verschoben. Es gab keine Neugestaltung, keine neue API und keine Änderung der
Linkziele.

Demoprofile sind beim Direkteinstieg als fiktiv und als keine reale Coachperson
gekennzeichnet, ohne Porträt und mit `noindex`. Der Kalender beschreibt alle
Termine als nicht echt, nicht buchbar und nicht veröffentlicht; die Aktion ist
nur eine Simulation und besitzt keinen Übermittlungsendpunkt. Kontakt bietet
direkte `mailto:`- und `tel:`-Wege und beschreibt den Übergang an das lokale
E-Mail-Programm weiterhin ehrlich.

## Dateien und Umfang

Geändert wurden die betroffenen Website-Komponenten und Seiten unter
`apps/website/src`, die Browserregression
`apps/website/scripts/run-messe-browser-acceptance.py` sowie zugehörige
Content-, Privacy-, Stakeholder- und Projektstatusdokumente. Es gab keine
Backend-, API-, Datenbank-, Rollen-, Konto- oder Echtdatenänderung.

## Lokale Nachweise

- Astro: 41 Dateien, 0 Fehler, 0 Warnungen, 0 Hinweise.
- Build: 33 Seiten; 1.237 interne Referenzen verifiziert.
- Vollständige Edge-Abnahme: 823/823 bestanden.
- Zweiter KI-Fokusabgleich: 82/82 bestanden.
- SFTP-Rehearsal-Tooling: 8/8 bestanden.
- Desktop, 390 px, 200 Prozent, Tastatur/Fokus und Reduced Motion sind in der
  vollständigen Abnahme enthalten.

## Release

- Source-Commit: `d051a2e27f22` (`Apply final September website feedback`).
- Artefakt:
  `competence-hub-website-d051a2e27f22-20260925T113559Z.zip`.
- Umfang: 52 Dateien.
- SHA-256:
  `d58a38d2af3b72d3fb8d62cbd859f35c7119396332a5252ae77d6faff0ba2f95`.
- Veröffentlichung: kontrolliertes SFTP-Update; `index.html` zuletzt aktiviert.

Die Vorabkopie enthielt 56 Dateien. Alle 52 erwarteten Dateien stimmten
bytegenau mit `d493e195f80a`; vier unreferenzierte Altassets waren zusätzlich
vorhanden. Eine alte JavaScript-Datei enthielt abgelöste Demoidentitäten. Beim
Release wurden alle fünf gegenüber dem neuen Artefakt veralteten Assets gezielt
entfernt. Die abschließende SFTP-Liste bestätigt exakt vier aktuelle
`_astro`-Dateien.

## Rollback

Die vollständige Rohsicherung
`release-artifacts/website-sftp-rollback/20260925-pre-d051a2e` bleibt mit
Inventar-SHA-256
`25fd6153067a9571d69403a624879b39dff7f773a0e7fdc2dad017585c6813ce`
als Beweissicherung erhalten, ist wegen alter Assets aber kein zulässiges
öffentliches Rollback.

Zulässig ist ausschließlich das bereinigte 52-Dateien-Rollback
`release-artifacts/website-sftp-rollback/20260925-safe-d493e195f80a` mit
Inventar-SHA-256
`a815bb6022ec9d444195749e6b3d669037015561838d12b1da6b009c2f3d17fb`
und dem bereits öffentlich verifizierten ZIP-SHA-256
`6084fb45396a54ec067487c2c4707b2cfcbe8a8c2eb9d3583fb89ce357177a91`.
Ältere personenbezogene Releases sind keine Rollbackziele.

## Produktions-Smokes

- Kanonisches HTTPS liefert 200; HTTP und Alias leiten dauerhaft kanonisch um.
- 404 und Sicherheitsheader sind wirksam.
- 72/72 öffentliche Edge-Prüfungen bestanden.
- Kern-, Kontakt-, Rechts-, Coach- und Kalenderseiten liefern den erwarteten
  Status und Inhalt.
- Desktop und 390 px haben keinen horizontalen Überlauf oder JavaScriptfehler.
- Beide Zielgruppeneinstiege liegen im ersten Viewport.
- Sechs Demoprofile sind eindeutig, ohne Porträt und `noindex`; sechs entfernte
  Personenrouten liefern 404.
- Alte Assetpfade liefern kein CSS oder JavaScript mehr; Sitemap enthält nur
  Christian Galvano und Manuela Rodríguez als Coachdetailseiten.

## Messe-Handover und Freeze

Nach diesem Release gilt Feature Freeze bis nach der Messe am 17.10. Während
Manuels Abwesenheit ist Thomas Roß nur technischer Break-glass-Kontakt; Janay
verantwortet die Kontaktmailbox ohne benannte Vertretung. Zulässig sind nur
Incident-Recovery und ausdrücklich freigegebene Inhaltskorrekturen. CAL-1,
CAL-2 und FIN-01 bleiben bis nach der Messe pausiert.

Empfohlenes nächstes Gate ist genau ein begrenzter Messe-Preflight unmittelbar
vor dem 17.10.: TLS, Redirects, Kernrouten, Kontaktwege, Desktop/Mobil und eine
visuelle Stakeholderbestätigung. Das Gate ist bestanden, wenn Produktion weiter
dem Source-Commit `d051a2e27f22` entspricht und kein Korrekturrelease nötig ist.
