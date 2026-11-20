"use strict";
import { monthKeys, calendarInstantLabel, calendarMonthLabel, buildMonthLayout, renderMonth } from "./calendar-month.mjs";
import { createProductTour } from "./product-tour.js";
import { EVENT_FORMATS, eventPlace, eventPrice, seatBadge } from "./event-display.js";
const $ = id => document.getElementById(id);
const text = (tag, value) => { const element = document.createElement(tag); element.textContent = value; return element; };
const formats = EVENT_FORMATS;
const isDemo = location.pathname.startsWith("/demo/");
const months = monthKeys();
const params = new URLSearchParams(location.search);
const slug = params.get("coach");
const eventId = params.get("event");
let linkedEvent = /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(eventId || "") ? eventId.toLowerCase() : null;
const coachPath = slug && /^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug) && slug.length <= 100 ? `/coaches/${slug}/` : null;
let journey = { portal_reservations: false, local_website: false };
let month = 0, offers = [], selected = null, loaded = false, loading = false, downloading = false;
const date = calendarInstantLabel;
if ($("profile-filter")) $("profile-filter").hidden = !coachPath;
if ($("portal-reservation")) {
  fetch("/api/v1/calendar/journey", { credentials: "omit", cache: "no-store" })
    .then(response => response.ok ? response.json() : null)
    .then(data => {
      if (!data) return;
      journey = data;
      $("local-website").hidden = !journey.local_website;
      if (selected) { updateJourney(selected); void updateAvailability(selected); }
    }).catch(() => { /* The anonymous request draft remains available. */ });
}
if (document.getElementById("calendar-help")) {
  const tour = createProductTour({navigate:async () => {},canLeave:() => true,originSelector:"#calendar-help"});
  $("calendar-help").addEventListener("click",() => tour.start("calendar"));
}

function hideDetail() { selected = null; $("detail").hidden = true; $("request-status").textContent = ""; $("request-draft-panel").hidden = true; $("request-draft").value = ""; }
function render(keepDetail = false) {
  if (!keepDetail) hideDetail();
  $("month-label").textContent = calendarMonthLabel(months[month]);
  $("previous").disabled = month === 0;
  $("next").disabled = month === months.length - 1;
  const items = offers.filter(offer => (!$("topic").value || offer.topic.id === $("topic").value)
    && (!$("format").value || offer.format === $("format").value)
    && (!coachPath || offer.coach.profile_path === coachPath));
  const layout = buildMonthLayout(items, months[month]);
  $("empty").hidden = !loaded || layout.offerCount > 0;
  $("result-count").textContent = loaded ? `${layout.offerCount} freigegebene ${isDemo ? "Demo-Termine" : "Termine"}` : "";
  renderMonth($("grid"), layout, show, "detail");
}
function updateJourney(offer) {
  const path = offer.coach.profile_path;
  const valid = typeof path === "string" && /^\/coaches\/[a-z0-9]+(-[a-z0-9]+)*\/$/.test(path)
    && (path !== "/coaches/v2-demo-coach/" || journey.local_website);
  $("coach").hidden = !valid;
  if (valid) {
    if (isDemo) $("coach").href = path;
    else if (journey.local_website && path === "/coaches/v2-demo-coach/") $("coach").href = "/website" + path;
    else $("coach").href = "https://competencehub.donner-partner.de" + path;
  } else $("coach").removeAttribute("href");
  if ($("portal-reservation")) {
    const canLink = journey.portal_reservations && Date.parse(offer.decision_deadline) > Date.now();
    $("portal-reservation").hidden = !canLink;
    if (canLink) $("portal-reservation-link").href = `/portal/?offer=${encodeURIComponent(offer.id)}`;
    else $("portal-reservation-link").removeAttribute("href");
  }
}
async function updateAvailability(offer) {
  if (!journey.local_website) return;
  const target = $("public-seat-status");
  if (!target) return;
  try {
    const response = await fetch("/api/v1/calendar/upcoming?event_id=" + encodeURIComponent(offer.id), {
      credentials: "omit", cache: "no-store",
    });
    const candidate = response.ok ? (await response.json()).items[0] : null;
    if (selected !== offer || !target.isConnected) return;
    target.replaceChildren(seatBadge(candidate?.availability));
  } catch {
    if (selected === offer && target.isConnected) target.replaceChildren(seatBadge());
  }
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
    Zeitzone: offer.time_zone, Format: formats[offer.format], Ort: eventPlace(offer),
    Kapazität: `Höchstens ${offer.capacity} Teilnehmende.`,
    Entscheidungsfrist: date(offer.decision_deadline), Preishinweis: eventPrice({
      price: { status: "display_text", text: offer.price_display_text },
    }) })) {
    $("meta").append(text("dt", key), text("dd", value));
  }
  const label = $("meta").appendChild(text("dt", "Platzstand"));
  const seatDetail = text("dd", "");
  seatDetail.id = "public-seat-status";
  seatDetail.append(seatBadge());
  label.after(seatDetail);
  void updateAvailability(offer);
  // The fixture explicitly supplies these synthetic routes. Never derive real mappings.
  updateJourney(offer);
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
    if (background && loaded && JSON.stringify(offers) === previousSignature) {
      if (selected) void updateAvailability(selected);
      return;
    }
    // Capture current interaction AFTER the async reads, not before the user
    // may have selected another filter, event or field while they were pending.
    const previousSelection = selected?.id;
    const focus = document.activeElement;
    const focusedOffer = focus?.dataset?.offer, focusedDate = focus?.dataset?.date;
    const currentTopic = $("topic").value;
    $("topic").replaceChildren(new Option("Alle Themen", ""));
    for (const [id, name] of new Map(offers.map(o => [o.topic.id, o.topic.name]))) $("topic").add(new Option(name, id));
    if ([...$("topic").options].some(o => o.value === currentTopic)) $("topic").value = currentTopic;
    const scoped = coachPath ? offers.filter(item => item.coach.profile_path === coachPath) : offers;
    if (!loaded && scoped.length && !buildMonthLayout(scoped, months[month]).offerCount) {
      const found = months.findIndex(key => buildMonthLayout(scoped, key).offerCount > 0);
      if (found >= 0) month = found;
    }
    const retained = offers.find(o => o.id === previousSelection);
    const selectedChanged = retained && JSON.stringify(selected) !== JSON.stringify(retained);
    const seats = $("seats").value, requestStatus = $("request-status").textContent;
    loaded = true; $("error").hidden = true; render(background && Boolean(retained));
    if (linkedEvent) {
      const linked = scoped.find(item => item.id === linkedEvent);
      linkedEvent = null;
      if (linked) {
        const found = months.findIndex(key => buildMonthLayout([linked], key).offerCount > 0);
        if (found >= 0) { month = found; render(); }
        show(linked);
      } else if ($("event-link-status")) $("event-link-status").hidden = false;
    }
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
    `Ort: ${eventPlace(selected)}`, `Gewünschte Plätze: ${$("seats").value}`,
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
