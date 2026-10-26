# 申し送り — TASTI 2026 ポスター (T0043)

最終更新: 2026-10-26 / 華扇 (Claude Code)

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

## 1. 現在の状態 — **ブロック別レビュー済み (全 7 ブロック + References)、レイアウト未調整**

| 項目 | 状態 |
| --- | --- |
| ポスターサイズ | **A0 縦 (84.1 × 118.9 cm)**。公式要件 ([docs/poster_requirements.md](docs/poster_requirements.md)) |
| 本体 | `poster.tex` (beamerposter + 自作テーマ `beamerthemetasti2026.sty`)、3 カラム 7 ブロック。**列 2 が約 21 cm はみ出し中** |
| 図 | 6 枚: ネットワーク例、tall-skinny 行列、Fig. 1 (QR vs 正規方程式)、条件数の概念図、誤差バジェット (実測値で再作図)、Fig. 2 (5 シーンの CPU→GPU ダンベル、`make figures`)。`qr_column_sweep` は不使用 |
| 数字 | 抄録と同じ系列ルール + **投稿後の新結果** (5 シーン条件数サーベイ、PR の rebase) を反映 |
| ビルド | `make` → `poster.pdf`。`make preview` で PNG、`make check` で A0 / フォント埋め込み確認 |
| 印刷 | **未**。業者・紙・納期は未定 (→ §3) |
| 登録 | **未** (締切 2026-10-13、Syota さんの手作業) |

### 構成 (3 カラム)

| 列 | ブロック | 中身 | 図 |
| --- | --- | --- | --- |
| 1 | 1 The bottleneck | 43.5%、結論先出しの keypoint ("This work: 44×") | — (big number) |
| 1 | 2 Why a least-squares inversion? | 初見向けの導入: 干渉縞 → ネットワーク → 最小二乗 → ピクセルごとの重み | observation_network_example |
| 1 | 3 The problem | per-pixel WLS、$K \times P$、$n$ の規模、$D^3$ | tall_skinny |
| 2 | 4 Method: reformulate for the GPU | 素朴な移植 (QR) は **1.43×**・384 万 launches → 正規方程式 + batched Cholesky (厳密算術では同じ解、GEMM + batched Cholesky)、**S1 16.5× (条件つき)** | fig1 |
| 2 | 5 The accuracy cost | 条件数の意味 → 正規方程式の不利 → **実測 κ (5 シーン)** → 誤差 0.06 µm (中央値) / 16 µm (最大)、5 シーンとも gate 通過 (旧 block 7 を吸収) | network_redundancy + error_budget |
| 3 | 6 Results: speed | **グラフが主役** (5 シーンの CPU→GPU wall、ダンベル)、見出し **6,169 s → 139 s (44.4×)** | fig2 |
| 3 | 7 Why it matters | NISAR・小型 SAR・FORMOSAT-9 でデータ増 → 民生 GPU の意義、PR は under review、QR ×2 | QR |
| 3 | References | 抄録と同じ 7 件 | — |

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
| 6 | 条件数の話 | **block 5 として表に出す** | 抄録では裏方だったが、ポスターは立ち話で「float32 で大丈夫?」が最頻出。実測 κ の表が一番強い答え |
| 7 | FORMOSAT-9 | block 7 に 1 句だけ | 抄録と同じ。分解能は書かない。口頭で膨らませる |
| 8 | 写真・変位マップ | **第一稿では入れない** | 地図や干渉縞の写真があると映えるが、出典 (USGS/NASA 画像) の再利用条件と、Galapagos の velocity map を自前で描く手間を見てから決める (→ §3) |

## 3. 次にやること

1. **登録** (2026-10-13 まで): <https://tasti2026.conf.tw/site/mypage53.aspx?pid=127&lang=en&sid=1691>
2. **レイアウト調整** (次の作業): 列 2 (block 4 + 5) が約 21 cm はみ出し、列 3 は下に余白。
   案: 並びを「手法 → 速度 → 精度 → 意義」にして精度のブロックを列 3 へ。そのうえで
   `scale=1.15` と各 `\includegraphics` の幅を詰める。ロゴ (`figures/images/earthsea-wizard-logo.png`、
   Syota さんが追加) の反映もここで。仕上がったらカラスノエンドウ・ルスダンに agmsg で回す
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
