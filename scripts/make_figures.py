"""Render the README figures (SVG) from the published records.

Every number drawn here is read from evidence/results-v2/records.json, so the
figures cannot drift from the checked tables. Run from the repository root:

    python scripts/make_figures.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'

BG = '#0b0e13'
CARD = '#10151c'
LINE = '#232b36'
INK = '#f0f3f6'
MUTED = '#9da7b3'
FAINT = '#6e7781'
EMPTY = '#161c24'
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
ARC = {
    'blue': '#3e63dd', 'red': '#e5484d', 'green': '#30a46c', 'yellow': '#ffc53d',
    'grey': '#8b8d98', 'magenta': '#d6409f', 'orange': '#f76b15', 'sky': '#70b8ff',
    'maroon': '#a13544',
}


def records() -> dict[str, dict]:
    data = json.loads((ROOT / 'evidence/results-v2/records.json').read_text())
    return {r['id']: r for r in data['records']}


def svg(width: int, height: int, title: str, desc: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{title}</title>\n<desc id="d">{desc}</desc>\n{body}</svg>\n'
    )


def cell(x: float, y: float, s: float, fill: str, rx: float = 4) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" rx="{rx}" fill="{fill}"/>'


def grid(x0: float, y0: float, n: int, s: float, gap: float, filled: dict) -> str:
    out = [f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{n * s + (n - 1) * gap + 20}" '
           f'height="{n * s + (n - 1) * gap + 20}" rx="14" fill="{CARD}" stroke="{LINE}"/>']
    for r in range(n):
        for c in range(n):
            out.append(cell(x0 + c * (s + gap), y0 + r * (s + gap), s, filled.get((r, c), EMPTY)))
    return '\n'.join(out)


def hero() -> str:
    # A small invented puzzle: each seed casts a ray until it meets the edge or a filled cell.
    n = 7
    seeds = {(1, 0): ARC['red'], (6, 3): ARC['blue'], (4, 6): ARC['green']}
    rays = [((1, 0), (0, 1)), ((6, 3), (-1, 0)), ((4, 6), (0, -1))]
    out = dict(seeds)
    for (r, c), (dr, dc) in rays:
        rr, cc = r + dr, c + dc
        while 0 <= rr < n and 0 <= cc < n and (rr, cc) not in out:
            out[(rr, cc)] = seeds[(r, c)]
            rr, cc = rr + dr, cc + dc
    s, gap = 20, 4
    side = n * s + (n - 1) * gap
    gx, gy = 812, 128
    ox = gx + side + 76
    arrow_y = gy + side / 2
    palette = ''.join(
        cell(64 + i * 22, 384, 14, col, 3) for i, col in enumerate(ARC.values())
    )
    body = f'''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="{BG}"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.78" cy="0.45" r="0.5">
    <stop offset="0" stop-color="#3e63dd" stop-opacity="0.16"/><stop offset="1" stop-color="#3e63dd" stop-opacity="0"/>
  </radialGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="#1b222c"/>
  </pattern>
</defs>
<rect width="1280" height="440" rx="24" fill="url(#bg)"/>
<rect width="1280" height="440" rx="24" fill="url(#dots)"/>
<rect width="1280" height="440" rx="24" fill="url(#glow)"/>
<text x="64" y="92" fill="{FAINT}" font-family="{MONO}" font-size="14" letter-spacing="3">ARC RESEARCH RECORD  ·  APR – NOV 2026</text>
<text x="62" y="176" fill="{INK}" font-family="{SANS}" font-size="62" font-weight="700" letter-spacing="-1.5">Learning the rule</text>
<text x="62" y="248" fill="{INK}" font-family="{SANS}" font-size="62" font-weight="700" letter-spacing="-1.5">from a <tspan fill="{ARC['yellow']}">few</tspan> examples.</text>
<text x="64" y="304" fill="{MUTED}" font-family="{SANS}" font-size="20">A weight-free static-ARC solver in 84 KB, and agents that</text>
<text x="64" y="333" fill="{MUTED}" font-family="{SANS}" font-size="20">learn the rules of unseen ARC-AGI-3 games by playing them.</text>
{palette}
<text x="292" y="396" fill="{FAINT}" font-family="{MONO}" font-size="13" letter-spacing="1">KANISHK PAUL</text>
{grid(gx, gy, n, s, gap, seeds)}
<path d="M{gx + side + 30} {arrow_y}H{ox - 34}" stroke="{FAINT}" stroke-width="2" stroke-linecap="round"/>
<path d="M{ox - 44} {arrow_y - 8}L{ox - 34} {arrow_y}L{ox - 44} {arrow_y + 8}" fill="none" stroke="{FAINT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
{grid(ox, gy, n, s, gap, out)}
<text x="{gx - 10}" y="{gy + side + 44}" fill="{FAINT}" font-family="{MONO}" font-size="12" letter-spacing="2">INPUT</text>
<text x="{ox - 10}" y="{gy + side + 44}" fill="{FAINT}" font-family="{MONO}" font-size="12" letter-spacing="2">OUTPUT</text>
'''
    return svg(1280, 440, 'ARC research record — Kanishk Paul',
               'Learning the rule from a few examples. A small coloured-grid puzzle: three seeds on the input become rays on the output.',
               body)


def tiles(rec: dict[str, dict]) -> str:
    a1 = rec['0sr-arc1-public-eval']['metrics']
    cport = rec['0sr-c-port']['metrics']
    kag = rec[KAGGLE_BEST]['metrics']
    items = [
        (f"{a1['solved']}/{a1['tasks']}", ARC['yellow'], 'ARC-AGI-1 PUBLIC EVAL',
         f"{a1['solved_percent']:.1f}% · no weights · no LLM"),
        (f"{round(cport['binary_bytes'] / 1000)} KB", ARC['green'], 'THE WHOLE SOLVER',
         'one C file · libc only'),
        (f"{a1['cpu_seconds_per_task_mean']:.2f} s", ARC['sky'], 'CPU PER TASK',
         f"{a1['peak_memory_mb']} MB peak memory"),
        (f"#{kag['rank']:,}", ARC['red'], 'KAGGLE ARC PRIZE 2026',
         f"ARC-AGI-3 · of {kag['field_size']:,} teams"),
    ]
    w, h, gap = 302, 176, 24 / 3
    out = []
    for i, (big, col, label, sub) in enumerate(items):
        x = i * (w + gap)
        out.append(f'''<g transform="translate({x:.1f},0)">
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="{CARD}" stroke="{LINE}"/>
  <rect x="24" y="26" width="10" height="10" rx="2.5" fill="{col}"/>
  <text x="44" y="36" fill="{FAINT}" font-family="{MONO}" font-size="12" letter-spacing="1.8">{label}</text>
  <text x="22" y="112" fill="{INK}" font-family="{SANS}" font-size="56" font-weight="700" letter-spacing="-1.5">{big}</text>
  <text x="24" y="148" fill="{MUTED}" font-family="{SANS}" font-size="16">{sub}</text>
</g>''')
    return svg(1232, h, 'Headline numbers',
               'ARC-AGI-1 public evaluation score, solver size, CPU per task, and Kaggle ARC Prize 2026 rank.',
               '\n'.join(out) + '\n')


def progress(rec: dict[str, dict]) -> str:
    pts = rec['0sr-arc1-progression']['metrics']['points']
    pts = [(date.fromisoformat(p['date']), p['tasks_solved'], p['label']) for p in pts]
    d0, d1 = date(2026, 10, 27), date(2026, 11, 9)
    W, H, L, R, T, B = 1232, 380, 84, 48, 72, 64
    span = (d1 - d0).days

    def X(d):
        return L + (W - L - R) * (d - d0).days / span

    def Y(v):
        return T + (H - T - B) * (1 - v / 80)

    out = [f'<rect width="{W}" height="{H}" rx="20" fill="{CARD}" stroke="{LINE}"/>',
           f'<text x="32" y="42" fill="{FAINT}" font-family="{MONO}" font-size="12" letter-spacing="1.8">0SR · ARC-AGI-1 PUBLIC EVALUATION · TASKS SOLVED OF 400</text>']
    for v in (0, 20, 40, 60, 80):
        out.append(f'<path d="M{L} {Y(v):.1f}H{W - R}" stroke="{LINE}" stroke-dasharray="{"none" if v == 0 else "3 5"}"/>')
        out.append(f'<text x="{L - 14}" y="{Y(v) + 4:.1f}" text-anchor="end" fill="{FAINT}" font-family="{MONO}" font-size="12">{v}</text>')
    d = d0
    from datetime import timedelta
    while d <= d1:
        if d.day in (28, 30, 1, 3, 5, 7, 9):
            out.append(f'<text x="{X(d):.1f}" y="{H - 30}" text-anchor="middle" fill="{FAINT}" font-family="{MONO}" font-size="12">{d.strftime("%b %-d")}</text>')
        d += timedelta(days=1)
    # step line
    path = []
    for i, (dd, v, _) in enumerate(pts):
        if i == 0:
            path.append(f'M{X(dd):.1f} {Y(v):.1f}')
        else:
            path.append(f'H{X(dd):.1f}V{Y(v):.1f}')
    path.append(f'H{X(d1) - 6:.1f}')
    area = ' '.join(path) + f'V{Y(0):.1f}H{X(pts[0][0]):.1f}Z'
    out.append(f'<defs><linearGradient id="fillg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ARC["yellow"]}" stop-opacity="0.22"/><stop offset="1" stop-color="{ARC["yellow"]}" stop-opacity="0"/></linearGradient></defs>')
    out.append(f'<path d="{area}" fill="url(#fillg)"/>')
    out.append(f'<path d="{" ".join(path)}" fill="none" stroke="{ARC["yellow"]}" stroke-width="3" stroke-linejoin="round"/>')
    for i, (dd, v, label) in enumerate(pts):
        last = i == len(pts) - 1
        out.append(f'<circle cx="{X(dd):.1f}" cy="{Y(v):.1f}" r="{7 if last else 5}" fill="{BG}" stroke="{ARC["yellow"]}" stroke-width="3"/>')
        anchor = 'end' if last else 'start'
        dx = -14 if last else 12
        out.append(f'<text x="{X(dd) + dx:.1f}" y="{Y(v) - 16:.1f}" text-anchor="{anchor}" fill="{INK}" font-family="{SANS}" font-size="{26 if last else 20}" font-weight="700">{v}</text>')
        out.append(f'<text x="{X(dd) + dx:.1f}" y="{Y(v) + (26 if not last else -44):.1f}" text-anchor="{anchor}" fill="{MUTED}" font-family="{SANS}" font-size="13">{label}</text>')
    return svg(W, H, '0SR progress on ARC-AGI-1',
               'Step chart of tasks solved on the ARC-AGI-1 public evaluation set between late October and early November 2026.',
               '\n'.join(out) + '\n')


def timeline(rec: dict[str, dict]) -> str:
    W, H = 1232, 320
    d0, d1 = date(2026, 3, 25), date(2026, 11, 20)
    L, R = 48, 48

    def X(d):
        return L + (W - L - R) * (d - d0).days / (d1 - d0).days

    out = [f'<rect width="{W}" height="{H}" rx="20" fill="{CARD}" stroke="{LINE}"/>',
           f'<text x="32" y="42" fill="{FAINT}" font-family="{MONO}" font-size="12" letter-spacing="1.8">EIGHT MONTHS · SEVEN RESEARCH LINES</text>']
    axis_y = 240
    out.append(f'<path d="M{L} {axis_y}H{W - R}" stroke="{LINE}" stroke-width="2"/>')
    for m in range(4, 12):
        dm = date(2026, m, 1)
        out.append(f'<path d="M{X(dm):.1f} {axis_y - 5}V{axis_y + 5}" stroke="{FAINT}"/>')
        out.append(f'<text x="{X(dm) + 6:.1f}" y="{axis_y + 30}" fill="{FAINT}" font-family="{MONO}" font-size="12">{dm.strftime("%b").upper()}</text>')
    for i, m in enumerate(MILESTONES):
        x = X(date.fromisoformat(m['date']))
        top = (88, 136, 184)[m['row']]
        col = ARC[m['color']]
        out.append(f'<path d="M{x:.1f} {top + 10}V{axis_y - 8}" stroke="{col}" stroke-opacity="0.5" stroke-dasharray="2 4"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{axis_y}" r="6" fill="{col}"/>')
        anchor = m['anchor']
        dx = -8 if anchor == 'end' else 8
        out.append(f'<text x="{x + dx:.1f}" y="{top}" text-anchor="{anchor}" fill="{INK}" font-family="{SANS}" font-size="16" font-weight="700">{m["name"]}</text>')
        out.append(f'<text x="{x + dx:.1f}" y="{top + 20}" text-anchor="{anchor}" fill="{MUTED}" font-family="{SANS}" font-size="13">{m["note"](rec)}</text>')
    return svg(W, H, 'Research timeline',
               'Dated milestones of the research lines from April to November 2026.',
               '\n'.join(out) + '\n')


KAGGLE_BEST = 'kaggle-zerostar-attempt-1'
MILESTONES = [
    dict(date='2026-04-18', row=0, anchor='start', name='TCCA', color='grey', note=lambda r: 'first offline benchmark'),
    dict(date='2026-07-02', row=1, anchor='start', name='IWM → Categorical Cat', color='magenta', note=lambda r: 'learned-model prototypes'),
    dict(date='2026-07-19', row=0, anchor='start', name='Virgil', color='green', note=lambda r: 'LS20 level from a model plan'),
    dict(date='2026-09-12', row=2, anchor='end', name='N-pass', color='blue', note=lambda r: '17 levels on 25 public games'),
    dict(date='2026-10-30', row=0, anchor='end', name='0SR', color='yellow', note=lambda r: 'static ARC: ' + ' → '.join(str(p['tasks_solved']) for p in r['0sr-arc1-progression']['metrics']['points']) + ' of 400'),
    dict(date='2026-11-01', row=1, anchor='end', name='Zerostar', color='red',
         note=lambda r: f"Kaggle #{r[KAGGLE_BEST]['metrics']['rank']:,} of {r[KAGGLE_BEST]['metrics']['field_size']:,}"),
]


def main() -> None:
    rec = records()
    OUT.mkdir(exist_ok=True)
    (OUT / 'hero.svg').write_text(hero())
    (OUT / 'stats.svg').write_text(tiles(rec))
    (OUT / '0sr-progress.svg').write_text(progress(rec))
    (OUT / 'timeline.svg').write_text(timeline(rec))
    print('wrote', ', '.join(p.name for p in sorted(OUT.glob('*.svg'))))


if __name__ == '__main__':
    main()
