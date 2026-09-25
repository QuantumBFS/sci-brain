#!/usr/bin/env python3
"""Tidy up autoresearch attempt worktrees so a campaign can pause and resume.

Usage:
    python3 tidy_attempts.py inventory [--project DIR] [--json inv.json]
    python3 tidy_attempts.py apply --from inv.json [--project DIR] [--drop 003,007] [--keep 012]
    python3 tidy_attempts.py record --from inv.json [--project DIR] [--out research/ATTEMPTS.md]

`inventory` is read-only. It lists every `attempt-NNN` worktree/branch with
its LOG.md hypothesis, validator outcome, uncommitted work, build artifacts,
and push state, and decides per attempt:

    keep  anything with a LOG.md, a report.json, or code changes
    drop  an empty worktree: no log, no report, no commits, no changes
    ask   changes but no LOG.md, or large untracked files that match no
          build-artifact pattern -- the user decides these at the end

`apply` executes the decisions from a saved inventory: kept worktrees get
their artifacts ignored, everything else committed to their own attempt
branch, pushed when a remote exists, and the worktree directory removed
(the branch is the record; `git worktree add .worktrees/attempt-NNN
attempt-NNN` restores it). Dropped worktrees and branches are deleted.
`ask` rows are left untouched unless named in --drop or --keep. A second
`apply` on the same snapshot is safe: rows already handled are skipped.

`record` writes research/ATTEMPTS.md: one row per attempt in the snapshot,
with the disposition observed now (pushed / local only / dropped).
"""

import argparse
import datetime as dt
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

ARTIFACT_DIRS = ["__pycache__", "build", "dist", "target", "node_modules",
                 ".venv", "venv", ".pytest_cache", ".mypy_cache", ".ruff_cache"]
ARTIFACT_GLOBS = ["*.pyc", "*.pyo", "*.egg-info", "*.o", "*.so", "*.a",
                  "*.dylib", "*.class", "*.jar"]
LARGE_BYTES = 10 * 1024 * 1024
BRANCH_RE = re.compile(r"attempt-(\d{3,})$")
LOG_FIELD_RE = re.compile(r"^\W*(kind|parent|hypothesis)\W+(.+?)\s*$", re.I | re.M)


def git(cwd, *args, check=True):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)} in {cwd}: {r.stderr.strip()}")
    return r.stdout


def artifact_pattern(path):
    parts = Path(path).parts
    for d in ARTIFACT_DIRS:
        if d in parts[:-1] or (parts[-1] == d):
            return d + "/"
    for g in ARTIFACT_GLOBS:
        if any(fnmatch.fnmatch(p, g) for p in parts):
            return g
    return None


