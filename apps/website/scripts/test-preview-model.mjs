import assert from "node:assert/strict";
import { after, test } from "node:test";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { createServer } from "vite";
import { websiteEnvironment } from "../config/environment.mjs";

const vite = await createServer({
  configFile: false, envDir: false,
  server: { middlewareMode: true },
  optimizeDeps: { noDiscovery: true },
});
after(() => vite.close());
const { coaches } = await vite.ssrLoadModule("/src/preview/coaches.ts");
const { coaches: production } = await vite.ssrLoadModule("/src/data/coaches.ts");
const { categories, topics, topicsForCategory } = await vite.ssrLoadModule("/src/preview/topics.ts");
const { offerGroups } = await vite.ssrLoadModule("/src/preview/elisabeth-offers.ts");
const { susanneKlemm, workshops, qualifications } = await vite.ssrLoadModule("/src/preview/susanne-klemm.ts");
const { guelcanOfferFamilies } = await vite.ssrLoadModule("/src/preview/guelcan-offers.ts");
const { publicOfferKeywords } = await vite.ssrLoadModule("/src/preview/coach-discovery.ts");
const { coachRequestMailto } = await vite.ssrLoadModule("/src/preview/request-links.ts");
const { finderEntries } = await vite.ssrLoadModule("/src/preview/offering-finder-data.ts");
const { filterFinder, emptyFinderSelection, finderFormats, finderAudiences, finderDuration } = await vite.ssrLoadModule("/src/preview/offering-finder-model.ts");
const slugs = ["carolin-hupp", "elisabeth-schwabauer", "goran-celic",
  "guelcan-elmas-brandes", "stefanie-becker", "wegner-ney", "susanne-klemm"];

test("one validated mode controls host, base and artifact, rejecting legacy drift", () => {
  assert.equal(websiteEnvironment({}).mode, "production");
  assert.equal(websiteEnvironment({ WEBSITE_ENV: "preview" }).base, "/CompetenceHub");
  for (const mode of ["", "staging", "PREVIEW"]) {
    assert.throws(() => websiteEnvironment({ WEBSITE_ENV: mode }));
  }
  assert.throws(() => websiteEnvironment({ PUBLIC_REVIEW_MODE: "true" }));
  assert.throws(() => websiteEnvironment({ WEBSITE_ENV: "preview", GITHUB_PAGES_REVIEW: "false" }));
  assert.throws(() => websiteEnvironment({ WEBSITE_ENV: "preview", PUBLIC_REVIEW_MODE: "false" }));
});
test("preview real Coach records and detail templates agree; production remains unchanged", () => {
  assert.deepEqual(new Set(coaches.map((coach) => coach.profilePath)),
    new Set([...production.filter((coach) => coach.kind === "approved").map((coach) => coach.profilePath), ...slugs.map((slug) => `coaches/${slug}`)]));
  assert.equal(new Set(coaches.map((coach) => coach.profilePath)).size, coaches.length);
  assert.ok(coaches.every((coach) => coach.kind === "approved"));
  assert.equal(production.filter((coach) => coach.kind === "approved").length, 2);
  assert.equal(production.filter((coach) => coach.kind === "demo").length, 6);
});

