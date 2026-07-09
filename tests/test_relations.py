import numpy as np

from arc3_substrate.perception.grid import to_grid
from arc3_substrate.perception.objects import segment
from arc3_substrate.perception.relations import relate
from arc3_substrate.types import Grid
from tests.fixtures import CONTAINMENT, TWO_OBJECTS


def _kinds(rels):
    return {r.kind for r in rels}


def test_containment():
    g = to_grid(CONTAINMENT)
    objs = segment(g)  # the 5-ring and the inner 2
    rels = relate(objs, g.shape)
    assert any(r.kind == "contains" for r in rels)


def test_same_color_and_rel_pos():
    g = to_grid(TWO_OBJECTS)
    objs = segment(g)
    rels = relate(objs, g.shape)
    kinds = _kinds(rels)
    assert "same_color" in kinds  # the two blue blobs
    assert "rel_pos" in kinds
    # rel_pos data is quantized ints
    rp = next(r for r in rels if r.kind == "rel_pos")
    assert isinstance(rp.data["dx"], int) and isinstance(rp.data["dy"], int)


def test_alignment():
    # two cells sharing a column => aligned_v
    g = to_grid([[1, 0], [3, 0]])
    rels = relate(segment(g), g.shape)
    assert any(r.kind == "aligned_v" for r in rels)


def test_adjacency_handles_large_objects_with_bbox_filter():
    far_arr = np.zeros((16, 32), dtype=np.int8)
    far_arr[0:12, 0:12] = 1
    far_arr[0:12, 24:31] = 2
    near_arr = np.zeros((16, 32), dtype=np.int8)
    near_arr[0:12, 0:12] = 1
    near_arr[0:12, 12:19] = 2

    assert not any(r.kind == "adjacent" for r in relate(segment(Grid(far_arr)), far_arr.shape))
    assert any(r.kind == "adjacent" for r in relate(segment(Grid(near_arr)), near_arr.shape))
