const API = {
  session: "/api/v1/auth/session",
  sessionCsrf: "/api/v1/auth/session/csrf",
  login: "/api/v1/auth/login",
  totpVerify: "/api/v1/auth/mfa/totp/verify",
  recoveryVerify: "/api/v1/auth/mfa/recovery/verify",
  enrollment: "/api/v1/auth/mfa/totp/enrollment",
  enrollmentConfirm: "/api/v1/auth/mfa/totp/enrollment/confirm",
  passwordResetRequest: "/api/v1/auth/password-reset/request",
  passwordResetConfirm: "/api/v1/auth/password-reset/confirm",
  invitationAccept: "/api/v1/auth/invitations/accept",
  adminInvitations: "/api/v1/admin/users/invitations",
  companies: "/api/v1/portal/companies",
  calendarCapabilities: "/api/v1/portal/calendar/capabilities",
  calendarTopics: "/api/v1/portal/calendar/topics",
  calendarOffers: "/api/v1/portal/calendar/offers",
  calendarReviewQueue: "/api/v1/portal/calendar/review-queue",
};

const state = {
  challengeCsrf: null,
  sessionCsrf: null,
  session: null,
  companies: [],
  selectedCompany: null,
  calendarCapabilities: null,
  calendarTopics: [],
  coachOffers: [],
  reviewOffers: [],
  selectedCalendarOffer: null,
  selectedReviewOffer: null,
  activePortalArea: null,
  accountAction: null,
  pendingInvitation: null,
  submitting: new Set(),
};

const views = {
  login: document.querySelector("#login-view"),
  passwordResetRequest: document.querySelector("#password-reset-request-view"),
  accountToken: document.querySelector("#account-token-view"),
  mfa: document.querySelector("#mfa-view"),
  enrollment: document.querySelector("#enrollment-view"),
  recovery: document.querySelector("#recovery-view"),
  portal: document.querySelector("#portal-view"),
};

