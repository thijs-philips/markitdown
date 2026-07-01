# Platform or API Product

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

Choose this archetype for broad products with multiple capabilities, deployment paths, or developer entry points:
- backend platforms
- API products
- open-core infrastructure platforms
- data or AI application backends
- self-hosted plus managed offerings

This archetype fits README patterns like Supabase or Appwrite, where the repo front page must orient users before routing them into the right setup path.

## Primary audience and front-page job

Primary audience:
- developers evaluating the product and deciding how to start

Primary front-page job:
- explain the platform clearly and route readers into the right entry path

## Above-the-fold defaults

Put these near the top:
- product name
- one-line platform explanation
- key capabilities summary
- docs link
- quickstart or getting started link
- hosted vs self-hosted choice if relevant
- screenshot or architecture visual if it reduces ambiguity

## Recommended section order

1. Title
2. One-line explanation
3. Capability summary
4. Choose your path section
   - hosted
   - self-hosted
   - local dev
5. Quickstarts by framework or use case
6. Visual overview or screenshot
7. Core features or architecture summary
8. Support and community routing
9. Contribution, security, and license links

Optional:
- deployment options
- comparison or migration notes
- roadmap or ecosystem links

## Section guidance

### Capability summary

Summarize the product in reader language, not internal org language.
Examples:
- auth
- database
- storage
- functions
- messaging
- analytics

### Choose your path

This section is critical when the repo serves multiple starting modes.
Do not make readers infer whether they should use the hosted product, self-host, or develop locally.

### Quickstarts

Group quickstarts by framework, platform, or workflow only when the grouping is genuinely helpful.

### Visual overview

A dashboard screenshot or architecture diagram is useful when the product surface is broad. Add concise alt text and captions where needed.

### Support routing

Separate clearly:
- bug reports
- feature discussions
- community help
- security issues
- operational incidents if applicable

## What to avoid

- treating every audience as equally primary on the first screen
- putting contributor setup above user quickstarts
- listing twenty capabilities without explaining why they matter
- mixing managed and self-hosted instructions together
- dumping full architecture docs into README

## Inputs to collect

- product description
- capability list
- hosted offering URL if any
- self-host path if any
- quickstart links
- framework guides if any
- docs URL
- screenshot or architecture asset
- support channels
- security contact path

## Decision notes

If the product is complex, routing matters more than completeness. The README should help readers pick a lane, not explain every subsystem.
