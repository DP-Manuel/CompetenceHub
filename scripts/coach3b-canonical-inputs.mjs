// Read canonical public inputs only; no build, source-folder traversal or DB.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const website = join(root, "apps/website");
const require = createRequire(join(website, "package.json"));
const { parse } = require("@astrojs/compiler");
const ts = require("typescript");
const { createServer } = await import(pathToFileURL(join(dirname(require.resolve("vite/package.json")), "dist/node/index.js")));
const hash = bytes => createHash("sha256").update(bytes).digest("hex");
const normalize = text => text.replace(/\s+/gu, " ").trim();
function descendants(node, predicate) {
  return [...(predicate(node) ? [node] : []), ...(node.children ?? []).flatMap(child => descendants(child, predicate))];
}
const attr = (node, name) => node.attributes?.find(a => a.name === name)?.value;
function plain(node, coach) {
  if (node.type === "text") return node.value;
  if (node.type === "expression") {
    const value = node.children?.map(c => c.value ?? "").join("") ?? "";
    if (value.startsWith("coach.") && typeof coach[value.slice(6)] === "string") return coach[value.slice(6)];
    return "";
  }
  return (node.children ?? []).map(child => plain(child, coach)).join("");
}
function literal(node) {
  if (ts.isStringLiteral(node)) return node.text;
  if (ts.isArrayLiteralExpression(node)) return node.elements.map(literal);
  if (ts.isObjectLiteralExpression(node)) return Object.fromEntries(node.properties.map(p => {
    assert.ok(ts.isPropertyAssignment(p));
    return [p.name.text, literal(p.initializer)];
  }));
  throw new Error("Nonliteral canonical topic definition requires review");
}
function topicCards(frontmatter) {
  const source = ts.createSourceFile("profile.ts", frontmatter, ts.ScriptTarget.Latest, true);
  let result = [];
  function visit(node) {
    if (ts.isVariableDeclaration(node) && node.name.getText(source) === "topics") result = literal(node.initializer);
    ts.forEachChild(node, visit);
  }
  visit(source);
  return result;
}
const vite = await createServer({ root: website, configFile: false, envDir: false,
  server: { middlewareMode: true }, optimizeDeps: { noDiscovery: true } });
