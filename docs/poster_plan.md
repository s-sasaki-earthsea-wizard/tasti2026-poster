# ポスター構成計画 — ブロック別の内容・図・数字の系列・判断の記録

`poster.tex` の第一稿 (2026-10-07) の設計書。推敲・更新するときの作業基準。
数字は必ず [results.md](results.md) の系列名で照合すること。

## レイアウト

- **A0 縦、3 カラム** (各 0.305 × 紙幅、ガター 0.0175 × 紙幅)
- headline: タイトル / 著者 / 所属 + メール、右上に Paper No. バッジ
- footline: セッション日時 + 本リポジトリ URL
- 列 1 = 問題、列 2 = 手法、列 3 = 結果と意義。**左上から右下へ読む順に番号 1–8**
- 本文 `scale=1.22` (beamerposter)。`make preview` で見て 1 m 離れて読めなければ上げる

## ブロック別の内容

| # | ブロック | 主張 | 数字 (系列) | 図 |
| --- | --- | --- | --- | --- |
| 1 | The bottleneck | データ増 > 処理能力。`invert_network` が 1 step で 43.5% | 43.5% (`report_baseline.md`) | big number |
| 2 | The problem | per-pixel WLS、$G$ は全ピクセル共通、$n = 10^5$–$10^8$、per-pixel $O(KP^2+P^3/3)$、$D^3$ で伸びる | 3.4 M px (S2) / 3e8 px (NISAR, [compute_scale.md](compute_scale.md)) / 1→3 yr ≈ 29× | `observation_network_example` + `tall_skinny_matrix` |
| 3 | First attempt: batched QR | GPU 移植だけでは **CPU 比 1.43×**。82% が QR 内部、384 万 kernel launches / chunk。「形の問題」 | 1.43× (`report_torch.md` + `report_profile.md`), 3,841,835 (S1 表) | `qr_column_sweep` |
| 4 | Method | 正規方程式 + batched Cholesky。コード 5 行。**S1: 同一 GPU・Fernandina・solver core で 16.5×、step wall 4.49×**。CholeskyQR2 [3,4] は動機の支持まで。実装の要点 5 点 | S1 表 | `fig1_batched_cholesky` |
| 5 | Why safe | κ² の警句は「κ が大きいとき」。**実測 κ₂(G) = 11–55、重みつき最悪 ≤ 721、fp32 破綻 ≈ 4.1e3、余裕 ≥ 5.7×**。冗長網が κ を小さくする。誤差 ≈ 16 µm ≪ mm。破綻する tail = マスクされる画素。CholeskyQR2 も同じ射程 | 条件数サーベイ (`report_condition_number.md` @ `d74df50`), 16 µm (S2 注記) | `network_redundancy_conditioning` + `error_budget` |
| 6 | Results: speed | 全て CPU 比。**6,189 s → 170 s、36.4× step / 44.4× kernel、VRAM 7.6 GB**。5 シーン 5.3–93.8×。DEM 6.2× (overhead 律速)。18 step 完走 | S2 / S3 / `correct_topography` 表 | `fig2_speedup` (`scripts/plot_speedup.py`) |
| 7 | Numerical agreement | gate rms/max\|cpu\| < 1e-5 を**最終成果物**で 5/5。Kuju / SanFranSF のレーダー座標中間生成物の但し書き | S3 数値一致節 | — |
| 8 | Significance & outlook | 数時間→数分。NISAR 1 frame-year 外挿 (CPU ≈ 4 h → GPU ≈ 7–20 min、**extrapolated 明記**)。FORMOSAT-9 は地域文脈 1 句。PR #1490 の現状 (OPEN、2026-08-24 rebase、unit test 6/6)。Try it + QR ×2 | [compute_scale.md](compute_scale.md) / PR 状態 | QR (PR, 本リポジトリ) |
| — | References | 抄録と同じ 7 件、同じ番号 | — | — |

### 抄録にはなくポスターで初出のもの

| 要素 | 出典 | 載せた理由 |
| --- | --- | --- |
| 5 シーン条件数サーベイ (block 5 の表) | mintpy-benchmark `report_condition_number.md` @ `d74df50` (2026-08-06、抄録提出と同日に完成したため抄録には未反映) | 「float32 で大丈夫?」への最も直接的な答え。bound でなく実測 |
| S1 16.5× (block 4) | `report_solver_comparison.md` @ `039d176` | 面積があるので 3 条件を添えられる。「QR→Cholesky の寄与」を同一 GPU で分離した唯一の数字 |
| PR #1490 の rebase (block 8) | `gh pr view 1490 --repo insarlab/MintPy` (2026-10-07 時点: OPEN / REVIEW_REQUIRED、最終更新 2026-08-25) | 抄録の "submitted for upstream review" からの進展 |
| NISAR 外挿の数字 (block 8) | [compute_scale.md](compute_scale.md) | 宇宙系の学会なので NISAR を名指しで定量に踏み込む。**外挿である旨を必ず添える** |

