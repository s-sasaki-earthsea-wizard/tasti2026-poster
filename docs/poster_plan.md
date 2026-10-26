# ポスター構成計画 — ブロック別の内容・図・数字の系列・判断の記録

`poster.tex` の第一稿 (2026-10-07) の設計書。推敲・更新するときの作業基準。
数字は必ず [results.md](results.md) の系列名で照合すること。

## レイアウト

- **A0 縦、3 カラム**: 左右の余白 31.75 mm、ガター 26.5 mm、カラム幅は `\tastiColWidth` (≈ 241.5 mm)。
  見た目は「A · Deep-sea masthead」案 (2026-10-26、判断 21)
- headline: ロゴの紺 `#0f2e45` の全幅帯。左にクリームの円に載せたロゴ、中央にタイトル (コロンで
  title / subtitle に分割) と著者・所属、右に Paper No. バッジ。下にオレンジの細線
- ブロック: 箱で囲まず、紺の罫線 + 青の大きな番号 + Source Serif 4 の見出し (`posterblock`)。
  主結果の block 5 だけ淡青の面 (`featureblock`)
- footline: References の 3 段組 (カラムの格子に揃える) + 紺のセッション帯
- 列 1 = 問題 (1–3)、列 2 = 手法と速度 (4–5)、列 3 = 精度と意義 (6–7)。**左上から右下へ読む順に番号 1–7**
- 書体: 本文 Source Sans 3、見出し・大きな数字 Source Serif 4、コード Source Code Pro
  (どれも TeX Live の pdfLaTeX 用 Type 1)。本文 `scale=1.05` (≈ 26 pt)。3 カラムとも References 帯の
  3〜4 cm 手前で揃う

## ブロック別の内容

