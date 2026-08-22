#!/usr/bin/env python3
"""Full-campaign report: aggregate every attempt across all cycles.

Usage:
    python3 gen_campaign.py --dir docs/discussion/ [--out campaign.html]

Reads every cycle-*.json in --dir (siblings of the per-cycle reports),
renders a single campaign.html listing ALL attempts across ALL cycles
(per-cycle summary table + complete attempt table), and links each
attempt's id to its worktree LOG.md. Reuses report.py for CSS/charts/
escaping. Deterministic: same inputs give byte-identical output.

Attempts consumed by dev campaigns without validator scoring (worktree
present, no cycle listing) can be described in WORKTREE_ONLY below; they
render with an "unscored" chip so the campaign table stays complete.
"""

import argparse
import glob
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report as R

# id -> (kind, parent, hypothesis, causal_note) for worktree-only attempts
# that no cycle JSON lists (dev campaigns, pre-scoring era). Keys are ints.
WORKTREE_ONLY = {
    25: dict(kind=None, parent=None,
             hypothesis="worktree attempt-025 exists but holds no LOG.md / report.json — no record preserved",
             causal_note="no LOG.md, no report.json, no cycle listing"),
    57: dict(kind="draft", parent=38,
             hypothesis="scalable quotient-graph VE seed (AMD-style elimination order) — fixes 038's heap-freeze at 4k+ labels",
             causal_note="dev campaign (057/058): seeds emitted in tens of ms at 30k-70k tensors (vs 84 s before); relational_4 tc 108.97 vs ~202 floor; not validator-scored"),
    58: dict(kind="improve", parent=53,
             hypothesis="bounded cheap-first VE peel, adaptive ladder + racing fallback (053 falsified at nqueens; new annealer-immobile regime)",
             causal_note="confirmed on the immobile regime: decisive win is unbounded VE rung + library-greedy-hang fix; finite rungs carry linkage/reg3; not validator-scored"),
}

KIND_CLS = {"draft": "kind-draft", "improve": "kind-improve", "debug": "kind-debug"}
ST_CLS = {"improved": "st-good", "no-change": "st-neutral",
          "failed": "st-critical", "timeout": "st-serious"}


def chip(s):
    if s is None:
        return '<span class="chip st-neutral">unscored</span>'
    return f'<span class="chip {ST_CLS.get(s, "st-neutral")}">{html.escape(s)}</span>'


def badge(k):
    if k is None:
        return '<span class="badge">—</span>'
    return f'<span class="badge {KIND_CLS.get(k, "")}">{html.escape(k)}</span>'


def fmt(v):
    if v is None:
        return "—"
    return f"{v:.4g}" if isinstance(v, float) else str(v)


