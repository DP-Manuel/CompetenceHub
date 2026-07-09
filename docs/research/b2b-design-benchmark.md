# B2B Design Benchmark

Last updated: 2026-06-09

## Research Scope

Source article:

- Arounda, "55 Best B2B Website Design Examples for 2025"
  https://arounda.agency/blog/best-website-design-examples

Additional official sites reviewed:

- Notion: https://www.notion.com/
- monday.com: https://monday.com/
- Miro: https://miro.com/
- Webflow: https://webflow.com/
- Chainalysis: https://www.chainalysis.com/
- Slack for Healthcare: https://slack.com/solutions/healthcare
- Doximity: https://www.doximity.com/
- Cedar: https://www.cedar.com/
- Teladoc Health: https://www.teladochealth.com/
- ProPharma Group: https://www.propharmagroup.com/
- Astro docs: https://docs.astro.build/en/concepts/why-astro/

## Fit For Our Project

The best references for this project are not the most visually dramatic examples. The strongest matches are sites that explain complex B2B offerings, route multiple audiences, build trust in sensitive domains, and make a process easy to understand.

Most useful reference cluster:

- Slack for Healthcare: industry-specific B2B positioning and compliance-forward trust.
- Chainalysis: audience routing, product pillars, use-case pages, training/certification next to CTAs.
- Cedar: complex platform explained with outcomes, metrics, product modules, and case-story proof.
- Doximity: professional network trust, community scale, simple action-driven CTAs.
- Teladoc Health: multi-audience navigation without losing the core promise.
- ProPharma: deep service taxonomy and authority-first navigation for complex regulated services.
- monday.com / Miro / Notion: strong module cards, use-case routing, simple CTAs, proof near action.
- Webflow: growth-oriented site positioning and role-based navigation; useful mainly as a pattern and possible CMS/platform comparison.

## Patterns To Adopt

### 1. One Clear Hero Promise

Arounda repeatedly emphasizes that visitors decide quickly and that strong B2B sites lead with the outcome, not the feature list. For our homepage, the hero should keep the core story short:

> Weiterbildung, Recruiting und Vermittlung in einem System.

Then add one sentence that explains the loop:

> Seminare schaffen Vertrauen, machen Personalbedarfe sichtbar und verbinden Unternehmen mit gezielt qualifizierten Menschen.

Implementation rule:

- No more than one main headline, one support paragraph, one primary CTA, and one process cue in the hero.

### 2. Audience Routing From The Header

Relevant examples:

- monday.com routes by teams, business applications, company size, and industries.
- Teladoc separates individuals, organizations, and clinicians.
- Slack routes by department and industry.
- Webflow routes by role.

Recommended site routing:

- Primary: `Für Unternehmen`
- Secondary: `Seminare`
- Secondary: `Vermittlung & Qualifizierung`
- Support: `Branchen`
- Conversion: `Kontakt`

Later:

- `Für Teilnehmende`
- `Plattform`
- `App`

Why this matters:

- The model has several audiences, but the homepage must not become a compromise. Header routing lets the homepage stay B2B-first while still leaving room for participant and platform content later.

### 3. Modular Service Pillars

Relevant examples:

- Chainalysis uses product pillars and use-case pages.
- Cedar explains a complex platform with named solution modules.
- monday.com packages many use cases into repeated cards.
- Arounda's takeaways often recommend repeatable card patterns: title, one-line outcome, visual, CTA.

Recommended modules:

- `Firmenseminare`
- `Bedarfsanalyse`
- `Qualifizierung`
- `Matching & Vermittlung`
- `Begleitung beim Einstieg`

Design rule:

- Each module should use the same card pattern: title, one benefit line, one concrete detail, one link or CTA.

### 4. Process As The Central Visual

Relevant examples:

- Miro organizes complex collaboration work into visible lanes.
- Arounda highlights process clarity, flow, and one idea per section across several examples.

Recommended process:

`Seminar -> Bedarf -> Qualifizierung -> Matching -> Einstieg`

Design rule:

- Use rectangular steps connected by arrows or triangle cues.
- Keep the process visible above the middle of the homepage.
- On mobile, stack the steps vertically with clear numbering.

### 5. Trust And Compliance Early

Relevant examples:

- Slack Healthcare places healthcare-specific positioning and HIPAA-configurable messaging near the top.
- Arounda's healthcare section stresses that regulated industries need standards and proof up front.
- ProPharma relies on structured service depth and authority.
- Doximity uses scale and institutional trust signals.

Recommended trust section:

- Legal and DSGVO review before operational launch.
- Clear handling of participant consent before profile sharing.
- No guarantee claims around placement.
- Existing Donner + Partner courses and measures as credibility anchor.

Copy direction:

> Verlässlich, strukturiert und rechtssicher vorbereitet.

Avoid:

- "Garantierte Vermittlung"
- "Automatisches Matching" before the platform exists
- Any statement implying candidate data is processed before a legal/privacy setup exists

### 6. Proof Near Action

Relevant examples:

- Notion places recognizable trust logos and metrics near early CTAs.
- Miro uses company scale, metrics, and customer quote blocks.
- Cedar uses patient/provider metrics and long-form customer proof.

Recommended first-version proof:

- Existing course formats.
- Regional experience.
- Approved Donner + Partner brand trust.
- Later: company logos, seminar feedback, placement metrics, case studies.

MVP rule:

- If no approved proof exists yet, use "existing strengths" instead of invented metrics.

