# Thinking Patterns — code-review

- **Source:** Claude Code (2026-07-14 – 2026-10-14 JST)
- **Topic:** code-review (audits and reviews of issues, PRs, design docs, and `origin/main` in tenferro-rs, tensor4all-rs, strided-rs, hataori-rs, tprims-related repos, plus one matrix-desktop review)
- **Sessions analyzed:** 21 (254 user turns)
- **Pattern count:** 12
- **Method:** Turns were clustered when at least 3 of 4 dimensions (`bloom`, depth level, `discourse`, `mechanism`) matched the pattern's profile and the trigger was the same kind of event. Only patterns that appear in at least 2 sessions are kept. Frequencies count only turns that meet the 3-of-4 rule. A turn can belong to two patterns when it plays both roles (for example df29#7 and #8 are both a veto and a benchmark gate), so the counts overlap. The patterns cover 165 of the 254 turns.

Session key (file prefix): `1034`=10346a646f673ded2c0b, `14fd`=14fd17c8b2b89c9c291f, `1b62`=1b626845acc49f0d900d, `20df`=20df817909780308c573, `29c0`=29c0b4d18d6a1cbf04fa, `329a`=329a54b43c29370daefe, `383c`=383cb9e9990bbb543074, `3db6`=3db6bba98d6b284593fb, `71aa`=71aa54de0ab4dbcb1952, `7334`=7334bc868ba55050631a, `a3c0`=a3c044c8d47749c204f5, `a54e`=a54ef1640df5c5131880, `ad69`=ad6952b136aa06396d81, `b53c`=b53ceddc147d051a5c4a, `bac4`=bac404fab6d356ca1bfb, `c16f`=c16f7571ee148c29b7e3, `c597`=c597007df33f2b46330c, `c8c0`=c8c096947f778ee3dbb1, `cacf`=cacfe50d7f18d39c0609, `df29`=df293cba53292827259f, `e53b`=e53bba434d5c23cefcfc.

---

## Category A — Orchestrating the review pipeline

### Pattern: Commission an audit with an explicit evaluation lens
**Trigger:** A merged PR, a new or updated issue, a design doc, or the state of `origin/main`. This usually opens the session.
**Reaction:** He gives a URL or repo and a verb (監査 / レビュー / 評価), and often names the criteria: long-term direction rather than short-term effort, over-engineering, overly strict acceptance criteria, overly defensive code or tests written only for coverage, whether the API suits AI-written code, and rule porting. Sometimes he also says how the audit should run, for example by delegating to cheap agents.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 27 occurrences across 18 sessions
**Examples:**
- c16f#1: 「…#1433 を検討して．短期的な作業量ではなく，長期的に正しい方向性に向かっているか？という観点で評価してほしい．」 Outcome: a 62-turn design session about long-term direction.
- df29#1: 「…PR #1453 レビューしてください．特に，設計の柔軟性（長期的拡張に耐えうるか), 実装の妥当性 (too defensive, 過剰なテストがないか…)」 Outcome: the review found a Mutex issue and a performance regression, and the merge was postponed.
- 20df#1: 「AI時代に適したAPIかどうかという点は重視．つまり，人間がコードを書かないという前提です．」 Outcome: an audit judged from an AI-authorship premise, covering over-engineering and acceptance criteria.

### Pattern: Relay another agent's report for cross-checking
**Trigger:** Another agent (Codex, a parallel Claude session, or a human collaborator) posts a status report, an issue comment, or a new branch.
**Reaction:** He pastes the report or just says 「コメントを確認」/「issueとbranchが更新されました」, and expects the assistant to re-read the source and verify the claims instead of trusting them. Claude is used as an independent auditor of other agents.
**Tag profile:** `bloom:apply` (also evaluate/analyze) `depth:deep/instrumental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 12 occurrences across 8 sessions
**Examples:**
- 1034#3: pasted remediation status (「Issue #1617 remediation は、Apple 実機テスト直前まで完了しました。…」). Outcome: Metal tests were run locally against the candidate commit.
- c16f#11: 「• 設計書を更新し、commit・pushしました。…」 (another agent's completion report). Outcome: the assistant reviewed the detailed design.
- 329a#16: 「issueをチェック．新しいコメントが来た」 Outcome: the assistant read and assessed the new comment, then posted a review.

### Pattern: Convert a verdict into a GitHub artifact
**Trigger:** The assistant has finished a review or proposed a fix list.
**Reaction:** He gives a terse order to externalize the result, such as 「commentを追加」「監査コメントを投稿」「umbrella以下のすべてのphaseの起票」「commitしてよ」, so the issue tracker becomes the shared memory for downstream agents.
**Tag profile:** `bloom:apply` `depth:deep|shallow/instrumental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 26 occurrences across 14 sessions
**Examples:**
- 1b62#3: 「umbrella以下のすべてのphaseの起票をお願い」 Outcome: phase issues were filed under the new umbrella.
- c8c0#3: 「監査結果をissueとして投稿して」 Outcome: the algorithm audit became a tracked issue.
- df29#34: 「Close 1483.」 Outcome: an optimization issue with no evidence behind it was closed.

