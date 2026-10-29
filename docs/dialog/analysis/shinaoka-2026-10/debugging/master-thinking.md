# Master Thinking — debugging

- **Source:** Claude Code chat history (2026-07-14 – 2026-10-14, all projects)
- **Confirmed jumps:** 4 (all confirmed by the contributor in a one-at-a-time interview on 2026-10-14)

## 1. Elimination by reference client: Element works, so the bug is Koushi's

- **Ref:** `287ffddba41d5513de7d.json#4`

**Session:** Koushi(matrix-desktop)から送ったメッセージで、鍵ローテーション直後にindex=0の鍵が相手(Element/Element X)に届かず、特定DMで送信鍵が頻繁に切り替わる問題を、複数エージェントで並列調査したセッション。最終的に送信・鍵共有パスをElement Xと同じupstream経路に戻す方針がissue化された。

**Context:** アシスタントは、受信側には送信者へindex=0の再共有を求める経路がなく直せるのは送信側だけだと説明し、続けてrust-sdk調査結果として、vendorされたSDKが自作フォーク(+115コミット、共有パス+4600行)であり、メンバー再読込ごとの鍵破棄など複数のメカニズムを列挙した。結論はまだ『調査中』として保留していた。

**User question:**

> いや，Elementから送信してこの問題が起きないなら，Koushiの問題では．

**Why surprising:** アシスタントは個々のメカニズム(SDK・プロトコル・受信側)を積み上げていたが、ユーザーは対照実験の論理で一気に責任範囲を確定させた。同じSDKを使う参照クライアントで再現しないなら差分(フォークと呼び出し方)が原因、という消去法で、細部の検証を待たずに探索空間を大きく削った。

**Confirmed causal chain (option B):**

```text
アシスタントが受信側やプロトコル仕様の話に広げ続けている + 受信側は直せないという説明が既に出た => 調査が発散している => 自分で直せる側に焦点を戻させる
```

**Self-interview prompt:** 「アシスタントは、受信側には送信者へindex=0の再共有を求める経路がなく直せるのは送信側だけだと説明し、続けてrust…」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？

## 2. Scroll position must be determined by local information

- **Ref:** `c3031e376e17d1ef3f96.json#2`

**Session:** matrix-desktopのタイムラインで、画像やプレビューによるスクロールのガタつきと、過去履歴読み込み時に想定以上に過去へ飛ばされる問題を調査したセッション。Element Web/Element X iOS/Androidの実装比較を経て最小修正のissue化、さらに別ルーム復帰時のジャンプ問題も診断した。

**Context:** アシスタントはTimelineView.tsxを読み、新規行を一律72pxで見積もる高さモデル、推定値ベースのアンカー復元フォールバック、7200px閾値でのプリフェッチ連鎖などを原因として挙げ、同期scrollTop補償・高さ完全予約・行種別推定高さなど4つの修正方向を提示して、どれで進めるか指示を求めた。

**User question:**

> スクロール中は画像がpreviewは凍結しておくべきでは？Element, Element Xの実装を見て
>
> 過去の急に飛ばされるのは，過去へのスクロール距離の計算が狂うせいだよね．過去に大量の履歴が伸びたときに．局所的情報からスクロール距離は決まっているべき

**Why surprising:** アシスタントの提案はいずれも既存のグローバルオフセット設計を補正する局所修正だったが、ユーザーは『スクロール位置は局所的な情報から決まるべき』という設計不変量を提示し、問題を推定誤差の補正から座標系の選び方へと言い換えた。Element調査の結果、3実装とも下端基準・リスト反転などの局所アンカー設計を採っていて、この直観が裏づけられた。

**Confirmed causal chain (option B):**

```text
テンソルネットワークなど数値計算での経験(大域量の差分は誤差が累積し、局所量で定式化すると安定) + 補正を足す提案ばかり出ている => 補正ではなく不変量の設計が必要 => 局所性を要求
```

**Self-interview prompt:** 「アシスタントはTimelineView.tsxを読み、新規行を一律72pxで見積もる高さモデル、推定値ベースのアンカー復…」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？

## 3. Catch performance bugs at the lower layer (strided-rs) with benchmarks and audit rules

