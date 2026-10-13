"""Check public outcome-table arithmetic and checksums; never run a solver."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict]:
    with path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows or len({r['game_id'] for r in rows}) != len(rows):
        raise ValueError(f'{path.name}: empty table or duplicate game IDs')
    return rows


def calculate(bundle: Path) -> dict[str, dict]:
    tcca = read_rows(bundle / 'tcca-per-game.csv')
    npass = read_rows(bundle / 'npass-per-game.csv')
    for row in npass:
        discovery = float(row['discovery_score_percent'])
        replay = float(row['replay_score_percent'])
        if not math.isclose(float(row['best_score_percent']), max(discovery, replay), abs_tol=1e-12):
            raise ValueError(f"{row['game_id']}: maximum does not match its plays")
    for rows in (tcca, npass):
        for row in rows:
            if not 0 <= int(row['levels_completed']) <= int(row['levels_total']):
                raise ValueError(f"{row['game_id']}: invalid completion count")
    def coverage(rows):
        return dict(games=len(rows), levels_total=sum(int(r['levels_total']) for r in rows), levels_completed=sum(int(r['levels_completed']) for r in rows), full_game_wins=sum(int(r['full_game_win']) for r in rows))
    return {
        'tcca-public25': {**coverage(tcca), 'scoring_games': sum(float(r['score_percent']) > 0 for r in tcca), 'score_percent': statistics.mean(float(r['score_percent']) for r in tcca), 'actions': sum(int(r['actions']) for r in tcca)},
        'virgil-npass': {**coverage(npass), 'scoring_games': sum(float(r['best_score_percent']) > 0 for r in npass), 'discovery_mean_percent': statistics.mean(float(r['discovery_score_percent']) for r in npass), 'replay_mean_percent': statistics.mean(float(r['replay_score_percent']) for r in npass), 'per_game_best_mean_percent': statistics.mean(float(r['best_score_percent']) for r in npass), 'physical_actions': sum(int(r['physical_actions']) for r in npass), 'sum_per_game_wall_seconds': sum(float(r['wall_seconds']) for r in npass), 'replay_regression_count': sum(float(r['replay_score_percent']) < float(r['discovery_score_percent']) for r in npass)},
    }


def verify(bundle: Path) -> dict[str, dict]:
    manifest = json.loads((bundle / 'manifest.json').read_text())
    for name, expected in manifest['checksums'].items():
        if hashlib.sha256((bundle / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'{name}: checksum mismatch')
    records = {r['id']: r for r in json.loads((bundle / 'records.json').read_text())['records']}
    derived = calculate(bundle)
    for name, metrics in derived.items():
        for key, value in metrics.items():
            expected = records[name]['metrics'][key]
            if not math.isclose(value, expected, rel_tol=1e-10, abs_tol=1e-10):
                raise ValueError(f'{name}.{key}: {value} != {expected}')
    return derived


if __name__ == '__main__':
    summaries = verify(ROOT / 'evidence/results-v1')
    for name, metrics in summaries.items():
        print(f"{name}: verified {metrics['games']} games, {metrics['levels_completed']}/{metrics['levels_total']} levels")
    print('Published table arithmetic and artifact checksums verified; no solver execution.')