def load(directory):
    cycles = []
    for f in sorted(directory.glob("cycle-*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            errs = R.validate_cycle(d)
        except (json.JSONDecodeError, OSError) as e:
            d, errs = None, [str(e)]
        if errs:
            print(f"gen_campaign.py: skipping {f.name}: {errs[0]}", file=sys.stderr)
            continue
        d["_file"] = f.name.replace(".json", ".html")
        cycles.append(d)
    return cycles


def render(cycles, records_note, out):
    rows = []
    for c in cycles:
        for a in c["attempts"]:
            a = dict(a)
            if isinstance(a.get("parent"), str):
                a["parent"] = int(a["parent"])
            rows.append(dict(a, cycle=c["cycle"], _file=c["_file"]))
    for n, e in WORKTREE_ONLY.items():
        rows.append(dict(id=n, cycle=None, kind=e["kind"], parent=e["parent"],
                         hypothesis=e["hypothesis"], primary=None, status=None,
                         causal_note=e["causal_note"],
                         log_path=f".worktrees/attempt-{n:03d}/LOG.md", _file=None))
    rows.sort(key=lambda r: r["id"])

    trows = []
    for r in rows:
        cyc = (f'<a href="{r["_file"]}">c{r["cycle"]:02d}</a>'
               if r["cycle"] is not None else '<span class="note">—</span>')
        log = f'<a href="../../{r["log_path"]}">{r["id"]:03d}</a>'
        parent = f'{r["parent"]:03d}' if r["parent"] is not None else "—"
        trows.append(
            f'<tr><td class="idcell">{log}</td><td>{cyc}</td>'
            f'<td>{badge(r["kind"])}</td>'
            f'<td class="num">{parent}</td><td class="num">{fmt(r["primary"])}</td>'
            f'<td>{chip(r["status"])}</td>'
            f'<td class="hyp">{html.escape(r["hypothesis"] or "")}</td>'
            f'<td class="hyp">{html.escape(r["causal_note"] or "")}</td></tr>')

    srows = []
    for c in sorted(cycles, key=lambda c: c["cycle"]):
        k = sum(1 for a in c["attempts"] if a["status"] == "improved")
        n = len(c["attempts"])
        lo, hi = c["attempts_range"]
        srows.append(
            f'<tr><td><a href="{c["_file"]}">cycle {c["cycle"]:02d}</a></td>'
            f'<td>{c["date_utc"][:10]}</td><td class="num">{lo:03d}–{hi:03d}</td>'
            f'<td class="num">{k}/{n}</td><td class="num">{len(c["blacklist_new"])}</td>'
            f'<td class="hyp">{html.escape(R.first_sentence(c["reflection"]["next"]))}</td></tr>')

    yield_pts = [(c["cycle"],
                  sum(1 for a in c["attempts"] if a["status"] == "improved") / len(c["attempts"]))
                 for c in cycles]
    chart = R.svg_line_chart(yield_pts, title="yield (fraction improved) by cycle",
                             width=720, height=200)

    total = len(rows)
    scored = sum(1 for r in rows if r["primary"] is not None)
    improved = sum(1 for r in rows if r["status"] == "improved")
    blacklisted = sum(len(c["blacklist_new"]) for c in cycles)
    project = cycles[-1]["project"]
    note_extra = (f" Records: {records_note}." if records_note else "")

    body = f"""
<h1>{html.escape(project)} — full campaign</h1>
<p class="meta">{len(cycles)} cycles · {total} worktree attempts
({scored} validator-scored) · {improved} improved · {blacklisted} blacklisted approaches</p>
<div class="card">
<figure><figcaption>yield by cycle (fraction of attempts that improved)</figcaption>{chart}</figure>
</div>
<h2>Cycles</h2>
<div class="scroll"><table>
<thead><tr><th>cycle</th><th>date</th><th class="num">attempts</th><th class="num">yield</th>
<th class="num">blacklist</th><th>next</th></tr></thead>
<tbody>{''.join(srows)}</tbody></table></div>
<h2>All attempts ({total})</h2>
<div class="scroll"><table>
<thead><tr><th>id</th><th>cycle</th><th>kind</th><th class="num">parent</th>
<th class="num">primary</th><th>status</th><th>hypothesis</th><th>causal note</th></tr></thead>
<tbody>{''.join(trows)}</tbody></table></div>
<p class="note">Primary = validator score (mean tc delta vs record; higher better). Score scales
may differ across metric-axis changes between cycles — direction (max) is the same; each cycle's
page carries its own axis. Attempts listed without a cycle were consumed by dev campaigns
without validator scoring (their worktrees document them).{note_extra}</p>
<footer><a href="index.html">index</a></footer>
"""
    out.write_text(R.page(f"{project} — full campaign", body), encoding="utf-8")
    print(f"wrote {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True,
                    help="directory holding cycle-*.json (docs/discussion/)")
    ap.add_argument("--out", default="campaign.html",
                    help="output filename inside --dir (default campaign.html)")
    ap.add_argument("--records", default="",
                    help="optional one-line records summary appended to the note")
    args = ap.parse_args(argv)
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"gen_campaign.py: no such directory: {directory}", file=sys.stderr)
        sys.exit(1)
    cycles = load(directory)
    if not cycles:
        print("gen_campaign.py: no valid cycle-*.json found", file=sys.stderr)
        sys.exit(1)
    render(cycles, args.records, directory / args.out)


if __name__ == "__main__":
    main()
