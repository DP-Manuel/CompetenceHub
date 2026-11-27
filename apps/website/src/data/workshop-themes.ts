import { editorialProfileCopy } from "../components/editorial-profile-copy";
import { finderEntries } from "../preview/offering-finder-data";
import { activeCoaches } from "./coaches";

export const workshopDiscoveryPath = "coaches/#workshop-themen";

// Navigation scope only. Titles, copy and publication rights remain in their source data.
const approvedThemes = new Map<string, readonly string[]>([
  ["coaches/christian-galvano", ["neuroleadership", "konfliktmanagement", "stresspraevention"]],
  ["coaches/manuela-rodriguez", ["ki-kompetenz"]],
]);

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
      return topic ? [{ ...topic, id, path: `${coach.profilePath}/angebote/${id}/` }] : [];
    });

    return copy && themes.length ? [{ coach, copy, slug, themes }] : [];
  })
  : [];

export type WorkshopProfile = (typeof workshopProfiles)[number];
export type WorkshopTheme = WorkshopProfile["themes"][number];
