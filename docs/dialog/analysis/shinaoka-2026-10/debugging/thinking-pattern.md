# Thinking Patterns — debugging

- **Source:** Claude Code (2026-07-14 – 2026-10-14 JST)
- **Topic:** debugging
- **Contributor:** Hiroshi Shinaoka
- **Sessions analyzed:** 11 (74 user turns; sessions dated 2026-07-19 – 2026-10-05)
  - `0990badbf09ea982d0e0` tenferro/strided-rs benchmark gaps vs PyTorch, fixes, release (9 turns)
  - `27cd3fee44d23aca3197` koushi-matrix batch of GitHub issues (3)
  - `287ffddba41d5513de7d` Koushi Megolm index-0 key loss / frequent rotation (9)
  - `390b0d7f3d8edc01f68c` SparseIR.jl complex-fit bug → full audit → org rules → patch release (11)
  - `51b3f7dc5c11a508f199` matrix-desktop attachment preview sliding (4)
  - `5d59b7c19c46d3f88a5a` tensor4all-rs TreeTN TDVP accuracy regression (1)
  - `5e567c0882365f6b9627` matrix-desktop add-account sign-in failure → revert multi-account (17)
  - `73c7f96f938ad2a2e631` thread root / pre-join messages unreadable, layout break (3)
  - `96278e622f138bab2e51` tray icon / resident app on Linux/Windows (1)
  - `9cf3238a20c7ab77f334` Element receive-side key loss, `m.dummy` unwedge bug upstream (8)
  - `c3031e376e17d1ef3f96` timeline scroll jank and jump-to-past (8)
- **Pattern count:** 12 (60 of 74 turns clustered)

Clustering rule: turns grouped when at least 3 of {bloom, depth level, discourse, mechanism} match the pattern's core profile; only patterns seen in at least 2 sessions are kept. Counts computed by script over the session JSON.

---

## A. Diagnosis and root-cause framing

### Pattern: Report symptoms with an embedded causal hunch and ask for the root cause
**Trigger:** A user-visible malfunction in his own software (Koushi/matrix-desktop, SparseIR.jl, tensor4all-rs), often at session start, or a new symptom appearing mid-session.
**Reaction:** Describes concrete symptoms (often two at once), frequently adds a tentative mechanism as a question or "〜だよね" and sometimes pastes raw diagnostics/logs; asks for the "根本的な原因" rather than a patch. Includes cross-client comparison ("Element/Element Xでも起きる?").
**Tag profile:** `bloom:analyze` `depth:deep/causal-antecedent` `discourse:indirect-request` `mechanism:debugging`
**Frequency:** 10 occurrences across 7 sessions
**Examples:**
- `287ffddba41d5513de7d#1` — 「送信用の鍵が更新されたタイミングで，相手がindex=0の鍵を受け取れていません．…特定のDMで，こちらの送信用の鍵がしょっちゅう切り替わりますね」 → parallel investigation found a forked SDK that discards keys on every member reload; the two symptoms turned out to be linked.
- `9cf3238a20c7ab77f334#1` — 「何が根本的な理由なのか，調べて．Element/Element Xから送信する場合にも起きうる問題ですか？」 → identified a known UISI race class, then shifted to receiver-side analysis.
- `c3031e376e17d1ef3f96#5` — 「最新履歴にいたはずなのに，別のルームから戻ってきたとき，盛大に過去に飛ばされることがある．確率的にしか起きない」 + pasted generation logs → stale-generation projection replay diagnosed and filed as issues.

### Pattern: Challenge the diagnosis by comparison with a reference implementation
**Trigger:** The assistant offers a detailed mechanism, a fix menu, or asks for more symptom details.
**Reaction:** Steps back to an evaluative stance and reasons by contrast with a known-good system (Element / Element X): "if Element does not have this problem, it is ours"; "does Element X even have this feature?"; "look at Element's implementation". Often states a design principle that the fix must satisfy.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:indirect-request|referential` `mechanism:debugging` (probe: assumption-probe in all 3)
**Frequency:** 3 occurrences across 3 sessions
**Examples:**
- `287ffddba41d5513de7d#4` — 「いや，Elementから送信してこの問題が起きないなら，Koushiの問題では．」 → assistant confirmed: same SDK upstream works, Koushi's vendored fork (+4600 lines on the share path) is the culprit.
- `c3031e376e17d1ef3f96#2` — 「Element, Element Xの実装を見て … 局所的情報からスクロール距離は決まっているべき」 → all three Element clients use local (bottom-anchored / inverted-list) anchoring; confirmed the global-offset + 72px estimate as root cause.
- `5e567c0882365f6b9627#5` — 「サーバーを手動で変えるパスは不要では？Element Xにそういう機能あります？…UIと処理を考え直してみて」 → skipped symptom Q&A; triggered a redesign audit that found the login-accept bug.

