# Accessibility and GitHub Markdown Mechanics

## Contents
- Writing principles
- Heading structure
- Link text
- Images and alt text
- Lists and emoji
- Tables and collapsed sections
- Internal navigation and file placement
- Quick audit checklist

## Writing principles

A README should be easy to scan, easy to understand, and easy to navigate with assistive technology.
Use plain language and keep sections purposeful.

## Heading structure

Use one `#` title, then descend in order with `##`, `###`, and so on.
Do not skip heading levels without a good reason.

Good:
- `# Project`
- `## Install`
- `### macOS`

Bad:
- `# Project`
- `#### Install`

Clear headings also improve GitHub's auto-generated outline.

## Link text

Write links so they make sense in isolation.
Prefer:
- `Read the quickstart`
- `API reference`
- `Security policy`

Avoid:
- `here`
- `this`
- `learn more`

## Images and alt text

Every meaningful image should have short, specific alt text.
Include the important context, not generic filler.

Good alt text:
- `Screenshot of the web app booking flow showing time zone selection`
- `Bar chart comparing warm-cache install time across package managers`

If an image needs longer explanation, keep the alt text short and put the long explanation nearby or in a `<details>` block.

## Lists and emoji

Use real Markdown lists, not decorative pseudo-bullets.
Use emoji sparingly. Too many emoji can become noisy for screen readers and for visual scanning.

## Tables and collapsed sections

Tables are useful for:
- platform support
- feature comparison
- download matrices

`<details>` blocks are useful for secondary material such as:
- alternate install methods
- long troubleshooting notes
- advanced configuration examples

Do not hide the main onboarding path inside collapsed content.

## Internal navigation and file placement

Use relative links for files in the same repository.
If the repo includes multiple README files, remember GitHub surfaces README files in `.github`, then root, then `docs`.
Keep the main repository front page in the location that matches the repository's needs.

## Quick audit checklist

- Is the heading hierarchy clean?
- Do links make sense out of context?
- Do images have useful alt text?
- Are lists real lists?
- Is emoji restrained?
- Are tables readable and necessary?
- Is the first action visible without opening `<details>`?
- Are internal links relative?