test("Susanne uses approved workshops and qualification scope, not inferred academic or mediation credentials", () => {
  assert.equal(susanneKlemm.profilePath, "coaches/susanne-klemm");
  assert.deepEqual(susanneKlemm.topics, ["fuehrung", "teams-konflikte", "gesundheit-praevention"]);
  assert.equal(workshops.length, 8);
  assert.equal(qualifications.length, 8);
  assert.ok(qualifications.includes("Weiterbildung „Systemische Supervision kompakt“ (44 Zeitstunden)"));
  assert.ok(!JSON.stringify({ susanneKlemm, qualifications }).match(/DGSv|Mediatorin|Diplom|M\.Sc\./));
  assert.ok(!production.some((coach) => coach.profilePath === susanneKlemm.profilePath));
});
test("latest explicit spelling preserves the historical route; Carolin has no invented portrait", () => {
  const elisabeth = coaches.find((coach) => coach.profilePath === "coaches/elisabeth-schwabauer");
  assert.equal(elisabeth.name, "Frau Elisabeth Schwabauer");
  assert.ok(!JSON.stringify(coaches).includes("Schabbauer"));
  assert.equal(coaches.find((coach) => coach.profilePath === "coaches/carolin-hupp").image, undefined);
});
test("three real categories, unique canonical topics, computed All and many-to-many membership", () => {
  assert.deepEqual(categories.map((category) => category.id),
    ["personalentwicklung", "persoenlichkeitsentwicklung", "karrierecoaching"]);
  assert.equal(new Set(topics.map((topic) => topic.id)).size, topics.length);
  assert.deepEqual(topicsForCategory("all"), topics);
  for (const topic of topics) {
    assert.ok(topic.categories.length > 0);
    assert.equal(new Set(topic.categories).size, topic.categories.length);
    assert.ok(topic.categories.every((id) => categories.some((category) => category.id === id)));
  }
  const health = topics.find((topic) => topic.id === "gesundheit-praevention");
  assert.ok(health.categories.includes("personalentwicklung"));
  assert.ok(health.categories.includes("persoenlichkeitsentwicklung"));
  assert.ok(topicsForCategory("personalentwicklung").includes(health));
  assert.ok(topicsForCategory("persoenlichkeitsentwicklung").includes(health));
});
test("Coach topics reference canonical themes; Mediation remains qualification-gated", () => {
  for (const coach of coaches) assert.ok(coach.topics.every((id) => topics.some((topic) => topic.id === id)));
  assert.ok(coaches.every((coach) => !coach.topics.includes("mediation")));
});
test("supplied offers remain four separate formats with exactly 3/7/5/2 titles", () => {
  assert.deepEqual(offerGroups.map((group) => group.offers.length), [3, 7, 5, 2]);
  assert.equal(offerGroups[0].offers[1], "Positive Leadership – Mitarbeiter stärken und Potenziale entfalten");
  assert.equal(offerGroups[2].offers[4], "Kurzanalyse im Team (KiT)");
  assert.deepEqual(offerGroups[3].offers, ["Coaching", "Psychotherapie (HeilprG)"]);
});
test("all five restored portrait bytes match approved Git snapshot 53a89a8", () => {
  const blobs = {
    "elisabeth-schwabauer.webp": "86a1e3047d1e7bfcbe3473816b57d906ff348ced",
    "goran-celic.png": "adbcd760a9aa7d3abb242af9979ea8ac45b34032",
    "guelcan-elmas-brandes.png": "971aacc0c4ca119e601126adcec8126f4efe0847",
    "stefanie-becker.webp": "cb22ac2450f56a273b8849f47db8915076b6323c",
    "wegner-ney.jpg": "a48c43610caefc4c5b0e2dd71756f78ca30d542e",
  };
  for (const [file, blob] of Object.entries(blobs)) {
    const path = fileURLToPath(new URL(`../src/preview/portraits/${file}`, import.meta.url));
    assert.equal(execFileSync("git", ["hash-object", path], { encoding: "utf8" }).trim(), blob);
  }
});
test("restored templates are outside production pages and suppress non-existent canonicals", () => {
  for (const slug of slugs) {
    const source = readFileSync(new URL(`../src/preview/profiles/${slug}.astro`, import.meta.url), "utf8");
    assert.match(source, /canonical=\{false\}/);
  }
});

