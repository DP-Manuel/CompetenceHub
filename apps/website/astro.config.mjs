import { defineConfig } from "astro/config";

const isGitHubPagesReview = process.env.GITHUB_PAGES_REVIEW === "true";

export default defineConfig({
  site: isGitHubPagesReview
    ? "https://dp-manuel.github.io"
    : "https://competencehub.donner-partner.de",
  base: isGitHubPagesReview ? "/CompetenceHub" : "/",
});
