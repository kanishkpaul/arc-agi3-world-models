# arc-agi3-world-models

[![tests](https://github.com/kanishkpaul/arc-agi3-world-models/actions/workflows/ci.yml/badge.svg)](https://github.com/kanishkpaul/arc-agi3-world-models/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Three attempts at the same hard problem: an agent that learns the rules of an
unseen ARC-AGI-3 game from its own interactions, then plans inside its own
head before spending real moves.**

> Part of a research series — see also
> [register-obstruction](https://github.com/kanishkpaul/register-obstruction) and
> [butterflygate](https://github.com/kanishkpaul/butterflygate) ·
> write-ups at [kanishkpaul.com/research](https://kanishkpaul.com/research)

ARC-AGI-3 games are interactive puzzles with hidden mechanics. You don't get the
rules — you get frames and an action budget. A good agent has to *induce a world
model* online (what does each action do?), notice when it's uncertain, probe to
resolve that uncertainty, and plan in simulation instead of flailing. This repo
consolidates three independent research prototypes I built toward that goal,
each taking a different bet on representation.

> **Status.** These are honest research prototypes with **modest live scores**
> (see below). They're published as a portfolio of *methodology and
> engineering*, not as a leaderboard win. The novel rule-induction cores
> (categorical world-model transfer) are summarized here but the full
> implementations are held back pending a write-up. See
> [What's public vs. withheld](#whats-public-vs-withheld).

---

## New: auditable Virgil result

Virgil is the current private follow-on to these three prototypes. On a fresh
run of public environment `ls20-9607627b`, its provisional world model completed
level 0 in **76 actions**: 60 survey actions, then 16 actions emitted from an
internal model plan. The level counter advanced from 0 to 1 on the final
planned action.

The model was hand-authored from recorded interaction evidence, so this is
evidence of model-based planning and execution, **not** autonomous induction or
cross-game generalization. The public
[`result card`](docs/virgil-result-card.md) includes a run GIF, artifact
manifest, hash-chained trace, and a script that replays all 76 actions against
the official environment without exposing the private model or planner.

## The three bets

### 1. `iwm` — a clean symbolic world-model agent (stdlib-only)
Parses frames into a typed object graph, extracts action→result deltas, induces
compact executable transition rules, probes when uncertain, and plans in an
internal simulator before acting. Runtime uses **only the Python standard
library**; an offline demo runs two toy games (`key-door`, movement/pickup)
with no network. Strong test suite (30+ tests) and a written failure analysis.

**Result:** clean architecture, 0 official levels completed — the honest
diagnosis of *why* (pixel-first deltas polluting evidence, ungrounded
`ACTION6(0,0)`, one-example rule over-confidence) is written up in
`docs/current_failure_analysis.md` and is, frankly, the most useful artifact.

### 2. `categorical-cat` — a category-theory world model
Reframes the world model categorically: typed scene graphs, morphisms, and a
`WorldModel` protocol with a replay verifier. A symbolic **template rule
proposer** induces verified transition rules offline.

**Result (offline, reproducible):** the template-induced model **beats the
identity baseline on held-out logs** (1.00 vs 0.00 exact-match) and produces
verified rules on the exact official-run logs where an earlier LLM proposer
produced **zero** — in microseconds per proposal instead of hundreds of LLM
calls. **Result (live):** official score 0.0 across 11 environments / 1,978
actions. The honest blocker (object-identity churn from content-addressed
object ids) is documented.

### 3. `tcca` — a neuro-symbolic Kaggle agent
A competition-oriented agent (parser, typed state, causal graph, planner,
explorer, n-gram memory) built to run **fully offline** under Kaggle
constraints.

**Result:** best of the three — **4 / 183 levels** across 25 public
environments, aggregate ARC-AGI-3 score ≈ **0.257%** (Kaggle-normalized
≈ 0.0026). Reliable offline benchmark harness + reproducible submission
notebooks.

## What this demonstrates

- Building **world-model induction** loops from scratch (perception → delta →
  rule → verify → plan), three different ways
- **Rigorous offline evaluation**: replay verifiers, held-out log pairs,
  identity/lookup baselines, ablations — not just live scorecards
- **Honest negative-result engineering**: when live score is 0, diagnosing the
  exact broken invariant instead of hiding it
- Running real agents under **hard constraints** (stdlib-only; fully-offline
  Kaggle inference)

## Architecture (shared shape)

```
API frames ─▶ Parser ─▶ typed WorldState/Scene
                          │
                          ▼
                    Delta extractor  (action → result)
                          │
                          ▼
                    Rule inducer ─▶ executable world model
                          │
              ┌───────────┴───────────┐
              ▼                        ▼
        Probing policy            Planner (plan in simulation)
              └───────────┬───────────┘
                          ▼
                      API action
```

## Run it

The offline **evaluation substrate** — perception → logging → verification — is
included and runnable (no network, no keys, no GPU). It's the well-tested
foundation the world models plug into via a one-method `WorldModel` protocol.

```bash
pip install -e ".[dev]"
pytest -q                        # 26 tests: substrate + evidence integrity
python examples/verify_demo.py   # ReplayVerifier vs Identity / Oracle / a custom model
```

```
world model              exact match    cell acc
------------------------------------------------
Oracle (ceiling)               1.000       1.000
Identity (floor)               0.250       0.729
```

The Oracle scores 1.0 by construction — that's how the verifier validates
itself. A real induced world model drops in the same way: implement `predict()`.

To replay the Virgil evidence against the official public LS20 environment:

```bash
pip install arc-agi==0.9.9
python evidence/virgil-ls20-v1/replay_trace.py
```

This online replay verifies the observed frames and level transition. It does
not include or reconstruct the private world model.

## What's public vs. withheld

| Public here | Withheld |
|---|---|
| `arc3_substrate/` — perception, logging, `WorldModel` protocol, `ReplayVerifier` (runnable, 25 tests) | Categorical rule-induction internals (`arc3_cwm/induction`, `dpo`, `transfer`) |
| Identity / Oracle baselines + verify demo | The TCCA neuro-symbolic engine |
| Real result numbers (0.0 / 4·183 / ≈0.257%) | iwm rule inducer + planner internals |
| Virgil LS20 trace, GIF, manifest, and replay verifier | Virgil world model, planner, verifier, and orchestration |
| — | Live API keys / scorecard credentials (never committed) |

The withheld pieces are the one part I may still write up; everything needed to
evaluate the engineering is here.

## Author

Kanishk Paul — [kanishkpaul.com](https://kanishkpaul.com) ·
[github.com/kanishkpaul](https://github.com/kanishkpaul)
