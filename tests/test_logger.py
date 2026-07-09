import json

from arc3_substrate.logging_.logger import TransitionLog
from arc3_substrate.logging_.transition import Transition
from arc3_substrate.perception.scene import build_scene
from tests.fixtures import BLOCK_POST, BLOCK_PRE, FakeFrame


def _log():
    pre = build_scene(FakeFrame([BLOCK_PRE]))
    post = build_scene(FakeFrame([BLOCK_POST]))
    log = TransitionLog()
    log.append(Transition.build("ls20", "guid", 0, 0, pre, "ACTION1", None, post))
    log.append(Transition.build("ls20", "guid", 1, 0, post, "ACTION2", None, pre))
    return log


def test_roundtrip_and_filter(tmp_path):
    log = _log()
    p = tmp_path / "x.jsonl"
    log.to_jsonl(p)
    back = TransitionLog.from_jsonl(p)
    assert len(back) == 2
    assert [t.to_dict() for t in back] == [t.to_dict() for t in log]
    assert len(log.filter(game_id="ls20")) == 2
    assert len(log.filter(game_id="nope")) == 0


def test_key_order_deterministic(tmp_path):
    log = _log()
    p = tmp_path / "x.jsonl"
    log.to_jsonl(p)
    line = p.read_text().splitlines()[0]
    # sort_keys => re-dumping the parsed dict yields the identical string
    assert json.dumps(json.loads(line), sort_keys=True) == line