| # | ブロック | 主張 | 数字 (系列) | 図 |
| --- | --- | --- | --- | --- |
| 1 | The bottleneck | データ増 > 処理能力。`invert_network` が 1 step で 43.5%。keypoint で結論先出し ("This work: 44× on one consumer GeForce GPU, one template option") | 43.5% (`report_baseline.md`) / 44× (S2 internal、block 5 の big number と同じ値) | big number |
| 2 | Why a least-squares inversion? | InSAR 初見の人向けの導入。干渉縞 = 2 時期の差 → 短いペアのネットワーク (辺 > 未知数) → 最小二乗。冗長性が平均化するのは干渉縞ごとのノイズ (大気は日付ごとなので消えない)。**重みがピクセルごと → 分解を共有できない → 数百万の小問題** | 数字なし | `observation_network_example` |
| 3 | The problem | per-pixel WLS、$G$ は全ピクセル共通、$n = 10^5$–$10^8$、per-pixel $O(KP^2+P^3/3)$、$D^3$ で伸びる | 3.4 M px (S2) / 3e8 px (NISAR, [compute_scale.md](compute_scale.md)) / 1→3 yr ≈ 29× | `tall_skinny_matrix` |
| 4 | Method: reformulate for the GPU, don't just port | 冒頭 keypoint「CPU の解法を GPU に移すだけではダメ、GPU に向いた形に定式化し直す」。素朴な移植 (batched QR) は CPU 比 **1.43×**、19,403 px の 1 チャンクで 3,841,835 kernel launches。正規方程式 + batched Cholesky (厳密算術では同じ最小二乗解、GEMM 1 回 + batched Cholesky 1 回、custom GPU code なし)。欠測はゼロ重み = 行削除なので 1 batch のまま。**S1: 同一 GPU・Fernandina で 16.5× (MintPy が報告する step 時間、起動除く)**。step wall 4.49× は載せない。CholeskyQR2 [3,4] は動機の支持まで。コードと実装の要点は載せない | 1.43× (`report_torch.md`、Phase 1) / S1 表 | `fig1_batched_cholesky` |
| 5 | Results: speed | 全て CPU 比。**feature block** (ポスター全体で唯一の淡青の面) に載せる。**主役はグラフ** (S3 の CPU / GPU wall をダンベル + CPU→GPU の矢印、対数軸で矢印の長さ = speedup)。big number は **6,169 s → 139 s、44.4× (S2 internal)、VRAM 7.6 GB**。行ラベルは反転画素数 (Galápagos 1.29 M px で S2 の 3.4 M と区別) と San Francisco の "unweighted"。DEM 6.2× と 18 step 完走の箇条書きは外した | S2 / S3 | `fig2_speedup` (`scripts/plot_speedup.py`) |
| 6 | The accuracy cost: micrometres, against millimetre signals | 旧 block 7 (Numerical agreement) を吸収: 5 シーンとも最終成果物で gate (rms/max\|cpu\| < 1e-5) を通過、を 1 文で。keypoint は「CPU の SVD ベースの解法と比べて κ の二乗の跡は残るが µm 級で、InSAR の他の誤差に埋もれる」。論理 (2026-10-26 改訂): 条件数の意味 = **潰して戻す** (行列は単位円を楕円に潰し、κ = 長軸 / 短軸。解く = 引き伸ばして戻す、まるめのぼけも κ 倍に。短軸がぼけより薄い κ ≳ 1/u では戻らない) → 正規方程式は 2 回潰す (κ(N) = κ(G_w)²) ので fp32 Cholesky は κ(G_w) ≈ u^{-1/2} ≈ 4.1e3 で破綻、教科書的に不利なのは数学的に必然 → 誤差が InSAR の分解能に届かなければ GPU の恩恵が勝つ → 実測。誤差は S2 Galápagos の画素ごと RMS で**中央値 0.06 µm / 最大 16 µm**。旧版の要点: κ² の警句は「κ が大きいとき」。**実測 κ₂(G) = 11–55、重みつき最悪 ≤ 721、fp32 破綻 ≈ 4.1e3、余裕 ≥ 5.7×**。「冗長網が κ を小さくする」は経験則なので**載せない** (判断 24)。誤差 ≈ 16 µm ≪ mm。破綻する tail = マスクされる画素。CholeskyQR2 も同じ射程 | 条件数サーベイ (`report_condition_number.md` @ `d74df50`), 16 µm (S2 注記) | `condition_number_flatten_restore` + `error_budget` |
| 7 | Why it matters: SAR data is multiplying | 2026-10-26 改訂: NISAR・商用小型 SAR コンステレーション・FORMOSAT-9 でデータが増える → $D^3$ と毎回の全網再反転 → 民生 GPU で数時間→数分、HPC なしで定常監視・再処理が可能に。keypoint「SAR アーカイブが増えても民生 GPU なら誰でも時系列解析できる」。PR は "under review" の 1 文、QR 2 つ (Code / Poster and benchmarks)。NISAR 外挿の数字と Try it は外した。旧版: 数時間→数分。NISAR 1 frame-year 外挿 (CPU ≈ 4 h → GPU ≈ 7–20 min、**extrapolated 明記**)。FORMOSAT-9 は地域文脈 1 句。PR #1490 の現状 (OPEN、2026-08-24 rebase、unit test 6/6)。Try it + QR ×2 | [compute_scale.md](compute_scale.md) / PR 状態 | QR (PR, 本リポジトリ) |
| — | References | 抄録と同じ 7 件、同じ番号。footline の上に、カラムの格子に揃えた 3 段組の帯で置く | — | — |

### 抄録にはなくポスターで初出のもの

| 要素 | 出典 | 載せた理由 |
| --- | --- | --- |
| 5 シーン条件数サーベイ (block 6 の表) | mintpy-benchmark `report_condition_number.md` @ `d74df50` (2026-08-06、抄録提出と同日に完成したため抄録には未反映) | 「float32 で大丈夫?」への最も直接的な答え。bound でなく実測 |
| S1 16.5× (block 4) | `report_solver_comparison.md` @ `039d176` | 面積があるので条件 (同一 GPU・Fernandina・MintPy の step 時間) を添えられる。「QR→Cholesky の寄与」を同一 GPU で分離した唯一の数字 |
| PR #1490 (block 7、"under review" の 1 文のみ) | `gh pr view 1490 --repo insarlab/MintPy` (2026-10-07 時点: OPEN / REVIEW_REQUIRED、最終更新 2026-08-25) | 抄録の "submitted for upstream review" からの進展 |
| NISAR 外挿の数字 (**2026-10-26 にポスターから外し Q&A のみ**) | [compute_scale.md](compute_scale.md) | 宇宙系の学会なので NISAR を名指しで定量に踏み込む。**外挿である旨を必ず添える** |

## 図の一覧

