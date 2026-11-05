import { offerGroups } from "./elisabeth-offers";
import { workshops } from "./susanne-klemm";
import { guelcanOfferFamilies } from "./guelcan-offers";
import { coaches } from "./coaches";
import type { FinderEntry, FinderFormatId, FinderTopicId } from "./offering-finder-model";

function coach(slug: string) {
  const item = coaches.find((value) => value.profilePath === `coaches/${slug}`);
  if (!item || item.kind !== "approved") throw new Error("Finder requires an approved public Coach");
  return { name: item.name, profilePath: item.profilePath, image: item.image };
}

// Editorial navigation against existing public titles, never qualifications.
// Unknown durations and delivery modes intentionally remain unknown.
const health: FinderTopicId[] = ["gesundheit-praevention"];
const elisabethTopics: FinderTopicId[][] = [
  ["gesundheit-praevention", "fuehrung"], ["fuehrung"], health,
  health, ["gesundheit-praevention", "fuehrung"], health, health, health, health, health,
  ["teams-konflikte"], health, ["psychologische-beratung"], health, ["teams-konflikte"],
  ["psychologische-beratung"],
];
const activeElisabeth = offerGroups.flatMap((group) => group.offers
  .filter((title) => title !== "Psychotherapie (HeilprG)")
  .map((title) => ({ title, group: group.id })));
const types: Record<string, FinderFormatId> = {
  vortraege: "lecture", workshops: "workshop", individuell: "individual", weitere: "coaching",
};
const elisabeth: FinderEntry[] = activeElisabeth.map((offer, index) => ({
  id: `elisabeth/${offer.group}/${index}`, title: offer.title, description: null,
  coach: coach("elisabeth-schwabauer"), options: [],
  boundaries: ["Coaching und berufliche Beratung ersetzen keine medizinische Beratung oder akute Krisenversorgung. Über den Competence Hub wird derzeit keine Psychotherapie angeboten."],
  formats: [{ id: `elisabeth/${offer.group}/${index}`, title: offer.title, kind: types[offer.group],
    description: null, duration: null, audiences: ["companies", "leaders"], topics: elisabethTopics[index] }],
}));
const susanneTopics: FinderTopicId[][] = [
  ["teams-konflikte"], ["teams-konflikte"], ["teams-konflikte"], ["fuehrung"],
  health, ["fuehrung"], ["fuehrung"], ["teams-konflikte"],
];
if (activeElisabeth.length !== elisabethTopics.length || workshops.length !== susanneTopics.length) {
  throw new Error("Changed public offering scope requires reviewed navigation metadata");
}
const susanne: FinderEntry[] = workshops.map((title, index) => ({
  id: `susanne/workshop/${index}`, title, description: null,
  coach: coach("susanne-klemm"), options: [], boundaries: [],
  formats: [{ id: `susanne/workshop/${index}`, title, kind: "workshop", description: null,
    duration: null, audiences: ["companies", "leaders"], topics: susanneTopics[index] }],
}));
const guelcan: FinderEntry[] = guelcanOfferFamilies.map((family, index) => ({
  id: family.key, title: family.title, description: family.audience,
  coach: coach("guelcan-elmas-brandes"), options: family.options, boundaries: [family.boundary],
  formats: family.formats.map((format) => ({
    id: format.key, title: format.title, description: format.detail,
    kind: format.key === "business-balance/six-weeks" ? "program"
      : format.key === "teamreflexion/series" ? "individual" : "workshop",
    duration: format.key === "business-balance/six-weeks"
      ? { weeks: 6, sessions_per_week: 1, session_minutes: 60 }
      : format.key === "gesundheit/half-day" ? { minutes: 240 }
        : format.key.endsWith("/day") ? { label: "Tagesworkshop" } : null,
    audiences: index === 0 ? ["companies", "entrepreneurs"] : ["companies"],
    topics: index === 0 ? ["fuehrung", "gesundheit-praevention"]
      : index === 1 ? ["gesundheit-praevention"] : ["teams-konflikte"],
  })),
}));

// Public static adapter only. The UI accepts this view model as props; a later
// validated COACH-4 adapter can supply it without changing the component.
export const finderEntries: readonly FinderEntry[] = [...guelcan, ...elisabeth, ...susanne];
