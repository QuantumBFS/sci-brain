# Master Thinking — code-review

- **Source:** Claude Code chat history (2026-07-14 – 2026-10-14, all projects)
- **Confirmed jumps:** 5 (all confirmed by the contributor in a one-at-a-time interview on 2026-10-14)

## 1. Question whether the optimization queue is needed at all

- **Ref:** `df293cba53292827259f.json#30`

**Session:** tenferro-rs の PR #1453 から umbrella #1489 までを71ターンかけてレビューしたセッション。設計の柔軟性、性能回帰、AD 移行、最適化キューの是非、ドキュメント、ベンチマーク結果まで扱った。

**Context:** アシスタントは grad() の in-place 累積に関する #1483 の CoW 化を説明した。続けて、同じ aliasing の危険が #1479・#1480・#1284 と inplace-indexing 設計にも及ぶことを横断的に示し、一意性証明を必須とする横断ルールと debug 限定の version counter を提案して、#1489 への投稿を打診していた。

**User question:**

> そもそもこれらの最適化は本当に必要なのか？

**Why surprising:** アシスタントは「どう安全に実装するか」を詰める流れにあり、投稿の可否を尋ねていた。ユーザーはそれに答えず、最適化キュー全体の前提そのものを問い直した。結果として、キューがプロファイル数値ではなく静的なコード読解から生まれていたことが明らかになり、「数値に裏付けられていない最適化は禁止」という恒久方針と、JAX 型の in-place 意味論の採用につながった。

**Confirmed causal chain (option A):**

```text
aliasing リスクが複数 issue に横断的に広がっている + 安全化の機構を足すほど複雑さが増す => リスクとコストに見合う便益があるか自体を問うべき => 必要性を先に検証する
```

**Self-interview prompt:** 「アシスタントは grad() の in-place 累積に関する #1483 の CoW 化を説明した。続けて、同じ a…」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？

## 2. Generalize a cache-key lesson into an org-wide agent rule

- **Ref:** `71aa54de0ab4dbcb1952.json#8`

**Session:** tensor4all-rs の issue #626（treeaci の LRU キャッシュ提案）を検討したセッション。キー設計、TT 版の改善、ベンチマークによるゲートを決め、実装は他者に任せた。

**Context:** アシスタントは、自分で走らせていた実装エージェントと worktree を停止・削除した。#626 への設計コメントと TT 側改善 issue #627 を投稿済みであること、役割分担をメモリに保存したことを報告し、PR が来たらレビューとベンチ判定を引き受けると締めくくっていた。

**User question:**

> パフォーマンスに関するルールにVector{Int}をそのままkeyにすべきではないと入れるべきですね．メモリサイズ，Hash化速度が問題になる．全体のagent rulesに実装してPRmerge https://github.com/tensor4all/tensor4all-agent-rules/agents?author=shinaoka

**Why surprising:** セッションは区切りを迎えて終わりかけていた。そこでユーザーは、一つの issue で得た教訓（部分ベクトルをキーにしない）を、組織全体のエージェント規則へ昇格させた。アシスタントからの促しはなかった。結果として、common・Rust・Julia の3ファイルに規則を追加する PR #12 がマージされた。

**Confirmed causal chain (option A):**

```text
同じキー設計ミスを TT 版でも見てきた + 実装は今後 AI エージェントが担う => 個別レビューでは再発を防げない => 規則として事前に埋め込む
```

**Self-interview prompt:** 「アシスタントは、自分で走らせていた実装エージェントと worktree を停止・削除した。#626 への設計コメントと …」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？

## 3. Separate thread count from core binding

- **Ref:** `c16f7571ee148c29b7e3.json#32`

**Session:** tenferro-rs #1433（実行エンジンとプロバイダ設計）が長期的に正しい方向かを62ターンかけて評価したセッション。NUMA、スレッド budget、BLAS 各種の制御能力、eager のオーバーヘッドまで掘り下げた。

**Context:** アシスタントは #1433 の粒度表に ArmPL _mp・ArmPL serial・NVPL の3行を追加した。あわせて、serial ビルドは自明に適格とする target policy の拡張を報告していた。議論はスレッド「数」の局所制御が可能かどうかに集中していた。

**User question:**

> OpenBLAS pthreadはnest parallelismをどう制御可能なんだ？スレッド数をlocalに設定できるのはいいけど，CPUコアにどうバインドするのかがわからない

