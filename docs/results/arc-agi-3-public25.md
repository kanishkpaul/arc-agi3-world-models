# ARC-AGI-3 · the 25 public games

[← Research record](../README.md) · [Evaluation guide](../evaluation.md)

ARC-AGI-3 is a set of interactive turn-based games. An agent starts each game with no instructions and has to work out the controls, the rules and the goal by playing. Scores are action-efficiency percentages: completing a level counts for more the closer the agent comes to the human baseline's action count. A score is **not** the percentage of games solved.

## Every recorded run

| Run | Date | Protocol | Mean score | Levels (of 183) | Full games won (of 25) |
| :--- | :--- | :--- | ---: | ---: | ---: |
| **Zerostar · configuration C** | 2026-11-01 | single pass, Kaggle notebook | **49.50%** | **106** | 7 |
| Zerostar · configuration B | 2026-10-31 | single pass, Kaggle notebook | 46.10% | 105 | 8 |
| Zerostar · configuration A | 2026-10-31 | single pass, Kaggle notebook | 42.75% | 102 | 7 |
| [Virgil CX · research regression](virgil-cx.md#research-regression) | 2026-07-19 (rerun 09-24) | exploration plus fresh replay | 2.23% | 16 | 0 |
| Virgil CC floor v3 | 2026-07-14 | local public-game run | 2.02% | — | — |
| Virgil CC floor v2 | 2026-07-14 | local public-game run | 1.99% | — | — |
| Virgil CC floor v1 | 2026-07-14 | local public-game run | 1.79% | — | — |
| [Virgil N-pass](npass.md) | 2026-09-12 | per-game best of discovery and replay | 1.44% | 17 | 0 |
| [Virgil CX · competition-style](virgil-cx.md#competition-style-public-run) | 2026-07-19 (rerun 09-24) | one construction per game, restricted resets | 0.56% | 17 | 0 |
| [TCCA](prototypes.md#tcca) | 2026-04-18 | offline benchmark | 0.26% | 4 | 0 |

Zerostar was built on a public community baseline notebook. Its configurations are not described here. The Virgil CC floor runs logged only aggregate scores, so they have no level counts.

## Reading the table

- **Public is not hidden.** These are the 25 public games, which an entrant can study. The Kaggle leaderboard scores hidden games. The configuration-C notebook scored 49.50% here and 6.15 on the [leaderboard](kaggle.md).
- **Noise.** Each Zerostar configuration is one draw. The per-game standard deviation is about 25 points, and the paired standard error between configurations is about 5. The differences among A, B and C are therefore within run-to-run noise.
- **Protocols differ.** Rows from different lines use different budgets, reset rules and replay allowances. They form a record, not a controlled comparison.

Per-game rows for the Zerostar and Virgil CX runs are in [`public25-per-game.csv`](../../evidence/results-v2/public25-per-game.csv). The TCCA and N-pass tables are in [`results-v1`](../../evidence/results-v1/). All of them are recomputed by `scripts/verify_results.py`.
