# ARC Prize 2026 · Kaggle leaderboard

[← Research record](../README.md) · [Evaluation guide](../evaluation.md)

ARC Prize 2026 ran ARC-AGI-3 as a Kaggle code competition. Every submitted notebook was re-run by Kaggle on **hidden games** the entrant never sees, under a fixed GPU and time budget. That makes the leaderboard the one place where agents from different teams are measured on the same unseen games.

## Best entry

| Entry | Leaderboard score | Rank |
| :--- | ---: | ---: |
| **Zerostar attempt 1** · October 31, 2026 | **28.40** | **1,377 of 5,012** |

Zerostar was built on a public community baseline notebook. The changes made to that baseline are private.

## Every recorded entry

| Date | Entry | Score |
| :--- | :--- | ---: |
| 2026-04-05 | TCCA submission 1 | 0.17 |
| 2026-04-11 | TCCA submission 2 | 0.16 |
| 2026-07-12 | Virgil CC floor v1 | 0.21 |
| 2026-07-13 | Virgil CC floor v2 | 0.21 |
| 2026-09-24 ¹ | Virgil CX competition-mode notebook | 0.06 |
| 2026-10-30 ² | Virgil CC floor v3 | 0.23 (rank 3,492 of 4,994) |
| 2026-10-31 | Zerostar attempt 1 | **28.40** (rank 1,377 of 5,012) |
| 2026-11-01 | Zerostar attempt 2 | 20.27 |
| 2026-11-03 | Zerostar attempt 3 | 6.15 |

¹ Date of the summary that records the score; the submission date is not preserved.
² Date of the leaderboard snapshot that shows the score.

The leaderboard ranks a team by its best entry, so only that entry has a rank of its own.

## Reading these numbers

- **Which leaderboard.** All scores are from the Kaggle public leaderboard. That board scores the public share of the hidden game set while the competition runs. No final private-leaderboard score is recorded here.
- **Noise.** One submission is one draw. Identical notebooks varied by several points between submissions in this competition, so the differences between Zerostar attempts are not claimed as effects.
- **Hidden games are not public games.** The configuration behind attempt 3 scored 49.50 on the 25 public games and 6.15 on the leaderboard. See [ARC-AGI-3 public games](arc-agi-3-public25.md).

Records: [`kaggle-leaderboard.csv`](../../evidence/results-v2/kaggle-leaderboard.csv), checked against [`records.json`](../../evidence/results-v2/records.json) by `scripts/verify_results.py`.