const restrictedCalendarNodes = {
  coachWorkspace: document.querySelector("#coach-calendar-workspace"),
  reviewWorkspace: document.querySelector("#review-calendar-workspace"),
  offerDialog: document.querySelector("#calendar-offer-dialog"),
  reviewDialog: document.querySelector("#calendar-review-dialog"),
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

function setErrorElement(element, message = "") {
  if (!element) {
    return;
  }
  element.textContent = message;
  element.hidden = !message;
  if (message) {
    element.focus?.();
  }
}

function setError(id, message = "") {
  setErrorElement(byId(id), message);
}

function clearPortalWorkflowErrors() {
  [
    "create-company-error",
    "edit-company-error",
    "add-contact-error",
    "coach-calendar-error",
    "review-calendar-error",
    "calendar-offer-error",
    "calendar-review-error",
  ].forEach((id) => {
    setError(id);
  });
  Object.values(restrictedCalendarNodes).forEach((node) => {
    node.querySelectorAll(".form-error").forEach((error) => {
      setErrorElement(error);
    });
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
      request_not_accepted: "Der Link ist ungültig oder abgelaufen.",
      idempotency_conflict: "Die Einladung steht im Konflikt mit einer vorherigen Anfrage.",
      account_conflict: "Für diese E-Mail kann derzeit keine Einladung erstellt werden.",
      company_record_not_found: "Der Datensatz wurde nicht gefunden.",
      portal_unavailable: "Das Portal ist derzeit nicht verfügbar.",
      calendar_offer_not_found: "Das Angebot wurde nicht gefunden.",
      calendar_version_conflict: "Der Datenstand wurde zwischenzeitlich geändert.",
      calendar_time_conflict: "Der Zeitraum überschneidet sich mit einem anderen Angebot.",
      calendar_transition_conflict: "Diese Aktion passt nicht mehr zum aktuellen Status.",
      calendar_idempotency_conflict: "Dieser Entwurf steht im Konflikt mit einer früheren Anfrage.",
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
  clearPortalClientState();
  state.session = null;
  state.sessionCsrf = null;
  state.challengeCsrf = null;
  state.accountAction = null;
  byId("session-summary").hidden = true;
  setError("login-error", message);
  showView("login");
  byId("login-email").focus();
}

function clearPortalClientState() {
  state.companies = [];
  state.selectedCompany = null;
  state.calendarCapabilities = null;
  state.calendarTopics = [];
  state.coachOffers = [];
  state.reviewOffers = [];
  state.selectedCalendarOffer = null;
  state.selectedReviewOffer = null;
  state.activePortalArea = null;
  byId("company-list")?.replaceChildren();
  restrictedCalendarNodes.coachWorkspace
    .querySelector("#coach-calendar-list")
    ?.replaceChildren();
  restrictedCalendarNodes.reviewWorkspace
    .querySelector("#review-calendar-list")
    ?.replaceChildren();
  [restrictedCalendarNodes.offerDialog, restrictedCalendarNodes.reviewDialog]
    .forEach((dialog) => {
      if (dialog.open) {
        dialog.close();
      }
    });
  configureRestrictedCalendarNodes(false, false);
}

function showPasswordResetRequest() {
  setError("password-reset-request-error");
  byId("password-reset-request-status").hidden = true;
  showView("passwordResetRequest");
  byId("password-reset-email").focus();
}

function consumeAccountActionFromFragment() {
  const fragment = window.location.hash;
  const match = /^#\/(einladung|passwort-zuruecksetzen)\?(.+)$/.exec(fragment);
  if (!match) {
    return false;
  }
  const token = new URLSearchParams(match[2]).get("token") || "";
  window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}`);
  if (!token || token.length > 128) {
    showLogin("Der Link ist ungültig oder unvollständig.");
    return true;
  }
  const purpose = match[1] === "einladung" ? "invitation" : "password_reset";
  state.accountAction = { purpose, token };
  const invitation = purpose === "invitation";
  byId("account-token-eyebrow").textContent = invitation
    ? "Einladung annehmen"
    : "Passwort zurücksetzen";
  byId("account-token-title").textContent = invitation
    ? "Zugang einrichten"
    : "Neues Passwort festlegen";
  byId("account-token-description").textContent = invitation
    ? "Legen Sie Ihr persönliches Passwort fest. Anschließend richten Sie den zweiten Faktor ein."
    : "Legen Sie ein neues persönliches Passwort fest. Bestehende Sitzungen werden beendet.";
  byId("account-token-submit").textContent = invitation
    ? "Zugang aktivieren"
    : "Passwort speichern";
  showView("accountToken");
  byId("account-token-password").focus();
  return true;
}

async function handlePasswordResetRequest(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("password-reset-request-error");
  byId("password-reset-request-status").hidden = true;
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  try {
    const response = await request(API.passwordResetRequest, {
      method: "POST",
      body: { email: data.get("email") },
    });
    if (!response.ok) {
      setError("password-reset-request-error", await problemMessage(response, "Anfrage nicht möglich."));
      return;
    }
    form.reset();
    const status = byId("password-reset-request-status");
    status.textContent = "Falls ein aktives Konto vorhanden ist, wurde ein Link versendet.";
    status.hidden = false;
  } catch {
    setError("password-reset-request-error", "Das Portal ist momentan nicht erreichbar.");
  } finally {
    setBusy(form, false);
  }
}

async function handleAccountToken(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("account-token-error");
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  const password = String(data.get("password") || "");
  if (password !== data.get("password_confirm")) {
    setError("account-token-error", "Die eingegebenen Passwörter stimmen nicht überein.");
    setBusy(form, false);
    return;
  }
  if (!state.accountAction) {
    setError("account-token-error", "Der Link ist ungültig oder abgelaufen.");
    setBusy(form, false);
    return;
  }
  try {
    const invitation = state.accountAction.purpose === "invitation";
    const response = await request(
      invitation ? API.invitationAccept : API.passwordResetConfirm,
      {
        method: "POST",
        body: { token: state.accountAction.token, password },
      },
    );
    if (!response.ok) {
      setError("account-token-error", await problemMessage(response, "Anfrage nicht möglich."));
      return;
    }
    state.accountAction = null;
    form.reset();
    if (!invitation) {
      showLogin("Das Passwort wurde geändert. Bitte melden Sie sich neu an.");
      return;
    }
    const body = await response.json();
    state.challengeCsrf = body.csrf_token;
    await beginEnrollment();
  } catch {
    setError("account-token-error", "Das Portal ist momentan nicht erreichbar.");
  } finally {
    setBusy(form, false);
  }
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
  await configurePortalAreas();
}

const CALENDAR_STATUS_LABELS = {
  draft: "Entwurf",
  in_review: "Zur Prüfung eingereicht",
  published: "Veröffentlicht",
  changes_requested: "Änderung angefordert",
  superseded: "Durch neuere Fassung ersetzt",
};

const CALENDAR_FORMAT_LABELS = {
  online: "Online",
  praesenz: "Präsenz",
  hybrid: "Hybrid",
};

function calendarStatusLabel(status) {
  return CALENDAR_STATUS_LABELS[status] || "Status nicht verfügbar";
}

function calendarOfferStatusLabel(offer) {
  return offer.lifecycle_status === "withdrawn"
    ? "Zurückgezogen"
    : calendarStatusLabel(offer.workflow_status);
}

function calendarFormatLabel(format) {
  return CALENDAR_FORMAT_LABELS[format] || "Format nicht verfügbar";
}

function formatCalendarDate(value) {
  if (!value) {
    return "Nicht angegeben";
  }
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Europe/Berlin",
  }).format(new Date(value));
}

function toBerlinInputValue(value) {
  if (!value) {
    return "";
  }
  const parts = new Intl.DateTimeFormat("sv-SE", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
    timeZone: "Europe/Berlin",
  }).formatToParts(new Date(value));
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${values.year}-${values.month}-${values.day}T${values.hour}:${values.minute}`;
}

function berlinLocalToIso(value) {
  const guess = new Date(`${value}:00Z`);
  const parts = new Intl.DateTimeFormat("en-CA", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
    timeZone: "Europe/Berlin",
  }).formatToParts(guess);
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  const represented = Date.UTC(
    Number(values.year),
    Number(values.month) - 1,
    Number(values.day),
    Number(values.hour),
    Number(values.minute),
    Number(values.second),
  );
  return new Date(guess.getTime() - (represented - guess.getTime())).toISOString();
}

async function loadCalendarCapabilities() {
  try {
    const response = await request(API.calendarCapabilities);
    if (response.status === 401) {
      showLogin("Die Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.");
      return null;
    }
    if (response.status === 403 || response.status === 503) {
      return null;
    }
    if (!response.ok) {
      return null;
    }
    return response.json();
  } catch {
    return null;
  }
}

async function configurePortalAreas() {
  const roles = new Set(state.session.user.roles || []);
  const canUseCompanies = roles.has("admin") || roles.has("internal");
  state.calendarCapabilities = await loadCalendarCapabilities();
  const canManageCalendar = Boolean(
    state.calendarCapabilities?.can_manage_own_offers
    || state.calendarCapabilities?.can_administer_offers,
  );
  const canReviewCalendar = Boolean(state.calendarCapabilities?.can_review_offers);
  configureRestrictedCalendarNodes(canManageCalendar, canReviewCalendar);
  applyMutationAvailability();
  const areas = [];
  if (canUseCompanies) {
    areas.push({ id: "companies", label: "Firmen" });
  }
  if (canManageCalendar) {
    areas.push({ id: "coach-calendar", label: "Kalenderangebote" });
  }
  if (canReviewCalendar) {
    areas.push({ id: "review-calendar", label: "Prüfliste" });
  }
  renderPortalNavigation(areas);
  byId("portal-empty").hidden = areas.length !== 0;
  if (areas.length === 0) {
    state.activePortalArea = null;
    switchPortalWorkspace(null);
    return;
  }
  const selected = areas.some((area) => area.id === state.activePortalArea)
    ? state.activePortalArea
    : areas[0].id;
  await selectPortalArea(selected);
}

function configureRestrictedCalendarNodes(canManage, canReview) {
  const portal = views.portal;
  if (canManage) {
    if (!restrictedCalendarNodes.coachWorkspace.isConnected) {
      portal.append(restrictedCalendarNodes.coachWorkspace);
    }
    if (!restrictedCalendarNodes.offerDialog.isConnected) {
      document.body.append(restrictedCalendarNodes.offerDialog);
    }
  } else {
    restrictedCalendarNodes.coachWorkspace.remove();
    restrictedCalendarNodes.offerDialog.remove();
  }
  if (canReview) {
    if (!restrictedCalendarNodes.reviewWorkspace.isConnected) {
      portal.append(restrictedCalendarNodes.reviewWorkspace);
    }
    if (!restrictedCalendarNodes.reviewDialog.isConnected) {
      document.body.append(restrictedCalendarNodes.reviewDialog);
    }
  } else {
    restrictedCalendarNodes.reviewWorkspace.remove();
    restrictedCalendarNodes.reviewDialog.remove();
  }
}

function renderPortalNavigation(areas) {
  const navigation = byId("portal-navigation");
  navigation.replaceChildren();
  navigation.hidden = areas.length < 2;
  areas.forEach((area) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = area.label;
    button.setAttribute("aria-current", area.id === state.activePortalArea ? "page" : "false");
    button.addEventListener("click", () => selectPortalArea(area.id));
    navigation.append(button);
  });
}

