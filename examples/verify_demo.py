"""Offline demo of the world-model evaluation substrate.

Runs the ReplayVerifier against a recorded transition log with two reference
world models:

  * IdentityWorldModel  — predicts "nothing changes" (a floor)
  * OracleWorldModel     — replays the true post-state (validates the verifier)

Then plugs in a tiny custom world model to show the one method you implement to
drop your own model into the harness. No network, no keys, no GPU.

    python examples/verify_demo.py
"""

from __future__ import annotations

from pathlib import Path

from arc3_substrate.logging_.logger import TransitionLog
from arc3_substrate.verify.replay import ReplayVerifier
from arc3_substrate.verify.world_model import (
    IdentityWorldModel,
    OracleWorldModel,
    PredictedScene,
)

LOG = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "sample_log.jsonl"


class EchoPreWorldModel:
    """Example custom model: predict post == pre. Implement `predict()` alone;
    the verifier and every metric come for free."""

    def predict(self, pre, action_name, action_data) -> PredictedScene:
        return PredictedScene(grid=pre.grid, state=pre.state, reward_delta=0)


def main() -> None:
    log = TransitionLog.from_jsonl(LOG)
    verifier = ReplayVerifier(log)

    print(f"Loaded {len(log)} transitions from {LOG.name}\n")
    print(f"{'world model':<22}{'exact match':>14}{'cell acc':>12}")
    print("-" * 48)
    for name, model in [
        ("Oracle (ceiling)", OracleWorldModel(log)),
        ("Identity (floor)", IdentityWorldModel()),
        ("EchoPre (custom)", EchoPreWorldModel()),
    ]:
        r = verifier.evaluate(model)
        print(f"{name:<22}{r.exact_match_rate:>14.3f}{r.mean_cell_accuracy:>12.3f}")

    print(
        "\nThe Oracle scores 1.0 by construction — that is how the verifier "
        "validates itself.\nA real induced world model plugs in exactly the same "
        "way: implement predict()."
    )


if __name__ == "__main__":
    main()
