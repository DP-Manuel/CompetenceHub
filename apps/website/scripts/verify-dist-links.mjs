import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { extname, join, relative, resolve, sep } from "node:path";

const dist = resolve("dist");
const canonicalHost = "competencehub.donner-partner.de";
const htmlFiles = [];

function walk(directory) {
  for (const entry of readdirSync(directory)) {
    const fullPath = join(directory, entry);
    if (statSync(fullPath).isDirectory()) walk(fullPath);
    else if (entry.endsWith(".html")) htmlFiles.push(fullPath);
  }
}

function publicPathForFile(file) {
  const value = relative(dist, file).split(sep).join("/");
  return value.endsWith("/index.html")
    ? `/${value.slice(0, -"index.html".length)}`
    : `/${value}`;
}

function targetFile(pathname) {
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
  const references = html.matchAll(/\b(?:href|src)=(?:"([^"]+)"|'([^']+)')/gi);

  for (const match of references) {
    const raw = match[1] ?? match[2];
    if (/^(?:mailto:|tel:|data:|javascript:|\/\/)/i.test(raw)) continue;

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

console.log(`Verified ${checked} internal references across ${htmlFiles.length} HTML files.`);
if (failures.length > 0) {
  console.error(JSON.stringify(failures, null, 2));
  process.exitCode = 1;
}
