import { defineConfig } from "astro/config";
import { cp, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { websiteEnvironment } from "./config/environment.mjs";

const environment = websiteEnvironment();
const restoredSlugs = [
  "carolin-hupp", "elisabeth-schwabauer", "goran-celic",
  "guelcan-elmas-brandes", "stefanie-becker", "wegner-ney",
  "susanne-klemm",
];

export default defineConfig({
  site: environment.site,
  base: environment.base,
  outDir: environment.outDir,
  vite: {
    envDir: false,
    define: {
      "import.meta.env.PUBLIC_REVIEW_MODE": JSON.stringify(String(environment.preview)),
    },
    resolve: { alias: {
      "@website-coaches": fileURLToPath(new URL(
        environment.preview ? "./src/preview/coaches.ts" : "./src/data/coaches.ts",
        import.meta.url,
      )),
    } },
  },
  integrations: environment.preview ? [{
    name: "approved-preview-content",
    hooks: {
      "astro:config:setup": ({ injectRoute }) => {
        for (const slug of restoredSlugs) {
          injectRoute({
            pattern: `/coaches/${slug}`,
            entrypoint: fileURLToPath(new URL(`./src/preview/profiles/${slug}.astro`, import.meta.url)),
          });
        }
      },
      "astro:build:done": async ({ dir }) => {
        const target = new URL("images/coaches/", dir);
        await mkdir(target, { recursive: true });
        await cp(new URL("./src/preview/portraits/", import.meta.url), target, { recursive: true });
      },
    },
  }] : [],
});
