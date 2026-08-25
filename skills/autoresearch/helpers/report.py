#!/usr/bin/env python3
"""Render per-cycle HTML reports for the autoresearch run stage.

Usage:
    python3 report.py --cycle NN --dir docs/discussion/

Reads cycle-NN.json (schema: ../references/report-schema.md) plus every other
cycle-*.json in --dir, writes cycle-NN.html and regenerates index.html. Both
outputs are self-contained (inline CSS + SVG, no JS, no external requests).
Python 3 stdlib only. Deterministic: same inputs give byte-identical output,
so regenerating old cycles after a template change is safe.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = 1

REQUIRED_TOP = [
    "schema_version", "cycle", "date_utc", "project", "attempts_range",
    "attempts_remaining", "primary_metric", "bar", "best_this_cycle",
    "best_prior", "holdout", "attempts", "reflection", "lessons",
    "blacklist_new", "insight_promotions",
]
REQUIRED_ATTEMPT = ["id", "kind", "parent", "hypothesis", "primary", "status",
                    "log_path"]
REQUIRED_LESSON = ["observation", "root_cause", "evidence", "implication"]
CONFIDENCES = ("confirmed", "suspected")
REFLECTION_SECTIONS = ["review", "evidence", "literature", "todo", "next"]
KINDS = ("draft", "improve", "debug")
STATUSES = ("improved", "no-change", "failed", "timeout")
DIRECTIONS = ("min", "max")


# ---------------------------------------------------------------- validation

def validate_cycle(data):
    """Return a list of error strings, each naming the offending field."""
    errors = []
    if not isinstance(data, dict):
        return ['top level is not a JSON object']
    for f in REQUIRED_TOP:
        if f not in data:
            errors.append(f'missing required field "{f}"')
    pm = data.get("primary_metric")
    if isinstance(pm, dict):
        for f in ("name", "direction"):
            if f not in pm:
                errors.append(f'missing required field "primary_metric.{f}"')
        if pm.get("direction") not in DIRECTIONS:
            errors.append(f'"primary_metric.direction" must be one of {DIRECTIONS}')
    elif "primary_metric" in data:
        errors.append('"primary_metric" must be an object')
    bar = data.get("bar")
    if isinstance(bar, dict):
        for f in ("value", "source"):
            if f not in bar:
                errors.append(f'missing required field "bar.{f}"')
    elif "bar" in data:
        errors.append('"bar" must be an object')
    holdout = data.get("holdout")
    if isinstance(holdout, dict):
        for f in ("spent", "result"):
            if f not in holdout:
                errors.append(f'missing required field "holdout.{f}"')
    elif "holdout" in data:
        errors.append('"holdout" must be an object')
    refl = data.get("reflection")
    if isinstance(refl, dict):
        for f in REFLECTION_SECTIONS:
            if f not in refl:
                errors.append(f'missing required field "reflection.{f}"')
    elif "reflection" in data:
        errors.append('"reflection" must be an object')
    if "score_formula" in data and not (
        isinstance(data["score_formula"], str) and data["score_formula"].strip()
    ):
        errors.append('"score_formula" must be a non-empty string when present')
    attempts = data.get("attempts")
    if isinstance(attempts, list):
        for i, a in enumerate(attempts):
            if not isinstance(a, dict):
                errors.append(f'"attempts[{i}]" is not an object')
                continue
            for f in REQUIRED_ATTEMPT:
                if f not in a:
                    errors.append(f'missing required field "attempts[{i}].{f}"')
            if "kind" in a and a["kind"] not in KINDS:
                errors.append(f'"attempts[{i}].kind" must be one of {KINDS}')
            if "status" in a and a["status"] not in STATUSES:
                errors.append(f'"attempts[{i}].status" must be one of {STATUSES}')
    elif "attempts" in data:
        errors.append('"attempts" must be an array')
    lessons = data.get("lessons")
    if isinstance(lessons, list):
        if not lessons:
            errors.append('"lessons" must contain at least one entry — '
                          'every cycle has something to diagnose')
        for i, l in enumerate(lessons):
            if not isinstance(l, dict):
                errors.append(f'"lessons[{i}]" is not an object')
                continue
            for f in REQUIRED_LESSON:
                if not (isinstance(l.get(f), str) and l[f].strip()):
                    errors.append(f'missing required field "lessons[{i}].{f}"')
            if "confidence" in l and l["confidence"] not in CONFIDENCES:
                errors.append(f'"lessons[{i}].confidence" must be one of '
                              f'{CONFIDENCES}')
    elif "lessons" in data:
        errors.append('"lessons" must be an array')
    return errors


# ------------------------------------------------------------------ helpers

def esc(s):
    return html.escape(str(s), quote=True)


def fmt(v):
    if v is None:
        return "—"  # em dash
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def best_so_far(cycles, direction):
    """[(cycle, running best_this_cycle)], None until a scored cycle appears."""
    pick = max if direction == "max" else min
    series, best = [], None
    for c in sorted(cycles, key=lambda c: c["cycle"]):
        v = c.get("best_this_cycle")
        if v is not None:
            best = v if best is None else pick(best, v)
        series.append((c["cycle"], best))
    return series


def fmt_date(date_utc):
    """YYYY-MM-DD[Thh:mm[:ss]Z] -> 'YYYY-MM-DD hh:mm UTC' (seconds dropped)."""
    s = date_utc.replace("Z", "")
    if "T" in s:
        date, time = s.split("T", 1)
        time = ":".join(time.split(":")[:2])
        return f"{date} {time} UTC"
    return s


def first_sentence(md_text):
    text = re.sub(r"[*`_#]", "", md_text or "").strip()
    m = re.split(r"(?<=[.!?])\s", text, maxsplit=1)
    return m[0] if m else text


# ----------------------------------------------------------------- markdown

def md_inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\s][^*]*)\*(?!\*)", r"<em>\1</em>", s)
    return s


def md_to_html(text):
    """Minimal markdown: headings, flat lists, paragraphs, inline styles.
    Anything unrecognized renders as an escaped paragraph — never raw HTML."""
    out, para, in_list = [], [], None  # in_list: None | "ul" | "ol"

    def close_para():
        if para:
            out.append("<p>" + md_inline(" ".join(para)) + "</p>")
            para.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            close_para()
            close_list()
            continue
        h = re.match(r"(#{1,6})\s+(.*)", stripped)
        ul = re.match(r"[-*]\s+(.*)", stripped)
        ol = re.match(r"\d+\.\s+(.*)", stripped)
        if h:
            close_para()
            close_list()
            level = min(len(h.group(1)) + 3, 6)  # page owns h1-h3
            out.append(f"<h{level}>{md_inline(h.group(2))}</h{level}>")
        elif ul or ol:
            close_para()
            tag = "ul" if ul else "ol"
            if in_list != tag:
                close_list()
                out.append(f"<{tag}>")
                in_list = tag
            out.append("<li>" + md_inline((ul or ol).group(1)) + "</li>")
        else:
            close_list()
            para.append(stripped)
    close_para()
    close_list()
    return "\n".join(out)


# ---------------------------------------------------------------------- SVG
# Palette: validated reference instance (dataviz skill), light mode only —
# the report is deliberately print/email-safe.
SERIES = "#2a78d6"        # categorical slot 1 (blue)
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"


def _ticks(lo, hi, n=4):
    if hi <= lo:
        pad = abs(lo) * 0.1 or 1.0
        lo, hi = lo - pad, hi + pad
    step = (hi - lo) / n
    return [lo + i * step for i in range(n + 1)], lo, hi


def svg_line_chart(points, *, bar=None, bar_label=None, title,
                   width=720, height=220, color=SERIES, x_label="cycle",
                   current_best=None, current_best_label=None):
    """One series, one axis. points: [(x:int, y:float)] with y != None."""
    pts = [(x, y) for x, y in points if y is not None]
    ml, mt, mb = 52, 18, 30
    LABEL_GAP = 16  # min vertical separation between reference labels
    label_ys = []
    references = []
    if current_best is not None:
        references.append({
            "value": current_best,
            "label": current_best_label or f"current best {fmt(current_best)}",
            "color": color,
            "dash": "2 3",
        })
    if bar is not None:
        target_label = bar_label or f"target {fmt(bar)}"
        if current_best is not None and bar == current_best:
            references[-1]["label"] = (
                f"{references[-1]['label']} / {target_label}"
            )
            references[-1]["dash"] = "5 4"
        else:
            references.append({
                "value": bar,
                "label": target_label,
                "color": MUTED,
                "dash": "5 4",
            })

    # right margin sized so the longest reference label never clips at the
    # SVG edge (labels start at ml + pw + 6; ~6.2 px per glyph at font 11)
    longest_label = max((len(r["label"]) for r in references), default=0)
    mr = max(96, int(longest_label * 6.2) + 24)
    pw, ph = width - ml - mr, height - mt - mb

    parts = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"'
             f' role="img" aria-label="{esc(title)}" '
             'font-family="system-ui,-apple-system,\'Segoe UI\',sans-serif">']
    if not pts:
        if references:
            spacing = min(28, height / (len(references) + 2))
            start_y = height / 2 - spacing * (len(references) - 1) / 2
            for i, ref in enumerate(references):
                ry = start_y + i * spacing
                parts.append(
                    f'<line x1="{ml}" y1="{ry:.1f}" x2="{ml + pw}" '
                    f'y2="{ry:.1f}" stroke="{ref["color"]}" stroke-width="1" '
                    f'stroke-dasharray="{ref["dash"]}"/>'
                )
                parts.append(
                    f'<text x="{ml + pw + 6}" y="{ry:.1f}" '
                    f'dominant-baseline="middle" fill="{ref["color"]}" '
                    f'font-size="11">{esc(ref["label"])}</text>'
                )
            message_y = min(height - 12, start_y + len(references) * spacing)
        else:
            message_y = height / 2
        parts.append(f'<text x="{width / 2}" y="{message_y:.1f}" text-anchor="middle" '
                     f'fill="{MUTED}" font-size="13">no scored '
                     f'{esc(x_label)}s yet</text></svg>')
        return "\n".join(parts)

    ys = [y for _, y in pts] + [ref["value"] for ref in references]
    ticks, ylo, yhi = _ticks(min(ys), max(ys))
    yspan = yhi - ylo
    ylo, yhi = ylo - 0.05 * yspan, yhi + 0.05 * yspan
    xs = [x for x, _ in pts]
    xlo, xhi = min(xs), max(xs)

    def X(x):
        return ml + (pw / 2 if xhi == xlo else (x - xlo) / (xhi - xlo) * pw)

    def Y(y):
        return mt + ph - (y - ylo) / (yhi - ylo) * ph

    for t in ticks:  # horizontal hairlines + y labels
        parts.append(f'<line x1="{ml}" y1="{Y(t):.1f}" x2="{ml + pw}" y2="{Y(t):.1f}" '
                     f'stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{ml - 8}" y="{Y(t):.1f}" text-anchor="end" '
                     f'dominant-baseline="middle" fill="{MUTED}" font-size="11" '
                     f'font-variant-numeric="tabular-nums">{fmt(t)}</text>')
    every = max(1, -(-(xhi - xlo + 1) // 12))
    for x in range(xlo, xhi + 1):
        if (x - xlo) % every == 0:
            parts.append(f'<text x="{X(x):.1f}" y="{height - mb + 16}" '
                         f'text-anchor="middle" fill="{MUTED}" font-size="11">{x}</text>')
    parts.append(f'<line x1="{ml}" y1="{mt + ph}" x2="{ml + pw}" y2="{mt + ph}" '
                 f'stroke="{AXIS}" stroke-width="1"/>')

    for ref in references:
        ry = Y(ref["value"])
        ly = ry
        # nudge labels apart so nearby reference lines' labels never collide
        for prev in label_ys:
            if abs(ly - prev) < LABEL_GAP:
                ly = prev - LABEL_GAP if ly < prev else prev + LABEL_GAP
        label_ys.append(ly)
        parts.append(f'<line x1="{ml}" y1="{ry:.1f}" x2="{ml + pw}" y2="{ry:.1f}" '
                     f'stroke="{ref["color"]}" stroke-width="1" '
                     f'stroke-dasharray="{ref["dash"]}"/>')
        parts.append(f'<text x="{ml + pw + 6}" y="{ly:.1f}" dominant-baseline="middle" '
                     f'fill="{ref["color"]}" font-size="11">'
                     f'{esc(ref["label"])}</text>')

    if len(pts) > 1:
        poly = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in pts)
        parts.append(f'<polyline points="{poly}" fill="none" stroke="{color}" '
                     'stroke-width="2" stroke-linejoin="round"/>')
    for x, y in pts:
        parts.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4" fill="{color}">'
                     f'<title>{esc(x_label)} {x}: {fmt(y)}</title></circle>')
    lx, ly = pts[-1]
    if X(lx) <= ml + pw - 40:
        # keep clear of the right-margin reference labels; the value stays
        # readable via the y-axis, tooltip, and the "current best"/"target"
        # labels when the last point is one of them
        label_x, label_y, label_txt = X(lx) + 9, Y(ly), fmt(ly)
        # halo first so reference lines crossing the last-point label stay legible
        parts.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" dominant-baseline="middle" '
                     f'stroke="#f9f9f7" stroke-width="3" paint-order="stroke" '
                     f'font-size="12" font-weight="600" '
                     f'font-variant-numeric="tabular-nums">{label_txt}</text>')
        parts.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" dominant-baseline="middle" '
                     f'fill="{INK}" font-size="12" font-weight="600" '
                     f'font-variant-numeric="tabular-nums">{label_txt}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


# ------------------------------------------------------------------- pieces

STATUS_CLASS = {"improved": "st-good", "no-change": "st-neutral",
                "failed": "st-critical", "timeout": "st-serious"}


def status_chip(status):
    return f'<span class="chip {STATUS_CLASS[status]}">{esc(status)}</span>'


def kind_badge(kind):
    return f'<span class="badge kind-{esc(kind)}">{esc(kind)}</span>'


def best_attempt(cycle):
    direction = cycle["primary_metric"]["direction"]
    scored = [a for a in cycle["attempts"] if a.get("primary") is not None]
    if not scored:
        return None
    pick = max if direction == "max" else min
    return pick(scored, key=lambda a: a["primary"])


def attempt_table(data):
    """Lineage-ordered: each chain's rows grouped together, descendants
    indented under their ancestor; prior-cycle ancestors as grey rows.
    One representation carries both the results and the parent structure."""
    best = best_attempt(data)
    best_id = best["id"] if best else None
    attempts = {a["id"]: a for a in data["attempts"]}
    guard_names = sorted({g for a in data["attempts"]
                          for g in (a.get("guards") or {})})
    ncols = 6 + len(guard_names)

    children = {}
    batch_roots, prior_groups = [], {}
    for a in data["attempts"]:
        p = a["parent"]
        if p is None:
            batch_roots.append(a["id"])
        elif p in attempts:
            children.setdefault(p, []).append(a["id"])
        else:
            prior_groups.setdefault(p, []).append(a["id"])  # earlier-cycle parent

    def subtree_min(aid):
        return min([aid] + [subtree_min(k) for k in children.get(aid, [])])

    # chains in rough chronological order: by the earliest attempt id in each
    groups = ([("batch", rid, subtree_min(rid)) for rid in batch_roots]
              + [("prior", pid, min(min(map(subtree_min, kids)), 10 ** 9))
                 for pid, kids in prior_groups.items()])
    groups.sort(key=lambda g: g[2])

    rows = []

    def emit(aid, depth):
        a = attempts[aid]
        cls = ' class="best"' if aid == best_id else ""
        indent = (f'<span style="padding-left:{depth * 16}px">└ </span>'
                  if depth else "")
        guards = a.get("guards") or {}
        guard_cells = "".join(f'<td class="num">{fmt(guards.get(g))}</td>'
                              for g in guard_names)
        rows.append(
            f"<tr{cls}><td class=\"idcell\">{indent}"
            f"<a href=\"../../{esc(a['log_path'])}\">{aid:03d}</a></td>"
            f"<td>{kind_badge(a['kind'])}</td>"
            f"<td class=\"hyp\">{esc(a['hypothesis'])}</td>"
            f"<td class=\"num\">{fmt(a['primary'])}</td>{guard_cells}"
            f"<td>{status_chip(a['status'])}</td>"
            f"<td class=\"hyp\">{esc(a.get('causal_note') or '')}</td></tr>")
        for k in sorted(children.get(aid, [])):
            emit(k, depth + 1)

    for kind, rid, _ in groups:
        if kind == "batch":
            emit(rid, 0)
        else:
            rows.append(f'<tr class="prior"><td class="idcell">{rid:03d}</td>'
                        f'<td colspan="{ncols - 1}">ancestor from an earlier '
                        f'cycle — this batch builds on it below</td></tr>')
            for k in sorted(prior_groups[rid]):
                emit(k, 1)

    head = ("<tr><th>id</th><th>kind</th><th>hypothesis</th>"
            f"<th class=\"num\">{esc(data['primary_metric']['name'])}</th>"
            + "".join(f'<th class="num">{esc(g)}</th>' for g in guard_names)
            + "<th>status</th><th>causal note</th></tr>")
    note = ("<p class=\"note\">Grouped by lineage: └ rows build on the attempt "
            "above; grey rows are earlier-cycle ancestors. Best row shaded. "
            "Attempt ids link to the worktree LOG.md (may dangle if pruned).</p>")
    return (f'<table class="attempts"><thead>{head}</thead>'
            f'<tbody>{"".join(rows)}</tbody></table>{note}')


def lessons_html(lessons):
    """Each lesson: observation headline, then the why-chain rows."""
    blocks = []
    for l in lessons:
        conf = l.get("confidence")
        tag = (f'<span class="conf conf-{esc(conf)}">{esc(conf)}</span>'
               if conf else "")
        blocks.append(f"""<div class="lesson">
