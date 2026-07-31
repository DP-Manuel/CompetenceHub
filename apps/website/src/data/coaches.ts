export type CoachTopicId =
  | "fuehrung"
  | "teams-konflikte"
  | "gesundheit-praevention"
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
    name: "Christian Galvano",
    role: "Dozent, Fachtrainer und Coach",
    previewRole: "Führung, Konflikte & Prävention",
    focus: [
      "Neuroleadership",
      "Konfliktmanagement",
      "Stress- und Burnoutprävention",
    ],
    topics: ["fuehrung", "teams-konflikte", "gesundheit-praevention"],
    text: "Christian Galvano verbindet neurowissenschaftliche Grundlagen mit praxisnahen Methoden für Führung, Kommunikation und gesundes Arbeiten.",
    profilePath: "coaches/christian-galvano",
    image: "images/coaches/christian-galvano.webp",
    imageWidth: 830,
    imageHeight: 830,
    initials: "CG",
  },
  {
    name: "Elisabeth Schwabauer",
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
    text: "Elisabeth Schwabauer verbindet psychologische Fachkenntnis mit Erfahrung in beruflicher Beratung, Teamprozessen und der Einordnung psychischer Belastungen.",
    profilePath: "coaches/elisabeth-schwabauer",
    image: "images/coaches/elisabeth-schwabauer.webp",
    imageWidth: 1200,
    imageHeight: 1800,
    initials: "ES",
  },
  {
    name: "Carolin Hupp",
    role: "Diplom-Sportwissenschaftlerin",
    previewRole: "Gesundheit, Bewegung & Prävention",
    focus: [
      "Betriebliche Gesundheit",
      "Bewegung und Prävention",
      "Entspannung und Balance",
    ],
    topics: ["gesundheit-praevention"],
    text: "Carolin Hupp bringt Gesundheits- und Trainingsmanagement, Bewegungsförderung und alltagstaugliche Prävention in Unternehmen und Gruppen zusammen.",
    profilePath: "coaches/carolin-hupp",
    initials: "CH",
  },
  {
    name: "Wegner-Ney",
    role: "Workshop- und Vortragsexpertise",
    previewRole: "Führung, Teams & Recruiting",
    focus: [
      "Führung und Teamstärkung",
      "Recruiting und Potenziale",
      "Zusammenarbeit im Mittelstand",
    ],
    topics: ["fuehrung", "teams-konflikte", "recruiting-potenziale"],
    text: "Wegner-Ney richtet den Blick auf starke Führung, funktionierende Teams und eine Personalgewinnung, die praktische Fähigkeiten und Entwicklungspotenziale ernst nimmt.",
    profilePath: "coaches/wegner-ney",
    image: "images/coaches/wegner-ney.jpg",
    imageWidth: 830,
    imageHeight: 830,
    initials: "WN",
  },
  {
    name: "Goran Celic",
    role: "Coach für Rhetorik und Vertrieb",
    previewRole: "Rhetorik, Vertrieb & Storytelling",
    focus: [
      "Rhetorik und überzeugender Auftritt",
      "Vertriebscoaching",
      "Storytelling und Gesprächsführung",
    ],
    topics: ["rhetorik-vertrieb"],
    text: "Goran Celic verbindet langjährige Vertriebserfahrung mit Rhetorik, Gesprächsführung und praxisnaher Begleitung für Vertriebsteams und Experten.",
    profilePath: "coaches/goran-celic",
    image: "images/coaches/goran-celic.png",
    imageWidth: 768,
    imageHeight: 929,
    initials: "GC",
  },
];