function switchPortalWorkspace(area) {
  byId("company-workspace").hidden = area !== "companies";
  restrictedCalendarNodes.coachWorkspace.hidden = area !== "coach-calendar";
  restrictedCalendarNodes.reviewWorkspace.hidden = area !== "review-calendar";
}

async function selectPortalArea(area) {
  state.activePortalArea = area;
  switchPortalWorkspace(area);
  const selectedLabel = area === "companies"
    ? "Firmen"
    : area === "coach-calendar"
      ? "Kalenderangebote"
      : "Prüfliste";
  [...byId("portal-navigation").querySelectorAll("button")].forEach((button) => {
    button.setAttribute("aria-current", button.textContent === selectedLabel ? "page" : "false");
  });
  byId("admin-invitation-panel").hidden = !(
    area === "companies" && state.session.user.roles.includes("admin")
  );
  if (area === "companies") {
    await loadCompanies();
  } else if (area === "coach-calendar") {
    await loadCalendarTopics();
    await loadCoachOffers();
  } else if (area === "review-calendar") {
    await loadReviewQueue();
  }
}

async function loadCalendarTopics() {
  try {
    const response = await request(API.calendarTopics);
    if (!response.ok) {
      state.calendarTopics = [];
      renderCalendarTopicOptions();
      return;
    }
    state.calendarTopics = (await response.json()).items || [];
    renderCalendarTopicOptions();
  } catch {
    state.calendarTopics = [];
    renderCalendarTopicOptions();
  }
}