| ファイル (`figures/src/`) | 出典 | 状態 | 使用ブロック |
| --- | --- | --- | --- |
| `fig1_batched_cholesky.svg` | 抄録 Fig. 1 (元は LT の `cholesky_batch.svg`) | 英語・パレット済 | 4 |
| `observation_network_example.svg` | LT | ノード色を #1a6fb5 に。時間軸と凡例 (acquisition date / interferogram) を追加 | 2 |
| `tall_skinny_matrix.svg` | LT | **英語化済**。2026-10-26 に viewBox を描画範囲 (`138 0 690 382`) に詰めてカラム幅いっぱいに。同日 "stiffening the network" を "averaging out per-interferogram noise" に (判断 24) | 3 |
| `qr_column_sweep.svg` | LT | **英語化済**。図中の "~40,000" は誤り (S1 の chunk は 19,403 px) | — (block 4 統合で不使用) |
| `condition_number_flatten_restore.svg` | 新規 (2026-10-26) | 2 行 × 3 列 (元の円 → 行列で潰した楕円 → 解いて戻した形)。上段 κ = 4 は戻る (ぼけが ×4)、下段 κ ≳ 1/u は短軸がまるめのぼけより薄く戻らない。ぼけ (橙) は両段で同じ幅 | 6 |
| ~~`network_redundancy_conditioning.svg`~~ | LT | **削除** (2026-10-26)。「網を密にすると κ が下がる」は経験則で、実測の tail も重みが作っていたため (判断 24)。日本語原図は `ja/` に残る | — |
| `error_budget.svg` | LT を 2026-10-19 に描き直し | 実測値 (S2 Galápagos) で再作図: 信号 (画素ごとの時系列 std、中央値) 16 mm、誤差 最悪 16 µm / 中央値 0.06 µm。"Typical InSAR precision ~1 mm" だけは一般的な目安で実測ではない。旧図は大気の下限を 0.1 mm、復元したい変位を 0.1–1 mm に置いていて水準が不正確だった | 6 |
| `fig2_speedup.pdf` | `scripts/plot_speedup.py` (S3 系列) | 生成物。2026-10-26 に speedup の横棒から CPU / GPU wall のダンベル (CPU→GPU 矢印) に変更。同日、矢印を青・太線に、背景を透過に (判断 23) | 5 |
| `ja/edge_stamp.ja.svg` | LT | **未英語化** (候補) | (4) Gram 組み立ての説明 |
| `ja/assembly_as_gemm.ja.svg` | LT | **未英語化** (候補) | (4) 同上 |

英語化の手順: `<text>` 要素を書き換え、`#0084ff → #1a6fb5`、`#e8833a → #c8641e` に置換、
英語は日本語より長いので `viewBox` の幅を広げるか文を短くする。`make figures` で
`rsvg-convert` が PDF 化する。

## 判断の記録

