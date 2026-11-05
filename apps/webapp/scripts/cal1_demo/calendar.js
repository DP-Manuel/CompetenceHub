"use strict";
const $ = id => document.getElementById(id);
const text = (tag, value) => { const element = document.createElement(tag); element.textContent = value; return element; };
const formats = { online: "Online", praesenz: "Präsenz", hybrid: "Hybrid" };
const now = new Date();
const months = [0, 1, 2, 3].map(offset => new Date(now.getFullYear(), now.getMonth() + offset, 1));
let month = 0, offers = [], selected = null, loaded = false;
const date = value => new Date(value).toLocaleString("de-DE", { timeZone: "Europe/Berlin", dateStyle: "medium", timeStyle: "short" });
const dayKey = value => new Date(value).toLocaleDateString("sv-SE", { timeZone: "Europe/Berlin" });

function hideDetail() { selected = null; $("detail").hidden = true; $("request-status").textContent = ""; }
function render() {
  hideDetail();
  const first = months[month];
  $("month-label").textContent = first.toLocaleDateString("de-DE", { month: "long", year: "numeric" });
  $("previous").disabled = month === 0;
  $("next").disabled = month === months.length - 1;
  const items = offers.filter(offer => dayKey(offer.starts_at).slice(0, 7) === dayKey(first).slice(0, 7)
    && (!$("topic").value || offer.topic.id === $("topic").value)
    && (!$("format").value || offer.format === $("format").value));
  $("grid").replaceChildren();
  $("empty").hidden = !loaded || items.length > 0;
  $("result-count").textContent = loaded ? `${items.length} freigegebene Demo-Termine` : "";
  const count = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate();
  for (let day = 1; day <= count; day++) {
    const current = new Date(first.getFullYear(), first.getMonth(), day, 12);
    const cell = text("div", ""); cell.className = "day";
    if (day === 1) cell.style.setProperty("--weekday", String((current.getDay() + 6) % 7 + 1));
    const label = text("time", current.toLocaleDateString("de-DE", { weekday: "short", day: "numeric" }));
    label.className = "day-label"; label.dateTime = dayKey(current); cell.append(label);
    for (const offer of items.filter(item => dayKey(item.starts_at) === dayKey(current))) {
      const button = text("button", `${date(offer.starts_at).split(", ").pop()} · ${offer.title}`);
      button.type = "button"; button.dataset.offer = offer.id;
      button.addEventListener("click", () => show(offer)); cell.append(button);
    }
    $("grid").append(cell);
  }
}
function show(offer) {
  selected = offer; $("detail").hidden = false;
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
    if (!loaded && offers.length && !offers.some(o => dayKey(o.starts_at).slice(0, 7) === dayKey(months[month]).slice(0, 7))) {
      const found = months.findIndex(m => dayKey(m).slice(0, 7) === dayKey(offers[0].starts_at).slice(0, 7));
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
