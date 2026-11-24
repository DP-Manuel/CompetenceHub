import assert from "node:assert/strict";
import { after, test } from "node:test";
import { createServer } from "vite";

const vite = await createServer({ configFile: false, envDir: false,
  server: { middlewareMode: true }, optimizeDeps: { noDiscovery: true } });
after(() => vite.close());
const { fitsHub, hubEdgePath, moveHubDisc } = await vite.ssrLoadModule("/src/components/hub-geometry.ts");

const stage = { width: 1000, height: 500 };
const start = { x: 210, y: 250, radius: 50 };
const obstacle = { x: 500, y: 250, radius: 130 };

test("hub drag follows pointer and clamps both axes inside the artwork", () => {
  assert.deepEqual(moveHubDisc(start, { x: 280, y: 315 }, stage, []), { x: 280, y: 315 });
  assert.deepEqual(moveHubDisc(start, { x: -400, y: 700 }, stage, []), { x: 60, y: 440 });
});

test("a coalesced rapid move cannot jump through the core or another node", () => {
  const result = moveHubDisc(start, { x: 920, y: 250 }, stage, [obstacle]);
  assert.ok(result.x <= obstacle.x - obstacle.radius - start.radius - 12);
  assert.ok(result.x > start.x);
  assert.ok(fitsHub(result, start.radius, stage, [obstacle]));
  assert.equal(fitsHub(obstacle, start.radius, stage, [obstacle]), false);
});

test("redrawn edge keeps exact endpoints with a deterministic bend", () => {
  assert.match(hubEdgePath({ x: 600, y: 380 }, { x: 124.3, y: 88.5 }, 0),
    /^M600\.00 380\.00 Q[-.\d]+ [-.\d]+ 124\.30 88\.50$/);
});
