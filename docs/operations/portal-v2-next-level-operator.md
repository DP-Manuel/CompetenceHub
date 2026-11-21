# Portal V2 Next Level: Entscheidung und Betrieb

**Stand: 21.11.2026. NO-GO für VPS-Änderungen, persönliche Aktivierung und
Echtdaten.** Technischer Operator ist Manuel. Diese Unterlage ist ein Planungsstand,
keine fachliche Abnahme, technische Review-Freigabe oder Ausführungserlaubnis.

## Ausgangslage und EDV-Entscheidung

- **Letzter belegter VPS-Stand (15./16.11.):** V1.2 `5a555e9a9aae`,
  `competence_hub_staging` mit Ledger `0001..0006` und 27 Tabellen,
  API/TLS/PostgreSQL nur auf Loopback, sechs Referenzdienste einschließlich
  Chatbot. Der [SSH-Versuch am 21.11.](portal-v2-pilot-gates-2026-11-21.md#j-operations-and-publication-evidence)
  endete bei der Anmeldung; kein aktuelles Dienst-, TLS- oder DB-Inventar.
  Das ist kein Ausfallnachweis. Die [lokale Next-Level-Probe](../handoffs/2026-11-21-v2-next-level.md)
  umfasst `0013` und einen Restore synthetischer Daten, aber keine Live-Recovery.
- **EDV: Antwort nicht belegt.** Manuel gleicht den
  [EDV-Entwurf](edv-portal-dns-smtp-2026-11-10.md) vor Versand mit dem
  [aktuellen Fragenblock](portal-v2-pilot-gates-2026-11-21.md#k-onboarding-and-edv-decisions)
  ab. Benötigt: verbindlicher App-FQDN und DNS-Ziel, erlaubter TLS-/ACME-Weg
  samt Erneuerungs- und Alarmverantwortung, geschützter Zugang (VPN/freigegebene
  Quellnetze) und SMTP-Freigabe samt Versandidentität, Zustellregeln und sicherem
  Übergabeweg. Vorschläge sind keine Konfiguration; offene Punkte mit
  Zuständigkeit und Termin festhalten. Bis zu verifiziertem HTTPS-`/portal/` und
  eigener Publikationsfreigabe bleibt `WEBSITE_PORTAL_URL` ungesetzt. Kein
  Ersatzversand, keine allgemeine Öffnung.
- **Private TLS-Frist separat.** Der am 16.11. [abgenommene](pilot-tls-renewal-2026-11-16.md#actual-acceptance)
  `localhost`-Leaf läuft laut historischem Receipt ab am
  **30.11.2026, 19:09:39 MEZ (18:09:39 UTC)**. Am 21.11. liegt das noch
  bevor; ob der Leaf aktuell ausgeliefert wird, ist unbewiesen. Der alte
  Leaf ist nur bis 24.11., 18:20:45 MEZ, als TLS-Rückfall geeignet.
  Entscheidung vor Ablauf mit Zeitreserve: nur bei bestätigten EDV-Eingaben
  und gesondert abgenommener, pin-kompatibler Zugriffslösung darauf umstellen;
  sonst bei weiterem Pilotbedarf ein separates privates TLS-Erneuerungsfenster
  beantragen. Ohne eines von beiden Zugang nach Ablauf aussetzen. Vor V2
  müssen strikte CA-/Hostnamenprüfung, Leaf-Pin und negativer Trust-Test
  passen, und der V1.2-Rückweg muss für Fenster **und** Rückfallreserve gültig
  sein. Abweichung oder Ablauf: STOP, kein TLS-Bypass. Private TLS-Freigabe
  ersetzt weder EDV-App-HTTPS noch SMTP-/Onboardingfreigabe.

## Unabhängig wiederherstellbare Sicherung

Der [tatsächliche DPAPI/BitLocker-Restore vom 15.11.](portal-v12-calendar-ux-2026-11-13.md#v12-tats%C3%A4chlich-abgenommen)
belegt einen damaligen Rückfall mit derselben Windows-Identität, keine
Wiederherstellung ohne den ursprünglichen Rechner und Benutzer. Zweite Kopie
desselben DPAPI-Ciphertexts genügt nicht. **Unabhängige Recovery: OFFEN.**

1. **Ziel und Schlüssel vorher qualifizieren.** Manuel benennt genau ein
   bereits D+P-freigegebenes, verschlüsseltes Off-VPS-Ziel (vorhandener
   Custody-Rechner oder geeignetes Medium) und einen getrennt nutzbaren
   Restore-Arbeitsplatz. Aktuell nachweisen: Zugriff mit vorhandenen
   Mindestberechtigungen auch ohne die alte Windows-Identität, Verschlüsselung
   aktiv, unabhängiger Entsperr-/Recovery-Weg, les- und schreibbares exklusives
   Ziel und genügend Platz/Quote auch im geschützten Arbeitsbereich
   (Erstprobe: mindestens 4× erwartete Nutzlast + 512 MiB). Nur genehmigt
   mit harmloser Testdatei Schreiben und Reread prüfen. Der bekannte Key-Stick ist
   kein DB-Ziel, SMB ist nur geplant, und es gibt keine automatische Freigabe
   für einen zweiten Host. Details: [Zielvertrag](backup-destinations-2026-11-04.md).
2. **Portables Format, keine neue Technik.** Vorhandenen PostgreSQL-Custom-Dump-
   und OpenPGP-Pfad aus [B/R](controlled-backup-key-rebase-2026-11-04.md#storage-and-independent-recovery)
   verwenden, aber nur mit aktuell freigegebenem Empfänger und echtem
   Kaltstart-Recovery-Beleg: passphrasengeschützten Recovery-Export aus
   getrennter Verwahrung in frisches isoliertes GPG-Home laden und mit separat
   verfügbarer Passphrase in privater Pinentry ohne ursprüngliches Home,
   Agent-Cache oder DPAPI entschlüsseln. Entsperr-/Schlüsselmaterial nicht beim
   Dump ablegen; auf dem VPS wäre nur der öffentliche Empfänger nötig.
   Kein nachgewiesener Zugriff,
   passender Key, Platz oder freigegebenes Ziel: STOP. GPG/R2 bleibt pausiert;
   weder Alt-Key-Versuch noch neue Technik, Hardware, Konten oder Infrastruktur
   aus diesem Plan ableiten. Manuel bleibt technischer Custodian; keine neue
   Schlüsselrolle für Janay. Für einen vollständigen Dienstwiederanlauf
   zusätzlich separat belegte Verfügbarkeit der nötigen Runtime-/App-Schlüssel
   und Konfiguration verlangen; DB-Restore allein beweist keinen Login.
3. **Aktuelles Set erzeugen und aus genau dieser Kopie testen.** Nur im
   genehmigten ruhigen Fenster einen konsistenten `0006`-Snapshot samt
   Vergleichsbaseline nach dem
   [Backup-/Restore-Runbook](../architecture/postgresql-backup-restore-runbook.md#external-copy-gate)
   und dem neu gebundenen B/R-Verfahren erzeugen. Nur den vollständigen
   Satz (beide GPG-Payloads, Metadaten, Prüfsummen, `COMPLETE`) ohne
   Überschreiben übernehmen, SHA-256 vor Transfer und beim Reread
   vergleichen. Daraus auf dem unabhängigen Weg in eigener
   netzloser PG16-Instanz (vorhandenes gepinntes Image, keine Ports) restaurieren.
   Keine Globals oder Rollenpasswörter einspielen; erforderliche Testrollen
   isoliert vorhalten. `0001..0006`, alle 27 Tabellen (Zeilen und Digests),
   Schema, Owner/Grants und Sequenzstände gegen die ruhige Quelle prüfen.
   Weder der generische Restore-Check ohne ACLs noch der
   [B/R-Helper](../../deploy/scripts/restore-competence-hub-snapshot.ps1)
   mit Baseline-Zählwerten allein deckt diese Parität ab. Quelle erneut
   auf Drift prüfen; nur eigene Probe und temporären Klartext bereinigen,
   verschlüsseltes Set behalten.
4. **Beleg statt Zusage.** Receipt mit UTC-Zeit, Quell-/Zielkennung, Umfang,
   Set-/Baseline-SHA-256, freigegebenem Empfänger-Fingerprint, Schutz-/ACL-/
   Kapazitätsnachweis, unabhängigem Decrypt, Parität, Laufzeit und Cleanup
   protokollieren. Keine Zugangsdaten, privaten Pfade oder Zeileninhalte in
   Git/Chat. Fehlender Beleg oder Drift = kein Clone-Gate. Vor dem Eingriff
   Frische und unveränderten Referenzstand belegen und gemessene Restore-Zeit
   gegen das genehmigte Fenster prüfen. Keine RPO-/RTO-Zusage aus einer Probe.

## Exakte Go/No-Go-Folge für den synthetischen Pilot

1. **Freigabebasis:** Gemeinsame lokale Abnahme durch Manuel und Frau Rappelt
   dokumentieren (offen). `0013` erweitert bestehende Coaching-Anfragen,
   bleibt rein synthetisch und ändert nicht die CAL-2-Platzbindung. Geänderte
   Anfragepfade und Migration aus gefülltem Stand gezielt nachweisen. Nur ein
   neu exakt gebundenes Paket mit getestetem Commit, ZIP-/Testbeleg-SHA-256,
   [Manifest `competence-hub-private-v2/3`](../../deploy/v2/v2_package.py),
   Migrationen `0007..0013`, `deployment_authorized: false` und passenden
   Helfern verwenden. Das bisherige `0012`-Manifest und dessen
   Schema-Approval sind dafür **nicht verwendbar**.
2. **Read-only, Backup, Restore:** Manuells phasenbezogene Grants binden
   Commit, ZIP-/Evidenz-Hash, Ziel, erlaubte Aktion und Zeitfenster. Zuerst
   V1.2, sechs Dienste, Loopback/Ports, striktes TLS und ruhige synthetische
   Quelle aktuell belegen; dann frische unabhängige Sicherung und exakten
   Restore nach obigem Gate abnehmen. Alte Receipts begründen keinen PASS.
3. **Clone und Schema getrennt:** Gesondert freigegebenen, unbedienten
   `competence_hub_v2_pilot` aus der verifizierten Kopie provisionieren,
   `0006`-Parität, Provenienz und unverändertes Original belegen. Erst
   danach `V2_SCHEMA_ONLY_0007_TO_0013` mit `real_coach_import_authorized: false`
   an Cluster-ID, Clone-OID, Referenz-, Restore- und Paritäts-Receipt-Hashes
   sowie UTC-Ablauf (max. 24 h) binden; Grant-Datei separat per SHA-256
   pinnen. Nur dort atomar migrieren,
   Altwerte erhalten und neue Notiz-/Historientabellen zunächst leer
   nachweisen. `ready` muss vor Aktivierung wiederverwendbare Sessions,
   Challenges, Einmaltokens und offene Zustellungen ausschließen. Nie Original-
   Sitzungen dafür invalidieren. Bei Drift, fehlender Bereitschaft oder
   unklarem Commit stoppen und Zustand prüfen, nicht blind wiederholen.
4. **Aktivierung / Rückfall:** Nur separat freigegebene V2-Loopback-Dienste
   `8002/8444`, eigenes Browserprofil, Einladungen und SMTP aus. Kompakter
   Smoke: TLS/Readiness, anonymer Zugriff verweigert, MFA/RBAC/Origin/CSRF,
   eine synthetische `0013`-Anfrage mit Wiedervorlage und begrenzter
   Coach-Sicht, Ausschluss der fremden Firma, ein CAL-2-Vorgang mit Rückfrage
   sowie Persistenz nach V2-Neustart. V1.2 und alle sechs Dienste bleiben
   erhalten. Bei Fehler nur V2 schließen/stoppen und den unveränderten
   V1.2-Zugang strikt neu prüfen; keine V2-Listener, ursprüngliche Referenz
   und sechs Dienste nachweisen. Clone geschützt behalten; kein Drop, keine
   Down-Migration, kein In-place-Restore, kein Eingriff in den Chatbot.
   Ist V1.2 nicht gesund oder Originaldaten zeigen Drift, Incident-Entscheidung
   einholen, keine improvisierte Reparatur. Ablauf und Befehle erst aus dem
   zur `0013`-Freigabe passenden Stand des
   [Private-Staging-Runbooks](portal-v2-private-staging.md) übernehmen.

## Tagesbetrieb und Datengrenzen

- **Start:** Bestehenden V1.2-Pilot nur über den [festen Teststarter](../handoffs/PORTAL_TESTZUGAENGE.md)
  öffnen, keinen Installer erneut starten. V2 bis zu eigener Freigabe nur
  [lokal vorführen](../handoffs/2026-11-21-v2-next-level.md#gemeinsame-vorf%C3%BChrung).
  Getrennte Rollenfenster nutzen, abmelden, nur den eigenen Tunnel schließen.
- **Benutzen:** Unter **Anfragen** erfassen Admin/Intern synthetische Anliegen,
  Zuständigkeit und Wiedervorlage. Coach bearbeitet eigene Angebote und sieht
  nur die für ihn freigegebenen Anfrageinfos; interne Notizen bleiben intern.
  Reviewer prüft CAL-1/CAL-2 und Rückfragen ohne Adminrechte. Firma nutzt nur
  eigene unverbindliche Vorgänge; Firma B prüft die Mandantentrennung. Admin
  betreut außerdem Zugriffe/Audit; Kundenpflege bleibt im Admin-/Internbereich.
  Privatkunde ist kein Login. Keine echten Profile, Zuordnungen, Buchungen,
  Einladungen oder Nachrichten. Bei Zugriffsfehlern nur bereinigten STOP
  melden; keine Resets oder Rechteausweitung.
- **Kontrollieren:** Manuel prüft an Pilotbetriebstagen Freigabestatus,
  Readiness/TLS-Frist und letzter Sicherungs-/Restore-Beleg (Alter, Integrität,
  Ergebnis); prüft Backup-/Monitorstatus nur, soweit freigegeben und aktiv.
  Fehlendes oder fehlerhaftes Set als offen melden, keine Schreibfreigabe
  darauf stützen. Timer und Alarmaktivierung bleiben separat; vor Echtbetrieb
  bestätigte Erfolgs- und Testfehlerzustellung und Notfallzugriff verlangen.
- **Datenschutz vor Echtdaten:** Verantwortliche für Fachlichkeit und
  Datenschutz/Legal bestätigen Zweck, minimale Felder und Leserechte,
  Aufbewahrung und Löschweg für Anliegen, Kunden, Auth/Audit, Logs sowie
  Clone und Sicherungskopien (einschließlich erneut anzuwendender Löschregeln
  nach Restore). 30 tägliche/12 monatliche Sets sind nur der bisherige
  [Pilotwert](pilot-account-operations-decisions-2026-09-11.md), keine
  Echtdaten- oder Löschfreigabe. Keine Aufbewahrung oder Zustellung als
  abgenommen melden. Persönliche Aktivierung bleibt hinter dem
  [Einzelfall-Gate](portal-v2-pilot-gates-2026-11-21.md#k-onboarding-and-edv-decisions),
  ohne Rollen-/UUID-Ableitung und ohne Freigabe für REAL APPLY.

**Nächster Block:** Manuel entscheidet den geschützten Zugang vor Ablauf.
Inputs: EDV-Antwort oder benannte Zuständigkeit/Frist je offenem Punkt und
TLS-Receipt vom 16.11. Deliverable/DoD: DNS/TLS/Zugang/SMTP abgeglichen und
ein konkretes privates Erneuerungsfenster zur gesonderten Freigabe oder ein
tragfähiger, gesondert abzunehmender HTTPS-Weg benannt; andernfalls STOP.
Wiederverwendbare Regel: Historischer Restore, unabhängige Entschlüsselung
und erfolgreicher Runtime-Rückfall sind drei getrennte Nachweise.
