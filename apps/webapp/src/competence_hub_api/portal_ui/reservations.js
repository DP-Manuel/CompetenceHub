import { germanDateTime } from "./calendar-form.mjs";

const API = "/api/v1/portal/reservations";
const STATUS = {
  pending: "Eingereicht", clarification: "Klärung nötig", approved: "Positiv geprüft",
  rejected: "Abgelehnt", withdrawn: "Zurückgenommen", cancelled: "Veranstaltung abgesagt",
};
const linkedOffer = new URLSearchParams(location.search).get("offer");
const initialOffer = linkedOffer && /^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(linkedOffer) ? linkedOffer : "";
const EVENT = {
  submitted: "Eingereicht", seats_changed: "Platzzahl geändert",
  clarification_requested: "Rückfrage gestellt", clarification_answered: "Rückfrage beantwortet",
  offer_cancelled: "Veranstaltung abgesagt",
  ...STATUS,
};
const TASK = { overdue: "Entscheidung überfällig", deadline_soon: "Frist endet bald",
  revision_pending: "Änderung zur Prüfung eingereicht", reply_needed: "Ihre Antwort ist offen" };
const CHANGE_LABEL = {
  starts_at: "Beginn", ends_at: "Ende", time_zone: "Zeitzone", capacity: "Kapazität",
  review_threshold: "Prüfschwelle", decision_deadline: "Entscheidungsfrist", format_code: "Format",
  public_location: "Ort", topic_id: "Thema", title: "Titel", summary: "Beschreibung", price_display_text: "Preishinweis",
};
const FORMAT = { online: "Online", praesenz: "Präsenz", hybrid: "Hybrid" };
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
  reservation_idempotency_conflict: "Dieser Auftrag wurde bereits anders verarbeitet. Bitte laden Sie die Übersicht neu.",
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

function filterControl(form, id, label, value, options, type = "text") {
  const group = element("div", null, "field");
  const caption = element("label", label);
  const input = element(options ? "select" : "input");
  caption.htmlFor = input.id = id;
  if (options) {
    for (const [key, title] of Object.entries(options)) {
      const option = element("option", title);
      option.value = key;
      input.append(option);
    }
  } else {
    input.type = type;
    if (type === "text") input.maxLength = 100;
  }
  input.value = value;
  group.append(caption, input);
  form.append(group);
  return input;
}

function query(path, values) {
  const url = new URL(path, location.origin);
  for (const [key, value] of Object.entries(values)) {
    if (value !== "") url.searchParams.set(key, value);
  }
  return url.pathname + url.search;
}

