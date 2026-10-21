import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { resolve, join } from "node:path";
import { createHash } from "node:crypto";

const baseline = resolve(process.argv[2] || "release-artifacts/preview-qa/baseline");
const current = resolve("dist");
function files(root, prefix = "") {
  return readdirSync(join(root, prefix), { withFileTypes: true }).flatMap((entry) => {
    const name = prefix ? `${prefix}/${entry.name}` : entry.name;
    return entry.isDirectory() ? files(root, name) : [name];
  }).sort();
}
const names = files(baseline);
assert.deepEqual(files(current), names, "Production artifact inventory changed");
const differences = names.filter((name) =>
  !readFileSync(join(baseline, name)).equals(readFileSync(join(current, name))));
assert.deepEqual(differences, [], "Production artifact bytes changed");
const digest = createHash("sha256");
for (const name of names) {
  digest.update(name + "\0").update(readFileSync(join(current, name)));
}
console.log(JSON.stringify({ files: names.length, byteIdentical: true, sha256: digest.digest("hex") }));
