# 申し送り — TASTI 2026 ポスター (T0043)

最終更新: 2026-10-07 / 華扇 (Claude Code)

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

## 1. 現在の状態 — **第一稿 (全 8 ブロック + References)**

| 項目 | 状態 |
| --- | --- |
| ポスターサイズ | **A0 縦 (84.1 × 118.9 cm)**。公式要件 ([docs/poster_requirements.md](docs/poster_requirements.md)) |
| 本体 | `poster.tex` (beamerposter + 自作テーマ `beamerthemetasti2026.sty`)、3 カラム 8 ブロック |
| 図 | 6 枚: Fig. 1 (抄録から流用)、Fig. 2 (5 シーン speedup、`make figures`)、英語化した LT 図 4 枚 |
| 数字 | 抄録と同じ系列ルール + **投稿後の新結果** (5 シーン条件数サーベイ、PR の rebase) を反映 |
| ビルド | `make` → `poster.pdf`。`make preview` で PNG、`make check` で A0 / フォント埋め込み確認 |
| 印刷 | **未**。業者・紙・納期は未定 (→ §3) |
| 登録 | **未** (締切 2026-10-13、Syota さんの手作業) |

### 構成 (3 カラム)

| 列 | ブロック | 中身 | 図 |
| --- | --- | --- | --- |
| 1 | 1 The bottleneck | 43.5% / 設計目標 | — (big number) |
| 1 | 2 The problem | per-pixel WLS、$K \times P$、$n$ の規模、$D^3$ | network + tall_skinny |
| 1 | 3 First attempt: batched QR | CPU 比 **1.43×**、384 万 launches、「形の問題」 | qr_column_sweep |
| 2 | 4 Method | 正規方程式 + batched Cholesky、コード 5 行、**S1 16.5× (3 条件つき)**、実装の要点 | fig1 |
| 2 | 5 Why safe | κ² の警句 → **実測 κ (5 シーン)**、冗長網、誤差バジェット、CholeskyQR2 の射程 | network_redundancy + error_budget |
| 3 | 6 Results: speed | **6,189 s → 170 s (36.4× / 44.4×)**、5 シーン 5.3–93.8×、DEM 6.2×、18 step 完走 | fig2 |
| 3 | 7 Numerical agreement | gate < 1e-5 を最終成果物で 5/5、中間生成物の但し書き | — |
| 3 | 8 Significance & outlook | 数時間→数分、NISAR 外挿、FORMOSAT-9、PR #1490 の現状、Try it、QR ×2 | QR |
| 3 | References | 抄録と同じ 7 件 | — |

### 抄録から**増えた**もの (ポスターで初出)

- **5 シーンの設計行列条件数サーベイ** (mintpy-benchmark `report_condition_number.md`
  @ `d74df50`, 2026-08-06): 無重み κ₂(G) = 11–55、重みつき最悪 ≤ 721、
  fp32 の破綻域 ≈ 4.1e3 に対し余裕 ≥ 5.7×。「なぜ安全か」を実測で言える
- **S1 (16.5×)** を 3 条件つきで block 4 に載せた (抄録では基準統一のため外していた)
- **PR #1490 の現状**: 2026-08-24 に `main` へ rebase、GPU unit test 6/6。まだ OPEN / review 待ち
- **NISAR 外挿** の数字 (1 frame-year: CPU ≈ 4 h → GPU ≈ 7–20 min)。外挿である旨を明記

## 2. 判断の記録

| # | 論点 | 結論 | 根拠 |
| --- | --- | --- | --- |
| 1 | ツールチェーン | **LaTeX beamerposter** | 抄録と同じ TeX Live + rsvg-convert の流れで図を vector のまま使える。印刷向け PDF を直接出せる。HTML (reveal.js) は画面向けで A0 印刷の色・フォント管理に向かない |
| 2 | サイズ | **A0 縦** | 公式要件 "84.1cm (width) x 118.9cm (height)"。orientation の明記はないが幅 < 高さなので縦 |
| 3 | 配色 | 図のパレット (#1a6fb5 / #c8641e) をテーマにも使う | 図 6 枚と本文が 1 セットに見える。LT 図の #0084ff / #e8833a は英語化時に置換済み |
| 4 | S1 (16.5×) | **載せる (block 4)** | 面積があるので 3 条件を添えられる。抄録で外した理由 (基準が 2 つ) はポスターでは「同一 GPU・solver core のみ」と太字で明示して回避 |
| 5 | 5 シーン表 vs チャート | **チャート (Fig. 2)** | ポスターは遠目で読ませる。ただしキャプションで "No size dependence is claimed" と明記 |
| 6 | 条件数の話 | **block 5 として表に出す** | 抄録では裏方だったが、ポスターは立ち話で「float32 で大丈夫?」が最頻出。実測 κ の表が一番強い答え |
| 7 | FORMOSAT-9 | block 8 に 1 句だけ | 抄録と同じ。分解能は書かない。口頭で膨らませる |
| 8 | 写真・変位マップ | **第一稿では入れない** | 地図や干渉縞の写真があると映えるが、出典 (USGS/NASA 画像) の再利用条件と、Galapagos の velocity map を自前で描く手間を見てから決める (→ §3) |

## 3. 次にやること

1. **登録** (2026-10-13 まで): <https://tasti2026.conf.tw/site/mypage53.aspx?pid=127&lang=en&sid=1691>
2. **第一稿のレビュー**: `make preview` で全体を眺め、文字量・余白・フォントサイズを調整
   (`poster.tex` の `scale=1.22` と各 `\includegraphics` の幅)。カラスノエンドウ・ルスダンに
   agmsg で回す (チーム `tasti2026`)
3. **図の追加検討**: Galapagos の velocity map (MintPy fork で `view.py velocity.h5`) を
   block 1 か 6 の目玉にする案。`figures/src/ja/` の `edge_stamp` / `assembly_as_gemm` は
   「Gram 行列の組み立てが行列積 1 発」の説明用。入れるなら英語化して block 4
4. **印刷の段取り** ([docs/poster_requirements.md](docs/poster_requirements.md) §印刷):
   日本で印刷して筒で持参が無難。合成紙 or マット紙、A0、納期 3–5 営業日を見込む。
   遅くとも **2026-11-01 までに `make print`** して入稿
5. **印刷直前チェック**: `make check` + `gh pr view 1490 --repo insarlab/MintPy` で
   block 8 の PR 記述を現状に合わせる (merge されていれば書き換え)
6. **Q&A 準備**: [docs/qa_prep.md](docs/qa_prep.md) を一読。A4 縮刷版を 20 部ほど持参
   (`pdfjam` / `pdftoppm` で縮小) すると立ち話で渡せる

## 4. 運用メモ

- コミットは英語・動詞始まり。通常の Syota さん流
- `*.pdf` は git 管理外。`print/*.pdf` だけ例外 (入稿した版の保全)
- 姉妹 repo の docs は本リポジトリに**コピー**してある (抄録 repo と同じ自己完結方針)。
  向こうを更新してもこちらは自動で追わない
- agmsg のチーム **tasti2026** (華扇 / カラスノエンドウ / ルスダン) をそのまま使う
