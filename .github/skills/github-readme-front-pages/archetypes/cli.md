# CLI or Developer Tool

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

Choose this archetype for tools users run directly from the terminal or developer environment:
- command-line tools
- package managers
- linters
- build tools
- deployment tools
- local automation tools

This archetype fits README patterns like `uv`: show why the tool matters, how to install it, and what the first useful command looks like.

## Primary audience and front-page job

Primary audience:
- developers deciding whether to install and use the tool

Primary front-page job:
- move the user from evaluation to first command as fast as possible

## Above-the-fold defaults

Put these near the top:
- project name
- one-line differentiator
- install method
- first command or two
- docs link
- benchmark chart if performance is the core claim

## Recommended section order

1. Title
2. One-line value proposition or differentiator
3. Install
4. First commands or quickstart
5. Why this tool or feature highlights
6. Platform support
7. Configuration or common workflows
8. Documentation links
9. Contributing and support
10. License

Optional:
- benchmark section
- migration from another tool
- shell completion setup
- FAQ

## Section guidance

### Differentiator

Make the main reason to switch obvious. Examples:
- faster
- simpler
- more reproducible
- fewer dependencies
- safer defaults

### Install

Prefer one recommended path first. Add alternatives after it.

### First commands

Show commands that solve a real beginner task.
Examples:
- install package
- initialize project
- run lint
- sync dependencies
- deploy preview

### Feature highlights

Keep feature bullets focused on outcomes, not only internal implementation.

### Platform support

State operating systems, shells, language versions, or architecture constraints when they matter.

## What to avoid

- long philosophy before installation
- too many shell snippets before explaining the tool's purpose
- charts without context
- hiding the docs link below a very long examples section
- configuration detail that belongs in docs

## Inputs to collect

- package name or binary name
- install methods
- supported operating systems or runtimes
- first useful commands
- docs link
- benchmark claims and evidence if applicable
- migration notes if the tool replaces another workflow

## Decision notes

Use a benchmark visual only if the claim is central and credible.
If the tool's main value is reliability or ergonomics rather than speed, prioritize clear command examples over charts.
