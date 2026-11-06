import { defineConfig } from "astro/config";

// Separate source root: neither normal build nor Pages can discover this route.
export default defineConfig({
  srcDir: "./src/local-calendar",
  publicDir: "./src/local-calendar/public",
  outDir: "./.tmp/cal1-public",
  base: "/demo/public",
  vite: { envDir: false, define: { "import.meta.env.PUBLIC_REVIEW_MODE": '"false"' } },
});
