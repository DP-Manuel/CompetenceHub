export function websiteEnvironment(env = process.env) {
  const mode = env.WEBSITE_ENV ?? "production";
  if (!["production", "preview"].includes(mode)) {
    throw new Error("WEBSITE_ENV must be production or preview.");
  }
  const preview = mode === "preview";
  for (const key of ["GITHUB_PAGES_REVIEW", "PUBLIC_REVIEW_MODE"]) {
    if (env[key] !== undefined && env[key] !== String(preview)) {
      throw new Error(`${key} conflicts with WEBSITE_ENV=${mode}. Use WEBSITE_ENV only.`);
    }
  }
  return Object.freeze({
    mode,
    preview,
    site: preview ? "https://dp-manuel.github.io" : "https://competencehub.donner-partner.de",
    base: preview ? "/CompetenceHub" : "/",
    outDir: preview ? "./dist-preview" : "./dist",
  });
}
