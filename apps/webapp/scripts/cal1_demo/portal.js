"use strict";
// Populate native form values only; all mutations still use the existing Portal.
const dialog = document.querySelector("#calendar-offer-dialog");
const fill = document.createElement("button");
fill.type = "button";
fill.className = "demo-fill";
fill.textContent = "Demo-Werte einsetzen";
fill.addEventListener("click", () => {
  const start = new Date();
  start.setDate(start.getDate() + 10);
  start.setHours(10, 0, 0, 0);
  const end = new Date(start); end.setHours(12);
  const deadline = new Date(start); deadline.setDate(deadline.getDate() - 3);
  const local = date => new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  const values = {
    "calendar-title": "DEMO: Teamworkshop",
    "calendar-summary": "Synthetischer Gruppenworkshop. Kein echtes Angebot.",
    "calendar-starts-at": local(start), "calendar-ends-at": local(end),
    "calendar-time-zone": "Europe/Berlin", "calendar-format": "praesenz",
    "calendar-location": "Demo-Raum (kein echter Veranstaltungsort)",
    "calendar-capacity": "12", "calendar-review-threshold": "6",
    "calendar-decision-deadline": local(deadline), "calendar-price": "Demo: Preis nach Abstimmung",
  };
  for (const [id, value] of Object.entries(values)) {
    const input = document.getElementById(id);
    if (input) { input.value = value; input.dispatchEvent(new Event("input", { bubbles: true })); }
  }
  const topic = document.querySelector("#calendar-topic");
  if (topic.options.length > 1) topic.selectedIndex = 1;
  document.querySelector("#calendar-title").focus();
});
dialog?.append(fill);
