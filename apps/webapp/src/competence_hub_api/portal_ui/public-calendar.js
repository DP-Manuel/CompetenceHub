"use strict";
import { monthKeys, calendarInstantLabel, calendarMonthLabel, buildMonthLayout, renderMonth } from "./calendar-month.mjs";
const $ = id => document.getElementById(id);
const text = (tag, value) => { const element = document.createElement(tag); element.textContent = value; return element; };
const formats = { online: "Online", praesenz: "Präsenz", hybrid: "Hybrid" };
const isDemo = location.pathname.startsWith("/demo/");
const months = monthKeys();
let month = 0, offers = [], selected = null, loaded = false, loading = false, downloading = false;
const date = calendarInstantLabel;

function hideDetail() { selected = null; $("detail").hidden = true; $("request-status").textContent = ""; $("request-draft-panel").hidden = true; $("request-draft").value = ""; }
function render(keepDetail = false) {
  if (!keepDetail) hideDetail();
  $("month-label").textContent = calendarMonthLabel(months[month]);
  $("previous").disabled = month === 0;
  $("next").disabled = month === months.length - 1;
  const items = offers.filter(offer => (!$("topic").value || offer.topic.id === $("topic").value)
    && (!$("format").value || offer.format === $("format").value));
  const layout = buildMonthLayout(items, months[month]);
  $("empty").hidden = !loaded || layout.offerCount > 0;
  $("result-count").textContent = loaded ? `${layout.offerCount} freigegebene ${isDemo ? "Demo-Termine" : "Termine"}` : "";
  renderMonth($("grid"), layout, show, "detail");
}
function show(offer, focus = true) {
  selected = offer; $("detail").hidden = false;
  $("ics").href = `/api/v1/calendar/offers/${encodeURIComponent(offer.id)}/calendar.ics`;
  $("detail").dataset.eventId = offer.id;
  $("detail-title").textContent = offer.title; $("summary").textContent = offer.summary || "";
  $("meta").replaceChildren();
  for (const [key, value] of Object.entries({ Coach: offer.coach.display_name,
    Thema: offer.topic.name, Beginn: date(offer.starts_at), Ende: date(offer.ends_at),
    Dauer: `${Math.round((new Date(offer.ends_at) - new Date(offer.starts_at)) / 60000)} Minuten`,
    Zeitzone: offer.time_zone, Format: formats[offer.format], Ort: offer.public_location || "Online",
    Kapazität: `Höchstens ${offer.capacity} Teilnehmende. Kein Stand freier Plätze.`,
    Entscheidungsfrist: date(offer.decision_deadline), Preishinweis: offer.price_display_text })) {
    $("meta").append(text("dt", key), text("dd", value));
  }
  // The fixture explicitly supplies these synthetic routes. Never derive real mappings.
  const path = offer.coach.profile_path;
  const validPath = typeof path === "string" && /^\/coaches\/[a-z0-9]+(-[a-z0-9]+)*\/$/.test(path);
  $("coach").hidden = !validPath;
  if (validPath) $("coach").href = isDemo ? path : `https://competencehub.donner-partner.de${path}`;
  $("coach").textContent = `${offer.coach.display_name}${isDemo ? " · Fiktives Profil" : " · Profil"}`;
  $("seats").max = String(offer.capacity); $("seats").value = "1";
  $("request-status").textContent = "";
  if (focus) $("detail").focus();
}
async function load(background = false) {
  if (loading) return;
  loading = true;
  const previousSignature = JSON.stringify(offers);
  if (!background) {
    $("loading").hidden = false; $("error").hidden = true; $("reload").disabled = true;
    offers = []; loaded = false; render();
  }
  try {
    const received = new Map();
    for (const visibleMonth of months) {
      let cursor = null;
      const cursors = new Set();
      do {
        const params = new URLSearchParams({ month: visibleMonth, limit: "100" });
        if (cursor) params.set("cursor", cursor);
        const url = isDemo ? `/demo/api/public-calendar?${params}` : `/api/v1/calendar/months/${visibleMonth}/offers?${params}`;
        const response = await fetch(url, { credentials: "omit", cache: "no-store" });
        if (!response.ok) throw new Error("calendar unavailable");
        const page = await response.json();
        for (const offer of page.items) received.set(offer.id, offer);
        cursor = page.next_cursor;
        if (cursor && cursors.has(cursor)) throw new Error("repeated cursor");
        if (cursor) cursors.add(cursor);
      } while (cursor);
    }
    offers = [...received.values()];
    if (background && loaded && JSON.stringify(offers) === previousSignature) return;
    // Capture current interaction AFTER the async reads, not before the user
    // may have selected another filter, event or field while they were pending.
    const previousSelection = selected?.id;
    const focus = document.activeElement;
    const focusedOffer = focus?.dataset?.offer, focusedDate = focus?.dataset?.date;
    const currentTopic = $("topic").value;
    $("topic").replaceChildren(new Option("Alle Themen", ""));
    for (const [id, name] of new Map(offers.map(o => [o.topic.id, o.topic.name]))) $("topic").add(new Option(name, id));
    if ([...$("topic").options].some(o => o.value === currentTopic)) $("topic").value = currentTopic;
    if (!loaded && offers.length && !buildMonthLayout(offers, months[month]).offerCount) {
      const found = months.findIndex(key => buildMonthLayout(offers, key).offerCount > 0);
      if (found >= 0) month = found;
    }
    const retained = offers.find(o => o.id === previousSelection);
    const selectedChanged = retained && JSON.stringify(selected) !== JSON.stringify(retained);
    const seats = $("seats").value, requestStatus = $("request-status").textContent;
    loaded = true; $("error").hidden = true; render(background && Boolean(retained));
    if (background) {
      if (retained) {
        show(retained, false);
        $("seats").value = seats; $("request-status").textContent = requestStatus;
        if (selectedChanged && !$("request-draft-panel").hidden) {
          $("request-draft-panel").hidden = true; $("request-draft").value = "";
          $("request-status").textContent = "Terminangaben wurden aktualisiert. Anfrage bitte neu vorbereiten.";
        }
      }
      if (focusedOffer) {
        const button = [...$("grid").querySelectorAll("[data-offer]")].find(e => e.dataset.offer === focusedOffer && e.dataset.date === focusedDate);
        (button || $("reload")).focus({ preventScroll: true });
      } else if (previousSelection && !retained && $("detail").contains(focus)) $("reload").focus({ preventScroll: true });
    }
  } catch {
    offers = []; loaded = false; render(); $("error").hidden = false;
    if (!background) $("error").focus();
  } finally { loading = false; $("loading").hidden = true; $("reload").disabled = false; }
}
$("reload").addEventListener("click", () => load());
$("topic").addEventListener("change", () => render()); $("format").addEventListener("change", () => render());
$("previous").addEventListener("click", () => { month--; render(); });
$("next").addEventListener("click", () => { month++; render(); });
$("request").addEventListener("submit", event => {
  event.preventDefault();
  if (!selected || !$("request").reportValidity()) return;
  $("request-status").textContent = `${isDemo ? "Simulation: " : ""}Anfrage für ${$("seats").value} Platz/Plätze zu „${selected.title}“ vorbereitet. Nichts gesendet oder reserviert.`;
  $("request-draft").value = [`Unverbindliche Anfrage: ${selected.title}`,
    `Coach: ${selected.coach.display_name}`, `Thema: ${selected.topic.name}`,
    `Beginn: ${date(selected.starts_at)}`, `Ende: ${date(selected.ends_at)}`,
    `Zeitzone: ${selected.time_zone}`, `Format: ${formats[selected.format]}`,
    `Ort: ${selected.public_location || "Online"}`, `Gewünschte Plätze: ${$("seats").value}`,
    `Preishinweis: ${selected.price_display_text}`, "Bitte informieren Sie mich über die nächsten Schritte. Keine verbindliche Buchung."].join("\n");
  $("request-draft-panel").hidden = false;
});
$("copy-request").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText($("request-draft").value); $("request-status").textContent = "Anfragetext kopiert. Nichts gesendet oder reserviert."; }
  catch { $("request-status").textContent = "Bitte den sichtbaren Anfragetext markieren und kopieren. Nichts gesendet."; }
});
$("ics").addEventListener("click", async event => {
  event.preventDefault();
  if (!selected || downloading) return;
  const id = selected.id;
  downloading = true; $("ics").setAttribute("aria-busy", "true");
  try {
    const response = await fetch(`/api/v1/calendar/offers/${encodeURIComponent(id)}/calendar.ics`, {credentials:"omit",cache:"no-store"});
    if (!response.ok || !response.headers.get("content-type")?.startsWith("text/calendar")) throw new Error("calendar unavailable");
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a"); link.href = url; link.download = `competence-hub-${id}.ics`;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch { $("request-status").textContent = "Kalendereintrag momentan nicht verfügbar. Bitte Termine aktualisieren."; }
  finally { downloading = false; $("ics").removeAttribute("aria-busy"); }
});
if (location.pathname === "/demo/history") {
  $("calendar").hidden = true; $("history").hidden = false;
  const statuses = { draft: "Entwurf", in_review: "Zur Prüfung eingereicht", changes_requested: "Änderung angefordert", published: "Veröffentlicht" };
  (async () => {
    try {
      const response = await fetch("/demo/api/history", { cache: "no-store" });
      if (!response.ok) throw new Error("sign in");
      const data = await response.json();
      $("history-message").textContent = data.items.length ? "Sichtbarer Demo-Verlauf" : "Noch kein sichtbarer Verlauf.";
      for (const row of data.items) $("history-list").append(text("li", `${row.title} · Revision ${row.revision} · ${row.lifecycle === "withdrawn" ? "Zurückgezogen" : statuses[row.status]} · ${row.action}`));
    } catch { $("history-message").textContent = "Bitte zuerst als Demo-Coach oder Demo-Reviewer im Portal anmelden."; }
  })();
} else {
  load();
  // Same-origin, anonymous reads only. No Portal identity or data in Web Storage.
  const refresh = setInterval(() => { if (!document.hidden) load(true); }, 5000);
  addEventListener("pagehide", () => clearInterval(refresh), { once: true });
  document.addEventListener("visibilitychange", () => { if (!document.hidden) load(true); });
}
