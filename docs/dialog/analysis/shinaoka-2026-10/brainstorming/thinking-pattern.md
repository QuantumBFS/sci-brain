# Thinking Patterns — brainstorming

- **Source:** Claude Code session history, 2026-07-14 – 2026-10-14 (JST)
- **Contributor:** Hiroshi Shinaoka
- **Topic:** brainstorming (library/architecture design, research-idea generation, strategy and community building)
- **Sessions analyzed:** 14 (278 tagged user turns)
- **Patterns found:** 12 (covering 244 / 278 turns, 88%)

Method: each turn was assigned to the pattern centroid with which it shares at least 3 of the 4 discriminating dimensions (`bloom`, depth level, `discourse`, `mechanism`); ties go to the earlier-listed pattern. Only patterns present in 2+ sessions are kept. Session IDs are abbreviated to the first 8 characters of the JSON file name.

Sessions: `05b6bc31` tprims-rs redesign / rayon overhead · `1c150a51` sparse-ir + MiniPole integrated package · `35a8fc0e` naming a distributed-rayon crate · `4b3736b6` LJ/atomic-cluster sampling (BP, NCMC, MACE distillation) · `5053584a` ghost-based correlation functional proposal · `5269dfd9` multi-chart QTT proposal · `5ecae483` einsum/AD extraction from tprims · `7dc4cac2` koushi-matrix issue scoping · `9ddb9c70` matrix-desktop multi-account design · `a88c8fde` Rust scientific-computing company · `bab3c6db` cluster-expansion surrogate for LJ · `c1906c00` Rust SciML / tenferro-rs strategy · `c1f12ad9` LJ38 surrogate + MCMC · `e6632dfb` EPW/RESPACK replacement built on IR/DLR/MiniPole.

---

## A. Idea generation and reframing

### Pattern: Propose an unprompted alternative mechanism in reply to the assistant's analysis
**Trigger:** The assistant lays out options, a feasibility analysis, or a limitation (e.g. "BP needs a fixed discrete graph", "this estimator dies on oscillating functions").
**Reaction:** Instead of choosing among the options, the user offers a new mechanism from a neighbouring field (ML quantisation, Potts mapping, distillation, QTT compression, field-theory channels) phrased as a tentative question ("〜はどうか？", "〜では？").
**Tag profile:** `bloom:create` `depth:deep/judgmental|enablement` `discourse:referential` `mechanism:exploration`
**Frequency:** 33 occurrences across 10 sessions
**Examples:**
- `5269dfd9#5` 「もしくは回路全体を連続量に拡張するかですね．つまり，NNの学習→量子化によるデータ削減，という最近のMLの流れに乗せる．」 — shifted the multi-chart QTT optimisation from discrete search to continuous relaxation.
- `4b3736b6#17` 「MACEって任意の原子種に対して作られているじゃない？…Siクラスターで計算しているときは，蒸留できませんか？」 — opened the teacher/student distillation plus delayed-acceptance MCMC line.
- `c1f12ad9#8` 「セルを切って占有数表示にしてしまうとか？そうすれば，連続系でもBP使えるが」 — countered "BP cannot apply to off-lattice systems" with a discretisation trick.

### Pattern: Open with a loosely framed agenda and let the design emerge
**Trigger:** Session start, or a pause where the user feels the direction is stale.
**Reaction:** States an intent or a hunch ("〜を作れないかなー", "考え直しています") with several bundled sub-ideas and no single question, inviting the assistant to structure it; later in a session, an explicit "全然違う発想をしてみないか" pivot.
**Tag profile:** `bloom:create` `depth:deep/instrumental` `discourse:indirect-request` `mechanism:exploration`
**Frequency:** 19 occurrences across 10 sessions
**Examples:**
- `a88c8fde#1` 「tenferro-rsを中心に, Rust scientific computingを中心に会社を作れないかなーと思ってます」 — started a business-model exploration that the user then constrained turn by turn.
- `4b3736b6#16` 「なんかさ，ぜんぜん違う発想をしてみないか．例えばスナップショットから別のスナップショップを提案するとか」 — broke out of a stuck NCMC discussion into replica-crossover moves.
- `e6632dfb#4` 「理想的には，QE，VASP，abinit, OpenMX等に全対応する後処理コードにするのが良い」 — generalised an EPW complaint into a code-agnostic post-processing project.

