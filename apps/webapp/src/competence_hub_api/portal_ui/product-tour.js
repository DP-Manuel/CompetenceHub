"use strict";

// Bounded tab-history progress only: no user IDs, credentials or Web Storage.
export function createProductTour({ navigate, canLeave }) {
  const dialog = document.getElementById("product-tour");
  const title = document.getElementById("tour-title"), copy = document.getElementById("tour-copy");
  const progress = document.getElementById("tour-progress");
  let steps = [], index = 0, target = null, origin = null, serial = 0, role = null;
  const historyKey = "competenceHubTourV1";
  function remember(status) {
    try {history.replaceState({...history.state,[historyKey]:{role,index,status}},"",location.href);} catch { /* History persistence is optional. */ }
  }
  function saved() {
    const value=history.state?.[historyKey];
    return value && definitions[value.role] && Number.isInteger(value.index) && value.index>=0 && value.index<definitions[value.role].length && ["active","completed","skipped"].includes(value.status) ? value : null;
  }
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
      step("Benutzerverwaltung", "Die Liste zeigt Aktivierung, MFA und letzte Anmeldung. Über Zugang verwalten können Sie fremde Konten sperren oder Rollen ändern. Der eigene Zugang bleibt geschützt.", "#pilot-users", "accounts"),
      step("Rollen und Coachzuordnungen", "Einladung und Rolle sind explizite Entscheidungen. Coachzugänge benötigen die bestätigte stabile Coach-UUID; fehlende Zuordnungen werden nicht erraten.", "#pilot-account-summary", "accounts"),
      step("Kalenderverwaltung", "Administratoren dürfen verwalten und prüfen, erhalten aber keine fremde Coachidentität.", "#portal-navigation"),
      step("Status und Audit", "Aktivierung und Kalenderentscheidungen werden serverseitig auditiert. Die Startübersicht ist kein vollständiger Auditviewer.", "#pilot-overview"),
      step("Hilfe und Betriebsstatus", "Die Anzeige bestätigt nur die aktuelle Datenbankabfrage, nicht TLS, Backup oder alle VPS-Dienste. Betriebsnachweise bleiben gesondert erforderlich.", "#pilot-help"),
    ],
  };
  const pointer=document.createElement("span");pointer.className="tour-pointer";pointer.setAttribute("aria-hidden","true");dialog.append(pointer);
  function clear() { target?.classList.remove("tour-target"); target = null; }
  function position() {
    if (!dialog.open || !target?.getClientRects().length) {pointer.hidden=true;return;}
    const t=target.getBoundingClientRect(), d=dialog.getBoundingClientRect(), gap=18, pad=12;
    const candidates=[{side:"right",x:t.right+gap,y:t.top},{side:"left",x:t.left-d.width-gap,y:t.top},
      {side:"bottom",x:t.left,y:t.bottom+gap},{side:"top",x:t.left,y:t.top-d.height-gap}];
    const fit=candidates.find(p=>p.x>=pad && p.x+d.width<=innerWidth-pad && p.y>=pad && p.y+d.height<=innerHeight-pad);
    const p=fit || {side:"bottom",x:pad,y:Math.min(innerHeight-d.height-pad,Math.max(pad,t.bottom+gap))};
    dialog.style.left=`${Math.max(pad,Math.min(innerWidth-d.width-pad,p.x))}px`;
    dialog.style.top=`${Math.max(pad,Math.min(innerHeight-d.height-pad,p.y))}px`;
    dialog.dataset.placement=p.side;pointer.hidden=!fit;
    pointer.textContent={right:"←",left:"→",bottom:"↑",top:"↓"}[p.side];
  }
  async function show() {
    const ticket = ++serial;
    clear();
    const current = steps[index];
    if (current.area) await navigate(current.area);
    if (ticket !== serial || !dialog.open) return;
    target = document.querySelector(current.selector);
    if (target?.matches("section,ul,nav,details")) target=target.querySelector("h2,summary,button,strong") || target;
    if (target && !target.hidden && target.getClientRects().length) {
      target.classList.add("tour-target");
      target.scrollIntoView({block:"start", behavior:"instant"});
    }
    title.textContent = current.heading;
    copy.textContent = current.body + (!target || !target.getClientRects().length
      ? " Dieses Bedienelement ist aktuell nicht verfügbar." : "");
    progress.textContent = `Schritt ${index + 1} von ${steps.length}`;
    document.getElementById("tour-back").disabled = index === 0;
    document.getElementById("tour-next").textContent = index === steps.length - 1 ? "Abschließen" : "Weiter";
    title.focus();
    remember("active");position();
  }
  function stop(status="skipped") {
    if (dialog.open) remember(status);
    serial++; clear(); if (dialog.open) dialog.close();
    if (origin?.isConnected && origin.getClientRects().length) origin.focus();
    else document.querySelector("#pilot-help summary")?.focus();
  }
  document.getElementById("tour-next").addEventListener("click", () => {
    if (index + 1 === steps.length) stop("completed"); else { index++; show(); }
  });
  document.getElementById("tour-back").addEventListener("click", () => { if (index) { index--; show(); } });
  document.getElementById("tour-skip").addEventListener("click", () => stop());
  document.getElementById("tour-close").addEventListener("click", () => stop());
  dialog.addEventListener("cancel", event => { event.preventDefault(); stop(); });
  window.addEventListener("resize",position);
  window.addEventListener("scroll",position,{passive:true});
  function start(nextRole,{automatic=false,resume=false}={}) {
    if (!definitions[nextRole] || !canLeave() || document.querySelector("dialog[open]")) return;
    const prior=saved();
    if (automatic && prior?.role===nextRole && prior.status!=="active") return;
    role=nextRole;origin = document.querySelector("#pilot-help summary"); steps = definitions[role]; index = resume && prior?.role===role ? prior.index : 0;
    dialog.showModal(); show();
  }
  return {stop,start,
    resume(roles) {const prior=saved();const admitted={coach:"coach",reviewer:"calendar_reviewer",admin:"admin"};if(prior?.status==="active" && roles.includes(admitted[prior.role])) start(prior.role,{resume:true});},
    reset() {stop();try {const next={...history.state};delete next[historyKey];history.replaceState(next,"",location.href);} catch { /* No personal state retained. */ }}
  };
}
