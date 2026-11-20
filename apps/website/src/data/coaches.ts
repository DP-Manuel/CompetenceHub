import { activeCoachProfiles } from "../../config/active-coach-publication.mjs";
import { historicalCoaches } from "../preview/historical-coaches";
import { susanneKlemm } from "../preview/susanne-klemm";
import type { CoachTopicId } from "./coach-topics";

export interface Coach {
  kind: "approved" | "demo";
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

const existingCoaches: Coach[] = [
  {
    kind: "approved",
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
    kind: "approved",
    name: "Manuela Rodríguez, M.A.",
    role: "KI-Managerin, Leitung Digitalstrategie, Dozentin und Coach",
    previewRole: "KI-Kompetenz, Didaktik & Transformation",
    focus: [
      "KI-Literacy und ethische Standards",
      "Didaktik und Psychoedukation",
      "Erwachsenenbildung",
    ],
    topics: [
      "ki-transformation",
      "fuehrung",
      "psychologische-beratung",
    ],
    text: "Manuela Rodríguez verbindet KI-Kompetenz, Didaktik und menschenzentrierte Transformation und begleitet Unternehmen beim verantwortungsvollen Einsatz künstlicher Intelligenz.",
    profilePath: "coaches/manuela-rodriguez",
    image: "images/coaches/manuela-rodriguez.webp",
    imageWidth: 1200,
    imageHeight: 1200,
    initials: "MR",
  },
  {
    kind: "approved",
    name: "Frau Gülcan Elmas-Brandes",
    role: "Coach, Trainerin und Diplom-Betriebswirtin (VWA)",
    previewRole: "Karriere, Gesundheit & Qualität",
    focus: ["Karriere- und Bewerbungscoaching", "Ernährungs- und Gesundheitsorientierung", "Projekt- und Qualitätsmanagement"],
    topics: ["recruiting-potenziale", "gesundheit-praevention", "teams-konflikte"],
    text: "Frau Gülcan Elmas-Brandes verbindet Coaching und Training mit langjähriger Erfahrung in Projekt-, Qualitäts- und Finanzmanagement sowie interkultureller Zusammenarbeit.",
    profilePath: "coaches/guelcan-elmas-brandes",
    image: "images/coaches/guelcan-elmas-brandes.png",
    imageWidth: 203,
    imageHeight: 260,
    initials: "GE",
  },
  {
    kind: "demo",
    name: "Demoprofil 01",
    role: "Fiktives Profil · Psychologie und Teamklärung",
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
    text: "Dieses fiktive Demoprofil zeigt, wie psychologische Beratung, Belastungsprävention und Teamklärung im Coach-Netzwerk auffindbar werden können.",
    profilePath: "coaches/demoprofil-01",
    initials: "01",
  },
  {
    kind: "demo",
    name: "Demoprofil 02",
    role: "Fiktives Profil · Gesundheit und Prävention",
    previewRole: "Gesundheit, Bewegung & Prävention",
    focus: [
      "Betriebliche Gesundheit",
      "Bewegung und Prävention",
      "Entspannung und Balance",
    ],
    topics: ["gesundheit-praevention"],
    text: "Dieses fiktive Demoprofil veranschaulicht Angebote rund um betriebliche Gesundheit, Bewegung und alltagstaugliche Prävention.",
    profilePath: "coaches/demoprofil-02",
    initials: "02",
  },
  {
    kind: "demo",
    name: "Demoprofil 03",
    role: "Fiktives Profil · Karriere, Gesundheit und Qualität",
    previewRole: "Karriere, Gesundheit & Qualität",
    focus: [
      "Karriere- und Bewerbungscoaching",
      "Ernährungs- und Gesundheitsorientierung",
      "Projekt- und Qualitätsmanagement",
    ],
    topics: [
      "recruiting-potenziale",
      "gesundheit-praevention",
      "teams-konflikte",
    ],
    text: "Dieses fiktive Demoprofil zeigt die kombinierte Suche nach beruflicher Orientierung, Gesundheitsimpulsen und organisatorischer Qualität.",
    profilePath: "coaches/demoprofil-03",
    initials: "03",
  },
  {
    kind: "demo",
    name: "Demoprofil 04",
    role: "Fiktives Profil · Veränderung, Prozesse und Führung",
    previewRole: "Veränderung, Prozesse & Führung",
    focus: [
      "Technologie- und Prozessveränderung",
      "Führung und Mitarbeiterbeteiligung",
      "Qualitätsmanagement im Mittelstand",
    ],
    topics: ["fuehrung", "teams-konflikte", "recruiting-potenziale"],
    text: "Dieses fiktive Demoprofil veranschaulicht die Suche nach Begleitung für Technologie- und Prozessveränderung, Führung und Beteiligung.",
    profilePath: "coaches/demoprofil-04",
    initials: "04",
  },
  {
    kind: "demo",
    name: "Demoprofil 05",
    role: "Fiktives Profil · Rhetorik und Vertrieb",
    previewRole: "Rhetorik, Vertrieb & Storytelling",
    focus: [
      "Rhetorik und überzeugender Auftritt",
      "Vertriebscoaching",
      "Storytelling und Gesprächsführung",
    ],
    topics: ["rhetorik-vertrieb"],
    text: "Dieses fiktive Demoprofil zeigt mögliche Schwerpunkte für Auftritt, Gesprächsführung, Vertrieb und Storytelling.",
    profilePath: "coaches/demoprofil-05",
    initials: "05",
  },
  {
    kind: "demo",
    name: "Demoprofil 06",
    role: "Fiktives Profil · Change, Führung und Organisation",
    previewRole: "Change, Führung & Organisation",
    focus: [
      "Change und Organisationsentwicklung",
      "Vision, Strategie und Kultur",
      "Female Leadership und Neurodiversität",
    ],
    topics: ["fuehrung", "teams-konflikte"],
    text: "Dieses fiktive Demoprofil veranschaulicht Begleitung für Change, Führung, Strategie, Kultur und Organisationsentwicklung.",
    profilePath: "coaches/demoprofil-06",
    initials: "06",
  },
];

export const activeCoaches = activeCoachProfiles.map(({ slug, portrait }) => {
  const coach = [...existingCoaches, ...historicalCoaches, susanneKlemm].find((entry) =>
    entry.kind === "approved" && entry.profilePath === `coaches/${slug}`
  );
  if (!coach || coach.image !== `images/coaches/${portrait}`) {
    throw new Error(`Missing approved Coach or portrait: ${slug}`);
  }
  return coach;
});

// Previously published fictional routes remain accessible directly, but are
// not part of the active portfolio, sitemap or Finder.
export const coaches = [...activeCoaches, ...existingCoaches.filter(({ kind }) => kind === "demo")];
