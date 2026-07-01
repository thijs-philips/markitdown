# Support, Community, and Trust Signals

## Contents
- Why routing matters
- Support paths to surface
- Contribution paths
- Security and governance files
- Organization defaults
- Example routing patterns
- Pitfalls

## Why routing matters

A good README helps visitors know where to go next when they need help. It reduces issue noise and makes the project feel maintained.

## Support paths to surface

Typical channels:
- documentation for self-serve help
- GitHub Issues for bugs
- GitHub Discussions or forum for questions and ideas
- chat community for informal help
- security policy or contact path for vulnerabilities
- operational contact path for hosted products if one exists

Do not point all traffic to Issues if that is not how the project is actually run.

## Contribution paths

If the repo accepts contributions, make that discoverable with:
- a short contribution invitation
- link to `CONTRIBUTING.md`
- coding or style expectations if they are critical
- good-first-issue link if available

Keep contributor detail brief in the README unless contributors are the main audience.

## Security and governance files

When relevant, link to:
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `CITATION.cff`

These files improve trust but should not overwhelm the front page.

## Organization defaults

If the repo belongs to an organization with many repositories, note that default community health files in a public `.github` repository can supply shared policies.

## Example routing patterns

### Platform product
- Docs: setup and product usage
- Issues: bugs
- Discussions: usage questions and feature ideas
- Security: private reporting path

### Research repo
- Docs: reproduction guide
- Issues: reproducibility bugs or code defects
- Citation: `CITATION.cff`

### End-user app
- Downloads: first action
- FAQ or troubleshooting: common user issues
- Issues: confirmed bugs

## Pitfalls

- no help path at all
- using README prose instead of real policy files
- making vulnerability reporting public by default when private reporting is expected
- writing a contribution section that is longer than the getting-started section