| # | 論点 | 結論 | 根拠 |
| --- | --- | --- | --- |
| 1 | ツールチェーン | **beamerposter** (LaTeX) | 抄録と同じ TeX Live + `rsvg-convert` の流れ。図を vector のまま使え、印刷向け PDF を直接出せる。`tikzposter` はブロック内レイアウトの自由度が低く、HTML は印刷の色・フォント管理に向かない |
| 2 | 読む順 | 1–7 の番号を見出しに | 3 カラムで Z 字に読ませると迷う。番号があれば立ち話で「3 を見てください」と言える |
| 3 | 5 シーンは表かチャートか | **チャート** | 抄録は表 (規模依存に見えるのを避けるため) だったが、ポスターは遠目で読ませるのでチャート。キャプションで "No size dependence is claimed" と明記して同じ懸念を潰す |
| 4 | 条件数を表に出すか | **出す (block 5)** | 抄録では裏方。ポスターは質問が来る場なので、先回りして実測 κ の表を置く |
| 5 | S1 (16.5×) | **載せる** | 抄録で外した理由は「基準が 2 つあると初読者が混乱」。ポスターでは太字で「Same GPU, same scene (Fernandina)」と前置きし、MintPy が報告する step 時間 (起動除く) であることを明記。CPU 比の数字 (block 6) とは列を分けた |
| 6 | コードを載せるか | **載せない** (2026-10-19 改訂、当初は 5 行) | ポスターは何をやってどうなったかのダイジェスト。手法は数式で足りる。「PyTorch で書ける」は "no custom GPU code" の 1 句で言う。chunk・rank 落ち・opt-in などの実装 Tips も外し、[qa_prep.md](qa_prep.md) Q6 / Q13 と block 7 の Try it に回す |
| 7 | FORMOSAT-9 | 1 句 | 抄録と同じ。分解能の数字は出さない。台湾の聴衆へのフックは口頭 |
| 8 | 写真・変位マップ | **第一稿では入れない** | 出典の再利用条件と作図の手間を見てから。候補: Galapagos の `velocity.h5` を `view.py` で描いて block 6 に |
| 9 | References | 抄録と同じ 7 件・同じ番号 | 抄録を読んだ人が番号で辿れる |
| 10 | 公開範囲 | **public** | 抄録 repo が public で、ポスターの中身は抄録の範囲 + 公開済み report。LT からも参照できる |
| 11 | 導入ブロック (2026-10-19) | **block 2 "Why a least-squares inversion?" を新設**、旧 2–8 を 3–9 に | 旧 block 2 は WLS の式から始まり、InSAR を知らない人には「なぜ最小二乗か / なぜ重み付きか」が見えなかった。block 1 (つかみ) の後、問題の形 (block 3) の前に置く |
| 12 | block 1 の地震の扱い (2026-10-19) | 「地震の前後の断層沿いの変形」として書く | 地震時変位は 1 ペアの干渉縞で見るもので、時系列解析の対象は interseismic / postseismic のゆっくりした変形 |
| 13 | block 1 の keypoint (2026-10-19) | "Goal" → "This work:" で結論を先出し | 実装済みなので Goal は弱い。"Achievement" は自画自賛に響く。"default CPU path unchanged" は聴衆よりメンテナ向けなので block 7 の Try it 注記へ移動 |
| 14 | block 3 と 4 の統合 (2026-10-19) | **旧 block 4 (First attempt) を旧 block 5 (Method) に統合**して block 4 "Method: reformulate for the GPU, don't just port" に。全 8 ブロック | 一番大事な考えは「CPU の解法を移すだけではダメで、GPU に向いた形に定式化し直す」。`fig1_batched_cholesky` が QR 経路と正規方程式経路を launch 数つきで並べており、`qr_column_sweep` は重複。82% (profile) は落とした |
| 15 | S1 の step wall 4.49× (2026-10-19) | **載せない** (CLAUDE.md のルールも改訂) | S1 の step wall は両側に約 47 s の起動コスト (NAS 上の fork `.venv` からの torch import) を含み、solver の比較として正当でない。16.5× は MintPy が報告する step 時間 (起動除く) で、solver 単独の値でもないので "solver core" とは書かない ([results.md](results.md) §計測環境の検証) |
| 16 | S3 の CPU 基準 (2026-10-19) | **ポスターには注記しない**。docs と Q&A のみ | S3 は sibling venv (numpy 1.26.4) で CPU ループが Phase 1〜S2 (numpy 2.4.4) より遅い。ただし S3 は CPU・GPU とも同じ環境なので系列内ではフェア |
| 17 | block 5 の組み替え (2026-10-19) | タイトルを「誤差は µm、信号は mm」に。条件数の意味 → 正規方程式の不利 → 実用上の閾値 → 実測、の順 | 「教科書の警告が効かない」はタイトルとして弱い。κ を定義せずに数値条件を並べても読者が追えない。CholeskyQR2 の文と「κ²u 上界の 2〜4 桁下」(S2 では約 1 桁下で不正確) は外して Q&A へ |
| 18 | block 6 のグラフと見出し (2026-10-26) | **グラフを主役に**: CPU / GPU の wall をダンベル + 矢印で並べる。見出しは S2 internal の **44.4× (6,169 → 139 s)**。block 1 の keypoint も 44× に | 対数軸の棒は起点 (1 s) 次第で長さが変わり、棒の長さの比が速度比にならない。ダンベルなら矢印の長さ = speedup。36.4× (step wall) は起動 20–30 s 込みで、S1 の 4.49× を外したのと同じ理屈で見出しにしない。DEM 6.2× と 18 step 完走の箇条書きは外す (Q&A Q4 とキャプション) |
| 19 | 旧 block 7 (Numerical agreement) の扱い (2026-10-26) | **block 5 に吸収して削除**。全 7 ブロック | 主張 (κ² の差は出るが µm 級で InSAR の他の誤差に埋もれる) は block 5 が誤差の図つきで既に言っている。ポスターは図とワンフレーズで伝える場で、テクニカルな文章の箇条書きは不要。レーダー座標の中間生成物の但し書きは Q&A Q14 へ。CPU 側は QR ではなく SVD (`scipy.linalg.lstsq` の既定 `gelsd`) |
| 20 | block 7 の組み替え (2026-10-26) | タイトル "Why it matters: SAR data is multiplying"。データ増の 3 要因 → 民生 GPU の意義を主役に | 一番推すべきは意義。"hours → minutes" の keypoint と NISAR 外挿の箇条書きは他ブロックの繰り返し。PR は未マージなので "under review" だけ (rebase・unit test の詳細は不要)。Try it (template key、install、CPU 経路不変) は実際に動かす人向けの情報で GitHub に任せ、QR だけ残す。旧版の "rapid-response ... earthquakes" も地震時変位の誤解を招くので消えた |
| 21 | 見た目の刷新 (2026-10-26) | **「A · Deep-sea masthead」案** (Design キャンバスで A / B の 2 案を A0 実寸で比較して選択)。テーマを書き直し、ロゴをタイトル部に | Beamer の素のブロックは「スライドの拡大」に見える。ロゴの紺とクリームをヘッダーに使うと図のパレット (青・橙) とも合う。HTML (reveal.js) は不要: TikZ と beamercolorbox で全部組めて、判断 1 の印刷上の理由もそのまま |
| 22 | block 5 と 6 の入れ替え (2026-10-26) | **5 = Results: speed、6 = The accuracy cost** (旧番号の逆)。列 2 = 手法 → 速度、列 3 = 精度 → 意義。本文中の相互参照 (block 1 → 5、block 3 のキャプション → 6) も追随 | 旧配置は列 2 (手法 + 精度) が約 21 cm はみ出し、列 3 に余白があった。速度を手法の直後に置くと「定式化し直した → これだけ速い → 精度の代償は µm」と読める。判断 4・5・17・18 の block 番号は当時のもの |
| 23 | Fig. 2 の強調 (2026-10-26) | 矢印を青系・太線 (5 pt) に、GPU の点を大きく、倍率を紺で大きく。背景は透過 | 主結果なのに灰色の細い矢印で周りの図より弱かった。太字は matplotlib が macOS の HelveticaNeue.ttc の先頭 face しか読めず効かないので、大きさと色で立たせる (Source Sans 3 の OTF は CFF を TrueType と宣言して埋め込むので、印刷の RIP を考えて避けた) |
| 24 | block 6 の概念図と主張 (2026-10-26) | **「潰して戻す」に差し替え**。κ の定義 (楕円の長軸 / 短軸) → 解く = 引き伸ばして戻す、まるめのぼけも最大 κ 倍 → 短軸がぼけより薄い (κ ≳ 1/u) と戻らない → 正規方程式は 2 回潰す (κ²) ので fp32 Cholesky は κ(G_w) ≈ 4.1e3 で破綻。旧図 `network_redundancy_conditioning` と「冗長網が κ を小さくする」(block 3 のキャプション、`tall_skinny_matrix` の "stiffening") は削除 | 旧図の主張は経験則で、実測の κ の tail は網の形ではなく重みのダイナミックレンジが作っていた。新しい筋は特異値分解だけで言える数学的事実。比喩の注意点: (1) 厳密算術では σ_min > 0 なら必ず戻せる。戻らないのは有限精度のぼけがあるから → 図にぼけを描く。(2) 「戻る / 戻らない」は二値でなく、誤差は κ に比例して連続に増える → 上段にも「ぼけが ×4」を描く。(3) 効くのは潰れの**偏り** (長軸 / 短軸) で、一様に縮めても κ は変わらない。(4) ぼけを全方向同じ幅にしたのはノルムでの後退誤差 (≈ u‖G‖) のモデルで、浮動小数点の丸めは本来成分ごとの相対誤差。QR と正規方程式を「κ 対 κ²」で並べる図にはしない (QR でも残差つきの問題では κ² の項が残る)。「最悪の画素は重みが作る」は表のキャプションに入れたが、列 3 の高さの都合で外して Q&A に回した |

## 未決事項

- [x] 下端まで収まるか / 余白が空きすぎないか → `scale=1.05` で 3 カラムとも収まる (判断 21・22)
- [x] block 6 の概念図と「冗長な網が κ を小さくする」の主張の見直し → 「潰して戻す」の図に差し替え、
  冗長網の主張は block 3 のキャプションと `tall_skinny_matrix` からも削除 (判断 24)
- [ ] 変位マップや干渉縞の写真を入れるか (判断 8)
- [ ] `edge_stamp` / `assembly_as_gemm` を英語化して block 4 を図で厚くするか
- [ ] block 7 の PR 記述を印刷直前に更新 (merge されていれば "merged in vX.Y" に)
- [ ] 印刷業者・紙の決定 ([poster_requirements.md](poster_requirements.md) §印刷)
