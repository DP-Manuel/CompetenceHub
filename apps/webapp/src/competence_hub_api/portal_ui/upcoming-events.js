import { calendarInstantLabel } from "./calendar-month.mjs";
import { EVENT_FORMATS, eventPlace, eventPrice, seatBadge } from "./event-display.js";

const node = (tag, label) => Object.assign(document.createElement(tag), { textContent: label });
const uuid = /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i;

for (const section of document.querySelectorAll("[data-live-upcoming]")) {
  const form = section.querySelector("form");
  const choices = form?.querySelector("datalist");
  const list = section.querySelector("ul");
  const notice = section.querySelector("[role=status]");
  const profile = section.dataset.coachPath;
  let controller;

  function card(event) {
    const li = node("li", "");
    const title = node("a", event.title);
    title.href = "/portal/calendar-public.html?event=" + encodeURIComponent(event.id);
    const heading = node("h3", "");
    heading.append(title);
    const when = [event.starts_at, event.ends_at].map(calendarInstantLabel).join(" bis ");
    li.append(heading, node("p", when), node("p", [EVENT_FORMATS[event.format], eventPlace(event)]
      .filter((value, index, values) => value && values.indexOf(value) === index).join(" · ")));
    if (!profile) {
      const coach = node("p", event.coach.display_name);
      // The fixture is the only local mapping; never resolve a real identity from a name.
      if (event.coach.profile_path === "/coaches/v2-demo-coach/") {
        const link = node("a", event.coach.display_name);
        link.href = "/website" + event.coach.profile_path;
        coach.replaceChildren(link);
      }
      li.append(coach);
    }
    li.append(seatBadge(event.availability), node("p", eventPrice(event)));
    return li;
  }

  async function load(values = new URLSearchParams()) {
    controller?.abort();
    const signal = (controller = new AbortController()).signal;
    if (profile) values.set("coach_path", profile);
    list.replaceChildren();
    list.setAttribute("aria-busy", "true");
    notice.textContent = "Termine werden geladen …";
    try {
      const response = await fetch("/api/v1/calendar/upcoming?" + values, {
        signal, credentials: "omit", cache: "no-store",
      });
      if (signal.aborted) return;
      if (response.status === 400 && values.has("location")) {
        notice.textContent = "Ort oder PLZ nicht gefunden. Bitte einen Ort mit bekannten Koordinaten wählen.";
        return;
      }
      if (!response.ok) throw new Error("Unavailable");
      const data = await response.json();
      if (signal.aborted) return;
      if (choices && !choices.options.length) {
        choices.replaceChildren(...data.locations.map(point => Object.assign(node("option", ""), {value: point.label})));
        form.hidden = !choices.options.length;
      }
      const events = data.items.filter(event => uuid.test(event.id)).slice(0, 5);
      list.replaceChildren(...events.map(card));
      notice.textContent = events.length ? "" : values.has("location")
        ? "Keine veröffentlichten Präsenz- oder Hybridtermine im gewählten Umkreis."
        : "Derzeit sind keine Termine veröffentlicht.";
    } catch {
      if (!signal.aborted) notice.textContent = "Termine momentan nicht verfügbar. Bitte Seite neu laden.";
    } finally {
      if (!signal.aborted) list.removeAttribute("aria-busy");
    }
  }

  if (form) {
    form.addEventListener("submit", event => {
      event.preventDefault();
      const values = new URLSearchParams(new FormData(form));
      values.set("location", values.get("location").trim());
      if (!values.get("location")) {
        notice.textContent = "Bitte einen Ort oder eine PLZ angeben.";
        return;
      }
      void load(values);
    });
    form.addEventListener("reset", () => { void load(); });
  }
  addEventListener("pageshow", event => { if (event.persisted) { form?.reset(); if (!form) void load(); } });
  void load();
}
