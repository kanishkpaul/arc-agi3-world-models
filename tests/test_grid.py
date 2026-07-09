import numpy as np
import pytest

from arc3_substrate.perception.grid import to_grid, to_grids
from arc3_substrate.types import Grid, PerceptionError
from tests.fixtures import ASYMMETRIC


def test_stack_and_single():
    grids = to_grids([ASYMMETRIC])  # stack of 1
    assert len(grids) == 1
    assert to_grid([ASYMMETRIC]).shape == (3, 4)
    # 2D payload is accepted directly
    assert to_grid(ASYMMETRIC).shape == (3, 4)


def test_xy_convention_not_transposed():
    g = to_grid(ASYMMETRIC)
    # red (2) cell must be at grid[y=0, x=2], NOT grid[2, 0]
    assert g.array[0, 2] == 2
    assert g.array[2, 0] == 0


def test_value_validation():
    with pytest.raises(PerceptionError):
        to_grid([[0, 99]])


def test_shape_validation():
    with pytest.raises(PerceptionError):
        to_grid(np.zeros((65, 3)))


def test_grid_eq_and_hash():
    a = Grid(np.array(ASYMMETRIC, dtype=np.int8))
    b = Grid(np.array(ASYMMETRIC, dtype=np.int8))
    assert a == b and hash(a) == hash(b)
    assert a.to_dict() and Grid.from_dict(a.to_dict()) == a
