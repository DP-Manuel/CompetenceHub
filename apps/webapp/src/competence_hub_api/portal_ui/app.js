const API = {
  session: "/api/v1/auth/session",
  sessionCsrf: "/api/v1/auth/session/csrf",
  login: "/api/v1/auth/login",
  totpVerify: "/api/v1/auth/mfa/totp/verify",
  recoveryVerify: "/api/v1/auth/mfa/recovery/verify",
  enrollment: "/api/v1/auth/mfa/totp/enrollment",
  enrollmentConfirm: "/api/v1/auth/mfa/totp/enrollment/confirm",
  companies: "/api/v1/portal/companies",
};

const state = {
  challengeCsrf: null,
  sessionCsrf: null,
  session: null,
  companies: [],
  selectedCompany: null,
  submitting: new Set(),
};

const views = {
  login: document.querySelector("#login-view"),
  mfa: document.querySelector("#mfa-view"),
  enrollment: document.querySelector("#enrollment-view"),
  recovery: document.querySelector("#recovery-view"),
  portal: document.querySelector("#portal-view"),
};

function byId(id) {
  return document.getElementById(id);
}

function showView(name) {
  Object.entries(views).forEach(([viewName, element]) => {
    element.hidden = viewName !== name;
  });
  const heading = views[name].querySelector("h1");
  if (heading) {
    heading.setAttribute("tabindex", "-1");
    heading.focus();
  }
}

function setError(id, message = "") {
  const element = byId(id);
  element.textContent = message;
  element.hidden = !message;
  if (message) {
    element.focus?.();
  }
}

function clearPortalWorkflowErrors() {
  ["create-company-error", "edit-company-error", "add-contact-error"].forEach((id) => {
    setError(id);
  });
  document.querySelectorAll(".contact-edit-form .form-error").forEach((error) => {
    error.textContent = "";
    error.hidden = true;
  });
}

let statusTimer = null;

function announce(message) {
  const status = byId("status-message");
  status.textContent = message;
  status.hidden = false;
  window.clearTimeout(statusTimer);
  statusTimer = window.setTimeout(() => {
    status.hidden = true;
    status.textContent = "";
  }, 4500);
}

function normalizeOptional(value) {
  const normalized = String(value ?? "").trim();
  return normalized || null;
}

function setBusy(form, busy) {
  const key = form.id;
  if (busy) {
    if (state.submitting.has(key)) {
      return false;
    }
    state.submitting.add(key);
  } else {
    state.submitting.delete(key);
  }
  form.querySelectorAll("button, input, textarea").forEach((control) => {
    control.disabled = busy;
  });
  form.setAttribute("aria-busy", String(busy));
  return true;
}

function beginFormSubmission(form) {
  if (!form.reportValidity()) {
    return null;
  }
  const data = new FormData(form);
  return setBusy(form, true) ? data : null;
}

