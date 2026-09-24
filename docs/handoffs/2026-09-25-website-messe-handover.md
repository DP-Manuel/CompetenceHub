# Website Messe-Handover

Stand: 24.09.2026

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

- Website-Source: `d493e195f80a`
- Tooling-/Handover-Source: `1f0453c`
- Artefakt:
  `competence-hub-website-d493e195f80a-20260924T115022Z.zip`
- Artefakt-SHA-256:
  `6084fb45396a54ec067487c2c4707b2cfcbe8a8c2eb9d3583fb89ce357177a91`
- Umfang: 52 Dateien; `index.html` wurde zuletzt aktiviert.
- Inhalt: zwei reale Coachprofile, sechs ausdrueckliche Demoprofile,
  freigegebenes Janay-Portrait und freigegebener Telefonlink.
- Lokal: 41 Astro-Dateien ohne Diagnose, 33 Seiten, 1.303 interne Referenzen
  und 803/803 Edge-Pruefungen.
- Produktion: Kern-, Rechts-, Robots-, Sitemap- und 404-Routen gruen;
  HTTP/Alias-Redirects und Sicherheitsheader gruen; 22/22 fokussierte
  Desktop-/390-Pixel-Edgechecks ohne Ueberlauf oder JavaScriptfehler.

## Rollbackstand

- Verzeichnis:
  `release-artifacts/website-sftp-rollback/20260924-pre-d493e19`
- Umfang: 54 Dateien. 52 stimmen bytegenau mit dem vorherigen, oeffentlich
  verifizierten Release `9955e03` ueberein; zwei zusaetzliche alte Astro-Assets
  sind unreferenziert und wurden vorsorglich mitgesichert.
- SHA-256-Inventar:
  `release-artifacts/website-sftp-rollback/20260924-pre-d493e19-SHA256SUMS.txt`
- Inventar-SHA-256:
  `a497f9e51fe5d33c4cd70ff5b367d79acc45a49f6d8b32b4688c748e93e2a3f5`
- Aeltere Archive vor `9955e03` enthalten abgeloeste Coachidentitaeten und
  duerfen nicht als oeffentlicher Rollback verwendet werden.

## Betrieb und Stop-Regeln

1. Vor jedem neuen Upload Host-Key, Webroot, Freigabe, Clean-Artefakt und eine
   neue vollstaendige Remote-Sicherung pruefen.
2. Manuel kopiert das SFTP-Passwort. Deshalb Terminal A fuer Login/SFTP und
   Terminal B zum Laden der Befehlsdatei erst nach sichtbarem `sftp>` nutzen.
3. Bei unbekannten Remote-Dateien, Providerkonfiguration, 5xx/403,
   Redirectschleife, fehlenden Assets oder Sicherheitsbefund stoppen.
4. `index.html` zuletzt aktivieren; danach kanonische Domain, Alias, Kernrouten,
   Kontakt, Bilder, Mobilansicht, 404 und Sicherheitsheader von aussen pruefen.
5. Waehrend Manuels Abwesenheit nur freigegebene Inhaltskorrekturen oder
   Incident-Recovery; keine Portal-/Backend-Aktivierung.

## Naechste Pruefungen

- Einmalige reale Kontaktmail-Zustellung an Janay pruefen und Empfang oder
  Routingluecke dokumentieren.
- Vor der Messe am 17.10. Kernrouten, Mobilansicht, Kontaktweg, Zertifikat und
  Redirects erneut pruefen.
- Weitere CAL-1-Arbeit erst nach separatem Gate wieder aufnehmen.
