"""ReplayVerifier (spec §5). Purely offline — never touches network or SDK."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..logging_.logger import TransitionLog
from .diff import cell_accuracy, changed_cells, grid_match
from .world_model import WorldModel


@dataclass
class VerifyReport:
    n_transitions: int
    exact_match_rate: float
    mean_cell_accuracy: float
    state_accuracy: float
    reward_accuracy: float
    per_transition: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "n_transitions": self.n_transitions,
            "exact_match_rate": self.exact_match_rate,
            "mean_cell_accuracy": self.mean_cell_accuracy,
            "state_accuracy": self.state_accuracy,
            "reward_accuracy": self.reward_accuracy,
            "per_transition": self.per_transition,
        }


class ReplayVerifier:
    def __init__(self, log: TransitionLog) -> None:
        self.log = log

    def evaluate(self, model: WorldModel) -> VerifyReport:
        n = 0
        exact = 0
        cell_acc_sum = 0.0
        state_seen = state_ok = 0
        reward_seen = reward_ok = 0
        per: list[dict] = []

        for t in self.log:
            pred = model.predict(t.pre, t.action_name, t.action_data)
            match = grid_match(pred.grid, t.post.grid)
            acc = cell_accuracy(pred.grid, t.post.grid)
            n += 1
            exact += int(match)
            cell_acc_sum += acc

            if pred.state is not None:
                state_seen += 1
                state_ok += int(pred.state == t.post.state)
            if pred.reward_delta is not None:
                reward_seen += 1
                reward_ok += int(pred.reward_delta == t.reward_delta)

            per.append(
                {
                    "index": t.step_index,
                    "action": t.action_name,
                    "exact": match,
                    "cell_acc": round(acc, 6),
                    "mismatches": changed_cells(pred.grid, t.post.grid)[:5],
                }
            )

        return VerifyReport(
            n_transitions=n,
            exact_match_rate=(exact / n) if n else 0.0,
            mean_cell_accuracy=(cell_acc_sum / n) if n else 0.0,
            state_accuracy=(state_ok / state_seen) if state_seen else 0.0,
            reward_accuracy=(reward_ok / reward_seen) if reward_seen else 0.0,
            per_transition=per,
        )

    def evaluate_incremental(self, model_factory, k: int) -> list[VerifyReport]:
        """Report how match rate evolves over the first k transitions (prefixes).

        `model_factory` is a zero-arg callable returning a fresh model, so
        stateful models (e.g. OracleWorldModel) are re-seeded per prefix.
        """
        items = list(self.log)
        reports = []
        for i in range(1, min(k, len(items)) + 1):
            sub = ReplayVerifier(TransitionLog(items[:i]))
            reports.append(sub.evaluate(model_factory()))
        return reports
