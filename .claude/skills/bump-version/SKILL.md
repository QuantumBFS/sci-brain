---
name: bump-version
description: Use when the user asks to tag, release, or bump the version of the sci-brain plugin (e.g. "tag a version", "cut a release", "bump to 0.3.0", "release v0.x"). Handles the three-manifest version sync, commit, annotated tag, push, and GitHub release.
---

# Bump Version

## Overview

sci-brain is a Claude Code plugin. Its version is declared in **three** JSON files that must stay in lockstep — the marketplace reads it from `marketplace.json`, plugin tooling reads it from `plugin.json`, and npm/pi read it from `package.json`. CI (`scripts/validate_skills.py`) fails if they diverge, and `.github/workflows/publish.yml` refuses to publish unless the pushed tag equals `v` + `package.json`'s version. A release is: bump all three files → commit → annotated tag → push → GitHub release.

## Version Source of Truth

| File | Path to version |
|---|---|
| `.claude-plugin/plugin.json` | `.version` |
| `.claude-plugin/marketplace.json` | `.plugins[0].version` |
| `package.json` | `.version` |

All three MUST match. If they diverge, CI's version-sync check fails, the npm publish tag gate rejects the release, and the marketplace and the installed plugin report different versions.

## When to Use

- "tag a version", "bump version", "cut a release", "release v0.x"
- After a batch of merged PRs that warrants a new release
- Before announcing changes that downstream users need to pull

Do NOT use for:
- Pre-release / draft tags (the workflow below assumes a real release)
- Hotfix to an old branch — this skill assumes you tag from `main`

## Bump Type → New Version

Read current version from `.claude-plugin/plugin.json`, then:

- **patch** (`X.Y.Z` → `X.Y.Z+1`): bugfix, doc tweak, no behavior change
- **minor** (`X.Y.Z` → `X.Y+1.0`): new skill, new feature, additive change
- **major** (`X.Y.Z` → `X+1.0.0`): breaking change to a skill's contract / removed skill

If the user didn't specify, ask which bump type (patch/minor/major) before continuing.

## Procedure

1. **Read current version** from `.claude-plugin/plugin.json` and confirm `marketplace.json` and `package.json` match. If they already disagree, stop and flag it — don't paper over the drift.

2. **Edit all three files** to the new version. Use the `Edit` tool, not `sed`, so the diff is reviewable.

3. **Commit + tag locally** (one shell call):
   ```bash
   python3 scripts/validate_skills.py
   git add .claude-plugin/plugin.json .claude-plugin/marketplace.json package.json
   git commit -m "chore: bump version to X.Y.Z"
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   ```
   - `validate_skills.py` is the same sync check CI runs; it must pass before committing.
   - Annotated tag (`-a`), not lightweight. The annotation is what `gh release` and changelog tools read.
   - Tag is `vX.Y.Z` (with `v` prefix). Version field in JSON is `X.Y.Z` (no `v`).

4. **Push** — tag first, then main:
   ```bash
   git push origin vX.Y.Z
   git push origin main
   ```
   - Pushing the tag without main is fine — the tag ref carries the commit. The push of `main` may be denied by the harness's auto-mode classifier (pushing to a default branch bypasses PR review). If it is, tell the user to run `! git push origin main` themselves rather than retrying.

5. **Create GitHub release**:
   ```bash
   gh release create vX.Y.Z --generate-notes --title "vX.Y.Z" --repo QuantumBFS/sci-brain
   ```
   - `--generate-notes` builds release notes from merged PRs since the previous tag.
   - Repo flag is explicit because the local remote may still point at the old `sci-brainstorm` name (the repo was renamed; pushes get a redirect notice but succeed).

6. **Report** the release URL back to the user.

## Common Pitfalls

| Pitfall | Why it bites | Fix |
|---|---|---|
| Edited only `plugin.json` | Marketplace will still show old version to new installs | Always edit all three files in the same commit |
| Skipped `package.json` | CI sync check fails and `publish.yml` rejects the tag, so nothing is published to npm | Bump `package.json` too; run `scripts/validate_skills.py` before committing |
| Lightweight tag (`git tag vX.Y.Z`) | `gh release --generate-notes` and some tools miss the annotation | Use `git tag -a vX.Y.Z -m "..."` |
| Tag prefix mismatch (`0.2.0` vs `v0.2.0`) | Inconsistent with existing tags, breaks tooling that filters `v*` | JSON = `0.2.0`, git tag = `v0.2.0` |
| Pushed tag without bumping JSON first | Released artifact reports stale version | Bump → commit → tag, in that order |
| Created tag on a dirty tree | Tag points at uncommitted state | `git status` clean before tagging |
| Tried to re-push after main push was blocked | Auto-mode classifier won't reverse itself | Hand off to user with `! git push origin main` |

## Quick Reference

```bash
# Inspect
grep -H '"version"' .claude-plugin/plugin.json .claude-plugin/marketplace.json package.json
git tag --sort=-creatordate | head -5

# Release (after editing all three JSON files to NEW_VERSION)
python3 scripts/validate_skills.py
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json package.json
git commit -m "chore: bump version to NEW_VERSION"
git tag -a vNEW_VERSION -m "Release vNEW_VERSION"
git push origin vNEW_VERSION
git push origin main   # may need user to run manually
gh release create vNEW_VERSION --generate-notes --title "vNEW_VERSION" --repo QuantumBFS/sci-brain
```