### Pattern: Greenlight an offered side-effect with a one-word reply
**Trigger:** The assistant asks for permission ("投稿しますか", "メモリに残しますか", option a/b).
**Reaction:** He approves with one word (はい / おk / y / 投稿 / a) and does not reread the draft. He trusts the content once the substance has been agreed.
**Tag profile:** `bloom:remember` `depth:shallow/verification` `discourse:confirmation-check` `mechanism:common-ground`
**Frequency:** 13 occurrences across 7 sessions
**Examples:**
- 329a#18: 「投稿」 Outcome: the review was posted to the issue.
- 71aa#10: 「y」 Outcome: the reply was posted and a prerequisite issue was created.
- c16f#49: 「a」 Outcome: option (a) was chosen and the issue was closed.

---

## Category B — Steering and constraining

### Pattern: Push back on the assistant's framing with insider design intent
**Trigger:** The assistant labels something as a defect, proposes a scoped-down option, or treats a constraint as optional.
**Reaction:** He rejects the framing in a short sentence based on history, design intent, or a downstream need ("this coexistence is historical", "session propagation is unavoidable", "multi-GPU must stay in mind"), and the assistant re-scopes.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:referential` `mechanism:conversation-control`; `probe:assumption-probe` is common
**Frequency:** 10 occurrences across 8 sessions
**Examples:**
- a54e#3: 「「networkスタック」…と「TCIスタック」…という2製品の同居は，仕方ないことです．歴史的に」 Outcome: the audit stopped treating the dual stack as a defect.
- 20df#6: 「session引数が下流に伝搬することは避けられないと思います」 Outcome: session propagation was recorded as a downstream convention, not a flaw.
- 3db6#4: 「IDのみでソートはまずいです．」 Outcome: the ID-only sort became a blocking point in the posted review.

### Pattern: Veto or re-sequence work based on live project state
**Trigger:** The assistant proposes editing an issue or starting work, or a question about ordering comes up.
**Reaction:** He uses knowledge the assistant lacks (another agent is implementing, P0 is already in progress, benchmarks would be wasted before unification) to block a change, defer it to a future-plan issue, or reorder the work: unify first, then benchmark. 「いや」 often marks the turn.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:indirect-request` `mechanism:conversation-control|action-coordination`
**Frequency:** 16 occurrences across 6 sessions
**Examples:**
- c16f#48: 「いや実装中だからいじらないで．」 Outcome: the issue was left untouched while implementation was in progress.
- df29#7: 「今別エージェントがベンチマークをしていますが，しんけいろに統一してからでないと無駄になりますね」 Outcome: benchmarking was moved after the path unification.
- a3c0#14: 「いやP0の実装は進んでるから，将来計画として，issueに投稿したほうがいいね」 Outcome: prefetch was filed as a future-plan issue instead of changing P0.

---

## Category C — Building understanding

### Pattern: Admit confusion and demand a plain explanation
**Trigger:** The assistant's answer is dense, full of jargon, or quotes an unexplained claim.
**Reaction:** He says openly that he does not follow (「何を言ってんのか不明だ」「10μsが大きいのかよくわからんな」) or quotes the sentence and asks 「どういうこと？」. In other sessions he asks for an illustrated explainer.
**Tag profile:** `bloom:understand` `depth:intermediate` `discourse:clarification-request` `mechanism:knowledge-deficit`
**Frequency:** 7 occurrences across 5 sessions
**Examples:**
- c16f#4: 「何を言ってんのか不明だ」 Outcome: the assistant re-explained the thread budget as a number passed to kernels, and he then adopted it into the design (c16f#5).
- df29#26: 「grad() が返す tensor をユーザーが保持している場合…どういうこと？」 Outcome: the aliasing hazard was clarified, which led to the copy-on-write discussion and a systemic audit.
- a3c0#4: 「UNNELEDに留まり，MULTIPLEを非目標とするとは？」 Outcome: the MPI threading-level choice was explained.

