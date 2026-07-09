"""Parallel visual perception over ARC-AGI-3 frame stacks.

The game arrives as JSON-backed 64x64 color grids, not camera pixels, but the
agent still needs a vision lane: frame-stack motion, salience, object-layer
choice, and click targets. This module keeps that lane deterministic and
dependency-free. The `tiny_cnn_*` functions are fixed convolutional filters over
one-hot-ish grid features; a trained CNN can later implement the same summary
contract without changing the controller.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from ..types import ArcObject, Grid


RELATION_OBJECT_CAP = 60


def choose_active_layer(
    color_objects: tuple[ArcObject, ...],
    multicolor_objects: tuple[ArcObject, ...],
) -> str:
    """Pick the object layer the symbolic model should currently consume.

    Per-color components are best when the scene is already compact. When they
    fragment sprites into dozens of pieces, multicolor blobs are a better causal
    hypothesis and restore relation computation under the object cap.
    """
    c, m = len(color_objects), len(multicolor_objects)
    if m == 0:
        return "color"
    if c > RELATION_OBJECT_CAP and m < c:
        return "multicolor"
    if c >= 12 and m <= max(2, c // 3):
        return "multicolor"
    return "color"


def motion_cells(grids: Iterable[Grid]) -> set[tuple[int, int]]:
    """Cells that changed anywhere inside the returned frame sequence."""
    arrs = [g.array for g in grids]
    if len(arrs) < 2:
        return set()
    changed = np.zeros(arrs[-1].shape, dtype=bool)
    for a, b in zip(arrs, arrs[1:]):
        if a.shape == b.shape:
            changed |= a != b
    ys, xs = np.nonzero(changed)
    return {(int(y), int(x)) for y, x in zip(ys, xs)}


def _bbox(cells: set[tuple[int, int]]) -> list[int] | None:
    if not cells:
        return None
    ys = [c[0] for c in cells]
    xs = [c[1] for c in cells]
    return [min(ys), min(xs), max(ys), max(xs)]


def _shift_sum(img: np.ndarray) -> np.ndarray:
    padded = np.pad(img, 1, mode="constant")
    out = np.zeros_like(img, dtype=np.float32)
    for dy in range(3):
        for dx in range(3):
            out += padded[dy:dy + img.shape[0], dx:dx + img.shape[1]]
    return out


def tiny_cnn_salience(
    grids: tuple[Grid, ...],
    background: int,
    top_k: int = 32,
) -> list[list[float]]:
    """Fixed-filter CNN-style salience over the last frame plus stack motion.

    Returns compact `[y, x, score]` triples instead of a large array so it can be
    stored in logs. The filters reward foreground, local edges, and animation.
    """
    if not grids:
        return []
    arr = grids[-1].array
    fg = (arr != background).astype(np.float32)
    density = _shift_sum(fg) / 9.0
    edge = np.abs(8.0 * fg - (_shift_sum(fg) - fg))

    motion = np.zeros_like(fg)
    for y, x in motion_cells(grids):
        if 0 <= y < motion.shape[0] and 0 <= x < motion.shape[1]:
            motion[y, x] = 1.0
    motion_density = _shift_sum(motion) / 9.0
    score = 0.35 * fg + 0.45 * edge + 1.75 * motion + 0.75 * motion_density + 0.15 * density
    if not np.any(score):
        return []
    flat = np.argsort(score.ravel())[::-1][:top_k]
    h, w = score.shape
    out = []
    for idx in flat:
        y, x = divmod(int(idx), w)
        val = float(score[y, x])
        if val <= 0:
            break
        out.append([int(y), int(x), round(val, 4)])
    return out


def click_targets(
    color_objects: tuple[ArcObject, ...],
    multicolor_objects: tuple[ArcObject, ...],
    motion: set[tuple[int, int]],
    salient: list[list[float]],
    limit: int = 12,
) -> list[dict]:
    """Rank ACTION6 coordinates from both symbolic layers and CNN salience."""
    raw: list[dict] = []

    def add_object_targets(layer: str, objects: tuple[ArcObject, ...]) -> None:
        for o in objects:
            y, x = int(round(o.centroid[0])), int(round(o.centroid[1]))
            overlap = len(set(o.cells) & motion)
            compact = 1.0 / max(1.0, float(o.size) ** 0.5)
            score = 1.0 + 2.0 * min(1.0, overlap / max(1, o.size)) + compact
            raw.append({
                "x": x,
                "y": y,
                "score": round(score, 4),
                "source": f"{layer}_centroid",
                "oid": o.oid,
            })

    add_object_targets("color", color_objects)
    add_object_targets("multicolor", multicolor_objects)
    for y, x, score in salient[:limit]:
        raw.append({
            "x": int(x),
            "y": int(y),
            "score": round(0.75 + float(score), 4),
            "source": "tiny_cnn_salience",
            "oid": None,
        })

    best: dict[tuple[int, int], dict] = {}
    for item in raw:
        key = (int(item["y"]), int(item["x"]))
        if key not in best or item["score"] > best[key]["score"]:
            best[key] = item
    return sorted(best.values(), key=lambda d: (-d["score"], d["source"], d["y"], d["x"]))[:limit]


def vision_summary(
    grids: tuple[Grid, ...],
    background: int,
    color_objects: tuple[ArcObject, ...],
    multicolor_objects: tuple[ArcObject, ...],
    active_layer: str,
) -> dict:
    motion = motion_cells(grids)
    salient = tiny_cnn_salience(grids, background)
    return {
        "frame_count": len(grids),
        "active_layer": active_layer,
        "color_object_count": len(color_objects),
        "multicolor_object_count": len(multicolor_objects),
        "motion_cell_count": len(motion),
        "motion_bbox": _bbox(motion),
        "click_targets": click_targets(color_objects, multicolor_objects, motion, salient),
        "salient_cells": salient[:16],
        "backend": "symbolic+tiny_cnn",
    }
