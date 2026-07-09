from arc3_substrate.perception.scene import build_scene
from arc3_substrate.types import ArcObject, Grid, Relation, Scene
from tests.fixtures import CONTAINMENT, FakeFrame


def test_scene_roundtrip_lossless():
    scene = build_scene(FakeFrame([CONTAINMENT]))
    back = Scene.from_dict(scene.to_dict())
    assert back.to_dict() == scene.to_dict()
    assert back.grid == scene.grid
    assert back.objects == scene.objects
    assert back.relations == scene.relations


def test_object_and_relation_roundtrip():
    scene = build_scene(FakeFrame([CONTAINMENT]))
    o = scene.objects[0]
    assert ArcObject.from_dict(o.to_dict()) == o
    r = Relation("rel_pos", "a", "b", {"dx": 1, "dy": -2})
    assert Relation.from_dict(r.to_dict()) == r


def test_grid_roundtrip():
    g = scene_grid = build_scene(FakeFrame([CONTAINMENT])).grid
    assert Grid.from_dict(g.to_dict()) == scene_grid
