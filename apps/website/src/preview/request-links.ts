// Public contact already used by /kontakt. No data submission or tracking.
export function coachRequestMailto(coach: string, offering = ""): string {
  const subject = offering ? `Anfrage: ${offering} · ${coach}` : `Coaching-Anfrage: ${coach}`;
  const body = [
    "Guten Tag Frau Rappelt,",
    "",
    `ich interessiere mich für eine Abstimmung mit ${coach}.`,
    ...(offering ? [`Angebot / Format: ${offering}`] : []),
    "",
    "Mein Anliegen / meine Zielgruppe:",
    "",
    "Gewünschter Zeitraum und Rahmen:",
    "",
    "Bitte kontaktieren Sie mich zur persönlichen Abstimmung.",
  ].join("\n");
  return `mailto:competencehub@donner-partner.de?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}
