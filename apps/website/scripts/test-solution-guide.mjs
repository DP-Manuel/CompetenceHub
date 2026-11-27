import assert from "node:assert/strict";
import test from "node:test";
import { audiences, contactTopics, directions, goals, suggestDirections } from "../src/data/solution-guide.mjs";

test("the existing six compass topics return at most three real local directions", () => {
  for (const topic of ["fuehrung", "teams", "recruiting", "entwicklung", "veraenderung", "gesundheit"]) {
    for (const { id: audience } of audiences) {
      for (const { id: goal } of goals) {
        const result = suggestDirections(topic, audience, goal);
        assert.ok(result.length >= 2 && result.length <= 3);
        assert.equal(new Set(result).size, result.length);
        assert.deepEqual(suggestDirections(topic, audience, goal), result);
        for (const direction of result) {
          assert.ok(Object.values(directions).includes(direction));
          assert.match(direction.href, /^(mindforge|leistungen|unternehmen)#[a-z-]+$/);
          assert.ok(Object.hasOwn(contactTopics, direction.contact));
          assert.ok(direction.reason);
        }
      }
    }
  }
});

test("the ranking reflects the task without introducing a new service", () => {
  assert.equal(suggestDirections("fuehrung", "einzel", "entwickeln")[0], directions.business);
  assert.equal(suggestDirections("fuehrung", "team", "entwickeln")[0], directions.workshops);
  assert.equal(suggestDirections("recruiting", "organisation", "auswahl")[0], directions.assessment);
  assert.equal(suggestDirections("recruiting", "organisation", "klaeren")[0], directions.recruiting);
});

test("unknown choices fail closed, including inherited object names", () => {
  assert.deepEqual(suggestDirections("__proto__", "einzel", "klaeren"), []);
  assert.deepEqual(suggestDirections("fuehrung", "unknown", "klaeren"), []);
  assert.deepEqual(suggestDirections("fuehrung", "einzel", "unknown"), []);
  assert.deepEqual(suggestDirections("fuehrung"), []);
});
