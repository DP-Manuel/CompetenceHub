export type CoachTopicId =
  | "fuehrung"
  | "teams-konflikte"
  | "gesundheit-praevention"
  | "ki-transformation"
  | "mediation"
  | "recruiting-potenziale"
  | "rhetorik-vertrieb"
  | "psychologische-beratung";

export type CoachTopicIcon =
  | "heart-pulse"
  | "leadership"
  | "message-circle"
  | "sparkles"
  | "user-round"
  | "users";

export interface CoachTopic {
  id: CoachTopicId;
  label: string;
  detail: string;
  icon: CoachTopicIcon;
}

export const coachTopics: CoachTopic[] = [
  {
    id: "fuehrung",
    label: "Führung",
    detail: "Verantwortung und Wirkung",
    icon: "leadership",
  },
  {
    id: "teams-konflikte",
    label: "Teams & Konflikte",
    detail: "Zusammenarbeit und Klärung",
    icon: "users",
  },
  {
    id: "gesundheit-praevention",
    label: "Gesundheit & Prävention",
    detail: "Belastung und Balance",
    icon: "heart-pulse",
  },
  {
    id: "ki-transformation",
    label: "KI & Transformation",
    detail: "KI-Kompetenz und verantwortungsvolle Einführung",
    icon: "sparkles",
  },
  {
    id: "mediation",
    label: "Mediation",
    detail: "Strukturierte Konfliktklärung",
    icon: "message-circle",
  },
  {
    id: "recruiting-potenziale",
    label: "Recruiting & Potenziale",
    detail: "Auswahl und Entwicklung",
    icon: "user-round",
  },
  {
    id: "rhetorik-vertrieb",
    label: "Rhetorik & Vertrieb",
    detail: "Auftritt und Gesprächsführung",
    icon: "message-circle",
  },
  {
    id: "psychologische-beratung",
    label: "Psychologische Beratung",
    detail: "Einordnung und Orientierung",
    icon: "sparkles",
  },
];
