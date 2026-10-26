# ベンチマーク結果の正典 — ポスターに載せる数字はここから引く

計測の実体は sibling repo
[mintpy-benchmark](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark)
(report は commit SHA 固定 permalink、一覧は [sources.md](sources.md))。
ポスター・スライドに数字を書くときは**必ずこの doc の表と系列名で照合**すること。

> 本ファイルは抄録 repo `tasti2026-abstract/docs/results.md` (2026-08-06 版) のコピーに、
> **§投稿後の追加結果** (条件数サーベイ・DEM 5 シーン・PR の状態) を足したもの。
> 抄録は凍結済みなので、新しい数字はこちらにだけ足す。

## ⚠️ 最重要: 数字の系列を混ぜない

speedup には**測定条件の違う 3 系列**があり、混ぜると誤りになる:

| 系列 | 比較 | 条件 | 代表値 |
| --- | --- | --- | --- |
| **S1: solver 対決** | GPU QR (lstsq) vs GPU Cholesky | Fernandina, SSD, 3-shot mean | **16.50×** (internal) |
| **S2: CPU 置き換え** | CPU lstsq vs GPU Cholesky | Galapagos, 条件統一計測 | **44.4×** internal / **36.4×** step wall |
| **S3: 5 シーン E2E** | CPU vs torch (end-to-end 実行から step wall 抽出) | warm SSD, `/usr/bin/time -v` | **5.32〜93.77×** |

- **16.5× を「CPU 比」と書くのは誤り** (過去に一度取り違えて撤回した前科あり)。
  16.5× は「アルゴリズム置換 (QR→Cholesky) の寄与」を同一 GPU で分離した数字。
- **internal = MintPy が報告する `Time used:`** (Python の起動・トップレベル import を除く。
  スタックの読み込み・重み計算・書き出しは**含む**)。"solver core" ではない。
- **S1 の step wall 4.49× は使わない**。両側に約 47 s の起動コストが乗っている
  (§計測環境の検証)。
- S2 の 44.4× は「GPU 化 + バッチ化 + アルゴリズム変更」の 3 効果込み。
- S3 は E2E 実行からの抽出で S1/S2 と測定方法が違う。**規模依存の議論
  (5〜94× のレンジ) は S3 の表だけで閉じる**こと。
- 「小シーン 16.5× → 大シーン 44.4× と伸びる」という異系列連結も**禁止**。

## S1: 同一 GPU での QR vs Cholesky (Fernandina)

出典: mintpy-benchmark `report_solver_comparison.md` @ `0682c4c`

| Metric | GPU lstsq (QR/gels) | GPU Cholesky | ratio |
| --- | ---: | ---: | ---: |
| internal (MintPy `Time used`、起動除く) | 228.17 s | **13.83 s** | **16.50×** |
| step wall (**使わない**: 起動 ~47 s 込み) | 275.07 s | 61.34 s | 4.49× |
| kernel launches / chunk | 3,841,835 | **57** | **67,400×** |
| kernel time / chunk | 10.41 s | 24.20 ms | 430× |
| 正規化 RMS max (相互差) | — | — | **1.19e-5** |

- abstract の "16.5×" と "3.8M → 57 kernel launches" はこの表。
- **chunk は自動設定の 19,403 px** (14 chunk)。3,841,835 ≈ 19,403 + 2 × 1,882,091 + 58,209
  (`report_solver_comparison.md` §4.3)。旧ポスターの "about 40,000 pixels" と
  `qr_column_sweep.svg` の "~40,000" は誤り (40,000 は chunk sweep の 1 点)。
- 素朴な移植 (Phase 1、batched QR) の **1.43×** も internal 同士の比
  (CPU 367.0 s / torch QR 257.4 s、269,999 px)。wall だと 1.38× (386.09 / 280.39 s)。
  出典 `report_torch.md`。
