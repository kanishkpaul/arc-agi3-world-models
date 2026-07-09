from pathlib import Path

from arc3_substrate.logging_.logger import TransitionLog
from arc3_substrate.verify.replay import ReplayVerifier
from arc3_substrate.verify.world_model import IdentityWorldModel, OracleWorldModel

FIXTURE = Path(__file__).parent / "fixtures" / "sample_log.jsonl"


def _log():
    return TransitionLog.from_jsonl(FIXTURE)


def test_oracle_is_perfect():
    log = _log()
    report = ReplayVerifier(log).evaluate(OracleWorldModel(log))
    assert report.exact_match_rate == 1.0
    assert report.state_accuracy == 1.0
    assert report.reward_accuracy == 1.0
    assert report.n_transitions == len(log)


def test_identity_below_one_on_changing_log():
    log = _log()
    assert any(t.grid_delta for t in log)  # log contains a real grid change
    report = ReplayVerifier(log).evaluate(IdentityWorldModel())
    assert report.exact_match_rate < 1.0
    assert 0.0 <= report.mean_cell_accuracy <= 1.0
    assert report.per_transition and "cell_acc" in report.per_transition[0]


def test_incremental_prefixes():
    log = _log()
    reps = ReplayVerifier(log).evaluate_incremental(lambda: OracleWorldModel(log), k=3)
    assert len(reps) == min(3, len(log))
    assert all(r.exact_match_rate == 1.0 for r in reps)
