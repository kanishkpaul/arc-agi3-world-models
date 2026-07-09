"""Assemble a Scene from a FrameData (spec §3).

`build_scene` is the ONLY perception function that reads SDK fields, and it
reads them defensively (getattr) per what sdk_probe found:
  - `frame`: stack (N, H, W) int8 -> primary grid is the last one
  - `state`: GameState enum -> plain name string
  - `available_actions`: list[int] action VALUES -> action names
  - no `.score` field -> score := levels_completed
"""

from __future__ import annotations

from ..types import Scene
from .grid import to_grids
from .objects import estimate_background, segment, segment_multicolor
from .relations import relate
from .vision import choose_active_layer, vision_summary

# GameAction value -> name, per sdk_probe (0..7). Kept local so types stay
# SDK-free; verified against arc_agi.api.GameAction in tests when available.
_ACTION_NAMES = {
    0: "RESET",
    1: "ACTION1",
    2: "ACTION2",
    3: "ACTION3",
    4: "ACTION4",
    5: "ACTION5",
    6: "ACTION6",
    7: "ACTION7",
}


def _action_names(values) -> tuple[str, ...]:
    names = []
    for v in values or []:
        if hasattr(v, "name"):  # already a GameAction enum
            names.append(v.name)
        else:
            names.append(_ACTION_NAMES.get(int(v), f"ACTION_{v}"))
    return tuple(names)


def _state_name(state) -> str:
    return getattr(state, "name", str(state))


def perceive_grid(
    primary,
    grids,
    background: int | None | str = "auto",
    connectivity: int = 4,
    multicolor: bool | str = "auto",
) -> tuple[tuple, dict, dict, int]:
    """Return active objects plus parallel object/vision hypotheses.

    `multicolor="auto"` keeps per-color components for compact scenes and
    switches to multicolor blobs when per-color segmentation fragments sprites
    into too many objects for reliable relational reasoning.
    """
    grids = tuple(grids)

    if background == "auto":
        background = estimate_background(*grids)
    bg = background if isinstance(background, int) else 0

    color_objects = tuple(segment(primary, background=background, connectivity=connectivity))
    multicolor_objects = tuple(
        segment_multicolor(primary, background=background, connectivity=connectivity)
    )
    layers = {"color": color_objects, "multicolor": multicolor_objects}
    if multicolor == "auto":
        active = choose_active_layer(color_objects, multicolor_objects)
    elif multicolor:
        active = "multicolor"
    else:
        active = "color"
    objects = layers[active]
    vision = vision_summary(grids, bg, color_objects, multicolor_objects, active)
    return objects, layers, vision, bg


def build_scene(
    frame,
    available_actions=None,
    background: int | None | str = "auto",
    connectivity: int = 4,
    multicolor: bool | str = "auto",
    include_raw: bool = False,
) -> Scene:
    """``background="auto"`` estimates it as the modal color of the frame stack —
    the background is game-dependent and not always 0. Perception keeps both the
    symbolic per-color layer and a CNN-style multicolor/salience lane."""
    grids = to_grids(getattr(frame, "frame"))
    primary = grids[-1]
    objects, layers, vision, bg = perceive_grid(
        primary, grids, background=background,
        connectivity=connectivity, multicolor=multicolor,
    )
    relations = tuple(relate(objects, primary.shape))

    if available_actions is None:
        available_actions = getattr(frame, "available_actions", None)
    actions = _action_names(available_actions)

    levels = int(getattr(frame, "levels_completed", 0) or 0)
    raw = None
    if include_raw:
        dump = getattr(frame, "model_dump", None)
        raw = dump() if callable(dump) else {"repr": repr(frame)}

    return Scene(
        grid=primary,
        grids=tuple(grids),
        objects=objects,
        relations=relations,
        state=_state_name(getattr(frame, "state", "UNKNOWN")),
        score=levels,  # no per-frame .score field; score := levels_completed
        levels_completed=levels,
        available_actions=actions,
        background=bg,
        raw=raw,
        object_layers=layers,
        vision=vision,
    )
