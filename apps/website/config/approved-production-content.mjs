import { cp, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { activeCoachProfiles } from "./active-coach-publication.mjs";

export function approvedCoachContent() {
  const injectedProfiles = activeCoachProfiles.filter((profile) => profile.injected);
  return {
    name: "approved-active-coaches",
    hooks: {
      "astro:config:setup": ({ injectRoute }) => {
        for (const { slug } of injectedProfiles) {
          injectRoute({
            pattern: `/coaches/${slug}`,
            entrypoint: fileURLToPath(new URL(`../src/preview/profiles/${slug}.astro`, import.meta.url)),
          });
        }
      },
      "astro:build:done": async ({ dir }) => {
        const target = new URL("images/coaches/", dir);
        await mkdir(target, { recursive: true });
        for (const { portrait } of injectedProfiles) {
          await cp(new URL(`../src/preview/portraits/${portrait}`, import.meta.url), new URL(portrait, target));
        }
      },
    },
  };
}
