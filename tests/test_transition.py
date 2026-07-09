from arc3_substrate.logging_.transition import Transition, compute_deltas
from arc3_substrate.perception.scene import build_scene
from tests.fixtures import BLOCK_POST, BLOCK_PRE, FakeFrame


def _scene(grid):
    return build_scene(FakeFrame([grid]))


def test_grid_delta_exact():
    pre, post = _scene(BLOCK_PRE), _scene(BLOCK_POST)
    gd, od = compute_deltas(pre, post)
    # 4 cells cleared on the left + 4 filled on the right = 8 changed cells
    assert len(gd) == 8
    # every entry is (y, x, old, new)
    assert all(len(c) == 4 for c in gd)


def test_object_delta_move():
    pre, post = _scene(BLOCK_PRE), _scene(BLOCK_POST)
    _, od = compute_deltas(pre, post)
    # the 2x2 block has the same oid pre/post => detected as a move, not appear/disappear
    assert od["moved"], od
    assert not od["appeared"] and not od["disappeared"]
    mv = od["moved"][0]
    assert mv["dx"] == 2 and mv["dy"] == 0


def test_transition_roundtrip():
    pre, post = _scene(BLOCK_PRE), _scene(BLOCK_POST)
    t = Transition.build("g", "guid", 0, 0, pre, "ACTION1", None, post)
    t2 = Transition.from_dict(t.to_dict())
    assert t2.to_dict() == t.to_dict()
    assert t2.pre.grid == pre.grid and t2.post.grid == post.grid
