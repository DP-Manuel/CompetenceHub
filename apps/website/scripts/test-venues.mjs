import assert from "node:assert/strict";
import test from "node:test";
import { photoFor, previewCities, roomsFor, roomWidths } from "../src/data/venues.mjs";
import { venuePhotoPaths } from "../config/venue-preview-media.mjs";

test("only actual reviewed locations and neutral room groups are public", () => {
  assert.deepEqual(previewCities.map(({ id }) => id), ["wuerzburg"]);
  const [city] = previewCities;
  assert.deepEqual(city.venues, [], "venue/operator unknown");
  const rooms = roomsFor(city);
  const photos = rooms.flatMap((room) => room.photos);
  assert.equal(new Set(rooms.map(({ id }) => id)).size, rooms.length);
  assert.equal(new Set(photos.map(({ id }) => id)).size, 12);
  assert.deepEqual(rooms.filter(({ photos }) => photos.length > 1).map(({ photos }) => photos.map(({ id }) => id)),
    [["seminar-side", "seminar-front"]]);
  for (const id of [city.lead, ...city.preview, ...city.featured]) assert.ok(photoFor(city, id).alt);
  assert.ok(city.featured.every((id) => rooms.some(({ photos }) => photos[0]?.id === id)));
  assert.throws(() => photoFor(city, "unknown"));
});

test("media allowlist has responsive JPEG and WebP only", () => {
  const files = venuePhotoPaths();
  assert.equal(files.length, 12 * roomWidths.length * 2);
  assert.equal(new Set(files).size, files.length);
  assert.ok(files.every((name) => /^wuerzburg\/[a-z-]+-\d+\.(jpg|webp)$/.test(name)));
});
