import { cp, mkdir, rm } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { approvedCoachProfiles, coachProfilesFor } from "./active-coach-publication.mjs";

export function approvedCoachContent(mode) {
  const visible = coachProfilesFor(mode);
  const injectedProfiles = visible.filter((profile) => profile.injected);
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
        for (const profile of approvedCoachProfiles) {
          if (!visible.includes(profile)) await rm(new URL(profile.portrait, target), { force: true });
        }
        for (const { portrait } of injectedProfiles) {
          await cp(new URL(`../src/preview/portraits/${portrait}`, import.meta.url), new URL(portrait, target));
        }
      },
    },
  };
}
