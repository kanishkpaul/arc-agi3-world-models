"""Transition dataclass + delta computation (spec §4).

The grid diff is the GROUND TRUTH. `object_delta` is a convenience view built
from a simple, honest matching heuristic (exact oid first, then shape-tolerant:
same color + nearest centroid + shape-overlap IoU, so an object that moves AND
deforms by a pixel still reads as moved rather than disappear+appear); it will
sometimes be wrong, and that is acceptable because the authoritative signal is
always the exact cell diff.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..types import ArcObject, Scene


def _grid_delta(pre: Scene, post: Scene) -> list[tuple[int, int, int, int]]:
    a, b = pre.grid.array, post.grid.array
    if a.shape != b.shape:
        # Shape change: report every cell of the (larger) post grid as changed.
        out = []
        for y, x, val in post.grid.cells():
            old = int(a[y, x]) if (y < a.shape[0] and x < a.shape[1]) else -1
            if old != val:
                out.append((y, x, old, val))
        return out
    import numpy as np

    ys, xs = np.nonzero(a != b)
    return [(int(y), int(x), int(a[y, x]), int(b[y, x])) for y, x in zip(ys, xs)]


# minimum shape-overlap (IoU of bbox-normalized cell sets) for two same-color
# objects to count as the same object having moved/deformed
SHAPE_IOU_THRESHOLD = 0.5


def _shape_iou(a: ArcObject, b: ArcObject) -> float:
    sa, sb = set(a.shape_signature), set(b.shape_signature)
    union = len(sa | sb)
    return len(sa & sb) / union if union else 0.0


def _object_delta_for_objects(pre_objs: list[ArcObject], post_objs: list[ArcObject]) -> dict:
    free_pre = set(range(len(pre_objs)))
    free_post = set(range(len(post_objs)))
    moved: list[dict] = []

    def dist(p: ArcObject, q: ArcObject) -> float:
        return abs(p.centroid[0] - q.centroid[0]) + abs(p.centroid[1] - q.centroid[1])

    def match(candidates: list[tuple[float, int, int]], deformed: bool) -> None:
        # greedy nearest-first, each object matched at most once
        for _d, i, j in sorted(candidates):
            if i not in free_pre or j not in free_post:
                continue
            free_pre.discard(i)
            free_post.discard(j)
            p, q = pre_objs[i], post_objs[j]
            dy = q.centroid[0] - p.centroid[0]
            dx = q.centroid[1] - p.centroid[1]
            if dy or dx or deformed:
                entry = {"oid": p.oid, "dy": round(dy, 3), "dx": round(dx, 3)}
                if deformed:
                    entry["to_oid"] = q.oid
                    entry["deformed"] = True
                moved.append(entry)

    # pass 1: exact oid (color + shape identical) — clean moves / unchanged
    match(
        [
            (dist(p, q), i, j)
            for i, p in enumerate(pre_objs)
            for j, q in enumerate(post_objs)
            if p.oid == q.oid
        ],
        deformed=False,
    )

    # pass 2: same color + shape overlap — moved with deformation (animation,
    # occlusion, growth); dy=dx=0 entries are in-place deformations
    match(
        [
            (dist(p, q), i, j)
            for i in free_pre
            for j in free_post
            if (p := pre_objs[i]).color == (q := post_objs[j]).color
            and _shape_iou(p, q) >= SHAPE_IOU_THRESHOLD
        ],
        deformed=True,
    )

    disappeared = [pre_objs[i] for i in sorted(free_pre)]
    appeared = [post_objs[j] for j in sorted(free_post)]

    # "recolored": disappeared shape reappears as another color at same location.
    recolored = []
    for d in list(disappeared):
        for a in list(appeared):
            if d.shape_signature == a.shape_signature and d.bbox[:2] == a.bbox[:2]:
                recolored.append(
                    {"from_oid": d.oid, "to_oid": a.oid, "from": d.color, "to": a.color}
                )
                disappeared.remove(d)
                appeared.remove(a)
                break

    return {
        "appeared": [o.oid for o in appeared],
        "disappeared": [o.oid for o in disappeared],
        "moved": moved,
        "recolored": recolored,
    }


def _delta_score(od: dict) -> float:
    return (
        3.0 * len(od.get("moved", ()))
        + 2.0 * len(od.get("recolored", ()))
        + 0.75 * len(od.get("appeared", ()))
        + 0.75 * len(od.get("disappeared", ()))
    )


def _object_delta(pre: Scene, post: Scene) -> dict:
    """Object delta from the richest parallel perception layer.

    The active layer may be multicolor for clean graph reasoning, while mechanics
    can still be visible only in the per-color layer. Score both when available
    and feed induction the layer with the strongest causal signal.
    """
    candidates: list[tuple[str, list[ArcObject], list[ArcObject]]] = [
        ("active", list(pre.objects), list(post.objects))
    ]
    for layer in sorted(set(pre.object_layers) & set(post.object_layers)):
        candidates.append((layer, list(pre.object_layers[layer]), list(post.object_layers[layer])))

    best_name = "active"
    best = _object_delta_for_objects(candidates[0][1], candidates[0][2])
    best_score = _delta_score(best)
    for name, pre_objs, post_objs in candidates[1:]:
        od = _object_delta_for_objects(pre_objs, post_objs)
        score = _delta_score(od)
        if score > best_score:
            best_name, best, best_score = name, od, score
    if best_name != "active":
        best = {**best, "layer": best_name}
    return best


def compute_deltas(pre: Scene, post: Scene):
    return _grid_delta(pre, post), _object_delta(pre, post)


@dataclass
class Transition:
    game_id: str
    guid: str | None
    step_index: int
    level_index: int | None
    pre: Scene
    action_name: str
    action_data: dict | None
    post: Scene
    reward_delta: int
    state_change: tuple[str, str]
    grid_delta: list[tuple[int, int, int, int]]
    object_delta: dict

    @classmethod
    def build(
        cls,
        game_id: str,
        guid: str | None,
        step_index: int,
        level_index: int | None,
        pre: Scene,
        action_name: str,
        action_data: dict | None,
        post: Scene,
    ) -> "Transition":
        gd, od = compute_deltas(pre, post)
        return cls(
            game_id=game_id,
            guid=guid,
            step_index=step_index,
            level_index=level_index,
            pre=pre,
            action_name=action_name,
            action_data=action_data,
            post=post,
            reward_delta=post.score - pre.score,
            state_change=(pre.state, post.state),
            grid_delta=gd,
            object_delta=od,
        )

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "guid": self.guid,
            "step_index": self.step_index,
            "level_index": self.level_index,
            "pre": self.pre.to_dict(),
            "action_name": self.action_name,
            "action_data": self.action_data,
            "post": self.post.to_dict(),
            "reward_delta": self.reward_delta,
            "state_change": list(self.state_change),
            "grid_delta": [list(c) for c in self.grid_delta],
            "object_delta": self.object_delta,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Transition":
        return cls(
            game_id=d["game_id"],
            guid=d["guid"],
            step_index=d["step_index"],
            level_index=d["level_index"],
            pre=Scene.from_dict(d["pre"]),
            action_name=d["action_name"],
            action_data=d["action_data"],
            post=Scene.from_dict(d["post"]),
            reward_delta=d["reward_delta"],
            state_change=tuple(d["state_change"]),  # type: ignore[arg-type]
            grid_delta=[tuple(c) for c in d["grid_delta"]],  # type: ignore[misc]
            object_delta=d["object_delta"],
        )
