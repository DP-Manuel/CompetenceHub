export type CoachTopicId =
  | "fuehrung"
  | "teams-konflikte"
  | "gesundheit-praevention"
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

export interface Coach {
  name: string;
  role: string;
  previewRole: string;
  focus: string[];
  topics: CoachTopicId[];
  text: string;
  profilePath: string;
  image?: string;
  imageWidth?: number;
  imageHeight?: number;
  initials: string;
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

export const coaches: Coach[] = [
  {
    name: "Herr Christian Galvano",
    role: "Dozent, Fachtrainer und Coach",
    previewRole: "Führung, Konflikte & Prävention",
    focus: [
      "Neuroleadership",
      "Konfliktmanagement",
      "Stress- und Burnoutprävention",
    ],
    topics: ["fuehrung", "teams-konflikte", "gesundheit-praevention"],
    text: "Herr Christian Galvano verbindet neurowissenschaftliche Grundlagen mit praxisnahen Methoden für Führung, Kommunikation und gesundes Arbeiten.",
    profilePath: "coaches/christian-galvano",
    image: "images/coaches/christian-galvano.webp",
    imageWidth: 830,
    imageHeight: 830,
    initials: "CG",
  },
  {
    name: "Frau Elisabeth Schwabauer",
    role: "Psychologin (M.Sc.)",
    previewRole: "Psychologie, Belastung & Teams",
    focus: [
      "Psychologische Beratung",
      "Psychische Belastung",
      "Team- und Konfliktklärung",
    ],
    topics: [
      "psychologische-beratung",
      "gesundheit-praevention",
      "teams-konflikte",
    ],
    text: "Frau Elisabeth Schwabauer verbindet psychologische Fachkenntnis mit Erfahrung in beruflicher Beratung, Teamprozessen und der Einordnung psychischer Belastungen.",
    profilePath: "coaches/elisabeth-schwabauer",
    image: "images/coaches/elisabeth-schwabauer.webp",
    imageWidth: 1200,
    imageHeight: 1800,
    initials: "ES",
  },
  {
    name: "Frau Carolin Hupp",
    role: "Diplom-Sportwissenschaftlerin",
    previewRole: "Gesundheit, Bewegung & Prävention",
    focus: [
      "Betriebliche Gesundheit",
      "Bewegung und Prävention",
      "Entspannung und Balance",
    ],
    topics: ["gesundheit-praevention"],
    text: "Frau Carolin Hupp bringt Gesundheits- und Trainingsmanagement, Bewegungsförderung und alltagstaugliche Prävention in Unternehmen und Gruppen zusammen.",
    profilePath: "coaches/carolin-hupp",
    initials: "CH",
  },
  {
    name: "Herr T. Wegner-Ney",
    role: "Unternehmensberater, Speaker, Workshop-Leiter und Coach",
    previewRole: "Veränderung, Prozesse & Führung",
    focus: [
      "Technologie- und Prozessveränderung",
      "Führung und Mitarbeiterbeteiligung",
      "Qualitätsmanagement im Mittelstand",
    ],
    topics: ["fuehrung", "teams-konflikte", "recruiting-potenziale"],
    text: "Herr T. Wegner-Ney begleitet mittelständische Unternehmen dabei, neue Technologien, Prozesse und Qualitätsanforderungen wirtschaftlich einzuordnen und gemeinsam mit ihren Mitarbeitenden wirksam umzusetzen.",
    profilePath: "coaches/wegner-ney",
    image: "images/coaches/wegner-ney.jpg",
    imageWidth: 830,
    imageHeight: 830,
    initials: "WN",
  },
  {
    name: "Herr Goran Celic",
    role: "Coach für Rhetorik und Vertrieb",
    previewRole: "Rhetorik, Vertrieb & Storytelling",
    focus: [
      "Rhetorik und überzeugender Auftritt",
      "Vertriebscoaching",
      "Storytelling und Gesprächsführung",
    ],
    topics: ["rhetorik-vertrieb"],
    text: "Herr Goran Celic verbindet langjährige Vertriebserfahrung mit Rhetorik, Gesprächsführung und praxisnaher Begleitung für Vertriebsteams und Experten.",
    profilePath: "coaches/goran-celic",
    image: "images/coaches/goran-celic.png",
    imageWidth: 768,
    imageHeight: 929,
    initials: "GC",
  },
  {
    name: "Frau Dr. Stefanie Becker",
    role: "Executive Coach und Team- und Organisationsentwicklerin",
    previewRole: "Change, Führung & Organisation",
    focus: [
      "Change und Organisationsentwicklung",
      "Vision, Strategie und Kultur",
      "Female Leadership und Neurodiversität",
    ],
    topics: ["fuehrung", "teams-konflikte"],
    text: "Frau Dr. Stefanie Becker begleitet Leitungsteams, Führungskräfte und Mitarbeitende in organisationalen und persönlichen Transformationsprozessen mit einem hypnosystemischen und beteiligungsorientierten Ansatz.",
    profilePath: "coaches/stefanie-becker",
    initials: "SB",
  },
];
