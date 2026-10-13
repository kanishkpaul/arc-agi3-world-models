# Reading the results

[← Research record](README.md)

## Score units

ARC-AGI-3 uses Relative Human Action Efficiency (RHAE). Completion and action efficiency both affect the score. A score of 1.44495% is not 1.44495% of games solved. Report level coverage and full-game wins separately.

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

The result cards report the interaction conditions needed to interpret their numbers. Detailed solver configurations remain private.

## Evidence levels

**Replayable observation record.** The existing LS20 artifacts include a trace, hashes, and a script to check the recorded actions against the official environment. The public material does not independently establish the private plan-generation mechanism.

**Recalculable summary.** TCCA and N-pass have sanitized per-game outcome tables. Their arithmetic can be recomputed locally. This does not rerun the private solvers or establish that the source records are authentic.

**Documented historical aggregate.** IWM, Categorical Cat, and the CX cards report measurements from preserved run or phase records. Full raw runs and implementations are private; these rows are not independently reproducible from this repository.

## Comparison limits

These experiments change code, budgets, information, and interaction protocols. They do not form a matched scaling study, a causal component ablation, or an unseen-game generalization test. Efficient replay on completed levels does not establish efficient discovery of unfamiliar ones.

No result here establishes superior intelligence per dollar. Action efficiency is not a full accounting of compute, model induction, retries, or development cost.
