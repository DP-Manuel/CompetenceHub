import { defineConfig } from "astro/config";
import { rm } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { approvedCoachContent } from "./config/approved-production-content.mjs";
import { demoCoachPath } from "./src/v2-local/journey.mjs";

export default defineConfig({
  base: "/website",
  outDir: "./.tmp/v2-local-website",
  devToolbar: { enabled: false },
  build: { inlineStylesheets: "never" },
  vite: {
    envDir: false,
    build: { assetsInlineLimit: 0 },
    define: {
      "import.meta.env.PUBLIC_REVIEW_MODE": '"false"',
      __WEBSITE_V2_LOCAL__: "true",
    },
    resolve: { alias: {
      "@website-coaches": fileURLToPath(new URL("./src/preview/coaches.ts", import.meta.url)),
      "@website-offer-finder": fileURLToPath(new URL("./src/preview/OfferingFinder.astro", import.meta.url)),
    } },
  },
  integrations: [approvedCoachContent("production"), {
    name: "v2-loopback-website",
    hooks: {
      "astro:config:setup": ({ command, config, injectRoute }) => {
        const publicOutputs = ["./dist/", "./dist-preview/"].map((path) => new URL(path, config.root).href);
        if (config.base.replace(/\/$/, "") !== "/website"
          || (command === "build" && publicOutputs.some((path) => config.outDir.href.startsWith(path)))) {
          throw new Error("V2 local website requires /website and an isolated output directory.");
        }
        injectRoute({
          pattern: `/${demoCoachPath.slice(0, -1)}`,
          entrypoint: fileURLToPath(new URL("./src/v2-local/DemoCoach.astro", import.meta.url)),
        });
      },
      "astro:build:done": ({ dir }) => rm(new URL(".htaccess", dir), { force: true }),
    },
  }],
});
