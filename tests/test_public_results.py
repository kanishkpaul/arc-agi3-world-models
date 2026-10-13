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
