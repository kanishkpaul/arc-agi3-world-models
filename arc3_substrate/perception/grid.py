"""FrameData payload -> canonical Grid(s) (spec §3).

COORDINATE CONVENTION (enforced here and nowhere else): a grid is a NumPy
array indexed ``grid[y, x]`` — first axis is the row / y / vertical, second is
the column / x / horizontal, origin top-left. The SDK gives ``(x, y)`` only for
ACTION6 coordinates; that conversion happens at the harness boundary, not here.
The SDK `frame` payload is a stack ``(N_frames, H, W)`` already in ``[y, x]``
row-major order, so ``np.array(frame)[i]`` is grid i indexed ``[y, x]``.
"""

from __future__ import annotations

import numpy as np

from ..types import Grid, PerceptionError

MAX_SIDE = 64
MIN_VAL, MAX_VAL = 0, 15


def _validate(a: np.ndarray) -> None:
    if a.ndim != 2:
        raise PerceptionError(f"grid must be 2D, got shape {a.shape}")
    h, w = a.shape
    if h > MAX_SIDE or w > MAX_SIDE or h == 0 or w == 0:
        raise PerceptionError(f"grid shape {a.shape} out of bounds (1..{MAX_SIDE})")
    if a.size and (a.min() < MIN_VAL or a.max() > MAX_VAL):
        raise PerceptionError(
            f"cell values must be {MIN_VAL}..{MAX_VAL}, got {a.min()}..{a.max()}"
        )


def _as_stack(payload) -> np.ndarray:
    """Normalize any accepted payload into a 3D stack ``(N, H, W)``."""
    a = np.asarray(payload)
    if a.dtype == object:
        raise PerceptionError(f"ragged / non-rectangular frame payload: {a.shape}")
    if a.ndim == 2:  # single grid
        a = a[None, ...]
    elif a.ndim != 3:
        raise PerceptionError(f"expected 2D or 3D frame payload, got ndim {a.ndim}")
    return a.astype(np.int8)


def to_grids(payload) -> list[Grid]:
    """Handle single grid, stack of grids, nested lists, or numpy arrays."""
    stack = _as_stack(payload)
    grids = []
    for i in range(stack.shape[0]):
        _validate(stack[i])
        grids.append(Grid(stack[i]))
    if not grids:
        raise PerceptionError("empty frame stack")
    return grids


def to_grid(payload) -> Grid:
    """The primary (last) grid of the stack."""
    return to_grids(payload)[-1]