<p class="lesson-obs">{md_inline(l["observation"])} {tag}</p>
<dl>
<dt>root cause</dt><dd>{md_inline(l["root_cause"])}</dd>
<dt>evidence</dt><dd>{md_inline(l["evidence"])}</dd>
<dt>implication</dt><dd>{md_inline(l["implication"])}</dd>
</dl>
</div>""")
    return f'<div class="lessons">{"".join(blocks)}</div>'


def highlight_box(title, items, cls):
    lis = "".join(f"<li>{md_inline(i)}</li>" for i in items)
    return f'<div class="box {cls}"><strong>{esc(title)}</strong><ul>{lis}</ul></div>'


# -------------------------------------------------------------------- pages

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; background: #f9f9f7; color: #0b0b0b;
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 960px; margin: 0 auto; padding: 24px 20px 48px; }
h1 { font-size: 20px; margin: 0 0 2px; }
h2 { font-size: 16px; margin: 28px 0 8px; border-bottom: 1px solid #e1e0d9;
  padding-bottom: 4px; }
h3 { font-size: 14px; margin: 18px 0 4px; color: #52514e; }
h4, h5, h6 { font-size: 14px; margin: 12px 0 4px; }
a { color: #1c5cab; }
.meta { color: #52514e; margin: 0 0 16px; }
.note { color: #898781; font-size: 12px; margin: 6px 0 0; }
.score-formula { margin: 0 0 8px; font-size: 12px; color: #52514e;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.card { background: #fcfcfb; border: 1px solid rgba(11,11,11,0.10);
  border-radius: 6px; padding: 14px 16px; margin: 12px 0; }
table { border-collapse: collapse; width: 100%; background: #fcfcfb; }
th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #e1e0d9;
  vertical-align: top; }
th { color: #52514e; font-size: 12px; font-weight: 600; white-space: nowrap; }
td.num, th.num { text-align: right;
  font-variant-numeric: tabular-nums; white-space: nowrap; }
td.hyp { max-width: 26em; }
tr.best td { background: #eef4fc; }
tr.prior td { color: #898781; background: #f5f5f2; font-size: 12px; }
td.idcell { white-space: nowrap; }
.scroll { overflow-x: auto; }
.chip { display: inline-block; padding: 1px 8px; border-radius: 9px;
  font-size: 12px; white-space: nowrap; }
.st-good { background: #e2f3e2; color: #0a5c0a; }
.st-neutral { background: #f0efec; color: #52514e; }
.st-critical { background: #fae3e3; color: #922929; }
.st-serious { background: #fdeae2; color: #8a4526; }
.badge { display: inline-block; padding: 1px 8px; border-radius: 3px;
  font-size: 12px; white-space: nowrap; }
.kind-draft { background: #e5eefb; color: #1c5cab; }
.kind-improve { background: #ddf2ea; color: #0b6647; }
.kind-debug { background: #faf0d8; color: #7a5600; }
.lesson { border-left: 3px solid #c3c2b7; background: #fcfcfb;
  padding: 8px 14px; margin: 10px 0; }
.lesson-obs { margin: 0 0 6px; font-weight: 600; }
.lesson dl { display: grid; grid-template-columns: 7em 1fr; gap: 2px 12px;
  margin: 0; }
.lesson dt { color: #898781; font-size: 12px; line-height: 1.7; }
.lesson dd { margin: 0; }
.conf { font-size: 11px; padding: 1px 7px; border-radius: 9px;
  vertical-align: 1px; }
.conf-confirmed { background: #e2f3e2; color: #0a5c0a; }
.conf-suspected { background: #f0efec; color: #52514e; }
.box { border-radius: 6px; padding: 10px 14px; margin: 10px 0; }
.box ul { margin: 6px 0 0; padding-left: 20px; }
.box-blacklist { background: #fae3e3; border: 1px solid #e8b9b9; }
.box-promote { background: #faf0d8; border: 1px solid #e3cf94; }
figure { margin: 0; }
figcaption { color: #52514e; font-size: 12px; margin-bottom: 2px; }
svg { max-width: 100%; height: auto; }
footer { margin-top: 32px; color: #52514e; display: flex; gap: 16px; }
footer .disabled { color: #c3c2b7; }
"""


