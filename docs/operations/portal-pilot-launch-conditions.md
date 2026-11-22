# Portal-Pilot: Startbedingungen

**Stand: 22.11.2026. Entscheidung fuer Manuel, Fachabnahme und EDV.**
Bestehender V1.2-Testzugang: nur synthetisch und nur bei gueltiger, strikt
gepruefter Verbindung. V2: lokal vorfuehrbar, **kein Go fuer VPS-Aenderungen,
persoenliche Zugaenge oder Echtdaten**. Diese Unterlage erteilt keine Freigabe.

## Was belegt ist

- **15./16.11., tatsaechlicher VPS-Betrieb:** [V1.2-Abnahme](portal-v12-calendar-ux-2026-11-13.md#v12-tats%C3%A4chlich-abgenommen)
  und [TLS-Abnahme](pilot-tls-renewal-2026-11-16.md#actual-acceptance) sind der
  letzte belegte Stand: `5a555e9a9aae`, Ledger `0001..0006`, 27 Tabellen in
  `competence_hub_staging`, API/TLS/PostgreSQL auf Loopback und sechs Dienste
  einschliesslich Chatbot. Beide oeffentlichen Receipts lokal erneut gegen ihre
  SHA-256-Pins geprueft: PASS. `migrations: []` bedeutet kein Schemaeingriff in
  diesen Fenstern, kein leeres Ledger. Janays fachliche V1.2-Abnahme ist
  [gemeldet und abgeschlossen](portal-v12-calendar-ux-2026-11-13.md#fachliche-abnahme1611).
- **21.11., aktueller Betriebsstand nicht belegt:** Der
  [Anmeldeversuch](portal-v2-pilot-gates-2026-11-21.md#j-operations-and-publication-evidence)
  endete vor der Ausfuehrung der Remote-Abfragen; kein Dienst-, TLS- oder
  DB-Inventar und kein Ausfallnachweis. Am 22.11. nur lokale Aktenpruefung,
  kein SSH und kein neuer Live-Check.
- **21.11., V2 nur lokal:** [Next Level](../handoffs/2026-11-21-v2-next-level.md#pr%C3%BCfnachweis-und-releasepaket)
  belegt 45 integrierte Checks, isolierte Migration bis `0013`, synthetischen
  Restore und Offline-Installation. ZIP und `tested-source.json` fuer `a6bea57`
  lokal gegen ihre SHA-256-Pins geprueft; `MANIFEST.json` bindet beide historischen
  Receipts, Format `competence-hub-private-v2/3`, `0007..0013` sowie
  `deployment_authorized: false` und `real_coach_import_authorized: false`.
  Gemeinsame V2-Fachabnahme und gesprochener Screenreader-Smoke sind offen.
- **22.11., aktueller lokaler Kandidat:** [Pilot-Readiness mit Paketnachweis](../handoffs/2026-11-22-v2-pilot-readiness.md)
  belegt getrennte synthetische Linux-Quell-/Recovery-Instanzen, OpenPGP und
  einen funktionalen Start aus der gesicherten Konfiguration. Kein Nachweis
  fuer echte VPS-Daten, aktuelle TLS-Auslieferung oder Produktionsbetrieb.

## EDV und TLS: eine Entscheidungsliste

Keine bestaetigte EDV-Antwort in den vorliegenden Belegen. Manuel gleicht den
[Nachfassentwurf](edv-portal-dns-smtp-2026-11-10.md) vor einem Versand mit
dieser Frist und dem [Aktivierungsvertrag](../requirements/activation-input-contract-2026-08-24.md)
ab. EDV benennt je offenem Punkt Zustaendigkeit und verbindlichen Termin.

| Punkt | Entscheidung und erforderlicher Beleg | Bis dahin |
| --- | --- | --- |
| App-DNS | EDV bestaetigt verbindlichen App-FQDN und direktes VPS-Ziel fuer A; AAAA nur fuer genehmigtes, getestetes IPv6. Vorschlaege aus dem Entwurf sind keine Wertefreigabe. | Kein DNS-Auftrag, `WEBSITE_PORTAL_URL` bleibt ungesetzt. |
| App-HTTPS | EDV bestaetigt Zertifikatsweg, ACME-Challenge/CAA (falls zutreffend), Erneuerung und Alarmverantwortung. Betreiber weist striktes HTTPS fuer `/portal/` auf dem bestaetigten Host nach. | Kein Umstieg; privates `localhost`-TLS belegt kein App-HTTPS. |
| Zugriff | EDV bestaetigt Pilotkreis und VPN oder erlaubte Quellnetze. Zugelassenen Zugriff und Abweisung von aussen pruefen; API und PostgreSQL bleiben nicht direkt erreichbar. | Keine allgemeine Oeffnung. Bestehender privater Testzugang bleibt an seine eigene Freigabe und Pruefung gebunden. |
| SMTP | EDV bestaetigt Host/Port/TLS, Versandidentitaet, Absender/Reply-To, VPS-Senderecht, Limits und SPF/DKIM/DMARC sowie sichere Uebergabe. Freigegebene Testzustellung fuer Einladung und Reset tatsaechlich empfangen, nicht nur Outbox pruefen. | Kein Ersatzversand, keine echten Einladungen; keine Secrets per normaler Mail, Git oder Chat. |
| Privates TLS: vor Ablauf entscheiden | Akzeptierter Leaf laut Receipt bis **30.11.2026, 19:09:39 MEZ (18:09:39 UTC)**; der im Entwurf genannte 24.11. betrifft den alten Leaf (Rueckfall nur bis **24.11., 18:20:45 MEZ**). Mit Reserve entweder den bestaetigten, gesondert abgenommenen HTTPS-Weg waehlen oder bei weiterem Bedarf ein separates privates [TLS-Fenster](pilot-tls-renewal-2026-11-16.md) freigeben lassen. | Ohne nachgewiesenen Weg nach Ablauf den privaten Zugang aussetzen. Vor V2: CA/Hostname, Leaf-Pin, Readiness und negative Trust-Tests; gueltiger V1.2-Rueckweg fuer Fenster und Rueckfallreserve. Geaenderter Leaf erfordert akzeptierte Baseline und passende Starter-/Paket-Pins. Kein Bypass. |

Ein Website-Loginlink braucht zusaetzlich eine eigene
[Publikationsfreigabe](../architecture/website-portal-login-2026-11-17.md#genau-eine-sp%C3%A4tere-konfiguration).
VPS, IONOS und GitHub Pages bleiben [getrennte Umgebungen](../architecture/environment-policy.md).

## Tagesbetrieb nach Rolle

**Start und Ende:** V1.2 ueber den [festen Teststarter](../handoffs/PORTAL_TESTZUGAENGE.md),
V2 derzeit nur ueber die [lokale Vorfuehrung](../handoffs/2026-11-21-v2-next-level.md#gemeinsame-vorf%C3%BChrung).
Synthetische Rollenfenster getrennt halten. Kein Installer fuer den Einstieg;
nach der Arbeit abmelden und nur die eigene Sitzung bzw. den eigenen Tunnel
schliessen. Die persoenliche [Erstaktivierung](pilot-first-activation.md) gilt
erst nach eigener Freigabe.

- **Coach:** Im [Coach-Kalender](pilot-coach-guide.md) eigene Angebote entwerfen,
  einreichen und Rueckmeldungen als neue Revision bearbeiten. In V2 ausserdem
  nur ausdruecklich freigegebene Informationen zur aktuellen Zuweisung lesen.
- **Kalenderpruefung / Janay:** [Pruefliste](pilot-janay-guide.md) sichten,
  Aenderungen anfordern oder die gepruefte Revision im jeweiligen Testkalender
  freigeben. In V2 CAL-2-Rueckfragen und unverbindliche Entscheidungen pruefen;
  zustaendige Anfragen bearbeiten. Fachpruefung ist keine Konto- oder Key-Adminrolle.
- **Intern / Admin:** In V2 unter **Anfragen** zustaendige Faelle und faellige
  Wiedervorlagen sichten, Status und Aufgaben pflegen; interne Notizen von
  ausdruecklichen Coach-Freigaben trennen. Kundenpflege bleibt intern. Nur Admin
  verantwortet [Zugaenge und Verwaltungsnachvollzug](pilot-admin-guide.md);
  keine echten Einladungen oder Rollenaenderungen im synthetischen Pilot.
- **Firmenkontakt (V2):** Eigene CAL-2-Vormerkungen und Rueckfragen bearbeiten,
  Status eigener Coaching-Anfragen lesen. Keine Sicht auf andere Firmen oder
  interne Notizen; keine verbindliche Buchung oder Mail aus einem Entwurf.
  Privatkunde ist ein interner Datensatz, kein Login. Anfragen binden keine Plaetze.
- **Manuel, technischer Betrieb:** An Betriebstagen Freigabe, strikte Readiness,
  TLS-Frist, Alter/Integritaet des letzten Sets und letzten Restore-Beleg pruefen;
  Monitoring nur, soweit es genehmigt und aktiv ist. Bei Konflikt aktuellen Stand
  laden, nicht blind erneut schreiben. Bei TLS-, Rollen-, Daten- oder Backupfehler
  betroffene Aktion stoppen und Zeitpunkt, Umgebung, Bereich und bereinigten
  Fehler melden. Keine Resets, Rechteausweitung oder Weitergabe von Zugangsdaten.

## Unabhaengige Sicherung fuer Echtdaten

**Offen.** Der DPAPI-/BitLocker-Restore vom 15.11. war ein echter damaliger
Rueckfallnachweis fuer dieselbe Windows-Identitaet. Eine zweite Kopie desselben
DPAPI-Ciphertexts und der lokale V2-Synthetic-Restore belegen keine Recovery
nach Verlust von VPS und Originalrechner/-profil.

1. **Ziel und Verfahren freigeben:** Manuel benennt ein genehmigtes verschluesseltes
   Off-VPS-Ziel und einen getrennt nutzbaren geschuetzten Restore-Arbeitsplatz.
   Zugriff/Entsperrung ohne Originalprofil, Mindestberechtigungen und aktuelle
   Kapazitaet (Erstprobe: mindestens 4x Nutzlast + 512 MiB Arbeitsreserve) nach
   [Zielvertrag](backup-destinations-2026-11-04.md) belegen. Key-Stick ist kein
   DB-Ziel; SMB ist ungeprueft und nicht genehmigt. Bestehendes Custom-Dump-/OpenPGP-
   Verfahren nur mit aktuell genehmigtem Empfaenger und belegter getrennter
   Schluessel-/Passphrasenverwahrung nutzen. Kaltstart ohne altes Home, Agent-Cache
   oder DPAPI im frischen isolierten GPG-Home nachweisen. [GPG/R2](gpg-root-cause-recovery-decision-2026-11-05.md)
   bleibt pausiert: keine Wiederaufnahme, neuen Keys oder Altpasswortversuche aus
   diesem Plan. Manuel bleibt Custodian; Janay hat keine technische Recovery-Rolle.
2. **Backup und Restore getrennt genehmigen:** Pro Fenster Quelle, erlaubten
   Datenumfang, Empfaenger, exaktes Ziel und isolierten Restore-Ort, Operator,
   Zeit und Cleanup benennen. Vor dem ersten Echtdaten-Schreibfenster den
   aktuellen, noch synthetischen Zielstand sichern und aus genau dieser Kopie
   wiederherstellen. Im gesondert freigegebenen ersten Echtdatenfenster dasselbe
   Verfahren mit dem aktuellen Set nach der ersten minimalen Kohorte nachweisen,
   bevor weitere Daten freigegeben werden. Vollstaendiges Set mit `COMPLETE` und
   SHA-256 beim Transfer und Reread pruefen. Isolierte PG16 ohne Netzwerk/Ports,
   keine Rollenpasswoerter oder Globals zurueckspielen. Ledger, Tabellen/Zeilen-
   Digests, Schema, Rechte und Sequenzen gegen die ruhige Quelle pruefen; blosse
   Tabellenzahl genuegt nicht. Nur eigene Probe und temporaeren Klartext bereinigen,
   verschluesseltes Set behalten. Verfahren: [Backup/Restore](../architecture/postgresql-backup-restore-runbook.md#external-copy-gate)
   und [unabhaengige Recovery](portal-v2-next-level-operator.md#unabh%C3%A4ngig-wiederherstellbare-sicherung).
3. **Betrieb abnehmen:** Bereinigtes Receipt mit UTC, Umfang, Set-/Baseline-Hashes,
   Schutz, unabhaengigem Decrypt, Paritaet, Laufzeit und Cleanup. Dienst-Recovery
   zusaetzlich mit vorhandener geschuetzter Runtime-Konfiguration/App-Keys und
   isolierter Readiness/Auth belegen; ein DB-Restore allein beweist keinen Login.
   Manuel genehmigt maximalen Datenverlust (RPO) und Wiederanlaufzeit (RTO) gegen
   gemessene Werte. Vor Echtdaten muessen Backup/Monitor, Erfolgs- und
   Testfehlerzustellung, Wiederholungsprobe und getesteter Notfallzugriff nach
   [Betriebsstandard](pilot-account-operations-decisions-2026-09-11.md#abnahmebeweis-vor-echtdaten)
   belegt sein. Timer, Alarmierung und Notfallkonto sind eigene Betriebsfreigaben.
   Datenschutz/Legal bestaetigt Aufbewahrung und Loeschung auch fuer Sets, Logs und
   Clones sowie erneute Anwendung von Loeschregeln nach Restore. Historische
   Pilot-Retention ist keine Echtdatenregel. Fehlender Nachweis, Drift oder
   fehlgeschlagener Erstrestore: keine Ausweitung; neue Schreibvorgaenge stoppen,
   Nachweise sichern und gesonderte Incident-Entscheidung einholen. Kein In-place-Restore.

## Phasen und Freigaben

Jede operative Phase braucht ein ausdrueckliches Go von Manuel fuer Ziel,
erlaubte Aktion, Zeitfenster und passende Nachweise (bei V2: getesteter Commit,
ZIP- und Evidenz-SHA-256). Ein Go gilt nur fuer diese Phase; unklarer Ausgang,
Drift oder fehlender Nachweis bedeutet STOP. Passende Tests wiederverwenden,
[risikobasiert](../requirements/calendar-quality-plan-v0.1.md#risk-based-evidence-reuse)
nur geaenderte Pfade und kompakten Smoke nachweisen.

1. **Lokal abnehmen:** Manuel und Frau Rappelt dokumentieren V2-Fachentscheidung
   und gesprochene Screenreader-Probe. Keine erneute V1.2-Fachabnahme.
   Die fristgebundene EDV-/TLS-Entscheidung kann parallel fallen.
2. **Zugang und Referenz pruefen:** EDV-/TLS-Entscheidung festhalten. Ein spaeteres
   Live-Inventar nur mit ausdruecklich genehmigtem Read-only-Umfang und etabliertem
   Zugang ohne Secret-Lesezugriff: V1.2, sechs Dienste, Listener, striktes TLS,
   ruhige Referenz und freie V2-Ports. Ohne Zugang kein SSH und kein aktuelles PASS.
3. **Sichern und separat restaurieren:** Vor Clone-Provisionierung frisches
   unabhaengiges Backup und exakten Restore der synthetischen `0006`-Referenz mit
   27-Tabellen-Paritaet abnehmen. Ein altes Receipt ersetzt das nicht; die
   isolierte Restore-Probe provisioniert keinen dauerhaften Clone.
4. **Clone, dann Schema:** Eigenes Go fuer den unbedienten synthetischen Clone
   `competence_hub_v2_pilot`, Provenienz/Paritaet belegen. Anschliessend separater
   `0013`-Schema-Grant an Clone-Identitaet und Receipts gebunden; nie der alte
   `0012`-Grant. `ready` muss wiederverwendbare Auth-Artefakte und offene
   Zustellung ausschliessen. Details: [Private-Staging-Runbook](portal-v2-private-staging.md#3-future-window-schema-only-grant).
5. **Privat und synthetisch aktivieren:** Eigenes Go fuer V2-Loopback, eigenes
   Browserprofil, Einladungen/SMTP aus. Kompakter Smoke fuer TLS, MFA/Rollen,
   Origin/CSRF, eine `0013`-Anfrage mit Firmen-/Coach-Isolation, CAL-2 und Persistenz
   nach V2-Neustart.
   Bei Fehler nur V2 schliessen/stoppen; unveraendertes V1.2, sechs Referenzdienste
   und fehlende V2-Listener pruefen. Clone behalten; kein Drop, keine
   Down-Migration und kein Chatbot-Eingriff. [Aktivierung und Rueckfall](portal-v2-private-staging.md#4-future-window-private-activation-and-no-drop-rollback).
6. **Persoenliche Zugaenge separat:** Erst nach bestaetigtem App-Zugang und
   Zustellnachweis, geeignetem Betriebs-/Recovery-Beleg und Einzelfall-Go. Identitaet,
   Arbeitsadresse, exakte Rolle und ggf. belegte Coach-UUID bestaetigen, bestehende
   Zuordnung pruefen; persoenlichen Empfang, MFA/Recovery und Least Privilege
   nachweisen. [Aktivierungsmatrix](coach-account-mapping-v1-2026-11-10.md),
   [Admin-Bootstrap](staging-admin-bootstrap-2026-10-30.md) und
   [Coach-Onboarding](coach-post-migration-onboarding.md) bleiben getrennt;
   `ON_HOLD` bleibt ausgeschlossen, keine Ableitung aus Websiteprofil oder Testrolle.
7. **Erste Echtdaten separat:** Zielumgebung, fachlichen Zweck, minimale Felder,
   Leserechte, Rechtsgrundlage, Datenschutzhinweis und Loeschweg genehmigen;
   G-DATA/G-OPS und separates Portal-Go (G-PROD) fuer den Produktivbetrieb nachweisen.
   Erst dann die explizit freigegebene minimale Kohorte im genehmigten Ziel,
   nie im synthetischen Clone. Das V2-Synthetic-Paket autorisiert keinen
   Echtbetrieb. Kein Coach-Import per impliziter Freigabe; REAL APPLY bleibt aus.

**Naechster Block:** Manuel klaert vor Fristablauf den geschuetzten Zugang.
Inputs: EDV-Rueckmeldung oder Verantwortliche mit Termin je offenem Punkt sowie
das TLS-Receipt vom 16.11. Ergebnis/DoD: dokumentierte EDV-Entscheidung und ein
konkreter gesondert freizugebender HTTPS-/Erneuerungsweg mit Rueckfallreserve,
andernfalls dokumentierte Aussetzung nach Ablauf.

Wiederverwendbare Pruefregel: Receipt-Integritaet, aktueller Live-Zustand und
unabhaengige Wiederherstellbarkeit getrennt belegen. Diese Unterlage aendert
keinen Betriebsstand: kein Commit, Push, Deployment, Konto- oder Dateneingriff.
