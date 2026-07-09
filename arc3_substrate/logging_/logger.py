"""TransitionLog: append / to_jsonl / from_jsonl (spec §4)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .transition import Transition


class TransitionLog:
    def __init__(self, transitions: list[Transition] | None = None) -> None:
        self._items: list[Transition] = list(transitions or [])

    def append(self, t: Transition) -> None:
        self._items.append(t)

    def extend(self, ts) -> None:
        self._items.extend(ts)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Transition]:
        return iter(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def reperceive(self) -> "TransitionLog":
        """Rebuild every transition's derived views (objects, relations, deltas)
        from the stored grids with CURRENT perception. Grids are ground truth;
        everything else is a view — logs written by older perception (background
        assumed 0, oid-exact object matching) get today's segmentation and
        shape-tolerant deltas without touching the file."""
        from dataclasses import replace as _replace

        from ..perception.objects import estimate_background
        from ..perception.relations import relate
        from ..perception.scene import perceive_grid

        grids = [g for t in self._items for g in (t.pre.grid, t.post.grid)]
        if not grids:
            return TransitionLog()
        bg = estimate_background(*grids)

        def rebuild(scene):
            objects, layers, vision, _bg = perceive_grid(
                scene.grid, scene.grids or (scene.grid,), background=bg, multicolor="auto",
            )
            return _replace(
                scene,
                objects=objects,
                relations=tuple(relate(objects, scene.grid.shape)),
                background=bg,
                object_layers=layers,
                vision=vision,
            )

        out = TransitionLog()
        for t in self._items:
            out.append(Transition.build(
                game_id=t.game_id,
                guid=t.guid,
                step_index=t.step_index,
                level_index=t.level_index,
                pre=rebuild(t.pre),
                action_name=t.action_name,
                action_data=t.action_data,
                post=rebuild(t.post),
            ))
        return out

    def filter(self, game_id=None, level_index=None) -> "TransitionLog":
        out = [
            t
            for t in self._items
            if (game_id is None or t.game_id == game_id)
            and (level_index is None or t.level_index == level_index)
        ]
        return TransitionLog(out)

    def to_jsonl(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            for t in self._items:
                # sort_keys => deterministic, git-stable diffs
                f.write(json.dumps(t.to_dict(), sort_keys=True) + "\n")
        return path

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "TransitionLog":
        items = []
        with Path(path).open() as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(Transition.from_dict(json.loads(line)))
        return cls(items)


def default_run_path(game_id: str, guid: str | None, runs_dir="runs") -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    g = (guid or "noguid")[:8]
    return Path(runs_dir) / f"{game_id}__{g}__{ts}.jsonl"
