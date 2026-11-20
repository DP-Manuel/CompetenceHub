const api = "/api/v1/portal/customers";
const addressFields = [
  ["street", "Straße und Hausnummer", 200],
  ["postal_code", "Postleitzahl", 20],
  ["city", "Ort", 120],
  ["country", "Land", 100],
];

function element(tag, text = "", className = "") {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = text;
  return node;
}

function button(text, style = "secondary", type = "button") {
  const control = element("button", text, `button button-${style}`);
  control.type = type;
  return control;
}

function field(prefix, name, title, maxLength, options = {}) {
  const wrapper = element("div", "", "field");
  const label = element("label", options.required ? `${title} *` : title);
  const input = element("input");
  input.name = name;
  input.id = `${prefix}-${name}`;
  label.htmlFor = input.id;
  input.type = options.type || "text";
  input.maxLength = maxLength;
  input.required = Boolean(options.required);
  input.value = options.value || "";
  input.autocomplete = "off";
  wrapper.append(label, input);
  return wrapper;
}

function addressFieldsFor(prefix, initial, business) {
  const block = element("details");
  const caption = business ? "Geschäfts- oder Rechnungsanschrift" : "Rechnungsanschrift";
  block.open = Boolean(initial);
  block.append(element("summary", `${caption} (optional)`));
  if (business) {
    const wrapper = element("div", "", "field");
    const label = element("label", "Art der Anschrift");
    const select = element("select");
    select.id = `${prefix}-purpose`;
    select.name = "purpose";
    label.htmlFor = select.id;
    for (const [value, title] of [["business", "Geschäftsanschrift"], ["billing", "Rechnungsanschrift"]]) {
      select.add(new Option(title, value));
    }
    select.value = initial?.purpose || "business";
    wrapper.append(label, select);
    block.append(wrapper);
  }
  const grid = element("div", "", "form-grid");
  for (const [name, title, length] of addressFields) {
    grid.append(field(prefix, name, title, length, { value: initial?.[name] }));
  }
  block.append(grid);
  return block;
}

function readAddress(form, addressBlock, business) {
  const address = Object.fromEntries(addressFields.map(([name]) => [name, form.elements[name].value.trim()]));
  if (!Object.values(address).some(Boolean)) return null;
  const empty = addressFields.find(([name]) => !address[name]);
  if (empty) {
    addressBlock.open = true;
    form.elements[empty[0]].focus();
    throw new Error("Bitte füllen Sie die Anschrift vollständig aus oder lassen Sie sie leer.");
  }
  return business ? { ...address, purpose: form.elements.purpose.value } : address;
}

