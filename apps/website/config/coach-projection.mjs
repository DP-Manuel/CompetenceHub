import { createHash } from "node:crypto";
import { lstatSync, readFileSync, realpathSync, statSync } from "node:fs";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, basename, isAbsolute, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import ts from "typescript";

const website = fileURLToPath(new URL("../", import.meta.url));
const localRoot = resolve(website, "../../.tmp/coach4");
const localBuildRoot = resolve(website, ".tmp/coach4");
const fail = () => { throw new Error("Invalid local Coach projection (schema, environment, path or asset)."); };
const text = (max, min = 0) => (v) => typeof v === "string" && v.length >= min && v.length <= max && !/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/u.test(v);
const nullable = (check) => (v) => v === null || check(v);
const optional = (check) => Object.assign((v) => v === undefined || check(v), { optional: true });
const integer = (min, max) => (v) => Number.isInteger(v) && v >= min && v <= max;
const choice = (...values) => (v) => values.includes(v);
const match = (pattern) => (v) => typeof v === "string" && v.match(pattern)?.[0] === v;
const array = (check, max) => (v) => Array.isArray(v) && v.length <= max && v.every(check);
const object = (fields) => (v) => v !== null && typeof v === "object" && !Array.isArray(v)
  && Object.keys(v).every((key) => Object.hasOwn(fields, key))
  && Object.entries(fields).every(([key, check]) => (Object.hasOwn(v, key) || check.optional) && check(v[key]));
const labels = (max, length = 250) => array(text(length, 1), max);
const key = match(/^[a-z0-9][a-z0-9/_-]{0,119}$/);
const domains = array(choice("coaching", "consulting", "psychotherapy", "training", "moderation", "health_promotion"), 6);
const category = choice("personalentwicklung", "persoenlichkeitsentwicklung", "karrierecoaching");
export const categoryLabels = Object.freeze({
  personalentwicklung: "Personalentwicklung",
  persoenlichkeitsentwicklung: "Pers\u00f6nlichkeitsentwicklung",
  karrierecoaching: "Karrierecoaching",
});
const boundary = object({ text: text(2000, 1), excluded_services: array(match(/^[a-z_]{1,80}$/), 15) });
const durationShape = object({
  clock_start: optional(match(/^(?:[01][0-9]|2[0-3]):[0-5][0-9]$/)),
  clock_end: optional(match(/^(?:[01][0-9]|2[0-3]):[0-5][0-9]$/)),
  minutes: optional(integer(1, 10080)), weeks: optional(integer(1, 104)),
  sessions_per_week: optional(integer(1, 14)), session_minutes: optional(integer(1, 1440)),
  label: optional(text(250)),
});
const duration = (v) => durationShape(v) && Boolean(v.clock_start) === Boolean(v.clock_end)
  && (!v.clock_start || v.clock_start < v.clock_end)
  && (!(v.sessions_per_week || v.session_minutes) || Boolean(v.weeks));
const variant = object({ kind: choice("variant", "add_on", "option"), title: text(250, 1), description: nullable(text(500)), duration: nullable(duration) });
const offerFields = {
  title: text(250, 1), type: choice("lecture", "workshop", "coaching", "individual", "other"),
  description: nullable(text(2000)), ordering: integer(0, 1000),
};
const richOfferFields = {
  service_domains: domains, bookable: (v) => typeof v === "boolean", duration: nullable(duration),
  delivery_mode: choice("unknown", "online", "in_person", "online_or_in_person", "hybrid", "live_unspecified"),
  delivery_label: nullable(text(250)), target_groups: labels(20, 500), target_focus: labels(20, 500),
  program_modules: labels(30, 500), boundaries: array(boundary, 10), variants: array(variant, 20),
};
const richOfferShape = object({ ...offerFields, ...richOfferFields });
const richOffer = (v) => richOfferShape(v) && (!v.service_domains.includes("psychotherapy")
  || (!v.bookable && v.type !== "coaching" && !v.service_domains.includes("coaching")));
