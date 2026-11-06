# Thinking Patterns — research

- **Source:** Claude Code (local history), 2026-07-14 – 2026-10-14 JST
- **Contributor:** Hiroshi Shinaoka
- **Topic:** research (tensor networks / QTT / TCI, patching + QFT, Green's-function compression, sampling methods, tenferro-rs / tensor4all-rs ecosystem and its attribution policy)
- **Sessions analyzed:** 23 (833 user turns)
- **Pattern count:** 12

**Method.** Each turn's four discriminating tags (`bloom`, depth level, `discourse`, `mechanism`) were matched against 11 cluster centroids taken from the tag-group listing. A turn joins the centroid it matches best, if it matches on at least 3 of the 4 tags; ties go to the centroid listed first. One centroid (`evaluate/deep/referential`) was then split into two patterns by `probe` (assumption or evidence probe vs. other). 741 of 833 turns (89%) landed in a pattern. The other 92 are scattered one-off combinations. Every pattern appears in at least 8 sessions. Example references use the form `session-file#turn`.

---

## Category A — Steering execution (orchestrating the agent)

### Pattern: Fire terse execution directives
**Trigger:** The assistant finishes a step, proposes a next action, or asks for permission (commit, PR, merge, run, save, search).
**Reaction:** A short imperative that delegates the whole operation, often including the full lifecycle (open the PR, enable auto-merge, monitor until merged). Explanations are rare. Context the agent should already have fills the gaps.
**Tag profile:** `bloom:apply` `depth:deep/instrumental` (some `shallow/instrumental`) `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 144 occurrences across 17 sessions
**Examples:**
- `1cd38dfa991d47baf9bd.json#18` — 「AND BSD-3-Clauseでいいよ．修正PR with auto mergeを立てて mergeまで監視」 → In one turn he settles the license expression and hands over the PR. The assistant opened strided-rs PR #144 with auto-merge and a background monitor.
- `c471da7881e04ec3368f.json#2` — 「Rustで書き直して．多分速くなる．LJ13が出来るか試して」 → A port plus an immediate scale-up target. The assistant rewrote the sampler in Rust and caught a sign error in the Hermite correction along the way.
- `f374b012fd20ad0cef81.json#25` — 「commit & push」 → Pure housekeeping delegation inside a long theory session.

### Pattern: Attach a judgment to the order
**Trigger:** The assistant offers options, a draft, or a plan with an embedded assumption.
**Reaction:** He gives a verdict (soften, drop, pick option X, this is too strong, go bigger) and in the same turn tells the agent to act on it. About 20% of these turns carry an assumption probe that corrects the plan's premise before execution.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:indirect-request` `mechanism:action-coordination` (probe: none or assumption-probe)
**Frequency:** 56 occurrences across 13 sessions
**Examples:**
- `1cd38dfa991d47baf9bd.json#11` — 「そこは謝辞だけでいい気がする．force push」 → Wording judgment and a git command in one line. The attribution text was reduced to an acknowledgment.
- `6f328b71ab7251b1c8d2.json#3` — 「tenferroのorigin/mainを確認．GPU・CPUは必須．tenferroはOpenXLA対応しているよ．」 → The assistant's cost argument rested on a stale local checkout. After fetching origin/main (about 580 files had changed), it retracted the claim.
- `c471da7881e04ec3368f.json#28` — 「いや，より大きなLJクラスターにいこう．今回の系にoveroptimizedしても意味がない」 → He cut off local tuning and redirected the project to larger systems.

### Pattern: Specify the deliverable or experiment from his own design
**Trigger:** A finished discussion, a new idea, or an external event (a reviewer's question, a paper) that needs to become an artifact.
**Reaction:** He states what to build (a crate split, an experiment protocol, a note, a report, a policy table) and usually supplies its key content or framing himself. The assistant fills in the details.
**Tag profile:** `bloom:create` `depth:deep/instrumental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 72 occurrences across 13 sessions
**Examples:**
- `397ea728294db9c54825.json#6` — 「tcontract-rsを作成して，CPU einsum/contractはtenferro-rsから移譲するのがよさそうだ．」 → The assistant agreed but separated what delegation would fix from what it would not.
- `c471da7881e04ec3368f.json#17` — 「比較すべきは．PT only vs PT + qでは？それで，比熱かなにかのvarianceを見る．qはワープで補助」 → He redefined the fair benchmark and its metric.
- `fc52955f8b37bf4bd6a4.json#3` (file `fc52955f70d579a68ee`) — 「最近のcandleの例とかを入れたレポートを返した方がいいね．…エルゴノミクスよりも堅牢性を重視は，ユーザーがエージェントAIを使う時代を見据えた選択でもある」 → A plain-text reply to the reviewer, backed by verified candle `Result` APIs.

### Pattern: Approve with a minimal token
**Trigger:** The assistant asks a yes/no permission question ("Commit?", "Proceed with option 1?") or reports a step done.
**Reaction:** One token (「y」「OK」「はい」「お願い」「書き上げて良い」) or a one-line agreement, keeping the loop going without discussion.
**Tag profile:** `bloom:remember` `depth:shallow/verification` `discourse:confirmation-check` `mechanism:common-ground`
**Frequency:** 89 occurrences across 17 sessions
**Examples:**
- `1cd38dfa991d47baf9bd.json#21` — 「y」 → Authorizes the next PR step.
- `6f5ee131fafcf96e8e85.json#7` — 「方針を更新してよい」 → Approves updating the NOTE's evaluation axis.
- `9bd22dceb57af28d1d20.json#19` — 「それをやりましょう」 → Adopts the proposed experiment.

---

## Category B — Critical evaluation

### Pattern: Overrule the premise with domain knowledge
**Trigger:** An assistant result or argument that rests on a wrong metric, a misleading picture, or a cost assumption he knows from experience to be off.
**Reaction:** A short, often blunt assertion of the correct fact or criterion (「…はずです」「…ではないよ」「なんか変だな」), sometimes with a rough estimate. This usually forces the assistant to re-read its data or redesign.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:referential` `mechanism:conversation-control | common-ground | exploration`, `probe:assumption-probe | evidence-probe`
**Frequency:** 30 occurrences across 12 sessions
**Examples:**
- `a2ea2427e7d122b26fcf.json#29` — 「パラメータの数を減らすことが，パッチングの目的ではないよ．一つ一つのパッチのボンド次元を抑えることです」 → The assistant switched the evaluation axis to patch count at fixed χ and re-read the V=0 data.
- `f374b012fd20ad0cef81.json#55` — 「QFTのMPOのボンド次元はたかだか10-15ぐらいのはず (1軸).一発でかければ，山に登らなくていい」 → The assistant replied 「それだ」 and replaced the staged operator split with a data split.
- `a2ea2427e7d122b26fcf.json#22` — 「QTTは斜めの直線構造は大得意だよ．」 → He corrected an assumed weakness of QTT.

### Pattern: Reflect on strategic positioning and value
**Trigger:** A result, a competitor's paper, or the assistant's framing prompts a "so what" question about the method's or the project's place.
**Reaction:** A judgment about value, competition, or direction ("is QTT worth it vs Chebyshev", "Strand is a rival", "users are not growing", "AI-driven development makes ad-hoc libraries possible"). Often it is self-directed thinking aloud rather than a question.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:referential` `mechanism:exploration | conversation-control` (probe: none or perspective)
**Frequency:** 36 occurrences across 13 sessions
**Examples:**
- `c46a3a56d8b34653a439.json#1` — 「Agentic AI coding時代は，ユーザーがアドホックにテンソルライブラリを作ることも可能である．」 → This opened a long discussion of tenferro-rs's value in the agent era and of agent experience (AX).
- `e6debda059b0e389c462.json#74` — 「短期なら，SOEなり確立した数学理論を物理に応用するほうが気楽．それを超えた革新を狙っているからこそ」 → He framed TT research as a long-horizon bet.
- `c46a3a56d8b34653a439.json#47` — 「ちょっと不安です．ユーザーが増えない」 → The assistant reframed adoption on a months-to-years time constant.

---

## Category C — Idea generation

### Pattern: Float a speculative combination or what-if
**Trigger:** A newly explained method, a bottleneck, or a stray association (a paper, an old technique, a sibling project).
**Reaction:** A question or conjecture that connects two things: "Can X be combined with QTT?", "What if tenferro had fori_loop?", "Can we steal threads from Rayon?", "Represent particles as TTs?" These are often prefaced with 「もっと自由に考えよう」 or 「Fancyなこと言っていい？」.
**Tag profile:** `bloom:create` `depth:deep/enablement | instrumental | causal-consequent` `discourse:referential` `mechanism:exploration` (probe: none, implication, perspective)
**Frequency:** 71 occurrences across 18 sessions
**Examples:**
- `cd03a0be09b472333c90.json#1` — 「テトラヘドロン法を思い出しました．QTTで1/f(kx, ky, kz)を表現できたとき，f(kx, ky, kz)の積分が高速に評価できるなんてことはあるかな」 → Links a classic band-structure method to QTT. The assistant separated the linear integral from the nonlinear inverse.
- `f374b012fd20ad0cef81.json#9` — 「MPOのcontractionはO(chi^4). ただ，要素積はO(chi^3)まで落ちます．…一旦Quantum Fouier transformするか？」 → Proposes using QFT to turn convolution into an elementwise product. This became the backbone of the qtt-moment line.
- `261a5da280c41acb3c0a.json#4` — 「Rayonからスレッドを所有権付きで盗めないのか？そうすれば一部だけ，HPCRayonみたいに書ける」 → An HPC-style team-execution design question about Rayon.

---

## Category D — Understanding and verification

### Pattern: Probe the mechanism behind a claim or scaling
**Trigger:** The assistant reports a number, a scaling, or a performance gap, or asserts an impossibility.
**Reaction:** He asks why. What makes MC work when TCI does not, why the overhead is thin, why one sweep is not enough parallelism, what the scaling in χ is. He often brings his own guess about the cause.
**Tag profile:** `bloom:analyze` `depth:deep/causal-antecedent | intermediate` `discourse:referential` `mechanism:knowledge-deficit | exploration`
**Frequency:** 49 occurrences across 15 sessions
**Examples:**
- `82304d5301d34303b601.json#2` — 「なんでモンテカルロは動くのに，TCIだと計算量が指数的に増えるんだ？何根本的なことを見逃している気がする」 → The assistant explained that MC and TCI rely on different resources (typical-set concentration vs. low rank).
- `397ea728294db9c54825.json#9` — 「そもそもなぜtensorcontractのオーバーヘッドは薄いのか」 → This triggered layer-by-layer profiling arms in tenferro.
- `f274d1980785238b429f.json#9` — 「1本の QTT のスイープだけでは並列度が足りないのはなぜ？」 → The assistant showed that sweeps are sequential and the per-step work is too small to fill a GPU.

### Pattern: Offer his own hypothesis as a tag question
**Trigger:** A partial explanation, or an anomaly whose cause is still open.
**Reaction:** He proposes the explanation himself in a 「…だよね」「…かな」 form, inviting confirmation, and sometimes supplies the actual fix.
**Tag profile:** `bloom:analyze` `depth:intermediate/verification` `discourse:confirmation-check` `mechanism:common-ground` (probe: none, assumption-probe, implication)
**Frequency:** 28 occurrences across 8 sessions
**Examples:**
- `c471da7881e04ec3368f.json#14` — 「一段粗いキーの条件付き分布か、かな」 → His hypothesis about the "hole" led directly to the fb=1 fallback fix.
- `e6debda059b0e389c462.json#14` — 「Kのボンド次元はG程度では？」 → Confirmed: χ_K ≈ χ_G × O(1).
- `f374b012fd20ad0cef81.json#18` — 「kを固定すればポールの数でrankが制限されるね．」 → Confirmed as an exact bound that tied several threads of the formalism together.

### Pattern: Restate the takeaway to lock in understanding
**Trigger:** After an explanation, especially one that corrects his own framing.
**Reaction:** A one-line paraphrase opening with 「ああなるほど」 or 「…だよね」, summarizing the operational conclusion.
**Tag profile:** `bloom:understand` `depth:shallow/verification` `discourse:confirmation-check` `mechanism:common-ground`
**Frequency:** 20 occurrences across 9 sessions
**Examples:**
- `1043ff044d3ebd5e4344.json#5` — 「ああなるほど，TCIをしたければ，sum of product of TTs or product of sum of TTsにとどめるしかないのだね」 → The assistant confirmed it and sharpened where the boundary lies.
- `f374b012fd20ad0cef81.json#31` — 「ああ，k空間で分割されたオブジェクトごとの畳み込みですね．まあ，QFTを高速にやれるかということだよね」 → The assistant refined the claim: the obstacle is the sum over patches, not the QFT itself.
- `9bd22dceb57af28d1d20.json#51` — 「ああ，離散極限ならわかりますね」

### Pattern: Ask what an agent-introduced term means
**Trigger:** The assistant uses jargon, a coined label, or a numbered item he cannot place (staircase, Khatri–Rao sketch, "hole", 「まど」).
**Reaction:** A bare 「〜とは？」 or 「〜ってなに？」 clarification request, often several in a row in dense sessions.
**Tag profile:** `bloom:understand` `depth:intermediate/concept-completion | feature-specification` `discourse:clarification-request` `mechanism:knowledge-deficit` (probe: clarification)
**Frequency:** 85 occurrences across 17 sessions
**Examples:**
- `9bd22dceb57af28d1d20.json#10` — 「staircaseとは？」 → The assistant admitted the label was its own name for the user's proposed structure.
- `c471da7881e04ec3368f.json#12` — 「チェーンが重みを置く状態でほとんど確率を持たない「穴」とは？」 → The assistant corrected its earlier imprecise wording.
- `f274d1980785238b429f.json#15` — 「中間テンソルとは？環境じゃないよね」

### Pattern: Look up facts, status, or a forgotten definition
**Trigger:** He needs a factual input (prior work, benchmark data, repo status) or resumes after a break and has lost the notation.
**Reaction:** A short retrieval question: 「…はあるか？」「…ってなんだっけ」「done?」.
**Tag profile:** `bloom:remember` `depth:shallow/verification | concept-completion` `discourse:referential` `mechanism:knowledge-deficit`
**Frequency:** 61 occurrences across 13 sessions
**Examples:**
- `b57cb7bbac8bf9ed4fe5.json#2` — 「Faerの並列性能についてベンチマーク結果はありますか？」 → The assistant pulled the official faer benchmark pages.
- `82304d5301d34303b601.json#7` — 「たきどうに拡張した後続論文はあるか？」 → A literature follow-up check.
- `a7f70052a345e9139e19.json#7` — 「mu(h)ってなんだっけ？muとhの定義？」 → A notation refresh mid-derivation.

---

## Distribution summary

**Pattern share (741 clustered turns):** Steering execution 361 (49%): directives 144, approvals 89, deliverable specs 72, judgment plus order 56. Understanding 243 (33%): term clarification 85, lookups 61, mechanism probes 49, own hypotheses 28, restatements 20. Idea generation 71 (10%). Critical evaluation 66 (9%): premise overrule 30, strategic reflection 36.

**Whole-topic tag distribution (833 turns):**
- **Bloom:** evaluate 184, apply 146, analyze 134, remember 127, create 125, understand 117. Evaluate is the most common level. Higher-order turns (analyze + evaluate + create) make up 53%.
- **Depth:** deep 429 (51%), shallow 240, intermediate 164.
- **Discourse:** indirect-request 304, referential 278, confirmation-check 152, clarification-request 79, rhetorical 17, display 3.
- **Mechanism:** action-coordination 256, knowledge-deficit 203, common-ground 177, exploration 134, conversation-control 51, debugging 10.
- **Probe:** none 565, clarification 97, assumption-probe 93, implication 34, perspective 27, evidence-probe 12, meta-question 5. Assumption probes concentrate in the premise-overrule and judgment-plus-order patterns.
- **Presupposition:** sound 774 (93%). Non-sound cases are rare: ambiguous 18, missing-context 12, leading 10, factive-gap 8, complex 5, loaded 4, existential-gap 2. Most stem from typos, elliptical references, or leading tag questions rather than false beliefs.

**Shape of a typical session:** long sessions (77–107 turns: `1cd38dfa`, `9bd22dce`, `e6debda0`, `f374b012`, `a7f70052`) alternate between bursts of terse execution directives and bursts of deep exploration. A typical sequence:
1. He floats a combination or conjecture.
2. The assistant builds it out.
3. He probes the mechanism or overrules a premise using a physical estimate.
4. He specifies the experiment or note.
5. He approves with a single token.

Explicit debugging (`mechanism:debugging`) is almost absent from this topic. Errors are caught as premise overrules ("the bond dimension should be ~10–15", "cutoff is too small") rather than as stack-trace-driven debugging.
