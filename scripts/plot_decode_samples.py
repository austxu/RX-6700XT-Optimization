#!/usr/bin/env python3
"""Draw every retained-a551 decode (tg128) sample as an SVG strip chart for the README.

Reads release/evidence/campaigns/llama2-retained-a551/raw-samples.csv and writes
docs/images/decode-samples.svg. Standard library only; the output is deterministic.
"""

import csv
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "release/evidence/campaigns/llama2-retained-a551/raw-samples.csv"
OUT = ROOT / "docs/images/decode-samples.svg"

W, H = 900, 330
LEFT, RIGHT = 190, 100
LO, HI = 72.0, 92.0
SCOREBOARD = 83.88
BG, INK, MUTED, GRID = "#0e0f12", "#f1eee6", "#8b8d94", "#2a2c33"
COLOR = {"control": "#8b8d94", "candidate": "#e5735a"}
ROWS = [  # (flash_attn, role, label, y)
    ("0", "control", "FA off · control", 92),
    ("0", "candidate", "FA off · optimized", 132),
    ("1", "control", "FA on · control", 212),
    ("1", "candidate", "FA on · optimized", 252),
]


def x(tps: float) -> float:
    return LEFT + (tps - LO) / (HI - LO) * (W - LEFT - RIGHT)


def main() -> None:
    with SAMPLES.open() as f:
        rows = [r for r in csv.DictReader(f) if r["workload"] == "tg128"]

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        'font-family="ui-monospace, SFMono-Regular, Menlo, monospace">',
        f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>',
        f'<text x="28" y="40" fill="{INK}" font-size="15">Llama 2 7B Q4_0 decode (tg128), every sample</text>',
        f'<text x="28" y="60" fill="{MUTED}" font-size="12">42 per row: 3 ABBA cycles x 2 invocations x 7 repetitions. Ticks mark the mean.</text>',
    ]
    for t in range(int(LO), int(HI) + 1, 4):
        out.append(f'<line x1="{x(t):.1f}" y1="72" x2="{x(t):.1f}" y2="276" stroke="{GRID}"/>')
        out.append(f'<text x="{x(t):.1f}" y="296" fill="{MUTED}" font-size="11" text-anchor="middle">{t}</text>')
    out.append(f'<text x="{x((LO + HI) / 2):.1f}" y="316" fill="{MUTED}" font-size="11" text-anchor="middle">tokens / s</text>')

    sx = x(SCOREBOARD)
    out.append(f'<line x1="{sx:.1f}" y1="72" x2="{sx:.1f}" y2="152" stroke="{INK}" stroke-dasharray="3 4" opacity=".6"/>')
    out.append(f'<rect x="{sx + 2:.1f}" y="70" width="190" height="16" fill="{BG}"/>')
    out.append(f'<text x="{sx + 6:.1f}" y="82" fill="{MUTED}" font-size="11">public scoreboard row, 83.88</text>')

    for fa, role, label, y in ROWS:
        vals = [float(r["tps"]) for r in rows if r["flash_attn"] == fa and r["role"] == role]
        out.append(f'<text x="28" y="{y + 4}" fill="{INK if role == "candidate" else MUTED}" font-size="12">{label}</text>')
        for i, v in enumerate(vals):
            dy = (i % 7 - 3) * 2.2  # spread the seven repetitions vertically
            out.append(f'<circle cx="{x(v):.1f}" cy="{y + dy:.1f}" r="2.6" fill="{COLOR[role]}" fill-opacity=".55"/>')
        m = mean(vals)
        out.append(f'<line x1="{x(m):.1f}" y1="{y - 12}" x2="{x(m):.1f}" y2="{y + 12}" stroke="{COLOR[role]}" stroke-width="2.5"/>')
        out.append(f'<text x="{W - 20}" y="{y + 4}" fill="{COLOR[role]}" font-size="12" text-anchor="end">{m:.2f}</text>')

    out.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
