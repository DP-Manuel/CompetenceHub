export const CALENDAR_ZONE = "Europe/Berlin";
const dayFormatter = new Intl.DateTimeFormat("en-CA", {
  timeZone: CALENDAR_ZONE, year: "numeric", month: "2-digit", day: "2-digit",
});
const clockFormatter = new Intl.DateTimeFormat("de-DE", {
  timeZone: CALENDAR_ZONE, hour: "2-digit", minute: "2-digit", hourCycle: "h23",
});
const zoneFormatter = new Intl.DateTimeFormat("de-DE", { timeZone: CALENDAR_ZONE, timeZoneName: "short" });
const instantFormatter = new Intl.DateTimeFormat("de-DE", {
  timeZone: CALENDAR_ZONE, day: "2-digit", month: "2-digit", year: "numeric",
  hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZoneName: "short",
});
export const calendarInstantLabel = value => instantFormatter.format(new Date(value));
const dateFormatter = new Intl.DateTimeFormat("de-DE", {
  timeZone: "UTC", weekday: "short", day: "numeric", month: "long", year: "numeric",
});

export function berlinDay(value) {
  const parts = Object.fromEntries(dayFormatter.formatToParts(new Date(value)).map(part => [part.type, part.value]));
  return `${parts.year}-${parts.month}-${parts.day}`;
}
export function monthKeys(value = new Date(), count = 4) {
  const [year, month] = berlinDay(value).split("-").map(Number);
  return Array.from({ length: count }, (_, offset) => new Date(Date.UTC(year, month - 1 + offset, 1)).toISOString().slice(0, 7));
}
const civilDate = key => new Date(`${key}T12:00:00Z`);
export const calendarDateLabel = key => dateFormatter.format(civilDate(key));
export const calendarMonthLabel = key => civilDate(key + "-01").toLocaleDateString("de-DE", { timeZone: "UTC", month: "long", year: "numeric" });

function interval(offer) {
  const start = Date.parse(offer.starts_at), end = Date.parse(offer.ends_at);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return null;
  // [start,end): the final millisecond belongs to the final occupied civil day.
  // Never advance by 24 hours: Berlin civil days may be 23 or 25 hours long.
  return { offer, start, end, first: berlinDay(start), last: berlinDay(end - 1) };
}

export function segmentLabel(offer, day, role) {
  const begin = clockFormatter.format(new Date(offer.starts_at));
  const end = clockFormatter.format(new Date(offer.ends_at));
  const zone = value => zoneFormatter.formatToParts(new Date(value)).find(part => part.type === "timeZoneName").value;
  const beginZone = zone(offer.starts_at), endZone = zone(offer.ends_at);
  const changesZone = beginZone !== endZone;
  const beginLabel = `${begin} Uhr${changesZone ? ` (${beginZone})` : ""}`;
  const endLabel = `${end} Uhr${changesZone ? ` (${endZone})` : ""}`;
  const suffix = berlinDay(offer.ends_at) > day ? " (Folgetag)" : "";
  if (role === "single") return changesZone ? `${beginLabel} – ${endLabel}${suffix}` : `${begin} – ${end} Uhr${suffix}`;
  if (role === "start") return `Beginn ${beginLabel}`;
  if (role === "end") return `Ende ${endLabel}${suffix}`;
  return "Fortsetzung";
}