## B. Critical evaluation and premise checking

### Pattern: Reject or redirect when the assistant's framing carries a wrong premise
**Trigger:** The assistant's recommendation rests on an assumption the user does not share (anchoring on a word, wrong target, wrong scope, outdated facts).
**Reaction:** Short corrective — 「いや，…」「〜に引きずられていないか？」「以前の議論を引きずるな」 — that names the premise and forces a re-plan.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:referential` `mechanism:conversation-control`
**Frequency:** 22 occurrences across 11 sessions
**Examples:**
- `35a8fc0e#2` 「rankに引きづられていないか？」 — the assistant admitted the anchoring and regenerated rank-free names.
- `c1f12ad9#5` 「いやいや，LJ38が最終目的ではないので．問題は機械学習ポテンシャルやDFTがまだ重いときです」 — re-targeted the surrogate discussion to expensive potentials.
- `c1906c00#39` 「いや，tenferro-rsは既にフォーク版を使っているぜ 1次ソース取得が甘いのでは」 — corrected a factual error and demanded primary-source checking.

### Pattern: Inject first-hand domain knowledge to qualify a claim
**Trigger:** The assistant cites a paper, a method, or a general principle without the nuance the user knows from experience.
**Reaction:** A declarative remark that limits or contextualises the claim (where a paper actually worked, why a method is meaningful, what the user already has).
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:referential` `mechanism:common-ground`
**Frequency:** 14 occurrences across 6 sessions
**Examples:**
- `4b3736b6#7` 「これ，2Dイジングをやっているけど，高温だったんだよ」 — downgraded the relevance of a cited prior-art paper.
- `4b3736b6#26` 「HSは，一体問題が厳密に解けるからこそ意味がある」 — qualified his own hidden-variable idea with the condition that makes HS useful.
- `c1906c00#8` 「JSPS 二国間交流事業は，FWF＝JSPSで既に持っているからね．」 — removed an already-held programme from the funding plan.

### Pattern: Assert a scaling or design verdict and seek agreement
**Trigger:** A measurement, derivation, or draft that leaves a design choice open.
**Reaction:** States a conclusion with a quick quantitative justification and ends with 「〜では？」「〜だね」, expecting confirmation or pushback.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:confirmation-check` `mechanism:common-ground`
**Frequency:** 18 occurrences across 9 sessions
**Examples:**
- `05b6bc31#19` 「正直，10micro secぐらいのオーバーヘッドはいいのでは？N = 100のmatvecは1micro secぐらいだけど，その場合はseqでいいわけだし．」 — simplified the thread-pool design to "accept 10 µs, run small ops sequentially".
- `e6632dfb#32` 「これは実空間でやるのが提積では？」 — the assistant conceded its k,q-space TCI answer was a detour and switched to space-time.
- `5053584a#26` 「静的な量を表現するなら，松原よりも少ないはず．O(log beta wmax)だね．」 — imported IR-basis scaling to bound the ghost count.

### Pattern: Probe a downstream consequence the assistant did not flag
**Trigger:** A proposal or design that looks complete on its own terms.
**Reaction:** Asks what breaks downstream — basis dependence, non-unique μ, untrained regions, bond-dimension squaring, missing screens/databases.
**Tag profile:** `bloom:analyze` `depth:deep/causal-consequent` `discourse:referential` `mechanism:exploration`
**Frequency:** 20 occurrences across 7 sessions
**Examples:**
- `5053584a#18` 「gap系でT＝0だと化学ポテンシャルは一意に決まらないのでは？」 — led to a rewrite of the μ / fixed-N formulation.
- `5053584a#19` 「学習は停留点だけで行うんですよね．NNは停留点以外ではトレーニングされない．自己無道着計算のときに問題になりそう．」 — identified the highest implementation risk; fixed by random external-field augmentation.
- `9ddb9c70#5` 「ローカルなデータベースは？アカウントごとに分離するのか？」 — added storage isolation to the multi-account design.