- RMS 1.19e-5 は**条件数二乗の代償だけ**を分離した実測
  ([numerical_method.md](numerical_method.md) §3)。

## S2: CPU 経路との比較 (Galapagos 大シーン)

出典: mintpy-benchmark `report_large_scene.md` @ `019ceba`

| シーン | ピクセル × ifgs | CPU (lstsq) | GPU (Cholesky) | internal | step wall |
| --- | --- | ---: | ---: | ---: | ---: |
| GalapagosSenDT128 | 3.4M × 475 kept | 6,189 s | **170.06 s** | **44.4×** | **36.4×** |

- internal = MintPy の `Time used` (読み込み・重み計算込み、起動除く) / step wall =
  `--dostep` プロセス全体。**差は起動コスト** (CPU 19.7 s、GPU 31 s。NAS 上の fork
  `.venv` から import するため)。I/O・転送は internal 側に入っている。
- 解いたピクセル数は 3,399,999 (6 box × 578,000 の全画素)、ifgs は 475 (490 中)。
- 画素ごとの時系列の絶対 RMS 差 (CPU 参照比): **中央値 0.065 µm**、p99 0.39 µm、**最大 16.4 µm**。
  参照側の時系列の標準偏差は中央値 16 mm (p99 86 mm)。出典 `reports/galapagos_diff/cpu_vs_torch_r1.json`。
  正規化 RMS は中央値 3.7e-6、p99 2.1e-5、最大 4.3e-4。
- Max RSS 3.73 → 5.80 GiB、VRAM peak 7.6/16 GiB (48%)。

## S3: 5 シーン end-to-end 検証 (「偶然ではない」の裏付け)