### Pattern: Probe backend capability facts to ground a design rule
**Trigger:** A design contract touches a concrete library (faer, OpenBLAS, MKL, Accelerate, ArmPL, Rayon, Julia, cuTENSOR).
**Reaction:** He asks a chain of concrete capability or quantity questions: can it control threads locally, where does AMX run, what is PyTorch's small-matrix overhead, what does a Rayon install cost. Each answer becomes a contract clause or a decision.
**Tag profile:** `bloom:analyze|understand` `depth:intermediate/feature-specification|quantification` `discourse:referential` `mechanism:knowledge-deficit`
**Frequency:** 19 occurrences across 6 sessions
**Examples:**
- c16f#5: 「faerは制御可能．BLASは最新のOpenBLAS, MKLはスレッド数をlocalで制御可能なはず．Accelerateはどうか？」 Outcome: led to the rule "error if `openblas_set_num_threads_local` is missing" (c16f#6).
- c16f#46: 「PyTorchで小行列のオーバーヘッドはの程度？n = 32とか？」 Outcome: set the "match PyTorch eager overhead" goal (c16f#47).
- 20df#14: 「本当にzero overheadが必要なところはバックエンドを直に呼べばいいわけだからな．それはでkるの？」 Outcome: an issue to re-export faer and BLAS from tenferro-cpu (20df#15).

---

## Category D — Reframing and systematizing

### Pattern: Step back to question necessity or inject a driving workload
**Trigger:** A detailed design or optimization discussion reaches a plateau.
**Reaction:** He zooms out to the meta level: is a tensor library needed at all in the AI era, is a Julia layer still worth having, are these optimizations needed, what would it take to reimplement arXiv:2310.03920. He sometimes asks for an explicit rebuttal of his own provocation.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental|goal-orientation` `discourse:referential` `mechanism:exploration`; `probe:assumption-probe|meta-question`
**Frequency:** 11 occurrences across 5 sessions
**Examples:**
- c16f#26: 「テンソルライブラリなんて，AI時代にいるんだろうか．AIが直接raw BLAS/LAPACK APIを叩けばいいのでは？どう反論する？」 Outcome: a rebuttal, then his own counterpoint that not everyone wants to build from scratch.
- df29#30: 「そもそもこれらの最適化は本当に必要なのか？」 Outcome: the optimization queue turned out to come from static reading, not profiling, and the "no optimization without numbers" policy was adopted.
- c16f#16: 「https://arxiv.org/pdf/2310.03920 例えばこれを再実装しようとすると？tenferroには何が必要だ？」 Outcome: a gap list checked against a real DMRG workload.

### Pattern: Derive a downstream consequence the assistant left implicit
**Trigger:** The assistant explains a mechanism or a migration plan.
**Reaction:** He states the logical consequence himself and asks for confirmation: CPU idles without prefetch, in-place indexing forces a version counter, non-regression means the whole port must finish, depending on cuTENSOR makes it mandatory.
**Tag profile:** `bloom:analyze` `depth:deep/causal-consequent` `discourse:confirmation-check` `mechanism:common-ground`; `probe:implication`
**Frequency:** 7 occurrences across 5 sessions
**Examples:**
- df29#15: 「この移植は正さ＋パフォーマンスが非劣化を確認して終わりです．ということは，全移植が終わらないと，いけないとうことなんですよ」 Outcome: the issue tree was rebuilt with a terminal performance gate, and correctness checks moved into each phase.
- a3c0#9: 「新しいタスクを割り当てるとき，事前にデータ転送をしないとCPUが遊ぶよね」 Outcome: surfaced root-serial dispatch as a hidden amplifier, and prefetch was planned.
- df29#54: 「CuTensorに依存させると，それが必須になるよね．」 Outcome: the decision fork "make cuTENSOR mandatory or not" (df29#55–59).

### Pattern: Promote a local finding into a systemic rule, requirement, or audit
**Trigger:** A concrete defect or lesson in one issue (vector cache keys, missing view docs, an unmeasured optimization, retired duplicate crates).
**Reaction:** He turns it into an org-wide or repo-wide norm: an agent-rules PR, an implementation-complete requirement, a policy recorded to memory, an umbrella issue, or an inventory of AGENTS.md and REPOSITORY_RULES.md.
**Tag profile:** `bloom:evaluate|create` `depth:deep/judgmental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 11 occurrences across 6 sessions
**Examples:**
- 71aa#8: 「パフォーマンスに関するルールにVector{Int}をそのままkeyにすべきではないと入れるべきですね．…全体のagent rulesに実装してPRmerge」 Outcome: tensor4all-agent-rules PR #12 merged (common, Rust, and Julia rules).
- 29c0#3: 「実装完了の要件にドキュメントを追加を入れるべきですね」 Outcome: documentation became part of the definition of done.
- df29#32: 「数値に裏付けられていない最適化は禁止ですね．はい，JAXに揃えるのがいいです」 Outcome: both policies were posted to #1489 and saved to memory.

