from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "evidence" / "virgil-ls20-v1"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_virgil_trace_matches_manifest() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    records = [
        json.loads(line)
        for line in (ROOT / "trace.jsonl").read_text().splitlines()
        if line
    ]

    assert len(records) == manifest["run"]["actions_to_first_level"] == 76
    assert sum(r["action_origin"] == "model_plan" for r in records) == 16
    assert next(r["step"] for r in records if r["action_origin"] == "model_plan") == 61
    assert [r["step"] for r in records] == list(range(1, len(records) + 1))
    assert all(
        left["observed_after_sha256"] == right["observed_before_sha256"]
        for left, right in zip(records, records[1:])
    )
    assert records[-1]["levels_before"] == 0
    assert records[-1]["levels_after"] == manifest["run"]["levels_after"] == 1
    assert file_hash(ROOT / "trace.jsonl") == manifest["artifacts"]["trace.jsonl"]["sha256"]
    assert file_hash(ROOT / "run.gif") == manifest["artifacts"]["run.gif"]["sha256"]
