import { editorialProfileCopy } from "../components/editorial-profile-copy";
import { finderEntries } from "../preview/offering-finder-data";
import { activeCoaches } from "./coaches";

export const workshopDiscoveryPath = "coaches/#workshop-themen";

// Navigation scope only. Titles, copy and publication rights remain in their source data.
const approvedThemes = new Map<string, readonly string[]>([
  ["coaches/christian-galvano", ["neuroleadership", "konfliktmanagement", "stresspraevention"]],
  ["coaches/manuela-rodriguez", ["ki-kompetenz"]],
]);

// Editorial summaries of the already published profile topics; no delivery promises.
const editorial: Record<string, { fit: string; focus: string[]; takeaway: string }> = {
  neuroleadership: {
    fit: "Für Führungskräfte und Unternehmen, die Mitarbeitende in Veränderungsphasen begleiten.",
    focus: ["Führung und Motivation", "Veränderung im Arbeitsalltag", "Mentale Stärke"],
    takeaway: "Impulse, um Führungsverhalten und Motivation im eigenen Arbeitsalltag bewusster zu betrachten.",
  },
  konfliktmanagement: {
    fit: "Für Teams und Führungskräfte, die Konflikte konstruktiver ansprechen und klären möchten.",
    focus: ["Konfliktklärung", "Kommunikation", "Verhandlungsstrategien"],
    takeaway: "Ansätze für Gespräche, die zur Klärung beitragen und Zusammenarbeit erleichtern können.",
  },
  stresspraevention: {
    fit: "Für Unternehmen und Teams, die beruflichen Stress und den Umgang mit Belastungen betrachten möchten.",
    focus: ["Stressmechanismen", "Eigene Ressourcen", "Gesunder Arbeitsalltag"],
    takeaway: "Anregungen, um Belastungen besser einzuordnen und vorhandene Ressourcen gezielter zu nutzen.",
  },
  "ki-kompetenz": {
    fit: "Für Unternehmen und Mitarbeitende, die KI-Kompetenz aufbauen und KI verantwortungsvoll einsetzen möchten.",
    focus: ["KI-Literacy", "Ethische Standards", "Praktische Anwendung"],
    takeaway: "Orientierung für den sicheren, sinnvollen Einsatz von KI im eigenen Arbeitskontext.",
  },
};

export const workshopProfiles = import.meta.env.PUBLIC_REVIEW_MODE === "true"
  ? activeCoaches.flatMap((coach) => {
    const themeIds = approvedThemes.get(coach.profilePath);
    if (coach.kind !== "approved" || !themeIds) return [];

    const slug = coach.profilePath.split("/")[1];
    const copy = editorialProfileCopy.get(coach.profilePath);
    const themes = themeIds.flatMap((id) => {
      const entry = finderEntries.find((item) => item.id === `${slug}/${id}`
        && item.coach.profilePath === coach.profilePath
        && item.formats.some((format) => format.kind === "individual" && format.audiences.includes("companies")));
      const topic = copy?.topics.find(({ title }) => title === entry?.title);
      return topic && editorial[id] ? [{ ...topic, ...editorial[id], id, path: `${coach.profilePath}/angebote/${id}/` }] : [];
    });

    return copy && themes.length ? [{ coach, copy, slug, themes }] : [];
  })
  : [];

export type WorkshopProfile = (typeof workshopProfiles)[number];
export type WorkshopTheme = WorkshopProfile["themes"][number];
