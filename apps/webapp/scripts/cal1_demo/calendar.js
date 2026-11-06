"use strict";
import { monthKeys, calendarInstantLabel, calendarMonthLabel, buildMonthLayout, renderMonth } from "./calendar-month.mjs";
const $ = id => document.getElementById(id);
const text = (tag, value) => { const element = document.createElement(tag); element.textContent = value; return element; };
const formats = { online: "Online", praesenz: "Präsenz", hybrid: "Hybrid" };
const months = monthKeys();
let month = 0, offers = [], selected = null, loaded = false;
const date = calendarInstantLabel;

function hideDetail() { selected = null; $("detail").hidden = true; $("request-status").textContent = ""; }
function render() {
  hideDetail();
  $("month-label").textContent = calendarMonthLabel(months[month]);
  $("previous").disabled = month === 0;
  $("next").disabled = month === months.length - 1;
  const items = offers.filter(offer => (!$("topic").value || offer.topic.id === $("topic").value)
    && (!$("format").value || offer.format === $("format").value));
  const layout = buildMonthLayout(items, months[month]);
  $("empty").hidden = !loaded || layout.offerCount > 0;
  $("result-count").textContent = loaded ? `${layout.offerCount} freigegebene Demo-Termine` : "";
  renderMonth($("grid"), layout, show, "detail");
}
function show(offer) {
  selected = offer; $("detail").hidden = false;
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
  $("coach").hidden = !["/coaches/demo-coach-a/", "/coaches/demo-coach-b/"].includes(path);
  if (!$("coach").hidden) $("coach").href = path;
  $("coach").textContent = `${offer.coach.display_name} · Fiktives Profil`;
  $("seats").max = String(offer.capacity); $("seats").value = "1";
  $("request-status").textContent = "";
  $("detail").focus();
}
async function load() {
  $("loading").hidden = false; $("error").hidden = true; $("reload").disabled = true;
  offers = []; loaded = false; render();
  try {
    const sampled = new Date();
    const from = new Date(sampled.getTime() + 60000);
    // Same calendar-month bound as CAL-1, including month-end clamping.
    const to = new Date(sampled), day = to.getUTCDate();
    to.setUTCDate(1); to.setUTCMonth(to.getUTCMonth() + 3);
    const last = new Date(Date.UTC(to.getUTCFullYear(), to.getUTCMonth() + 1, 0)).getUTCDate();
    to.setUTCDate(Math.min(day, last)); to.setUTCSeconds(to.getUTCSeconds() - 1);
    let cursor = null;
    do {
      const params = new URLSearchParams({ from: from.toISOString(), to: to.toISOString(), limit: "100" });
      if (cursor) params.set("cursor", cursor);
      const response = await fetch(`/api/v1/calendar/offers?${params}`, { credentials: "omit", cache: "no-store" });
      if (!response.ok) throw new Error("calendar unavailable");
      const page = await response.json(); offers.push(...page.items); cursor = page.next_cursor;
    } while (cursor);
    const currentTopic = $("topic").value;
    $("topic").replaceChildren(new Option("Alle Themen", ""));
    for (const [id, name] of new Map(offers.map(o => [o.topic.id, o.topic.name]))) $("topic").add(new Option(name, id));
    if ([...$("topic").options].some(o => o.value === currentTopic)) $("topic").value = currentTopic;
    if (!loaded && offers.length && !buildMonthLayout(offers, months[month]).offerCount) {
      const found = months.findIndex(key => buildMonthLayout(offers, key).offerCount > 0);
      if (found >= 0) month = found;
    }
    loaded = true; render();
  } catch {
    offers = []; loaded = false; render(); $("error").hidden = false; $("error").focus();
  } finally { $("loading").hidden = true; $("reload").disabled = false; }
}
$("reload").addEventListener("click", load);
$("topic").addEventListener("change", render); $("format").addEventListener("change", render);
$("previous").addEventListener("click", () => { month--; render(); });
$("next").addEventListener("click", () => { month++; render(); });
$("request").addEventListener("submit", event => {
  event.preventDefault();
  if (!selected || !$("request").reportValidity()) return;
  $("request-status").textContent = `Simulation: Anfrage für ${$("seats").value} Platz/Plätze zu „${selected.title}“ vorbereitet. Nichts gesendet oder reserviert.`;
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
} else load();
