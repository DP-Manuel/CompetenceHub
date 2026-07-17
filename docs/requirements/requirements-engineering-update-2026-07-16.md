# Requirements Engineering Update

Last updated: 2026-07-16

## Source

- Local source: `Quellen/Requirements Engineering.docx`
- Coach material: approved local intake under `Quellen/Coach`
- The source material remains excluded from Git.

## Confirmed Direction

- Competence Hub is primarily an intermediary between companies and coaches.
- Coaches and their individual expertise are the core of the public offer.
- Network quality and fit are more important than the number of profiles.
- Relevant formats include Livecoaching, Businesscoaching, psychological
  consultation in a professional context, supervision, workshops, and talks.
- Offers may take place on site in the Würzburg region or digitally, depending
  on coach, topic, and target group.
- The public website should retain visitors through useful, interactive content.
  Leadership, stress, and AI self-checks are candidate topics.

## Website Consequences

- Describe Competence Hub as a curated broker, not as the direct provider of
  every coaching service.
- Make coach profiles, qualifications, topics, and suitable use cases more
  prominent.
- Keep all contact and booking requests routed through Competence Hub instead of
  publishing private coach contact details.
- Clearly distinguish professional psychological consultation from
  psychotherapy, medical advice, and crisis services.
- Add quiz/self-check functionality only after content ownership, result wording,
  privacy, analytics, and accessibility are defined.

## New Coach Intake

- Christian Galvano remains the first profile with an approved portrait.
- Elisabeth Schwabauer: psychology, occupational psychological consultation,
  mental workload, team development, and conflict clarification. No portrait is
  currently available for publication.
- Carolin Hupp: sports science, health and training management, movement,
  prevention, and relaxation. A public professional website was supplied, but no
  portrait was provided.
- Private source contact details are not copied into the website or project docs.
- Final wording, current availability, portrait rights, and publication approval
  must be confirmed before launch.

## Price Input Requiring Decision

- Workshop input: `850 EUR standard / 680 EUR discount`.
- Talk input: `200 EUR` with a minimum group size of 25.
- The source alternates between a flat workshop price and per-person comparisons.
  Prices must not be published until unit, VAT treatment, included catering/room,
  cancellation rules, discount eligibility, and coach remuneration are approved.

## Future Administration MVP

First candidate functions:

- Internal user login and user management.
- Company and company-contact management.
- Coach and public-profile management.
- Coaching service and assignment management.
- Company feedback connected to company, service, and assignment.

The public Astro website remains database-free. Operational data belongs behind
an authenticated backend API in the later webapp.

## Open Decisions

- Is the new server development/staging or already intended for production?
- Is MySQL or MariaDB installed, and which supported version is available?
- Which internal roles may create users, companies, coaches, and assignments?
- Who approves coach profile wording, qualifications, images, and availability?
- What exactly does `Livecoaching` mean commercially and operationally?
- Are supervision and psychological consultation already approved offers?
- Which price unit and inclusions are authoritative?
- Which self-check should be the first interactive website format?