async function problemMessage(response, fallback) {
  try {
    const body = await response.json();
    const messages = {
      authentication_failed: "Die Anmeldung ist nicht mehr gültig.",
      authentication_unavailable: "Die Anmeldung ist derzeit nicht verfügbar.",
      authorization_failed: "Für diese Aktion fehlt die Berechtigung.",
      request_verification_failed: "Die sichere Anfrage konnte nicht bestätigt werden.",
      invalid_request: "Bitte prüfen Sie die eingegebenen Daten.",
      rate_limit_exceeded: "Zu viele Versuche. Bitte warten Sie einen Moment.",
      company_record_not_found: "Der Datensatz wurde nicht gefunden.",
      portal_unavailable: "Das Portal ist derzeit nicht verfügbar.",
    };
    return messages[body.code] || body.title || fallback;
  } catch {
    return fallback;
  }
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  if (options.csrf === "challenge" && state.challengeCsrf) {
    headers.set("X-CSRF-Token", state.challengeCsrf);
  }
  if (options.csrf === "session" && state.sessionCsrf) {
    headers.set("X-CSRF-Token", state.sessionCsrf);
  }
  return fetch(path, {
    method: options.method || "GET",
    credentials: "same-origin",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
}

function showLogin(message = "") {
  state.challengeCsrf = null;
  byId("session-summary").hidden = true;
  setError("login-error", message);
  showView("login");
  byId("login-email").focus();
}

async function restoreSession() {
  let response;
  try {
    response = await request(API.session);
  } catch {
    showLogin("Das Portal ist momentan nicht erreichbar.");
    return;
  }
  if (!response.ok) {
    showLogin();
    return;
  }
  state.session = await response.json();
  try {
    const csrfResponse = await request(API.sessionCsrf, { method: "POST" });
    state.sessionCsrf = csrfResponse.ok
      ? csrfResponse.headers.get("X-CSRF-Token")
      : null;
  } catch {
    state.sessionCsrf = null;
  }
  await enterPortal();
}

async function refreshSessionAfterMfa(response) {
  state.sessionCsrf = response.headers.get("X-CSRF-Token");
  const sessionResponse = await request(API.session);
  if (!sessionResponse.ok) {
    showLogin(await problemMessage(sessionResponse, "Die Sitzung konnte nicht geladen werden."));
    return false;
  }
  state.session = await sessionResponse.json();
  if (!state.sessionCsrf) {
    try {
      const csrfResponse = await request(API.sessionCsrf, { method: "POST" });
      state.sessionCsrf = csrfResponse.ok
        ? csrfResponse.headers.get("X-CSRF-Token")
        : null;
    } catch {
      state.sessionCsrf = null;
    }
  }
  return true;
}

async function enterPortal() {
  if (!state.session) {
    showLogin();
    return;
  }
  byId("session-user").textContent = state.session.user.display_name;
  byId("session-summary").hidden = false;
  clearPortalWorkflowErrors();
  applyMutationAvailability();
  showView("portal");
  await loadCompanies();
}

function applyMutationAvailability() {
  const canMutate = Boolean(state.sessionCsrf);
  byId("reauth-notice").hidden = canMutate;
  document.querySelectorAll(".mutation-control").forEach((control) => {
    control.disabled = !canMutate;
  });
  byId("logout-button").textContent = canMutate ? "Abmelden" : "Erneut anmelden";
}

async function handleLogin(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("login-error");
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  try {
    const response = await request(API.login, {
      method: "POST",
      body: {
        email: data.get("email"),
        password: data.get("password"),
      },
    });
    if (!response.ok) {
      setError("login-error", await problemMessage(response, "Anmeldung nicht möglich."));
      return;
    }
    const body = await response.json();
    state.challengeCsrf = body.csrf_token;
    form.reset();
    if (body.state === "mfa_enrollment_required") {
      await beginEnrollment();
      return;
    }
    showView("mfa");
    byId("mfa-code").focus();
  } catch {
    setError("login-error", "Das Portal ist momentan nicht erreichbar.");
  } finally {
    setBusy(form, false);
  }
}

async function beginEnrollment() {
  const response = await request(API.enrollment, {
    method: "POST",
    csrf: "challenge",
  });
  if (!response.ok) {
    showLogin(await problemMessage(response, "MFA konnte nicht eingerichtet werden."));
    return;
  }
  const body = await response.json();
  let secret = body.provisioning_uri;
  try {
    secret = new URL(body.provisioning_uri).searchParams.get("secret") || secret;
  } catch {
    // Keep the server value visible if a future non-URI enrollment format is used.
  }
  byId("provisioning-secret").textContent = secret;
  showView("enrollment");
  byId("enrollment-code").focus();
}

async function handleMfa(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("mfa-error");
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  const method = data.get("mfa-method");
  const endpoint = method === "recovery" ? API.recoveryVerify : API.totpVerify;
  try {
    const response = await request(endpoint, {
      method: "POST",
      csrf: "challenge",
      body: { code: String(data.get("code") || "").trim() },
    });
    if (!response.ok) {
      setError("mfa-error", await problemMessage(response, "Code konnte nicht bestätigt werden."));
      return;
    }
    form.reset();
    state.challengeCsrf = null;
    if (await refreshSessionAfterMfa(response)) {
      await enterPortal();
    }
  } catch {
    setError("mfa-error", "Das Portal ist momentan nicht erreichbar.");
  } finally {
    setBusy(form, false);
  }
}

async function handleEnrollmentConfirmation(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("enrollment-error");
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  try {
    const response = await request(API.enrollmentConfirm, {
      method: "POST",
      csrf: "challenge",
      body: { code: String(data.get("code") || "").trim() },
    });
    if (!response.ok) {
      setError(
        "enrollment-error",
        await problemMessage(response, "Code konnte nicht bestätigt werden."),
      );
      return;
    }
    const body = await response.json();
    state.challengeCsrf = null;
    if (!(await refreshSessionAfterMfa(response))) {
      return;
    }
    renderRecoveryCodes(body.recovery_codes || []);
    showView("recovery");
  } catch {
    setError("enrollment-error", "Das Portal ist momentan nicht erreichbar.");
  } finally {
    setBusy(form, false);
  }
}

function renderRecoveryCodes(codes) {
  const list = byId("recovery-codes");
  list.replaceChildren();
  codes.forEach((code) => {
    const item = document.createElement("li");
    item.textContent = code;
    list.append(item);
  });
  byId("recovery-confirmed").checked = false;
  byId("enter-portal").disabled = true;
}

async function copyText(text, successMessage) {
  try {
    await navigator.clipboard.writeText(text);
    announce(successMessage);
  } catch {
    announce("Kopieren nicht möglich. Bitte markieren Sie den Text manuell.");
  }
}

async function loadCompanies(query = "") {
  byId("company-empty").hidden = true;
  const parameters = new URLSearchParams({ limit: "50" });
  if (query.trim()) {
    parameters.set("query", query.trim());
  }
  try {
    const response = await request(`${API.companies}?${parameters}`);
    if (response.status === 401) {
      showLogin("Die Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.");
      return;
    }
    if (!response.ok) {
      announce(await problemMessage(response, "Firmen konnten nicht geladen werden."));
      return;
    }
    const body = await response.json();
    state.companies = body.items || [];
    renderCompanies();
  } catch {
    announce("Firmen konnten nicht geladen werden.");
  }
}

function renderCompanies() {
  const list = byId("company-list");
  list.replaceChildren();
  byId("company-count").textContent = `${state.companies.length} Einträge`;
  byId("company-empty").hidden = state.companies.length !== 0;
  state.companies.forEach((company) => {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.companyId = company.id;
    button.setAttribute(
      "aria-current",
      String(state.selectedCompany?.id === company.id),
    );

    const name = document.createElement("strong");
    name.textContent = company.name;
    const industry = document.createElement("small");
    industry.textContent = company.industry || "Branche nicht erfasst";
    const status = document.createElement("span");
    status.className = "status-label";
    status.textContent = company.status === "prospect" ? "Interessent" : company.status;

    button.append(name, industry, status);
    item.append(button);
    list.append(item);
  });
}

async function selectCompany(companyId) {
  try {
    const response = await request(`${API.companies}/${companyId}`);
    if (response.status === 401) {
      showLogin("Die Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.");
      return;
    }
    if (!response.ok) {
      announce(await problemMessage(response, "Firma konnte nicht geladen werden."));
      return;
    }
    state.selectedCompany = await response.json();
    renderCompanies();
    renderCompanyDetail();
  } catch {
    announce("Firma konnte nicht geladen werden.");
  }
}

function renderCompanyDetail() {
  const company = state.selectedCompany;
  if (!company) {
    byId("detail-placeholder").hidden = false;
    byId("detail-content").hidden = true;
    return;
  }
  byId("detail-placeholder").hidden = true;
  byId("detail-content").hidden = false;
  byId("detail-company-name").textContent = company.name;
  byId("detail-company-meta").textContent = company.industry || "Branche nicht erfasst";
  byId("detail-company-notes").textContent = company.internal_notes || "Keine interne Notiz.";
  byId("edit-company-name").value = company.name;
  byId("edit-company-industry").value = company.industry || "";
  byId("edit-company-notes").value = company.internal_notes || "";
  setError("edit-company-error");
  byId("edit-company-form").hidden = true;
  byId("edit-company-button").hidden = false;
  renderContacts(company.contacts || []);
  applyMutationAvailability();
}

function createContactField(contact, fieldName, labelText, type = "text") {
  const wrapper = document.createElement("div");
  wrapper.className = "field";
  const id = `contact-${contact.id}-${fieldName}`;
  const label = document.createElement("label");
  label.htmlFor = id;
  label.textContent = labelText;
  const input = document.createElement("input");
  input.id = id;
  input.name = fieldName;
  input.type = type;
  input.value = contact[fieldName] || "";
  input.maxLength = fieldName === "email"
    ? 254
    : fieldName === "job_function"
      ? 200
      : fieldName === "phone"
        ? 50
        : 100;
  if (["first_name", "last_name", "email"].includes(fieldName)) {
    input.required = true;
  }
  wrapper.append(label, input);
  return wrapper;
}

function renderContacts(contacts) {
  const list = byId("contact-list");
  list.replaceChildren();
  contacts.forEach((contact) => {
    const item = document.createElement("li");
    const name = document.createElement("strong");
    name.textContent = `${contact.first_name} ${contact.last_name}`;
    const email = document.createElement("a");
    email.href = `mailto:${contact.email}`;
    email.textContent = contact.email;
    const detail = document.createElement("span");
    detail.textContent = [contact.job_function, contact.phone].filter(Boolean).join(" | ") || "Keine weiteren Angaben";
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "button button-quiet mutation-control";
    editButton.textContent = "Kontakt bearbeiten";

    const form = document.createElement("form");
    form.className = "contact-edit-form";
    form.hidden = true;
    form.dataset.contactId = contact.id;
    form.append(
      createContactField(contact, "first_name", "Vorname"),
      createContactField(contact, "last_name", "Nachname"),
      createContactField(contact, "email", "E-Mail", "email"),
      createContactField(contact, "phone", "Telefon", "tel"),
      createContactField(contact, "job_function", "Funktion"),
    );
    const error = document.createElement("p");
    error.className = "form-error";
    error.setAttribute("role", "alert");
    error.hidden = true;
    const actions = document.createElement("div");
    actions.className = "button-row";
    const save = document.createElement("button");
    save.type = "submit";
    save.className = "button button-primary mutation-control";
    save.textContent = "Kontakt speichern";
    const cancel = document.createElement("button");
    cancel.type = "button";
    cancel.className = "button button-secondary";
    cancel.textContent = "Abbrechen";
    cancel.addEventListener("click", () => {
      form.hidden = true;
      editButton.hidden = false;
      editButton.focus();
    });
    actions.append(save, cancel);
    form.append(error, actions);
    form.addEventListener("submit", (event) => handleContactUpdate(event, error));
    editButton.addEventListener("click", () => {
      form.hidden = false;
      editButton.hidden = true;
      form.querySelector("input").focus();
    });

    item.append(name, email, detail, editButton, form);
    list.append(item);
  });
}

async function handleCreateCompany(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("create-company-error");
  if (!state.sessionCsrf) {
    setError("create-company-error", "Bitte melden Sie sich für Änderungen erneut an.");
    return;
  }
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  const payload = {
    name: data.get("name"),
    industry: normalizeOptional(data.get("industry")),
    internal_notes: normalizeOptional(data.get("internal_notes")),
    initial_contact: {
      first_name: data.get("first_name"),
      last_name: data.get("last_name"),
      email: data.get("email"),
      phone: normalizeOptional(data.get("phone")),
      job_function: normalizeOptional(data.get("job_function")),
    },
  };
  try {
    const response = await request(API.companies, {
      method: "POST",
      csrf: "session",
      body: payload,
    });
    if (!response.ok) {
      setError("create-company-error", await problemMessage(response, "Firma konnte nicht angelegt werden."));
      return;
    }
    state.selectedCompany = await response.json();
    form.reset();
    byId("company-dialog").close();
    await loadCompanies();
    renderCompanyDetail();
    announce("Firma wurde angelegt.");
  } catch {
    setError("create-company-error", "Firma konnte nicht angelegt werden.");
  } finally {
    setBusy(form, false);
  }
}

async function handleCompanyUpdate(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("edit-company-error");
  if (!state.selectedCompany || !state.sessionCsrf) {
    setError("edit-company-error", "Bitte melden Sie sich für Änderungen erneut an.");
    return;
  }
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  try {
    const response = await request(`${API.companies}/${state.selectedCompany.id}`, {
      method: "PATCH",
      csrf: "session",
      body: {
        name: data.get("name"),
        industry: normalizeOptional(data.get("industry")),
        internal_notes: normalizeOptional(data.get("internal_notes")),
      },
    });
    if (!response.ok) {
      setError("edit-company-error", await problemMessage(response, "Firma konnte nicht aktualisiert werden."));
      return;
    }
    await selectCompany(state.selectedCompany.id);
    await loadCompanies(byId("company-search").value);
    announce("Firma wurde aktualisiert.");
  } catch {
    setError("edit-company-error", "Firma konnte nicht aktualisiert werden.");
  } finally {
    setBusy(form, false);
  }
}

async function handleAddContact(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("add-contact-error");
  if (!state.selectedCompany || !state.sessionCsrf) {
    setError("add-contact-error", "Bitte melden Sie sich für Änderungen erneut an.");
    return;
  }
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  try {
    const response = await request(
      `${API.companies}/${state.selectedCompany.id}/contacts`,
      {
        method: "POST",
        csrf: "session",
        body: {
          first_name: data.get("first_name"),
          last_name: data.get("last_name"),
          email: data.get("email"),
          phone: normalizeOptional(data.get("phone")),
          job_function: normalizeOptional(data.get("job_function")),
        },
      },
    );
    if (!response.ok) {
      setError("add-contact-error", await problemMessage(response, "Kontakt konnte nicht gespeichert werden."));
      return;
    }
    form.reset();
    byId("contact-dialog").close();
    await selectCompany(state.selectedCompany.id);
    announce("Kontakt wurde hinzugefügt.");
  } catch {
    setError("add-contact-error", "Kontakt konnte nicht gespeichert werden.");
  } finally {
    setBusy(form, false);
  }
}

async function handleContactUpdate(event, errorElement) {
  event.preventDefault();
  const form = event.currentTarget;
  errorElement.hidden = true;
  if (!state.selectedCompany || !state.sessionCsrf) {
    errorElement.textContent = "Bitte melden Sie sich für Änderungen erneut an.";
    errorElement.hidden = false;
    return;
  }
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  try {
    const response = await request(
      `${API.companies}/${state.selectedCompany.id}/contacts/${form.dataset.contactId}`,
      {
        method: "PATCH",
        csrf: "session",
        body: {
          first_name: data.get("first_name"),
          last_name: data.get("last_name"),
          email: data.get("email"),
          phone: normalizeOptional(data.get("phone")),
          job_function: normalizeOptional(data.get("job_function")),
        },
      },
    );
    if (!response.ok) {
      errorElement.textContent = await problemMessage(response, "Kontakt konnte nicht aktualisiert werden.");
      errorElement.hidden = false;
      return;
    }
    await selectCompany(state.selectedCompany.id);
    announce("Kontakt wurde aktualisiert.");
  } catch {
    errorElement.textContent = "Kontakt konnte nicht aktualisiert werden.";
    errorElement.hidden = false;
  } finally {
    setBusy(form, false);
  }
}

async function handleLogout() {
  if (!state.sessionCsrf) {
    showLogin("Bitte melden Sie sich erneut an, um die bestehende Sitzung sicher zu ersetzen.");
    return;
  }
  try {
    const response = await request(API.session, {
      method: "DELETE",
      csrf: "session",
    });
    if (!response.ok) {
      announce(await problemMessage(response, "Abmeldung nicht möglich."));
      return;
    }
  } catch {
    announce("Abmeldung nicht möglich.");
    return;
  }
  state.session = null;
  state.sessionCsrf = null;
  state.companies = [];
  state.selectedCompany = null;
  showLogin("Sie wurden abgemeldet.");
}

function bindEvents() {
  byId("login-form").addEventListener("submit", handleLogin);
  byId("mfa-form").addEventListener("submit", handleMfa);
  byId("enrollment-form").addEventListener("submit", handleEnrollmentConfirmation);
  byId("create-company-form").addEventListener("submit", handleCreateCompany);
  byId("edit-company-form").addEventListener("submit", handleCompanyUpdate);
  byId("add-contact-form").addEventListener("submit", handleAddContact);
  byId("logout-button").addEventListener("click", handleLogout);
  byId("reauth-button").addEventListener("click", () => showLogin());

  byId("show-password").addEventListener("change", (event) => {
    byId("login-password").type = event.currentTarget.checked ? "text" : "password";
  });

  document.querySelectorAll("[data-action='restart-login']").forEach((button) => {
    button.addEventListener("click", () => showLogin());
  });

  document.querySelectorAll("input[name='mfa-method']").forEach((input) => {
    input.addEventListener("change", (event) => {
      const recovery = event.currentTarget.value === "recovery";
      byId("mfa-code-label").textContent = recovery ? "Recovery-Code" : "Sechsstelliger Code";
      byId("mfa-code").inputMode = recovery ? "text" : "numeric";
      byId("mfa-code").value = "";
      byId("mfa-code").focus();
    });
  });

  byId("copy-provisioning").addEventListener("click", () => {
    copyText(byId("provisioning-secret").textContent, "Einrichtungsschlüssel wurde kopiert.");
  });
  byId("copy-recovery").addEventListener("click", () => {
    const codes = [...byId("recovery-codes").querySelectorAll("li")]
      .map((item) => item.textContent)
      .join("\n");
    copyText(codes, "Recovery-Codes wurden kopiert.");
  });
  byId("recovery-confirmed").addEventListener("change", (event) => {
    byId("enter-portal").disabled = !event.currentTarget.checked;
  });
  byId("enter-portal").addEventListener("click", enterPortal);

  byId("company-search-form").addEventListener("submit", (event) => {
    event.preventDefault();
    loadCompanies(byId("company-search").value);
  });
  byId("company-list").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-company-id]");
    if (button) {
      selectCompany(button.dataset.companyId);
    }
  });

  byId("open-company-dialog").addEventListener("click", () => {
    if (state.sessionCsrf) {
      byId("company-dialog").showModal();
      byId("create-company-name").focus();
    }
  });
  byId("open-contact-dialog").addEventListener("click", () => {
    if (state.sessionCsrf && state.selectedCompany) {
      byId("contact-dialog").showModal();
      byId("add-contact-first-name").focus();
    }
  });
  document.querySelectorAll("[data-dialog-close]").forEach((button) => {
    button.addEventListener("click", () => {
      byId(button.dataset.dialogClose).close();
    });
  });

  byId("edit-company-button").addEventListener("click", () => {
    byId("edit-company-form").hidden = false;
    byId("edit-company-button").hidden = true;
    byId("edit-company-name").focus();
  });
  byId("cancel-company-edit").addEventListener("click", () => {
    renderCompanyDetail();
    byId("edit-company-button").focus();
  });

  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        dialog.close();
      }
    });
  });
}

bindEvents();
restoreSession();
