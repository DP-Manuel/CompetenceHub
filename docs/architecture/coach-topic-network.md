# Coach Topic Network

Status: MVP foundation, 2026-07-31

## Purpose

The public Coach area must remain understandable as the network grows. Topics
must not be assigned to exactly one Coach: one Coach can cover several topics,
and one topic can be supported by several Coaches with different professional
perspectives.

The website therefore uses a many-to-many model and presents topics as filters
or entry points. It must not draw every possible Coach-to-topic connection at
the same time.

## Domain Model

### Coach

- stable ID or slug
- public name and role
- approved profile route
- approved image and publication state
- detailed focus statements
- zero or more canonical topic IDs

### Topic

- stable ID or slug
- public label
- short orientation text
- icon
- publication state
- optional future topic route

### CoachTopic

The relation connects one Coach and one Topic.

Future database fields may include:

- `coach_id`
- `topic_id`
- `priority`
- `context` such as company, private customer, or both
- `evidence_or_qualification_note`
- `approval_status`
- `valid_from` and `valid_to`

The public frontend must use only approved relations. Internal evidence or
private qualification notes must not be rendered publicly.

## Current Static Implementation

`apps/website/src/data/coaches.ts` is the single safe source for the public
Coach list, preview data, canonical topics, and current topic assignments.

The start-page carousel and `/coaches` consume this shared source. This avoids
maintaining names, images, profile links, and topic relations in multiple page
files.

The first topic set is derived only from already public profile focuses:

- Leadership
- Teams and conflicts
- Health and prevention
- Recruiting and potential
- Rhetoric and sales
- Psychological consultation

The taxonomy can grow, but new synonyms should first be mapped to an existing
canonical topic where possible.

## Public Interaction

- The default Coach view shows every approved profile.
- A topic filter shows every Coach assigned to that topic.
- Profiles are not duplicated when they match several topics.
- The URL hash `#thema-<topic-id>` preserves a selected topic without creating
  a new route.
- Buttons expose their state with `aria-pressed`; filtering changes are
  announced through an `aria-live` status.
- Without JavaScript, all approved profiles remain visible.

## Growth Path

1. Keep the in-page filter while the network and topic set are still compact.
2. Add dedicated routes such as `/themen/fuehrung` only when a topic has enough
   approved first-party substance, a clear audience/use case, and more value
   than a filtered list.
3. Let topic routes link to all matching Coaches, services, formats, and
   approved evidence instead of acting as thin SEO pages.
4. Move the same IDs and relations into the future database/API without
   changing public URLs or frontend labels unnecessarily.

## Visual Rules

- Show a topic layer before the profile layer.
- Highlight one selected topic and its matching profiles.
- Do not render a permanent all-to-all graph; it becomes unreadable as both
  topics and Coaches grow.
- Use hover/focus connections only for the current selection.
- Keep the full profile card as the authoritative destination.
- On mobile, use a single-column filter control and a normal profile list.

## Open Decisions

- Final owner and approval workflow for topic assignments.
- Whether topic pages become necessary and which topic qualifies first.
- Whether company/private context needs a second filter later.
- Whether services and formats share the same taxonomy or use linked,
  separately governed taxonomies.
