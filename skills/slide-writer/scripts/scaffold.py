#!/usr/bin/env python3
"""slide-writer scaffold — boot a self-contained Typst/Touying deck.

Copies the skill's `zoo/` directory next to a starter `<name>.typ` in the target
directory, so the resulting deck is portable (no dependency on the skill install
path). The starter deck imports `zoo/lib.typ`, binds gadgets/layouts to the
chosen theme, and ships one example slide per major pattern.

Usage:
    python3 scaffold.py [target_dir] [--name presentation] [--theme academic]

Idempotent: refuses to overwrite an existing `<name>.typ` unless --force.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ZOO_DIR = Path(__file__).resolve().parent.parent / "zoo"

DECK_TEMPLATE = """\
// {name} — scaffolded by slide-writer
// Self-contained: the zoo/ directory beside this file holds every theme,
// layout, and gadget. Recompile with:  typst compile {name}.typ

#import "zoo/lib.typ": *

#let pal = palettes.{theme}
#show: themes.{theme}.with(config-info(
  title: [{name}], subtitle: [a one-line subtitle],
  author: [Your Name], date: datetime.today(), institution: [Your affiliation],
))

#let (rail_pull, callout, codebox, quote_pull, figbox, portrait, clip_image,
      stat, stat_row, spec_list, theorem, definition, lemma, example, proof_box,
      badge, tag, time_badge, data_table, conclusion_grid, key_links, pacing,
      kicker, progress_dots) = gadgets(pal)
#let (spread, twocol, threecol, hero, band, cards, card, punch,
      centered_figure) = layouts(pal)

#title-slide()

== Outline
#outline()

= The problem
== The system breaks in three _places_
#spread(
  figbox([Fig 1 · Overview],
    rect(width: 100%, height: 130pt, fill: pal.paper_bg, stroke: pal.hairline)[your figure],
    caption: [how to read it]),
  [One-sentence lead. #rail_pull[The key insight in one line.]],
)

= Evidence
== Time inputs _collapse_
#stat_row((value: [*13*], label: [weeks]), (value: [*56%*], label: [daily]), (value: [*3*], label: [parts]))
#v(10pt)
#data_table(
  ("Metric", "Before", "After"),
  ("Latency", "340 ms", "52 ms"),
  ("Error rate", "12%", "1.3%"),
  highlight: (0,),
)

== A theorem and a proof
#theorem(title: [Main result], [Let $H = sum_i X_i$. Then the gap closes.])
#proof_box([The argument follows by expanding the sum. #h(8pt)$square$])

= Conclusion
== Copy the pattern, replace the _topic_
#conclusion_grid(
  (label: "Approach", title: [The method], body: [one sentence.]),
  (label: "Result",   title: [The outcome], body: [one sentence.]),
  (label: "Impact",   title: [Why it matters], body: [one sentence.]),
  (label: "Next",     title: [project URL], body: [the call to action.]),
)
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target_dir", nargs="?", default=".", help="deck directory")
    ap.add_argument("--name", default="presentation", help="deck file basename")
    ap.add_argument(
        "--theme",
        default="academic",
        choices=["academic", "dark", "minimal", "vibrant", "brand"],
        help="color theme to bind",
    )
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    if not ZOO_DIR.is_dir():
        print(f"error: zoo not found at {ZOO_DIR}", file=sys.stderr)
        return 1

    target = Path(args.target_dir).resolve()
    target.mkdir(parents=True, exist_ok=True)

    deck_path = target / f"{args.name}.typ"
    if deck_path.exists() and not args.force:
        print(f"error: {deck_path} exists (pass --force to overwrite)", file=sys.stderr)
        return 1

    zoo_dst = target / "zoo"
    if zoo_dst.exists():
        if not args.force:
            print(f"note: {zoo_dst} exists, leaving it (pass --force to refresh)")
        else:
            shutil.rmtree(zoo_dst)
            shutil.copytree(ZOO_DIR, zoo_dst)
            print(f"refreshed {zoo_dst}")
    else:
        shutil.copytree(ZOO_DIR, zoo_dst)
        print(f"copied zoo/ -> {zoo_dst}")

    deck_path.write_text(
        DECK_TEMPLATE.format(name=args.name, theme=args.theme), encoding="utf-8"
    )
    print(f"wrote {deck_path}")
    print(f"\nnext:  cd {target}  &&  typst compile {args.name}.typ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
