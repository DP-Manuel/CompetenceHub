// Read-only canonical/public content inventory. No DB, source-folder access or imports.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, access, mkdir, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, join, relative } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const website = join(root, "apps/website");
const require = createRequire(join(website, "package.json"));
const viteRoot = dirname(require.resolve("vite/package.json"));
const { createServer } = await import(pathToFileURL(join(viteRoot, "dist/node/index.js")));
const exists = async (path) => access(path).then(() => true, () => false);
const hash = async (path) => createHash("sha256").update(await readFile(path)).digest("hex");
const rel = (path) => relative(root, path).replaceAll("\\", "/");
const vite = await createServer({ root: website, configFile: false, envDir: false,
  server: { middlewareMode: true }, optimizeDeps: { noDiscovery: true } });
try {
  const { coaches } = await vite.ssrLoadModule("/src/preview/coaches.ts");
  const { topics, categories } = await vite.ssrLoadModule("/src/preview/topics.ts");
  const { offerGroups } = await vite.ssrLoadModule("/src/preview/elisabeth-offers.ts");
  const { workshops, qualifications } = await vite.ssrLoadModule("/src/preview/susanne-klemm.ts");
  assert.equal(coaches.length, 9);
  assert.equal(new Set(coaches.map(c => c.profilePath)).size, coaches.length);
  const records = [];
  for (const coach of coaches) {
    const slug = coach.profilePath.split("/").at(-1);
    assert.match(slug, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
    const page = join(website, "src/pages", coach.profilePath + ".astro");
    const template = await exists(page) ? page : join(website, "src/preview/profiles", slug + ".astro");
    let image = null;
    if (coach.image) {
      const candidate = join(website, "public", coach.image);
      const path = await exists(candidate) ? candidate : join(website, "src/preview/portraits", coach.image.split("/").at(-1));
      image = { reference: coach.image, source: rel(path), sha256: await hash(path) };
    }
    assert.ok(coach.topics.every(id => topics.some(t => t.id === id)));
    records.push({ ...coach, template: rel(template), template_sha256: await hash(template), asset: image,
      structured_offers: slug === "susanne-klemm" ? workshops : slug === "elisabeth-schwabauer" ? offerGroups : null,
      structured_qualifications: slug === "susanne-klemm" ? qualifications : null });
  }
  const output = join(root, ".tmp/coach3-static-inventory-2026-10-23.json");
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, JSON.stringify({ schema: 1, mode: "analysis_only_no_db", coaches: records, topics, categories }, null, 2));
  console.log(JSON.stringify({ status: "PASS", coaches: records.length, portraits: records.filter(c => c.asset).length,
    topics: topics.length, categories: categories.length, inventory_sha256: await hash(output), output: rel(output) }));
} finally { await vite.close(); }
