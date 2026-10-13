# Historical prototypes

[← Research record](../README.md) · [Evaluation guide](../evaluation.md)

These experiments preceded Virgil. The public library is their evaluation companion; it does not contain their full agent implementations.

## TCCA

| Measurement | Recorded value |
| :--- | ---: |
| Mean action-efficiency score | 0.256726225% |
| Public games evaluated | 25 |
| Games with nonzero score | 4 |
| Completed levels | 4 / 183 |
| Recorded actions | 11,217 |
| Elapsed time | 202.55 seconds |

**Evidence:** the preserved offline public-benchmark summary associated with the April 18, 2026 checkpoint. A sanitized [per-game table](../../evidence/results-v1/tcca-per-game.csv) supports the aggregate arithmetic. The underlying benchmark implementation and full run records remain private.

**Interpretation:** a working offline baseline with limited completion. The prototype included game-specific behavior; this result is not evidence of general autonomous mechanic induction. No new run is recorded for the final historical fix commit.

## IWM

| Measurement | Recorded value |
| :--- | ---: |
| Locally observed completed levels | 0 |
| Games touched | 4 |
| Logged actions | 266 |
| Finalized server score | Unavailable |

**Evidence:** June 21, 2026 interrupted API-run stop report. The run was stopped before completion, and the final scorecard close returned an error. Zero observed levels must not be converted into a finalized official score.

**Interpretation:** the historical live attempt did not complete a level. Its toy demonstrations do not establish live-game transfer. The [previously public failure note](../current_failure_analysis.md) remains available as historical context.

## Categorical Cat

| Measurement | Recorded value |
| :--- | ---: |
| Online score | 0.0% |
| Environments played | 11 of 25 planned |
| Completed levels | 0 |
| Official recorded actions | 1,978 |

**Evidence:** July 2, 2026 online run report and persisted scorecard. The sweep was stopped early; this is not a completed 25-game evaluation. The neural proposer produced no verified rules in that run.

**Interpretation:** the initial online attempt failed to complete a level. Previously reported template-induced held-out toy-log exact match of 1.00 versus an identity baseline of 0.00 is a separate, narrow offline result. It does not imply successful live induction or general transfer.

## Evidence boundary

These are documented historical results. Only sanitized outcome measurements are included in this update. Source implementations, detailed experiment configurations, and raw solver traces remain private. See the [summary records](../../evidence/results-v1/records.json) for dates and provenance labels.