function renderCalendarTopicOptions(selected = "") {
  const select = byId("calendar-topic");
  select.replaceChildren();
  const prompt = document.createElement("option");
  prompt.value = "";
  prompt.textContent = state.calendarTopics.length
    ? "Thema auswählen"
    : "Kein freigegebenes Thema vorhanden";
  select.append(prompt);
  state.calendarTopics.forEach((topic) => {
    const option = document.createElement("option");
    option.value = topic.id;
    option.textContent = topic.name;
    select.append(option);
  });
  select.value = String(selected || "");
  const canCreate = Boolean(
    state.calendarCapabilities?.can_manage_own_offers && state.calendarTopics.length,
  );
  byId("open-calendar-offer-dialog").hidden = !state.calendarCapabilities?.can_manage_own_offers;
  byId("open-calendar-offer-dialog").disabled = !canCreate || !state.sessionCsrf;
}

async function loadCoachOffers() {
  byId("coach-calendar-loading").hidden = false;
  byId("coach-calendar-empty").hidden = true;
  setError("coach-calendar-error");
  try {
    const response = await request(API.calendarOffers);
    if (response.status === 401) {
      showLogin("Die Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.");
      return;
    }
    if (!response.ok) {
      setError("coach-calendar-error", await problemMessage(response, "Angebote konnten nicht geladen werden."));
      return;
    }
    state.coachOffers = (await response.json()).items || [];
    renderCoachOffers();
  } catch {
    setError("coach-calendar-error", "Angebote konnten nicht geladen werden.");
  } finally {
    byId("coach-calendar-loading").hidden = true;
  }
}

function appendDefinition(list, label, value) {
  const term = document.createElement("dt");
  term.textContent = label;
  const description = document.createElement("dd");
  description.textContent = value;
  list.append(term, description);
}