## C. Knowledge acquisition

### Pattern: Ask for a term or mechanism to be unpacked before continuing
**Trigger:** The assistant uses jargon or a compressed step (NCMC bridge, Coulomb metric, spmd vs broadcast).
**Reaction:** Short 「〜とは？」 or 「もう少し説明して」, often with a typo; resumes evaluation right after.
**Tag profile:** `bloom:understand` `depth:intermediate/feature-specification` `discourse:clarification-request` `mechanism:knowledge-deficit`
**Frequency:** 27 occurrences across 8 sessions
**Examples:**
- `4b3736b6#10` 「NCMC の橋渡しで局所的に緩和させるとは？」 — followed by his own NCMC ≈ λ-replica MCMC equivalence (#14).
- `05b6bc31#17` 「うーむ　まだ内部でなにが起きてるのかイメージできない」 — the assistant answered with a diagram of rayon's install path.
- `e6632dfb#24` 「ちょい待ちもっと詳しく説明してよ」 — slowed down the phelel / Wannier discussion.

### Pattern: Fire quick factual lookups to calibrate the landscape
**Trigger:** A new name, tool, programme, or person appears in the conversation.
**Reaction:** One-line 「〜とは？」「〜は誰？」「どの程度使われている？」 lookups, in bursts, before resuming strategy.
**Tag profile:** `bloom:remember` `depth:shallow/feature-specification` `discourse:referential` `mechanism:knowledge-deficit`
**Frequency:** 27 occurrences across 6 sessions
**Examples:**
- `c1906c00#5` 「Timo Betcke 教授、Matthew Scroggs、Ignacia Fierro Piccardoは誰？どの分野の人？」 — mapped the Scientific Computing in Rust community.
- `4b3736b6#21` 「GRACE-1Lはどの程度使われているのか？」 — checked adoption before choosing a parent model.
- `e6632dfb#15` 「たしか，EPWには競合ソフトがあったと思うんだ．なんだっけ？」 — recalled competitors before positioning.

## D. Context sharing and synthesis

### Pattern: Restate the idea in his own terms to lock in a synthesis
**Trigger:** The assistant explains a technique (Gaussian splatting, multi-chart sums, flows).
**Reaction:** Compresses it into an analogy or an operational rule (「パッチングと同じ発想だね」「1つを最適化するとき，他を固定すればいい」) and checks it.
**Tag profile:** `bloom:analyze` `depth:intermediate/verification` `discourse:confirmation-check` `mechanism:common-ground`
**Frequency:** 10 occurrences across 5 sessions
**Examples:**
- `5269dfd9#10` 「まあ，パッチングと同じ発想だね．」 — linked Gaussian splatting to his own patching work.
- `5269dfd9#13` 「複数表現のQTTの和で表現している場合，TCIはまだできそう．1つを最適化するとき，他を固定すればいい」 — turned the representation into a backfitting algorithm.
- `bab3c6db#7` 「へシアンから体積を計算して小さいものから消していくのかなか」 — proposed a concrete pruning rule for spurious minima.

### Pattern: Volunteer insider network or own prior work
**Trigger:** The assistant reasons from public information about a community or code.
**Reaction:** Discloses a personal connection or an artefact he built (rsmpi-rt, friend at VASP, MACE-Osaka author, collaborator's kernels), which changes the feasible options.
**Tag profile:** `bloom:understand` `depth:intermediate|shallow/feature-specification` `discourse:referential` `mechanism:common-ground`
**Frequency:** 7 occurrences across 4 sessions
**Examples:**
- `05b6bc31#11` 「彼は共同研究者なので，彼のカーネルを取り込める」 — made lkdvos's TBLIS-style kernels a Phase 1 comparison target.
- `e6632dfb#7` 「rsmpi-rtというのを作りました．ランタイムでMPIをロード．」 — settled the MPI-ABI question for the new code.
- `4b3736b6#23` 「MACE-Osakaは友人の水上さんが作ってます」 — reshaped which parent model is practical.

## E. Steering and execution

### Pattern: Convert a converged discussion into a terse execution command
**Trigger:** The assistant offers a next step (measure, search, rewrite, post, push).
**Reaction:** One- to few-word imperative — 「試してみて」「先行研究を調べて」「投稿」「ここまででpush」「v7を追加」.
**Tag profile:** `bloom:apply` `depth:deep|shallow/instrumental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 33 occurrences across 9 sessions
**Examples:**
- `bab3c6db#10` 「試してみて」 — triggered the kinetic-distance numerical experiment.
- `4b3736b6#6` 「先行研究を調べて」 — prior-art search for window-BP block updates.
- `9ddb9c70#6` 「投稿」 — posted the design summary to the GitHub issue.

### Pattern: Specify the deliverable with priorities and exclusions
**Trigger:** The discussion has produced enough material for an artefact (plan, proposal PDF, report).
**Reaction:** Dictates scope, audience, and what to drop (「人間関係とか競合の話は抜きにして」「Phase 1では…を優先」), sometimes adding content items one by one.
**Tag profile:** `bloom:create` `depth:deep/instrumental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 14 occurrences across 9 sessions
**Examples:**
- `05b6bc31#23` 「phase 1では，tenferro-rsのバックエンドとして使えることを優先．contractの実装は，…permute + batched gemm方式，…TBLIS方式を移植して2つを比較しよう．」 — fixed the Phase 1 plan with a built-in A/B comparison.
- `e6632dfb#17` 「人間関係とか競合の話は抜きにして，他人に見せられる提案書をPDFで書いて」 — separated politics from the shareable proposal.
- `c1906c00#62` 「やっぱり以前の議論は忘れて，関係者に今後の展望を伝えるレポートにしたい．」 — reframed an email into a forward-looking report with a five-point argument.

---

## Distribution summary

| Dimension | Distribution (278 turns) |
|---|---|
| bloom | evaluate 76 · create 53 · analyze 46 · understand 44 · remember 35 · apply 24 |
| depth | deep 151 · shallow 73 · intermediate 54 |
| discourse | referential 126 · indirect-request 83 · confirmation-check 46 · clarification-request 17 · rhetorical 6 |
| mechanism | knowledge-deficit 67 · common-ground 66 · exploration 64 · action-coordination 53 · conversation-control 27 |
| probe | none 181 · assumption-probe 40 · clarification 27 · evidence-probe 13 · implication 9 · perspective 6 · meta-question 2 |
| presup | sound 247 · ambiguous 9 · missing-context 7 · factive-gap 4 · complex 4 · loaded 4 · leading 2 · existential-gap 1 |

| Category | Patterns | Turns |
|---|---|---|
| A. Idea generation and reframing | 2 | 52 |
| B. Critical evaluation and premise checking | 4 | 74 |
| C. Knowledge acquisition | 2 | 54 |
| D. Context sharing and synthesis | 2 | 17 |
| E. Steering and execution | 2 | 47 |

Observations:
- Evaluate + create together are 46% of turns, and deep turns are 54%: brainstorming is dominated by judging and generating, not by asking for information.
- Assumption probes (40) far outnumber evidence probes (13). He challenges premises from his own knowledge more often than he asks for sources; when he does ask, it is usually a prior-art check (「似た発想は既にないか？」).
- Idea generation (A) and premise checking (B) are interleaved within the same session: a new mechanism is often self-critiqued within one or two turns (`4b3736b6#12→#13`, `c1f12ad9#8→#9`).
- Unassigned residue (34 turns) is mostly one-word option picks from structured forms ("OK", "transfer", form answers) and a few relevance checks on pasted links (「これ関係ある？」).
