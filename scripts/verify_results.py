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


V2_STATUSES = {'replayable_observation_record', 'recalculable_summary', 'documented_historical_aggregate', 'leaderboard_record'}
V2_REQUIRED = ('id', 'label', 'measurement_date', 'protocol', 'evidence_status', 'source_record', 'metrics')


def _close(name: str, key: str, value, expected) -> None:
    if value is None or expected is None:
        if value != expected:
            raise ValueError(f'{name}.{key}: {value} != {expected}')
    elif not math.isclose(value, expected, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError(f'{name}.{key}: {value} != {expected}')


def calculate_v2(bundle: Path) -> dict[str, dict]:
    """Recompute every per-run aggregate of the v2 public-game table."""
    with (bundle / 'public25-per-game.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    runs: dict[str, list[dict]] = {}
    for row in rows:
        runs.setdefault(row['run_id'], []).append(row)
    derived = {}
    for run_id, table in runs.items():
        if len({r['game_id'] for r in table}) != len(table):
            raise ValueError(f'{run_id}: duplicate game IDs')
        for row in table:
            levels, total = int(row['levels_completed']), int(row['levels_total'])
            if not 0 <= levels <= total:
                raise ValueError(f"{run_id} {row['game_id']}: invalid completion count")
            if int(row['full_game_win']) != int(levels == total):
                raise ValueError(f"{run_id} {row['game_id']}: full-game win does not match its levels")
        scores = [float(r['score_percent']) for r in table]
        derived[run_id] = dict(
            games=len(table),
            levels_total=sum(int(r['levels_total']) for r in table),
            levels_completed=sum(int(r['levels_completed']) for r in table),
            full_game_wins=sum(int(r['full_game_win']) for r in table),
            scoring_games=sum(s > 0 for s in scores),
            score_percent=statistics.mean(scores),
            median_score_percent=statistics.median(scores),
            actions=sum(int(r['actions']) for r in table),
        )
    return derived


def _check_internal(record: dict) -> str:
    """Arithmetic that must hold inside a record without a per-game table."""
    name, m = record['id'], record['metrics']
    if 'points' in m:
        solved = [p['tasks_solved'] for p in m['points']]
        dates = [p['date'] for p in m['points']]
        if dates != sorted(dates) or not all(0 <= v <= m['tasks'] for v in solved):
            raise ValueError(f'{name}: progression points out of order or out of range')
        return ' -> '.join(f"{v}" for v in solved) + f" of {m['tasks']}"
    if 'tasks' in m:
        _close(name, 'solved_percent', 100 * m['solved'] / m['tasks'], m.get('solved_percent', 100 * m['solved'] / m['tasks']))
        if 'credit' in m:
            _close(name, 'credit_percent', 100 * m['credit'] / m['tasks'], m['credit_percent'])
        _close(name, 'gain', m['solved'] - m['reference_solved'], m['gain_wins'] - m['gain_losses'])
        if 'strict_tasks' in m and not (m['strict_tasks'] == m['tasks'] - 1 and m['strict_solved'] in (m['solved'], m['solved'] - 1)):
            raise ValueError(f'{name}: strict score does not follow from the headline')
        if 'tasks_excluding_overlap' in m:
            _close(name, 'tasks_excluding_overlap', m['tasks'] - m['overlap_tasks_excluded'], m['tasks_excluding_overlap'])
            if not 0 <= m['solved_excluding_overlap'] <= m['solved']:
                raise ValueError(f'{name}: overlap-excluded score exceeds the raw score')
            return f"{m['solved_excluding_overlap']}/{m['tasks_excluding_overlap']} excluding overlap ({m['solved']}/{m['tasks']} raw)"
        return f"{m['solved']}/{m['tasks']} (strict {m['strict_solved']}/{m['strict_tasks']}), +{m['gain_wins']}/-{m['gain_losses']} vs reference"
    if 'differing_answers' in m:
        return f"{m['differing_answers']} differing answers in {m['identity_task_runs']} runs; {m['c_source_bytes']} B source, {m['binary_bytes']} B binary"
    return f"aggregate only, score {m['score_percent']}"


def verify_v2(bundle: Path) -> dict[str, str]:
    """Check the v2 bundle: checksums, record shape, per-game and leaderboard tables. Returns one summary line per record."""
    manifest = json.loads((bundle / 'manifest.json').read_text())
    for name, expected in manifest['checksums'].items():
        if hashlib.sha256((bundle / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'{name}: checksum mismatch')
    document = json.loads((bundle / 'records.json').read_text())
    if document['schema_version'] != 2 or manifest['schema_version'] != 2:
        raise ValueError('schema_version must be 2')
    records = {}
    for record in document['records']:
        missing = [k for k in V2_REQUIRED if k not in record]
        if missing or record['evidence_status'] not in V2_STATUSES or record['id'] in records:
            raise ValueError(f"{record.get('id')}: malformed record")
        records[record['id']] = record

    lines: dict[str, str] = {}
    derived = calculate_v2(bundle)
    tabled = {k for k, r in records.items() if r.get('public_table') == 'public25-per-game.csv'}
    if set(derived) != tabled:
        raise ValueError(f'public25 table runs {sorted(set(derived) ^ tabled)} do not match records')
    with (bundle / 'public25-per-game.csv').open(newline='') as f:
        game_sets = {}
        for row in csv.DictReader(f):
            game_sets.setdefault(row['run_id'], set()).add(row['game_id'])
    if len({frozenset(s) for s in game_sets.values()}) != 1:
        raise ValueError('public25 runs do not cover the same games')
    for name, metrics in derived.items():
        for key, value in metrics.items():
            if key in records[name]['metrics']:
                _close(name, key, value, records[name]['metrics'][key])
        lines[name] = f"verified {metrics['games']} games, {metrics['levels_completed']}/{metrics['levels_total']} levels, mean {metrics['score_percent']:.5f}"

    with (bundle / 'kaggle-leaderboard.csv').open(newline='') as f:
        board = list(csv.DictReader(f))
    boarded = {k for k, r in records.items() if r['evidence_status'] == 'leaderboard_record'}
    if sorted(r['run_id'] for r in board) != sorted(boarded):
        raise ValueError('kaggle-leaderboard.csv rows do not match leaderboard records')
    for row in board:
        record = records[row['run_id']]
        m = record['metrics']
        if row['date'] != record['measurement_date'] or row['entry'] != record['label'] or row['leaderboard'] != record['leaderboard']:
            raise ValueError(f"{row['run_id']}: leaderboard row does not match its record")
        if record['leaderboard'] not in document['leaderboards']:
            raise ValueError(f"{row['run_id']}: undefined leaderboard")
        _close(row['run_id'], 'score_percent', float(row['score_percent']), m['score_percent'])
        for key in ('rank', 'field_size'):
            _close(row['run_id'], key, int(row[key]) if row[key] else None, m[key])
        if m['rank'] is not None and not 1 <= m['rank'] <= m['field_size']:
            raise ValueError(f"{row['run_id']}: rank outside field")
        place = f", rank {m['rank']}/{m['field_size']}" if m['rank'] else ''
        lines[row['run_id']] = f"leaderboard row matches ({row['score_percent']} on {row['leaderboard']}{place})"

    for name, record in records.items():
        if name not in lines:
            lines[name] = _check_internal(record)
    return {name: lines[name] for name in records}


if __name__ == '__main__':
    summaries = verify(ROOT / 'evidence/results-v1')
    for name, metrics in summaries.items():
        print(f"{name}: verified {metrics['games']} games, {metrics['levels_completed']}/{metrics['levels_total']} levels")
    for name, line in verify_v2(ROOT / 'evidence/results-v2').items():
        print(f'{name}: {line}')
    print('Published table arithmetic and artifact checksums verified; no solver execution.')
