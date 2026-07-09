"""WorldModel Protocol + PredictedScene + reference implementations (spec §5).

This is the interface Phase 3 depends on. A new world model is dropped in by
implementing `predict()` alone — nothing else changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..types import Grid, Scene


@dataclass
class PredictedScene:
    """A prediction of the post-scene. `grid` is the authoritative field."""

    grid: Grid
    state: str | None = None
    reward_delta: int | None = None


@runtime_checkable
class WorldModel(Protocol):
    def predict(
        self, pre: Scene, action_name: str, action_data: dict | None
    ) -> PredictedScene: ...


class IdentityWorldModel:
    """Predicts post == pre (grid never changes). Establishes a floor."""

    def predict(self, pre: Scene, action_name, action_data) -> PredictedScene:  # noqa: ARG002
        return PredictedScene(grid=pre.grid, state=pre.state, reward_delta=0)


class OracleWorldModel:
    """Returns the true post from a recorded log. A test double that validates
    the verifier itself — must score exact_match_rate == 1.0."""

    def __init__(self, log) -> None:
        # key by (game_id, step_index) -> post Scene
        self._by_key = {}
        for t in log:
            self._by_key[(t.game_id, t.step_index)] = t.post
        self._seq = [t.post for t in log]
        self._i = 0

    def predict(self, pre: Scene, action_name, action_data) -> PredictedScene:  # noqa: ARG002
        # Sequential replay: the verifier calls predict once per transition in order.
        post = self._seq[self._i] if self._i < len(self._seq) else pre
        self._i += 1
        return PredictedScene(
            grid=post.grid, state=post.state, reward_delta=post.score - pre.score
        )
