import type { Coach } from "../data/coaches";

// Authorized source review and explicit Preview/portrait approval, 23.10.2026.
export const susanneKlemm: Coach = {
  kind: "approved",
  name: "Frau Susanne Klemm",
  role: "Coach und Trainerin",
  previewRole: "Führung, Kommunikation & Resilienz",
  focus: ["Gesprächsführung", "Rollenbewusstsein", "Selbstwahrnehmung und Abgrenzung"],
  topics: ["fuehrung", "teams-konflikte", "gesundheit-praevention"],
  text: "Susanne Klemm bietet praxisorientierte Workshops zu Führung, Kommunikation, Selbstwahrnehmung und dem Umgang mit Stress an.",
  profilePath: "coaches/susanne-klemm",
  image: "images/coaches/susanne-klemm.webp",
  imageWidth: 1200,
  imageHeight: 1800,
  initials: "SK",
};

export const qualifications = [
  "Kinder- und Jugendcoach",
  "Selbstbehauptungs- und Resilienztrainerin",
  "Licensed Business Practitioner of NLP",
  "Licensed Business Master Practitioner of NLP",
  "Hypnose Coach",
  "NLS Stage Master",
  "Weiterbildung „Systemische Supervision kompakt“ (44 Zeitstunden)",
  "Fachfortbildung zur ganzheitlichen Mobbingpräventionstrainerin",
];

// Eight workshop titles from Seminarangebote Donner-Partner.pdf, in source order.
export const workshops = [
  "Mit den richtigen Fragetechniken erfolgreich zum Ziel – Reden kann jeder, fragen will gelernt sein!",
  "Selbstwahrnehmung trifft Fremdwahrnehmung – Spiegelkabinett oder klares Bild?",
  "Zwischen den Zeilen – Was wird (nicht) gesagt? Wahrnehmungsschulung & Körpersprache verstehen",
  "Zwischen Mama und Chefin: Wer hat hier eigentlich das Sagen? Rollenbewusstsein stärken & im Berufsalltag klar führen",
  "Dein Stress, nicht meiner! Warum soll ich mich eigentlich mit aufregen?",
  "Vom Kollegen zur Führungskraft",
  "Führungshaltung und Führungsstil",
  "Von Elefanten im Raum und anderen Missverständnissen",
];
