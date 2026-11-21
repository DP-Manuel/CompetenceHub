import { germanDateTime } from "./calendar-form.mjs";

const CLOSED = [
  ["approved", "Positiv geprüft (keine Buchung)"],
  ["rejected", "Abgelehnt"],
  ["withdrawn", "Zurückgenommen"],
  ["cancelled", "Veranstaltung abgesagt"],
];
const RISK = [
  ["overdue", "Angebote mit überfälligen Vorgängen"],
  ["deadline_soon", "Angebote mit Frist in 48 Stunden"],
  ["full", "Angebote ohne freie Plätze"],
  ["threshold_reached", "Angebote mit erreichter Prüfschwelle"],
  ["revision_pending", "Eingereichte Änderungen mit belegten Plätzen"],
];
const RESERVATION_STATUS = {
  pending: "Eingereicht",
  clarification: "In Klärung",
  ...Object.fromEntries(CLOSED),
};
const AUDIT_CATEGORY = {
  account_access: "Kontozugriff",
  account_activation: "Kontofreischaltung",
  account_recovery: "Kontowiederherstellung",
  calendar_publication: "Kalenderveröffentlichung",
  calendar_review: "Kalenderprüfung",
  calendar_withdrawal: "Veranstaltungsrücknahme",
  reservation_clarification: "Rückfrage zur Vormerkung",
  reservation_decision: "Vormerkungsentscheidung",
  reservation_withdrawal: "Rücknahme einer Vormerkung",
};
const AUDIT_STATUS = { success: "Erfolgreich", denied: "Abgewiesen", recorded: "Erfasst" };

