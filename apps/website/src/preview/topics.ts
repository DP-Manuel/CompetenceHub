import { coachTopics } from "../data/coaches";
import type { CoachTopic } from "../data/coaches";

export const categories = [
  { id: "personalentwicklung", label: "Personalentwicklung" },
  { id: "persoenlichkeitsentwicklung", label: "Persönlichkeitsentwicklung" },
  { id: "karrierecoaching", label: "Karrierecoaching" },
] as const;
export type CategoryId = (typeof categories)[number]["id"];
export interface PreviewTopic extends CoachTopic {
  categories: CategoryId[];
}

// Editorial navigation only, not new Coach qualifications.
const assignments: Record<CoachTopic["id"], CategoryId[]> = {
  fuehrung: ["personalentwicklung", "persoenlichkeitsentwicklung"],
  "teams-konflikte": ["personalentwicklung", "persoenlichkeitsentwicklung"],
  "gesundheit-praevention": ["personalentwicklung", "persoenlichkeitsentwicklung"],
  "ki-transformation": ["personalentwicklung", "karrierecoaching"],
  mediation: ["personalentwicklung", "persoenlichkeitsentwicklung"],
  "recruiting-potenziale": ["personalentwicklung", "karrierecoaching"],
  "rhetorik-vertrieb": ["personalentwicklung", "persoenlichkeitsentwicklung", "karrierecoaching"],
  "psychologische-beratung": ["personalentwicklung", "persoenlichkeitsentwicklung", "karrierecoaching"],
};
export const topics: PreviewTopic[] = coachTopics.map((topic) => ({
  ...topic, categories: assignments[topic.id],
}));
export function topicsForCategory(category: CategoryId | "all") {
  return category === "all" ? topics : topics.filter((topic) => topic.categories.includes(category));
}
