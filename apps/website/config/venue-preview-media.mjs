import { copyFile, mkdir } from "node:fs/promises";
import { previewCities, roomsFor, roomWidths } from "../src/data/venues.mjs";

export const venuePhotoPaths = () => previewCities.flatMap((city) => roomsFor(city).flatMap(({ photos }) =>
  photos.flatMap(({ id }) => roomWidths.flatMap((width) => ["webp", "jpg"]
    .map((ext) => `${city.id}/${id}-${width}.${ext}`)))));

export function venuePreviewMedia() {
  return {
    name: "approved-venue-preview-media",
    hooks: {
      "astro:build:done": async ({ dir }) => {
        const target = new URL("images/venues/", dir);
        await Promise.all(venuePhotoPaths().map(async (path) => {
          if (!/^[a-z0-9-]+\/[a-z0-9-]+\.(webp|jpg)$/.test(path)) throw new Error("Invalid public venue photo path");
          const output = new URL(path, target);
          await mkdir(new URL(".", output), { recursive: true });
          await copyFile(new URL(`../src/media/venues/${path}`, import.meta.url), output);
        }));
      },
    },
  };
}
