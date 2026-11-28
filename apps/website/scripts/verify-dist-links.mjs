import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { extname, join, relative, resolve, sep } from "node:path";
import assert from "node:assert/strict";
import { websiteEnvironment, portalLoginConfiguration } from "../config/environment.mjs";
import { approvedCoachProfiles, coachProfilesFor, featuredCoachSlugs, pausedCoachSlugs } from "../config/active-coach-publication.mjs";
import { venuePhotoPaths } from "../config/venue-preview-media.mjs";

const environment = websiteEnvironment();
const activeCoachProfiles = coachProfilesFor(environment.mode);
const excludedSlugs = [...pausedCoachSlugs, ...approvedCoachProfiles
  .filter((profile) => !activeCoachProfiles.includes(profile)).map(({ slug }) => slug)];
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
  if (/demoprofil-0[1-6]/.test(pathLower) || excludedSlugs.some((slug) => pathLower.includes(slug))) {
    failures.push({ source: publicPath, reason: "Deferred, paused or demo Coach route/asset in public artifact" });
  }
  if (!textExtensions.has(extname(file).toLowerCase())) continue;
  const content = readFileSync(file, "utf8").toLocaleLowerCase("de-DE");
  if (/v2-demo-coach|v2-demo-angebot|lokaler v2-pilot|data-live-upcoming|beispieltermin rhetorik|beispieltermin führung|\/portal\/(?:calendar-public\.html|upcoming-events\.js)/.test(content)) {
    failures.push({ source: publicPath, reason: "Local V2 Calendar journey in public artifact" });
  }
  if (/data-portal-login="design"/.test(content) || (!portalLogin.href && content.includes("data-portal-login"))) {
    failures.push({ source: publicPath, reason: "Unconfirmed or local-design Portal entry in public artifact" });
  }
  if (/carolin hupp|demoprofil-0[1-6]|janay rappelt|localhost:8447|217\.160\.255\.86|\/api\/v1\/portal|source_path|\.docx/.test(content)
    || excludedSlugs.some((slug) => content.includes(slug))) {
    failures.push({ source: publicPath, reason: "Paused identity or internal data in public artifact" });
  }
  if (environment.preview && /g[üu]lcan|elmas[- ]brandes|images\/room-experience\//.test(content)) {
    failures.push({ source: publicPath, reason: "Coach or room content outside the review release" });
  }
}

const read = (path) => readFileSync(join(dist, path), "utf8");
const expectedSlugs = activeCoachProfiles.map(({ slug }) => slug).sort();
const portraitPaths = allFiles.map((file) => relative(dist, file).split(sep).join("/"))
  .filter((path) => path.startsWith("images/coaches/"));
assert.deepEqual(portraitPaths.sort(), activeCoachProfiles.map(({ portrait }) => `images/coaches/${portrait}`).sort());
const profileRoutes = readdirSync(join(dist, "coaches"), { withFileTypes: true })
  .filter((entry) => entry.isDirectory()).map(({ name }) => name).sort();
assert.deepEqual(profileRoutes, expectedSlugs);
const home = read("index.html");
const directory = read("coaches/index.html");
assert.doesNotMatch(home, /Demoprofil/);
assert.doesNotMatch(directory, /Demoprofil|Transparenter Messestand|Schabbauer/);
assert.equal((directory.match(/class="coach-card__name"/g) ?? []).length, expectedSlugs.length);
assert.deepEqual([...home.matchAll(/data-spotlight-coach="([^"]+)"/g)].map((match) => match[1]),
  featuredCoachSlugs.filter((slug) => expectedSlugs.includes(slug)));
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
const expectedCatalogue = {
  "christian-galvano": environment.preview ? [3, 3] : [0, 0],
  "manuela-rodriguez": environment.preview ? [1, 1] : [0, 0],
  "elisabeth-schwabauer": [16, 16], "goran-celic": [1, 4],
  "guelcan-elmas-brandes": [3, 5], "susanne-klemm": [8, 8],
};
const expectedFinderSlugs = expectedSlugs.filter((slug) => expectedCatalogue[slug]?.[0]);
assert.deepEqual([...new Set(entries.map((entry) => entry.coach.profilePath))].sort(),
  expectedFinderSlugs.map((slug) => `coaches/${slug}`));
for (const slug of expectedFinderSlugs) {
  const items = entries.filter(({ coach }) => coach.profilePath === `coaches/${slug}`);
  assert.deepEqual([items.length, items.flatMap((entry) => entry.formats).length], expectedCatalogue[slug], slug);
}
assert.doesNotMatch(payload[1], /Psychotherapie \(HeilprG\)|carolin-hupp|stefanie-becker/);
const sitemap = read("sitemap.xml");
const company = read("unternehmen/index.html");
const contact = read("kontakt/index.html");
const venueFiles = allFiles.map((path) => relative(dist, path).split(sep).join("/"))
  .filter((path) => path.startsWith("images/venues/") || path.startsWith("veranstaltungsorte/")).sort();

if (environment.preview) {
  assert.deepEqual(venueFiles, [...venuePhotoPaths().map((path) => `images/venues/${path}`), "veranstaltungsorte/index.html"].sort());
  const venuePage = read("veranstaltungsorte/index.html");
  assert.match(venuePage, /property="og:image" content="https:\/\/dp-manuel\.github\.io\/CompetenceHub\/images\/venues\//);
  assert.doesNotMatch(venuePage, /rel="canonical"|Schreinerei|Heisenberg|Röntgen|K[öo]lliker|Siebold|Buchner|Max-Planck/);
  assert.match(company, /data-venue-teaser/);
  assert.match(contact, /data-venue="wuerzburg"/);
  assert.equal((company.match(/data-compass-recommendations/g) ?? []).length, 6);
  assert.doesNotMatch(company, /data-solution-guide(?:=|\s)/);
  assert.match(contact, /data-copy-address/);
  assert.match(contact, /data-copy-draft/);
  assert.equal(read("robots.txt"), "User-agent: *\nDisallow: /\n");
  assert.doesNotMatch(sitemap, /<url>/);
  assert.doesNotMatch(read("coaches/manuela-rodriguez/index.html"), /firmenseminare/);
  assert.match(read("coaches/manuela-rodriguez/index.html"), /href="https:\/\/advisory\.donner-partner\.de\/"/);
} else {
  assert.deepEqual(venueFiles, []);
  assert.doesNotMatch(company, /data-venue-teaser|veranstaltungsorte\//);
  assert.doesNotMatch(contact, /data-venue=/);
  assert.doesNotMatch(company, /data-compass-recommendations/);
  assert.doesNotMatch(contact, /data-copy-draft|data-copy-address/);
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
