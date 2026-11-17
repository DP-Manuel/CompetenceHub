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

export function portalLoginConfiguration(env = process.env, { development = false } = {}) {
  const value = env.WEBSITE_PORTAL_URL?.trim();
  let href = null;
  if (value) {
    let target;
    try { target = new URL(value); } catch { /* Report only the configuration field, not its contents. */ }
    if (!target || target.protocol !== "https:" || target.username || target.password
      || target.search || target.hash || target.pathname !== "/portal/"
      || !target.hostname.includes(".") || /^[\d.]+$/.test(target.hostname) || target.hostname.startsWith("[")
      || target.hostname.endsWith(".localhost") || target.hostname.endsWith(".local")) {
      throw new Error("WEBSITE_PORTAL_URL requires a confirmed HTTPS /portal/ address without credentials, query or fragment.");
    }
    href = target.href;
  }
  const design = !href && development && env.WEBSITE_PORTAL_DESIGN_PREVIEW === "true";
  return Object.freeze({ href, design, visible: Boolean(href) || design });
}
