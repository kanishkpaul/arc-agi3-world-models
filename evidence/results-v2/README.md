# Result summaries, second release

[← Research record](../../docs/README.md)

Published November 10, 2026. This bundle contains sanitized outcome measurements from April to November 2026; no new solver run was performed for the release. The [first release](../results-v1/README.md) is unchanged.

| File | Contents |
| :--- | :--- |
| [records.json](records.json) | Aggregate measurements, dates, protocols, leaderboard definitions, and provenance labels |
| [kaggle-leaderboard.csv](kaggle-leaderboard.csv) | Nine ARC Prize 2026 ARC-AGI-3 Kaggle leaderboard entries |
| [public25-per-game.csv](public25-per-game.csv) | Per-game outcomes for five runs on the 25 public games (`run_id` names the run) |
| [manifest.json](manifest.json) | File checksums, schema version, and disclosure scope |

## Headline outcomes

| Record | Outcome |
| :--- | :--- |
| Kaggle public leaderboard, best entry | 28.40, rank 1,377 of 5,012 (Zerostar attempt 1, October 31) |
| Kaggle public leaderboard, other entries | 0.06 to 0.23 (six entries before October 30); 20.27 and 6.15 (Zerostar attempts 2 and 3) |
| 25 public games, best single pass | 49.50 mean score, 106 of 183 levels (Zerostar configuration C) |
| ARC-AGI-1 public evaluation | 70 of 400 tasks (strict 69 of 399), +20/−0 against the same-run reference |
| ARC-AGI-2 public evaluation | 0 of 113 after removing 7 tasks that overlap ARC-AGI-1 (1 of 120 raw) |
| ARC-AGI-1 gated milestones | 10 → 34 → 50 → 70 of 400 (October 29 to November 7) |

## Leaderboards

Every Kaggle score here is from the **Kaggle public leaderboard**. Kaggle re-runs each submitted notebook on hidden games, not on the 25 public games, and the public leaderboard shows the score on the public share of that hidden set while the competition runs. None of these numbers is a final private-leaderboard score; the source records do not contain one. The leaderboard ranks a team by its best entry, so only the entry holding that position has a rank. Public-game scores and hidden-game leaderboard scores measure different games and differ widely: configuration C scored 49.50 on the public games and 6.15 as a submission.

## Evidence levels

`records.json` uses the three levels of the first release plus one:

- `recalculable_summary`: a per-game table is published and its arithmetic can be recomputed.
- `documented_historical_aggregate`: the aggregate comes from a preserved run, ledger, or report; no per-game table is published.
- `leaderboard_record`: a score, and a rank where recorded, as shown by the Kaggle leaderboard or submissions listing.
- `replayable_observation_record`: not used in this release.

The per-game table includes scores, completion, and action counts. Action counts follow each run's harness: the Virgil CX rows count engine calls including resets (both plays for the regression run), and the Zerostar rows count every recorded action including resets. Compare them within a run. The bundle excludes action sequences, model outputs, solver parameters, configuration descriptions, per-task result lists, submission and scorecard identifiers, and source-machine paths.

## Source notes

- The Virgil CC floor runs logged only an aggregate score, so they have no per-game rows.
- One run summary gives configuration B 104 of 183 levels; its per-game export gives 105, which also matches the summary's own paired difference against configuration A. This release uses 105.
- The 0.23 entry is confirmed by a leaderboard snapshot; its attribution to floor v3 rests on the owner's report. The 0.06 entry rests on a results summary and has no submission date.
- The ARC-AGI-1 maximum CPU time per task (3.84 s) is the maximum over three runs; the mean of the per-run maxima is 3.56 s.

## Verification

```bash
python scripts/verify_results.py
```

Run that command from the repository root to check table arithmetic, leaderboard rows, record consistency, and artifact hashes for both releases. The script verifies internal consistency; it does not authenticate the original records or reconstruct the private systems.

The source records are preserved privately. Their labels in `records.json` identify the measurement being summarized, not publicly available raw downloads. See the [evaluation guide](../../docs/evaluation.md) for each evidence level.