test("Guelcan approved short copy keeps three families, five formats and five non-bookable options", () => {
  assert.deepEqual(guelcanOfferFamilies.map((family) => family.key), [
    "family/business-balance", "family/gesundheit-im-unternehmensalltag", "family/konfliktklaerung-teamreflexion",
  ]);
  assert.deepEqual(guelcanOfferFamilies.map((family) => family.formats.length), [2, 1, 2]);
  assert.deepEqual(guelcanOfferFamilies.map((family) => family.options.length), [1, 4, 0]);
  assert.equal(new Set(guelcanOfferFamilies.flatMap((family) => family.formats.map((format) => format.key))).size, 5);
  assert.ok(guelcanOfferFamilies.every((family) => family.boundary.length > 60));
  assert.match(guelcanOfferFamilies[2].boundary, /keine Mediation.*Supervision.*Rechtsberatung/);
  assert.match(guelcanOfferFamilies[1].boundary, /keine ärztliche Behandlung.*Diagnostik.*Ernährungstherapie/);
  const series = guelcanOfferFamilies[2].formats[1];
  assert.equal(series.title, "Reflexionsreihe");
  assert.ok(!/\d/.test(series.detail), "unknown duration/frequency must not be invented");
  assert.ok(!JSON.stringify(guelcanOfferFamilies).match(/https?:|€|\bEUR\b|2026-|bookable/));
  assert.ok(!production.some((coach) => coach.profilePath === "coaches/guelcan-elmas-brandes"));
});

test("discovery uses only approved public active offers, never the held Becker or psychotherapy candidates", () => {
  assert.ok(publicOfferKeywords("coaches/elisabeth-schwabauer").includes("Positive Leadership – Mitarbeiter stärken und Potenziale entfalten"));
  assert.ok(!publicOfferKeywords("coaches/elisabeth-schwabauer").includes("Psychotherapie (HeilprG)"));
  assert.deepEqual(publicOfferKeywords("coaches/susanne-klemm"), workshops);
  assert.ok(publicOfferKeywords("coaches/guelcan-elmas-brandes").includes("Business & Balance"));
  assert.deepEqual(publicOfferKeywords("coaches/stefanie-becker"), []);
  assert.deepEqual(publicOfferKeywords("coaches/unknown"), []);
});

test("request links retain Coach/format context as an encoded mail draft, with no submission endpoint", () => {
  const coach = "Frau Gülcan Elmas-Brandes";
  const offering = "Business & Balance · 6-Wochen-Vertiefungsprogramm";
  const link = new URL(coachRequestMailto(coach, offering));
  assert.equal(link.protocol, "mailto:");
  assert.equal(link.pathname, "competencehub@donner-partner.de");
  assert.equal(link.searchParams.get("subject"), `Anfrage: ${offering} · ${coach}`);
  assert.match(link.searchParams.get("body"), /Angebot \/ Format: Business & Balance/);
  assert.ok(link.searchParams.get("body").includes(coach));
  assert.equal(new URL(coachRequestMailto(coach)).searchParams.get("subject"), `Coaching-Anfrage: ${coach}`);
  assert.ok(!link.href.includes("undefined"));
});

test("finder includes exactly approved 27 entries and 29 formats for three explicitly supplied offering lists", () => {
  assert.equal(finderEntries.length, 27);
  assert.equal(finderEntries.flatMap((entry) => entry.formats).length, 29);
  assert.deepEqual([...new Set(finderEntries.map((entry) => entry.coach.profilePath))].sort(), [
    "coaches/elisabeth-schwabauer", "coaches/guelcan-elmas-brandes", "coaches/susanne-klemm",
  ]);
  const titles = finderEntries.flatMap((entry) => entry.formats.map((format) => format.title));
  assert.deepEqual(titles, [...guelcanOfferFamilies.flatMap((family) => family.formats.map((format) => format.title)),
    ...offerGroups.flatMap((group) => group.offers).filter((title) => title !== "Psychotherapie (HeilprG)"), ...workshops]);
  assert.equal(new Set(finderEntries.map((entry) => entry.id)).size, 27);
  assert.equal(new Set(finderEntries.flatMap((entry) => entry.formats.map((format) => format.id))).size, 29);
});

test("finder keeps families together and optional variants out of standalone offer counts", () => {
  for (const family of guelcanOfferFamilies) {
    const entry = finderEntries.find((item) => item.id === family.key);
    assert.equal(entry.title, family.title);
    assert.deepEqual(entry.options, family.options);
    assert.deepEqual(entry.formats.map((format) => format.id), family.formats.map((format) => format.key));
    assert.ok(entry.options.every((option) => !finderEntries.some((item) => item.title === option)));
  }
});

