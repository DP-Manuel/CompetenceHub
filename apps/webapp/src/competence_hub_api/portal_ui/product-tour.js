"use strict";

// Bounded tab-history progress only: no user IDs, credentials or Web Storage.
export function createProductTour({ navigate, canLeave, originSelector = "#pilot-help summary" }) {
  const dialog = document.getElementById("product-tour");
  const title = document.getElementById("tour-title"), copy = document.getElementById("tour-copy");
  const progress = document.getElementById("tour-progress");
  const back = document.getElementById("tour-back"), next = document.getElementById("tour-next");
  title.setAttribute("aria-describedby", "tour-progress tour-copy");
  let steps = [], index = 0, target = null, origin = null, role = null, area = null, frame = 0;
  const historyKey = "competenceHubTourV1";
  function remember(status) {
    try {history.replaceState({...history.state,[historyKey]:{role,index,status}},"",location.href);} catch { /* History persistence is optional. */ }
  }
  function saved() {
    const value=history.state?.[historyKey];
    return value && Object.hasOwn(definitions,value.role) && Number.isInteger(value.index) && value.index>=0 && value.index<definitions[value.role].length && ["active","completed","skipped"].includes(value.status) ? value : null;
  }
  const step = (heading, body, selector, area, fallback) => ({heading, body, selector, area, fallback});
  const definitions = {
    coach: [
      step("Willkommen im Coach-Portal", "Hier sehen Sie ausschließlich Ihre eigenen Veranstaltungen und deren aktuellen Bearbeitungsstand.", "#pilot-overview-title"),
      step("Meine Veranstaltungen", "Die Liste enthält Ihre Entwürfe, Einreichungen und veröffentlichten Angebote. Mit den Filtern finden Sie einen Termin wieder.", "#calendar-offer-search", "coach-calendar", "#coach-calendar-title"),
      step("Neuen Termin erstellen", "Beginnen Sie mit einem Entwurf. Erst eine gesonderte fachliche Freigabe macht einen Termin öffentlich.", "#open-calendar-offer-dialog", "coach-calendar", "#coach-calendar-title"),
      step("Datum und Uhrzeit", "Wählen Sie Start- und Enddatum. Unter Uhrzeiten und weitere Pflichtangaben prüfen oder ändern Sie die Zeiten und ergänzen die Entscheidungsfrist. Es gilt Europe/Berlin.", "#open-calendar-offer-dialog", "coach-calendar", "#coach-calendar-title"),
      step("Feldfehler und Abbrechen", "Ein Fehler öffnet den betroffenen Abschnitt. Beim Abbrechen können Sie weiter bearbeiten oder ungespeicherte Änderungen verwerfen. Gespeicherte Entwürfe bleiben erhalten.", "#open-calendar-offer-dialog", "coach-calendar", "#coach-calendar-title"),
      step("Pflichtangaben und Beschreibung", "Ein Entwurf braucht unter anderem Zeitraum, Thema und Preishinweis. Präsenz und Hybrid brauchen einen öffentlichen Ort. Zielgruppe, Inhalte und Ablauf können Sie in der optionalen Beschreibung ergänzen.", "#open-calendar-offer-dialog", "coach-calendar", "#coach-calendar-title"),
      step("Speichern und einreichen", "Speichern Sie zunächst den Entwurf und reichen Sie ihn anschließend zur Prüfung ein. Das allein veröffentlicht noch nichts.", "#coach-calendar-list h3", "coach-calendar", "#coach-calendar-title"),
      step("Rückmeldung und Revision", "Bei Änderungsbedarf oder einem veröffentlichten Termin beginnen Sie eine neue Revision. Die letzte Freigabe bleibt bis zur neuen Entscheidung bestehen.", "#coach-calendar-title", "coach-calendar"),
      step("Kalender und Hilfe", "Der öffentliche Kalender zeigt nur freigegebene Angaben. Unter Hilfe können Sie diese Einführung jederzeit neu starten.", "#public-calendar-link"),
    ],
    reviewer: [
      step("Willkommen im Prüfbereich", "Sie prüfen eingereichte Angebote. Die Prüferrolle macht Sie nicht zum technischen Administrator.", "#pilot-overview-title"),
      step("Eingereichte Angebote", "Die Prüfliste enthält Angebote, für die eine Entscheidung aussteht.", "#review-calendar-title", "review-calendar"),
      step("Details prüfen", "Öffnen Sie Angebot prüfen. Kontrollieren Sie Inhalt, Zeitraum, Format, Kapazität und Entscheidungsfrist.", "#review-calendar-list button", "review-calendar", "#review-calendar-title"),
      step("Änderungen anfordern", "Bei Änderungen anfordern wird der Pflicht-Hinweis an den Coach eingeblendet. Die Änderungsanforderung veröffentlicht das Angebot nicht.", "#review-calendar-list button", "review-calendar", "#review-calendar-title"),
      step("Veranstaltung freigeben", "Mit Veröffentlichen geben Sie genau die geprüfte Revision frei. Ein Hinweis ist dabei freiwillig. Bei einem veralteten Stand müssen Sie erneut prüfen.", "#review-calendar-list button", "review-calendar", "#review-calendar-title"),
      step("Öffentlicher Kalender", "Nur die freigegebene Revision ist dort sichtbar. Interne Hinweise und persönliche Verfügbarkeiten bleiben geschützt.", "#public-calendar-link"),
      step("Statusübersicht", "Die Übersicht zählt die für Ihre Rolle sichtbaren aktuellen Revisionen. Sie ist keine Teilnehmer- oder Buchungsstatistik.", "#pilot-overview-title"),
    ],
    company: [
      step("Willkommen im Unternehmensbereich", "Hier sehen Sie die Vormerkungen Ihrer Firma und die verfügbaren Gruppenangebote.", "#reservations-title", "reservations"),
      step("Veranstaltung auswählen", "Suchen Sie nach Titel oder Thema und öffnen Sie die Veranstaltungsdetails. Dort stehen Zeitraum, Format, Ort und Frist.", "#cal2-search", "reservations", "#reservations-title"),
      step("Plätze vormerken", "Bei freien Plätzen geben Sie die Teilnehmerzahl ein und bestätigen den vorhandenen Firmenkontakt. Eine Vormerkung ist keine Buchung.", "#reservation-catalogue > :is(h3, summary)", "reservations", "#reservations-title"),
      step("Eigene Vorgänge finden", "Unter Vormerkungen Ihrer Firma sehen Sie nur die Vorgänge Ihres Unternehmens.", "#reservation-own > :is(h3, summary)", "reservations", "#reservations-title"),
      step("Ändern oder zurücknehmen", "Öffnen Sie einen noch nicht entschiedenen Vorgang. Dort können Sie die Platzzahl im erlaubten Rahmen ändern oder die Vormerkung zurücknehmen.", "#reservation-own > :is(h3, summary)", "reservations", "#reservations-title"),
      step("Status und Rückfragen", "Aufgaben zeigen offene Rückfragen. Lesen oder beantworten Sie diese im Vorgang. Auch Positiv geprüft ist noch keine Buchung.", ".reservation-activity summary", "reservations", "#reservations-title"),
    ],
    calendar: [
      step("Veranstaltung öffnen", "Wählen Sie einen freigegebenen Termin im Monatskalender. Alle Tagessegmente eines mehrtägigen Termins öffnen dieselben Details.", "#grid button", null, "#calendar-help"),
      step("Zum Kalender hinzufügen", "Öffnen Sie zuerst einen Termin. Mit Zum Kalender hinzufügen (.ics) laden Sie eine Datei für Outlook oder einen anderen Kalender herunter. Es entsteht keine automatische Synchronisierung.", "#ics"),
      step("Anfrage vorbereiten", "Wählen Sie die gewünschte Platzzahl und bereiten Sie einen Anfrageentwurf vor. Nichts wird gesendet oder verbindlich gebucht.", "#request"),
    ],
    admin: [
      step("Administrationsübersicht", "Sie verwalten den technischen Zugang. Die fachliche Prüfung kann eine separat zugewiesene Prüferrolle übernehmen.", "#pilot-overview-title"),
      step("Benutzerverwaltung", "Die Liste zeigt Aktivierung, MFA und letzte Anmeldung. Über Zugang verwalten können Sie fremde Konten sperren oder Rollen ändern. Der eigene Zugang bleibt geschützt.", "#pilot-users button", "accounts", "#pilot-accounts-title"),
      step("Rollen und Coachzuordnungen", "Einladung und Rolle sind explizite Entscheidungen. Coachzugänge benötigen die bestätigte stabile Coach-UUID; fehlende Zuordnungen werden nicht erraten.", "#invitation-role", "accounts", "#pilot-accounts-title"),
      step("Kalenderverwaltung", "Administratoren dürfen verwalten und prüfen, erhalten aber keine fremde Coachidentität.", "#portal-navigation [data-portal-area='coach-calendar']", null, "#pilot-overview-title"),
      step("Status und Audit", "Aktivierung und Kalenderentscheidungen werden serverseitig auditiert. Die Startübersicht ist kein vollständiger Auditviewer.", "#pilot-overview-state"),
      step("Hilfe und Betriebsstatus", "Die Anzeige bestätigt nur die aktuelle Datenbankabfrage, nicht TLS, Backup oder alle VPS-Dienste. Betriebsnachweise bleiben gesondert erforderlich.", "#pilot-help summary"),
    ],
  };
  const pointer=document.createElement("span");pointer.className="tour-pointer";pointer.setAttribute("aria-hidden","true");dialog.append(pointer);
  function clear() { target?.classList.remove("tour-target"); target = null; }
  function position() {
    if (!dialog.open) return;
    const gap=18, pad=12;
    const d={width:dialog.getBoundingClientRect().width,
      height:Math.min(dialog.scrollHeight+dialog.offsetHeight-dialog.clientHeight,innerHeight-2*pad)};
    const x=value=>Math.max(pad,Math.min(innerWidth-d.width-pad,value));
    const y=value=>Math.max(pad,Math.min(innerHeight-d.height-pad,value));
    const t=target?.getBoundingClientRect();
    const candidates=t && t.bottom>0 && t.top<innerHeight ? [
      {side:"right",x:t.right+gap,y:y(t.top)},{side:"left",x:t.left-d.width-gap,y:y(t.top)},
      {side:"bottom",x:x(t.left),y:t.bottom+gap},{side:"top",x:x(t.left),y:t.top-d.height-gap},
    ] : [];
    let fit=candidates.find(p=>p.x>=pad && p.x+d.width<=innerWidth-pad && p.y>=pad && p.y+d.height<=innerHeight-pad);
    if (!fit && candidates.length) {
      const below=Math.floor(innerHeight-pad-t.bottom-gap), above=Math.floor(t.top-gap-pad);
      const available=Math.max(below,above);
      if (available>=132) {
        d.height=Math.min(d.height,available);
        fit=below>=above ? {side:"bottom",x:x(t.left),y:t.bottom+gap}
          : {side:"top",x:x(t.left),y:t.top-d.height-gap};
      }
    }
    const p=fit || {side:"center",x:(innerWidth-d.width)/2,y:innerHeight-d.height-pad};
    dialog.style.maxHeight=`${d.height}px`;
    dialog.style.left=`${x(p.x)}px`;
    dialog.style.top=`${y(p.y)}px`;
    dialog.dataset.placement=p.side;pointer.hidden=!fit;
    pointer.textContent={right:"←",left:"→",bottom:"↑",top:"↓"}[p.side] || "";
  }
  function visible(selector) {
    if (!selector) return null;
    return [...document.querySelectorAll(selector)].find(element => {
      const box = element.getBoundingClientRect();
      return box.width > 0 && box.height > 0 && getComputedStyle(element).visibility === "visible";
    });
  }
  function refreshTarget() {
    if (!dialog.open) return;
    const current = steps[index];
    const resolved = visible(current.selector) || visible(current.fallback)
      || (role !== "calendar" ? visible("#portal-title") : null);
    if (resolved !== target) {
      clear();
      target = resolved || null;
      if (target) {
        target.classList.add("tour-target");
        target.scrollIntoView({block:"start", behavior:"instant"});
      }
    } else if (target) {
      const box=target.getBoundingClientRect();
      if (box.bottom<=0 || box.top>=innerHeight) target.scrollIntoView({block:"start",behavior:"instant"});
    }
    position();
  }
  function scheduleRefresh() {
    if (!frame && dialog.open) frame=requestAnimationFrame(() => {frame=0;refreshTarget();});
  }
  const observe = new MutationObserver(records => {
    if (records.some(record => !dialog.contains(record.target))) scheduleRefresh();
  });
  function show() {
    const current = steps[index];
    // Workspace visibility changes synchronously. A fetch must never gate progress.
    if (current.area && current.area !== area) {
      area = current.area;
      Promise.resolve(navigate(area)).then(scheduleRefresh, scheduleRefresh);
    }
    title.textContent = current.heading;
    copy.textContent = current.body;
    progress.textContent = `Schritt ${index + 1} von ${steps.length}`;
    back.disabled = index === 0;
    next.textContent = index === steps.length - 1 ? "Abschließen" : "Weiter";
    refreshTarget();
    dialog.scrollTop=0;
    if (document.activeElement === title) title.blur();
    title.focus({preventScroll:true});
    remember("active");
  }
  function stop(status="skipped") {
    if (!dialog.open) return;
    remember(status);
    observe.disconnect();
    cancelAnimationFrame(frame);
    frame=0;
    clear();
    dialog.close();
    if (origin?.isConnected && origin.getClientRects().length) origin.focus();
    else visible(originSelector)?.focus();
  }
  next.addEventListener("click", () => {
    if (index + 1 === steps.length) stop("completed"); else { index++; show(); }
  });
  back.addEventListener("click", () => { if (index) { index--; show(); } });
  document.getElementById("tour-skip").addEventListener("click", () => stop());
  document.getElementById("tour-close").addEventListener("click", () => stop());
  dialog.addEventListener("cancel", event => { event.preventDefault(); stop(); });
  window.addEventListener("resize",scheduleRefresh);
  window.addEventListener("scroll",scheduleRefresh,{passive:true});
  function start(nextRole,{automatic=false,resume=false}={}) {
    if (!Object.hasOwn(definitions,nextRole) || !canLeave() || document.querySelector("dialog[open]")) return;
    const prior=saved();
    if (automatic && prior?.role===nextRole && prior.status!=="active") return;
    role=nextRole;origin = document.querySelector(originSelector); steps = definitions[role]; index = resume && prior?.role===role ? prior.index : 0;
    area = null;
    dialog.showModal();
    observe.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:["hidden","open"]});
    show();
  }
  return {stop,start,
    resume(roles) {const prior=saved();const admitted={coach:"coach",reviewer:"calendar_reviewer",admin:"admin",company:"company_contact"};if(prior?.status==="active" && roles.includes(admitted[prior.role])) start(prior.role,{resume:true});},
    reset() {stop();try {const next={...history.state};delete next[historyKey];history.replaceState(next,"",location.href);} catch { /* No personal state retained. */ }}
  };
}
