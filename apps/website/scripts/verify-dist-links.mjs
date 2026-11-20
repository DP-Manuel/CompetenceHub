import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { extname, join, relative, resolve, sep } from "node:path";
import assert from "node:assert/strict";
import { websiteEnvironment, portalLoginConfiguration } from "../config/environment.mjs";
import { activeCoachProfiles, pausedCoachSlugs } from "../config/active-coach-publication.mjs";

const environment = websiteEnvironment();
const portalLogin = portalLoginConfiguration();
const dist = resolve(environment.outDir);
const base = environment.preview ? environment.base : "";
const canonicalHost = "competencehub.donner-partner.de";
const htmlFiles = [];
const allFiles = [];

const textExtensions = new Set([".css", ".html", ".js", ".json", ".txt", ".xml"]);

function walk(directory) {
  for (const entry of readdirSync(directory)) {
    const fullPath = join(directory, entry);
    if (statSync(fullPath).isDirectory()) walk(fullPath);
    else {
      allFiles.push(fullPath);
      if (entry.endsWith(".html")) htmlFiles.push(fullPath);
    }
  }
}

function publicPathForFile(file) {
  const value = relative(dist, file).split(sep).join("/");
  const path = value === "index.html" ? "/" : value.endsWith("/index.html")
    ? `/${value.slice(0, -"index.html".length)}` : `/${value}`;
  return base + path;
}

function targetFile(pathname) {
  if (base && (pathname === base || pathname.startsWith(base + "/"))) {
    pathname = pathname.slice(base.length) || "/";
  }
  const decoded = decodeURIComponent(pathname).replace(/^\/+/, "");
  const direct = join(dist, decoded);
  if (pathname.endsWith("/")) return join(direct, "index.html");
  if (extname(decoded)) return direct;
  if (existsSync(direct)) return direct;
  return join(direct, "index.html");
}

function hasFragment(file, fragment) {
  if (!fragment || !file.endsWith(".html")) return true;
  const id = decodeURIComponent(fragment);
  const html = readFileSync(file, "utf8");
  return html.includes(`id="${id}"`) || html.includes(`id='${id}'`);
}

walk(dist);
const failures = [];
let checked = 0;

for (const sourceFile of htmlFiles) {
  const sourcePublicPath = publicPathForFile(sourceFile);
  const html = readFileSync(sourceFile, "utf8");
  if (environment.preview) {
    assert.match(html, /<meta name="robots" content="noindex, nofollow, noarchive"/, sourcePublicPath);
    assert.match(html, /Entwicklungs-\/Vorschauversion/, sourcePublicPath);
    for (const match of html.matchAll(/<(?:link[^>]+rel="canonical"|meta[^>]+property="og:url")[^>]+(?:href|content)="([^"]+)"/g)) {
      assert.ok(match[1].startsWith(`https://${canonicalHost}/`), "Only production canonicals are permitted");
      assert.ok(!match[1].includes("/CompetenceHub"), "Canonical must not contain preview base");
    }
  }
  const references = html.matchAll(/\b(?:href|src)=(?:"([^"]+)"|'([^']+)')/gi);

  for (const match of references) {
    const raw = match[1] ?? match[2];
    if (/^(?:mailto:|tel:|data:|javascript:|\/\/)/i.test(raw)) continue;
    if (base && raw.startsWith("/") && !raw.startsWith(base + "/")) {
      failures.push({ source: sourcePublicPath, target: raw, reason: "missing preview base" });
    }

    let url;
    try {
      url = new URL(raw, `https://${canonicalHost}${sourcePublicPath}`);
    } catch {
      failures.push({ source: sourcePublicPath, target: raw, reason: "invalid URL" });
      continue;
    }

    if (url.host !== canonicalHost) continue;
    const file = targetFile(url.pathname);
    checked += 1;
    if (!existsSync(file)) {
      failures.push({ source: sourcePublicPath, target: raw, reason: "missing target" });
      continue;
    }
    if (!hasFragment(file, url.hash.slice(1))) {
      failures.push({ source: sourcePublicPath, target: raw, reason: "missing fragment" });
    }
  }
}

