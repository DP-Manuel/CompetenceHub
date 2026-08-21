import type { APIRoute } from "astro";

import { coaches } from "../data/coaches";

const site = new URL("https://competencehub.donner-partner.de");
const routes = [
  "",
  "leistungen",
  "lifecoaching",
  "livecoaching",
  "businesscoaching",
  "mindforge",
  "unternehmen",
  "coaches",
  ...coaches.map((coach) => coach.profilePath),
  "ueber-uns",
  "kontakt",
  "impressum",
  "datenschutz",
];

export const GET: APIRoute = () => {
  const urls = routes
    .map((route) => `  <url><loc>${new URL(route, site).toString()}</loc></url>`)
    .join("\n");
  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    urls,
    "</urlset>",
    "",
  ].join("\n");

  return new Response(body, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
};
