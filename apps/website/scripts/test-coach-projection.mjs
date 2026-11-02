import assert from "node:assert/strict";
import { test } from "node:test";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, writeFileSync, symlinkSync, truncateSync, readdirSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { adaptProjection, loadProjection, coachProjectionIntegration, durationLabel, assertProjectionOutput } from "../config/coach-projection.mjs";

const root = fileURLToPath(new URL("../../../.tmp/coach4", import.meta.url));
mkdirSync(root, { recursive: true });
const folder = mkdtempSync(resolve(root, "website-unit-"));
const buildRoot = fileURLToPath(new URL("../.tmp/coach4", import.meta.url));
mkdirSync(buildRoot, { recursive: true });
const buildFolder = mkdtempSync(resolve(buildRoot, "website-output-unit-"));
const boundary = { text: "No therapy <script>window.unsafe=true</script>", excluded_services: ["psychotherapy"] };
const duration = { clock_start: "09:00", clock_end: "10:30", weeks: 2, sessions_per_week: 1, session_minutes: 90, label: "Synthetic" };
const variant = { kind: "option", title: "Optional <b>text</b>", description: "Not HTML", duration };
const offer = { title: "Workshop", type: "workshop", description: "Public short copy", ordering: 1,
  service_domains: ["training"], bookable: false, duration, delivery_mode: "live_unspecified", delivery_label: null,
  target_groups: ["Teams"], target_focus: ["Practice"], program_modules: ["Module"], boundaries: [boundary], variants: [variant] };