出典: [`report_end_to_end_bench.md` @ 0fbf71b](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/0fbf71b/reports/report_end_to_end_bench.md)
/ [PR #1490 フォローアップコメント](https://github.com/insarlab/MintPy/pull/1490)
(2026-05-19 投稿) として公開済み。

| シーン | 処理系 / センサ | px (シーン) | px (反転) | ifgs (K) | dates (D) | 重み | cpu | torch | speedup |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| FernandinaSenDT128 | ISCE2 / S1 (C) | 270 k | 270 k | 288 | 98 | var | 645.12 s | 6.88 s | **93.77×** |
| GalapagosSenDT128 | ISCE2 / S1 (C) | 3.40 M | **1.29 M** | 475 (490 中) | 98 | var | 2976.72 s | 79.40 s | **37.49×** |
| SanFranBaySenD42 | GMTSAR / S1 (C) | 326 k | 234 k | 1297 | 333 | var | 1080.38 s | 17.42 s | **62.02×** |
| KujuAlosAT422F650 | ROI_PAC / ALOS-1 (L) | 226 k | 226 k | 167 | 24 | var | 31.01 s | 4.53 s | **6.85×** |
| SanFranSenDT42 | ARIA / S1 (C) | 1.04 M | 758 k | 505 | 114 | **no** | 58.85 s | 11.07 s | **5.32×** |

- cpu / torch は `/usr/bin/time -v` の step wall (sibling venv はローカル SSD なので起動は ~1 s)。
- **px (反転)** は `invert_network` ログの "number of pixels to invert" の合計。E2E の新規実行では
  `avgSpatialCoh` がゼロの画素がマスクされる。report の "3.40 M" 等はシーン画素数。
- **S3 の CPU 基準は他の系列より遅い** (numpy 1.26.4、§計測環境の検証)。系列内は
  CPU・GPU とも同じ環境なのでフェアだが、S1・S2 と絶対時間を比べないこと。

- **4 処理系 × 2 波長 × 全て Zenodo 公開データ** — abstract の "five-scene
  benchmark spanning four interferometric processors and two radar wavelengths"
  はこの表。この表で主張できるのは **external validity (どの条件でも一貫して速い)**
  であって、**規模依存ではない** (下記)。

### ⚠️ 規模依存は S3 では主張できない (2026-08-06 訂正)

以前ここには「レンジは per-pixel solve コスト ($\propto K D^2$) で構造的に決まる。
Kuju が床、SanFranBay が天井」と書いてあったが、**同じ表の実データと矛盾していた**。
床は SanFranSen の 5.32×、天井は Fernandina の 93.77× が正しい。

speedup と問題規模には相関がない (Spearman 順位相関、2026-10-19 に**実際に反転した
画素数**と使用 ifgs で再計算。シーン画素数で出した旧値は −0.20 / +0.00 / +0.20):

| 規模指標 | speedup との順位相関 |
| --- | ---: |
| 反転したピクセル数 | **−0.10** |
| per-pixel 演算密度 $KP^2 + P^3/3$ | **+0.00** |
| 総演算量 (px × per-pixel) | **+0.20** |

表の中に反例が並んでいる:

- 最小級の **Fernandina (270 k px) が最速の 93.77×**
- 反転画素数が最大の **Galapagos (1.29 M px) は 37.49×** — 最速ではない
- Fernandina の 2.8 倍の画素を解く **SanFranSen (758 k px) が最遅の 5.32×**

→ 「規模が大きいほど恩恵が大きい」と書くと**同じ表に否定される**。抄録・ポスター
いずれでもこの主張はしないこと。

**ばらつきの正体は CPU 側の経路の違い** (2026-10-19 にログで確認)。CPU の 1 画素あたり
時間は Fernandina 2.39 ms・Galapagos 2.31 ms・SanFranBay 4.61 ms (重み付き、画素ごと
ループ) に対し、Kuju 0.137 ms (重み付きだが $P = 23$ と小さい)、SanFranSen 0.078 ms。
**SanFranSen は `weightFunc = no` で、MintPy の CPU 経路が画素ごとのループを通らず
まとめて解く**ため CPU が速く、床の 5.32× になる。Kuju は 1 画素の問題が小さく、GPU 側が
固定費 (読み込み・起動) 律速。GPU 時間は総演算量 (反転画素ベースで 0.02 / 0.81 / 5.25 /
6.16 / 36.33 TFLOP → 4.53 / 6.88 / 11.07 / 79.40 / 17.42 s) には沿わず、むしろ読み込む
スタックの量 (シーン画素 × K、Galapagos が最大) におおむね沿う。

- **規模依存を主張したいときは S2 を使う** (Galapagos 同一シーンの条件統一計測、
  36.4× / 44.4×)。大規模シーンでの効きはこちらで担保できる。
- 参考: 姉妹 repo `vrc-insar-batched-cholesky-LT` のスライドが「行列が大きいほど
  効果は顕著」と言えているのは、5 シーンのうち **3 つ (Kuju / Galapagos / SanFranBay)
  だけを D 昇順に並べている**ため。Fernandina と SanFranSen を外すと単調に見える。
  LT での見せ方であって、**5 シーン全部を出す抄録では使えない**。
- **数値一致**: float32 round-off gate (rms/|cpu|.max < 1e-5) を、ユーザーが
  見る**最終成果物** (velocity.h5・geocoded 出力) で **5/5 通過**。
- 但し書き: Kuju / SanFranSen の 2 シーンはレーダー座標の**中間生成物**で
  rms/scale 1〜7% の発散があるが、near-rank-deficient ピクセル (CPU lstsq の
  最小ノルム解 vs `cholesky_ex` ゼロ埋めの差) に限局し、`maskTempCoh.h5` が
  捨てる領域。Kuju の geocoded velocity はマスク後 **1.38e-7** で通過。
  → 突っ込まれたら「発散が出た場所は品質マスクが先に棄却する場所」と答える。

Zenodo: Fernandina [3952953](https://zenodo.org/records/3952953) /
Galapagos [4743058](https://zenodo.org/records/4743058) /
SanFranBay [15814132](https://zenodo.org/records/15814132) /
Kuju [3952917](https://zenodo.org/records/3952917) /
SanFranSen [4265413](https://zenodo.org/records/4265413)

## 計測環境の検証 (2026-10-19)

ポスターの First attempt と Method のブロック統合時 (2026-10-19) に「同じ Fernandina で S1 の 4.49× と S3 の 93.77× は何が
違うのか」を、元プロジェクト (`/Volumes/EW-NAS-Atoll/Projects/third-party-projects/MintPy`)
の `.claude-notes/` と `benchmark/logs_*` の実ログで突き合わせた結果。

| | Phase 1 (04-26) | S1 (05-03) | S2 (05-06) | S3 (05-17〜18) |
| --- | --- | --- | --- | --- |
| Python 環境 | fork `.venv` (**NAS 上**) | 同左 | 同左 | sibling venv `~/MintPy_bench/.venv` (**ローカル SSD**) |
| numpy / scipy | **2.4.4** / 1.17.1 | 同左 | 同左 | **1.26.4** / 1.17.1 (`--system-site-packages`、apt GDAL のため `numpy<2`) |
| torch / GPU | 2.11.0+cu128 / RTX 5080 | 同左 | 同左 | 同左 |
| 起動 (wall − internal) | 約 20 s | **約 47 s** (harness が torch を先に import) | CPU 19.7 s / GPU 31 s | **約 1 s** |
| Fernandina CPU internal | 367.0 s (1.36 ms/px) | — | — | **644.5 s (2.39 ms/px)** |

わかったこと:

1. **S1 の step wall 4.49× は起動コストの産物**。Cholesky の 61 s のうち 47 s が起動。
   S1 report 自身も「フェアなのは internal の 16.5×」と書いている → ポスターでは使わない。
2. **S3 の CPU が遅いのは numpy 1.26.4 のため**。`ifgram_inversion.py` の CPU 経路は
   Phase 1 (`beca1403`) から S3 時点 (`0df5a241`) まで無変更 (差分は `backend`→`solver`
   の改名と GPU 振り分けの import 先だけ)。scipy は両環境とも 1.17.1 で、scipy は自前の
   OpenBLAS を同梱するので BLAS の差ではない。1 画素ぶんの処理 (重み付き lstsq + 残差 +
   temporal coherence) を模したマイクロベンチ (Ubuntu 機、2026-10-19) で
   **numpy 2.4.4: 1.829 ms/px、numpy 1.26.4: 5.166 ms/px (2.8×)**。実ログの差 (1.76×) と
   向きが一致し、小配列の numpy 呼び出しが多いマイクロベンチでは差が大きく出る。
3. **GPU internal の 13.8 s (S1) → 5.9 s (S3) は未解明**。候補は NAS 上の venv からの
   CUDA ライブラリ遅延ロードが計測区間に入っていたこと、05-03〜05-17 のコード変更。
4. S3 のセッションノート (`2026-05-17_issue21-phase1-2-e2e-harness.md`) にある
   「torch 2.11+cu128 + Blackwell の改善で 93.77× に上がった」は**誤り**。セットアップ
   (04-26) 時点から torch 2.11.0+cu128 / RTX 5080。
5. **系列をまたいで掛け算しない**。1.43× (Phase 1) × 16.5× (S1) ≈ 24× を S3 の 93.77× と
   比べると食い違うが、CPU 基準 (numpy)・起動・GPU internal の 3 つが系列ごとに違う。

## 同じコアの再利用 — `correct_topography` (DEM 残差推定)

出典: mintpy-benchmark `bench/correct-topography-cpu-vs-torch` ブランチの
2 シーン report (HEAD `b4047b0`)

| ステップ | 未知数 | Galapagos CPU | GPU | speedup | 数値 (rms/scale) |
| --- | ---: | ---: | ---: | ---: | --- |
| `correct_topography` | P=4 | 163.83 s | 26.66 s | **6.15×** | delta_z 7.10e-7 / ts_cor 2.08e-8 / ts_res 4.44e-7 |

- 44× に届かないのは per-pixel flops 密度 ~1/1000 で framework overhead 律速
  のため (天井 ~10×) → [numerical_method.md](numerical_method.md) §5。
- abstract では「同じ正規方程式コアが設計行列の差し替えだけで別ステップにも
  適用できた」= 一般性の主張として使う。

## その他 abstract で使っている事実

| 主張 | 出典 |
| --- | --- |
| `invert_network` が baseline の 43.5% を占有 | mintpy-benchmark `report_baseline.md` |
| GPU batched QR (Phase 1) は CPU 比 1.43× 止まり | `report_torch.md` + `report_profile.md` @ `cea7573` |
| 全 18 step の smallbaselineApp が solver=torch で完走 | fork Wiki "GPU Quick Start" + PR #1490 記載の E2E 実測 |
| ハードウェア: RTX 5080 16 GB (コンシューマ) | 全 report 共通の環境欄 |

## permalink 方針

sibling repo (mintpy-benchmark) は将来 private 化の可能性があるため、
**abstract 本文には数値を焼き込み、リンクは張らない** (references は文献のみ)。
発表スライド段階でも commit-pin permalink を補助的に添えるに留める
(upstream PR #1490 で採った Option C と同じ)。

---

## 投稿後の追加結果 (抄録には未反映、ポスターで初出)

### 設計行列の条件数サーベイ (2026-08-06、block 6)

出典: [`report_condition_number.md` @ d74df50](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/d74df50/reports/report_condition_number.md)
(harness: `tools/measure_design_matrix_cond.py`)。
5 シーンの `ifgramStack.h5` から、実際に解いている行列 (`B`、min-norm velocity 定式化) の
2-ノルム条件数を **float64 SVD** で計測。重みは MintPy 既定の `var` (逆位相分散)。
サンプリングは一様 2,000 px + 重みダイナミックレンジ最大の 100 px (tail probe)。

fp32 の単位丸め $u = 2^{-24} \approx 5.96 \times 10^{-8}$。Gram 行列の Cholesky は
$\kappa_2 \approx u^{-1/2} \approx 4.1 \times 10^{3}$ 付近で破綻、正規方程式の forward error は
$\kappa_2^2 u$ でスケール。

| シーン | kept ifgs × dates | κ₂(B) 無重み | κ₂(diag(w)B) median / p99 / **max** | 解析上界 (最悪 px) | 破綻までの余裕 (4.1e3 / κ_max) |
| --- | --- | ---: | --- | ---: | ---: |
| FernandinaSenDT128 | 288 × 98 | 11.0 | 13.5 / 194 / **323** | 894 | **12.7×** |
| GalapagosSenDT128 | 475 × 98 | 12.7 | 13.6 / 148 / **242** | 1075 | **16.9×** |
| KujuAlosAT422F650 | 167 × 24 | 28.6 | 23.4 / 38.7 / **81.1** | 3061 | **50.5×** |
| SanFranBaySenD42 | 1297 × 333 | 55.1 | 55.1 / 200 / **721** | 1.62e4 | **5.7×** |
| SanFranSenDT42 † | 505 × 114 | 51.1 | 51.1 / 1078 / **3764** | 1.05e4 | **1.1×** (†) |

† SanFranSenDT42 は E2E ベンチでは `weightFunc = no` (OLS) で走らせているので、**実際に解いた系は
無重みの B (κ₂ = 51.1、余裕 ≈ 80×)**。重みつきの列は「もし var 重みにしたら」の what-if。
ポスターの表では "(run unweighted)" と注記して余裕 80× を載せた。

- **実際にベンチした構成は全て fp32 破綻域の内側**: 最悪は SanFranBay の κ = 721 (余裕 5.7×)。
  無重みの κ₂(B) はどのシーンも O(10)。
- κ の tail を作るのは**網の形ではなく重みのダイナミックレンジ** (max(w)/min(w) が 6.6e3〜8.6e4)。
  コヒーレンス床 (ε = 5e-2) 近傍と高コヒーレンスの行が混ざる画素で κ ~ 10³。
- **誤差スケールの検算**: 最悪 px の κ²u (Fernandina 6.2e-3、Galapagos 3.5e-3、SanFranBay 3.1e-2)
  に対し、S1 (Fernandina、GPU QR vs GPU Cholesky) の差 1.19e-5 正規化は約 2.7 桁下。ただし
  S2 (Galapagos、CPU vs GPU) の正規化 RMS 最大は 4.3e-4 で、κ²u に対して**約 1 桁下**にとどまる。
  旧ポスターの「2〜4 桁下」は S1 の値だけを見た言い方で、ポスターからは外した (2026-10-19)。
  ポスターは絶対値 (中央値 0.06 µm / 最大 16 µm、S2) で語る。
- **CholeskyQR2 への回答** (report §4): 適用域が同じ (Gram の Cholesky が通ることが前提) なので
  同じ画素で破綻する。利点は Q の直交性で、1 回の LS solve では使わない。tail を硬くするなら
  flag された画素だけ fp64 で再解 (破綻域 6.7e7) か rcond 打ち切り SVD の方が安い。
- **但し書き**: サンプルは kept-ifgram 網の全体。実際の per-pixel 系は無効位相の行を落とすので、
  切断された部分網は rank 落ち (κ = ∞) になりうる。それは `cholesky_ex` の info で拾う母集団で、
  κ の議論の外 (CholeskyQR2 でも同じ)。

### Baseline 18 step の内訳 (2026-10-27、block 1 の横棒)

出典: [`report_baseline.md` @ 0a60cd4](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/0a60cd4/reports/report_baseline.md)
§3。Fernandina、CPU、2026-04-26 (Phase 1 の環境: NAS 上の fork `.venv`、numpy 2.4.4)。
入力データは CIFS 共有 (1 GbE) 上。各 step を `--dostep` で別プロセスとして実行。
抄録の 43.5% と同じ run。ポスターでは**横棒の幅にだけ使い、秒数は載せない**。

| 順 | step | internal (s) | 割合 | 備考 |
| --: | --- | --: | --: | --- |
| 1 | **invert_network** | **218.0** | **43.5%** | ポスターで名指しする唯一の step |
| 2 | load_data | 88.6 | 17.7% | I/O。CIFS 越しで膨らんでいる → ポスターでは名指ししない |
| 3 | modify_network | 43.9 | 8.8% | |
| 4 | residual_RMS | 25.8 | 5.1% | |
| 5 | quick_overview | 25.1 | 5.0% | |
| 6 | reference_date | 17.7 | 3.5% | |
| 7 | deramp | 16.4 | 3.3% | |
| 8 | reference_point | 15.4 | 3.1% | |
| 9 | correct_topography | 14.9 | 3.0% | GPU 化済み (block 5 の補足、Galápagos 6.15×) |
| 10 | google_earth | 9.1 | 1.8% | |
| 11 | geocode | 8.8 | 1.8% | |
| 12 | correct_troposphere | 7.3 | 1.5% | |
| 13 | velocity | 5.1 | 1.0% | |
| 14 | correct_SET | 2.1 | 0.4% | |
| 15 | correct_ionosphere | 1.5 | 0.3% | 設定なし |
| 16 | correct_LOD | 0.9 | 0.2% | Sentinel-1 では skip |
| 17 | correct_unwrap_error | 0.1 | ≈0 | 無効 |
| 18 | hdfeos5 | 0.1 | ≈0 | 無効 |
| | **計** | **500.8** | 100% | |

- **母数は internal の合計**。wall の合計 991.0 s には step ごとの起動 (約 20〜30 s × 18、計 489.5 s) が
  乗っていて、wall で割ると invert_network は 237.85 / 991.0 = **24.0%**。通常の 1 プロセス実行では
  起動は 1 回なので、internal の割合の方が実態に近い。ポスターのキャプションは
  "as reported by MintPy with interpreter start-up excluded"
- **43.5% は控えめな値**: load_data がローカル SSD なら母数が減り、invert_network の割合は上がる
- **この割合に 44× (S2) を掛けて全体の短縮を計算しない**。シーン (Fernandina vs Galápagos)・
  環境が違う系列の掛け算になる。この run の中だけで言えるのは「invert_network が 0 s になっても
  全体は最大 1 / (1 − 0.435) ≈ **1.8×**」(Amdahl の上限)。correct_topography も含めると約 1.9×
- §計測環境の検証 の「Fernandina CPU internal 367.0 s (1.36 ms/px)」とは別の run。画素あたりに直すと
  baseline は 218.0 s / 157,667 有効画素 = 1.38 ms/px で整合する (差は反転した画素数と見られる)

### `correct_topography` 5 シーン (block 5 の補足)

出典: [`dem_error/report_bench_survey.md` @ 3f4b8ea](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/3f4b8ea/reports/dem_error/report_bench_survey.md)。
SSD 統一、fork `60c9e3ac`。

| シーン | px | D | P | CPU (s) | GPU (s) | speedup | VRAM peak (MiB) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kuju | 226k | 24 | 4 | 9.14 | 3.61 | 2.53× | 302 |
| SanFranSF | 260k | 114 | 4 | 9.32 | 3.84 | 2.43× | 1,163 |
| Fernandina | 270k | 98 | 6 | 11.15 | 4.36 | 2.56× | 1,834 |
| SanFranBay | 326k | 333 | 4 | 14.53 | 8.23 | 1.76× | 4,381 |
| Galapagos | 3,400k | 98 | 4 | 163.83 | 26.66 | **6.15×** | 7,758 |

- 数値 gate (rms/scale < 1e-5) は 5/5 通過 (最も厳しい SanFranBay `delta_z` 4.33e-6)。
- ポスターには Galapagos の 6.2× だけを載せ、「per-pixel 演算量が ~1/1000 なので overhead 律速
  (天井 ~10×)」と説明する。小シーンの 1.8–2.6× は聞かれたら答える。

### E2E "GPU-able subtotal" (参考、ポスター未使用)

同じ `report_end_to_end_bench.md` には `invert_network + correct_topography` の合算 speedup
(Fernandina 63.89× / Galapagos 30.84× / SanFranBay 45.86× / Kuju 5.92× / SanFranSF 5.24×) もある。
**ポスターの Fig. 2 は `invert_network` 単独の step wall (S3 表)** で、抄録 Table 1 と同じ系列。
合算値と混ぜないこと。

### PR #1490 の状態 (2026-10-07 確認)

`gh pr view 1490 --repo insarlab/MintPy`:

| 項目 | 値 |
| --- | --- |
| state | **OPEN** / reviewDecision REVIEW_REQUIRED |
| 最終更新 | 2026-08-25 |
| 直近の動き | 2026-08-24 に `main` (`9ede611`) へ rebase、conflict なし、3 commit 不変 (`git range-diff` で確認)。`pre-commit` clean、GPU unit test 6/6 (RTX 5080)。rank 落ち処理の stale コメントを修正 |
| maintainer (yunjunz) の最終コメント | 2026-07-16: ISCE+ short course 後にレビュー再開予定 |
| PR 内 commit | `86a6aea` solver / `53eec83` requirements-gpu / `118fc34` docs gpu.md + installation §2.4 / `086d162` comment fix |

→ ポスター block 7 は "under review; rebased on the current main (August 2026), GPU unit
tests passing" と書いてある。**印刷直前に再確認**し、merge されていれば書き換える。
