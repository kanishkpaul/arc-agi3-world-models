from arc3_substrate.perception.grid import to_grid
from arc3_substrate.perception.objects import segment, segment_multicolor
from tests.fixtures import DIAGONAL, TWO_OBJECTS


def test_segment_counts_and_colors():
    objs = segment(to_grid(TWO_OBJECTS))
    # two blue (1) blobs + one green (3) column
    colors = sorted(o.color for o in objs)
    assert colors == [1, 1, 3]
    assert len(objs) == 3


def test_connectivity_4_vs_8():
    g = to_grid(DIAGONAL)
    assert len(segment(g, connectivity=4)) == 2
    assert len(segment(g, connectivity=8)) == 1


def test_shape_signature_translation_invariant():
    objs = segment(to_grid(TWO_OBJECTS))
    blues = [o for o in objs if o.color == 1]
    sigs = {o.shape_signature for o in blues}
    # the two blue blobs differ in shape (an L vs a domino) -> different sigs
    assert len(sigs) == 2
    # same shape => same oid regardless of position
    for o in objs:
        assert o.oid == segment(to_grid(TWO_OBJECTS))[objs.index(o)].oid


def test_multicolor_groups_across_colors():
    grid = to_grid([[1, 2, 0], [0, 0, 0]])
    assert len(segment(grid)) == 2  # per-color: two objects
    assert len(segment_multicolor(grid)) == 1  # multicolor: one blob


def test_background_none_segments_zero():
    objs = segment(to_grid([[0, 0], [0, 0]]), background=None)
    assert len(objs) == 1 and objs[0].color == 0
