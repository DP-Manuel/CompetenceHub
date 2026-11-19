import { cp, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";

export function approvedProductionContent() {
  return {
    name: "approved-production-guelcan",
    hooks: {
      "astro:config:setup": ({ injectRoute }) => injectRoute({
        pattern: "/coaches/guelcan-elmas-brandes",
        entrypoint: fileURLToPath(new URL("../src/preview/profiles/guelcan-elmas-brandes.astro", import.meta.url)),
      }),
      "astro:build:done": async ({ dir }) => {
        const target = new URL("images/coaches/", dir);
        await mkdir(target, { recursive: true });
        await cp(new URL("../src/preview/portraits/guelcan-elmas-brandes.png", import.meta.url),
          new URL("guelcan-elmas-brandes.png", target));
      },
    },
  };
}