def page(title, body):
    return (f"<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{esc(title)}</title>\n<style>{CSS}</style>\n</head>\n"
            f"<body>\n<main>\n{body}\n</main>\n</body>\n</html>\n")


def render_cycle(data, all_cycles):
    direction = data["primary_metric"]["direction"]
    metric = data["primary_metric"]["name"]
    attempt_scores = [(a["id"], a["primary"]) for a in data["attempts"]
                      if a.get("primary") is not None]
    current_best_attempt = best_attempt(data)
    current_best = (current_best_attempt["primary"]
                    if current_best_attempt else None)
    a_lo, a_hi = data["attempts_range"]
    nn = data["cycle"]

    known = {c["cycle"] for c in all_cycles}
    prev_nn, next_nn = nn - 1, nn + 1
    prev_link = (f'<a href="cycle-{prev_nn:02d}.html">← cycle {prev_nn:02d}</a>'
                 if prev_nn in known else
                 f'<span class="disabled">← cycle {prev_nn:02d}</span>')
    next_link = (f'<a href="cycle-{next_nn:02d}.html">cycle {next_nn:02d} →</a>'
                 if next_nn in known else
                 f'<span class="disabled">cycle {next_nn:02d} →</span>')

    refl = data["reflection"]
    evidence_extra = (highlight_box("New blacklist entries this cycle",
                                    data["blacklist_new"], "box-blacklist")
                      if data["blacklist_new"] else "")
    decision_extra = (highlight_box("Insight promotions — awaiting user "
                                    "confirmation at the gate",
                                    data["insight_promotions"], "box-promote")
                      if data["insight_promotions"] else "")
    holdout_extra = (f'<p class="note"><strong>Holdout:</strong> '
                     f'{esc(data["holdout"]["result"])}</p>'
                     if data["holdout"]["spent"] else "")
    score_formula = data.get("score_formula")
    formula_html = (f'<p class="score-formula">{md_inline(score_formula)}</p>'
                    if score_formula else "")

    direction_word = 'higher' if direction == 'max' else 'lower'

    body = f"""<h1>{esc(data["project"])} — cycle {nn:02d}</h1>
<p class="meta">attempts {a_lo:03d}–{a_hi:03d} · {esc(fmt_date(data["date_utc"]))}</p>
<h2>Review — what we did</h2>
<div class="card">
{formula_html}
<figure><figcaption>{esc(metric)} — {direction_word} is better</figcaption>
{svg_line_chart(attempt_scores, bar=data["bar"]["value"],
                bar_label=(f'target {fmt(data["bar"]["value"])}'
                           if data["bar"]["value"] is not None else None),
                title=f"{metric} by attempt", x_label="attempt",
                current_best=current_best,
                current_best_label=f'current best {fmt(current_best)}')}
</figure>
</div>
<div class="scroll">{attempt_table(data)}</div>
{holdout_extra}
{md_to_html(refl["review"])}
<h2>Lessons we learnt</h2>
{lessons_html(data["lessons"])}
<h3>Evidence carried forward</h3>
{md_to_html(refl["evidence"])}{evidence_extra}
<h3>Literature check</h3>{md_to_html(refl["literature"])}
<h2>TODO — worth checking</h2>{md_to_html(refl["todo"])}
<h2>Next round</h2>{md_to_html(refl["next"])}{decision_extra}
<footer>{prev_link}<a href="index.html">index</a>{next_link}</footer>"""
    return page(f"{data['project']} — cycle {nn:02d}", body)