function calendarCard(offer, review = false) {
  const item = document.createElement("li");
  item.className = "calendar-card";
  const heading = document.createElement("div");
  heading.className = "calendar-card-heading";
  const title = document.createElement("h3");
  title.textContent = offer.title;
  const status = document.createElement("span");
  status.className = "calendar-status";
  status.textContent = calendarOfferStatusLabel(offer);
  heading.append(title, status);
  const meta = document.createElement("dl");
  meta.className = "calendar-card-meta";
  if (review) {
    appendDefinition(meta, "Coach", offer.coach_display_name || "Nicht verfügbar");
  }
  appendDefinition(meta, "Thema", offer.topic_name || "Nicht verfügbar");
  appendDefinition(meta, "Beginn", formatCalendarDate(offer.starts_at));
  appendDefinition(meta, "Ende", formatCalendarDate(offer.ends_at));
  const revision = document.createElement("p");
  revision.textContent = `Aktuelle Revision: ${offer.revision_number || 1}`;
  const actions = document.createElement("div");
  actions.className = "calendar-card-actions";
  item.append(heading, meta, revision, actions);
  return { item, actions };
}

function actionButton(label, style, handler) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `button ${style} calendar-mutation-control`;
  button.textContent = label;
  button.disabled = !state.sessionCsrf;
  button.addEventListener("click", handler);
  return button;
}

function renderCoachOffers() {
  const list = byId("coach-calendar-list");
  list.replaceChildren();
  byId("coach-calendar-empty").hidden = state.coachOffers.length !== 0;
  state.coachOffers.forEach((offer, index) => {
    const card = calendarCard(offer);
    const editable = ["draft", "changes_requested", "published"].includes(offer.workflow_status)
      && offer.lifecycle_status === "active";
    if (editable) {
      const label = offer.workflow_status === "draft" ? "Entwurf bearbeiten" : "Neue Revision bearbeiten";
      card.actions.append(actionButton(label, "button-secondary", () => openCalendarOffer(index)));
    }
    if (offer.workflow_status === "draft" && offer.lifecycle_status === "active") {
      card.actions.append(actionButton("Zur Prüfung einreichen", "button-primary", () => submitCalendarOffer(index)));
    }
    if (offer.lifecycle_status === "active") {
      card.actions.append(actionButton("Angebot zurückziehen", "button-quiet", () => withdrawCalendarOffer(index)));
    }
    list.append(card.item);
  });
}

async function fetchCalendarDetail(offer, target) {
  const response = await request(`${API.calendarOffers}/${offer.id}`);
  if (!response.ok) {
    setError(target, await problemMessage(response, "Angebot konnte nicht geladen werden."));
    return null;
  }
  return { detail: await response.json(), etag: response.headers.get("ETag") };
}

function fillCalendarOfferForm(detail = null) {
  const form = byId("calendar-offer-form");
  form.reset();
  setError("calendar-offer-error");
  byId("reload-calendar-offer").hidden = true;
  byId("calendar-review-feedback").hidden = true;
  const draft = detail?.current_revision;
  byId("calendar-offer-dialog-title").textContent = draft ? "Entwurf bearbeiten" : "Entwurf anlegen";
  byId("save-calendar-offer").textContent = draft ? "Entwurf speichern" : "Entwurf anlegen";
  renderCalendarTopicOptions(draft?.topic_id || "");
  if (!draft) {
    return;
  }
  if (detail.review_decision?.outcome === "changes_requested") {
    byId("calendar-review-feedback-text").textContent = detail.review_decision.note
      || "Für dieses Angebot wurden Änderungen angefordert.";
    byId("calendar-review-feedback").hidden = false;
  }
  byId("calendar-title").value = draft.title;
  byId("calendar-summary").value = draft.summary || "";
  byId("calendar-starts-at").value = toBerlinInputValue(draft.starts_at);
  byId("calendar-ends-at").value = toBerlinInputValue(draft.ends_at);
  byId("calendar-time-zone").value = draft.time_zone;
  byId("calendar-format").value = draft.format;
  byId("calendar-location").value = draft.public_location || "";
  byId("calendar-capacity").value = draft.capacity;
  byId("calendar-review-threshold").value = draft.review_threshold;
  byId("calendar-decision-deadline").value = toBerlinInputValue(draft.decision_deadline);
  byId("calendar-price").value = draft.price_display_text;
}

function openNewCalendarOffer() {
  state.selectedCalendarOffer = null;
  fillCalendarOfferForm();
  byId("calendar-offer-dialog").showModal();
  byId("calendar-title").focus();
}

