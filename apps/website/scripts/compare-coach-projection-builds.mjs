import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { resolve, join } from "node:path";

const [before, after] = process.argv.slice(2).map((path) => resolve(path));
assert.ok(before && after, "Pass baseline and candidate build directories");
function files(root, prefix = "") {
  return readdirSync(join(root, prefix), { withFileTypes: true }).flatMap((entry) => {
    const name = prefix ? `${prefix}/${entry.name}` : entry.name;
    assert.ok(!entry.isSymbolicLink(), "Build must not contain symlinks");
    return entry.isDirectory() ? files(root, name) : [name];
  }).sort();
}
const names = files(before);
assert.deepEqual(files(after), names, "Build inventory changed");
const digest = createHash("sha256");
for (const name of names) {
  const old = readFileSync(join(before, name));
  assert.deepEqual(readFileSync(join(after, name)), old, `Build bytes changed: ${name}`);
  digest.update(name + "\0").update(old);
}
console.log(JSON.stringify({ files: names.length, byteIdentical: true, sha256: digest.digest("hex") }));