// The caller owns session/loading state and workspace changes.
export function render({ target, business, calendar, createElement, onNavigate, areas }) {
  target.replaceChildren();
  target.hidden = true;
  if (!business) return;
  const create = createElement ?? ((tag) => target.ownerDocument.createElement(tag));

  function element(tag, label, className) {
    const node = create(tag);
    if (label != null) node.textContent = label;
    if (className) node.className = className;
    return node;
  }

  function time(value) {
    const instant = new Date(value);
    if (!value || !Number.isFinite(instant.getTime())) return null;
    const node = element("time", germanDateTime(instant));
    node.dateTime = instant.toISOString();
    return node;
  }

  function shortcut(area, label, options, context) {
    if (!onNavigate || (areas && !areas.has(area))) return null;
    const action = element("button", label, "button button-secondary");
    action.type = "button";
    action.dataset.businessDestination = area;
    if (context) action.setAttribute("aria-label", `${label}: ${context}`);
    action.addEventListener("click", () => onNavigate(area, options));
    return action;
  }

  function section(key, title, destinations) {
    const node = element("section");
    node.dataset.businessSection = key;
    node.setAttribute("aria-label", title);
    node.append(element("h3", title));
    const links = destinations.map((args) => shortcut(...args)).filter(Boolean);
    if (links.length) {
      const actions = element("div", null, "button-row");
      actions.append(...links);
      node.append(actions);
    }
    target.append(node);
    target.hidden = false;
    return node;
  }

  function counts(values, entries) {
    const list = element("dl", null, "calendar-card-meta");
    for (const [key, label] of entries) {
      list.append(element("dt", label), element("dd", String(values[key] ?? 0)));
    }
    return list;
  }

  function workCounts(values, entries) {
    const list = element("dl", null, "business-work-counts");
    for (const [key, label, area, options] of entries) {
      const value = values[key] ?? 0;
      const group = element("div");
      const count = element("dd", String(value));
      const action = value > 0 && shortcut(area, label, options);
      if (action) {
        action.classList.add("business-count-action");
        // Preserve the visible count and the term without announcing the count twice.
        action.setAttribute("aria-label", `${label}: ${value}`);
        count.setAttribute("aria-hidden", "true");
      }
      const term = element("dt", action ? null : label);
      if (action) term.append(action);
      group.append(term, count);
      list.append(group);
    }
    return list;
  }

  function details(title, ...children) {
    const node = element("details", null, "reservation-activity");
    node.append(element("summary", title), ...children);
    return node;
  }

  function taskList(tasks, emptyLabel, rowContent) {
    if (!tasks.length) return element("p", emptyLabel, "empty-state");
    const list = element("ul", null, "pilot-users");
    for (const task of tasks) {
      const row = element("li");
      if (task.kind) row.dataset.businessTask = task.kind;
      row.append(element("strong", task.title), ...rowContent(task).filter(Boolean));
      list.append(row);
    }
    return list;
  }

  function facts(labels, dateLabel, date) {
    const row = element("p");
    row.textContent = labels.filter(Boolean).join(" · ");
    const dateNode = time(date);
    if (dateNode) row.append(row.textContent ? " · " : "", `${dateLabel}: `, dateNode);
    return row;
  }

  if (business.review) {
    const { counts: summary, tasks } = business.review;
    const calendarTasks = tasks.filter((task) => task.kind === "calendar_review");
    const reservationTasks = tasks.filter((task) => task.kind === "reservation_review");
    const reserveQueue = ["reservation-review", "Vormerkungen prüfen", { reservationFilters: {} }];
    const reviewQueue = ["review-calendar", "Zur Prüfliste", { reviewTitle: "" }];
    const node = section("review", "Prüfung und Vormerkungen", [reviewQueue, reserveQueue]);
    node.append(workCounts({ ...summary, decision: (summary.pending ?? 0) + (summary.reply_ready ?? 0) }, [
      ["calendar_in_review", "Angebote zur Prüfung", reviewQueue[0], reviewQueue[2]],
      ["decision", "Vormerkungen zur Entscheidung", reserveQueue[0], { reservationFilters: { status: "decision" } }],
      ["overdue", "Angebote mit Fristablauf", reserveQueue[0], { reservationFilters: { deadline: "overdue" } }],
      ["deadline_soon", "Angebote mit Frist in 48 Stunden", reserveQueue[0], { reservationFilters: { deadline: "soon" } }],
    ]));
    const queues = element("div", null, "business-queues");
    const reservations = element("div");
    reservations.append(element("h4", "Priorisierte Vormerkungen"),
      taskList(reservationTasks, "Keine priorisierten Vormerkungen.", (task) => {
        const isDeadline = task.overdue || task.deadline_soon;
        // The snapshot groups by offer/revision but exposes only the title, not an ID.
        const reservationFilters = { offer: Array.from(task.title).slice(0, 100).join(""), status: "" };
        if (isDeadline) {
          reservationFilters.status = "open";
          reservationFilters.deadline = task.overdue ? "overdue" : "soon";
        }
        return [facts([
          task.overdue ? "Entscheidungsfrist abgelaufen" : task.deadline_soon ? "Frist endet bald" : null,
          task.revision_pending ? "Neue Fassung eingereicht; Plätze belegt" : null,
          task.reply_ready ? `Antworten zur Prüfung: ${task.reply_ready}` : null,
          task.pending ? `Neue Vormerkungen: ${task.pending}` : null,
        ], "Frist", task.decision_deadline),
        facts([`${task.occupied_seats} von ${task.capacity} Plätzen belegt`,
          task.threshold_reached ? "Prüfschwelle erreicht" : null]),
        shortcut(reserveQueue[0], "Vorgänge zum Titel suchen", { reservationFilters }, task.title)];
      }));
    const submissions = element("div");
    submissions.append(element("h4", "Eingereichte Angebote"),
      taskList(calendarTasks, "Keine eingereichten Angebote.", (task) => [
        facts([], "Eingereicht", task.submitted_at),
        shortcut(reviewQueue[0], "Titel in der Prüfliste suchen", { reviewTitle: task.title }, task.title),
      ]));
    queues.append(reservations, submissions);
    node.append(queues, details("Weitere Kennzahlen",
      counts(summary, [
        ["calendar_resubmitted", "Erneut eingereichte Angebote"],
        ["pending", "Neue Vormerkungen"],
        ["reply_ready", "Antworten zur Prüfung"],
        ["clarification", "Warten auf Antwort der Firma"],
        ...RISK.slice(2), ...CLOSED, ["past", "Vormerkungen vergangener Veranstaltungen"],
      ])));
  }

  if (business.company) {
    const { counts: summary, tasks } = business.company;
    const node = section("company", "Vormerkungen Ihrer Firma", [
      ["reservations", "Zu den Vormerkungen"],
      ["reservations", "Veranstaltungen finden", { catalogue: true }],
    ]);
    const forKind = (kind, empty, dateLabel, dateKey) => taskList(
      tasks.filter((task) => task.kind === kind), empty,
      (task) => [facts([
        task.reply_ready ? "Antwort eingereicht" : RESERVATION_STATUS[task.status],
        `Plätze: ${task.seats}`,
      ], dateLabel, task[dateKey])]
    );
    node.append(
      counts(summary, [
        ["reply_needed", "Ihre Antwort ist offen"],
        ["awaiting_decision", "Entscheidung ausstehend"],
        ["upcoming", "Bevorstehende Vormerkungen"],
        ["past", "Vergangene Vormerkungen"],
      ]),
      element("h4", "Offene Antworten"),
      forKind("reply_needed", "Keine offenen Antworten.", "Entscheidungsfrist", "decision_deadline"),
      element("h4", "Bevorstehende Veranstaltungen"),
      forKind("upcoming", "Keine bevorstehenden Vormerkungen.", "Beginn", "starts_at"),
      details("Vergangene und entschiedene Vormerkungen",
        forKind("past", "Keine vergangenen Vormerkungen.", "Ende", "ends_at"), counts(summary, CLOSED))
    );
  }

  if (business.coach) {
    const node = section("coach", "Eigene Angebote und Termine", [
      ["coach-calendar", "Zu den Kalenderangeboten", { coachStatus: "" }],
    ]);
    if (calendar) node.append(workCounts(calendar, [
      ["changes_requested", "Änderungen angefordert", "coach-calendar", { coachStatus: "changes_requested" }],
      ["draft", "Entwürfe", "coach-calendar", { coachStatus: "draft" }],
      ["in_review", "Zur Prüfung eingereicht", "coach-calendar", { coachStatus: "in_review" }],
    ]));
    const offers = business.coach.upcoming_offers || [];
    const totals = business.coach.counts;
    node.append(element("h4", "Kommende freigegebene Termine"),
      taskList(offers, "Keine kommenden freigegebenen Termine.", (offer) => [
        facts([`${offer.occupied_seats} von ${offer.capacity} Plätzen belegt`,
          offer.revision_pending ? "Neue Fassung betrifft belegte Plätze" : null,
        ], "Beginn", offer.starts_at),
        offer.id && shortcut("coach-calendar", "Angebot in der Liste anzeigen", { coachOfferId: offer.id }, offer.title),
      ]),
      details("Veröffentlichung und Auslastung", counts(totals, [
        ["published", "Veröffentlicht"], ["upcoming", "Bevorstehend"], ["past", "Vergangen"], ...RISK,
      ])));
  }

  if (business.admin) {
    const node = section("admin", "Zugänge und wichtige Änderungen", [
      ["accounts", "Zu den Zugängen"],
      ["companies", "Zur Firmen- und Kundenbetreuung"],
    ]);
    const { counts: summary, audit } = business.admin;
    const activity = element("ul", null, "pilot-users");
    for (const item of audit) {
      const row = element("li");
      row.append(element("strong", AUDIT_CATEGORY[item.category] ?? "Änderung"),
        facts([AUDIT_STATUS[item.status] ?? "Erfasst"], "Zeit", item.occurred_at));
      activity.append(row);
    }
    node.append(
      counts(summary, [["accounts", "Konten"], ["active", "Aktiv"], ["pending_activation", "Erstzugang offen"],
        ["companies", "Unternehmen"], ["linked_contacts", "Zugeordnete Firmenkontakte"]]),
      details(`Wichtige Änderungen (${audit.length})`, audit.length
        ? activity : element("p", "Keine wichtigen Änderungen erfasst.", "empty-state"))
    );
  }
}
