export const audiences = [
  { id: "einzel", label: "Eine Person" },
  { id: "team", label: "Ein Team oder eine Gruppe" },
  { id: "organisation", label: "Das Unternehmen" },
];

export const goals = [
  { id: "klaeren", label: "Eine Situation besser einordnen" },
  { id: "entwickeln", label: "Kompetenzen gezielt entwickeln" },
  { id: "auswahl", label: "Potenziale oder Eignung einschätzen" },
];

export const contactTopics = Object.freeze({
  business: "Businesscoaching für Unternehmen",
  assessment: "Assessment Center",
  workshop: "Workshop oder Vortrag",
  recruiting: "Recruiting",
  development: "Personalentwicklung",
  private: "Beratungsgespräche für Privatpersonen",
  advice: "Beratung",
});

export const directions = Object.freeze({
  business: { title: "Businesscoaching für Unternehmen", href: "mindforge#unternehmen", contact: "business",
    reason: "Für einzelne Führungskräfte oder Mitarbeitende, die eine berufliche Situation gezielt bearbeiten möchten.", audiences: ["einzel"], goals: ["klaeren", "entwickeln"] },
  workshops: { title: "Workshops & Vorträge", href: "leistungen#gruppenformate", contact: "workshop",
    reason: "Für Gruppen, die ein gemeinsames Thema erarbeiten oder einen fachlichen Impuls setzen möchten.", audiences: ["team"], goals: ["entwickeln"] },
  recruiting: { title: "Recruiting für Unternehmen", href: "leistungen#recruiting", contact: "recruiting",
    reason: "Wenn Sie den Personalbedarf, das Profil der Stelle und einen passenden Auswahlweg klären möchten.", audiences: ["organisation"], goals: ["klaeren"] },
  assessment: { title: "Assessment Center", href: "unternehmen#assessment-center", contact: "assessment",
    reason: "Wenn Sie Bewerbende strukturiert beurteilen oder Entwicklungsfelder sichtbar machen möchten.", audiences: ["einzel", "organisation"], goals: ["auswahl"] },
  development: { title: "Personalentwicklung", href: "leistungen#personalentwicklung", contact: "development",
    reason: "Wenn Sie den Entwicklungsbedarf einordnen und geeignete nächste Schritte für Mitarbeitende bestimmen möchten.", audiences: ["organisation", "team"], goals: ["entwickeln"] },
  advice: { title: "Beratung für Unternehmen", href: "mindforge#beratung", contact: "advice",
    reason: "Wenn mehrere Fragen zusammenspielen und der Auftrag zunächst gemeinsam eingeordnet werden soll.", audiences: ["organisation", "team"], goals: ["klaeren"] },
});

const byTopic = Object.freeze({
  fuehrung: ["business", "workshops", "development"],
  teams: ["workshops", "business", "advice"],
  recruiting: ["recruiting", "assessment"],
  entwicklung: ["development", "assessment", "workshops"],
  veraenderung: ["advice", "business", "workshops"],
  gesundheit: ["business", "advice", "development"],
});

// Input is a closed set. Neither answers nor resulting order are transmitted.
/** @returns {(typeof directions)[keyof typeof directions][]} */
export function suggestDirections(topic = "", audience = "", goal = "") {
  if (!Object.hasOwn(byTopic, topic) || !audiences.some(({ id }) => id === audience)
    || !goals.some(({ id }) => id === goal)) return [];
  return byTopic[topic]
    .map((key, index) => {
      const direction = directions[key];
      const score = Number(direction.audiences.includes(audience)) + 2 * Number(direction.goals.includes(goal));
      return { direction, index, score };
    })
    .sort((a, b) => b.score - a.score || a.index - b.index)
    .map(({ direction }) => direction);
}
