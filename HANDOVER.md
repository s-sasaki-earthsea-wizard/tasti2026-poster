# 申し送り — TASTI 2026 ポスター (T0043)

最終更新: 2026-10-26 (夜) / 華扇 (Claude Code)

> 数字を触るときは [docs/results.md](docs/results.md) (系列混同の禁止事項) を、
> 構成を触るときは [docs/poster_plan.md](docs/poster_plan.md) を先に読むこと。
> 抄録リポジトリの表現上の注意 9 項目 (特に **CholeskyQR2 の引用範囲** と
> **規模依存を主張しない**) はポスターでも有効。

## 0. 経緯

- 2026-08-06: 抄録を提出 ([tasti2026-abstract](https://github.com/s-sasaki-earthsea-wizard/tasti2026-abstract))。
  内容はその時点で凍結。
- **2026-10-07: 受理メール受信。Paper No. T0043、ポスター発表**
  (トピック 0201 Earth Observation and Remote Sensing)。
- 2026-10-07: 本リポジトリを立ち上げ、ポスターの第一稿 (全ブロック埋め済み) を作成。
- 2026-10-19〜26: Syota さんとブロック別レビュー。導入ブロック新設、手法と精度のブロック統合、
  意義のブロックの組み替えで **全 7 ブロック**に。元プロジェクトのログで数字を再監査し、
  計測環境の違い (numpy・起動コスト・反転画素数) を [docs/results.md](docs/results.md) §計測環境の検証 に記録。
- 2026-10-26: **見た目を刷新**。Design キャンバス (<https://claude.ai/artifact/PV2bEMCVCxWzZKJtp9RBXA>、非公開) で
  A0 実寸の 2 案を比較して「A · Deep-sea masthead」を採用し、テーマを書き直した。block 5 と 6 を入れ替えて
  列 2 のはみ出しを解消。

## 1. 現在の状態 — **レイアウト・見た目は調整済み。block 6 の内容 (概念図と主張) が未決**

| 項目 | 状態 |
| --- | --- |
| ポスターサイズ | **A0 縦 (84.1 × 118.9 cm)**。公式要件 ([docs/poster_requirements.md](docs/poster_requirements.md)) |
| 本体 | `poster.tex` (beamerposter + 自作テーマ `beamerthemetasti2026.sty`)、3 カラム 7 ブロック + References 帯。本文 `scale=1.05` (≈ 26 pt) で 3 カラムとも収まる |
| 図 | 6 枚: ネットワーク例、tall-skinny 行列、Fig. 1 (QR vs 正規方程式)、条件数の概念図、誤差バジェット (実測値で再作図)、Fig. 2 (5 シーンの CPU→GPU ダンベル、`make figures`)。`qr_column_sweep` は不使用 |
| 数字 | 抄録と同じ系列ルール + **投稿後の新結果** (5 シーン条件数サーベイ、PR の rebase) を反映 |
| ビルド | `make` → `poster.pdf`。`make preview` で PNG、`make check` で A0 / フォント埋め込み確認 |
| 印刷 | **未**。業者・紙・納期は未定 (→ §3) |
| 登録 | **未** (締切 2026-10-13、Syota さんの手作業) |

### 構成 (3 カラム)

| 列 | ブロック | 中身 | 図 |
| --- | --- | --- | --- |
| 1 | 1 The bottleneck | 43.5%、結論先出しの keypoint ("This work: 44×"、block 5 を参照) | — (big number) |
| 1 | 2 Why a least-squares inversion? | 初見向けの導入: 干渉縞 → ネットワーク → 最小二乗 → ピクセルごとの重み | observation_network_example |
| 1 | 3 The problem | per-pixel WLS、$K \times P$、$n$ の規模、$D^3$ | tall_skinny (viewBox を描画範囲に詰めてカラム幅いっぱい) |
| 2 | 4 Method: reformulate for the GPU | 素朴な移植 (QR) は **1.43×**・384 万 launches → 正規方程式 + batched Cholesky (厳密算術では同じ解、GEMM + batched Cholesky)、**S1 16.5× (条件つき)** | fig1 |
| 2 | 5 Results: speed | **グラフが主役** (5 シーンの CPU→GPU wall、ダンベル)、見出し **6,169 s → 139 s (44.4×)**。唯一の淡青の面 (`featureblock`) | fig2 (矢印を青・太線に) |
| 3 | 6 The accuracy cost | 条件数の意味 → 正規方程式の不利 → **実測 κ (5 シーン)** → 誤差 0.06 µm (中央値) / 16 µm (最大)、5 シーンとも gate 通過 (旧 block 7 を吸収) | network_redundancy (**見直し予定**) + error_budget |
| 3 | 7 Why it matters | NISAR・小型 SAR・FORMOSAT-9 でデータ増 → 民生 GPU の意義、PR は under review、QR ×2 | QR |
| 全幅 | References | 抄録と同じ 7 件。footline の上にカラムの格子に揃えた 3 段組 | — |

### 抄録から**増えた**もの (ポスターで初出)

- **5 シーンの設計行列条件数サーベイ** (mintpy-benchmark `report_condition_number.md`
  @ `d74df50`, 2026-08-06): 無重み κ₂(G) = 11–55、重みつき最悪 ≤ 721、
  fp32 の破綻域 ≈ 4.1e3 に対し余裕 ≥ 5.7×。「なぜ安全か」を実測で言える
- **S1 (16.5×)** を条件つき (同一 GPU・Fernandina・MintPy の step 時間) で block 4 に載せた (抄録では基準統一のため外していた)。step wall 4.49× は起動コスト込みなので載せない
- **PR #1490 の現状**: 2026-08-24 に `main` へ rebase、GPU unit test 6/6。まだ OPEN / review 待ち
- **NISAR 外挿** の数字 (1 frame-year: CPU ≈ 4 h → GPU ≈ 5–20 min) は 2026-10-26 にポスターから外し、Q&A のみ

## 2. 判断の記録

| # | 論点 | 結論 | 根拠 |
| --- | --- | --- | --- |
| 1 | ツールチェーン | **LaTeX beamerposter** | 抄録と同じ TeX Live + rsvg-convert の流れで図を vector のまま使える。印刷向け PDF を直接出せる。HTML (reveal.js) は画面向けで A0 印刷の色・フォント管理に向かない |
| 2 | サイズ | **A0 縦** | 公式要件 "84.1cm (width) x 118.9cm (height)"。orientation の明記はないが幅 < 高さなので縦 |
| 3 | 配色 | 図のパレット (#1a6fb5 / #c8641e) をテーマにも使う | 図 6 枚と本文が 1 セットに見える。LT 図の #0084ff / #e8833a は英語化時に置換済み |
| 4 | S1 (16.5×) | **載せる (block 4)** | 面積があるので 3 条件を添えられる。抄録で外した理由 (基準が 2 つ) はポスターでは「同一 GPU・同一シーン」と太字で明示して回避。step wall 4.49× は起動コスト込みなので載せない |
| 5 | 5 シーン表 vs チャート | **チャート (Fig. 2)** | ポスターは遠目で読ませる。ただしキャプションで "No size dependence is claimed" と明記 |
| 6 | 条件数の話 | **block 6 として表に出す** (当初 block 5、2026-10-26 の入れ替えで 6) | 抄録では裏方だったが、ポスターは立ち話で「float32 で大丈夫?」が最頻出。実測 κ の表が一番強い答え |
| 7 | FORMOSAT-9 | block 7 に 1 句だけ | 抄録と同じ。分解能は書かない。口頭で膨らませる |
| 8 | 写真・変位マップ | **第一稿では入れない** | 地図や干渉縞の写真があると映えるが、出典 (USGS/NASA 画像) の再利用条件と、Galapagos の velocity map を自前で描く手間を見てから決める (→ §3) |
| 9 | 見た目 (2026-10-26) | **「A · Deep-sea masthead」**: ロゴの紺の全幅ヘッダー + クリームの円にロゴ、罫線で区切る開いたブロック、主結果 (block 5) だけ淡青の面、References は格子に揃えた帯 | Design キャンバスで B (白ヘッダー + 角丸カード) と A0 実寸で比較。詳細は [docs/poster_plan.md](docs/poster_plan.md) 判断 21–23 |

## 3. 次にやること

1. **登録** (2026-10-13 まで): <https://tasti2026.conf.tw/site/mypage53.aspx?pid=127&lang=en&sid=1691>
2. **block 6 の内容の見直し** (次の作業、別セッション): 必要な情報は §5 にまとめた。
   仕上がったらカラスノエンドウ・ルスダンに agmsg で回す
3. **図の追加検討**: Galapagos の velocity map (MintPy fork で `view.py velocity.h5`) を
   block 1 か 6 の目玉にする案。`figures/src/ja/` の `edge_stamp` / `assembly_as_gemm` は
   「Gram 行列の組み立てが行列積 1 発」の説明用。入れるなら英語化して block 4
4. **印刷の段取り** ([docs/poster_requirements.md](docs/poster_requirements.md) §印刷):
   日本で印刷して筒で持参が無難。合成紙 or マット紙、A0、納期 3–5 営業日を見込む。
   遅くとも **2026-11-01 までに `make print`** して入稿
5. **印刷直前チェック**: `make check` + `gh pr view 1490 --repo insarlab/MintPy` で
   block 7 の PR 記述を現状に合わせる (merge されていれば書き換え)
6. **Q&A 準備**: [docs/qa_prep.md](docs/qa_prep.md) を一読。A4 縮刷版を 20 部ほど持参
   (`pdfjam` / `pdftoppm` で縮小) すると立ち話で渡せる

## 4. 運用メモ

- コミットは英語・動詞始まり。通常の Syota さん流
- `*.pdf` は git 管理外。`print/*.pdf` だけ例外 (入稿した版の保全)
- 姉妹 repo の docs は本リポジトリに**コピー**してある (抄録 repo と同じ自己完結方針)。
  向こうを更新してもこちらは自動で追わない
- agmsg のチーム **tasti2026** (華扇 / カラスノエンドウ / ルスダン) をそのまま使う

## 5. block 6 の見直しに必要な情報 (次セッション用)

### 指摘 (Syota さん、2026-10-26)

- 概念図の「網を密にすると κ が下がる」は**経験則**。強く主張しない
- 軸にするのは数学的事実: κ₂ = σ_max / σ_min は単位球を $G$ で写した楕円の長軸 / 短軸。
  **κ が大きい = 楕円が極端に細長い = 逆変換で短軸方向を割り戻すときに丸め誤差が増幅され、桁落ちで戻しきれない**
- だから正規方程式 (κ を二乗) が不利なのは数学的に必然 → それでも**実用上は問題にならない桁**、に繋ぐ

### 触る場所

| 場所 | 今の内容 |
| --- | --- |
| `poster.tex` の `\begin{posterblock}{6}` (先頭のコメントから) | κ の定義 → 概念図 (`0.85\linewidth`) とキャプション "A redundant SBAS network supports every direction and keeps κ small." → κ² の段落 → 表 → 誤差の段落 → `error_budget` → keypoint |
| `figures/src/network_redundancy_conditioning.svg` | 左 "Sparse network (chain) / few edges → weak directions remain"、右 "Redundant network / many edges → every direction is supported"、"add edges" の矢印、細長い楕円 (κ large) → 円 (κ small) |
| `poster.tex` block 3 のキャプション | "The 191 redundant rows are what make the network well-conditioned (block 6)." |
| `figures/src/tall_skinny_matrix.svg` | "averaging noise, stiffening the network" |
| `docs/poster_plan.md` の block 6 の行、`docs/numerical_method.md` §条件数の但し書き 1 | 「冗長網が κ を小さくする」「冗長網で接続が担保される」 |

### 使える事実と数字 (正典: [docs/results.md](docs/results.md) §設計行列の条件数サーベイ)

- 計測: float64 SVD、1 シーンあたり 2,100 px。fp32 の $u = 2^{-24} \approx 5.96 \times 10^{-8}$
- Gram の Cholesky は $\kappa(G_w) \approx u^{-1/2} \approx 4.1 \times 10^3$ (つまり $\kappa(N) \approx u^{-1}$) で破綻。
  正規方程式の forward error は $\kappa^2 u$ でスケール
- 無重み κ₂(G) = 11.0–55.1。実際に解いた系の最悪は 721 (San Francisco Bay、余裕 5.7×)。
  San Francisco は無重みで実行 (51.1、余裕 80×)
- **κ の tail を作るのは網の形ではなく重みのダイナミックレンジ** (max(w)/min(w) = 6.6e3〜8.6e4)。
  実測データ自体が「網の密さ → κ」を主役にしない根拠になる
- 誤差: S2 Galápagos の画素ごと RMS で中央値 0.06 µm / 最大 16 µm。5 シーンとも gate (< 1e-5) を通過
- 検算: 最悪 px の κ²u (Fernandina 6.2e-3、Galápagos 3.5e-3、San Francisco Bay 3.1e-2) に対し、S2 の正規化 RMS 最大
  4.3e-4 は**約 1 桁下**。「2〜4 桁下」とは言わない

### 注意

- 「QR / SVD なら誤差 ∝ κ、正規方程式なら ∝ κ²」は**残差が小さい問題での簡略化**。最小二乗の摂動論では
  QR でも κ² × (残差の大きさ) の項が残る (Golub & Van Loan §5.3、Higham Ch. 20)。今の文
  "That is why textbooks solve least squares with QR or SVD" は安全だけど、図や文で κ と κ² を対比させて言い切らない
- CholeskyQR2 [3,4] の引用は「Gram + Cholesky は確立した戦略で、κ² の代償は既知」まで ([docs/qa_prep.md](docs/qa_prep.md) Q2)
- 図を描き直すなら: `<text>` に英語を直書き、パレットは `#1a6fb5` / `#c8641e`、書体は Helvetica Neue (他の図と同じ)。
  `make figures` で PDF 化。今の図は幅 205 mm × 高さ約 108 mm
- 列 3 は References 帯の 3〜4 cm 手前で終わっている。図や文が伸びるならその範囲に収める
  (超えたら `error_budget` の幅 `0.8\linewidth` を詰める)。毎回 `make preview` で確認
