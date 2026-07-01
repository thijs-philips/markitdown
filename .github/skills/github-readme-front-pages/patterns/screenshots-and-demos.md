# Screenshots, Demos, and Visual Proof

## Contents
- When visuals help
- What kind of proof fits each archetype
- Screenshot guidance
- Demo and GIF guidance
- Benchmark chart guidance
- Captions and alt text
- Pitfalls

## When visuals help

Use visuals when they remove uncertainty faster than text.
Common cases:
- apps with graphical interfaces
- products with broad dashboards or admin consoles
- tools whose main claim is performance
- research repos with result visuals that need interpretation

Do not add visuals just because they look impressive.

## What kind of proof fits each archetype

### Library
- tiny code example
- architecture sketch only if needed
- screenshot only for UI libraries

### CLI
- shell snippet
- benchmark chart if speed is core
- short terminal capture only if it clarifies a workflow

### Platform
- dashboard screenshot
- architecture overview
- framework quickstart matrix

### Web app
- screenshot or short gallery
- demo link
- result-oriented before-and-after visual when relevant

### Desktop or mobile app
- screenshot gallery
- download matrix
- small workflow illustration if networking or sync behavior is unusual

### Research software
- benchmark table or output visual
- pipeline diagram if reproducibility depends on it

## Screenshot guidance

Pick screenshots that answer these questions:
- What does the product look like?
- What is the core interaction?
- What important state should the viewer understand?

Prefer one strong image over many weak ones.
If using multiple images, label them clearly.

## Demo and GIF guidance

Use a demo link when the product benefits from exploration.
Use GIFs sparingly. They can be large, distracting, or inaccessible if they auto-loop without context.

## Benchmark chart guidance

Only use charts if:
- performance is a key adoption reason
- the chart is honest and interpretable
- axes, workload, and comparison context are clear

Place performance methodology in docs if the full explanation is long.

## Captions and alt text

For every visual, provide concise alt text.
Good alt text examples:
- `Screenshot of the dashboard showing team calendars and booking rules`
- `Bar chart comparing dependency resolution time across three tools`
- `Screenshot of the desktop app transfer screen showing two nearby devices`

Use captions when the reader needs extra interpretation.

## Pitfalls

- decorative screenshots with no explanatory value
- image carousels that push install info too far down
- charts without units or labels
- giant GIFs for a simple point a static image could make
- no alt text
