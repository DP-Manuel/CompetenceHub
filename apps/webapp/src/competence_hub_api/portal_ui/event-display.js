export const EVENT_FORMATS = Object.freeze({ online: "Online", praesenz: "Präsenz", hybrid: "Hybrid" });

const seatLabels = {
  unknown: "Platzstand nicht bekannt",
  closed: "Anfragefrist abgelaufen",
  none: "Keine Plätze für weitere Vormerkungen",
};

export function seatBadge(value) {
  const badge = document.createElement("span");
  const status = value?.status;
  const count = value?.remaining;
  const known = (status === "many" || status === "limited") && Number.isInteger(count) && count > 0;
  const label = known
    ? `${status === "limited" ? "Wenige Plätze" : "Plätze verfügbar"} · ${count} für Vormerkungen`
    : Object.hasOwn(seatLabels, status) ? seatLabels[status] : seatLabels.unknown;
  badge.className = "event-seat-status";
  badge.dataset.status = known ? status : Object.hasOwn(seatLabels, status) ? status : "unknown";
  badge.textContent = label;
  return badge;
}

export function eventPlace(event) {
  return event.format === "online" ? EVENT_FORMATS.online : event.public_location || "Ort noch nicht angegeben";
}

export function eventPrice(event) {
  return event.price?.status === "display_text" && event.price.text ? event.price.text : "Preis auf Anfrage";
}
