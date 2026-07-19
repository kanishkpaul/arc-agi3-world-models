"""Replay the public Virgil LS20 evidence trace against ARC-AGI-3.

This verifies the observed frames and the level transition. It does not contain
or reconstruct the private world model that produced the action sequence.

Requires internet access for ARC environment metadata and:

    pip install arc-agi==0.9.9 numpy
    python evidence/virgil-ls20-v1/replay_trace.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from arc_agi import Arcade
from arcengine import GameAction


ROOT = Path(__file__).resolve().parent
TRACE = ROOT / "trace.jsonl"
MANIFEST = ROOT / "manifest.json"


def grid_hash(frame_data) -> str:
    grid = np.asarray(frame_data.frame[-1], dtype=np.uint8)
    return hashlib.sha256(grid.tobytes()).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    records = [json.loads(line) for line in TRACE.read_text().splitlines() if line]
    expected_environment = manifest["run"]["environment"]

    arcade = Arcade()
    environment = next(
        item
        for item in arcade.get_environments()
        if item.game_id == expected_environment
    )
    game = arcade.make(environment.game_id)
    observation = game.step(GameAction.RESET)
    if observation is None:
        raise RuntimeError("Initial RESET failed")
    if grid_hash(observation) != records[0]["observed_before_sha256"]:
        raise AssertionError("Initial frame hash differs from the recorded run")

    for record in records:
        data = record.get("action_data")
        observation = game.step(GameAction.from_id(record["action_id"]), data=data)
        if observation is None:
            raise AssertionError(f"Step {record['step']} was rejected")
        if grid_hash(observation) != record["observed_after_sha256"]:
            raise AssertionError(f"Frame hash mismatch at step {record['step']}")
        if observation.levels_completed != record["levels_after"]:
            raise AssertionError(f"Level counter mismatch at step {record['step']}")

    expected_levels = manifest["run"]["levels_after"]
    if observation.levels_completed != expected_levels:
        raise AssertionError(
            f"Expected {expected_levels} completed level, got "
            f"{observation.levels_completed}"
        )
    print(
        f"verified {len(records)} actions on {environment.game_id}: "
        f"levels 0 -> {observation.levels_completed}"
    )


if __name__ == "__main__":
    main()