// Pure public-view layout. Neither DTOs nor records are changed or duplicated.
// Each week assigns a stable lane to an interval, shared by all its day cells.
export function buildMonthLayout(offers, month) {
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(month)) throw new RangeError("Invalid calendar month");
  const [year, number] = month.split("-").map(Number);
  const count = new Date(Date.UTC(year, number, 0)).getUTCDate();
  const firstWeekday = (civilDate(month + "-01").getUTCDay() + 6) % 7;
  const weeks = [];
  for (let day = 1; day <= count; day++) {
    const index = firstWeekday + day - 1, weekIndex = Math.floor(index / 7);
    const week = weeks[weekIndex] ??= { days: [], lanes: 0 };
    week.days.push({ key: `${month}-${String(day).padStart(2, "0")}`, column: index % 7, segments: [] });
  }
  const unique = [...new Map(offers.map(offer => [offer.id, offer])).values()];
  const intervals = unique.map(interval).filter(item => item && item.first <= `${month}-${count}` && item.last >= `${month}-01`)
    .sort((a, b) => a.start - b.start || b.end - a.end || String(a.offer.id).localeCompare(String(b.offer.id), "en"));
  for (const week of weeks) {
    const occupiedUntil = [];
    for (const item of intervals) {
      const days = week.days.filter(day => item.first <= day.key && day.key <= item.last);
      if (!days.length) continue;
      const from = days[0].column, to = days.at(-1).column;
      let lane = occupiedUntil.findIndex(lastColumn => lastColumn < from);
      if (lane === -1) lane = occupiedUntil.length;
      occupiedUntil[lane] = to;
      days.forEach((day, index) => {
        const role = item.first === item.last ? "single" : day.key === item.first ? "start" : day.key === item.last ? "end" : "continue";
        day.segments.push({ offer: item.offer, day: day.key, lane, role,
          label: segmentLabel(item.offer, day.key, role),
          connectedBefore: index > 0, connectedAfter: index < days.length - 1 });
      });
    }
    week.lanes = occupiedUntil.length;
  }
  return { month, weeks, offerCount: intervals.length };
}

function text(tag, value, className) {
  const element = document.createElement(tag);
  element.textContent = value;
  if (className) element.className = className;
  return element;
}

// Reusable DOM view: a future CAL-0.1 adapter supplies public offers + callback.
// No fetch, auth, persistence, real Coach mapping or application-global IDs here.
export function renderMonth(container, layout, onSelect, detailsId = null) {
  container.classList.add("calendar-month");
  container.replaceChildren();
  for (const week of layout.weeks) {
    const row = document.createElement("div");
    row.className = "calendar-week";
    row.setAttribute("role", "group");
    row.setAttribute("aria-label", `Kalenderwoche, ${calendarDateLabel(week.days[0].key)} bis ${calendarDateLabel(week.days.at(-1).key)}`);
    row.style.gridTemplateRows = `minmax(28px, auto)${week.lanes ? ` repeat(${week.lanes}, minmax(76px, auto))` : ""}`;
    for (const day of week.days) {
      const cell = document.createElement("div");
      cell.className = "day";
      cell.dataset.date = day.key;
      cell.style.gridColumn = String(day.column + 1);
      cell.style.gridRow = `1 / span ${week.lanes + 1}`;
      const label = text("time", civilDate(day.key).toLocaleDateString("de-DE", { timeZone: "UTC", weekday: "short", day: "numeric" }), "day-label");
      label.dateTime = day.key;
      cell.append(label);
      for (const segment of day.segments) {
        const { offer } = segment;
        const button = document.createElement("button");
        button.type = "button";
        button.className = "event-segment";
        button.classList.toggle("is-connected-before", segment.connectedBefore);
        button.classList.toggle("is-connected-after", segment.connectedAfter);
        button.dataset.offer = offer.id;
        button.dataset.segmentRole = segment.role;
        button.dataset.date = day.key;
        if (detailsId) button.setAttribute("aria-controls", detailsId);
        button.style.gridRow = String(segment.lane + 2);
        const range = `${calendarInstantLabel(offer.starts_at)} bis ${calendarInstantLabel(offer.ends_at)}, Europe/Berlin`;
        button.setAttribute("aria-label", `${offer.title}, ${offer.topic.name}, ${calendarDateLabel(day.key)}, ${segment.label}. Gesamtzeitraum: ${range}`);
        button.append(text("span", segment.label, "event-segment__phase"),
          text("strong", offer.title, "event-segment__title"), text("span", offer.topic.name, "event-segment__topic"));
        button.addEventListener("click", () => onSelect(offer));
        cell.append(button);
      }
      row.append(cell);
    }
    container.append(row);
  }
}