def render_index(all_cycles, campaign_href=None):
    cycles = sorted(all_cycles, key=lambda c: c["cycle"])
    latest = cycles[-1]
    direction = latest["primary_metric"]["direction"]
    metric = latest["primary_metric"]["name"]
    # Only cycles scored under the latest concrete definition share an axis;
    # older cycles used different metrics/references and must not shape the
    # best-so-far trajectory or the headline "best" number. The metric name
    # (not the formula — that is mathematically identical across eras) is the
    # reliable discriminator here.
    axis = ([c for c in cycles
             if c.get("primary_metric", {}).get("name") == metric]
            if metric else cycles)
    series = best_so_far(axis, direction)
    overall_best = series[-1][1] if series else None
    total_attempts = sum(len(c["attempts"]) for c in cycles)
    total_blacklist = sum(len(c["blacklist_new"]) for c in cycles)
    bar = latest["bar"]["value"]
    target_meta = f" vs target {fmt(bar)}" if bar is not None else ""

    rows = []
    for c in cycles:
        n = c["cycle"]
        k = sum(1 for a in c["attempts"] if a["status"] == "improved")
        lo, hi = c["attempts_range"]
        rows.append(
            f'<tr><td><a href="cycle-{n:02d}.html">cycle {n:02d}</a></td>'
            f'<td>{esc(c["date_utc"][:10])}</td>'
            f'<td class="num">{lo:03d}–{hi:03d}</td>'
            f'<td class="num">{k}/{len(c["attempts"])}</td>'
            f'<td class="num">{fmt(c["best_this_cycle"])}</td>'
            f'<td class="hyp">{esc(first_sentence(c["reflection"]["next"]))}</td></tr>')

    campaign_link = (f'<footer><a href="{esc(campaign_href)}">'
                     'full campaign overview</a></footer>'
                     if campaign_href else "")
    body = f"""<h1>{esc(latest["project"])} — autoresearch cycles</h1>
<p class="meta">{len(cycles)} cycles · {total_attempts} attempts ·
{total_blacklist} blacklisted approaches · best {esc(metric)}
{fmt(overall_best)}{target_meta}</p>
<div class="card">
<figure><figcaption>best-so-far {esc(metric)} —
{'higher' if direction == 'max' else 'lower'} is better</figcaption>
{svg_line_chart(series, bar=bar,
                bar_label=f'target {fmt(bar)}' if bar is not None else None,
                title=f"best-so-far {metric} by cycle")}
</figure>
</div>
<div class="scroll">
<table><thead><tr><th>cycle</th><th>date</th><th class="num">attempts</th>
<th class="num">yield</th><th class="num">best</th>
<th>next</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
</div>
{campaign_link}"""
    return page(f"{latest['project']} — autoresearch cycles", body)


