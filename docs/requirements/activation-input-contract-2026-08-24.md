# Activation Input Contract

Stand: 2026-08-25

## Zweck

Dieser Vertrag ordnet externe Freigaben und Betriebsnachweise den Activation
Gates des Competence Hub zu. Fachliche Grundlage ist das lokal freigegebene
Activation Input Pack vom 24.08.2026. Die private Arbeitsmappe bleibt eine
Operator-Eingabe und wird nicht in das Repository kopiert.

## Datenregel

In Projektdateien duerfen nur Entscheidungen, Status, Owner, Termine,
Hostnamen, Ports, Fingerprints und Evidence-Verweise stehen. Passwoerter,
Private Keys, Recovery Keys, SFTP-/SMTP-Zugangsdaten, personenbezogene
Produktivdaten und Vertragsrohtexte bleiben ausserhalb von Git.

Fehlende Werte werden nicht erraten. Ein neuerer ausdruecklich bestaetigter
Operator-Input hat Vorrang vor einem aelteren Projektstatus; der Konflikt wird
im Projektlog dokumentiert.

## Input-Bereiche

| Bereich | Mindestnachweis | Erlaubte Folgeaktion | Bei fehlendem Nachweis |
| --- | --- | --- | --- |
| SB-23 Backup | kontrolliertes verschluesseltes Medium, verschluesselter synthetischer Satz, identische Hashes, Restore aus exakter externer Kopie, Servicehealth | G-DATA-Evidence aktualisieren | keine Echtdaten |
| EDV DNS/TLS/SMTP | bestaetigter App-FQDN, DNS-Ziel, TLS-Pfad, SMTP-Vertrag und Systemabsender | hostbezogene Konfiguration rendern und nativ validieren | Platzhalter behalten, keine Live-Mail |
| Legal/Release | Betreiber, Rechtstexte, Inhalts- und Produktionsfreigabe | Website-Produktionsgate vorbereiten | kein beworbener Livegang |
| Janay Onboarding | Termin, persoenliche Einladung, MFA, Least Privilege und dokumentierte Abnahme | benannten Pilotzugang aktivieren | nur synthetische Abnahme |
| Mailbox | Owner, Vertretung, interner Reaktions- und Eskalationsweg | Kontaktprozess freigeben | keine oeffentliche Reaktionszeit versprechen |
| Successor/Break Glass | benannte Notfallperson, benoetigte Rollen und gepruefter Runbook-Pfad | Betriebsrisiko neu bewerten | Produktionsrisiko offen lassen |
| Erste Firma | G-DATA und G-PROD geschlossen, Rechtsgrundlage/Freigabe belegt | freigegebenen Minimaldatensatz erfassen | keine Echtdaten eingeben |

## Routing

1. Ist SB-23 ausfuehrbar, hat der externe Backup-/Restore-Nachweis Vorrang.
2. Trifft vorher die vollstaendige EDV-Antwort ein, wird nur die hostbezogene
   Konfiguration bearbeitet; Secrets bleiben extern.
3. Legal-, Onboarding- und Mailbox-Eingaben schliessen ausschliesslich ihre
   jeweiligen Gates.
4. Solange kein Gate ausreichend belegt ist, beginnt keine neue Featurearbeit.
   Es wird nur ein bereits geplanter unabhaengiger sicherer Slice gezogen.

## Aktueller Precheck

- `D:` wurde am 25.08.2026 als gesunder, fast leerer 2-GB-USB-Datentraeger mit
  FAT-Dateisystem erkannt.
- BitLocker To Go wurde am 25.08.2026 aktiviert und als `FullyEncrypted`,
  `ProtectionStatus On`, `Aes128`, 100 Prozent und `Unlocked` nachgewiesen.
  Windows hat damit die Datentraegerverschluesselung hergestellt; OpenPGP
  schuetzt spaeter zusaetzlich jede Backup-Nutzlast.
- Das lokale Systemlaufwerk `C:` der Restore-Umgebung wurde ebenfalls als
  `FullyEncrypted`, Schutz aktiv, `XtsAes128`, 100 Prozent nachgewiesen.
- Der physische Aufbewahrungsort des USB-Sticks ist der Safe. Janay Rappelt ist
  als Notfall-/Recovery-Verantwortliche benannt. Die tatsaechliche sichere
  Hinterlegung des BitLocker-Recovery-Codes bleibt noch nachzuweisen.
- Es wurden keine Backupdaten, Secrets oder Echtdaten auf `D:` geschrieben.

## Abschlussregel

Nach einem Gate-Nachweis werden `PROJECT_PLAN.md`, `PROJECT_STATUS.md`,
`PROJECT_LOG.md`, das Readiness Gate Board und der Go-Live Evidence Index
synchronisiert. Deployment und Echtdaten bleiben jeweils separate Freigaben.
