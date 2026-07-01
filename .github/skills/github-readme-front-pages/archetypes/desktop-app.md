# Desktop or Mobile App

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

Choose this archetype for end-user apps installed on devices:
- desktop applications
- mobile applications
- cross-platform apps
- offline-first local apps

This archetype fits patterns like LocalSend or AppFlowy, where users need visual proof, download options, and clear compatibility information.

## Primary audience and front-page job

Primary audience:
- end users deciding whether to download or install the app

Primary front-page job:
- show what the app does and make download or install friction low

## Above-the-fold defaults

Put these near the top:
- app name
- one-line explanation
- screenshot or short gallery
- download links or app store links
- supported platform summary
- brief trust signal if relevant, such as privacy-first or local-only

## Recommended section order

1. Title
2. One-line product explanation
3. Screenshots
4. Download or install matrix
5. How it works or core value
6. Compatibility notes
7. Troubleshooting or FAQ link
8. Contributing and build-from-source section
9. License

Optional:
- release channels
- localization notes
- data or privacy notes
- sync or networking explanation

## Section guidance

### Screenshots

Use screenshots generously but selectively. A single strong image is better than a cluttered gallery.

### Download matrix

Group links by platform:
- macOS
- Windows
- Linux
- iOS
- Android

If multiple formats exist, label them clearly.

### How it works

Explain enough to remove fear or confusion.
Examples:
- local network only
- no cloud account required
- end-to-end encrypted
- offline-first

### Build from source

Keep this separate from user installation. End users should not fall into contributor setup.

## What to avoid

- code-first README for an end-user app
- hiding downloads below contributor content
- mixing user install and dev build instructions together
- leaving platform support ambiguous
- using low-value badges instead of screenshots

## Inputs to collect

- app description
- screenshots
- download links or app store links
- supported platforms
- privacy or networking notes if relevant
- troubleshooting link
- source build instructions link
- docs or website URL

## Decision notes

For end-user apps, visuals and download paths usually matter more than long technical explanations. Keep the first screen user-centered.
