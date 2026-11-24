import { publicElisabethOfferGroups } from "./elisabeth-offers";
import { workshops } from "./susanne-klemm";
import { guelcanOfferFamilies } from "./guelcan-offers";
import { goranOffer } from "./goran-offers";
import { activeCoaches, knownApprovedCoaches } from "../data/coaches";
import type { FinderEntry, FinderFormatId, FinderTopicId } from "./offering-finder-model";

function coach(slug: string) {
  const item = knownApprovedCoaches.find((value) => value.profilePath === `coaches/${slug}`);
  if (!item) throw new Error("Finder requires an approved Coach");
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
const activeElisabeth = publicElisabethOfferGroups.flatMap((group) => group.offers
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

const goran: FinderEntry = {
  id: "goran/rhetorik-vertrieb",
  title: goranOffer.title, description: goranOffer.description,
  coach: coach("goran-celic"), options: [], boundaries: [],
  formats: goranOffer.formats.map((format) => ({
    ...format, id: `goran/rhetorik-vertrieb/${format.id}`,
    description: null, duration: null, audiences: ["companies"], topics: ["rhetorik-vertrieb"],
  })),
};

// Public static adapter only. The UI accepts this view model as props; a later
// validated COACH-4 adapter can supply it without changing the component.
const established: readonly FinderEntry[] = [...guelcan, goran, ...elisabeth, ...susanne];

// The profile text describes these focus areas, not dated or bookable workshops.
const spotlightTopics = [
  { slug: "christian-galvano", id: "neuroleadership", title: "Neuroleadership", topic: "fuehrung" },
  { slug: "christian-galvano", id: "konfliktmanagement", title: "Konfliktmanagement", topic: "teams-konflikte" },
  { slug: "christian-galvano", id: "stresspraevention", title: "Stress- und Burnoutprävention", topic: "gesundheit-praevention" },
  { slug: "manuela-rodriguez", id: "ki-kompetenz", title: "KI-Kompetenz und Verantwortung", topic: "ki-transformation" },
] as const satisfies readonly { slug: string; id: string; title: string; topic: FinderTopicId }[];

const spotlight: FinderEntry[] = spotlightTopics.map(({ slug, id, title, topic }) => ({
  id: `${slug}/${id}`, title, description: null, coach: coach(slug), options: [], boundaries: [],
  formats: [{ id: `${slug}/${id}`, title, kind: "individual", description: null,
    duration: null, audiences: ["companies"], topics: [topic] }],
}));

const visiblePaths = new Set(activeCoaches.map(({ profilePath }) => profilePath));
const catalogue = import.meta.env.PUBLIC_REVIEW_MODE === "true"
  ? [...spotlight, ...established] : established;
export const finderEntries = catalogue.filter(({ coach }) => visiblePaths.has(coach.profilePath));
