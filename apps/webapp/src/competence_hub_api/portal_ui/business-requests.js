const API = "/api/v1/portal/requests";
const STATUSES = new Map([["open", "Offen"], ["in_progress", "In Bearbeitung"], ["waiting", "Wartend"], ["closed", "Abgeschlossen"]]);
const AUDIT_ACTIONS = new Map([["created", "Anfrage erstellt"], ["updated", "Anfrage geändert"], ["note_added", "Notiz hinzugefügt"]]);
const FIELD_LABELS = new Map(Object.entries({
  subject: "Betreff", description: "Beschreibung", status: "Status", company_id: "Unternehmen",
  private_customer_id: "Privatkunde", responsible_user_id: "Interne Zuständigkeit", desired_period: "Wunschzeitraum",
  preferred_format: "Bevorzugtes Format", service_id: "Leistung", offer_id: "Kalenderangebot", coach_id: "Coach",
  follow_up_on: "Wiedervorlage", coach_summary: "Coach-Freigabetext", notes: "Notizen",
}));

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text != null) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function button(text, handler, primary = false) {
  const node = element("button", text, `button button-${primary ? "primary" : "secondary"}`);
  node.type = "button";
  if (handler) node.addEventListener("click", handler);
  return node;
}

function focus(node) {
  node.tabIndex = -1;
  node.focus();
}

function date(value) {
  if (!value) return "";
  const instant = new Date(value);
  if (!Number.isFinite(instant.getTime())) return "";
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "medium", timeZone: value.length === 10 ? "UTC" : "Europe/Berlin",
  }).format(instant);
}

function field(name, label, { value = "", required = false, type = "text", maxLength, choices } = {}) {
  const control = element(choices ? "select" : type === "textarea" ? "textarea" : "input");
  if (choices) {
    for (const [key, caption] of choices) {
      const option = element("option", caption);
      option.value = key;
      control.append(option);
    }
  } else if (type === "textarea") {
    control.rows = 5;
  } else {
    control.type = type;
  }
  control.id = `requests-${name}`;
  control.name = name;
  control.value = value ?? "";
  control.required = required;
  if (maxLength) control.maxLength = maxLength;
  const title = element("label", label);
  title.htmlFor = control.id;
  const row = element("div", null, "field");
  row.append(title, control);
  return row;
}

function facts(values) {
  const list = element("dl", null, "calendar-card-meta request-facts");
  for (const [label, value] of values) {
    if (value != null && value !== "") list.append(element("dt", label), element("dd", value));
  }
  return list;
}

