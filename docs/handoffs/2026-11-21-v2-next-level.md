# Competence Hub V2 Next Level: Abnahme und Betrieb

**21.11.2026.** Synthetische lokale Produktstufe; noch keine fachliche Abnahme
dieses Inkrements, keine Betriebsfreigabe und kein V2-Deployment. Manuel
priorisiert das Produkt. Frau Rappelt prüft den Fachablauf gesammelt.

## Was sich ändert

- **Anfragen:** Die vorhandenen `coaching_requests` erhalten Zuständigkeit,
  Wiedervorlage, Status, Zuordnung zu Coach und Leistung oder Termin sowie
  Notizen und einen Versionsverlauf. Firma oder Privatkunde, nie beides. Die
  Kundenzuordnung wird nach dem Anlegen nicht an einen anderen Mandanten
  übertragen. CAL-2 bleibt für Plätze und dessen Rückfragen zuständig.
- **Rollen:** Admin, Intern und Reviewer bearbeiten Anfragen. Das vorhandene
  Cockpit und die Bereiche für Zugänge, Coaches und Kunden bleiben bestehen.
  Der Firmenkontakt kann den Status der eigenen Firmenanfragen sehen und
  bisherige CAL-2-Vormerkungen bearbeiten. Der Coach sieht nur den gesondert
  freigegebenen Text und Notizen seiner aktuellen Zuordnung, keine internen
  Notizen oder Kundenakte. Eine neue Coachzuordnung übernimmt keine alten
  Freigaben. Privatkundenregister bleiben interne Datensätze ohne Login.
- **Datengrenzen:** Kein Mailversand, keine rechtlich bindende Entscheidung,
  Rechnung oder Zahlung. Herkunft, Notizen und Verlauf sind nicht öffentlich.
  Der Desk-Workflow benutzt keine parallele Vormerkung und keine zweite Demo.

## Gemeinsame Vorführung

**Terminal: lokale PowerShell.** Docker Desktop (Linux), vorhandenes
`postgres:16-bookworm`-Image und Projektumgebung verwenden:

```powershell
Set-Location 'C:\Users\RödelManuel\Documents\IT\Firmendingsbums\Website\apps\webapp'
.\.venv\Scripts\python.exe scripts/run-cal2-local.py
```

`V2_PLATFORM=READY` öffnet fünf synthetische Rollenfenster und die lokale
Website im Fenster von Firma A. Keine echten Zugangsdaten eingeben oder teilen.

1. Coach legt den Workshop an und reicht ihn ein; Reviewer veröffentlicht.
   Firma A findet ihn auf der lokalen Website, merkt Plätze vor und beantwortet
   eine CAL-2-Rückfrage. Reviewer trifft eine unverbindliche Entscheidung.
2. Reviewer erfasst unter **Anfragen** eine Anfrage von Demo-Firma A. Den
   Workshop als Kalenderangebot wählen, Zuständigkeit und Wiedervorlage setzen,
   Aufgabestatus ändern und eine interne Rückfrage als Notiz festhalten.
3. Den zuständigen Coach zuordnen. Nur einen separaten, fiktiven Freigabetext
   oder eine ausdrücklich freigegebene Notiz eintragen. Im Coachfenster prüfen,
   dass die interne Rückfrage nicht sichtbar ist. Firma A prüft den eigenen
   Status; Firma B darf den Vorgang nicht sehen.
4. Admin legt bei Bedarf einen fiktiven Privatkunden ohne Unternehmen an.
   Dazu eine zweite Anfrage anlegen, Aufgabenstatus und Verlauf prüfen.
5. Im Terminal `R` und Enter drücken. Nach `CAL2_RESTART=PASS` denselben
   Vorgang erneut öffnen. Enter beendet die Demo; `CAL2_CLEANUP=PASS` bestätigt
   die Bereinigung der eigenen Testressourcen.

## Noch zu entscheiden

1. **Produkt:** Welche Firmenanfragen dürfen Kunden künftig selbst erfassen,
   beantworten oder zurückziehen? Welche Aufgaben sollen welchem Fachteam
   zugewiesen werden? Kein Privatkundenkonto oder Versand aus dieser Vorbereitung ableiten.
2. **Daten:** Zuständigkeiten, zulässige Inhalte und Leserechte je Fall,
   Aufbewahrung und genehmigte Löschung auch in Archiven und nach Restore.
   Append-only Betriebshistorie bedeutet keine dauerhafte Aufbewahrungspflicht.
3. **Pilot:** Verbindliche App-Adresse, DNS, TLS, Zugriff und SMTP; aktuelles
   VPS-Inventar und unabhängige Wiederherstellung. Nichts davon aus lokalen
   Tests ableiten. [Kurzleitfaden und Fristen](../operations/portal-v2-next-level-operator.md).

Die produktive Website bleibt auf dem Stand vom 20.11. Frau Hupp bleibt
pausiert, Frau Rappelts Personalvermittlungsprofil unveröffentlicht.

## Barrierefreiheit und Betriebsgrenze

Die Browserprüfung deckt Tastatur, Fokus, zugängliche Formularnamen und
Status-/Fehleransagen im Accessibility Tree ab. Die gesprochene Wiedergabe
ist **offen**: Das isolierte Edge-Fenster ließ sich über die Windows-Automation
nicht aus dem minimierten Zustand aktivieren. Ein sichtbarer Desktop muss
Anfragenliste, Pflichtfelder, Fehlermeldung und Fokuswechsel mit aktivem
Screenreader prüfen, ausschließlich mit Testdaten. Die
[Sprachzusammenfassung der Windows-Sprachausgabe](https://support.microsoft.com/de-de/accessibility/windows/narrator/chapter-2-narrator-basics)
kann die tatsächlich ausgegebenen Ansagen belegen. Baumprüfung ist kein Ersatz.

Die lokale Restoreprobe ersetzt keinen unabhängig entschlüsselbaren
VPS-Sicherungsstand. Die letzte bestätigte private TLS-Frist ist **30.11.2026,
19:09:39 MEZ**. Ohne gesondert freigegebenen und nachgewiesenen Zugangsweg
kein V2-Start am VPS; ein abgelaufenes Zertifikat wird nicht umgangen.
