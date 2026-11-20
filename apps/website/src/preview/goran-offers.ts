import type { FinderFormatId } from "./offering-finder-model";

// Same existing profile copy in the Finder and on the profile. These are
// formats by arrangement, not bookable events or newly titled workshops.
export const goranOffer = {
  title: "Rhetorik & Vertriebscoaching",
  description: "Zielgruppe, Ausgangslage und gewünschte Wirkung bestimmen den passenden Rahmen.",
  formats: [
    { id: "lecture", kind: "lecture", title: "Impulsvortrag" },
    { id: "workshop", kind: "workshop", title: "Workshop" },
    { id: "coaching", kind: "coaching", title: "Coaching" },
    { id: "individual", kind: "individual", title: "Firmenspezifisches Konzept" },
  ] satisfies { id: string; kind: FinderFormatId; title: string }[],
};
