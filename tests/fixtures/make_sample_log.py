"""Generate the frozen fixture log once (spec §7). Offline, synthetic.

Run: ``python -m tests.fixtures.make_sample_log``  (commit the resulting jsonl).
"""

from __future__ import annotations

from pathlib import Path

from arc3_substrate.logging_.logger import TransitionLog
from arc3_substrate.logging_.transition import Transition
from arc3_substrate.perception.scene import build_scene
from tests.fixtures import FakeFrame

# A short scripted episode: a 2x2 block slides right, then a cell recolors,
# then an identity (no-op) step, then a WIN. Guarantees >=1 grid change.
FRAMES = [
    ([[7, 7, 0, 0], [7, 7, 0, 0], [0, 0, 0, 0]], "NOT_FINISHED", 0),
    ([[0, 0, 7, 7], [0, 0, 7, 7], [0, 0, 0, 0]], "NOT_FINISHED", 0),
    ([[0, 0, 3, 3], [0, 0, 3, 3], [0, 0, 0, 0]], "NOT_FINISHED", 0),
    ([[0, 0, 3, 3], [0, 0, 3, 3], [0, 0, 0, 0]], "NOT_FINISHED", 0),  # no-op
    ([[0, 0, 3, 3], [0, 0, 3, 3], [5, 0, 0, 0]], "WIN", 1),
]
ACTIONS = ["ACTION1", "ACTION2", "ACTION3", "ACTION1"]


def build() -> TransitionLog:
    scenes = [
        build_scene(FakeFrame([g], state=s, levels_completed=lv))
        for g, s, lv in FRAMES
    ]
    log = TransitionLog()
    for i, action in enumerate(ACTIONS):
        log.append(
            Transition.build("ls20", "fixgu-01", i, scenes[i + 1].levels_completed,
                             scenes[i], action, None, scenes[i + 1])
        )
    return log


if __name__ == "__main__":
    out = Path(__file__).parent / "sample_log.jsonl"
    build().to_jsonl(out)
    print(f"wrote {out}")
