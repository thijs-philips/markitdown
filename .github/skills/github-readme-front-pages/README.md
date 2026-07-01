# GitHub README Front Pages Skill Bundle

This bundle packages research, guidance, templates, and evaluation cases for a Claude Skill that helps create strong GitHub `README.md` front pages.

The bundle is intentionally archetype-based rather than one-size-fits-all. A README for a technical library should not look like a README for a desktop app, and a platform product should not be framed like a research repo.

## Included files

- `SKILL.md` - main skill entrypoint with classification and workflow
- `archetypes/` - section stacks and decision rules by project type
- `patterns/` - reusable guidance for hero sections, visuals, links, support, and accessibility
- `templates/` - starter README skeletons
- `evals.md` - evaluation scenarios and rubrics
- `research/` - source notes and best-practice observations used to build the bundle

## Archetypes covered

- Technical library or SDK
- CLI or developer tool
- Platform or API product
- Web app or open-core product
- Desktop or mobile app
- Research or scientific software

## Design intent

This skill is built around a few durable ideas:

1. Treat the README as a landing page, not a full manual.
2. Optimize the first screen for clarity and next action.
3. Route readers by audience and task.
4. Keep long material in docs or companion files.
5. Use visuals when they remove uncertainty.
6. Keep links, headings, and images accessible.

## Notes

- `SKILL.md` stays concise and points directly to one-level-deep reference files.
- Reference files include contents sections so Claude can scan them quickly.
- Templates use relative links and placeholder blocks to reduce brittle repository-specific assumptions.