async function openCalendarOffer(index) {
  setError("coach-calendar-error");
  const selected = await fetchCalendarDetail(state.coachOffers[index], "coach-calendar-error");
  if (!selected) {
    return;
  }
  state.selectedCalendarOffer = selected;
  fillCalendarOfferForm(selected.detail);
  byId("calendar-offer-dialog").showModal();
  byId("calendar-title").focus();
}

function calendarDraftPayload(data) {
  return {
    topic_id: data.get("topic_id"),
    title: data.get("title"),
    summary: normalizeOptional(data.get("summary")),
    starts_at: berlinLocalToIso(data.get("starts_at")),
    ends_at: berlinLocalToIso(data.get("ends_at")),
    time_zone: data.get("time_zone"),
    format: data.get("format"),
    public_location: normalizeOptional(data.get("public_location")),
    capacity: Number(data.get("capacity")),
    review_threshold: Number(data.get("review_threshold")),
    decision_deadline: berlinLocalToIso(data.get("decision_deadline")),
    price_display_text: data.get("price_display_text"),
  };
}

function showCalendarConflict(errorId, reloadId) {
  setError(errorId, "Der Datenstand wurde inzwischen geändert. Laden Sie den aktuellen Stand, bevor Sie fortfahren.");
  byId(reloadId).hidden = false;
}

async function handleCalendarOfferSave(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("calendar-offer-error");
  byId("reload-calendar-offer").hidden = true;
  if (!state.sessionCsrf) {
    setError("calendar-offer-error", "Bitte melden Sie sich für Änderungen erneut an.");
    return;
  }
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  const editing = state.selectedCalendarOffer;
  const path = editing
    ? `${API.calendarOffers}/${editing.detail.id}/draft`
    : API.calendarOffers;
  const body = editing
    ? calendarDraftPayload(data)
    : { client_request_id: window.crypto.randomUUID(), draft: calendarDraftPayload(data) };
  const headers = editing?.etag ? { "If-Match": editing.etag } : {};
  try {
    const response = await request(path, {
      method: editing ? "PATCH" : "POST",
      csrf: "session",
      headers,
      body,
    });
    if (response.status === 409) {
      showCalendarConflict("calendar-offer-error", "reload-calendar-offer");
      return;
    }
    if (!response.ok) {
      setError("calendar-offer-error", await problemMessage(response, "Entwurf konnte nicht gespeichert werden."));
      return;
    }
    byId("calendar-offer-dialog").close();
    state.selectedCalendarOffer = null;
    await loadCoachOffers();
    announce("Der Entwurf wurde gespeichert.");
  } catch {
    setError("calendar-offer-error", "Entwurf konnte nicht gespeichert werden.");
  } finally {
    setBusy(form, false);
  }
}

async function versionedCalendarAction(index, action, successMessage) {
  const actionKey = `calendar-${action}-${index}`;
  if (state.submitting.has(actionKey)) {
    return;
  }
  state.submitting.add(actionKey);
  const selected = await fetchCalendarDetail(state.coachOffers[index], "coach-calendar-error");
  if (!selected || !state.sessionCsrf) {
    state.submitting.delete(actionKey);
    return;
  }
  try {
    const response = await request(`${API.calendarOffers}/${selected.detail.id}/${action}`, {
      method: "POST",
      csrf: "session",
      headers: { "If-Match": selected.etag },
    });
    if (response.status === 409) {
      setError("coach-calendar-error", "Der Datenstand wurde inzwischen geändert. Die Liste wurde aktualisiert; bitte prüfen Sie den Status.");
      await loadCoachOffers();
      return;
    }
    if (!response.ok) {
      setError("coach-calendar-error", await problemMessage(response, "Aktion konnte nicht ausgeführt werden."));
      return;
    }
    await loadCoachOffers();
    announce(successMessage);
  } catch {
    setError("coach-calendar-error", "Aktion konnte nicht ausgeführt werden.");
  } finally {
    state.submitting.delete(actionKey);
  }
}

async function submitCalendarOffer(index) {
  await versionedCalendarAction(index, "submit", "Das Angebot wurde zur Prüfung eingereicht.");
}

async function withdrawCalendarOffer(index) {
  await versionedCalendarAction(index, "withdraw", "Das Angebot wurde zurückgezogen.");
}

