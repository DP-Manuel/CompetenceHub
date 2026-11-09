"use strict";

// Deliberately opt-in on every device: no identity or completion data in Web Storage.
export function createProductTour({ navigate, canLeave }) {
  const dialog = document.getElementById("product-tour");
  const title = document.getElementById("tour-title"), copy = document.getElementById("tour-copy");
  const progress = document.getElementById("tour-progress");
  let steps = [], index = 0, target = null, origin = null, serial = 0;
  const step = (heading, body, selector, area) => ({heading, body, selector, area});
  const definitions = {
    coach: [
      step("Willkommen im Coach-Portal", "Hier sehen Sie ausschließlich Ihre eigenen Veranstaltungen und deren aktuellen Bearbeitungsstand.", "#pilot-overview"),
      step("Meine Veranstaltungen", "Die Liste enthält Ihre Entwürfe, Einreichungen und veröffentlichten Angebote. Mit den Filtern finden Sie einen Termin wieder.", "#calendar-offer-search", "coach-calendar"),
      step("Neuen Termin erstellen", "Beginnen Sie mit einem Entwurf. Erst eine gesonderte fachliche Freigabe macht einen Termin öffentlich.", "#open-calendar-offer-dialog", "coach-calendar"),
      step("Pflichtangaben und Teilnehmerzahl", "Geben Sie Beginn und Ende, Format, Ort und Kapazität an. Die Prüfschwelle ist ein interner Prüfwert, keine Buchung oder Mindestbelegung.", "#coach-calendar-workspace", "coach-calendar"),
      step("Speichern und einreichen", "Speichern Sie zunächst den Entwurf und reichen Sie ihn anschließend zur Prüfung ein. Das allein veröffentlicht noch nichts.", "#coach-calendar-list", "coach-calendar"),
      step("Rückmeldung und Revision", "Bei Änderungsbedarf oder einem veröffentlichten Termin beginnen Sie eine neue Revision. Die letzte Freigabe bleibt bis zur neuen Entscheidung bestehen.", "#coach-calendar-workspace", "coach-calendar"),
      step("Kalender und Hilfe", "Der öffentliche Kalender zeigt nur freigegebene Angaben. Unter Hilfe können Sie diese Einführung jederzeit neu starten.", "#public-calendar-link"),
    ],
    reviewer: [
      step("Willkommen im Prüfbereich", "Sie prüfen eingereichte Angebote. Die Prüferrolle macht Sie nicht zum technischen Administrator.", "#pilot-overview"),
      step("Eingereichte Angebote", "Die Prüfliste enthält Angebote, für die eine Entscheidung aussteht.", "#review-calendar-list", "review-calendar"),
      step("Details prüfen", "Öffnen Sie Angebot prüfen. Kontrollieren Sie Inhalt, Zeitraum, Format, Kapazität und Entscheidungsfrist.", "#review-calendar-workspace", "review-calendar"),
      step("Änderungen anfordern", "Beschreiben Sie die erforderliche Änderung im Hinweis an den Coach. Eine Änderungsanforderung veröffentlicht das Angebot nicht.", "#review-calendar-workspace", "review-calendar"),
      step("Veranstaltung freigeben", "Mit Veröffentlichen geben Sie genau die geprüfte Revision frei. Bei einem veralteten Datenstand müssen Sie erneut prüfen.", "#review-calendar-workspace", "review-calendar"),
      step("Öffentlicher Kalender", "Nur die freigegebene Revision ist dort sichtbar. Interne Hinweise und persönliche Verfügbarkeiten bleiben geschützt.", "#public-calendar-link"),
      step("Statusübersicht", "Die Übersicht zählt die für Ihre Rolle sichtbaren aktuellen Revisionen. Sie ist keine Teilnehmer- oder Buchungsstatistik.", "#pilot-overview"),
    ],
    admin: [
      step("Administrationsübersicht", "Sie verwalten den technischen Zugang. Die fachliche Prüfung kann eine separat zugewiesene Prüferrolle übernehmen.", "#pilot-overview"),
      step("Benutzerverwaltung", "Die Liste unterscheidet aktive Zugänge, ausstehende Aktivierung und noch erforderliche MFA.", "#pilot-users", "accounts"),
      step("Rollen und Coachzuordnungen", "Einladung und Rolle sind explizite Entscheidungen. Coachzugänge benötigen die bestätigte stabile Coach-UUID; fehlende Zuordnungen werden nicht erraten.", "#pilot-account-summary", "accounts"),
      step("Kalenderverwaltung", "Administratoren dürfen verwalten und prüfen, erhalten aber keine fremde Coachidentität.", "#portal-navigation"),
      step("Status und Audit", "Aktivierung und Kalenderentscheidungen werden serverseitig auditiert. Die Startübersicht ist kein vollständiger Auditviewer.", "#pilot-overview"),
      step("Hilfe und Betriebsstatus", "Die Anzeige bestätigt nur die aktuelle Datenbankabfrage, nicht TLS, Backup oder alle VPS-Dienste. Betriebsnachweise bleiben gesondert erforderlich.", "#pilot-help"),
    ],
  };
  function clear() { target?.classList.remove("tour-target"); target = null; }
  async function show() {
    const ticket = ++serial;
    clear();
    const current = steps[index];
    if (current.area) await navigate(current.area);
    if (ticket !== serial || !dialog.open) return;
    target = document.querySelector(current.selector);
    if (target && !target.hidden && target.getClientRects().length) {
      target.classList.add("tour-target");
      target.scrollIntoView({block:"center", behavior:"instant"});
    }
    title.textContent = current.heading;
    copy.textContent = current.body + (!target || !target.getClientRects().length
      ? " Dieses Bedienelement ist aktuell nicht verfügbar." : "");
    progress.textContent = `Schritt ${index + 1} von ${steps.length}`;
    document.getElementById("tour-back").disabled = index === 0;
    document.getElementById("tour-next").textContent = index === steps.length - 1 ? "Abschließen" : "Weiter";
    title.focus();
  }
  function stop() {
    serial++; clear(); if (dialog.open) dialog.close();
    if (origin?.isConnected && origin.getClientRects().length) origin.focus();
    else document.querySelector("#pilot-help summary")?.focus();
  }
  document.getElementById("tour-next").addEventListener("click", () => {
    if (index + 1 === steps.length) stop(); else { index++; show(); }
  });
  document.getElementById("tour-back").addEventListener("click", () => { if (index) { index--; show(); } });
  document.getElementById("tour-skip").addEventListener("click", stop);
  document.getElementById("tour-close").addEventListener("click", stop);
  dialog.addEventListener("cancel", event => { event.preventDefault(); stop(); });
  return { stop, start(role) {
    if (!definitions[role] || !canLeave() || document.querySelector("dialog[open]")) return;
    origin = document.querySelector("#pilot-help summary"); steps = definitions[role]; index = 0;
    dialog.showModal(); show();
  }};
}
