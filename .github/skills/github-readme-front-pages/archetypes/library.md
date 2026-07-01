# Technical Library or SDK

## Contents
- Use when
- Primary audience and front-page job
- Above-the-fold defaults
- Recommended section order
- Section guidance
- What to avoid
- Inputs to collect
- Decision notes

## Use when

Choose this archetype for code-first projects that developers embed into their own software:
- language libraries
- SDKs
- frameworks
- modules or packages
- infrastructure client libraries

This archetype fits projects like React or FastAPI style READMEs: clear framing, fast onboarding, and a handoff to deeper docs.

## Primary audience and front-page job

Primary audience:
- developers evaluating whether to adopt the project

Primary front-page job:
- explain the value quickly and get the reader to a working install or example

## Above-the-fold defaults

Put these near the top:
- project name
- one-sentence value proposition
- a very small set of badges if useful
- docs link
- installation command or link to install section
- one short proof point such as a tiny example or 2 to 5 key benefits

If the project is already mature and has deep docs, keep the top lighter and hand off early.
If the project needs persuasion, use the README to sell the value more directly.

## Recommended section order

1. Title
2. One-line value proposition
3. Key links: docs, API reference, examples, changelog
4. Install
5. Minimal example
6. Why use this library or core features
7. Compatibility or supported versions
8. Contributing and support links
9. License

Optional:
- migration notes
- ecosystem links
- FAQ
- benchmarks when performance is central

## Section guidance

### Title and value proposition

State the category and the benefit.
Good pattern:
- "A Python web framework for building fast APIs"
- "A JavaScript library for declarative user interfaces"

### Install

Show the default install path first. Do not place six package managers on equal footing unless the repo truly supports them equally.

### Minimal example

The example should fit on screen and prove the core idea. If the example becomes a tutorial, move it into docs.

### Features or benefits

Summarize the 3 to 6 most decision-relevant benefits.
Examples:
- type safety
- speed
- simple mental model
- extensibility
- ecosystem compatibility

### Compatibility

Include supported runtimes, language versions, or platform notes where adoption risk is real.

### Docs handoff

Always include the docs link near the top if the project has serious documentation.

## What to avoid

- giant marketing paragraphs before install
- a long internal architecture dump before usage
- screenshots that do not help a code-first project
- showing advanced configuration before the first success path
- burying the docs and examples links

## Inputs to collect

- package or module name
- supported language versions
- default install method
- fastest example that proves the project works
- docs link
- API reference link
- examples repo or docs link
- compatibility notes
- migration guide or changelog if relevant

## Decision notes

Use a screenshot only when the library creates visible UI or dashboards. Otherwise, a tiny code sample is usually better.

If the project is a framework, a stronger benefits section near the top is justified. If it is a low-level SDK, keep the README more concise and operational.