**Why surprising:** それまでの契約は「スレッド数を局所的に設定できるか」を適格性の軸にしていた。ユーザーは、数を制御できることと、どのコアで走るかという配置を制御できることは別問題だと見抜いた。結果として、OpenBLAS は配置を制御できず並列ジョブもロックで直列化されること、budget=1 なら健全であることが判明し、capability を2軸に分ける契約修正につながった。

**Confirmed causal chain (option A):**

```text
NUMA ドメインごとの実行を設計目標にしている + スレッド数だけではメモリ局所性が保証されない => 配置（affinity）も制御軸に入れる必要がある => 契約の穴を指摘する
```

**Self-interview prompt:** 「アシスタントは #1433 の粒度表に ArmPL _mp・ArmPL serial・NVPL の3行を追加した。あわせ…」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？

## 4. Introduce simple-NN differentiation as the goal that fixes the layering

- **Ref:** `20df817909780308c573.json#10`

**Session:** tenferro-rs #1938 を、人間がコードを書かない AI 時代の API という観点で監査したセッション。FFI のオーバーヘッドや「巨大テンソルライブラリは必要か」という問いを経て、カーネル分離とモジュラー構造の方針を決めた。

**Context:** アシスタントは AD の複雑さを「AD 固有で避けられないもの」と「普通のテンソルに漏れている避けられるもの」に分けた。AD は限定された演算集合に対する opt-in 層だと明記するよう提案し、tensor4all-rs で AD が必要な用途は何かを尋ねていた。

**User question:**

> tensor4all-rsだけではないからね．簡易NNを微分することも最終的な目標だ．さすがにAIにベタ書きさせるのは大変だからね．やはりnon-AD用途でシンプルに使えるモジュラー構造を目指すべきだ．カーネル群はtenferro-rs外に再利用できる形で取り出す

**Why surprising:** アシスタントは tensor4all-rs の用途に絞って AD の対象演算を列挙しようとしていた。ユーザーはその前提を外し、簡易 NN の微分という将来目標を持ち込んだ。そのうえで「AI にベタ書きさせるのは大変」という AI 時代の開発コストの観点から、non-AD 用途のシンプルさとカーネルの外部化という層構造の方針を一気に決めた。結果として、カーネル・薄いテンソル・実行・AD の4層一方向依存の設計が #1938 への要求になった。

**Confirmed causal chain (option A):**

```text
AD の対象を TN 用途に絞ると将来の NN 微分で破綻する + AI に AD を手書きさせるのは高コスト => AD 基盤は必要だが非 AD 利用者に漏らしてはいけない => opt-in 層とモジュラー構造にする
```

**Self-interview prompt:** 「アシスタントは AD の複雑さを「AD 固有で避けられないもの」と「普通のテンソルに漏れている避けられるもの」に分けた。…」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？

## 5. Spot the missing human-facing view documentation

- **Ref:** `29c0b4d18d6a1cbf04fa.json#2`

**Session:** tenferro-rs #1555（ストレージ所有権と view 設計）を ndarray/mdarray の issue を参照してレビューしたセッション。指摘の返信を確認し、Phase 1–7 の設計書作成まで進めた。

**Context:** アシスタントは、マルチ GPU と単一配列への複数ビューに需要があることを ndarray の issue 群から示した。新しいビュー機構は不要で owned パーティションだけが穴であること、長期のマルチ GPU に向けた3つの文言上の布石（語彙の中立化、span-scoped な timeline クエリ、sharding の合成層固定）を報告していた。

**User question:**

> viewに関するドキュメントがないのでは？少なくとも人間が見るonline docからある？

**Why surprising:** 設計レビューは型と所有権の議論に終始しており、ドキュメントには触れていなかった。ユーザーは、設計がどれだけ正しくても利用者が理解できなければ意味がないという別の軸を持ち込んだ。調査の結果、公開サイト83ページに view の体系的なユーザー向け文書が存在しないことが確認された。直後に「実装完了の要件にドキュメントを追加」という完了定義の変更につながり、別セッションでも online doc の追随監査が繰り返された。

**Confirmed causal chain (option A):**

```text
view は所有・借用・エイリアスなど誤用しやすい概念 + 設計が複雑になるほど利用者の理解コストが上がる => 設計レビューと同時に人間向けの説明の有無を確認すべき => ドキュメントの欠落を疑う
```

**Self-interview prompt:** 「アシスタントは、マルチ GPU と単一配列への複数ビューに需要があることを ndarray の issue 群から示した…」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？
