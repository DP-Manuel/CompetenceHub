# Pilot Portal Browser Acceptance Checklist

Status: completed; BA-01 through BA-17 passed and local runner cleaned up
Scope: SB-15 same-origin pilot portal
Runtime: local synthetic HTTPS fixture only

## Safety Boundary

- Use only the printed `example.invalid` identities and synthetic records.
- Do not enter real names, companies, contacts, passwords or MFA secrets.
- Do not open other websites in the Edge window started by the runner. Its
  certificate exception exists only for this isolated local test profile.
- The fixture binds to `127.0.0.1`, stores data only in memory and does not read
  `.env` files or connect to PostgreSQL.
- Close the Edge window before pressing Enter in the runner terminal. The
  temporary certificate, browser profile and logs are then removed.

## Start

From the repository root:

```powershell
cd apps\webapp
.\scripts\run-browser-acceptance.ps1
```

Expected start evidence:

- Edge opens `https://127.0.0.1:8443/portal/` without a public deployment.
- The terminal prints two `example.invalid` identities and synthetic MFA data.
- The login view is visible; no company record is preloaded.

## Functional Journeys

Record each item as `Pass`, `Fail` or `Not tested`. A failure needs viewport,
step, expected result, actual result and a screenshot without sensitive data.

| ID | Journey | Expected evidence | Result |
| --- | --- | --- | --- |
| BA-01 | Existing-MFA login | Internal test identity plus password leads to MFA; TOTP `123456` opens `Firmenbetreuung`. | bestanden |
| BA-02 | Empty state | `0 Eintraege`, `Noch keine Firmen gefunden` and a usable `Firma anlegen` action are visible. | bestanden |
| BA-03 | Create company | A synthetic company and first synthetic contact are created once; the dialog closes and the detail view is populated. | bestanden |
| BA-04 | Search and select | Search narrows the company list; clearing the query restores it; list selection updates details. | bestanden |
| BA-05 | Correct company | Name, industry and internal note can be changed and remain visible after reselecting the record. | bestanden |
| BA-06 | Contact lifecycle | A second synthetic contact can be added and an existing contact can be corrected without duplicate submission. | Bestanden |
| BA-07 | Session restore | Reloading the page restores the authenticated session and company list; protected mutations remain usable after CSRF rotation. | Bestanden |
| BA-08 | Logout | `Abmelden` returns to login; browser back/reload does not restore the authenticated view. | Bestanden |
| BA-09 | First MFA enrollment | Enrollment identity shows Authenticator setup; `123456` creates recovery codes; portal entry stays disabled until acknowledgement. | Bestanden |
| BA-10 | Recovery login | Existing-MFA identity, recovery method and `AAAA-BBBB-CCCC-DDDD` open the portal. | Bestanden |

Because the fixture is intentionally volatile, restart the runner before BA-09
or BA-10 when an earlier journey changed synthetic session state.

## Responsive And Accessibility Checks

Run the relevant functional journey first at desktop width, then use Edge
DevTools device emulation with an exact CSS viewport width of 390 pixels.

| ID | Check | Expected evidence | Result |
| --- | --- | --- | --- |
| BA-11 | Desktop layout | Login, list/detail workspace and dialogs fit without overlap, clipped labels or accidental horizontal scrolling. | Bestanden; deutsche Umlaute umgesetzt |
| BA-12 | Exact 390 px layout | Forms, buttons, company list, detail content and dialogs remain readable and operable without clipped text. | bestanden |
| BA-13 | Keyboard only | Tab and Shift+Tab follow a logical order; focus is visible; Enter/Space activate controls; Escape closes native dialogs and focus returns sensibly. | Bestanden |
| BA-14 | Validation and errors | Required/invalid fields expose readable messages near the affected workflow and do not erase valid input unexpectedly. | Bestanden nach Zustandsfix und Nachtest |
| BA-15 | 200% zoom | Core login and company/contact tasks remain usable without content overlap or loss of controls. | Bestanden |
| BA-16 | Reduced motion | With `prefers-reduced-motion: reduce`, no essential action depends on animation and automatic movement is suppressed. | Bestanden |
| BA-17 | Contrast and state | Text, focus indicators, disabled controls, selected company and status labels remain distinguishable. | Bestanden |

## Feedback Follow-up 2026-08-20

- BA-09/10: Recovery-Codes waren optisch kollidiert und ihr Zweck war nicht
  ausreichend erklärt. Sie werden nun als einzelne responsive Einträge
  dargestellt; Einrichtung und Notfallnutzung sind erläutert. Gezielter
  visueller Nachtest bestanden.
- BA-09: Statt der technischen `otpauth://`-URI zeigt die Oberfläche nur noch
  den manuellen Authenticator-Schlüssel mit Sicherheitshinweis. Gezielter
  visueller Nachtest bestanden.
- BA-14: Nach Re-Login konnte ein alter Änderungsfehler sichtbar hängen
  bleiben. Schreib-CSRF-Fallback, Fehlerbereinigung, Mutationszustand und
  Abbrechen/Zurücksetzen wurden korrigiert. Gezielter Ablaufnachtest bestanden.

## Completion Evidence

SB-15 browser acceptance is complete only when:

1. BA-01 through BA-17 have explicit results.
2. Every failure is fixed and rerun, or accepted with an owner and follow-up.
3. No real or sensitive data was used or captured.
4. The Edge window is closed, the runner exits cleanly and the local port is no
   longer listening.
5. The result and any residual browser risk are recorded in `PROJECT_LOG.md`
   and `PROJECT_STATUS.md`.

This checklist does not authorize deployment, DNS changes, real accounts or
production data use.
