import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { extname, join, relative, resolve, sep } from "node:path";
import assert from "node:assert/strict";
import { websiteEnvironment } from "../config/environment.mjs";

const environment = websiteEnvironment();
const dist = resolve(environment.outDir);
const base = environment.preview ? environment.base : "";
const canonicalHost = "competencehub.donner-partner.de";
const htmlFiles = [];
const allFiles = [];

const forbiddenPublicIdentityFragments = [
  "Susanne Klemm",
  "susanne-klemm",
  "Carolin Hupp",
  "Elisabeth Schwabauer",
  "Goran Celic",
  "Gülcan Elmas",
  "Guelcan Elmas",
  "Stefanie Becker",
  "Wegner-Ney",
  "carolin-hupp",
  "elisabeth-schwabauer",
  "goran-celic",
  "guelcan-elmas-brandes",
  "stefanie-becker",
  "wegner-ney",
];

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
  for (const fragment of environment.preview ? [] : forbiddenPublicIdentityFragments) {
    if (pathLower.includes(fragment.toLocaleLowerCase("de-DE"))) {
      failures.push({ source: publicPath, target: fragment, reason: "removed identity in artifact path" });
    }
  }

  if (!textExtensions.has(extname(file).toLowerCase())) continue;
  const content = readFileSync(file, "utf8").toLocaleLowerCase("de-DE");
  for (const fragment of environment.preview ? [] : forbiddenPublicIdentityFragments) {
    if (content.includes(fragment.toLocaleLowerCase("de-DE"))) {
      failures.push({ source: publicPath, target: fragment, reason: "removed identity in generated content" });
    }
  }
}

if (environment.preview) {
  assert.equal(readFileSync(join(dist, "robots.txt"), "utf8"), "User-agent: *\nDisallow: /\n");
  assert.doesNotMatch(readFileSync(join(dist, "sitemap.xml"), "utf8"), /<url>/);
  for (const slug of ["carolin-hupp", "elisabeth-schwabauer", "goran-celic",
    "guelcan-elmas-brandes", "stefanie-becker", "wegner-ney", "susanne-klemm"]) {
    const html = readFileSync(join(dist, "coaches", slug, "index.html"), "utf8");
    assert.doesNotMatch(html, /rel="canonical"|property="og:url"/, slug);
  }
  assert.doesNotMatch(readFileSync(join(dist, "coaches/index.html"), "utf8"), /Demoprofil|Transparenter Messestand|Schabbauer/);
  assert.doesNotMatch(readFileSync(join(dist, "coaches/manuela-rodriguez/index.html"), "utf8"), /firmenseminare/);
  assert.match(readFileSync(join(dist, "coaches/manuela-rodriguez/index.html"), "utf8"), /href="https:\/\/advisory\.donner-partner\.de\/"/);
} else {
  const manuela = readFileSync(join(dist, "coaches/manuela-rodriguez/index.html"), "utf8");
  assert.match(manuela, /href="https:\/\/donner-partner\.de\/dp\/fuer-unternehmen\/firmenseminare\/"/);
  assert.doesNotMatch(manuela, /href="https:\/\/advisory\.donner-partner\.de\/"/);
}
console.log(`Verified ${checked} internal references across ${htmlFiles.length} HTML files.`);
if (failures.length > 0) {
  console.error(JSON.stringify(failures, null, 2));
  process.exitCode = 1;
}