export function fixture() {
  return structuredClone({ schema: 1, environment: "preview", coaches: [{
    display_name: "Synthetic <img src=x onerror=alert(1)>", academic_suffix: null,
    short_intro: "Intro & safety", description: "Description", professional_background: "Background",
    target_groups: ["Teams"], profile_path: "/coaches/synthetic-alpha/", competencies: ["Listening"],
    topics: [{ name: "Topic <text>", categories: ["personalentwicklung", "karrierecoaching"] }], assets: [], offerings: [offer],
    roles: [{ code: "coach", label: "Coach" }], qualifications: [{ label: "Explicit label", issuer: null, type: null }],
    boundaries: [boundary], offering_families: [{ title: "Family", description: null, target_groups: [], target_focus: [], service_domains: ["training"], boundaries: [boundary], variants: [variant], formats: [offer] }],
    presentation: { teaser: null, focus_labels: [], background_labels: [], languages: ["Deutsch"],
      sections: [{ kind: "profile", headings: ["Heading"], paragraphs: ["<script>literal</script>"] }],
      topic_cards: [{ title: "Card", text: "Text" }], quote: "Quote", external_links: [{ label: "Reference", url: "https://example.invalid/" }],
      initials: null, portrait_width: null, portrait_height: null },
  }] });
}
function saved(value = fixture(), name = "input.json") {
  const path = resolve(folder, name);
  writeFileSync(path, JSON.stringify(value));
  return path;
}
test("default integration is entirely absent; an orphan asset opt-in fails", () => {
  assert.equal(coachProjectionIntegration({ mode: "production" }, {}), null);
  assert.throws(() => coachProjectionIntegration({ mode: "preview" }, { COACH_PROJECTION_ASSET_ROOT: folder }));
});
test("exact public target maps without inferred roles, qualifications or portrait", () => {
  const source = fixture();
  const [coach] = adaptProjection(source, "preview");
  assert.equal(coach.route, "/projected-coaches/synthetic-alpha/");
  assert.deepEqual(coach.qualifications, source.coaches[0].qualifications);
  assert.equal(coach.assets.length, 0);
  assert.equal(coach.offerings[0].bookable, false);
  assert.equal(coach.offering_families[0].formats.length, 1);
  assert.match(coach.display_name, /<img/);
  coach.roles[0].label = "Changed";
  assert.equal(source.coaches[0].roles[0].label, "Coach");
});
test("legacy projection remains supported, empty artifact is valid", () => {
  const source = fixture();
  for (const field of ["roles", "qualifications", "boundaries", "offering_families", "presentation"]) delete source.coaches[0][field];
  source.coaches[0].offerings = [{ title: "Legacy", type: "other", description: null, ordering: 0 }];
  const [coach] = adaptProjection(source, "preview");
  assert.equal(coach.roles, undefined);
  assert.deepEqual(adaptProjection({ schema: 1, environment: "production", coaches: [] }, "production"), []);
});
test("all nested object levels reject unknown fields including private metadata", () => {
  const paths = [];
  function visit(value, path = []) {
    if (Array.isArray(value)) value.forEach((v, i) => visit(v, [...path, i]));
    else if (value && typeof value === "object") {
      paths.push(path);
      Object.entries(value).forEach(([k, v]) => visit(v, [...path, k]));
    }
  }
  visit(fixture());
  for (const path of paths) for (const field of ["internal_note", "__proto__", "constructor", "price", "uuid"]) {
    const source = fixture();
    const target = path.reduce((v, key) => v[key], source);
    Object.defineProperty(target, field, { value: "must not publish", enumerable: true });
    assert.throws(() => adaptProjection(source, "preview"), `accepted ${path.join(".")}.${field}`);
  }
});
test("mode/schema/type mismatch, missing required and partial rich fields fail closed", () => {
  for (const value of [null, [], {}, { ...fixture(), schema: "1" }, { ...fixture(), environment: "production" }]) assert.throws(() => adaptProjection(value, "preview"));
  for (const change of [(c) => { delete c.short_intro; }, (c) => { c.roles = null; }, (c) => { delete c.qualifications; },
    (c) => { c.offerings[0].bookable = "false"; }, (c) => { c.presentation.portrait_width = 0; },
    (c) => { c.topics[0].categories = ["admin"]; }, (c) => { c.offerings[0].duration.clock_end = "08:00"; }]) {
    const source = fixture(); change(source.coaches[0]); assert.throws(() => adaptProjection(source, "preview"));
  }
});
test("unsafe or duplicate profile routes and asset filename injections fail", () => {
  for (const path of ["/coaches/../", "/coaches/UPPER/", "/coaches/a%2fb/", "/coaches/a/?x", "https://host/", "/coaches/a\\b/", "/coaches/a/\n"]) {
    const source = fixture(); source.coaches[0].profile_path = path; assert.throws(() => adaptProjection(source, "preview"));
  }
  const duplicate = fixture(); duplicate.coaches.push(duplicate.coaches[0]); assert.throws(() => adaptProjection(duplicate, "preview"));
  for (const reference of ["../x.png", "images/coaches/../x.png", "images/coaches/X.png", "images/coaches/x.svg", "images/coaches/x.png?y", "images/coaches/x.png\n"]) {
    const source = fixture(); source.coaches[0].assets = [{ type: "portrait", reference, sha256: "a".repeat(64), alt_text: "Test" }];
    assert.throws(() => adaptProjection(source, "preview"));
  }
});
test("external URLs are HTTPS without credentials, never executable URL text", () => {
  for (const url of ["javascript:alert(1)", "data:text/html,test", "http://example.invalid", "//example.invalid", "https://user:pass@example.invalid/", "https://example.invalid/\"x", "https://example.invalid/\\x"]) {
    const source = fixture(); source.coaches[0].presentation.external_links[0].url = url;
    assert.throws(() => adaptProjection(source, "preview"));
  }
});
test("psychotherapy is separate and never bookable", () => {
  for (const change of [(o) => { o.bookable = true; }, (o) => { o.type = "coaching"; }, (o) => { o.service_domains.push("coaching"); }]) {
    const source = fixture(); source.coaches[0].offerings[0].service_domains = ["psychotherapy"];
    change(source.coaches[0].offerings[0]); assert.throws(() => adaptProjection(source, "preview"));
  }
});
test("bounded artifact shape rejects oversized arrays/text, invalid durations", () => {
  const source = fixture(); source.coaches[0].display_name = "x".repeat(201); assert.throws(() => adaptProjection(source, "preview"));
  source.coaches = Array(501).fill(fixture().coaches[0]); assert.throws(() => adaptProjection(source, "preview"));
  assert.equal(durationLabel({ weeks: 2, sessions_per_week: 1, session_minutes: 60 }), "2 Wochen · 1 Termine/Woche · 60 Min./Termin");
});
test("local file names/extension, paths outside approved workspace and wrong mode reject", () => {
  assert.equal(loadProjection(saved(), "preview", folder).coaches.length, 1);
  for (const path of [saved(fixture(), "input.txt"), saved(fixture(), "UPPER.json"), resolve(folder, "../missing.json"), "https://example.invalid/input.json"]) assert.throws(() => loadProjection(path, "preview", folder));
  assert.throws(() => loadProjection(saved(), "production", folder));
  const path = resolve(folder, "malformed.json"); writeFileSync(path, "{"); assert.throws(() => loadProjection(path, "preview", folder));
});
test("exact local portrait bytes are frozen and mismatches/missing assets reject", () => {
  const assets = resolve(folder, "assets"); mkdirSync(resolve(assets, "images/coaches"), { recursive: true });
  const bytes = Buffer.from("synthetic asset bytes");
  const source = fixture();
  source.coaches[0].assets = [{ type: "portrait", reference: "images/coaches/alpha.png", sha256: createHash("sha256").update(bytes).digest("hex"), alt_text: "Synthetic" }];
  const file = saved(source); const image = resolve(assets, "images/coaches/alpha.png");
  assert.throws(() => loadProjection(file, "preview", assets));
  writeFileSync(image, bytes);
  const loaded = loadProjection(file, "preview", assets);
  writeFileSync(image, "changed");
  assert.deepEqual(loaded.assets.get("images/coaches/alpha.png"), bytes);
  assert.throws(() => loadProjection(file, "preview", assets));
});
test("symlink or junction input and asset root are rejected", () => {
  const linked = resolve(folder, "linked"); symlinkSync(folder, linked, "junction");
  assert.throws(() => loadProjection(resolve(linked, "input.json"), "preview", folder));
});
test("duplicate JSON keys, including escaped keys, reject at every depth", () => {
  for (const source of [JSON.stringify(fixture()).replace('"schema":1', '"schema":2,"schema":1'),
    JSON.stringify(fixture()).replace('"label":"Coach"', '"la\\u0062el":"First","label":"Coach"')]) {
    const file = resolve(folder, "duplicate.json"); writeFileSync(file, source);
    assert.throws(() => loadProjection(file, "preview", folder));
  }
});
test("portrait over 20 MiB is rejected before reading its bytes", () => {
  const source = fixture();
  const image = resolve(folder, "assets/images/coaches/huge.png");
  writeFileSync(image, ""); truncateSync(image, 20 * 1024 * 1024 + 1);
  source.coaches[0].assets = [{ type: "portrait", reference: "images/coaches/huge.png", sha256: "a".repeat(64), alt_text: "Synthetic" }];
  assert.throws(() => loadProjection(saved(source), "preview", resolve(folder, "assets")));
});
test("integration is build-only and injects two isolated routes, virtual JSON only", () => {
  const integration = coachProjectionIntegration({ mode: "preview" }, { COACH_PROJECTION_FILE: saved(), COACH_PROJECTION_ASSET_ROOT: folder });
  assert.throws(() => integration.hooks["astro:config:setup"]({ command: "dev" }));
  const routes = []; let updated;
  integration.hooks["astro:config:setup"]({ command: "build", injectRoute: (r) => routes.push(r), updateConfig: (v) => { updated = v; } });
  assert.deepEqual(routes.map((r) => r.pattern), ["/projected-coaches", "/projected-coaches/[slug]"]);
  const plugin = updated.vite.plugins[0];
  assert.match(plugin.load(plugin.resolveId("virtual:coach-projection")), /^export const coaches = /);
  assert.throws(() => integration.hooks["astro:config:done"]({ config: { outDir: new URL("../dist/", import.meta.url) } }));
});
test("output confinement rejects actual junction ancestors before any write or empty operation", () => {
  const target = resolve(folder, "untouched-output-target"); mkdirSync(target);
  writeFileSync(resolve(target, "sentinel.txt"), "must remain");
  const link = resolve(buildFolder, "output-junction"); symlinkSync(target, link, "junction");
  const integration = coachProjectionIntegration({ mode: "preview" }, { COACH_PROJECTION_FILE: saved(), COACH_PROJECTION_ASSET_ROOT: folder });
  for (const path of [link, resolve(link, "not-yet-created/site"), resolve(folder, "linked/site")]) {
    assert.throws(() => integration.hooks["astro:config:done"]({ config: { outDir: pathToFileURL(path + "/") } }));
  }
  assert.deepEqual(readdirSync(target), ["sentinel.txt"]);
  assertProjectionOutput(resolve(buildFolder, "safe-not-created/site"));
  assert.throws(() => assertProjectionOutput(resolve(folder, "outside-cwd/site")));
  assert.throws(() => execFileSync(process.execPath, [fileURLToPath(new URL("../node_modules/astro/astro.js", import.meta.url)),
    "build", "--outDir", resolve(link, "escape-site")], {
    cwd: fileURLToPath(new URL("../", import.meta.url)),
    env: { ...process.env, ASTRO_TELEMETRY_DISABLED: "1", WEBSITE_ENV: "preview", COACH_PROJECTION_FILE: saved(), COACH_PROJECTION_ASSET_ROOT: folder },
    stdio: "pipe",
  }), (error) => error.status === 1 && (error.stdout.toString() + error.stderr.toString()).includes("astro:config:done"));
  assert.deepEqual(readdirSync(target), ["sentinel.txt"]);
});