### Pattern: Flag a broken build/CI tersely and expect autonomous repair
**Trigger:** While the assistant is busy elsewhere, he notices a red CI run or locally failing tests.
**Reaction:** Pastes a URL or one-line observation (「mainが落ちてますね」「手元で落ちているやつは直して」) with no further spec; expects the assistant to diagnose and fix.
**Tag profile:** `bloom:apply` `depth:deep/instrumental` `discourse:indirect-request` `mechanism:debugging|action-coordination`
**Frequency:** 2 occurrences across 2 sessions (related: `51b3f7dc5c11a508f199#3` 「PRが失敗？」)
**Examples:**
- `0990badbf09ea982d0e0#9` — 「https://github.com/tensor4all/strided-rs/actions/runs/… mainが落ちてますね．」 → assistant investigated the strided-rs main failure in the middle of a release.
- `5e567c0882365f6b9627#16` — 「手元で落ちているやつは直して」 → local failing tests fixed before merge.

---

## B. Remedy selection and scope

### Pattern: Reject incremental fixes in favor of reverting to a known-good baseline
**Trigger:** The assistant lays out a list of fork-specific defects or offers "revert the last PR vs. minimal hotfix".
**Reaction:** Chooses the more radical structural option — revert the custom send/key-sharing path to upstream (Element X's path), or revert to before the whole multi-account feature — and justifies it with past failed attempts; then wants careful rework on a separate branch.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:referential|indirect-request` `mechanism:action-coordination`
**Frequency:** 3 occurrences across 2 sessions
**Examples:**
- `287ffddba41d5513de7d#5` — 「多分，一旦，送信・鍵の共有パスをオリジナルに戻すべきですね．」 → plan changed to restore upstream share→encrypt.
- `287ffddba41d5513de7d#6` — 「resend index-0系は試したけど，一度もうまくいなかった．全部一旦削除すべき」 → all custom repair mechanisms scheduled for removal (issue #795).
- `5e567c0882365f6b9627#7` — 「むしろmulti account以前にrevertして，じっくり作業しあmしょう」 → #1097 and #1102 reverted in #1107; work moved to `develop_multi_account`.

### Pattern: Generalize from one found bug to a systematic sweep
**Trigger:** One defect (or performance gap) has been confirmed and the assistant proposes fixing just that.
**Reaction:** Asks to look for the whole class: all cases trailing PyTorch, "類似の問題がないか精査", "見つけたバグを全部対処".
**Tag profile:** `bloom:analyze|evaluate` `depth:deep` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 3 occurrences across 3 sessions (related: `390b0d7f3d8edc01f68c#2` 「他にテストが弱いところはないのか？」)
**Examples:**
- `0990badbf09ea982d0e0#1` — 「PyTorchに大幅に劣後しているケースについて，原因を調べて．」 → categorized gaps A–E (op branching per element, serial reduce, non-parallel CopyPlan, etc.).
- `73c7f96f938ad2a2e631#3` — 「直して．類似の問題がないか精査して」 → fix plus audit for similar layout breaks.
- `390b0d7f3d8edc01f68c#11` — 「おっとそれを修正してからバージョンアップデートするべきでしたね．．．見つけたバグを全部対処」 → all audit-found bugs addressed before the release.

### Pattern: Institutionalize the lesson as tests, benchmarks, and repository rules
**Trigger:** An audit or benchmark report reveals bugs that existing tests/benchmarks should have caught.
**Reaction:** Escalates from fixing to prevention: add missing benchmarks at the lower layer, write audit rules, set up AGENTS.md / llms.txt / REPOSITORY_RULES modeled on tenferro-rs.
**Tag profile:** `bloom:create|evaluate` `depth:deep` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 3 occurrences across 2 sessions
**Examples:**
- `0990badbf09ea982d0e0#2` — 「strided-rsの段階でバグを検出するべきだと思う．…監査ルール整備をして．」 → missing reduce/max/min/CopyPlan benchmarks identified as why strided did not catch the bugs.
- `390b0d7f3d8edc01f68c#4` — 「tenferro-rsを見習って，llms.txt等の整備をしたい．…rust, julia, pythonにそれぞれissueを作成」 → three issues opened.
- `390b0d7f3d8edc01f68c#5` — 「AGENTS.mdやレポジトとルールを整備すべきでは？tenferro-rsに沿って．」 → led to an org-wide shared rules repository.

---

## C. Agent orchestration and workflow

### Pattern: Delegate exploration/implementation to sub-agents and keep the assistant as planner-auditor
**Trigger:** Start of a fix task, or the assistant offers to fix directly.
**Reaction:** Specifies roles: Opus/Sonnet sub-agents explore and implement, the main assistant plans and audits; asks for independent verification by another agent.
**Tag profile:** `bloom:apply` `depth:deep/instrumental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 4 occurrences across 4 sessions (related: `390b0d7f3d8edc01f68c#6` 「あなたはPLAN，reviewのみに集中」)
**Examples:**
- `96278e622f138bab2e51#1` — 「実装や探索はOpus or sonnetのサブエージェントに任せて，Fableは結果の監査，計画に集中すること．」 → fix delivered via sub-agents with audit.
- `390b0d7f3d8edc01f68c#3` — 「いや，opusに全コードをさらに探索させて．」 → two Opus audits found dead APIs and tests silenced by skip-on-failure.
- `9cf3238a20c7ab77f334#5` — 「今使っているissueに投稿．別エージェントにも確かめてもらいます」 → self-contained claim with verification recipe and falsification conditions posted.

### Pattern: Convert findings into a tracked issue instead of fixing in-session
**Trigger:** The assistant finishes an analysis or proposes to start implementing.
**Reaction:** Asks for an issue (or issue comment), often because other agents will implement, and adds constraints such as "simplest possible fix".
**Tag profile:** `bloom:apply` `depth:intermediate|deep/instrumental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 4 occurrences across 3 sessions
**Examples:**
- `287ffddba41d5513de7d#7` — 「作業は他のエージェントがやるので，issueを作成」 → issue #795 written so an implementing agent can work without the conversation.
- `c3031e376e17d1ef3f96#3` — 「できるだけ簡単な修正で直したいね issueにできるか？」 → minimal-fix issues filed.
- `287ffddba41d5513de7d#9` — 「js_error_count=1（window_error、詳細なし）issueを作って」 → diagnostics finding filed.

### Pattern: Set governance rules for autonomous agent work
**Trigger:** Multi-step work (PRs, releases, reverts) is about to proceed with the assistant asking for permission at each step.
**Reaction:** States a standing policy: may merge PRs autonomously; revert merges now but the new fix merges only after thorough testing on a working branch; org-wide rules repo with role split.
**Tag profile:** `bloom:evaluate` `depth:deep/judgmental` `discourse:indirect-request|confirmation-check` `mechanism:action-coordination|conversation-control`
**Frequency:** 3 occurrences across 3 sessions
**Examples:**
- `0990badbf09ea982d0e0#3` — 「自律的にPRはマージして良い．」 → assistant merged strided/tenferro PRs without further prompts.
- `5e567c0882365f6b9627#10` — 「revertはmerge. 今回の修正はworking branchで十分テストしてからマージする」 → revert merged; fixes accumulated on the working branch.
- `390b0d7f3d8edc01f68c#6` — 「組織共通ルールリポジトリにしましょう．実際の実装や捜索はsonnet, opusに任せてください．」 → `spm-agent-rules` repo plan.

### Pattern: Drive the PR → merge → release pipeline with terse imperatives
**Trigger:** The assistant reports progress, offers a PR, or asks "proceed?".
**Reaction:** One- to few-word commands (「PR」「PR merge」「修正」「check」「make a PR」「全部やって．できるだけPRをまとめる」「二つのPRを統合してマージして」), often chaining the next stage (release after merge) and consolidating PRs.
**Tag profile:** `bloom:apply` `depth:deep|shallow/instrumental` `discourse:indirect-request` `mechanism:action-coordination`
**Frequency:** 19 occurrences across 6 sessions
**Examples:**
- `390b0d7f3d8edc01f68c#10` — 「PR mergeまで．その後，Python, Juliaパッケージのpatch releaseの準備を進めて．」 → merge followed by release prep.
- `51b3f7dc5c11a508f199#4` — 「mergeされました．origin/mainのCIが通り次第，v0.6.0をリリースしてください」 → conditional release.
- `27cd3fee44d23aca3197#2` — 「全部やって．できるだけPRをまとめる」 → overrode the assistant's narrowing proposal.

---

## D. Grounding and comprehension

### Pattern: Approve the assistant's offer with a one-word go-ahead
**Trigger:** The assistant proposes a concrete next step or presents a choice form.
**Reaction:** 「すすめて」「issue化して」 or selecting the recommended option.
**Tag profile:** `bloom:remember` `depth:shallow/verification` `discourse:confirmation-check` `mechanism:common-ground|action-coordination`
**Frequency:** 4 occurrences across 3 sessions
**Examples:**
- `390b0d7f3d8edc01f68c#7` — 「すすめて」 → rules repo drafted and pushed.
- `c3031e376e17d1ef3f96#6` — 「issue化して」 → two issues filed.
- `0990badbf09ea982d0e0#7` — selected "Publish (Recommended)" for strided-rs 0.4.3 → crates.io publish.

### Pattern: Ask what an unfamiliar term or numbered point means
**Trigger:** The assistant's report uses protocol jargon or a numbered item whose meaning is opaque.
**Reaction:** Short clarification question, sometimes with a meta remark.
**Tag profile:** `bloom:understand` `depth:shallow/concept-completion` `discourse:clarification-request` `mechanism:knowledge-deficit`
**Frequency:** 2 occurrences across 2 sessions
**Examples:**
- `287ffddba41d5513de7d#3` — 「(1) -> 意味がわからない．」 → assistant re-explained the receiver-side impossibility point.
- `9cf3238a20c7ab77f334#4` — 「AIでのバグ報告は気が引けますね．m.dummyとは？」 → explanation of Olm unwedging via `m.dummy`; led to discovering it is never sent.

---

## Distribution summary

| Category | Patterns | Occurrences |
|---|---|---|
| A. Diagnosis and root-cause framing | 3 | 15 |
| B. Remedy selection and scope | 3 | 9 |
| C. Agent orchestration and workflow | 4 | 30 |
| D. Grounding and comprehension | 2 | 6 |

Whole-topic tag distribution (74 turns):

- **bloom:** apply 33, analyze 16, evaluate 14, remember 7, create 2, understand 2
- **depth:** deep 47, shallow 15, intermediate 12
- **discourse:** indirect-request 56, referential 10, confirmation-check 5, clarification-request 3
- **mechanism:** action-coordination 47, debugging 17, knowledge-deficit 4, conversation-control 3, common-ground 2, exploration 1
- **probe:** none 65, assumption-probe 3, clarification 2, implication 2, evidence-probe 1, perspective 1
- **presup:** sound 62, missing-context 4, factive-gap 3, ambiguous 2, complex 1, existential-gap 1, leading 1

Observations:

- The topic is dominated by orchestration (apply / action-coordination): he acts as a maintainer directing agents through issue → PR → merge → release, mostly in terse imperatives.
- The intellectually decisive turns are few but consistent: evaluative reasoning by contrast with a reference implementation (Element/Element X, upstream SDK, tenferro-rs as rules template) and a preference for structural remedies (revert to known-good, catch bugs at the lower layer, institutionalize rules) over local patches.
- Explicit probes are rare (9/74); when present they are assumption-probes against the assistant's framing. Presupposition gaps are mostly missing context in terse messages and impressions stated as fact (「…気がします」, 「新規コメントがついた」 when none existed).
- Unclustered turns (14) are mostly automated CI-monitor events, `continue`/`?` nudges, status checks (「Done?」「Koushiのバグはどれだっけ」), and single-session evaluation requests (`c3031e376e17d1ef3f96#4`, `#7`).