export function createReservations({ root, request, hasCsrf, expired }) {
  const heading = root.querySelector("h2");
  const scope = root.querySelector("[data-cal2-scope]");
  const status = root.querySelector("[role=status]");
  const notice = root.querySelector("[role=alert]");
  const content = root.querySelector("[data-cal2-content]");
  const initialReview = { status: "open", offer: "", coach: "", day: "", deadline: "" };
  const initialCatalogue = { search: "", day: "", offer_id: "" };
  let caps = {}, controller, currentForm, isReview = false;
  let reviewFilters = { ...initialReview }, catalogueFilters = { ...initialCatalogue, offer_id: initialOffer };
  const dirty = new Set();
  const hasDraft = () => Array.from(dirty).some(changed => changed());

  function canLeave() {
    if (currentForm) return window.confirm("Speicherung läuft noch. Zur Übersicht wechseln und dort den Status prüfen?");
    return !hasDraft() || window.confirm("Ungespeicherte Eingaben verwerfen?");
  }

  window.addEventListener("beforeunload", (event) => {
    if (currentForm || hasDraft()) {
      event.preventDefault();
      event.returnValue = true;
    }
  });

  function leave() {
    controller?.abort();
    controller = undefined;
    currentForm = undefined;
    dirty.clear();
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

  function listSection(title, path, render, empty, signal, id) {
    const section = element("section", null, "reservation-list");
    if (id) section.id = id;
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
        const data = await read(query(path, { after: after || "" }), signal);
        if (signal.aborted) return;
        list.append(...data.items.map(render));
        next = data.next_after;
        more.textContent = "Weitere laden";
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

  function offerFacts(item) {
    return facts([
      ["Thema", item.topic_name], ["Coach", item.coach_name],
      ["Beginn", date(item.starts_at)], ["Ende", date(item.ends_at)],
      ["Format", FORMAT[item.format_code]], ["Ort", item.public_location],
      ["Preishinweis", item.price_display_text], ["Freie Plätze", item.free_seats],
      ["Entscheidungsfrist", date(item.decision_deadline)],
    ]);
  }

  function catalogueCard(item) {
    const card = element("li", null, "calendar-card");
    const details = element("details", null, "reservation-offer-details");
    details.append(element("summary", "Veranstaltungsdetails"), offerFacts(item));
    if (item.summary) details.append(element("p", item.summary));
    card.append(element("h4", item.title), element("p", `${date(item.starts_at)} · ${FORMAT[item.format_code]} · ${item.free_seats} frei`), details);
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
      ["Status", item.status === "clarification" && item.clarification_answered ? "Antwort eingegangen" : STATUS[item.status]],
      ["Gewünschte Plätze", item.seats], ["Coach", item.coach_name],
      ["Beginn", date(item.starts_at)], ["Ende", date(item.ends_at)],
      ["Entscheidungsfrist", date(item.decision_deadline)],
      ["Firma", item.company_name], ["Kontaktperson", item.contact_name],
      ["Offen angefragt (Angebot)", item.requested_seats], ["Belegt (Angebot)", item.occupied_seats],
      ["Kapazität", item.capacity], ["Prüfschwelle", item.review_threshold], ["Offene Vorgänge (Angebot)", item.open_count],
    ]);
  }

  function attention(item) {
    if (!isReview || !isOpen(item)) return "";
    if (item.deadline_passed) return "Entscheidung überfällig";
    if (item.deadline_soon) return "Frist endet bald";
    if (item.occupied_seats >= item.review_threshold) return "Prüfschwelle erreicht";
    return "Prüfschwelle noch nicht erreicht";
  }

  function reservationCard(item) {
    const card = element("li", null, "calendar-card");
    card.append(element("h4", item.title), reservationFacts(item));
    if (attention(item)) card.append(element("p", attention(item), "calendar-status"));
    if (item.proposed_revision) card.append(element("p", "Änderung zur Prüfung eingereicht", "calendar-status"));
    card.append(button("Vorgang ansehen", () => void detail(item.id)));
    return card;
  }

  function filters(review) {
    const form = element("form", null, "reservation-filters");
    form.setAttribute("aria-label", review ? "Vorgänge filtern" : "Veranstaltungen suchen");
    const values = review ? reviewFilters : catalogueFilters;
    const fields = review ? {
      status: filterControl(form, "cal2-filter-status", "Status", values.status, {
        open: "Offene Vorgänge", pending: "Eingereicht", clarification: "Rückfragen",
        decision: "Entscheidung nötig", approved: "Positiv geprüft", rejected: "Abgelehnt",
        withdrawn: "Zurückgenommen", cancelled: "Veranstaltung abgesagt", past: "Vergangene Vorgänge",
        "": "Alle Vorgänge",
      }),
      offer: filterControl(form, "cal2-filter-offer", "Veranstaltung", values.offer),
      coach: filterControl(form, "cal2-filter-coach", "Coach", values.coach),
      day: filterControl(form, "cal2-filter-day", "Veranstaltungstag", values.day, null, "date"),
      deadline: filterControl(form, "cal2-filter-deadline", "Entscheidungsfrist", values.deadline,
        { "": "Alle Fristen", overdue: "Überfällig", soon: "Nächste 48 Stunden", later: "Später" }),
    } : {
      search: filterControl(form, "cal2-search", "Titel oder Thema", values.search),
      day: filterControl(form, "cal2-day", "Veranstaltungstag", values.day, null, "date"),
    };
    const actions = element("div", null, "button-row");
    const apply = element("button", review ? "Filtern" : "Suchen", "button button-primary");
    apply.type = "submit";
    actions.append(apply, button("Zurücksetzen", () => {
      if (review) reviewFilters = { ...initialReview };
      else clearCatalogueLink();
      void show(review);
    }));
    form.append(actions);
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      for (const [key, input] of Object.entries(fields)) values[key] = input.value.trim();
      if (!review && catalogueFilters.offer_id) {
        const updated = { ...catalogueFilters, offer_id: "" };
        clearCatalogueLink();
        catalogueFilters = updated;
      }
      void show(review);
    });
    return form;
  }

  function clearCatalogueLink() {
    catalogueFilters = { ...initialCatalogue };
    const url = new URL(location.href);
    url.searchParams.delete("offer");
    history.replaceState(history.state, "", url);
  }

  async function activity(review, signal) {
    const container = element("details", null, "reservation-activity");
    const summary = element("summary", "Aufgaben und Ereignisse");
    const body = element("div");
    container.append(summary, body);
    content.append(container);
    let loaded = false;
    container.addEventListener("toggle", async () => {
      if (!container.open || loaded) return;
      loaded = true;
      const note = element("p", "Wird geladen …");
      note.setAttribute("role", "status");
      body.replaceChildren(note);
      try {
        const data = await read(query(API + "/activity", { review }), signal);
        if (signal.aborted) return;
        body.replaceChildren();
        for (const [title, entries, labels] of [
          ["Anstehende Aufgaben", data.tasks, TASK], ["Letzte Ereignisse", data.events, EVENT],
        ]) {
          const list = element("ul", null, "reservation-activity-list");
          for (const entry of entries) {
            const line = element("li");
            line.append(button(`${labels[entry.kind]}: ${entry.title}`, () => {
              if (canLeave()) void detail(entry.reservation_id);
            }), element("small", date(entry.occurred_at || entry.decision_deadline)));
            list.append(line);
          }
          body.append(element("h3", title), entries.length ? list : element("p", "Keine Einträge."));
        }
      } catch {
        if (signal.aborted) return;
        note.textContent = "Die Übersicht konnte nicht geladen werden.";
        body.append(button("Erneut laden", () => { loaded = false; container.dispatchEvent(new Event("toggle")); }));
      }
    });
  }

  function communicationDrafts(review, signal) {
    const container = element("details", null, "reservation-activity");
    const summary = element("summary", "Kommunikationsentwürfe");
    const status = element("p");
    status.setAttribute("role", "status");
    const list = element("ul", null, "reservation-activity-list");
    const retry = button("Entwürfe erneut laden", () => { summary.focus(); void load(); });
    retry.hidden = true;
    let requested = false;
    container.append(summary, element("p", "Nur Entwürfe. Es wird nichts versendet."), status, list, retry);
    content.append(container);
    container.addEventListener("toggle", () => {
      if (container.open && !requested) void load();
    });

    async function load() {
      requested = true;
      retry.hidden = true;
      status.textContent = "Entwürfe werden geladen …";
      try {
        const data = await read(query(API + "/communication-drafts", { review }), signal);
        if (signal.aborted) return;
        for (const entry of data.items) {
          const event = Object.hasOwn(EVENT, entry.kind) ? EVENT[entry.kind] : "Änderung der Vormerkung";
          const when = date(entry.occurred_at);
          const row = element("li");
          row.append(element("span", `${event} · ${when}`), button("Zum Vorgang", () => {
            if (canLeave()) void detail(entry.reservation_id);
          }));
          row.lastElementChild.setAttribute("aria-label", `Zum Vorgang: ${event}, ${when}`);
          list.append(row);
        }
        status.textContent = data.items.length ? "" : "Keine Kommunikationsentwürfe vorhanden.";
      } catch {
        if (signal.aborted) return;
        list.replaceChildren();
        status.textContent = "Kommunikationsentwürfe konnten nicht geladen werden.";
        retry.hidden = false;
      }
    }
  }

  async function show(review, message = "", { reviewFilters: preset, catalogue = false } = {}) {
    leave();
    isReview = review;
    if (review && preset) reviewFilters = { ...initialReview, ...preset };
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
    activity(review, signal);
    communicationDrafts(review, signal);
    const control = filters(review);
    if (review) {
      content.append(control);
      await listSection("Vorgänge", query(API, { review, ...reviewFilters }), reservationCard,
        "Keine Vorgänge für diese Auswahl.", signal);
      return;
    }
    const own = () => listSection("Vormerkungen Ihrer Firma", API, reservationCard,
      "Noch keine Vormerkungen.", signal, "reservation-own");
    const ownList = catalogueFilters.offer_id ? null : own();
    if (catalogueFilters.offer_id) {
      const clear = button("Alle Veranstaltungen", () => { clearCatalogueLink(); void show(false); });
      content.append(clear);
    }
    content.append(control);
    const catalogueList = listSection(catalogueFilters.offer_id ? "Ausgewählte Veranstaltung" : "Veröffentlichte Gruppenangebote",
      query(API + "/catalogue", catalogueFilters), catalogueCard, catalogueFilters.offer_id
        ? "Für diese Veranstaltung sind keine neuen Vormerkungen möglich." : "Keine passenden Angebote für Vormerkungen gefunden.",
      signal, "reservation-catalogue");
    if (catalogue) control.querySelector("#cal2-search").focus();
    await Promise.all([catalogueList, ownList ?? own()]);
  }

  function openPanel(title) {
    leave();
    const signal = (controller = new AbortController()).signal;
    const back = button("Zur Übersicht", () => { if (canLeave()) void show(isReview); });
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
      if (item.proposed_revision) {
        const changes = item.changed_fields.map(field => CHANGE_LABEL[field]).filter(Boolean);
        const warning = element("div", null, "notice");
        warning.append(element("strong", "Änderung zur Prüfung eingereicht"),
          element("p", changes.length ? `Betroffen: ${changes.join(", ")}.` : "Keine Änderung der gezeigten Angebotsdaten."),
          element("p", "Die Vormerkung gilt für den zuletzt veröffentlichten Stand. Keine automatische Übernahme; Veröffentlichung bleibt bei belegten Plätzen gesperrt."));
        content.append(warning);
      }
      if (isOpen(item) && item.deadline_passed) {
        content.append(element("p", "Keine neuen oder zusätzlichen Plätze. Die Vormerkung bleibt bis zu einer Entscheidung oder Rücknahme offen."));
      }
      content.append(facts([["Telefon", item.phone], ["Nachricht", item.message]]));
      if (isOpen(item) && hasCsrf()) {
        if (isReview) decisionForm(item, signal);
        else {
          if (item.offer_available) changeForm(item, signal);
          if (item.status === "clarification" && !item.clarification_answered) replyForm(item, signal);
          const withdraw = button("Vormerkung zurücknehmen", () => {
            if (!canLeave()) return;
            const form = commandForm("Rücknahme bestätigen", signal, API + `/${item.id}/withdraw`,
              "POST", version(item), () => ({}), "Vormerkung zurückgenommen.", () => detail(item.id));
            form.container.prepend(element("p", "Die vorgemerkten Plätze werden wieder frei."));
            withdraw.replaceWith(form.node);
            form.submit.focus();
          });
          content.append(withdraw);
        }
      }
      content.append(element("h4", item.history.length === 50 ? "Statusverlauf (letzte 50 Einträge)" : "Statusverlauf"));
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

  function commandForm(label, signal, path, method, headers, payload, success, cancel) {
    const node = element("form", null, "reservation-form");
    const container = element("fieldset");
    const submit = element("button", label, "button button-primary");
    submit.type = "submit";
    const fields = {};
    let fingerprint, requestId;
    node.noValidate = true;
    const actions = element("div", null, "button-row");
    actions.append(submit, button("Abbrechen", () => { if (canLeave()) void cancel(); }));
    node.append(container, actions);
    let baseline;
    const changed = () => {
      if (baseline === undefined) return false;
      return JSON.stringify(payload()) !== baseline;
    };
    dirty.add(changed);
    queueMicrotask(() => { baseline = JSON.stringify(payload()); });
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
      if (Array.from(dirty).some(other => other !== changed && other()) &&
          !window.confirm("Andere ungespeicherte Eingaben werden verworfen. Diese Aktion speichern?")) return;
      const key = JSON.stringify(body);
      if (key !== fingerprint) { fingerprint = key; requestId = crypto.randomUUID(); }
      const running = currentForm = Symbol();
      container.disabled = submit.disabled = true;
      status.textContent = "Wird gespeichert …";
      try {
        const response = await request(path, {
          method, headers, csrf: "session", body: { ...body, request_id: requestId },
          signal: AbortSignal.any([signal, AbortSignal.timeout(15000)]),
        });
        if (signal.aborted) return;
        if (response.status === 401) { expired(); return; }
        if (response.ok) { void show(isReview, success); return; }
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
      "Vormerkung eingereicht. Es wurde nichts verbindlich gebucht.", () => show(false));
    content.append(offerFacts(item), form.node);
    if (item.summary) form.node.before(element("p", item.summary));
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
      version(item), () => ({ seats: seats.valueAsNumber }), "Platzzahl geändert.", () => detail(item.id));
    const seats = seatsField(form, String(item.seats), item.deadline_passed ? item.seats : item.capacity);
    content.append(form.node);
  }

  function replyForm(item, signal) {
    const form = commandForm("Antwort senden", signal, API + `/${item.id}/reply`, "POST",
      version(item), () => ({ reason: reply.value.trim() }), "Antwort im Vorgang gespeichert.", () => detail(item.id));
    const input = element("textarea");
    input.required = true; input.rows = 3; input.maxLength = 500;
    const reply = field(form, "reason", "Antwort auf die Rückfrage", input);
    content.append(form.node);
  }

  function decisionForm(item, signal) {
    const form = commandForm("Entscheidung speichern", signal, API + `/${item.id}/decide`, "POST",
      version(item), () => ({ outcome: outcome.value, reason: reason.value.trim() }), "Entscheidung gespeichert.", () => detail(item.id));
    const select = element("select");
    select.required = true;
    for (const [value, text] of Object.entries({
      "": "Bitte auswählen", clarification_requested: "Klärung anfordern",
      approved: "Positiv prüfen (keine Buchung)", rejected: "Ablehnen",
    })) {
      const option = element("option", text);
      option.value = value;
      if (value === "approved" && !item.offer_available) option.disabled = true;
      if (value === "clarification_requested" && item.status === "clarification" && !item.clarification_answered) option.disabled = true;
      select.append(option);
    }
    const outcome = field(form, "outcome", "Entscheidung", select);
    const reason = element("textarea");
    reason.required = true; reason.rows = 3; reason.maxLength = 500;
    field(form, "reason", "Begründung für die Firma", reason);
    content.append(form.node);
  }

  return { available, show, leave, canLeave, linkedOffer: () => Boolean(catalogueFilters.offer_id), reset() {
    leave();
    caps = {};
    reviewFilters = { ...initialReview };
    catalogueFilters = { ...initialCatalogue, offer_id: new URLSearchParams(location.search).has("offer") ? initialOffer : "" };
  } };
}
