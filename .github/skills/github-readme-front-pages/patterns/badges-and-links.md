# Badges, Links, and Companion Files

## Contents
- Badge rules
- High-value links near the top
- Relative links inside the repo
- Companion files worth surfacing
- Link text guidance
- Small checklists

## Badge rules

Badges are useful when they answer one of these questions quickly:
- Is the project maintained?
- What version is current?
- What is the license?
- Where are releases, docs, or community channels?

Common high-value badges:
- version or release
- CI status
- license
- docs
- chat or community

Use only the badges that matter to first-time visitors. Most repos do not need more than 3 to 5 badges near the top.

Avoid:
- vanity badges with no decision value
- duplicate badges for the same signal
- large multi-row badge walls

## High-value links near the top

Good top-level links include:
- documentation
- quickstart
- API reference
- demo
- download page
- self-host guide
- changelog
- contributing guide

Pick the minimum set that helps the primary audience act.

## Relative links inside the repo

For repo-internal files, prefer relative links.
Examples:
- `[Contributing](CONTRIBUTING.md)`
- `[Docs](docs/getting-started.md)`
- `[Security policy](.github/SECURITY.md)`

Relative links survive forks, local clones, and branch changes more gracefully than absolute GitHub URLs.

## Companion files worth surfacing

Recommend companion files when they materially improve the repo front page:

- `LICENSE` for legal clarity
- `CONTRIBUTING.md` for contributor onboarding
- `CODE_OF_CONDUCT.md` for community expectations
- `SECURITY.md` for vulnerability reporting
- `CITATION.cff` for research software and citable tools
- `CHANGELOG.md` for active release-driven projects

Do not copy the full content of these files into the README. Link to them.

## Link text guidance

Link text should make sense on its own.
Prefer:
- `Read the installation guide`
- `View the API reference`
- `Contribution guidelines`

Avoid:
- `click here`
- `this link`
- `more`

## Small checklists

### Badge check
- Does each badge add real value?
- Can a newcomer act on it?
- Is the total row visually calm?

### Link check
- Are the top links aligned with the main CTA?
- Are internal links relative?
- Are companion files discoverable without clutter?
