# Evaluation Scenarios for the Skill

## How to use these evals

Use these scenarios to test whether the skill:
- picks the right archetype
- structures the README around the right audience and CTA
- keeps the README focused instead of exhaustive
- suggests visuals, badges, and companion files appropriately
- preserves accessibility and GitHub-specific best practices

Each scenario includes a target outcome and common failure modes.

## Scenario 1: Mature library with deep docs

**Prompt:**
Create a README for a JavaScript UI library with excellent external docs. The main goal is to help developers evaluate and install it quickly.

**Expected behavior:**
- Select `archetypes/library.md`
- Keep the top concise
- Put docs and install high
- Use a small code sample instead of screenshots
- Avoid copying deep documentation into README

**Must avoid:**
- giant feature wall before install
- visual-heavy hero for a code-first library

## Scenario 2: Persuasive framework README

**Prompt:**
Draft a README for a new Python web framework that still needs to persuade developers to try it.

**Expected behavior:**
- Use library archetype but allow a stronger benefits section
- Include install and minimal example
- Add 3 to 6 outcome-focused benefits
- Keep docs link prominent

**Must avoid:**
- framework README that feels like a low-level SDK

## Scenario 3: CLI tool with speed as the main value

**Prompt:**
Write a README for a CLI dependency manager whose main differentiator is speed.

**Expected behavior:**
- Select `archetypes/cli.md`
- Put install and first commands near the top
- Include a benchmark visual only if provided or credibly described
- Keep platform support visible

**Must avoid:**
- long philosophy before the first command
- chart with no methodology note or context

## Scenario 4: Platform with hosted and self-hosted entry paths

**Prompt:**
Create a README for an open-core backend platform that offers both a managed cloud and self-hosting.

**Expected behavior:**
- Select `archetypes/platform.md`
- Add a clear "Choose your path" section
- Separate cloud, self-host, and local-dev routes
- Surface docs and support routing

**Must avoid:**
- mixing all setup paths together
- contributor setup above user onboarding

## Scenario 5: Web app with strong visual appeal

**Prompt:**
Create a README for a scheduling web app that users mostly judge by the interface and feature set.

**Expected behavior:**
- Select `archetypes/webapp.md`
- Use a screenshot high on the page
- Put demo or product CTA early
- Describe features as user outcomes

**Must avoid:**
- no visual proof
- backend-first framing for a UI-first product

## Scenario 6: Desktop app for end users

**Prompt:**
Write a README for a cross-platform desktop app that users download directly.

**Expected behavior:**
- Select `archetypes/desktop-app.md`
- Put screenshots and downloads near the top
- Separate user installation from build-from-source guidance
- Include compatibility notes

**Must avoid:**
- code-first README
- long contributor section above downloads

## Scenario 7: Research software repo

**Prompt:**
Draft a README for a paper companion repository with training scripts, evaluation code, and a preferred citation.

**Expected behavior:**
- Select `archetypes/research.md`
- Link the paper near the top
- Provide a quick reproduction path
- Mention `CITATION.cff`
- Include data and hardware notes when relevant

**Must avoid:**
- omitting scope of what the repo actually contains
- burying citation guidance

## Scenario 8: Existing README audit

**Prompt:**
Audit an existing README that starts with 18 badges, a giant roadmap, and contributor details before any install steps.

**Expected behavior:**
- identify the badge wall as a problem
- move install or download steps higher
- recommend moving roadmap detail out of the hero flow
- preserve useful legal and support links

**Must avoid:**
- rewriting everything without explaining the structural issues

## Scenario 9: Missing assets

**Prompt:**
Create a README for a web app, but screenshots and demo links are not yet available.

**Expected behavior:**
- still choose the right archetype
- draft a sensible structure
- leave concise placeholders for the missing assets
- avoid pretending screenshots or demo links exist

**Must avoid:**
- fabricated URLs or product details

## Scenario 10: Monorepo with multiple audiences

**Prompt:**
Write a root README for a monorepo containing a backend platform, docs site, SDKs, and examples.

**Expected behavior:**
- behave like a routing front page
- explain repo purpose and major folders
- point readers to the right subpaths quickly
- keep internal links relative

**Must avoid:**
- trying to merge every subproject manual into one README

## Scenario 11: Accessibility review

**Prompt:**
Review a README with vague links, missing alt text, skipped heading levels, and decorative emoji bullets.

**Expected behavior:**
- flag descriptive link text issues
- recommend proper heading hierarchy
- add useful alt text guidance
- replace decorative pseudo-bullets with real Markdown lists

**Must avoid:**
- focusing only on visual polish and missing accessibility defects

## Scenario 12: Companion file recommendations

**Prompt:**
Create a README for research software maintained by a large organization with multiple repos.

**Expected behavior:**
- recommend `CITATION.cff`
- link `CONTRIBUTING.md`, `SECURITY.md`, and `LICENSE` if relevant
- mention organization-level `.github` community health defaults when useful

**Must avoid:**
- stuffing the full policy text into the README
