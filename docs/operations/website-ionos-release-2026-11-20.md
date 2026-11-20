# IONOS Website-Release 20.11.2026

**Release PASS.** [IONOS-Produktion](https://competencehub.donner-partner.de/)
entspricht bytegenau dem freigegebenen Website-Paket.
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
| SFTP-Inventur | PASS: Webroot `/`, 39 Verzeichnisse einschließlich Webroot, genau 55 erwartete Dateien mit passenden Größen. Keine zusätzlichen Pfade oder Verknüpfungen. |
| Rückfall | Frische Kopie: 55/55 bekannte Dateien bytegenau, 11.932.989 Byte, einschließlich `.htaccess`; BitLocker C: und restriktive ACL geprüft. Neues Archiv getrennt entpackt, 55/55 Hashes erneut exakt. SHA-256 des Archivs: `7bec6352a1ffe5d5a8ef335259cc7e572e2f8f760bf2d6281aaa1868fc079aa0`. |
| Upload und Rücklesen | PASS: 35 ersetzt, 12 hinzugefügt, 17 unverändert, drei obsolete Assets entfernt; alle 64 Zieldateien per SFTP zurückgelesen und bytegenau abgeglichen. |
| Öffentliches HTTPS | PASS: 63/63 abrufbare Paketdateien; drei alte Assets liefern keine alten Bytes. Kanonische Domain, HTTP-/Alias-Weiterleitungen und beide Rechtsziele geprüft. |
| Produktionsbrowser | PASS: Firefox bei 1440 px, 390 px und nativem 200-%-Zoom; Tastatur und öffentlicher Anfrageweg ohne Versand. |

## Veröffentlichter Umfang

Alle acht aktiven Coachprofile einschließlich Namenslinks wurden auf der
echten Website geprüft. Elisabeth Schwabauers Themen, geöffnete erste
Angebotsgruppe und Rückverlinkung sowie „Rhetorik & Vertrieb“ mit den
bestehenden Formaten funktionieren. Der öffentliche Kalender zeigt einen
Leerzustand statt Testdaten. Kein neues Profil von Frau Rappelt, keine
Reaktivierung von Frau Hupp, keine neuen Preise, private API oder unbestätigter
Portal-Login. Impressum und Datenschutz führen zu den bestätigten D+P-Zielen.

Lokale private Ablage (nicht im Git):
`release-artifacts/website-production/20261120-b9b90bf/`.

| Beleg | SHA-256 / Ergebnis |
| --- | --- |
| `published-files.sha256` und `readback-files.sha256` | Identische Liste aller 64 veröffentlichten Pfade: `efbc6c818d74168adaa1c6f5e0223e20d1794aa09bd706c1440b4696a6aea854` |
| `release-receipt.json` | `24fe179c83e930b9b37e942905f25dfd8fe05004acd0843aa1112f5e84e356a3` |
| `SFTP-ROLLBACK-COMMANDS.txt` | Bindet den frisch wiederhergestellten Stand und betrifft ausschließlich die vom Release geänderten Pfade. Kein Rückfall erforderlich oder ausgeführt. |

## Abweichungen

Zwei entfernte Asset-URLs liefern Apache `300 Multiple Choices` statt `404`:
Die Antwort meldet die alte Datei als fehlend und schlägt ausschließlich
Pfade aus dem neuen geprüften Paket vor. Sie liefert weder die alten Bytes
noch eine automatische Weiterleitung. Das dritte alte Asset liefert `404`.
Ein erster Browserlauf wartete beim Kalender vergeblich auf das allgemeine
Ladeereignis. Beide Kalenderseiten antworteten unabhängig mit HTTPS `200`;
der zweite vollständige Durchlauf mit gezielten DOM-Prüfungen war grün.
Keine zusätzliche Produktionsänderung für diese Befunde.

## Abschluss

GitHub Pages bleibt bei Lauf `44149446991`, Quelle `11cb1ea`. VPS, Portal,
PostgreSQL, Benutzerkonten und E-Mail unverändert. Ausschließlich der
lokale Betriebsrecord wurde nachgetragen. Keine weitere Produktionsänderung
nach Abschluss der Prüfung.

**Nächster Block:** EDV-Rückmeldung zu App-Adresse, dauerhaftem HTTPS,
Zugriffsschutz und SMTP abgleichen; keine Änderung am jetzt abgenommenen
Website-Release.
