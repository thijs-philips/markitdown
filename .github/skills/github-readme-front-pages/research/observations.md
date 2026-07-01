# Research Notes: Best Practices from Strong GitHub Front Pages

## Core observation

The best README front pages are not generic. They are shaped by product type, audience, and the first action a visitor should take.

## Cross-cutting patterns

### 1. The first screen has one job

Strong READMEs answer what the project is, why it matters, and where to go next without asking the reader to scroll through noise.

### 2. Mature projects often route early

Well-established libraries with strong docs often keep the README concise and hand off quickly.
Newer or more opinionated frameworks use the README more actively to persuade.

### 3. Tools foreground install plus first command

For developer tools, the best front pages make installation and the first useful command almost impossible to miss.

### 4. Broad platforms route users by path

For complex products, the README works as a decision hub. The best ones separate hosted, self-hosted, local dev, and framework-specific quickstarts instead of blending them together.

### 5. User-facing apps lean on visuals and downloads

Desktop, mobile, and many web apps need screenshots, demos, compatibility notes, and download or install links much earlier than technical libraries do.

### 6. Research software needs reproducibility and citation near the front

For research repos, setup, scope, and citation are part of the front page. A `CITATION.cff` file is not an afterthought.

## Patterns by archetype

### Technical library or SDK

Typical winning pattern:
- concise hero
- docs link high on page
- install section
- small code sample
- compatibility notes
- contribution and license links

### CLI or developer tool

Typical winning pattern:
- one-line differentiator
- install command first
- first command examples
- benchmark chart only when justified
- platform support and docs

### Platform or API product

Typical winning pattern:
- broad capability summary
- screenshot or architecture cue
- choose-your-path routing
- framework quickstarts
- support routing

### Web app or open-core product

Typical winning pattern:
- screenshot-led hero
- clear try-it or self-host CTA
- outcome-focused feature summary
- lightweight local setup
- docs and community links

### Desktop or mobile app

Typical winning pattern:
- screenshots
- download matrix
- compatibility notes
- user install separated from source build

### Research software

Typical winning pattern:
- paper or project page link near top
- environment setup
- quick reproduction path
- data/model notes
- citation guidance

## Content that usually belongs outside README

- full API documentation
- exhaustive architecture detail
- long troubleshooting manuals
- every install method at equal prominence
- full governance or security policy text

## Practical implication for the skill

The skill should classify first, draft second. The most important decision is not wording. It is choosing the correct front-page job and section order.
