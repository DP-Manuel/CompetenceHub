import type { APIRoute } from "astro";

const reviewMode = import.meta.env.PUBLIC_REVIEW_MODE === "true";

export const GET: APIRoute = () => {
  const body = reviewMode || __WEBSITE_V2_LOCAL__
    ? "User-agent: *\nDisallow: /\n"
    : [
        "User-agent: *",
        "Allow: /",
        "Disallow: /kalender/",
        "Disallow: /login/",
        "Disallow: /prototyp/",
        "Disallow: /qualifizierung/",
        "Disallow: /seminare/",
        "Disallow: /system/",
        "Sitemap: https://competencehub.donner-partner.de/sitemap.xml",
        "",
      ].join("\n");

  return new Response(body, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