const offering = (v) => object(offerFields)(v) || richOffer(v);
const family = object({
  title: text(250, 1), description: nullable(text(2000)), target_groups: labels(20), target_focus: labels(20),
  service_domains: domains, boundaries: array(boundary, 10), variants: array(variant, 20), formats: array(richOffer, 100),
});
const https = (v) => {
  if (!text(1000, 1)(v) || /[\s<>"\\]/u.test(v)) return false;
  try { const u = new URL(v); return u.protocol === "https:" && Boolean(u.hostname) && !u.username && !u.password; }
  catch { return false; }
};
const presentation = object({
  teaser: nullable(text(1000)), focus_labels: labels(30, 1000), background_labels: labels(50, 1000), languages: labels(10, 1000),
  sections: array(object({ kind: choice("profile", "topics", "background", "formats", "boundary", "contact", "pending"), headings: labels(10, 2000), paragraphs: labels(12, 2000) }), 20),
  topic_cards: array(object({ title: text(250, 1), text: text(2000, 1) }), 20), quote: nullable(text(3000)),
  external_links: array(object({ label: text(250, 1), url: https }), 10), initials: nullable(text(8)),
  portrait_width: nullable(integer(1, 20000)), portrait_height: nullable(integer(1, 20000)),
});
const coach = object({
  display_name: text(200, 1), academic_suffix: nullable(text(100)), short_intro: text(1000, 1),
  description: nullable(text(10000)), professional_background: nullable(text(4000)),
  target_groups: labels(30), profile_path: (v) => text(200)(v) && match(/^\/coaches\/[a-z0-9]+(?:-[a-z0-9]+)*\/$/)(v),
  competencies: labels(50), topics: array(object({ name: text(200, 1), categories: array(category, 3) }), 50),
  assets: array(object({ type: choice("portrait"), reference: (v) => text(200)(v) && match(/^images\/coaches\/[a-z0-9]+(?:[-.][a-z0-9]+)*\.(?:webp|jpg|jpeg|png)$/)(v), sha256: match(/^[a-f0-9]{64}$/), alt_text: text(250, 1) }), 1),
  offerings: array(offering, 100),
  roles: optional(array(object({ code: key, label: text(250, 1) }), 20)),
  qualifications: optional(array(object({ label: text(1000, 1), issuer: nullable(text(250)), type: nullable(text(100)) }), 50)),
  boundaries: optional(array(boundary, 10)), offering_families: optional(array(family, 30)),
  presentation: optional(presentation),
});

// One adapter for the exact public_projection/public_target allowlist, never Admin JSON.
export function adaptProjection(value, environment) {
  if (!["preview", "production"].includes(environment) || !object({ schema: choice(1), environment: choice(environment), coaches: array(coach, 500) })(value)) fail();
  const paths = new Set();
  for (const item of value.coaches) {
    if (paths.has(item.profile_path)) fail();
    paths.add(item.profile_path);
    const rich = ["roles", "qualifications", "boundaries", "offering_families"];
    if (rich.some((field) => Object.hasOwn(item, field)) && !rich.every((field) => Object.hasOwn(item, field))) fail();
    if (item.presentation && !Object.hasOwn(item, "roles")) fail();
  }
  return value.coaches.map((item) => ({
    ...structuredClone(item), slug: item.profile_path.split("/")[2],
    route: `/projected-coaches/${item.profile_path.split("/")[2]}/`,
    initials: item.presentation?.initials || item.display_name.split(/\s+/u).slice(0, 2).map((part) => Array.from(part)[0]).join(""),
  }));
}

export function durationLabel(value) {
  if (!value) return "";
  return [value.label, value.clock_start && `${value.clock_start} - ${value.clock_end}`,
    value.minutes && `${value.minutes} Min.`, value.weeks && `${value.weeks} Wochen`,
    value.sessions_per_week && `${value.sessions_per_week} Termine/Woche`,
    value.session_minutes && `${value.session_minutes} Min./Termin`].filter(Boolean).join(" · ");
}

function inside(root, path) {
  const rel = relative(root, path);
  return rel !== "" && !rel.startsWith("..") && !isAbsolute(rel);
}
function assertUnlinkedTarget(path, root) {
  const full = resolve(path);
  if (!inside(root, full)) throw new Error("Coach projection output must remain in its explicit local workspace.");
  // Check the entire ancestor chain, including the local root, before Astro can empty/write it.
  for (let current = full; ; current = dirname(current)) {
    try {
      if (lstatSync(current).isSymbolicLink()) fail();
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
    if (dirname(current) === current) break;
  }
}
export const assertProjectionOutput = (path) => assertUnlinkedTarget(path, localBuildRoot);
export const assertProjectionArtifactTarget = (path) => assertUnlinkedTarget(path, localRoot);
function localFile(path, root) {
  const full = resolve(path);
  if (!inside(root, full) || !inside(realpathSync(root), realpathSync(full)) || !statSync(full).isFile()) fail();
  for (let current = full; inside(resolve(website, "../.."), current); current = dirname(current)) {
    if (lstatSync(current).isSymbolicLink()) fail();
  }
  return full;
}
function parseProjection(source) {
  const value = JSON.parse(source);
  // JSON.parse establishes grammar; the existing TS JSON AST exposes decoded property names.
  function visit(node) {
    if (ts.isObjectLiteralExpression(node)) {
      const keys = new Set();
      for (const property of node.properties) {
        if (!ts.isPropertyAssignment(property) || !ts.isStringLiteral(property.name)) fail();
        if (keys.has(property.name.text)) fail();
        keys.add(property.name.text);
      }
    }
    ts.forEachChild(node, visit);
  }
  visit(ts.parseJsonText("coach-projection.json", source));
  return value;
}
export function loadProjection(file, environment, assetRoot = resolve(website, "public")) {
  if (typeof file !== "string" || !match(/^[a-z0-9]+(?:[-.][a-z0-9]+)*\.json$/)(basename(file))) fail();
  const full = localFile(file, localRoot);
  if (statSync(full).size > 8 * 1024 * 1024) fail();
  let value;
  try { value = parseProjection(readFileSync(full, "utf8")); } catch { fail(); }
  const coaches = adaptProjection(value, environment);
  const assets = new Map();
  const root = resolve(assetRoot);
  if (root !== resolve(website, "public") && !inside(localRoot, root)) fail();
  for (const coach of coaches) for (const asset of coach.assets) {
    const path = localFile(resolve(root, asset.reference), root);
    if (statSync(path).size > 20 * 1024 * 1024) fail();
    const bytes = readFileSync(path);
    if (createHash("sha256").update(bytes).digest("hex") !== asset.sha256) fail();
    // Freeze verified bytes for the build; do not re-read a mutable asset after validation.
    assets.set(asset.reference, bytes);
  }
  return { coaches, assets };
}

export function coachProjectionIntegration(environment, env = process.env) {
  if (env.COACH_PROJECTION_FILE === undefined) {
    if (env.COACH_PROJECTION_ASSET_ROOT !== undefined) fail();
    return null;
  }
  const { coaches, assets } = loadProjection(env.COACH_PROJECTION_FILE, environment.mode, env.COACH_PROJECTION_ASSET_ROOT);
  const id = "virtual:coach-projection";
  let output;
  return {
    name: "local-coach-projection",
    hooks: {
      "astro:config:setup": ({ command, injectRoute, updateConfig }) => {
        if (command !== "build") throw new Error("Coach projection is local build-only.");
        updateConfig({ vite: { plugins: [{
          name: "local-coach-projection-data",
          resolveId: (source) => source === id ? `\0${id}` : undefined,
          load: (source) => source === `\0${id}` ? `export const coaches = ${JSON.stringify(coaches)};` : undefined,
        }] } });
        injectRoute({ pattern: "/projected-coaches", entrypoint: fileURLToPath(new URL("../src/projection/Directory.astro", import.meta.url)) });
        injectRoute({ pattern: "/projected-coaches/[slug]", entrypoint: fileURLToPath(new URL("../src/projection/Profile.astro", import.meta.url)) });
      },
      "astro:config:done": ({ config }) => {
        output = fileURLToPath(config.outDir);
        assertProjectionOutput(output);
      },
      "astro:build:start": () => assertProjectionOutput(output),
      "astro:build:done": async ({ dir }) => {
        assertProjectionOutput(fileURLToPath(dir));
        for (const [reference, bytes] of assets) {
          const target = new URL(reference, dir);
          assertProjectionOutput(fileURLToPath(target));
          await mkdir(dirname(fileURLToPath(target)), { recursive: true });
          await writeFile(target, bytes);
        }
      },
    },
  };
}