export function createCustomerAdministration({ request, hasCsrf, expired }) {
  let root, businessRoot, privatePanel, privateList, privateDetail, privateStatus;
  let companyId, onModeChange, mode, search, more, companyDraft, privateDraft;
  let generation = 0;
  let searchSequence = 0;
  let privateSequence = 0;
  let active = false;
  let query = "";
  let next = null;

  function reset() {
    generation++;
    active = false;
    root?.replaceChildren();
    businessRoot?.replaceChildren();
    onModeChange?.(true);
    companyId = companyDraft = privateDraft = undefined;
    root = businessRoot = onModeChange = undefined;
    mode = "business";
    query = "";
    next = null;
  }

  const dirty = () => [privateDraft, companyDraft].some((draft) => draft?.dirty);
  const busy = () => [privateDraft, companyDraft].some((draft) => draft?.saving);
  const canLeave = () => !busy() && (!dirty() || window.confirm("Ungespeicherte Änderungen verwerfen?"));
  window.addEventListener("beforeunload", (event) => {
    if (dirty() || busy()) {
      event.preventDefault();
      event.returnValue = "";
    }
  });

  async function fetchResult(path, options, fallback) {
    const current = generation;
    const response = await request(`${api}${path}`, options);
    if (current !== generation) return null;
    if (response.status === 401) {
      expired();
      return null;
    }
    if (response.status === 409) {
      throw new Error("Der Datensatz wurde geändert. Brechen Sie ab und öffnen Sie ihn erneut.");
    }
    if (response.status === 403) throw new Error("Die Sitzung konnte nicht bestätigt werden.");
    if (response.status === 400) throw new Error("Bitte prüfen Sie die eingegebenen Daten.");
    if (!response.ok) throw new Error(fallback);
    return response.json();
  }

  async function loadPrivate({ append = false } = {}) {
    const serial = ++searchSequence;
    const current = generation;
    if (!hasCsrf()) {
      privateStatus.textContent = "Bitte melden Sie sich erneut an.";
      return;
    }
    if (!append) privateList.replaceChildren();
    more.hidden = true;
    privateStatus.textContent = "Privatkunden werden geladen …";
    try {
      const result = await fetchResult("/private/search", {
        method: "POST", csrf: "session", body: { name: query, after: append ? next : null },
      }, "Die Privatkunden konnten nicht geladen werden.");
      if (!result || current !== generation || serial !== searchSequence || mode !== "private") return;
      for (const item of result.items) {
        const row = element("li");
        const control = button(`${item.first_name} ${item.last_name}`);
        control.dataset.customerId = item.id;
        control.addEventListener("click", () => loadPrivateDetail(item.id, control));
        row.append(control);
        privateList.append(row);
      }
      next = result.next_after;
      more.hidden = !next;
      privateStatus.textContent = privateList.children.length
        ? `${privateList.children.length} angezeigt` : "Keine Privatkunden gefunden.";
      if (append && !next) privateList.lastElementChild?.querySelector("button").focus();
      else if (append) more.focus();
    } catch (error) {
      if (current === generation && serial === searchSequence) privateStatus.textContent = error.message;
    }
  }

  async function loadPrivateDetail(id, trigger) {
    if (!canLeave()) return;
    const serial = ++privateSequence;
    const current = generation;
    privateDraft = undefined;
    privateDetail.replaceChildren(element("p", "Kundendaten werden geladen …"));
    try {
      const record = await fetchResult(`/private/${encodeURIComponent(id)}`, {}, "Kundendaten konnten nicht geladen werden.");
      if (record && current === generation && serial === privateSequence && mode === "private") {
        renderEditor(privateDetail, record, trigger);
      }
    } catch (error) {
      if (current === generation && serial === privateSequence) privateDetail.textContent = error.message;
    }
  }

  function renderEditor(target, record, trigger, { business = false } = {}) {
    const prefix = business ? "customer-business" : "customer-private";
    const draft = { dirty: false, saving: false };
    if (business) companyDraft = draft;
    else privateDraft = draft;
    const form = element("form", "", "edit-form");
    const title = business ? "Anschrift und USt-IdNr." : record ? "Privatkunde bearbeiten" : "Privatkunde anlegen";
    form.setAttribute("aria-label", title);
    const heading = element("h3", title);
    const grid = element("div", "", "form-grid");
    if (business) {
      grid.append(field(prefix, "vat_id", "Umsatzsteuer-ID (optional)", 32, { value: record.vat_id }));
    } else {
      grid.append(
        field(prefix, "first_name", "Vorname", 100, { value: record?.first_name, required: true }),
        field(prefix, "last_name", "Nachname", 100, { value: record?.last_name, required: true }),
        field(prefix, "email", "E-Mail (optional)", 254, { value: record?.email, type: "email" }),
        field(prefix, "phone", "Telefon (optional)", 50, { value: record?.phone, type: "tel" }),
      );
    }
    const address = addressFieldsFor(prefix, business ? record.address : record?.billing_address, business);
    const feedback = element("p", "", "form-error");
    feedback.setAttribute("role", "alert");
    feedback.hidden = true;
    const actions = element("div", "", "button-row");
    const save = button("Speichern", "primary", "submit");
    const cancel = button("Abbrechen");
    save.disabled = !hasCsrf();
    actions.append(save, cancel);
    form.append(heading, grid, address, feedback, actions);
    target.replaceChildren(form);
    if (!business) grid.querySelector("input").focus();
    form.addEventListener("input", () => { draft.dirty = true; });
    form.addEventListener("change", () => { draft.dirty = true; });
    cancel.addEventListener("click", () => {
      if (!canLeave()) return;
      if (business) {
        companyDraft = undefined;
        target.replaceChildren();
        trigger.open = false;
        trigger.querySelector("summary").focus();
      } else {
        privateDraft = undefined;
        target.replaceChildren();
        trigger?.focus();
      }
    });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!hasCsrf() || draft.saving) return;
      feedback.hidden = true;
      const current = generation;
      try {
        const optional = (name) => form.elements[name].value.trim() || null;
        const addressValue = readAddress(form, address, business);
        const payload = business
          ? { version: record.version, vat_id: optional("vat_id"), address: addressValue }
          : { first_name: optional("first_name"), last_name: optional("last_name"),
              email: optional("email"), phone: optional("phone"), billing_address: addressValue,
              ...(record ? { version: record.version } : {}) };
        draft.saving = true;
        for (const control of form.elements) control.disabled = true;
        const path = business ? `/companies/${encodeURIComponent(record.company_id)}/details`
          : record ? `/private/${encodeURIComponent(record.id)}` : "/private";
        const saved = await fetchResult(path, {
          method: record ? "PUT" : "POST", csrf: "session", body: payload,
        }, "Die Änderungen konnten nicht gespeichert werden.");
        if (!saved || current !== generation || !form.isConnected) return;
        if (business) {
          renderEditor(target, saved, trigger, { business });
          const status = element("p", "Gespeichert.");
          status.setAttribute("role", "status");
          target.prepend(status);
          trigger.querySelector("summary").focus();
        } else {
          privateDraft = undefined;
          target.replaceChildren();
          await loadPrivate();
          if (current !== generation || mode !== "private") return;
          privateStatus.textContent = "Privatkunde gespeichert.";
          const savedRow = [...privateList.querySelectorAll("button")]
            .find((control) => control.dataset.customerId === saved.id);
          (savedRow || (trigger?.isConnected ? trigger : search)).focus();
        }
      } catch (error) {
        if (current === generation && form.isConnected) {
          feedback.textContent = error.message;
          feedback.hidden = false;
        }
      } finally {
        if (draft.saving) {
          draft.saving = false;
          for (const control of form.elements) control.disabled = false;
        }
      }
    });
  }

  async function mount(anchor, { setBusinessVisible }) {
    reset();
    root = anchor;
    onModeChange = setBusinessVisible;
    const current = generation;
    try {
      const result = await fetchResult("/capabilities", {}, "");
      if (!result?.enabled || current !== generation) return false;
    } catch {
      return false;
    }
    active = true;
    const switcher = element("div", "", "button-row");
    switcher.setAttribute("role", "group");
    switcher.setAttribute("aria-label", "Kundenart");
    const business = button("Geschäftskunden");
    const privateButton = button("Privatkunden");
    switcher.append(business, privateButton);
    privatePanel = element("section");
    privatePanel.setAttribute("aria-label", "Privatkundenverwaltung");
    const searchForm = element("form", "", "search-bar");
    searchForm.setAttribute("role", "search");
    searchForm.setAttribute("aria-label", "Privatkunden");
    searchForm.append(field("private-search", "name", "Privatkunden suchen", 200, { type: "search" }),
      button("Suchen", "secondary", "submit"));
    search = searchForm.elements.namedItem("name");
    privateStatus = element("p");
    privateStatus.setAttribute("role", "status");
    privateList = element("ul", "", "company-list");
    more = button("Weitere Privatkunden");
    more.hidden = true;
    more.addEventListener("click", () => loadPrivate({ append: true }));
    privateDetail = element("div");
    privatePanel.append(searchForm, privateStatus, privateList, more, privateDetail);
    searchForm.addEventListener("submit", (event) => {
      event.preventDefault();
      query = search.value.trim();
      loadPrivate();
    });
    const show = (nextMode) => {
      mode = nextMode;
      business.setAttribute("aria-pressed", String(mode === "business"));
      privateButton.setAttribute("aria-pressed", String(mode === "private"));
      privatePanel.hidden = mode !== "private";
      onModeChange(mode === "business");
      if (mode === "private") loadPrivate();
    };
    business.addEventListener("click", () => {
      if (mode === "business" || !canLeave()) return;
      privateSequence++;
      privateDraft = undefined;
      privateDetail.replaceChildren();
      show("business");
    });
    privateButton.addEventListener("click", () => {
      if (mode === "private" || !canLeave()) return;
      const lastCompany = companyId;
      if (businessRoot && lastCompany) {
        companyId = undefined;
        selectCompany(businessRoot, lastCompany);
      }
      show("private");
    });
    root.append(switcher, privatePanel);
    show("business");
    return true;
  }

  function openPrivateCreate(trigger) {
    if (!active || mode !== "private") return false;
    if (hasCsrf() && canLeave()) {
      privateSequence++;
      renderEditor(privateDetail, null, trigger);
    }
    return true;
  }

  function leaveWorkspace() {
    if (!canLeave()) return false;
    privateSequence++;
    privateDraft = undefined;
    privateDetail?.replaceChildren();
    if (businessRoot && companyId) {
      const selected = companyId;
      companyId = undefined;
      selectCompany(businessRoot, selected);
    }
    return true;
  }

  function selectCompany(anchor, id) {
    if (!active || !anchor || (companyId === id && businessRoot === anchor)) return;
    businessRoot?.replaceChildren();
    companyDraft = undefined;
    companyId = id;
    businessRoot = anchor;
    if (!id) return;
    const panel = element("details");
    panel.append(element("summary", "Anschrift und USt-IdNr."));
    const content = element("div");
    panel.append(content);
    anchor.append(panel);
    const current = generation;
    let loading = false;
    panel.addEventListener("toggle", async () => {
      if (!panel.open || content.querySelector("form") || loading) return;
      loading = true;
      content.textContent = "Zusatzdaten werden geladen …";
      try {
        const record = await fetchResult(`/companies/${encodeURIComponent(id)}/details`, {},
          "Die Zusatzdaten konnten nicht geladen werden. Öffnen Sie den Bereich erneut.");
        if (record && current === generation && panel.isConnected) {
          renderEditor(content, record, panel, { business: true });
        }
      } catch (error) {
        if (current === generation && panel.isConnected) content.textContent = error.message;
      } finally {
        loading = false;
      }
    });
  }

  return { mount, reset, selectCompany, openPrivateCreate, canLeave, leaveWorkspace };
}
