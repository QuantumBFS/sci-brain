#!/usr/bin/env python3
"""Full-campaign report: aggregate every attempt across all cycles.

Usage:
    python3 gen_campaign.py --dir docs/discussion/ [--out campaign.html]
        [--extra docs/discussion/campaign-extra.json]

Reads every cycle-*.json in --dir (siblings of the per-cycle reports),
renders a single campaign.html listing ALL attempts across ALL cycles
(per-cycle summary table + complete attempt table), and links each
attempt's id to its worktree LOG.md. Reuses report.py for CSS/charts/
escaping. Deterministic: same inputs give byte-identical output.

Attempts consumed outside a scored cycle can be supplied with `--extra`;
they render with an "unscored" chip so the campaign table stays complete.
The extra file is a JSON array whose entries contain `id`, `kind`, `parent`,
`hypothesis`, and `causal_note`, plus optional `log_path`.
"""

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report as R

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
    invalid = []
    for f in sorted(directory.glob("cycle-*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            errs = R.validate_cycle(d)
        except (json.JSONDecodeError, OSError) as e:
            d, errs = None, [str(e)]
        if errs:
            invalid.append(f"{f.name}: {errs[0]}")
        else:
            d["_file"] = f.name.replace(".json", ".html")
            cycles.append(d)
    if invalid:
        raise ValueError("invalid cycle data: " + "; ".join(invalid))
    return cycles


def load_extra(path):
    """Load optional unscored attempts without baking campaign data into code."""
    if path is None:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise ValueError(f"cannot read extra attempts: {e}") from e
    if not isinstance(data, list):
        raise ValueError("extra attempts must be a JSON array")
    required = ("id", "kind", "parent", "hypothesis", "causal_note")
    rows = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            raise ValueError(f"extra[{i}] must be an object")
        missing = [field for field in required if field not in entry]
        if missing:
            raise ValueError(f"extra[{i}] missing {', '.join(missing)}")
        if not isinstance(entry["id"], int):
            raise ValueError(f"extra[{i}].id must be an integer")
        if entry["kind"] is not None and entry["kind"] not in R.KINDS:
            raise ValueError(f"extra[{i}].kind must be one of {R.KINDS} or null")
        if entry["parent"] is not None and not isinstance(entry["parent"], int):
            raise ValueError(f"extra[{i}].parent must be an integer or null")
        for field in ("hypothesis", "causal_note"):
            if not isinstance(entry[field], str):
                raise ValueError(f"extra[{i}].{field} must be a string")
        row = dict(entry)
        row.setdefault("log_path", f".worktrees/attempt-{entry['id']:03d}/LOG.md")
        if not isinstance(row["log_path"], str):
            raise ValueError(f"extra[{i}].log_path must be a string")
        rows.append(row)
    return rows


def render(cycles, extra_attempts, records_note, out):
    rows = []
    for c in cycles:
        for a in c["attempts"]:
            a = dict(a)
            if isinstance(a.get("parent"), str):
                a["parent"] = int(a["parent"])
            rows.append(dict(a, cycle=c["cycle"], _file=c["_file"]))
    for entry in extra_attempts:
        rows.append(dict(entry, cycle=None, primary=None, status=None, _file=None))
    rows.sort(key=lambda r: r["id"])
    ids = [r["id"] for r in rows]
    duplicates = sorted({attempt_id for attempt_id in ids if ids.count(attempt_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate attempt ids: {duplicates}")

    trows = []
    for r in rows:
        cyc = (f'<a href="{r["_file"]}">c{r["cycle"]:02d}</a>'
               if r["cycle"] is not None else '<span class="note">—</span>')
        log_path = html.escape(r["log_path"], quote=True)
        log = f'<a href="../../{log_path}">{r["id"]:03d}</a>'
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
            f'<td class="num">{k}/{n}</td>'
            f'<td class="hyp">{html.escape(R.first_sentence(c["reflection"]["next"]))}</td></tr>')

    yield_pts = []
    for c in cycles:
        count = len(c["attempts"])
        improved_count = sum(1 for a in c["attempts"]
                             if a["status"] == "improved")
        yield_pts.append((c["cycle"], improved_count / count if count else None))
    chart = R.svg_line_chart(yield_pts, title="yield (fraction improved) by cycle",
                             width=720, height=200)

    total = len(rows)
    cycle_listed = sum(1 for r in rows if r["cycle"] is not None)
    improved = sum(1 for r in rows if r["status"] == "improved")
    project = cycles[-1]["project"]
    note_extra = (f" Records: {html.escape(records_note)}."
                  if records_note else "")
    metric_defs = {(c["primary_metric"]["name"],
                    c["primary_metric"]["direction"]) for c in cycles}
    if len(metric_defs) == 1:
        metric_name, metric_direction = next(iter(metric_defs))
        metric_note = (f"Primary = {html.escape(metric_name)} "
                       f"({'higher' if metric_direction == 'max' else 'lower'} is better).")
    else:
        metric_note = ("Primary metric definitions vary across cycles; each cycle page "
                       "records its own metric and direction.")

    body = f"""
<h1>{html.escape(project)} — full campaign</h1>
<p class="meta">{len(cycles)} cycles · {total} worktree attempts
({cycle_listed} cycle-listed) · {improved} improved</p>
<div class="card">
<figure><figcaption>yield by cycle (fraction of attempts that improved)</figcaption>{chart}</figure>
</div>
<h2>Cycles</h2>
<div class="scroll"><table>
<thead><tr><th>cycle</th><th>date</th><th class="num">attempts</th><th class="num">yield</th>
<th>next</th></tr></thead>
<tbody>{''.join(srows)}</tbody></table></div>
<h2>All attempts ({total})</h2>
<div class="scroll"><table>
<thead><tr><th>id</th><th>cycle</th><th>kind</th><th class="num">parent</th>
<th class="num">primary</th><th>status</th><th>hypothesis</th><th>causal note</th></tr></thead>
<tbody>{''.join(trows)}</tbody></table></div>
<p class="note">{metric_note} Attempts listed without a cycle came from the optional
extra-attempt records and were not cycle-scored.{note_extra}</p>
<footer><a href="index.html">index</a></footer>
"""
    out.write_text(R.page(f"{project} — full campaign", body), encoding="utf-8")
    index_path = out.parent / "index.html"
    index_path.write_text(R.render_index(cycles, campaign_href=out.name),
                          encoding="utf-8")
    print(f"wrote {out}\nwrote {index_path}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True,
                    help="directory holding cycle-*.json (docs/discussion/)")
    ap.add_argument("--out", default="campaign.html",
                    help="output filename inside --dir (default campaign.html)")
    ap.add_argument("--records", default="",
                    help="optional one-line records summary appended to the note")
    ap.add_argument("--extra", type=Path,
                    help="optional JSON array of unscored/worktree-only attempts")
    args = ap.parse_args(argv)
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"gen_campaign.py: no such directory: {directory}", file=sys.stderr)
        sys.exit(1)
    try:
        cycles = load(directory)
        if not cycles:
            raise ValueError("no valid cycle-*.json found")
        extra_attempts = load_extra(args.extra)
        render(cycles, extra_attempts, args.records, directory / args.out)
    except ValueError as e:
        print(f"gen_campaign.py: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
