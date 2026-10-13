# Virgil CX

[← Research record](../README.md) · [Evaluation guide](../evaluation.md)

Two historical evaluations of Virgil CX use different interaction protocols. Keeping them separate is necessary to interpret the result.

## Research regression

| Measurement | Recorded value |
| :--- | ---: |
| Mean environment score | 2.232680% |
| Public games evaluated | 25 |
| Games with nonzero score | 13 |
| Completed levels | 16 |
| Combined engine calls | 61,098 |

**Run:** July 19, 2026 public-25 confirmation r5. The preserved phase report documents the final confirmation after reset-boundary normalization.

**Protocol:** exploration and fresh-environment replay under a research regression harness. Discovery and replay interact with the environment and must remain part of the accounting.

**Supports:** a historical result under that harness. It does not establish single-play competition parity, hidden-game performance, or broad autonomous world-model induction.

## Competition-style public run

| Measurement | Recorded value |
| :--- | ---: |
| Mean environment score | 0.561637954% |
| Public games evaluated | 25 |
| Games with nonzero score | 14 |
| Completed levels | 17 |
| Engine calls | 64,581 |
| Elapsed time | 983.36 seconds |

**Run:** July 19, 2026 competition-mode public25 r1. The evaluated policy was extracted from the notebook artifact.

**Protocol:** one environment construction per game, restricted level-reset semantics after construction, and isolated game processes. Score authority was the official local scorecard. This was a public-game artifact test, not evidence of a final private competition score.

**Supports:** the exact notebook artifact completed the documented public evaluation with limited score and completion. The historical score gate failed. The stronger research-regression score cannot substitute for that failure.

## Comparing the rows

The difference illustrates why protocols belong next to performance claims. It is not a controlled ablation, and its ratio is not a measured architectural improvement.

The [public summary records](../../evidence/results-v1/records.json) transcribe the preserved phase reports. Full solver code and raw runs remain private, so these aggregate rows are documented rather than independently executable here.
