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
export function render({ target, business, createElement, onNavigate }) {
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

  function section(key, title, destinations) {
    const node = element("section");
    node.dataset.businessSection = key;
    node.setAttribute("aria-label", title);
    node.append(element("h3", title));
    if (onNavigate) {
      const actions = element("div", null, "button-row");
      for (const [area, label] of destinations) {
        const action = element("button", label, "button button-secondary");
        action.type = "button";
        action.dataset.businessDestination = area;
        action.addEventListener("click", () => onNavigate(area));
        actions.append(action);
      }
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
      row.dataset.businessTask = task.kind;
      row.append(element("strong", task.title), ...rowContent(task));
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
    const node = section("review", "Prüfung und Vormerkungen", [
      ["review-calendar", "Zur Prüfliste"],
      ["reservation-review", "Vormerkungen prüfen"],
    ]);
    node.append(
      element("h4", "Offene Vorgänge"),
      counts(summary, [
        ["calendar_in_review", "Angebote zur Prüfung"],
        ["calendar_resubmitted", "Davon erneut eingereicht"],
        ["pending", "Neue Vormerkungen"],
        ["clarification", "Rückfrage offen"],
        ["reply_ready", "Antwort bereit zur Prüfung"],
      ]),
      element("h4", "Fristen und Auslastung"),
      counts(summary, RISK),
      element("h4", "Priorisierte Vorgänge"),
      taskList(tasks, "Keine priorisierten Vorgänge.", (task) => {
        if (task.kind === "calendar_review") {
          return [facts(["Angebot prüfen"], "Eingereicht", task.submitted_at)];
        }
        return [facts([
          `${task.occupied_seats} von ${task.capacity} Plätzen belegt`,
          task.occupied_seats >= task.review_threshold ? "Prüfschwelle erreicht" :
            `Noch ${task.review_threshold - task.occupied_seats} bis zur Prüfschwelle`,
          task.reply_ready ? `Antworten zur Prüfung: ${task.reply_ready}` : null,
          task.pending ? `Neue Vormerkungen: ${task.pending}` : null,
          task.overdue ? "Entscheidungsfrist abgelaufen" : task.deadline_soon ? "Frist endet bald" : null,
          task.revision_pending ? "Neue Fassung eingereicht; Plätze belegt" : null,
        ], "Frist", task.decision_deadline)];
      }),
      details("Entschiedene und vergangene Vormerkungen",
        counts(summary, [...CLOSED, ["past", "Vergangene Veranstaltungen"]]))
    );
  }

  if (business.company) {
    const { counts: summary, tasks } = business.company;
    const node = section("company", "Vormerkungen Ihrer Firma", [
      ["reservations", "Zu den Vormerkungen"],
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
    const node = section("coach", "Eigene veröffentlichte Veranstaltungen", [
      ["coach-calendar", "Zu den Kalenderangeboten"],
    ]);
    node.append(counts(business.coach.counts, [
      ["published", "Veröffentlicht"], ["upcoming", "Bevorstehend"], ["past", "Vergangen"],
      ...RISK,
    ]));
    const offers = business.coach.upcoming_offers || [];
    if (offers.length) {
      const list = element("ul", null, "pilot-users");
      for (const offer of offers) {
        const row = element("li");
        row.append(element("strong", offer.title), facts([
          `${offer.occupied_seats} von ${offer.capacity} Plätzen belegt`,
          offer.revision_pending ? "Neue Fassung betrifft belegte Plätze" : null,
        ], "Beginn", offer.starts_at));
        list.append(row);
      }
      node.append(element("h4", "Kommende freigegebene Termine"), list);
    }
  }

  if (business.admin) {
    const node = section("admin", "Zugänge und wichtige Änderungen", [
      ["accounts", "Zu den Zugängen"],
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