async function loadReviewQueue() {
  byId("review-calendar-loading").hidden = false;
  byId("review-calendar-empty").hidden = true;
  setError("review-calendar-error");
  try {
    const response = await request(API.calendarReviewQueue);
    if (response.status === 401) {
      showLogin("Die Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.");
      return;
    }
    if (!response.ok) {
      setError("review-calendar-error", await problemMessage(response, "Prüfliste konnte nicht geladen werden."));
      return;
    }
    state.reviewOffers = (await response.json()).items || [];
    renderReviewQueue();
  } catch {
    setError("review-calendar-error", "Prüfliste konnte nicht geladen werden.");
  } finally {
    byId("review-calendar-loading").hidden = true;
  }
}

function renderReviewQueue() {
  const list = byId("review-calendar-list");
  list.replaceChildren();
  byId("review-calendar-empty").hidden = state.reviewOffers.length !== 0;
  state.reviewOffers.forEach((offer, index) => {
    const card = calendarCard(offer, true);
    card.actions.append(actionButton("Angebot prüfen", "button-primary", () => openCalendarReview(index)));
    list.append(card.item);
  });
}

function renderReviewSummary(detail) {
  const summary = byId("calendar-review-summary");
  summary.replaceChildren();
  const revision = detail.current_revision;
  appendDefinition(summary, "Coach", detail.coach_display_name || "Nicht verfügbar");
  appendDefinition(summary, "Thema", revision.topic_name || "Nicht verfügbar");
  appendDefinition(summary, "Titel", revision.title);
  appendDefinition(summary, "Zeitraum", `${formatCalendarDate(revision.starts_at)} bis ${formatCalendarDate(revision.ends_at)}`);
  appendDefinition(summary, "Format", calendarFormatLabel(revision.format));
  appendDefinition(summary, "Ort", revision.public_location || "Nicht angegeben");
  appendDefinition(summary, "Kapazität", String(revision.capacity));
  appendDefinition(summary, "Entscheidungsfrist", formatCalendarDate(revision.decision_deadline));
  appendDefinition(summary, "Preishinweis", revision.price_display_text);
  appendDefinition(summary, "Revision", String(revision.revision_number));
}

async function openCalendarReview(index) {
  setError("review-calendar-error");
  const selected = await fetchCalendarDetail(state.reviewOffers[index], "review-calendar-error");
  if (!selected) {
    return;
  }
  state.selectedReviewOffer = selected;
  byId("calendar-review-form").reset();
  setError("calendar-review-error");
  byId("reload-calendar-review").hidden = true;
  renderReviewSummary(selected.detail);
  byId("calendar-review-dialog").showModal();
  byId("calendar-review-form").querySelector("input[name='outcome']").focus();
}

async function handleCalendarReview(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("calendar-review-error");
  byId("reload-calendar-review").hidden = true;
  if (!state.selectedReviewOffer || !state.sessionCsrf) {
    setError("calendar-review-error", "Bitte laden Sie das Angebot erneut.");
    return;
  }
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  const outcome = data.get("outcome");
  const note = normalizeOptional(data.get("note"));
  if (outcome === "changes_requested" && !note) {
    setBusy(form, false);
    setError("calendar-review-error", "Bitte beschreiben Sie die gewünschte Änderung.");
    byId("calendar-review-note").focus();
    return;
  }
  try {
    const selected = state.selectedReviewOffer;
    const response = await request(
      `${API.calendarOffers}/${selected.detail.id}/review-decisions`,
      {
        method: "POST",
        csrf: "session",
        headers: { "If-Match": selected.etag },
        body: { outcome, note },
      },
    );
    if (response.status === 409) {
      showCalendarConflict("calendar-review-error", "reload-calendar-review");
      return;
    }
    if (!response.ok) {
      setError("calendar-review-error", await problemMessage(response, "Entscheidung konnte nicht gespeichert werden."));
      return;
    }
    byId("calendar-review-dialog").close();
    state.selectedReviewOffer = null;
    await loadReviewQueue();
    announce(outcome === "published" ? "Das Angebot wurde veröffentlicht." : "Die Änderung wurde angefordert.");
  } catch {
    setError("calendar-review-error", "Entscheidung konnte nicht gespeichert werden.");
  } finally {
    setBusy(form, false);
  }
}

