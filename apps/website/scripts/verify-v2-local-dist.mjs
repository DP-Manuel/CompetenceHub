import assert from "node:assert/strict";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";

assert.ok(process.argv[2], "Pass the private V2 build output directory.");
const root = resolve(process.argv[2]);
const read = (file) => readFileSync(join(root, file), "utf8");
const walk = (dir = "") => readdirSync(join(root, dir), { withFileTypes: true }).flatMap((item) => {
  const file = join(dir, item.name);
  return item.isDirectory() ? walk(file) : [file];
});

const home = read("index.html");
const offers = read("leistungen/index.html");
const coach = read("coaches/v2-demo-coach/index.html");
const official = read("coaches/guelcan-elmas-brandes/index.html");
assert.match(home, /href="\/website\/leistungen\/#v2-demo-angebot"/);
assert.match(home, /href="\/portal\/calendar-public\.html"/);
assert.match(offers, /id="v2-demo-angebot"/);
assert.match(offers, /href="\/website\/coaches\/v2-demo-coach\/"/);
assert.match(offers, /href="\/website\/coaches\/guelcan-elmas-brandes" data-finder-profile/);
assert.match(coach, /Synthetisches Profil/);
assert.match(coach, /href="\/portal\/calendar-public\.html\?coach=v2-demo-coach"/);
assert.match(coach, /href="\/website\/leistungen\/#v2-demo-angebot"/);
assert.doesNotMatch(official, /calendar-public\.html\?coach=/);
assert.equal(read("robots.txt"), "User-agent: *\nDisallow: /\n");
assert.doesNotMatch(read("sitemap.xml"), /<url>/);
assert.ok(!existsSync(join(root, ".htaccess")));

if (process.argv[3]) {
  const production = (file) => readFileSync(join(resolve(process.argv[3]), file), "utf8");
  const finderData = (html) => html.match(/<script[^>]+data-finder-data[^>]*>(.*?)<\/script>/s)?.[1];
  const familyLinks = (html) => [...html.matchAll(/data-offer-family="([^"]+)"|href="(mailto:[^"]+)"/g)].map((match) => match[0]);
  assert.ok(finderData(offers), "Missing official Finder data");
  assert.equal(finderData(offers), finderData(production("leistungen/index.html")));
  assert.deepEqual(familyLinks(official), familyLinks(production("coaches/guelcan-elmas-brandes/index.html")));
}

const htmlFiles = walk().filter((file) => file.endsWith(".html"));
for (const file of htmlFiles) {
  const html = read(file);
  assert.match(html, /name="robots" content="noindex, nofollow, noarchive"/, file);
  assert.doesNotMatch(html, /rel="canonical"|property="og:url"|<[^>]+\sstyle=/, file);
  assert.equal([...html.matchAll(/href="\/portal\/" data-portal-login="enabled"/g)].length, 2, file);
  for (const [tag] of html.matchAll(/<script\b[^>]*>/g)) {
    assert.match(tag, /\btype="application\/json"|\bsrc="\/website\/_astro\//, `${file}: ${tag}`);
  }
}
console.log(`Verified local V2 journey, noindex and CSP contracts across ${htmlFiles.length} HTML files.`);
