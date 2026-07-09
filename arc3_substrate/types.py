"""Canonical internal representation (spec §2).

No SDK imports live here — this is what makes the substrate testable offline
and the world model swappable. Coordinate convention: every grid is indexed
``grid[y, x]`` (row = y = vertical, col = x = horizontal), origin top-left.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Iterator

import numpy as np


class PerceptionError(ValueError):
    """Raised when a frame payload cannot be turned into a valid Grid."""


@dataclass(frozen=True)
class Grid:
    """A single 2D grid, ``array[y, x]``, dtype int8, values 0-15."""

    array: np.ndarray

    def __post_init__(self) -> None:
        object.__setattr__(self, "array", np.asarray(self.array, dtype=np.int8))

    @property
    def shape(self) -> tuple[int, int]:
        return (int(self.array.shape[0]), int(self.array.shape[1]))

    def cells(self) -> Iterator[tuple[int, int, int]]:
        """Yield ``(y, x, value)`` for every cell."""
        h, w = self.shape
        for y in range(h):
            for x in range(w):
                yield y, x, int(self.array[y, x])

    def nonbackground(self, bg: int = 0) -> list[tuple[int, int, int]]:
        ys, xs = np.nonzero(self.array != bg)
        return [(int(y), int(x), int(self.array[y, x])) for y, x in zip(ys, xs)]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Grid) and np.array_equal(self.array, other.array)

    def __hash__(self) -> int:
        return hash(self.array.tobytes())

    def to_dict(self) -> dict:
        return {"array": self.array.tolist()}

    @classmethod
    def from_dict(cls, d: dict) -> "Grid":
        return cls(np.array(d["array"], dtype=np.int8))


@dataclass(frozen=True)
class ArcObject:
    color: int
    cells: frozenset[tuple[int, int]]  # (y, x) pairs
    bbox: tuple[int, int, int, int]  # (y_min, x_min, y_max, x_max)
    centroid: tuple[float, float]  # (y, x)
    size: int
    shape_signature: tuple[tuple[int, int], ...]  # bbox-normalized, sorted
    oid: str  # stable hash of (color, shape_signature) — NOT position

    def to_dict(self) -> dict:
        return {
            "color": self.color,
            "cells": sorted(list(c) for c in self.cells),
            "bbox": list(self.bbox),
            "centroid": list(self.centroid),
            "size": self.size,
            "shape_signature": [list(c) for c in self.shape_signature],
            "oid": self.oid,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ArcObject":
        return cls(
            color=d["color"],
            cells=frozenset((c[0], c[1]) for c in d["cells"]),
            bbox=tuple(d["bbox"]),  # type: ignore[arg-type]
            centroid=tuple(d["centroid"]),  # type: ignore[arg-type]
            size=d["size"],
            shape_signature=tuple((c[0], c[1]) for c in d["shape_signature"]),
            oid=d["oid"],
        )


def make_oid(color: int, shape_signature: tuple[tuple[int, int], ...]) -> str:
    payload = repr((color, shape_signature)).encode()
    return hashlib.sha1(payload).hexdigest()[:12]


@dataclass(frozen=True)
class Relation:
    kind: str  # adjacent|contains|aligned_h|aligned_v|same_color|same_shape|rel_pos
    a: str  # object oid
    b: str  # object oid
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"kind": self.kind, "a": self.a, "b": self.b, "data": self.data}

    @classmethod
    def from_dict(cls, d: dict) -> "Relation":
        return cls(kind=d["kind"], a=d["a"], b=d["b"], data=d.get("data", {}))


@dataclass(frozen=True)
class Scene:
    grid: Grid  # primary grid (last frame of the stack)
    objects: tuple[ArcObject, ...]
    relations: tuple[Relation, ...]
    state: str  # GameState name, decoupled from the SDK enum
    score: int
    levels_completed: int
    available_actions: tuple[str, ...]  # action names
    grids: tuple[Grid, ...] = ()  # full stack when multi-frame; else (grid,)
    background: int = 0  # estimated background color (game-dependent, not always 0)
    raw: dict | None = None
    # Parallel perception hypotheses. `objects` is the currently active layer,
    # while these keep alternatives available for exploration/model induction.
    object_layers: dict[str, tuple[ArcObject, ...]] = field(default_factory=dict)
    vision: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "grid": self.grid.to_dict(),
            "grids": [g.to_dict() for g in self.grids],
            "objects": [o.to_dict() for o in self.objects],
            "relations": [r.to_dict() for r in self.relations],
            "state": self.state,
            "score": self.score,
            "levels_completed": self.levels_completed,
            "available_actions": list(self.available_actions),
            "background": self.background,
            "raw": self.raw,
            "object_layers": {
                k: [o.to_dict() for o in v] for k, v in sorted(self.object_layers.items())
            },
            "vision": self.vision,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Scene":
        return cls(
            grid=Grid.from_dict(d["grid"]),
            grids=tuple(Grid.from_dict(g) for g in d.get("grids", [])),
            objects=tuple(ArcObject.from_dict(o) for o in d["objects"]),
            relations=tuple(Relation.from_dict(r) for r in d["relations"]),
            state=d["state"],
            score=d["score"],
            levels_completed=d["levels_completed"],
            available_actions=tuple(d["available_actions"]),
            background=d.get("background", 0),
            raw=d.get("raw"),
            object_layers={
                k: tuple(ArcObject.from_dict(o) for o in v)
                for k, v in d.get("object_layers", {}).items()
            },
            vision=d.get("vision", {}),
        )
