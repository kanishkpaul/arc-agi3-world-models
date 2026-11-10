# Public scope

[← Research record](README.md)

This repository is the public record of the work until the papers are released. It publishes **what was achieved and under what conditions**. It does not publish **how**.

## Included

- Measured outcomes for every research line, from April to November 2026, with the conditions needed to interpret them.
- Sanitized per-game tables, leaderboard records, aggregate records, checksums and arithmetic checks (`evidence/results-v1`, `evidence/results-v2`).
- A live, unedited video of 0SR solving public ARC evaluation tasks.
- The LS20 replayable trace and result card.
- The offline perception, logging, prediction-protocol and replay-evaluation library, `arc3_substrate`, with its tests and example.
- Figures generated from the published records.

## Private until publication

The following are not included:

- solver and agent source code;
- models, whether learned or hand-authored;
- planners, search and induction logic;
- configurations and prompts;
- solution banks;
- action traces beyond LS20;
- per-task result lists;
- the analyses and arguments of papers in preparation.

Third-party code, data and game source are never redistributed here.

There is no commitment to release the private material. Paper releases will decide what becomes public.

## What can be checked

- The library runs, and its test suite passes in CI.
- The LS20 record replays against the official environment.
- Every published table recomputes to its stated aggregates, and every figure is generated from those same records.

The private systems themselves cannot be re-executed from this repository. Their aggregates are documented measurements, labelled with the evidence level described in the [evaluation guide](evaluation.md).
