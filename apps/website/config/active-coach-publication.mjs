// 19.11.2026: only the eight existing, active profiles and their existing portraits.
// A new source profile, image or offering is not approved by adding it to a directory.
export const activeCoachProfiles = Object.freeze([
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