## 図の一覧

| ファイル (`figures/src/`) | 出典 | 状態 | 使用ブロック |
| --- | --- | --- | --- |
| `fig1_batched_cholesky.svg` | 抄録 Fig. 1 (元は LT の `cholesky_batch.svg`) | 英語・パレット済 | 4 |
| `observation_network_example.svg` | LT | 文字なし。title/desc のみ英語化、ノード色を #1a6fb5 に | 2 |
| `tall_skinny_matrix.svg` | LT | **英語化済** (viewBox を 720 幅に拡張) | 2 |
| `qr_column_sweep.svg` | LT | **英語化済** | 3 |
| `network_redundancy_conditioning.svg` | LT (`X` → `G` に変更) | **英語化済** | 5 |
| `error_budget.svg` | LT | **英語化済** | 5 |
| `fig2_speedup.pdf` | `scripts/plot_speedup.py` (S3 系列) | 生成物。フォントをポスター向けに拡大 | 6 |
| `ja/edge_stamp.ja.svg` | LT | **未英語化** (候補) | (4) Gram 組み立ての説明 |
| `ja/assembly_as_gemm.ja.svg` | LT | **未英語化** (候補) | (4) 同上 |

英語化の手順: `<text>` 要素を書き換え、`#0084ff → #1a6fb5`、`#e8833a → #c8641e` に置換、
英語は日本語より長いので `viewBox` の幅を広げるか文を短くする。`make figures` で
`rsvg-convert` が PDF 化する。

## 判断の記録

| # | 論点 | 結論 | 根拠 |
| --- | --- | --- | --- |
| 1 | ツールチェーン | **beamerposter** (LaTeX) | 抄録と同じ TeX Live + `rsvg-convert` の流れ。図を vector のまま使え、印刷向け PDF を直接出せる。`tikzposter` はブロック内レイアウトの自由度が低く、HTML は印刷の色・フォント管理に向かない |
| 2 | 読む順 | 1–8 の番号を見出しに | 3 カラムで Z 字に読ませると迷う。番号があれば立ち話で「3 を見てください」と言える |
| 3 | 5 シーンは表かチャートか | **チャート** | 抄録は表 (規模依存に見えるのを避けるため) だったが、ポスターは遠目で読ませるのでチャート。キャプションで "No size dependence is claimed" と明記して同じ懸念を潰す |
| 4 | 条件数を表に出すか | **出す (block 5)** | 抄録では裏方。ポスターは質問が来る場なので、先回りして実測 κ の表を置く |
| 5 | S1 (16.5×) | **載せる** | 抄録で外した理由は「基準が 2 つあると初読者が混乱」。ポスターでは太字で「Same GPU, same scene, solver core only」と前置きし、CPU 比の数字 (block 6) と列を分けた |
| 6 | コードを載せるか | **5 行だけ** | 「PyTorch で書ける」ことが参入障壁の低さそのもの。`cholesky_ex` の info が rank 落ちの安全弁であることも 1 行で見せられる |
| 7 | FORMOSAT-9 | 1 句 | 抄録と同じ。分解能の数字は出さない。台湾の聴衆へのフックは口頭 |
| 8 | 写真・変位マップ | **第一稿では入れない** | 出典の再利用条件と作図の手間を見てから。候補: Galapagos の `velocity.h5` を `view.py` で描いて block 6 に |
| 9 | References | 抄録と同じ 7 件・同じ番号 | 抄録を読んだ人が番号で辿れる |
| 10 | 公開範囲 | **public** | 抄録 repo が public で、ポスターの中身は抄録の範囲 + 公開済み report。LT からも参照できる |

## 未決事項

- [ ] `scale=1.22` で下端まで収まるか / 余白が空きすぎないか (`make preview` で判定)
- [ ] 変位マップや干渉縞の写真を入れるか (判断 8)
- [ ] `edge_stamp` / `assembly_as_gemm` を英語化して block 4 を図で厚くするか
- [ ] block 8 の PR 記述を印刷直前に更新 (merge されていれば "merged in vX.Y" に)
- [ ] 印刷業者・紙の決定 ([poster_requirements.md](poster_requirements.md) §印刷)
