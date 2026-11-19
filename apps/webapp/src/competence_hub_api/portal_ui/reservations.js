import { germanDateTime } from "./calendar-form.mjs";

const API = "/api/v1/portal/reservations";
const STATUS = {
  pending: "Eingereicht", clarification: "Klärung nötig", approved: "Positiv geprüft",
  rejected: "Abgelehnt", withdrawn: "Zurückgenommen", cancelled: "Veranstaltung abgesagt",
};
const EVENT = {
  submitted: "Eingereicht", seats_changed: "Platzzahl geändert",
  clarification_requested: "Klärung angefordert", offer_cancelled: "Veranstaltung abgesagt",
  ...STATUS,
};
const ERRORS = {
  reservation_capacity: "Es sind nicht genügend Plätze frei. Bitte reduzieren Sie die Platzzahl.",
  reservation_unchanged_seats: "Geben Sie eine andere Platzzahl ein.",
  reservation_deadline: "Die Frist ist abgelaufen. Neue oder zusätzliche Plätze sind nicht möglich.",
  reservation_already_requested: "Für Ihre Firma gibt es bereits eine aktive Vormerkung.",
  reservation_stale_version: "Der Datenstand hat sich geändert. Bitte laden Sie die Übersicht neu.",
  reservation_invalid_transition: "Diese Aktion ist im aktuellen Status nicht mehr möglich.",
  reservation_started: "Die Veranstaltung hat bereits begonnen.",
  reservation_not_found: "Dieser Vorgang oder das Angebot ist nicht mehr verfügbar.",
  reservation_contact_mapping: "Ihrem Konto ist kein eindeutiger Firmenkontakt zugeordnet.",
  reservation_forbidden: "Für diesen Vorgang fehlt die Berechtigung.",
};
const isOpen = (item) => ["pending", "clarification"].includes(item.status);
const date = (value) => germanDateTime(value);
const version = (item) => ({ "If-Match": `"v${item.version}"` });

function element(tag, value, className) {
  const node = document.createElement(tag);
  if (value != null) node.textContent = value;
  if (className) node.className = className;
  return node;
}

function button(label, action, primary = false) {
  const node = element("button", label, `button button-${primary ? "primary" : "secondary"}`);
  node.type = "button";
  node.addEventListener("click", action);
  return node;
}

function facts(entries) {
  const list = element("dl", null, "calendar-card-meta");
  for (const [label, value] of entries) {
    if (value != null && value !== "") list.append(element("dt", label), element("dd", value));
  }
  return list;
}