# --------------------------------------------------------------------- main

def load_cycles(directory, target_nn):
    """Load every cycle-*.json; the target must validate, siblings may be
    skipped with a warning (pre-adoption or broken cycles must not block)."""
    target = None
    others = []
    for path in sorted(directory.glob("cycle-*.json")):
        m = re.fullmatch(r"cycle-(\d+)\.json", path.name)
        if not m:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            errors = validate_cycle(data)
        except (json.JSONDecodeError, OSError) as e:
            data, errors = None, [str(e)]
        if int(m.group(1)) == target_nn:
            if errors:
                for e in errors:
                    print(f"report.py: {path.name}: {e}", file=sys.stderr)
                sys.exit(1)
            target = data
        elif errors:
            print(f"report.py: warning: skipping {path.name}: {errors[0]}",
                  file=sys.stderr)
        else:
            others.append(data)
    if target is None:
        print(f"report.py: cycle-{target_nn:02d}.json not found in {directory}",
              file=sys.stderr)
        sys.exit(1)
    return target, others + [target]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cycle", type=int, required=True, help="cycle number NN")
    ap.add_argument("--dir", required=True,
                    help="directory holding cycle-*.json (docs/discussion/)")
    args = ap.parse_args(argv)
    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"report.py: no such directory: {directory}", file=sys.stderr)
        sys.exit(1)

    target, all_cycles = load_cycles(directory, args.cycle)
    cycle_path = directory / f"cycle-{args.cycle:02d}.html"
    cycle_path.write_text(render_cycle(target, all_cycles), encoding="utf-8")
    index_path = directory / "index.html"
    campaign_href = "campaign.html" if (directory / "campaign.html").is_file() else None
    index_path.write_text(render_index(all_cycles, campaign_href=campaign_href),
                          encoding="utf-8")
    print(f"wrote {cycle_path}\nwrote {index_path}")


if __name__ == "__main__":
    main()
