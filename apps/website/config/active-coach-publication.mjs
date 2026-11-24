// Retained publication rights from 19.11, not a list of who appears in each release.
export const approvedCoachProfiles = Object.freeze([
  { slug: "christian-galvano", portrait: "christian-galvano.webp" },
  { slug: "manuela-rodriguez", portrait: "manuela-rodriguez.webp" },
  { slug: "guelcan-elmas-brandes", portrait: "guelcan-elmas-brandes.png", injected: true },
  { slug: "elisabeth-schwabauer", portrait: "elisabeth-schwabauer.webp", injected: true },
  { slug: "goran-celic", portrait: "goran-celic.png", injected: true },
  { slug: "stefanie-becker", portrait: "stefanie-becker.webp", injected: true },
  { slug: "wegner-ney", portrait: "wegner-ney.jpg", injected: true },
  { slug: "susanne-klemm", portrait: "susanne-klemm.webp", injected: true },
].map((profile) => Object.freeze(profile)));

export const pausedCoachSlugs = Object.freeze(["carolin-hupp"]);

// Stage a campaign here. Production keeps its existing scope until separately released.
const rollout = Object.freeze({
  preview: ["christian-galvano", "manuela-rodriguez"],
  production: approvedCoachProfiles.map(({ slug }) => slug),
});
export const featuredCoachSlugs = Object.freeze(["christian-galvano", "manuela-rodriguez"]);

export function coachProfilesFor(mode, selection = rollout[mode]) {
  if (!Object.hasOwn(rollout, mode) || !Array.isArray(selection)
    || new Set(selection).size !== selection.length) {
    throw new Error("Invalid Coach rollout selection");
  }
  return Object.freeze(selection.map((slug) => {
    const profile = approvedCoachProfiles.find((entry) => entry.slug === slug);
    if (!profile || pausedCoachSlugs.includes(slug)) throw new Error("Unapproved or paused Coach in rollout");
    return profile;
  }));
}
