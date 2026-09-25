# Website Messe-Handover

Stand: 25.09.2026

Zweck: secret-freie Uebergabe der statischen Competence-Hub-Website fuer den
stabilen Messestand am 17.10. Der aktuelle Produktionsstand ist verifiziert;
dieses Dokument autorisiert keinen weiteren Upload und keine Portal-, API-,
Datenbank-, Konto-, SMTP- oder Kalenderaktivierung.

## Ziel und Verantwortliche

- Repository: `https://github.com/DP-Manuel/CompetenceHub.git`
- Branch: `main`
- Website: `apps/website`
- Kanonische Domain: `https://competencehub.donner-partner.de`
- SFTP-Chroot: `/`; gemeldeter Providerpfad:
  `/kunden/homepages/16/d101506010/htdocs/competencehub`
- Betreiber: Donner + Partner; verantwortlich: Lars Donner
- Operativer Admin: Manuel; technischer Break-glass-Kontakt: Thomas Ross
- Janay verantwortet die Kontaktmailbox; eine Vertretung ist nicht benannt.
- Host-Key: ED25519
  `SHA256:1gx2w8Rtv3wCgi7Jh8myf/KVd72cRQbow03UP8P095Q`

## Aktueller Produktionsstand

- Website-Source: `1b4e33efa5e1`
- Artefakt:
  `competence-hub-website-1b4e33efa5e1-20260925T121142Z.zip`
- Artefakt-SHA-256:
  `d80bd25977dfabf5d3ecf9892ed1747ff18b69a485d6b631ea0a0a459226dd5f`
- Umfang: 52 Dateien; `index.html` wurde zuletzt aktiviert.
- Inhalt: zwei reale Coachprofile, sechs ausdrueckliche Demoprofile,
  freigegebenes Janay-Portrait und freigegebener Telefonlink.
- Lokal: 41 Astro-Dateien ohne Diagnose, 33 Seiten, 1.237 interne Referenzen
  und 865/865 Edge-Pruefungen einschliesslich Textgeometrie.
- Produktion: Kern-, Rechts-, Robots-, Sitemap- und 404-Routen gruen;
  HTTP/Alias-Redirects und Sicherheitsheader gruen; 72/72 Desktop-/390-Pixel-
  Edgechecks ohne Ueberlauf oder JavaScriptfehler. Demo-, Kalender-, Kontakt-,
  Altprofil- und Sitemap-Grenzen sind enthalten.
- SB-54 ist geschlossen: Der Mindforge-Abschnitt `Klare Grenze` bleibt bei
  2048/1440/1280/960/390 und 1280@200% innerhalb seiner Spalten, stapelt an
  kleinen Breiten und besteht 72/72 cache-frische Produktionschecks.

## Rollbackstand

- Aktuelle Pre-SB-54-Sicherung:
  `release-artifacts/website-sftp-rollback/20260925-pre-1b4e33e` mit exakt 52
  zu `d051a2e27f22` bytegleichen Dateien; Inventar-SHA-256
  `128fbf5c10e485f954a04563a69101b9763b70fc9ba8e079f7d411c6b77bb29a`.
  Sie ist nur Notfall-Rollback, weil sie den bekannten visuellen P0 zurueckbringt.

- Vollstaendige Beweissicherung:
  `release-artifacts/website-sftp-rollback/20260925-pre-d051a2e` mit 56 Dateien;
  Inventar-SHA-256
  `25fd6153067a9571d69403a624879b39dff7f773a0e7fdc2dad017585c6813ce`.
  Sie enthaelt vier alte, unreferenzierte Assets und ist kein oeffentliches
  Rollbackziel.
- Zulaessiges Rollback:
  `release-artifacts/website-sftp-rollback/20260925-safe-d493e195f80a` mit 52
  Dateien; Inventar-SHA-256
  `a815bb6022ec9d444195749e6b3d669037015561838d12b1da6b009c2f3d17fb`.
  Es entspricht dem zuvor oeffentlich verifizierten Artefakt `d493e195f80a`
  mit ZIP-SHA-256 `6084fb45396a54ec067487c2c4707b2cfcbe8a8c2eb9d3583fb89ce357177a91`.
- Aeltere Archive und die rohe Vorabkopie duerfen wegen abgeloester
  Identitaeten beziehungsweise alter Assets nicht oeffentlich restauriert
  werden.

## Betrieb und Stop-Regeln

1. Vor jedem neuen Upload Host-Key, Webroot, Freigabe, Clean-Artefakt und eine
   neue vollstaendige Remote-Sicherung pruefen.
2. Manuel kopiert das SFTP-Passwort. Deshalb Terminal A fuer Login/SFTP und
   Terminal B zum Laden der Befehlsdatei erst nach sichtbarem `sftp>` nutzen.
3. Bei unbekannten Remote-Dateien, Providerkonfiguration, 5xx/403,
   Redirectschleife, fehlenden Assets oder Sicherheitsbefund stoppen.
4. `index.html` zuletzt aktivieren; danach kanonische Domain, Alias, Kernrouten,
   Kontakt, Bilder, Mobilansicht, 404 und Sicherheitsheader von aussen pruefen.
5. Feature Freeze bis nach der Messe: waehrend Manuels Abwesenheit nur
   Incident-Recovery; keine Portal-/Backend-Aktivierung und keine CAL-1-,
   CAL-2- oder FIN-01-Arbeit.

## Naechste Pruefungen

- Einmalige reale Kontaktmail-Zustellung an Janay pruefen und Empfang oder
  Routingluecke dokumentieren.
- Vor der Messe am 17.10. Kernrouten, Mobilansicht, Kontaktweg, Zertifikat und
  Redirects erneut pruefen.
- Weitere CAL-1-, CAL-2- und FIN-01-Arbeit erst nach der Messe und separatem
  Gate wieder aufnehmen.