export function createBusinessRequests({ root, request, hasCsrf, expired }) {
  const scope = root.querySelector("[data-request-scope]");
  const status = root.querySelector("[role=status]");
  const notice = root.querySelector("[role=alert]");
  const content = root.querySelector("[data-request-content]");
  const optionLabels = new Map();
  let caps = {}, operation, editor, listFilter = "";

  function error(node, message = "") {
    node.textContent = message;
    node.hidden = !message;
    if (message) focus(node);
  }

  function snapshot(form) {
    return JSON.stringify([...new FormData(form)]);
  }

  function dirty() {
    return editor && (editor.saving || snapshot(editor.form) !== editor.baseline);
  }

  function canLeave() {
    if (editor?.saving) {
      return window.confirm("Speicherung läuft noch. Möchten Sie den Bereich verlassen und danach den Stand prüfen?");
    }
    return !dirty() || window.confirm("Ungespeicherte Eingaben verwerfen?");
  }

  window.addEventListener("beforeunload", (event) => {
    if (dirty()) {
      event.preventDefault();
      event.returnValue = true;
    }
  });

  function leave() {
    operation?.abort();
    operation = undefined;
    editor = undefined;
    listFilter = "";
    optionLabels.clear();
    content.replaceChildren();
    status.textContent = "";
    scope.textContent = "";
    error(notice);
  }

  function reset() {
    leave();
    caps = {};
    root.hidden = true;
  }

  async function available(valid) {
    try {
      const response = await request(`${API}/capabilities`);
      const data = response.ok ? await response.json() : {};
      if (!valid()) return false;
      caps = data;
      return data.enabled === true && data.can_read === true && ["internal", "company", "coach"].includes(data.scope);
    } catch {
      return false;
    }
  }

  function begin(message) {
    operation?.abort();
    operation = new AbortController();
    status.textContent = message;
    error(notice);
    return operation.signal;
  }

  const current = (signal) => !signal.aborted && operation?.signal === signal;
  const pathFor = (id) => `${API}/${encodeURIComponent(id)}`;
  const staff = () => caps.scope === "internal" && caps.can_manage === true;
  const coach = () => caps.scope === "coach";

  async function read(path, signal) {
    const response = await request(path, { signal });
    if (!current(signal)) return null;
    if (response.status === 401) { expired(); return null; }
    if (!response.ok) throw new Error(String(response.status));
    const data = await response.json();
    return current(signal) ? data : null;
  }

  const statusLabel = (value) => STATUSES.get(value) ?? (value ? "Unbekannter Status" : "");

  function reference(data, key) {
    const id = data[`${key}_id`];
    return id ? data[`${key}_label`] ?? optionLabels.get(id) ?? "Zugewiesen" : null;
  }

  function notesSection(data, title, staffView) {
    const section = element("section");
    const notes = element("ul", null, "requests-list");
    for (const note of data.notes || []) {
      if (!staffView && note.visibility && note.visibility !== "coach") continue;
      const item = element("li");
      const type = staffView ? note.visibility === "coach" ? "Als Coach-Notiz erfasst" : "Intern" : null;
      item.append(element("p", [type, date(note.created_at)].filter(Boolean).join(" · ")),
        element("p", note.body, "request-text"));
      notes.append(item);
    }
    section.append(element("h4", title), notes.childElementCount ? notes : element("p", "Keine Notizen vorhanden.", "empty-state"));
    if (data.has_more_notes) section.append(element("p", "Die neuesten 50 Notizen werden angezeigt."));
    return section;
  }

  function historySection(data) {
    const history = element("details", null, "reservation-activity");
    const items = element("ul", null, "reservation-history");
    for (const entry of data.audit || []) {
      const note = element("li");
      const fields = (entry.changed_fields || []).map((name) => FIELD_LABELS.get(name)).filter(Boolean);
      note.append(element("strong", AUDIT_ACTIONS.get(entry.action) ?? "Änderung"),
        element("p", [date(entry.occurred_at), fields.join(", ")].filter(Boolean).join(" · ")));
      items.append(note);
    }
    history.append(element("summary", "Verlauf"), items.childElementCount ? items : element("p", "Keine Änderungen erfasst."));
    if (data.has_more_audit) history.append(element("p", "Die neuesten 50 Änderungen werden angezeigt."));
    return history;
  }

  function row(item) {
    const entry = element("li");
    const title = coach() ? "Freigegebene Anfrage" : item.subject;
    const summary = element("p", coach() ? item.coach_summary : [statusLabel(item.status),
      staff() && (reference(item, "company") || reference(item, "private_customer")),
      staff() && item.follow_up_on && `Wiedervorlage: ${date(item.follow_up_on)}`].filter(Boolean).join(" · "));
    const open = button("Details öffnen", () => void showDetail(item.id));
    open.dataset.requestId = item.id;
    open.setAttribute("aria-label", `Details öffnen: ${title}`);
    entry.append(element("h4", title));
    if (summary.textContent) {
      summary.id = `request-summary-${item.id}`;
      open.setAttribute("aria-describedby", summary.id);
      entry.append(summary);
    }
    entry.append(open);
    return entry;
  }

  async function show({ restoreId, moveFocus = false } = {}) {
    editor = undefined;
    const signal = begin("Anfragen werden geladen …");
    scope.textContent = staff() ? "Business Operations" : coach() ? "Freigegebene Anfragen" : "Anfragen Ihres Unternehmens";
    const title = element("h3", "Übersicht");
    const list = element("ul", null, "requests-list");
    const actions = element("div", null, "button-row");
    const filters = element("form", null, "requests-filters");
    const section = element("section");
    const empty = element("p", "Keine Anfragen vorhanden.", "empty-state");
    empty.hidden = true;
    const more = button("Weitere Anfragen laden");
    more.hidden = true;
    section.append(title, actions);
    if (!coach()) {
      const filter = field("filter-status", "Status filtern", {
        choices: [["", "Alle Status"], ...STATUSES], value: listFilter,
      });
      const apply = button("Filtern");
      apply.type = "submit";
      filters.append(filter, apply);
      section.append(filters);
      filters.addEventListener("submit", (event) => {
        event.preventDefault();
        listFilter = filter.querySelector("select").value;
        void show({ moveFocus: true });
      });
    }
    section.append(empty, list, more);
    content.replaceChildren(section);
    if (moveFocus) focus(title);
    let after = null;

    async function load(append) {
      more.disabled = true;
      status.textContent = "Anfragen werden geladen …";
      error(notice);
      const params = new URLSearchParams();
      if (listFilter && !coach()) params.set("status", listFilter);
      if (append && after) params.set("after", after);
      try {
        const result = await read(`${API}${params.size ? `?${params}` : ""}`, signal);
        if (!result || !current(signal)) return;
        const { items, next_after: next } = result;
        const rows = items.map(row);
        if (append) list.append(...rows);
        else list.replaceChildren(...rows);
        after = next;
        empty.hidden = Boolean(list.childElementCount);
        more.hidden = !after;
        status.textContent = list.childElementCount === 1 ? "Eine Anfrage angezeigt." : `${list.childElementCount} Anfragen angezeigt.`;
        if (append && rows.length) rows[0].querySelector("button").focus();
        else if (restoreId && document.activeElement === title) {
          [...list.querySelectorAll("button")].find((action) => action.dataset.requestId === restoreId)?.focus();
        }
      } catch {
        if (!current(signal)) return;
        status.textContent = "";
        error(notice, "Anfragen konnten nicht geladen werden.");
        more.textContent = "Erneut laden";
        more.hidden = false;
      } finally {
        if (current(signal)) more.disabled = false;
      }
    }

    more.addEventListener("click", () => {
      more.textContent = "Weitere Anfragen laden";
      void load(Boolean(after));
    });
    const create = staff() && button("Anfrage erstellen", () => void openEditor("create"), true);
    if (create) actions.append(create);
    await load(false);
  }

  async function showDetail(id, message, saved) {
    editor = undefined;
    const signal = begin(message || "Anfrage wird geladen …");
    const back = button("Zur Übersicht", () => void show({ restoreId: id, moveFocus: true }));
    const detail = element("section", null, "request-detail");
    content.replaceChildren(back, detail);
    back.focus();
    try {
      const data = saved ?? await read(pathFor(id), signal);
      if (!data || !current(signal)) return;
      const title = element("h3", coach() ? "Freigegebene Anfrage" : data.subject);
      const values = coach() ? [] : [["Status", statusLabel(data.status)], ["Erstellt am", date(data.created_at)]];
      if (staff()) values.push(
        ["Unternehmen", reference(data, "company")], ["Privatkunde", reference(data, "private_customer")],
        ["Interne Zuständigkeit", reference(data, "responsible_user") || "Nicht zugewiesen"],
        ["Coach", reference(data, "coach") || "Nicht zugewiesen"],
        ["Wiedervorlage am", date(data.follow_up_on) || "Keine Frist"],
        ["Wunschzeitraum", data.desired_period], ["Bevorzugtes Format", data.preferred_format],
        ["Leistung", reference(data, "service")], ["Kalenderangebot", reference(data, "offer")],
      );
      detail.append(title);
      if (values.length) detail.append(facts(values));
      if (data.description && staff()) {
        detail.append(element("h4", "Beschreibung"), element("p", data.description, "request-text"));
      }
      if ((coach() || staff()) && data.coach_summary) {
        detail.append(element("h4", "Coach-Freigabetext"), element("p", data.coach_summary, "request-text"));
      }
      if (coach()) detail.append(notesSection(data, "Freigegebene Notizen", false));
      if (staff() && Number.isInteger(data.version)) {
        const actions = element("div", null, "button-row");
        actions.append(button("Bearbeiten", () => void openEditor("edit", data), true),
          button("Notiz hinzufügen", () => void openEditor("note", data)));
        detail.append(actions, notesSection(data, "Notizen", true), historySection(data));
      }
      status.textContent = message || "";
      if (document.activeElement === back) focus(title);
    } catch {
      if (!current(signal)) return;
      status.textContent = "";
      error(notice, "Diese Anfrage konnte nicht geladen werden.");
      detail.append(button("Erneut laden", () => void showDetail(id)));
    }
  }

  async function readOptionPage(bucket, signal, after) {
    const params = new URLSearchParams({ bucket });
    if (after) params.set("after", after);
    const page = await read(`${API}/options?${params}`, signal);
    if (!current(signal)) return null;
    for (const { id, label } of page?.items || []) optionLabels.set(id, label);
    return page;
  }

  function picker({ name, bucket, initial, signal, data, empty }) {
    const value = data?.[name] || "";
    const choices = [["", empty], ...initial.items.map(({ id, label }) => [id, label])];
    if (value && !initial.items.some(({ id }) => id === value)) {
      choices.push([value, data[`${name.slice(0, -3)}_label`] ?? optionLabels.get(value) ?? "Aktuelle Auswahl"]);
    }
    const label = FIELD_LABELS.get(name);
    const row = field(name, label, { value, choices });
    const select = row.querySelector("select");
    let after = initial.next_after;
    if (!after) return row;
    const more = button(`Weitere Optionen laden: ${label}`, async () => {
      more.disabled = true;
      try {
        const page = await readOptionPage(bucket, signal, after);
        if (!page || !current(signal)) return;
        for (const { id, label: caption } of page.items) {
          const existing = [...select.options].find((option) => option.value === id);
          if (existing) existing.textContent = caption;
          else {
            const option = element("option", caption);
            option.value = id;
            select.append(option);
          }
        }
        after = page.next_after;
        more.hidden = !after;
        more.textContent = `Weitere Optionen laden: ${label}`;
        if (!after && (document.activeElement === more || document.activeElement === document.body)) select.focus();
      } catch {
        if (current(signal)) more.textContent = `Optionen erneut laden: ${label}`;
      } finally {
        if (current(signal)) more.disabled = false;
      }
    });
    row.append(more);
    return row;
  }

  async function openEditor(mode, data) {
    const isCreate = mode === "create";
    const isNote = mode === "note";
    const backAction = () => isCreate ? show({ moveFocus: true }) : showDetail(data.id);
    const signal = begin("Formular wird geladen …");
    const back = button("Abbrechen", () => { if (canLeave()) void backAction(); });
    content.replaceChildren(back);
    back.focus();
    try {
      const buckets = isNote ? [] : isCreate
        ? ["companies", "private_customers", "services", "offers"] : ["responsible_users", "coaches", "services", "offers"];
      const loaded = await Promise.all(buckets.map(async (bucket) => [bucket, await readOptionPage(bucket, signal)]));
      if (!current(signal)) return;
      const pages = Object.fromEntries(loaded);
      const pick = (name, bucket, empty = "Keine Auswahl") => picker({ name, bucket, initial: pages[bucket], signal, data, empty });
      const title = element("h3", isCreate ? "Neue Anfrage" : isNote ? "Notiz hinzufügen" : "Anfrage bearbeiten");
      const form = element("form", null, "requests-form");
      const fields = element("fieldset");
      const feedback = element("p", null, "form-error");
      feedback.id = "requests-form-error";
      feedback.setAttribute("role", "alert");
      feedback.hidden = true;
      let invalidFields = [];
      function clearValidation() {
        for (const control of invalidFields) {
          control.removeAttribute("aria-invalid");
          control.removeAttribute("aria-describedby");
        }
        invalidFields = [];
        error(feedback);
      }
      function validationError(message, ...controls) {
        invalidFields = controls;
        for (const control of controls) {
          control.setAttribute("aria-invalid", "true");
          control.setAttribute("aria-describedby", feedback.id);
        }
        feedback.textContent = message;
        feedback.hidden = false;
        controls[0].focus();
      }
      form.addEventListener("input", (event) => {
        if (invalidFields.includes(event.target)) clearValidation();
      });
      const actions = element("div", null, "button-row");
      const save = button(isCreate ? "Anfrage speichern" : isNote ? "Notiz speichern" : "Änderungen speichern", null, true);
      save.type = "submit";
      const reload = button("Aktuellen Stand laden", () => { if (canLeave()) void backAction(); });
      reload.hidden = true;
      actions.append(save, reload);
      if (isCreate) {
        fields.append(field("subject", "Betreff", { required: true, maxLength: 160 }),
          field("description", "Beschreibung", { type: "textarea", required: true, maxLength: 4000 }),
          pick("company_id", "companies"), pick("private_customer_id", "private_customers"),
          field("desired_period", "Wunschzeitraum", { maxLength: 160 }),
          field("preferred_format", "Bevorzugtes Format", { maxLength: 100 }),
          pick("service_id", "services"), pick("offer_id", "offers"));
      } else if (isNote) {
        fields.append(field("visibility", "Sichtbarkeit", { choices: [
          ["internal", "Nur internes Team"], ...(data.coach_id ? [["coach", "Auch für den zugewiesenen Coach"]] : []),
        ], value: "internal", required: true }),
        field("body", "Notiz", { type: "textarea", required: true, maxLength: 2000 }));
      } else {
        const choices = [...STATUSES];
        if (data.status && !STATUSES.has(data.status)) choices.unshift([data.status, "Bisheriger Status"]);
        const coachField = pick("coach_id", "coaches", "Nicht zugewiesen");
        const summaryField = field("coach_summary", "Coach-Freigabetext", {
          type: "textarea", maxLength: 1200, value: data.coach_summary,
        });
        const coachSelect = coachField.querySelector("select");
        summaryField.hidden = !coachSelect.value;
        coachSelect.addEventListener("change", () => {
          summaryField.querySelector("textarea").value = coachSelect.value === data.coach_id ? data.coach_summary ?? "" : "";
          summaryField.hidden = !coachSelect.value;
        });
        fields.append(field("status", "Status", { value: data.status, required: true, choices }),
          pick("responsible_user_id", "responsible_users", "Nicht zugewiesen"), coachField,
          field("follow_up_on", "Wiedervorlage am", { value: data.follow_up_on, type: "date" }),
          pick("service_id", "services"), pick("offer_id", "offers"), summaryField);
      }
      fields.append(feedback, actions);
      form.append(fields);
      content.append(title, form);
      editor = { form, baseline: snapshot(form), saving: false };
      status.textContent = "";
      if (document.activeElement === back) focus(title);

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (!current(signal) || editor.saving) return;
        clearValidation();
        if (!hasCsrf()) {
          error(feedback, "Bitte melden Sie sich für Änderungen erneut an.");
          return;
        }
        let body = Object.fromEntries([...new FormData(form)].map(([key, value]) => [key, value.trim() || null]));
        const blank = [...form.elements].find((control) => control.required && control.name && !body[control.name]);
        if (blank) {
          validationError("Bitte füllen Sie alle Pflichtfelder aus.", blank);
          return;
        }
        if (isCreate && Boolean(body.company_id) === Boolean(body.private_customer_id)) {
          validationError("Wählen Sie entweder ein Unternehmen oder einen Privatkunden.",
            form.elements.company_id, form.elements.private_customer_id);
          return;
        }
        if (!isNote && body.service_id && body.offer_id) {
          validationError("Wählen Sie entweder eine Leistung oder ein Kalenderangebot.",
            form.elements.service_id, form.elements.offer_id);
          return;
        }
        if (!isCreate && !isNote) {
          body = Object.fromEntries(Object.entries(body).filter(([key, value]) => (data[key] ?? null) !== value));
          if (!Object.keys(body).length) { void backAction(); return; }
        }
        if (!isCreate) body.version = data.version;
        const path = isCreate ? API : `${pathFor(data.id)}${isNote ? "/notes" : ""}`;
        editor.saving = true;
        fields.disabled = true;
        form.setAttribute("aria-busy", "true");
        status.textContent = "Wird gespeichert …";
        let failure;
        try {
          const response = await request(path, {
            method: isCreate || isNote ? "POST" : "PATCH", csrf: "session", body, signal,
          });
          if (!current(signal)) return;
          if (response.status === 401) { expired(); return; }
          if (!response.ok) {
            if ([409, 412].includes(response.status) && !isCreate) {
              save.disabled = true;
              reload.hidden = false;
              failure = "Der Datenstand hat sich geändert. Laden Sie den aktuellen Stand vor einer erneuten Bearbeitung.";
            } else if (response.status === 403) {
              failure = "Speichern nicht erlaubt. Prüfen Sie Ihre Berechtigung oder melden Sie sich erneut an.";
            } else if ([400, 422].includes(response.status)) {
              failure = "Bitte prüfen Sie die eingegebenen Daten.";
            } else {
              failure = "Speichern fehlgeschlagen. Prüfen Sie den aktuellen Stand, bevor Sie es erneut versuchen.";
            }
            return;
          }
          const saved = await response.json();
          if (!current(signal)) return;
          void showDetail(saved.id, isNote ? "Notiz gespeichert." : "Anfrage gespeichert.", saved);
        } catch {
          failure = "Speicherung nicht bestätigt. Prüfen Sie den aktuellen Stand.";
        } finally {
          if (current(signal)) {
            status.textContent = "";
            editor.saving = false;
            fields.disabled = false;
            form.setAttribute("aria-busy", "false");
            if (failure) error(feedback, failure);
          }
        }
      });
    } catch {
      if (!current(signal)) return;
      status.textContent = "";
      error(notice, "Das Formular konnte nicht geladen werden.");
      content.append(button("Erneut laden", () => void openEditor(mode, data)));
    }
  }

  return { available, show, leave, reset, canLeave };
}
