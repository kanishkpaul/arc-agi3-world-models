# Virgil N-pass

[← Research record](../README.md) · [Evaluation guide](../evaluation.md)

A historical research run measured discovery followed by replay across the 25 public games.

| Aggregation | Mean score |
| :--- | ---: |
| Discovery play | 0.576725626% |
| Replay play | 1.341571591% |
| Each game's better play | 1.444953788% |

| Coverage and cost | Recorded value |
| :--- | ---: |
| Public games | 25 |
| Games with nonzero score | 14 |
| Completed levels | 17 / 183 |
| Full-game wins | 0 |
| Physical scorecard actions | 127,314 |
| Historical aggregate wall time | 2,655.21 seconds |
| Sum of exported per-game times | 2,641.08 seconds |

## Protocol

The preserved September 12, 2026 result uses two substantive plays per game: discovery, followed by reuse of discovered behavior and further exploration. Empty scorecard entries are not additional substantive attempts. This research protocol is not presented as a rules-conforming competition result.

The maximum column selects the better score separately for each game. It is not the score of one universal single pass. Physical action totals include all recorded plays; nominal controller budgets omit some prefix and recovery interactions. The two wall-time values have different accounting boundaries and should not be silently interchanged.

## What the result shows

Replay improved the mean score, but completed levels remained limited and no full game was won. Replay also scored worse than discovery on three games. Useful reuse of an observed solution is not evidence of general mechanic recovery or cross-game transfer.

This result belongs to the evaluated bank/replay controller. It is not attributed to a separate self-play/search implementation.

## Check the public arithmetic

The sanitized [per-game table](../../evidence/results-v1/npass-per-game.csv) contains outcome measurements only. From the repository root:

```bash
python scripts/verify_results.py
```

The script recomputes mean scores, coverage, physical actions, and replay regressions from that table and compares them with [records.json](../../evidence/results-v1/records.json). This verifies the published arithmetic, not the private algorithm or the provenance of the original interactions. Full action sequences, solution banks, models, and raw logs are not included.
