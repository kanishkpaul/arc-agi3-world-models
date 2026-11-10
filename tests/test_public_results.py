from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts.verify_results import calculate, verify


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'evidence/results-v1'


def test_published_summary_agrees_with_per_game_exports():
    verify(BUNDLE)


def test_corrupt_artifact_is_rejected(tmp_path):
    copy = tmp_path / 'bundle'
    shutil.copytree(BUNDLE, copy)
    table = copy / 'npass-per-game.csv'
    table.write_text(table.read_text() + '\n')
    with pytest.raises(ValueError, match='checksum mismatch'):
        verify(copy)


def test_incorrect_per_game_maximum_is_rejected(tmp_path):
    copy = tmp_path / 'bundle'
    shutil.copytree(BUNDLE, copy)
    table = copy / 'npass-per-game.csv'
    lines = table.read_text().splitlines()
    header = lines[0].split(',')
    values = lines[1].split(',')
    values[header.index('best_score_percent')] = '99.0'
    lines[1] = ','.join(values)
    table.write_text('\n'.join(lines) + '\n')
    with pytest.raises(ValueError, match='maximum does not match'):
        calculate(copy)


from scripts.verify_results import calculate_v2, verify_v2

BUNDLE_V2 = ROOT / 'evidence/results-v2'


def _rehash(bundle: Path, name: str) -> None:
    import hashlib
    import json
    manifest_path = bundle / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['checksums'][name] = hashlib.sha256((bundle / name).read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')


def _edit_cell(table: Path, row: int, column: str, value: str) -> None:
    lines = table.read_text().splitlines()
    header = lines[0].split(',')
    values = lines[row].split(',')
    values[header.index(column)] = value
    lines[row] = ','.join(values)
    table.write_text('\n'.join(lines) + '\n')


def test_v2_records_agree_with_tables():
    lines = verify_v2(BUNDLE_V2)
    assert any(name.startswith('kaggle-') for name in lines)
    assert any(name.startswith('public25-') for name in lines)


def test_v2_every_public_run_covers_25_games():
    for run_id, metrics in calculate_v2(BUNDLE_V2).items():
        assert metrics['games'] == 25, run_id
        assert metrics['levels_total'] == 183, run_id


def test_v2_corrupt_artifact_is_rejected(tmp_path):
    copy = tmp_path / 'bundle'
    shutil.copytree(BUNDLE_V2, copy)
    table = copy / 'kaggle-leaderboard.csv'
    table.write_text(table.read_text() + '\n')
    with pytest.raises(ValueError, match='checksum mismatch'):
        verify_v2(copy)


def test_v2_altered_game_score_is_rejected(tmp_path):
    copy = tmp_path / 'bundle'
    shutil.copytree(BUNDLE_V2, copy)
    _edit_cell(copy / 'public25-per-game.csv', 3, 'score_percent', '99.0')  # a game that already scores
    _rehash(copy, 'public25-per-game.csv')
    with pytest.raises(ValueError, match='score_percent'):
        verify_v2(copy)


def test_v2_inconsistent_win_flag_is_rejected(tmp_path):
    copy = tmp_path / 'bundle'
    shutil.copytree(BUNDLE_V2, copy)
    _edit_cell(copy / 'public25-per-game.csv', 1, 'full_game_win', '1')
    with pytest.raises(ValueError, match='full-game win'):
        calculate_v2(copy)


def test_v2_altered_leaderboard_score_is_rejected(tmp_path):
    copy = tmp_path / 'bundle'
    shutil.copytree(BUNDLE_V2, copy)
    _edit_cell(copy / 'kaggle-leaderboard.csv', 1, 'score_percent', '0.99')
    _rehash(copy, 'kaggle-leaderboard.csv')
    with pytest.raises(ValueError, match='score_percent'):
        verify_v2(copy)


def test_v2_bundle_has_no_paths_addresses_or_identifiers():
    import re
    guid = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)
    for path in BUNDLE_V2.iterdir():
        text = path.read_text()
        assert '@' not in text, path.name
        assert '/Users' not in text and '~/' not in text, path.name
        assert not guid.search(text), path.name
