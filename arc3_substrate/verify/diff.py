"""Grid diff primitives (spec §5)."""

from __future__ import annotations

import numpy as np

from ..types import Grid


def grid_match(a: Grid, b: Grid) -> bool:
    return a == b


def changed_cells(a: Grid, b: Grid) -> list[tuple[int, int, int, int]]:
    if a.shape != b.shape:
        return [(-1, -1, -1, -1)]  # sentinel: shape mismatch
    ys, xs = np.nonzero(a.array != b.array)
    return [(int(y), int(x), int(a.array[y, x]), int(b.array[y, x])) for y, x in zip(ys, xs)]


def cell_accuracy(a: Grid, b: Grid) -> float:
    """Fraction of matching cells over the FULL grid. Shape mismatch -> 0.0."""
    if a.shape != b.shape:
        return 0.0
    total = a.array.size
    if total == 0:
        return 1.0
    return float(np.count_nonzero(a.array == b.array)) / total
