import assert from "node:assert/strict";
import { test } from "node:test";
import { portalLoginConfiguration } from "../config/environment.mjs";

test("missing confirmed address is hidden in Production and public Preview", () => {
  for (const mode of ["production", "preview"]) {
    assert.deepEqual(portalLoginConfiguration({ WEBSITE_ENV: mode }), { href: null, design: false, visible: false });
    assert.deepEqual(portalLoginConfiguration({ WEBSITE_ENV: mode, WEBSITE_PORTAL_DESIGN_PREVIEW: "true" }),
      { href: null, design: false, visible: false });
  }
});

test("design is opt-in and development-only, with no invented destination", () => {
  assert.equal(portalLoginConfiguration({}, { development: true }).visible, false);
  assert.deepEqual(portalLoginConfiguration({ WEBSITE_PORTAL_DESIGN_PREVIEW: "true" }, { development: true }),
    { href: null, design: true, visible: true });
  assert.equal(portalLoginConfiguration({ WEBSITE_PORTAL_DESIGN_PREVIEW: "false" }, { development: true }).visible, false);
});

test("one confirmed URL activates the same native backend entry, without role parameters", () => {
  const href = "https://portal.example.invalid/portal/";
  for (const development of [false, true]) {
    const result = portalLoginConfiguration({ WEBSITE_PORTAL_URL: href, WEBSITE_PORTAL_DESIGN_PREVIEW: "true" }, { development });
    assert.deepEqual(result, { href, design: false, visible: true });
    assert.equal(Object.isFrozen(result), true);
    assert.equal(new URL(result.href).search, "");
  }
});

test("unsafe/misdirected values fail without echoing possibly confidential input", () => {
  for (const value of ["not a url", "javascript:alert(1)", "http://portal.example.invalid/portal/",
    "https://portal.example.invalid/login/intern", "https://user:password@portal.example.invalid/portal/",
    "https://portal.example.invalid/portal/?token=not-real", "https://portal.example.invalid/portal/#coach",
    "https://localhost:8447/portal/", "https://127.0.0.1/portal/", "https://[::1]/portal/", "https://pilot.local/portal/"]) {
    assert.throws(() => portalLoginConfiguration({ WEBSITE_PORTAL_URL: value }),
      (error) => error.message.startsWith("WEBSITE_PORTAL_URL requires") && !error.message.includes(value));
  }
});