def read_file(worktree, branch, name, project):
    if worktree and (Path(worktree) / name).is_file():
        return (Path(worktree) / name).read_text(errors="replace")
    if branch:
        r = subprocess.run(["git", "-C", str(project), "show", f"{branch}:{name}"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
    return None


def parse_log(text):
    fields = {"kind": "", "parent": "", "hypothesis": ""}
    for key, value in LOG_FIELD_RE.findall(text or ""):
        key = key.lower()
        if not fields[key]:
            fields[key] = value.strip("*_ ")
    return fields


def parse_report(text):
    try:
        d = json.loads(text)
    except (TypeError, ValueError):
        return None, None
    return d.get("status"), d.get("score")


def inventory(project):
    project = Path(project).resolve()
    remotes = git(project, "remote").split()
    remote = "origin" if "origin" in remotes else (remotes[0] if remotes else None)
    branches = {b for b in git(project, "for-each-ref", "--format=%(refname:short)",
                               "refs/heads/attempt-*").split() if BRANCH_RE.search(b)}
    worktrees = {}
    cur = {}
    for line in git(project, "worktree", "list", "--porcelain").splitlines() + [""]:
        if line.startswith("worktree "):
            cur = {"path": line[9:]}
        elif line.startswith("branch "):
            cur["branch"] = line[7:].replace("refs/heads/", "")
        elif not line and cur:
            name = cur.get("branch") or Path(cur["path"]).name
            if BRANCH_RE.search(name):
                worktrees[name] = cur["path"]
            cur = {}
    head = git(project, "rev-parse", "HEAD").strip()
    attempts = []
    for name in sorted(branches | set(worktrees), key=lambda n: int(BRANCH_RE.search(n).group(1))):
        wt = worktrees.get(name)
        has_branch = name in branches
        log = read_file(wt, name if has_branch else None, "LOG.md", project)
        status, score = parse_report(read_file(wt, name if has_branch else None,
                                               "report.json", project))
        dirty, untracked, artifacts, large = 0, [], set(), []
        if wt:
            for line in git(wt, "status", "--porcelain", "--untracked-files=all").splitlines():
                path = line[3:]
                if line.startswith("??"):
                    pat = artifact_pattern(path)
                    if pat:
                        artifacts.add(pat)
                    else:
                        untracked.append(path)
                        if (Path(wt) / path).stat().st_size >= LARGE_BYTES:
                            large.append(path)
                else:
                    dirty += 1
        own_commits = int(git(project, "rev-list", "--count", f"{head}..{name}").strip()) \
            if has_branch else 0
        pushed = False
        if remote and has_branch:
            r = subprocess.run(["git", "-C", str(project), "rev-parse", f"{remote}/{name}"],
                               capture_output=True, text=True)
            pushed = r.returncode == 0 and r.stdout.strip() == git(project, "rev-parse", name).strip()
        has_work = bool(dirty or untracked or own_commits)
        if not wt:
            decision, reason = "keep", "branch only, no worktree"
        elif log is None and status is None and not has_work:
            decision, reason = "drop", "empty worktree"
        elif log is None and (has_work or status is not None):
            decision, reason = "ask", "no LOG.md but has changes"
        elif large:
            decision, reason = "ask", "large untracked file(s): " + ", ".join(large)
        else:
            decision, reason = "keep", "has record"
        attempts.append({
            "id": int(BRANCH_RE.search(name).group(1)), "name": name,
            "branch": has_branch, "worktree": wt, "log": log is not None,
            **parse_log(log), "status": status or ("unscored" if log else None),
            "score": score, "dirty": dirty, "untracked": untracked,
            "artifacts": sorted(artifacts), "large": large,
            "own_commits": own_commits, "pushed": pushed,
            "decision": decision, "reason": reason,
        })
    return {"project": str(project), "remote": remote, "date": dt.date.today().isoformat(),
            "attempts": attempts}


def apply(project, inv, drop=frozenset(), keep=frozenset()):
    project = Path(project).resolve()
    remote = inv.get("remote")
    result = {"kept": [], "dropped": [], "skipped": [], "warnings": []}
    for a in inv["attempts"]:
        name, wt = a["name"], a["worktree"]
        branch_exists = subprocess.run(["git", "-C", str(project), "rev-parse", "--verify",
                                        "-q", "refs/heads/" + name], capture_output=True).returncode == 0
        if a["id"] in drop or a["decision"] == "drop":
            if wt and Path(wt).exists():
                git(project, "worktree", "remove", "--force", wt)
            if branch_exists:
                git(project, "branch", "-D", name)
            result["dropped"].append(a["id"])
            continue
        if a["decision"] == "ask" and a["id"] not in keep:
            result["skipped"].append(a["id"])
            continue
        if not branch_exists and not (wt and Path(wt).exists()):
            continue  # already dropped in an earlier pass
        if wt and Path(wt).exists():
            if a["artifacts"]:
                gi = Path(wt) / ".gitignore"
                have = gi.read_text().splitlines() if gi.exists() else []
                new = [p for p in a["artifacts"] if p not in have]
                if new:
                    gi.write_text("\n".join(have + new) + "\n")
            git(wt, "add", "-A")
            if subprocess.run(["git", "-C", wt, "diff", "--cached", "--quiet"]).returncode:
                git(wt, "commit", "-q", "-m", f"{name}: tidy-up")
        if remote:
            r = subprocess.run(["git", "-C", str(project), "push", "-q", remote, name],
                               capture_output=True, text=True)
            if r.returncode:
                result["warnings"].append(f"{name}: push failed: {r.stderr.strip()}")
        if wt and Path(wt).exists():
            git(project, "worktree", "remove", "--force", wt)
        result["kept"].append(a["id"])
    git(project, "worktree", "prune")
    return result


def record(project, inv, out=None):
    project = Path(project).resolve()
    live_inv = inventory(project)
    live = {a["id"]: a for a in live_inv["attempts"]}
    remote = live_inv["remote"]
    state = project / "research" / "STATE.md"
    state_lines = [l for l in state.read_text().splitlines()
                   if re.match(r"- (stage|topic|authorized_attempts|next_attempt|next_cycle):", l)] \
        if state.exists() else []
    lines = [f"# Attempts", "",
             f"Tidied {dt.date.today().isoformat()}. Regenerated by "
             f"`helpers/tidy_attempts.py record`; edit the notes column freely.", ""]
    lines += state_lines + [""]
    if not remote:
        lines += ["**No remote is configured: every kept branch is local only.** "
                  "Local commits are not a backup. Add a remote and push the "
                  "`attempt-*` branches, or copy `git bundle --all` off this machine.", ""]
    lines += ["| id | kind | parent | status | score | branch | disposition | hypothesis |",
              "|---|---|---|---|---|---|---|---|"]
    for a in inv["attempts"]:
        cur = live.get(a["id"])
        if cur is None:
            disp, branch = "dropped", "—"
        else:
            disp = "pushed" if cur["pushed"] else "local only"
            branch = f"`{a['name']}`"
        score = "—" if a["score"] is None else f"{a['score']:g}"
        lines.append(f"| {a['id']:03d} | {a['kind'] or '—'} | {a['parent'] or '—'} | "
                     f"{a['status'] or '—'} | {score} | {branch} | {disp} | "
                     f"{a['hypothesis'] or '—'} |")
    lines += ["", "## Resume", "",
              "- Restore any kept attempt with `git worktree add .worktrees/attempt-NNN attempt-NNN`; "
              "its `LOG.md` and `report.json` are on the branch.",
              "- Dropped rows keep only this summary; their code is gone.",
              "- Continue from the `autoresearch` soft gate: pick a direction from the last "
              "`docs/discussion/cycle-NN.md` and authorize attempts in `research/STATE.md`.", ""]
    text = "\n".join(lines)
    if out:
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["inventory", "apply", "record"])
    ap.add_argument("--project", default=".")
    ap.add_argument("--json", help="inventory: write the full snapshot here")
    ap.add_argument("--from", dest="snapshot", help="apply/record: snapshot from inventory --json")
    ap.add_argument("--drop", default="", help="apply: comma-separated attempt ids to drop")
    ap.add_argument("--keep", default="", help="apply: comma-separated ask-row ids to keep")
    ap.add_argument("--out", default="research/ATTEMPTS.md", help="record: output path")
    args = ap.parse_args(argv)
    project = Path(args.project).resolve()
    if args.command == "inventory":
        inv = inventory(project)
        if args.json:
            Path(args.json).write_text(json.dumps(inv, indent=1))
        counts = {d: [a for a in inv["attempts"] if a["decision"] == d]
                  for d in ("keep", "drop", "ask")}
        print(f"remote: {inv['remote'] or 'none'}; " + "; ".join(
            f"{d}: {len(v)}" for d, v in counts.items()))
        if counts["drop"]:
            print("drop (empty): " + ", ".join(a["name"] for a in counts["drop"]))
        for a in counts["ask"]:
            print(f"ask  {a['name']}: {a['reason']}; {a['dirty']} modified, "
                  f"{len(a['untracked'])} untracked, {a['own_commits']} commits")
        if args.json:
            print(f"snapshot: {args.json}")
        return 0
    if not args.snapshot:
        ap.error("--from is required")
    inv = json.loads(Path(args.snapshot).read_text())
    if args.command == "apply":
        drop = {int(x) for x in args.drop.split(",") if x.strip()}
        keep = {int(x) for x in args.keep.split(",") if x.strip()}
        r = apply(project, inv, drop, keep)
        print(f"kept: {len(r['kept'])}; dropped: {len(r['dropped'])}; "
              f"left for decision: {len(r['skipped'])}")
        for w in r["warnings"]:
            print("warning:", w, file=sys.stderr)
        return 1 if r["warnings"] else 0
    record(project, inv, out=project / args.out)
    print(f"wrote {project / args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