async function reloadSelectedCalendarOffer() {
  if (!state.selectedCalendarOffer) {
    return;
  }
  const selected = await fetchCalendarDetail(
    state.selectedCalendarOffer.detail,
    "calendar-offer-error",
  );
  if (selected) {
    state.selectedCalendarOffer = selected;
    fillCalendarOfferForm(selected.detail);
    announce("Der aktuelle Stand wurde geladen.");
  }
}

async function reloadSelectedCalendarReview() {
  if (!state.selectedReviewOffer) {
    return;
  }
  const selected = await fetchCalendarDetail(
    state.selectedReviewOffer.detail,
    "calendar-review-error",
  );
  if (selected) {
    state.selectedReviewOffer = selected;
    byId("calendar-review-form").reset();
    byId("reload-calendar-review").hidden = true;
    setError("calendar-review-error");
    renderReviewSummary(selected.detail);
    announce("Der aktuelle Stand wurde geladen.");
  }
}

async function handleAdminInvitation(event) {
  event.preventDefault();
  const form = event.currentTarget;
  setError("admin-invitation-error");
  if (!state.sessionCsrf) {
    setError("admin-invitation-error", "Bitte melden Sie sich für Einladungen erneut an.");
    return;
  }
  const data = beginFormSubmission(form);
  if (data === null) {
    return;
  }
  const body = {
    display_name: data.get("display_name"),
    email: data.get("email"),
    role_codes: ["internal"],
  };
  const fingerprint = JSON.stringify(body);
  if (!state.pendingInvitation || state.pendingInvitation.fingerprint !== fingerprint) {
    state.pendingInvitation = {
      fingerprint,
      key: window.crypto.randomUUID(),
    };
  }
  try {
    const response = await request(API.adminInvitations, {
      method: "POST",
      csrf: "session",
      headers: { "Idempotency-Key": state.pendingInvitation.key },
      body,
    });
    if (!response.ok) {
      setError("admin-invitation-error", await problemMessage(response, "Einladung konnte nicht erstellt werden."));
      return;
    }
    form.reset();
    state.pendingInvitation = null;
    announce("Die Einladung wurde zur Zustellung vorgemerkt.");
  } catch {
    setError("admin-invitation-error", "Einladung konnte nicht erstellt werden.");
  } finally {
    setBusy(form, false);
  }
}

function applyMutationAvailability() {
  const canMutate = Boolean(state.sessionCsrf);
  byId("reauth-notice").hidden = canMutate;
  document.querySelectorAll(".mutation-control").forEach((control) => {
    control.disabled = !canMutate;
  });
  document.querySelectorAll(".calendar-mutation-control").forEach((control) => {
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
  showLogin("Sie wurden abgemeldet.");
}

function bindEvents() {
  byId("login-form").addEventListener("submit", handleLogin);
  byId("password-reset-request-form").addEventListener("submit", handlePasswordResetRequest);
  byId("account-token-form").addEventListener("submit", handleAccountToken);
  byId("mfa-form").addEventListener("submit", handleMfa);
  byId("enrollment-form").addEventListener("submit", handleEnrollmentConfirmation);
  byId("create-company-form").addEventListener("submit", handleCreateCompany);
  byId("edit-company-form").addEventListener("submit", handleCompanyUpdate);
  byId("add-contact-form").addEventListener("submit", handleAddContact);
  byId("calendar-offer-form").addEventListener("submit", handleCalendarOfferSave);
  byId("calendar-review-form").addEventListener("submit", handleCalendarReview);
  byId("admin-invitation-form").addEventListener("submit", handleAdminInvitation);
  byId("logout-button").addEventListener("click", handleLogout);
  byId("reauth-button").addEventListener("click", () => showLogin());
  byId("open-password-reset").addEventListener("click", showPasswordResetRequest);

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
  byId("open-calendar-offer-dialog").addEventListener("click", openNewCalendarOffer);
  byId("refresh-review-queue").addEventListener("click", loadReviewQueue);
  byId("reload-calendar-offer").addEventListener("click", reloadSelectedCalendarOffer);
  byId("reload-calendar-review").addEventListener("click", reloadSelectedCalendarReview);

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
configureRestrictedCalendarNodes(false, false);
if (!consumeAccountActionFromFragment()) {
  restoreSession();
}
