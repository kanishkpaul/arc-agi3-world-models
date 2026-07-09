"""Hand-authored synthetic fixtures — no network, no SDK."""

from __future__ import annotations


class FakeFrame:
    """Duck-types the SDK FrameData fields build_scene reads (spec §7).

    frame is a stack (N, H, W); available_actions are int action VALUES;
    state is a plain string here (build_scene uses getattr(.name) or str()).
    """

    def __init__(self, frame, state="NOT_FINISHED", levels_completed=0,
                 available_actions=(1, 2, 3, 4), guid="fixgu-01"):
        self.frame = frame
        self.state = state
        self.levels_completed = levels_completed
        self.available_actions = list(available_actions)
        self.guid = guid


# An asymmetric grid: distinguishes [y, x] from a transpose. A single red (2)
# cell sits at y=0, x=2 (top row, third column). If perception transposed, it
# would land at y=2, x=0 instead.
ASYMMETRIC = [
    [0, 0, 2, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]

# Two separate blue (1) objects + one green (3) object.
TWO_OBJECTS = [
    [1, 1, 0, 0, 3],
    [1, 0, 0, 0, 3],
    [0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0],
]

# Diagonal touch: 4-connectivity => 2 objects; 8-connectivity => 1 object.
DIAGONAL = [
    [4, 0, 0],
    [0, 4, 0],
    [0, 0, 0],
]

# Containment: a 5-ring surrounding a single 2 cell.
CONTAINMENT = [
    [5, 5, 5],
    [5, 2, 5],
    [5, 5, 5],
]

# A single 7 block used for a move test.
BLOCK_PRE = [
    [7, 7, 0, 0],
    [7, 7, 0, 0],
    [0, 0, 0, 0],
]
BLOCK_POST = [
    [0, 0, 7, 7],
    [0, 0, 7, 7],
    [0, 0, 0, 0],
]
