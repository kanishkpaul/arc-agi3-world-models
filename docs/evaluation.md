# Reading the results

[← Research record](README.md)

## Score units

**ARC-AGI-1 and ARC-AGI-2** are scored as the share of tasks answered exactly, with two attempts per test input. 70/400 means 70 tasks fully correct.

**ARC-AGI-3** uses Relative Human Action Efficiency (RHAE). Completion and action efficiency both affect the score. A score of 1.44495% is not 1.44495% of games solved. Report level coverage and full-game wins separately.

The [official methodology](https://docs.arcprize.org/methodology) explains the metric. Historical result reproduction requires the original environment and scoring versions; a current documentation page does not retroactively fix their evaluation conditions.

## Protocols

| Label | Meaning in this record |
| :--- | :--- |
| Offline benchmark | Local evaluation on public games; not a final private leaderboard result |
| Online run | Interactions recorded through the official API; completion and score finalization must be established separately |
| Research regression | Development evaluation, including the documented fresh-replay behavior |
| Competition-style public test | Notebook artifact tested on public games under specified construction/reset rules |
| Per-game maximum | Each game's best score selected from multiple plays; not one single-pass result |
| Single-game demonstration | One bounded example; no claim of broad game competence |
| Single pass, Kaggle notebook | One play per public game inside a Kaggle notebook under its time limit |
| Kaggle public leaderboard | Kaggle re-runs the submitted notebook on hidden games; one draw per submission; not the final private leaderboard |
| Gated public evaluation (static ARC) | Public evaluation set scored only at milestone gates; descriptive when the set was inspected during development |

The result cards report the interaction conditions needed to interpret their numbers. Detailed solver configurations remain private.

## Evidence levels

**Replayable observation record.** The existing LS20 artifacts include a trace, hashes, and a script to check the recorded actions against the official environment. The public material does not independently establish the private plan-generation mechanism.

**Recalculable summary.** TCCA, N-pass, the Virgil CX reproduction and the Zerostar public-game runs have sanitized per-game outcome tables. Their arithmetic can be recomputed locally. This does not rerun the private solvers or establish that the source records are authentic.

**Leaderboard record.** A score, and a rank where recorded, as shown by the Kaggle leaderboard or submissions listing.

**Documented historical aggregate.** IWM, Categorical Cat, the CX cards and the 0SR card report measurements from preserved run or phase records. Full raw runs and implementations are private; these rows are not independently reproducible from this repository.

## Public games are not hidden games

The 25 ARC-AGI-3 public games can be studied before a run. The Kaggle leaderboard scores games the entrant never sees. Across this record, public-game scores have been a poor predictor of hidden-game scores: one configuration scored 49.50% on the public games and 6.15 on the leaderboard. Treat the two kinds of number as answers to different questions.

## Comparison limits

These experiments change code, budgets, information, and interaction protocols. They do not form a matched scaling study, a causal component ablation, or an unseen-game generalization test. Efficient replay on completed levels does not establish efficient discovery of unfamiliar ones.

No result here establishes superior intelligence per dollar. Action efficiency is not a full accounting of compute, model induction, retries, or development cost.