for (const file of allFiles) {
  const publicPath = relative(dist, file).split(sep).join("/");
  const pathLower = publicPath.toLocaleLowerCase("de-DE");
  if (pausedCoachSlugs.some((slug) => pathLower.includes(slug))) {
    failures.push({ source: publicPath, reason: "Paused Coach route/asset in public artifact" });
  }
  if (!textExtensions.has(extname(file).toLowerCase())) continue;
  const content = readFileSync(file, "utf8").toLocaleLowerCase("de-DE");
  if (/v2-demo-coach|v2-demo-angebot|lokaler v2-pilot|data-live-upcoming|\/portal\/(?:calendar-public\.html|upcoming-events\.js)/.test(content)) {
    failures.push({ source: publicPath, reason: "Local V2 Calendar journey in public artifact" });
  }
  if (/data-portal-login="design"/.test(content) || (!portalLogin.href && content.includes("data-portal-login"))) {
    failures.push({ source: publicPath, reason: "Unconfirmed or local-design Portal entry in public artifact" });
  }
  if (/carolin hupp|carolin-hupp|janay rappelt|localhost:8447|217\.160\.255\.86|\/api\/v1\/portal|source_path|\.docx/.test(content)) {
    failures.push({ source: publicPath, reason: "Paused identity or internal data in public artifact" });
  }
}

const read = (path) => readFileSync(join(dist, path), "utf8");
const expectedSlugs = activeCoachProfiles.map(({ slug }) => slug).sort();
const portraitPaths = allFiles.map((file) => relative(dist, file).split(sep).join("/"))
  .filter((path) => path.startsWith("images/coaches/"));
assert.deepEqual(portraitPaths.sort(), activeCoachProfiles.map(({ portrait }) => `images/coaches/${portrait}`).sort());
const profileRoutes = readdirSync(join(dist, "coaches"), { withFileTypes: true }).filter((entry) =>
  entry.isDirectory() && !(!environment.preview && /^demoprofil-0[1-6]$/.test(entry.name))
).map(({ name }) => name).sort();
assert.deepEqual(profileRoutes, expectedSlugs);
const home = read("index.html");
const directory = read("coaches/index.html");
assert.doesNotMatch(home, /Demoprofil/);
assert.doesNotMatch(directory, /Demoprofil|Transparenter Messestand|Schabbauer/);
assert.equal((directory.match(/class="coach-card__name"/g) ?? []).length, 8);
assert.equal((home.match(/class="coach-preview__name"/g) ?? []).length, 8);
for (const { slug, injected } of activeCoachProfiles) {
  const html = read(`coaches/${slug}/index.html`);
  assert.ok(html.includes(`data-coach-profile="${slug}"`), slug);
  assert.ok(directory.includes(`class="coach-card__name" href="${base}/coaches/${slug}"`), slug);
  if (environment.preview && injected) assert.doesNotMatch(html, /rel="canonical"|property="og:url"/, slug);
  if (!environment.preview) assert.match(html, /rel="canonical"/, slug);
}
const offers = read("leistungen/index.html");
const payload = offers.match(/<script[^>]+data-finder-data[^>]*>(.*?)<\/script>/s);
assert.ok(payload, "Finder must contain its allowlisted public data");
const entries = JSON.parse(payload[1]);
assert.deepEqual([...new Set(entries.map((entry) => entry.coach.profilePath))].sort(), [
  "coaches/elisabeth-schwabauer", "coaches/goran-celic", "coaches/guelcan-elmas-brandes", "coaches/susanne-klemm",
]);
assert.equal(entries.length, 28);
assert.equal(entries.flatMap((entry) => entry.formats).length, 33);
assert.doesNotMatch(payload[1], /Psychotherapie \(HeilprG\)|carolin-hupp|stefanie-becker/);
const sitemap = read("sitemap.xml");

if (environment.preview) {
  assert.equal(read("robots.txt"), "User-agent: *\nDisallow: /\n");
  assert.doesNotMatch(sitemap, /<url>/);
  assert.doesNotMatch(read("coaches/manuela-rodriguez/index.html"), /firmenseminare/);
  assert.match(read("coaches/manuela-rodriguez/index.html"), /href="https:\/\/advisory\.donner-partner\.de\/"/);
} else {
  assert.deepEqual([...sitemap.matchAll(/<loc>https:\/\/competencehub\.donner-partner\.de\/coaches\/([^<\/]+)\/?<\/loc>/g)]
    .map((match) => match[1]).sort(), expectedSlugs);
  const manuela = read("coaches/manuela-rodriguez/index.html");
  assert.match(manuela, /href="https:\/\/donner-partner\.de\/dp\/fuer-unternehmen\/firmenseminare\/"/);
  assert.doesNotMatch(manuela, /href="https:\/\/advisory\.donner-partner\.de\/"/);
}
console.log(`Verified ${checked} internal references across ${htmlFiles.length} HTML files.`);
if (failures.length > 0) {
  console.error(JSON.stringify(failures, null, 2));
  process.exitCode = 1;
}
