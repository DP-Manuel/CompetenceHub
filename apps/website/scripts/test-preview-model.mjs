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
