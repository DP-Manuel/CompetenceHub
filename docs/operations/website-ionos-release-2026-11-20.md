# IONOS Website-Release 20.11.2026

**Status: Vorprüfung bestanden, Produktionsupload noch nicht ausgeführt.**
Manuel hat den nach gemeinsamer Abnahme mit Frau Rappelt genau gebundenen
Website-Kandidaten für IONOS freigegeben. Die Freigabe umfasst die frische
Webrootsicherung, den kontrollierten Upload und einen nötigen Rückfall.
Kein VPS, keine Datenbank, Portal-Aktivierung, Konten, E-Mails oder Pages.

| Nachweis | Stand |
| --- | --- |
| Fachliche Abnahme | 20.11 erfolgreich und ohne Beanstandungen, [Abnahmebericht](../handoffs/2026-11-20-feedback-platform.md) |
| ZIP / Quelle | `competence-hub-website-b9b90bfb8885-20261120T150236Z.zip`, Quelle `b9b90bfb88852a9dcffb5c1e78595340551b5b11`; `5a423be` ist Dokumentation |
| Vollständiger SHA-256 | `e02b574bcb57844b69c9422b3517545d1ddc3811f0af0e101f0124f704b6fe2c` |
| Manifest und Inhalt | PASS: unverändert, sauberer Build, 64 Dateien, acht freigegebene Profile, kein Hupp-/Rappelt-Neuprofil und keine privaten Portal- oder Testdaten |
| Öffentlicher Ausgangsstand | PASS: 54/54 abrufbare Vorgängerdateien exakt gegen `11cb1ea`; `.htaccess` ist nur per SFTP prüfbar |
| Browser vor Upload | PASS am lokal aus dem exakten ZIP bereitgestellten Kandidaten: 1440 px, 390 px, nativer 200-%-Zoom, Tastatur, acht Profilpfade, Finder und Rechtswege. Kein Produktionsnachweis. |
| SFTP | Bestätigter ED25519-Pin, Anmeldung und 55 Downloads erfolgt. Vollständige Verzeichnisliste noch nicht ausgewertet; keine Aussage über zusätzliche Remotepfade. |
| Rückfall | Frische Kopie: 55/55 bekannte Dateien bytegenau, 11.932.989 Byte, einschließlich `.htaccess`; BitLocker C: und restriktive ACL geprüft. Neues Archiv getrennt entpackt, 55/55 Hashes erneut exakt. SHA-256 des Archivs: `7bec6352a1ffe5d5a8ef335259cc7e572e2f8f760bf2d6281aaa1868fc079aa0`. |
| Upload / Readback / Produktionsbrowser | Noch nicht ausgeführt |

## Geplanter Umfang

17 der 64 Zieldateien sind unverändert, 35 werden ersetzt, 12 hinzugefügt.
Die drei vom exakten Vorgängerpaket bekannten obsoleten Assets werden nach
Aktivierung entfernt, damit das Webroot bytegenau dem neuen Paket entspricht.
Keine unbekannten Pfade überschreiben oder entfernen. Vorhandene Inhalte,
Unterlagen und Rechte von Frau Hupp bleiben unangetastet und unveröffentlicht.

Lokale private Ablage (nicht im Git):
`release-artifacts/website-production/20261120-b9b90bf/`.
Dort liegt das SHA-256-Dateiinventar der 64 Zieldateien. Erst nach
Pfad-/Größen-/Hashparität und getrenntem Restore werden die konkreten
Upload-, Rücklese- und Rückfallbefehle freigegeben. Bei einer kritischen
Produktionsabweichung alte Dateien aus der frischen Sicherung zurückspielen
und nur die eigenen neuen Pfade entfernen.

**Nächster Block:** Vollständige SFTP-Verzeichnisliste einschließlich `pwd`
gegen die 55 bekannten Vorgängerdateien auswerten. Danach ausschließlich das
geprüfte Paket übertragen und per SFTP, HTTPS und Browser abnehmen.
