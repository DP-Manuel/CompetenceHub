import type { Duration } from "../projection/model";
import { topics, topicsForCategory, type CategoryId } from "./topics";

// Presentation vocabulary only: the existing public offering types stay canonical.
export const finderFormats = [
  { id: "coaching", label: "Coaching" }, { id: "workshop", label: "Workshop" },
  { id: "lecture", label: "Vortrag" }, { id: "program", label: "Programm" },
  { id: "individual", label: "Individuelles Format" },
] as const;
export const finderAudiences = [
  { id: "companies", label: "Unternehmen und Teams" },
  { id: "leaders", label: "Führungskräfte" },
  { id: "private", label: "Privatpersonen" },
  { id: "entrepreneurs", label: "Unternehmerinnen" },
] as const;
export type FinderFormatId = (typeof finderFormats)[number]["id"];
export type FinderAudienceId = (typeof finderAudiences)[number]["id"];
export type FinderTopicId = (typeof topics)[number]["id"];
export interface FinderFormat {
  id: string; title: string; kind: FinderFormatId; description: string | null;
  duration: Duration | null; audiences: FinderAudienceId[]; topics: FinderTopicId[];
}
export interface FinderEntry {
  id: string; title: string; description: string | null;
  coach: { name: string; profilePath: string; image?: string };
  formats: FinderFormat[]; options: readonly string[]; boundaries: readonly string[];
}
export interface FinderSelection {
  query: string; audience: string; category: CategoryId | "all";
  topics: string[]; format: string;
}
export const emptyFinderSelection = (): FinderSelection => ({
  query: "", audience: "all", category: "all", topics: [], format: "all",
});
export const normalizeFinderText = (value: string) => value.normalize("NFD")
  .replace(/\p{Diacritic}/gu, "").toLocaleLowerCase("de-DE").replace(/ß/g, "ss");

// Match all dimensions on ONE format, not unrelated siblings within a family.
export function filterFinder(entries: readonly FinderEntry[], selection: FinderSelection) {
  const available = new Set(topicsForCategory(selection.category).map((topic) => topic.id));
  const terms = normalizeFinderText(selection.query.trim().slice(0, 80)).split(/\s+/).filter(Boolean);
  return entries.flatMap((entry) => {
    const formats = entry.formats.filter((format) => {
      const search = normalizeFinderText([entry.title, entry.description, entry.coach.name,
        format.title, format.description,
        ...topics.filter((topic) => format.topics.includes(topic.id)).map((topic) => topic.label),
      ].filter(Boolean).join(" "));
      return (selection.audience === "all" || format.audiences.includes(selection.audience as FinderAudienceId))
        && (selection.format === "all" || format.kind === selection.format)
        && (selection.category === "all" || format.topics.some((id) => available.has(id)))
        && (!selection.topics.length || format.topics.some((id) => selection.topics.includes(id) && available.has(id)))
        && terms.every((term) => search.includes(term));
    });
    return formats.length ? [{ entry, formats }] : [];
  });
}

export function finderDuration(duration: Duration | null): string {
  if (!duration) return "Rahmen nach Abstimmung";
  return [duration.label, duration.minutes && `${duration.minutes} Minuten`,
    duration.weeks && `${duration.weeks} Wochen`,
    duration.sessions_per_week && `${duration.sessions_per_week} Termin/Woche`,
    duration.session_minutes && `${duration.session_minutes} Minuten je Termin`].filter(Boolean).join(" · ");
}
