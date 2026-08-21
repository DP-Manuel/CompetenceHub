import type { APIRoute } from "astro";

const reviewMode = import.meta.env.PUBLIC_REVIEW_MODE === "true";

export const GET: APIRoute = () => {
  const body = reviewMode
    ? "User-agent: *\nDisallow: /\n"
    : [
        "User-agent: *",
        "Allow: /",
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