### Pattern: Gate decisions on benchmark evidence
**Trigger:** An optimization, a cache, a merge point, or a default backend choice is on the table.
**Reaction:** He requires measurement before acceptance (compare against the TT version, check tree overhead, benchmark thoroughly after Phase 8) or brings his own measurement as the basis for the decision.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 8 occurrences across 3 sessions
**Examples:**
- 71aa#5: 「両方の実装を行って，ベンチマークでtree overheadを確認した後，実用上問題なければ完了とする」 Outcome: a benchmark gate was written into the acceptance criteria.
- df29#8: 「GraphExecutor の毎回再 stagingを除いても大きなregressionが見えています．…PRに指示文をコメント」 Outcome: an instruction comment on the PR to fix the design before merging.
- c16f#47: 「とはいえ，eagerでもPyTorch並みにoverheadは減らしたい」 Outcome: a PyTorch-parity overhead target was recorded.

---

## Distribution summary

| Dimension | Distribution over all 254 turns |
|---|---|
| bloom | evaluate 92 (36%), analyze 53 (21%), apply 44 (17%), understand 26 (10%), remember 21 (8%), create 18 (7%) |
| depth | deep 163 (64%), shallow 51 (20%), intermediate 40 (16%) |
| discourse | indirect-request 134 (53%), referential 75 (30%), confirmation-check 36 (14%), clarification-request 7, rhetorical 2 |
| mechanism | action-coordination 116 (46%), knowledge-deficit 54 (21%), common-ground 34 (13%), conversation-control 25 (10%), exploration 23 (9%), debugging 2 |
| probe | none 183, assumption-probe 33, clarification 15, implication 12, perspective 8, meta-question 2, evidence-probe 1 |
| presup | sound 230 (91%); leading 7, ambiguous 6, complex 3, factive-gap 3, missing-context 3, loaded 2 |

**Patterns by category:** A (orchestration) 4 patterns / 78 turns; B (steering) 2 / 26; C (understanding) 2 / 26; D (reframing and systematizing) 4 / 37.

**Reading:**
- Most turns are orchestration. Evaluate-level audit requests and apply-level "post/commit/file" commands make up about half of all turns. In this topic Claude acts as a reviewer and dispatcher inside a multi-agent pipeline, and the GitHub issue tracker is the system of record.
- The intellectual weight is in Category D and in the pushback pattern. These turns are few but they change the outcome: policies such as no unmeasured optimization and JAX-style in-place semantics, an org-wide agent rule, and the definition of done.
- Escalation is quick. A session can go from a one-word approval to a meta-question about whether the library should exist within a few turns (20df#7→#8, c16f#24→#26). Long sessions (c16f, df29) alternate between capability probing (C) and reframing (D).
- Presuppositions are almost always sound. The few leading turns (「どうせ…ですよね」「すべきだよね？」) are deliberate provocations or requests for agreement, and the assistant did not always correct them (see 20df#5 and c16f#38).
- Rare: explicit evidence-probes (1). He usually challenges with domain recall (「どこかでIdxTensorに変えたはず」) rather than asking for sources. Debugging-style reviews are also rare (2).