try {
  const { coaches } = await vite.ssrLoadModule("/src/preview/coaches.ts");
  const { topics, categories } = await vite.ssrLoadModule("/src/preview/topics.ts");
  const { offerGroups } = await vite.ssrLoadModule("/src/preview/elisabeth-offers.ts");
  const { workshops, qualifications } = await vite.ssrLoadModule("/src/preview/susanne-klemm.ts");
  const existing = JSON.parse(await readFile(join(root, ".tmp/coach3-static-inventory-2026-10-23.json"), "utf8"));
  assert.equal(coaches.length, 9);
  const records = [];
  for (const coach of coaches) {
    assert.match(coach.profilePath, /^coaches\/[a-z0-9]+(?:-[a-z0-9]+)*$/);
    const prior = existing.coaches.find(c => c.profilePath === coach.profilePath);
    assert.ok(prior);
    const safeSlug = coach.profilePath.split("/").at(-1);
    assert.ok([`apps/website/src/pages/coaches/${safeSlug}.astro`,
      `apps/website/src/preview/profiles/${safeSlug}.astro`].includes(prior.template));
    const template = await readFile(join(root, prior.template), "utf8");
    assert.equal(hash(template), prior.template_sha256, "Source changed since inventory");
    if (prior.asset) {
      assert.match(coach.image, /^images\/coaches\/[a-z0-9.-]+\.(?:webp|png|jpg)$/);
      assert.ok([`apps/website/public/${coach.image}`,
        `apps/website/src/preview/portraits/${coach.image.split("/").at(-1)}`].includes(prior.asset.source));
      assert.equal(hash(await readFile(join(root, prior.asset.source))), prior.asset.sha256);
    }
    const { ast } = await parse(template);
    const sections = descendants(ast, n => n.name === "section");
    const credentials = sections.find(n => attr(n, "class") === "coach-credentials");
    const labels = coach.profilePath.endsWith("susanne-klemm") ? qualifications :
      descendants(credentials, n => n.name === "li").map(n => normalize(plain(n, coach)));
    const staticSections = sections.map((n, i) => ({ source_key: `section-${i + 1}`, kind: attr(n, "class"),
      headings: descendants(n, c => /^h[123]$/.test(c.name ?? "")).map(c => normalize(plain(c, coach))).filter(Boolean),
      paragraphs: descendants(n, c => c.name === "p").map(c => normalize(plain(c, coach))).filter(Boolean) }));
    const frontmatter = ast.children.find(n => n.type === "frontmatter")?.value ?? "";
    const cards = topicCards(frontmatter);
    if (!cards.length) {
      const grid = descendants(ast, n => attr(n, "class") === "coach-topic-grid")[0];
      for (const article of descendants(grid, n => n.name === "article")) {
        cards.push({ title: normalize(plain(descendants(article,n=>n.name === "h3")[0],coach)),
          text: normalize(plain(descendants(article,n=>n.name === "p")[0],coach)) });
      }
    }
    const slug = coach.profilePath.split("/").at(-1);
    const offers = slug === "elisabeth-schwabauer" ? offerGroups.flatMap(group => group.offers.map((title,i) => ({
      key: `${group.id}/${i + 1}`, title, source_group: group.id,
      kind: group.id === "vortraege" ? "lecture" : group.id === "workshops" ? "workshop" : group.id === "individuell" ? "individual" : title === "Coaching" ? "coaching" : null,
      service_domain: title === "Psychotherapie (HeilprG)" ? "psychotherapy" : null,
      active: title !== "Psychotherapie (HeilprG)" }))) : slug === "susanne-klemm" ? workshops.map((title,i) => ({
        key: `workshop/${i+1}`,title,kind:"workshop",service_domain:null,active:true })) : [];
    records.push({ ...coach, source_identity: { source_system: "website-preview", source_key: `coach/${slug}` },
      profile_path: `/${coach.profilePath}/`, template: prior.template, template_sha256: prior.template_sha256,
      asset: prior.asset ? {...prior.asset,alt_text:attr(descendants(ast,n=>n.name === "img")[0],"alt")} : null,
      credentials: labels, topic_cards: cards, sections: staticSections,
      quotes: descendants(ast,n=>n.name === "blockquote").map(n=>normalize(plain(n,coach))),
      dynamic_text_expressions: descendants(ast,n=>n.type === "expression").map(n=>({
        expression: normalize(n.children?.map(c=>c.value ?? "").join("") ?? ""),
        line:n.position?.start.line})),
      external_links: descendants(ast,n=>n.name === "a").map(n=>({kind:n.attributes?.find(a=>a.name === "href")?.kind,
        target:attr(n,"href"),label:normalize(plain(n,coach))})).filter(n=>n.target?.includes("https://")),
      offerings: offers });
  }
  const output = join(root, ".tmp/coach3b-canonical-inputs-2026-10-29.json");
  const dependencies = [];
  for (const file of ["apps/website/src/data/coaches.ts","apps/website/src/preview/coaches.ts",
    "apps/website/src/preview/historical-coaches.ts","apps/website/src/preview/topics.ts",
    "apps/website/src/preview/elisabeth-offers.ts","apps/website/src/preview/ElisabethOffers.astro",
    "apps/website/src/preview/susanne-klemm.ts","docs/content/coach-publication-matrix-2026-09-24.md",
    "docs/content/susanne-klemm-preview-2026-10-23.md"]) {
    dependencies.push({path:file,sha256:hash(await readFile(join(root,file)))});
  }
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, JSON.stringify({ schema:1, mode:"READ_ONLY_CANONICAL_NO_DB", dependencies,coaches:records,topics,categories },null,2));
  console.log(JSON.stringify({status:"PASS",coaches:records.length, output:".tmp/coach3b-canonical-inputs-2026-10-29.json",sha256:hash(await readFile(output))}));
} finally { await vite.close(); }