export function createReservations({ root, request, hasCsrf, expired }) {
  const heading = root.querySelector("h2");
  const scope = root.querySelector("[data-cal2-scope]");
  const status = root.querySelector("[role=status]");
  const notice = root.querySelector("[role=alert]");
  const content = root.querySelector("[data-cal2-content]");
  let caps = {}, controller, currentForm, isReview = false, showDone = false;

  function leave() {
    controller?.abort();
    controller = undefined;
    currentForm = undefined;
    content.replaceChildren();
    status.textContent = "";
    notice.textContent = "";
    notice.hidden = true;
  }

  function setNotice(message) {
    notice.textContent = message;
    notice.hidden = !message;
  }

  async function read(path, signal) {
    const response = await request(path, { signal });
    if (response.status === 401) { expired(); throw new Error(); }
    if (!response.ok) throw new Error();
    return response.json();
  }

  async function available(roles, valid) {
    if (!roles.has("company_contact") && !roles.has("calendar_reviewer") && !roles.has("admin")) return {};
    try {
      const result = await request(API + "/capabilities");
      const data = result.ok ? await result.json() : {};
      if (valid()) caps = data;
      return data;
    } catch { return {}; }
  }

  function listSection(title, path, render, empty, signal) {
    const section = element("section", null, "reservation-list");
    const list = element("ul");
    section.append(element("h3", title), list);
    const pageStatus = element("p");
    pageStatus.setAttribute("role", "status");
    const more = button("Weitere laden", () => void load(next));
    more.hidden = true;
    section.append(more, pageStatus);
    content.append(section);
    let next = null;

    async function load(after) {
      more.disabled = true;
      pageStatus.textContent = "Wird geladen …";
      try {
        const url = new URL(path, location.origin);
        if (after) url.searchParams.set("after", after);
        const data = await read(url.pathname + url.search, signal);
        if (signal.aborted) return;
        list.append(...data.items.map(render));
        next = data.next_after;
        more.hidden = !next;
        pageStatus.textContent = list.children.length ? "" : empty;
        if (after && !next) {
          list.lastElementChild?.setAttribute("tabindex", "-1");
          list.lastElementChild?.focus();
        }
      } catch {
        if (!signal.aborted) {
          pageStatus.textContent = "Die Liste konnte nicht geladen werden.";
          more.textContent = "Erneut laden";
          more.hidden = false;
        }
      } finally { more.disabled = false; }
    }
    return load(null);
  }

  function catalogueCard(item) {
    const card = element("li", null, "calendar-card");
    card.append(element("h4", item.title), facts([
      ["Thema", item.topic_name], ["Beginn", date(item.starts_at)], ["Ende", date(item.ends_at)],
      ["Format", { online: "Online", praesenz: "Präsenz", hybrid: "Hybrid" }[item.format_code]],
      ["Ort", item.public_location], ["Preis", item.price_display_text],
      ["Freie Plätze", item.free_seats], ["Entscheidungsfrist", date(item.decision_deadline)],
    ]));
    if (item.has_reservation || item.free_seats < 1) {
      card.append(element("p", item.has_reservation ? "Für Ihre Firma bereits vorgemerkt" : "Keine freien Plätze"));
    } else {
      const open = button("Plätze vormerken", () => showCreate(item), true);
      open.disabled = !hasCsrf();
      open.setAttribute("aria-label", `Plätze vormerken: ${item.title}`);
      card.append(open);
    }
    return card;
  }

  function reservationFacts(item) {
    return facts([
      ["Status", STATUS[item.status]], ["Gewünschte Plätze", item.seats],
      ["Beginn", date(item.starts_at)], ["Ende", date(item.ends_at)],
      ["Entscheidungsfrist", date(item.decision_deadline)],
      ["Firma", item.company_name], ["Kontaktperson", item.contact_name],
      ["Offen angefragt (Angebot)", item.requested_seats], ["Belegt (Angebot)", item.occupied_seats],
      ["Kapazität", item.capacity], ["Prüfschwelle", item.review_threshold],
    ]);
  }

  function attention(item) {
    if (!isReview || !isOpen(item)) return "";
    if (item.deadline_passed) return "Entscheidung überfällig";
    if (Date.parse(item.decision_deadline) - Date.now() <= 48 * 3600 * 1000) return "Frist endet bald";
    if (item.occupied_seats >= item.review_threshold) return "Prüfschwelle erreicht";
    return "Prüfschwelle noch nicht erreicht";
  }

  function reservationCard(item) {
    const card = element("li", null, "calendar-card");
    card.append(element("h4", item.title), reservationFacts(item));
    if (attention(item)) card.append(element("p", attention(item), "calendar-status"));
    card.append(button("Vorgang ansehen", () => void detail(item.id)));
    return card;
  }

  async function show(review, done = false, message = "") {
    leave();
    isReview = review;
    showDone = done;
    const signal = (controller = new AbortController()).signal;
    heading.textContent = review ? "Vormerkungen prüfen" : "Plätze vormerken";
    scope.textContent = review ? "Lokale Demo · Synthetische Firmenanfragen"
      : `Lokale Demo${caps.company ? " · " + caps.company.name : ""}`;
    heading.focus();
    status.textContent = message;
    if (!review && !caps.company) {
      setNotice(ERRORS.reservation_contact_mapping);
      return;
    }
    if (review) {
      const toggle = element("input");
      toggle.type = "checkbox";
      toggle.checked = done;
      const label = element("label", null, "reservation-toggle");
      label.append(toggle, document.createTextNode(" Auch abgeschlossene Vorgänge anzeigen"));
      toggle.addEventListener("change", () => void show(true, toggle.checked));
      content.append(label);
      await listSection(done ? "Alle Vorgänge" : "Offene Vorgänge",
        API + `?review=true&open_only=${!done}`, reservationCard, "Keine Vorgänge vorhanden.", signal);
    } else {
      await Promise.all([
        listSection("Vormerkungen Ihrer Firma", API, reservationCard, "Noch keine Vormerkungen.", signal),
        listSection("Veröffentlichte Gruppenangebote", API + "/catalogue", catalogueCard,
          "Derzeit sind keine Angebote für Vormerkungen geöffnet.", signal),
      ]);
    }
  }

  function openPanel(title) {
    const review = isReview;
    const done = showDone;
    leave();
    const signal = (controller = new AbortController()).signal;
    const back = button("Zur Übersicht", () => void show(review, done));
    content.append(back, element("h3", title));
    back.focus();
    return signal;
  }

  async function detail(id) {
    const signal = openPanel("Vormerkung");
    status.textContent = "Vorgang wird geladen …";
    try {
      const item = await read(API + `/${id}?review=${isReview}`, signal);
      if (signal.aborted) return;
      status.textContent = "";
      content.append(element("h4", item.title), reservationFacts(item));
      if (attention(item)) content.append(element("p", attention(item), "calendar-status"));
      if (isOpen(item) && item.deadline_passed) {
        content.append(element("p", "Keine neuen oder zusätzlichen Plätze. Die Vormerkung bleibt bis zu einer Entscheidung oder Rücknahme offen."));
      }
      content.append(facts([["Telefon", item.phone], ["Nachricht", item.message]]));
      if (isOpen(item) && hasCsrf()) {
        if (isReview) decisionForm(item, signal);
        else {
          if (item.offer_available) changeForm(item, signal);
          const withdraw = button("Vormerkung zurücknehmen", () => {
            const form = commandForm("Rücknahme bestätigen", signal, API + `/${item.id}/withdraw`,
              "POST", version(item), () => ({}), "Vormerkung zurückgenommen.");
            form.container.prepend(element("p", "Die vorgemerkten Plätze werden wieder frei."));
            withdraw.replaceWith(form.node);
            form.submit.focus();
          });
          content.append(withdraw);
        }
      }
      content.append(element("h4", "Statusverlauf"));
      const history = element("ol", null, "reservation-history");
      for (const entry of item.history) {
        const row = element("li", `${date(entry.occurred_at)} · ${EVENT[entry.event]} · ${entry.seats_after} Plätze`);
        if (entry.reason) row.append(element("p", entry.reason));
        if (entry.threshold_reached) row.append(element("p", "Prüfschwelle bei diesem Schritt erreicht."));
        history.append(row);
      }
      content.append(history);
    } catch {
      if (!signal.aborted) { status.textContent = ""; setNotice("Der Vorgang konnte nicht geladen werden."); }
    }
  }

  function field(form, id, label, input) {
    const group = element("div", null, "field");
    const caption = element("label", label);
    const error = element("p", null, "field-error");
    caption.htmlFor = input.id = `cal2-${id}`;
    error.id = input.id + "-error";
    error.setAttribute("role", "status");
    input.setAttribute("aria-describedby", error.id);
    group.append(caption, input, error);
    form.container.append(group);
    form.fields[id] = { input, error };
    return input;
  }

  function seatsField(form, amount, limit) {
    const input = element("input");
    input.type = "number";
    input.inputMode = "numeric";
    input.min = "1";
    input.max = String(limit);
    input.step = "1";
    input.required = true;
    input.value = amount;
    return field(form, "seats", "Teilnehmerzahl", input);
  }

  function commandForm(label, signal, path, method, headers, payload, success) {
    const node = element("form", null, "reservation-form");
    const container = element("fieldset");
    const submit = element("button", label, "button button-primary");
    submit.type = "submit";
    const fields = {};
    let fingerprint, requestId;
    node.noValidate = true;
    node.append(container, submit);
    node.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (currentForm || signal.aborted) return;
      setNotice("");
      for (const { input, error } of Object.values(fields)) {
        input.removeAttribute("aria-invalid"); error.textContent = "";
      }
      function fieldError(key, error) {
        const field = fields[key];
        if (!field) { setNotice(error); notice.focus(); return; }
        field.input.setAttribute("aria-invalid", "true");
        field.error.textContent = error;
        field.input.focus();
      }
      for (const [key, { input }] of Object.entries(fields)) {
        if (!input.validity.valid || (key === "reason" && !input.value.trim())) {
          fieldError(key, {
            seats: `Bitte geben Sie eine ganze Zahl von 1 bis ${input.max} ein.`,
            contact_confirmed: "Bitte bestätigen Sie die Kontaktperson.",
            reason: "Bitte geben Sie eine kurze Begründung an.",
          }[key] || "Bitte prüfen Sie Ihre Eingabe.");
          return;
        }
      }
      const body = payload();
      const key = JSON.stringify(body);
      if (key !== fingerprint) { fingerprint = key; requestId = crypto.randomUUID(); }
      const running = currentForm = Symbol();
      container.disabled = submit.disabled = true;
      status.textContent = "Wird gespeichert …";
      try {
        const response = await request(path, {
          method, headers, csrf: "session", body: { ...body, request_id: requestId }, signal,
        });
        if (signal.aborted) return;
        if (response.status === 401) { expired(); return; }
        if (response.ok) { void show(isReview, showDone, success); return; }
        const problem = await response.json();
        if (signal.aborted) return;
        const field = problem.field_errors?.[0]?.field;
        container.disabled = submit.disabled = false;
        if (field) fieldError(field, ERRORS[problem.code] || "Bitte prüfen Sie Ihre Eingabe.");
        else { setNotice(ERRORS[problem.code] || "Der Vorgang konnte nicht gespeichert werden."); notice.focus(); }
      } catch {
        if (!signal.aborted) {
          setNotice("Nicht erreichbar. Prüfen Sie den Vorgang in der Übersicht oder versuchen Sie es erneut.");
          notice.focus();
        }
      } finally {
        if (currentForm === running) {
          currentForm = undefined;
          container.disabled = submit.disabled = false;
          status.textContent = "";
        }
      }
    });
    return { node, container, submit, fields };
  }

  function showCreate(item) {
    const signal = openPanel(item.title);
    const form = commandForm("Unverbindlich vormerken", signal, API + `/offers/${item.id}`, "POST", {},
      () => ({ seats: seats.valueAsNumber, revision_number: item.revision_number,
        contact_confirmed: confirmed.checked, phone: phone.value || null, message: message.value || null }),
      "Vormerkung eingereicht. Es wurde nichts verbindlich gebucht.");
    content.append(facts([["Beginn", date(item.starts_at)], ["Ende", date(item.ends_at)],
      ["Freie Plätze", item.free_seats], ["Entscheidungsfrist", date(item.decision_deadline)]]), form.node);
    const seats = seatsField(form, "1", item.free_seats);
    const check = element("input");
    check.type = "checkbox";
    check.required = true;
    const confirmed = field(form, "contact_confirmed", `Kontaktperson bestätigen: ${caps.company.contact}`, check);
    const phone = element("input");
    phone.type = "tel"; phone.maxLength = 50;
    field(form, "phone", "Telefon (optional)", phone);
    const message = element("textarea");
    message.rows = 3; message.maxLength = 500;
    field(form, "message", "Nachricht (optional)", message);
  }

  function changeForm(item, signal) {
    const form = commandForm("Platzzahl ändern", signal, API + `/${item.id}/seats`, "PATCH",
      version(item), () => ({ seats: seats.valueAsNumber }), "Platzzahl geändert.");
    const seats = seatsField(form, String(item.seats), item.deadline_passed ? item.seats : item.capacity);
    content.append(form.node);
  }

  function decisionForm(item, signal) {
    const form = commandForm("Entscheidung speichern", signal, API + `/${item.id}/decide`, "POST",
      version(item), () => ({ outcome: outcome.value, reason: reason.value.trim() }), "Entscheidung gespeichert.");
    const select = element("select");
    select.required = true;
    for (const [value, text] of Object.entries({
      "": "Bitte auswählen", clarification_requested: "Klärung anfordern",
      approved: "Positiv prüfen (keine Buchung)", rejected: "Ablehnen",
    })) {
      const option = element("option", text);
      option.value = value;
      if (value === "approved" && !item.offer_available) option.disabled = true;
      if (value === "clarification_requested" && item.status === "clarification") option.disabled = true;
      select.append(option);
    }
    const outcome = field(form, "outcome", "Entscheidung", select);
    const reason = element("textarea");
    reason.required = true; reason.rows = 3; reason.maxLength = 500;
    field(form, "reason", "Begründung für die Firma", reason);
    content.append(form.node);
  }

  return { available, show, leave, reset() { leave(); caps = {}; } };
}