- **Ref:** `0990badbf09ea982d0e0.json#2`

**Session:** tenferro-benchmarkを最新tenferroで再計測し、PyTorchに大きく劣る演算の原因を調べたセッション。原因の多くが下位層strided-rsの実装(要素ごとのop分岐、serial reduce、非並列CopyPlan等)にあることがわかり、ベンチマーク追加・修正・監査ルール整備・strided-rs 0.4.3とtenferro v0.7.0のリリースまで進んだ。

**Context:** アシスタントはPyTorchとの性能差をA〜Eに分類して報告した(batched eigh/svdのworkspace query重複、reduce_max/minにexecution contextが渡らない、reduce_max_axis0が汎用ストライドループに落ちる、reverse/slice等が1コアmemcpyで止まる等)。最後に、A〜Eをstrided-rs側とtenferro-rs側に分けてissue化するかを尋ねた。

**User question:**

> 別のagentがCPUka-nerunoのstrided-rs移行時に一部のバグを見つけて修正しました．PR作業を別エージェントがしているので，それらの完了を待って．その後，これらの問題を系統的に直したい．max/minなどのかけているベンチマークをstrided-benchmark, tenferro-benchmarkに追加するのを含めて．strided-rsの段階でバグを検出するべきだと思う．そちらのベンチマーク結果も更新．また，strided, tenferro側に今回見つけた性能バグを防ぐための監査ルール整備をして．

**Why surprising:** アシスタントは見つけたバグを個別issueにする提案にとどまったが、ユーザーは『なぜ上位層のベンチマークで初めて見つかったのか』という検出の失敗に目を向け、下位層で検出できるようにするベンチマーク追加と再発防止の監査ルールまで要求した。実際、strided-rsのベンチ群にerased elementwise/reduce/max/min/CopyPlan系がないことが検出漏れの直接原因と確認された。

**Confirmed causal chain (option A):**

```text
性能バグの多くがstrided-rs由来 + strided-rs単体のベンチにmax/min・reduceがない => 上位のtenferroで初めて露見した => 下位層のベンチを網羅して早期に検出すべき
```

**Self-interview prompt:** 「アシスタントはPyTorchとの性能差をA〜Eに分類して報告した(batched eigh/svdのworkspace …」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？

## 4. Ask whether the upstream fix would be minimal before reporting

- **Ref:** `9cf3238a20c7ab77f334.json#6`

**Session:** Koushiから鍵ローテーション直後に送ったメッセージがElement系で読めない問題(#577)の根本原因を追い、受信側の鍵喪失の解析から、matrix-rust-sdkでOlmのunwedge用m.dummyが送信キューに乗らず永遠に送られないというupstreamバグの発見に至ったセッション。

**Context:** アシスタントは、別エージェントが独立検証できるよう、m.dummyがSessionManagerのマップにinsertされるがOlmMachine::outgoing_requests()がそれを読まないという主張、検証レシピ、反証条件、検証リビジョンを#577に自己完結コメントとして投稿したと報告し、HEADで修正済みの可能性だけは未確認だと述べた。

**User question:**

> バグを直すとしたら修正は最小か？

**Why surprising:** アシスタントは主張の検証方法に集中していたが、ユーザーは修正の規模を問うことで、upstreamへの報告・パッチの説得力と、vendoredフォークに当てる際の安全性という次の段階の判断基準を先取りした。結果として、送信済み処理側は既に配線済みで『取り出して送る』部分だけが欠けている、という設計意図の傍証と約6行の最小修正が得られ、主張の確度も上がった。

**Confirmed causal chain (option A):**

```text
AIで見つけたバグをupstreamに報告するのは気が引ける + 外部メンテナに受け入れてもらう必要がある => 修正が小さく意図が明確なら報告の説得力が増す => 最小性を確認させる
```

**Self-interview prompt:** 「アシスタントは、別エージェントが独立検証できるよう、m.dummyがSessionManagerのマップにinsertさ…」という状況から、あなたは何を手がかりにこの問いへ跳んだのか？ 上の因果連鎖のうち、最初に頭に浮かんだのはどの観察だったか？
