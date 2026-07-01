# Research or Scientific Software

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

Choose this archetype for repositories whose value depends on reproducibility, methodology, or citation:
- research software
- benchmark repos
- paper companion code
- datasets or model repos with executable code
- scientific workflows

This archetype should help readers understand what the artifact is, how to reproduce results, and how to cite it.

## Primary audience and front-page job

Primary audience:
- researchers, practitioners, or reviewers trying to reproduce, evaluate, or cite the work

Primary front-page job:
- explain the artifact, make a first reproduction path possible, and route users to citation and methodology material

## Above-the-fold defaults

Put these near the top:
- project name
- one-line problem statement
- link to paper, preprint, or project page if available
- quick reproduction or install link
- citation guidance link

## Recommended section order

1. Title
2. One-line summary and scope
3. Links to paper, docs, dataset, or model cards
4. Environment setup
5. Minimal reproduction or quickstart
6. Repository layout or experiment entry points
7. Data, model, and evaluation notes
8. Citation guidance
9. License and contribution notes

Optional:
- hardware requirements
- expected outputs
- benchmark table
- limitations and caveats

## Section guidance

### Scope statement

Be explicit about what the repo contains.
Examples:
- training code only
- inference only
- paper reproduction scripts
- dataset preparation plus evaluation

### Quick reproduction

Give one path that lets a reader validate the repo works, even if the full paper pipeline is larger.

### Data and model notes

Link to datasets, checkpoints, licenses, and any access restrictions.

### Citation guidance

If the software should be cited, surface the preferred citation path. A `CITATION.cff` file is especially useful for this archetype.

## What to avoid

- vague claims about reproducing results without concrete steps
- no statement of what is and is not included
- forcing readers to inspect code before finding the paper or citation
- burying hardware or data access constraints

## Inputs to collect

- project summary
- paper or project page link
- setup requirements
- quick reproduction command
- dataset and model links
- expected output artifacts
- citation details
- license and usage constraints

## Decision notes

This README often needs stronger pointers to external artifacts than other archetypes. Reproducibility and citation are part of the front page, not only an appendix.