### 7. Education As Adoption Support

Relevant examples:

- Chainalysis places academy/certification near product narrative.
- Butterfly Network is noted for education-first adoption support.
- Slack and Miro use resources, demos, and templates to reduce evaluation friction.

Recommended content idea:

- Add a later resource area: `Seminarübersicht`, `Ablauf der Zusammenarbeit`, `FAQ für Unternehmen`, `Rechtliche Vorbereitung`.

Do not build this first unless content is available.

## Visual Translation For Our CI

The benchmark sites tend to use either bold SaaS visuals or polished enterprise minimalism. Our corporate design points us toward a restrained version:

- Use white and dark gray as the base.
- Use Pantone 320 as structural recognition color.
- Use Kaminrot for CTA emphasis and selected process moments.
- Use rectangular cards, bars, and process blocks instead of rounded SaaS-heavy components.
- Use people-centered imagery, but keep B2B seriousness.
- Keep every section focused on one idea.

Good visual direction:

- Enterprise clarity from Slack/ProPharma.
- Human trust from Doximity/Teladoc.
- Modular clarity from Chainalysis/Cedar.
- Process clarity from Miro/monday.com.

Avoid:

- Overly playful SaaS illustration style.
- Dark-mode-heavy tech aesthetic.
- Generic gradient hero.
- Product screenshots for platform/app features that do not exist yet.

## Homepage Structure Update

Recommended homepage order after research:

1. Hero with one-line promise, CTA, and process cue.
2. Trust strip or "existing strengths" strip.
3. Problem: qualification gaps and personnel needs.
4. Process: seminar to matching.
5. Service modules: seminars, needs, qualification, placement, entry support.
6. Seminar topics.
7. Industry focus.
8. Trust/legal/privacy readiness.
9. Future digital support, framed carefully.
10. Contact CTA.

Change from previous outline:

- Move trust/proof earlier.
- Make service modules more explicit.
- Keep future digital support lower on the page.

## Tech-Stack Implications

### Decision Drivers

- First deliverable is mostly static marketing content.
- B2B site needs excellent performance, SEO, accessibility, and maintainable design tokens.
- Later webapp should remain separate, but may share design tokens and components.
- Content may need non-developer editing later, but that is not confirmed.
- Legal/privacy concerns argue against premature backend forms and data storage.

### Option A: Astro Website + Later Separate Webapp

Recommended baseline.

Shape:

- `apps/website`: Astro static site.
- Later `apps/webapp`: separate app, likely Next.js or another full app framework if needed.
- Shared design tokens can later move into `packages/design-system`.

Why it fits:

- Excellent for content-first, SEO-oriented websites.
- Ships very little JavaScript by default.
- Allows React/Vue/Svelte islands later for interactive sections.
- Keeps the marketing website separate from future operational platform risk.
- Easy to host on static platforms.

Tradeoff:

- If the website quickly needs authenticated dashboards, complex forms, or server-heavy behavior, Astro alone is not the whole answer.

### Option B: Next.js For Website And Later Webapp

Good if we want one dominant framework from the start.

Why it fits:

- Strong path for a future webapp.
- Familiar React ecosystem.
- API routes/server components can support future forms or integrations.

Tradeoff:

- More moving parts for a mostly static first site.
- Easier to accidentally mix public marketing concerns with future private app concerns.

### Option C: Webflow

Good if non-developer marketing editing becomes the main requirement.

Why it fits:

- Fast marketing iteration.
- Built-in CMS and visual editing.
- B2B benchmark sites, including Cedar, show that Webflow can support polished enterprise sites.

Tradeoff:

- Less aligned with this local repo workflow.
- Future custom webapp and shared components would live elsewhere or require duplication.
- Export/custom integration paths can become awkward.

### Option D: WordPress

Good if the organization already has WordPress operations and wants classic CMS control.

Why it fits:

- Familiar CMS, many editors and plugins.
- Good for content-heavy sites.

Tradeoff:

- Higher maintenance and security burden.
- Less attractive for a clean repo-first static website unless WordPress is already an organizational standard.

## Recommended Stack

Use Astro for the first website.

Suggested initial stack:

- Astro
- TypeScript
- Plain CSS modules or scoped CSS with design tokens
- Minimal client-side JavaScript
- Optional later: React islands only where needed
- Static contact CTA first; form only after privacy/legal decision

Why:

- The current website is content, trust, routing, SEO, and visual clarity.
- The later platform/app should not force unnecessary complexity into the marketing site.
- Astro gives us a fast, static, maintainable first version while keeping room for future interactivity.
- Astro's official docs explicitly position it for content-driven websites such as marketing sites and emphasize server-first rendering, low client-side JavaScript, SEO, and performance.

ADR candidate:

- "Use Astro for the public website and keep future webapp as a separate app."

## Open Questions

- Does the organization require non-developer editing in the first release?
- Is there an existing hosting/deployment target?
- Will the website need a real contact form immediately, or is a mail/contact CTA enough for MVP?
- Are Donner + Partner logos, approved photos, and legal pages available?
- Should the public site be a subpage under the existing Donner + Partner domain or a separate sub-brand?

## Next-Step Options

Recommended:

1. Create a homepage wireframe concept based on this benchmark.

Alternatives:

1. Write an ADR for Astro vs Next.js vs Webflow before scaffolding.
2. Update `website-outline.md` to include the benchmark-driven section order.
3. Start implementation with Astro and use the benchmark as the design acceptance baseline.
