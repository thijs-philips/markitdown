---
name: github-readme-front-pages
description: Create or improve a GitHub README.md that acts as a project's front page. Use when users want to write, redesign, audit, benchmark, or critique a repository README, choose a README structure by project type, or decide what sections, visuals, badges, docs links, install steps, download links, demos, contribution links, or community files belong on the front page.
---

# GitHub README Front Pages

This skill helps create README files that work like good project front pages on GitHub. It treats the README as an audience-aware landing page, not as a full product manual.

A strong README should quickly answer:
- What is this project?
- Why is it useful?
- What should the visitor do next?

Use this skill for new READMEs, rewrites, structure reviews, and front-page audits.

## Success criteria

Aim for these outcomes:
1. The first screen explains the project in plain language.
2. The primary call to action is obvious.
3. The section stack matches the project archetype.
4. README content stays focused on getting started and navigation.
5. Long or specialized content is routed into docs or companion files.
6. Links, headings, visuals, and lists remain accessible.

## Inputs to gather

Collect only the information needed to draft the front page:
- project name
- project type
- primary audience
- primary call to action
- install, run, or download paths
- supported platforms or environments
- docs, demo, app store, or homepage links
- screenshots, benchmark charts, or architecture visuals if relevant
- support and community channels
- license and contribution info
- whether citation guidance matters

If some inputs are missing, do not block. Make the best grounded assumptions you can, call them out briefly, and leave short placeholders only where facts are genuinely unavailable.

## Project classification

Choose one primary archetype before drafting.

- Technical library or SDK -> read `archetypes/library.md`
- CLI or developer tool -> read `archetypes/cli.md`
- Platform or API product -> read `archetypes/platform.md`
- Web app or open-core product -> read `archetypes/webapp.md`
- Desktop or mobile app -> read `archetypes/desktop-app.md`
- Research or scientific software -> read `archetypes/research.md`

Then read pattern files only as needed:
- Hero and first screen choices -> `patterns/hero-sections.md`
- Badges, links, companion files -> `patterns/badges-and-links.md`
- Screenshots, demos, benchmark visuals -> `patterns/screenshots-and-demos.md`
- Help, contribution, community routing -> `patterns/support-and-community.md`
- Accessibility and GitHub Markdown mechanics -> `patterns/accessibility.md`

Use templates only after classifying the archetype:
- Small technical repo -> `templates/concise-readme.md`
- CLI or tool -> `templates/cli-readme.md`
- Platform or API product -> `templates/platform-readme.md`
- Visual product or end-user app -> `templates/visual-product-readme.md`
- Research software -> `templates/research-readme.md`

## Workflow

Follow this order.

### 1. Identify the front-page job

Determine who the README must serve first.

Typical primary jobs:
- convince a visitor to try the project
- help a developer install and run it
- route readers to docs, demos, or downloads
- help contributors understand how to engage
- help researchers cite and reproduce results

Pick one primary job. Secondary jobs can appear later in the document.

### 2. Choose the primary audience

Use the most likely first visitor:
- evaluator deciding whether the project is relevant
- developer deciding whether to adopt it
- operator deciding whether to self-host it
- end user deciding whether to download it
- researcher deciding whether to reproduce or cite it

Write the top section for that audience, not for everyone at once.

### 3. Choose the primary call to action

Decide the one action the front page should make easiest.

Examples:
- install package
- read docs
- run quickstart
- open demo
- download app
- self-host
- join community
- cite paper

Place that call to action in the first screen or immediately after it.

### 4. Build the section stack

Use the archetype file to choose the default order. Keep only sections that actively help the reader make progress.

Good candidates include:
- title and one-line value proposition
- docs or demo links
- install or download instructions
- minimal quickstart
- screenshot or benchmark visual
- feature summary
- architecture or capability overview
- platform compatibility
- support and contribution routing
- license and citation links

### 5. Keep the README focused

Do not turn the front page into a full manual.

Move long material into:
- docs site
- `docs/`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CITATION.cff`
- architecture docs
- API reference

The README should still link to those files clearly.

### 6. Draft with progressive disclosure

For the README itself:
- keep the narrative tight
- put critical information high
- use short sections and direct headings
- use relative links for repo-internal navigation
- use `<details>` only for truly secondary material

For the skill output:
- draft the README first
- then suggest companion files only if they materially improve the repo front page

### 7. Validate before finalizing

Run this checklist:
- Does the first screen explain what the project is?
- Is the main next action obvious?
- Does the section order fit the archetype?
- Are install, run, or download steps concrete?
- Are docs, demo, and help routes easy to find?
- Are there too many badges?
- Are screenshots or charts actually useful?
- Are internal links relative?
- Are headings, alt text, and link labels accessible?
- Should some content move out of README into docs or companion files?

## Front-page rules that apply across archetypes

### Keep the first screen high signal

The first visible area should usually include:
- project name
- one-line explanation
- one or two high-value links or actions
- only the most meaningful badges or proof points

### Do not bury the first useful action

Visitors should not have to scroll through a wall of badges, a giant feature manifesto, or contributor details before they can start.

### Prefer proof over hype

Use concrete evidence such as:
- a minimal working example
- a screenshot of the product
- a benchmark chart when performance is a core claim
- a supported platforms matrix
- a docs link that lands in a real quickstart

### Route by audience when necessary

If the repository serves multiple audiences, split paths cleanly. Common splits:
- hosted vs self-hosted
- user install vs developer setup
- evaluate vs contribute
- quickstart vs deep docs

### Be selective with badges

Badges are useful when they communicate status, version, license, or community entry points. Avoid a badge wall.

### Prefer relative links inside the repo

Use relative paths for files in the same repository. This is more robust for forks, branches, and local clones.

## Rewrite mode for existing READMEs

When improving an existing README:
1. Keep factual project details intact.
2. Remove repetition and low-signal sections.
3. Reorder sections around the primary audience and CTA.
4. Move long detail into docs or companion files.
5. Keep maintainer-specific content low unless contributors are the main audience.
6. Preserve important legal, support, and governance links.

## Output format

Produce:
1. the README draft in Markdown
2. a short note listing assumptions or missing facts
3. optional recommendations for companion files if useful

Do not add filler. Do not force sections that do not fit the project. Do not imitate one famous repo blindly when the product shape is different.

## Common mistakes to avoid

- Writing for contributors when the main audience is evaluators or users
- Putting long architecture or API detail before the quickstart
- Using screenshots for libraries that are better explained by code
- Using code samples for end-user apps when screenshots or download links are the real first need
- Putting every possible install method on equal footing
- Hiding the docs link below the fold
- Using vague headings like "Overview" everywhere
- Leaving broken, branch-specific, or absolute internal links
- Using inaccessible link text like "here" or "click this"

## Evaluation

Use `evals.md` to test the skill against representative scenarios before expanding the instructions further.
