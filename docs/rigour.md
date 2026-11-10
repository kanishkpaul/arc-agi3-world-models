# How the numbers are kept honest

[← Research record](README.md)

These are research results, not marketing. The practices below are why each number on this site means what it says. They describe the process; the methods themselves stay private until the papers are out.

## Pre-registration

Every experiment is written down before it runs. The entry records:

- the hypothesis and the arms;
- the data split and the compute caps;
- the metric and the number of replicates;
- a **promotion rule** and a **kill rule**.

Results are appended to that entry afterwards; the entry is never rewritten to fit them. Directions that miss their bar are killed, and their numbers are kept. The static-ARC line alone records about ten killed directions.

## Frozen splits and gated public runs

- Development, validation and confirmation splits are frozen in advance.
- A change is promoted only when it gains on development, loses **nothing** on validation, and holds on freshly generated task instances.
- Public evaluation sets are scored only at milestone gates, never in a tuning loop.
- When a public set has been seen during development, its score is labelled descriptive.

## Replication

- Headline runs are repeated; 0SR's final gate ran three times with identical answers.
- Ported code must reproduce its reference exactly. 0SR's C port matched its reference on all 6,240 paired task runs.
- ARC-AGI-3 local scores were checked against the official scorer. One run's per-game scores matched the official formula to 10⁻¹⁴.
- Two historical Virgil CX evaluations were rerun from frozen commits on 2026-09-24 and reproduced exactly.

## Separate protocols, separate rows

Public-game research runs, notebook-style competition runs and the Kaggle leaderboard (which scores hidden games) are reported in separate tables. A public-game score is never presented as a leaderboard result. The gap is large: an entry that scored 49.5% on the 25 public games scored 6.15 on the leaderboard.

## Checkable tables

Every aggregate on this site comes from a sanitized table in [`evidence/`](../evidence/). The tables are recomputed by `scripts/verify_results.py` in CI, and the README figures are generated from the same records by `scripts/make_figures.py`. This verifies the arithmetic and internal consistency. It does not rerun private solvers.
