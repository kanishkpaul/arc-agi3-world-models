"""objects -> list[Relation] (spec §3).

Closed vocabulary: adjacent, contains, aligned_h, aligned_v, same_color,
same_shape, rel_pos. O(n^2), capped; `rel_pos` is quantized (sign + small int
deltas) so relations compare across frames.
"""

from __future__ import annotations

from ..types import ArcObject, Relation

MAX_OBJECTS = 60  # cap; beyond this we skip pairwise relations


def _quant(delta: float) -> int:
    """Sign + magnitude bucket so rel_pos is comparable across frames."""
    if delta == 0:
        return 0
    mag = min(int(abs(delta)), 8)
    return mag if delta > 0 else -mag


def _adjacent(a: ArcObject, b: ArcObject) -> bool:
    ay0, ax0, ay1, ax1 = a.bbox
    by0, bx0, by1, bx1 = b.bbox
    if ay1 + 1 < by0 or by1 + 1 < ay0 or ax1 + 1 < bx0 or bx1 + 1 < ax0:
        return False
    left, right = (a, b) if len(a.cells) <= len(b.cells) else (b, a)
    for ay, ax in left.cells:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (ay + dy, ax + dx) in right.cells:
                    return True
    return False


def _contains(a: ArcObject, b: ArcObject) -> bool:
    ay0, ax0, ay1, ax1 = a.bbox
    by0, bx0, by1, bx1 = b.bbox
    return ay0 <= by0 and ax0 <= bx0 and ay1 >= by1 and ax1 >= bx1 and a.size > b.size


def relate(objects, grid_shape) -> list[Relation]:  # noqa: ARG001
    objs = list(objects)
    rels: list[Relation] = []
    if len(objs) > MAX_OBJECTS:
        import warnings

        warnings.warn(
            f"{len(objs)} objects > cap {MAX_OBJECTS}; emitting no pairwise relations",
            stacklevel=2,
        )
        return rels
    for i in range(len(objs)):
        for j in range(len(objs)):
            if i == j:
                continue
            a, b = objs[i], objs[j]
            # symmetric relations only emitted once (i < j)
            if i < j:
                if a.color == b.color:
                    rels.append(Relation("same_color", a.oid, b.oid))
                if a.shape_signature == b.shape_signature:
                    rels.append(Relation("same_shape", a.oid, b.oid))
                if _adjacent(a, b):
                    rels.append(Relation("adjacent", a.oid, b.oid))
                if a.centroid[0] == b.centroid[0]:
                    rels.append(Relation("aligned_h", a.oid, b.oid))
                if a.centroid[1] == b.centroid[1]:
                    rels.append(Relation("aligned_v", a.oid, b.oid))
            # directed relations
            if _contains(a, b):
                rels.append(Relation("contains", a.oid, b.oid))
            dy = _quant(b.centroid[0] - a.centroid[0])
            dx = _quant(b.centroid[1] - a.centroid[1])
            rels.append(Relation("rel_pos", a.oid, b.oid, {"dy": dy, "dx": dx}))
    return rels