test("finder metadata uses existing canonical topics, accepted public formats, and approved profile routes", () => {
  for (const entry of finderEntries) {
    assert.ok(coaches.some((coach) => coach.profilePath === entry.coach.profilePath && coach.name === entry.coach.name));
    for (const format of entry.formats) {
      assert.ok(finderFormats.some((item) => item.id === format.kind));
      assert.ok(format.topics.length > 0 && format.topics.every((id) => topics.some((topic) => topic.id === id)));
      assert.ok(format.audiences.every((id) => finderAudiences.some((audience) => audience.id === id)));
      assert.ok(!format.topics.includes("mediation"));
    }
  }
  assert.ok(finderEntries.some((entry) => entry.formats.some((format) => format.topics.length > 1)));
});

test("finder filters combine audience, category, OR-topics, format and accent-insensitive terms", () => {
  const select = (change) => filterFinder(finderEntries, { ...emptyFinderSelection(), ...change });
  assert.equal(select({}).length, 27);
  assert.deepEqual(select({ audience: "entrepreneurs", format: "program", topics: ["gesundheit-praevention"], category: "personalentwicklung", query: "Gulcan Balance" }).map((match) => match.entry.id), ["family/business-balance"]);
  assert.equal(select({ query: "Klemm", format: "workshop" }).length, 8);
  assert.equal(select({ format: "lecture" }).length, 3);
  const either = select({ topics: ["teams-konflikte", "gesundheit-praevention"] });
  assert.ok(either.length > select({ topics: ["teams-konflikte"] }).length);
  assert.equal(select({ query: "unbekanntxyz" }).length, 0);
  assert.equal(select({ audience: "private" }).length, 0, "no private audience may be invented from an approved biography");
  assert.equal(select({ topics: ["mediation"] }).length, 0);
  assert.equal(select({ query: '<img src=x onerror="alert(1)">' }).length, 0);
});

test("finder never cross-matches different sibling formats and returns only matching formats", () => {
  const source = structuredClone(finderEntries[0]);
  source.formats[0].audiences = ["leaders"];
  source.formats[0].topics = ["fuehrung"];
  source.formats[1].audiences = ["companies"];
  source.formats[1].topics = ["gesundheit-praevention"];
  const mismatch = filterFinder([source], { ...emptyFinderSelection(), audience: "leaders", format: "program" });
  assert.equal(mismatch.length, 0);
  const program = filterFinder(finderEntries, { ...emptyFinderSelection(), format: "program" });
  assert.deepEqual(program[0].formats.map((format) => format.id), ["business-balance/six-weeks"]);
});

test("finder exposes only public fields and preserves unknown duration and clinical boundaries", () => {
  const serialized = JSON.stringify(finderEntries);
  assert.ok(!/source_path|source_key|evidence|revision_id|coach_uuid|review_required|\.pdf|\.docx|password|token|€|\bEUR\b|2026-/i.test(serialized));
  for (const entry of finderEntries) {
    assert.deepEqual(Object.keys(entry).sort(), ["boundaries", "coach", "description", "formats", "id", "options", "title"]);
    assert.ok(!/stefanie|becker/.test(entry.id));
  }
  const elisabeth = finderEntries.filter((entry) => entry.coach.profilePath.endsWith("elisabeth-schwabauer"));
  assert.ok(elisabeth.every((entry) => entry.formats.every((format) => format.duration === null)));
  assert.ok(elisabeth.every((entry) => entry.boundaries.some((text) => text.includes("keine Psychotherapie"))));
  const conflict = finderEntries.find((entry) => entry.id === "family/konfliktklaerung-teamreflexion");
  assert.ok(conflict.boundaries.some((text) => text.includes("keine Mediation")));
  assert.equal(conflict.formats[1].duration, null);
  assert.equal(finderDuration(null), "Rahmen nach Abstimmung");
  assert.equal(finderDuration({ minutes: 240 }), "240 Minuten");
  assert.equal(finderDuration({ weeks: 6, sessions_per_week: 1, session_minutes: 60 }), "6 Wochen · 1 Termin/Woche · 60 Minuten je Termin");
});
