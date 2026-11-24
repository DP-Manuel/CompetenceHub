import { defineConfig } from "astro/config";
import { fileURLToPath } from "node:url";
import { websiteEnvironment } from "./config/environment.mjs";
import { coachProjectionIntegration } from "./config/coach-projection.mjs";
import { approvedCoachContent } from "./config/approved-production-content.mjs";

const environment = websiteEnvironment();
const projection = coachProjectionIntegration(environment);

export default defineConfig({
  site: environment.site,
  base: environment.base,
  outDir: projection ? `./.tmp/coach4/site-${environment.mode}` : environment.outDir,
  devToolbar: { enabled: process.env.WEBSITE_PORTAL_DESIGN_PREVIEW !== "true" },
  vite: {
    envDir: false,
    define: {
      "import.meta.env.PUBLIC_REVIEW_MODE": JSON.stringify(String(environment.preview)),
      __WEBSITE_V2_LOCAL__: "false",
    },
    resolve: { alias: {
      "@website-offer-finder": fileURLToPath(new URL(
        "./src/preview/OfferingFinder.astro",
        import.meta.url,
      )),
      "@website-coaches": fileURLToPath(new URL(
        "./src/preview/coaches.ts",
        import.meta.url,
      )),
    } },
  },
  integrations: [...(projection ? [projection] : []), approvedCoachContent(environment.mode)],
});
