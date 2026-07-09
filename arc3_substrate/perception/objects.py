"""Grid -> list[ArcObject] via connected components (spec §3).

Segmentation is stateless per-frame. `shape_signature` is translation-invariant
(normalized to bbox origin) but deliberately NOT rotation/reflection-invariant —
those are candidate mechanics to be discovered later, not baked into perception.
"""

from __future__ import annotations

import numpy as np

from ..types import ArcObject, Grid, make_oid

_NEIGHBORS_4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
_NEIGHBORS_8 = _NEIGHBORS_4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def estimate_background(*grids: Grid) -> int:
    """Modal color across the given grid(s) — the background estimate for games
    where the background isn't color 0 (assuming 0 shreds the scene)."""
    counts = np.zeros(16, dtype=np.int64)
    for g in grids:
        counts += np.bincount(g.array.ravel().astype(np.int64), minlength=16)[:16]
    return int(counts.argmax())


def _build_object(cells: list[tuple[int, int]], color: int) -> ArcObject:
    ys = [c[0] for c in cells]
    xs = [c[1] for c in cells]
    y_min, x_min, y_max, x_max = min(ys), min(xs), max(ys), max(xs)
    sig = tuple(sorted((y - y_min, x - x_min) for y, x in cells))
    return ArcObject(
        color=color,
        cells=frozenset(cells),
        bbox=(y_min, x_min, y_max, x_max),
        centroid=(sum(ys) / len(ys), sum(xs) / len(xs)),
        size=len(cells),
        shape_signature=sig,
        oid=make_oid(color, sig),
    )


def _flood(
    arr: np.ndarray,
    seen: np.ndarray,
    start: tuple[int, int],
    neighbors: list[tuple[int, int]],
    same: "callable",  # (value_a, value_b) -> bool
) -> list[tuple[int, int]]:
    h, w = arr.shape
    y0, x0 = start
    stack = [start]
    seen[y0, x0] = True
    comp = []
    while stack:
        y, x = stack.pop()
        comp.append((y, x))
        for dy, dx in neighbors:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx] and same(
                arr[y0, x0], arr[ny, nx]
            ):
                seen[ny, nx] = True
                stack.append((ny, nx))
    return comp


def segment(
    grid: Grid, background: int | None = 0, connectivity: int = 4
) -> list[ArcObject]:
    """Connected-component labeling per color (same-color adjacency = one object).

    ``background=None`` segments every color including 0. Which background is
    correct is game-dependent and unknown a priori; default 0 is just a default.
    """
    neighbors = _NEIGHBORS_8 if connectivity == 8 else _NEIGHBORS_4
    arr = grid.array
    seen = np.zeros(arr.shape, dtype=bool)
    if background is not None:
        seen |= arr == background
    objs: list[ArcObject] = []
    ys, xs = np.nonzero(~seen)
    for y, x in zip(ys, xs):
        if seen[y, x]:
            continue
        color = int(arr[y, x])
        comp = _flood(arr, seen, (int(y), int(x)), neighbors, lambda a, b: a == b)
        objs.append(_build_object(comp, color))
    return objs


def segment_multicolor(
    grid: Grid, background: int | None = 0, connectivity: int = 4
) -> list[ArcObject]:
    """Group spatially-connected cells regardless of color into one object.

    For games with multi-color sprites. Object `color` is set to the most common
    color in the blob. Which segmentation is correct is a later concern.
    """
    neighbors = _NEIGHBORS_8 if connectivity == 8 else _NEIGHBORS_4
    arr = grid.array
    seen = np.zeros(arr.shape, dtype=bool)
    if background is not None:
        seen |= arr == background
    objs: list[ArcObject] = []
    ys, xs = np.nonzero(~seen)
    for y, x in zip(ys, xs):
        if seen[y, x]:
            continue
        comp = _flood(arr, seen, (int(y), int(x)), neighbors, lambda a, b: True)
        colors = [int(arr[cy, cx]) for cy, cx in comp]
        color = max(set(colors), key=colors.count)
        objs.append(_build_object(comp, color))
    return objs
