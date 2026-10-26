# ポスターセッション想定問答

立ち話で聞かれそうな順。英語の答えは**短く言い切り、詳細は図を指す**。
数字は [results.md](results.md)、数理は [numerical_method.md](numerical_method.md) が正。

## 1. "Is float32 really enough? Normal equations square the condition number."

> Yes, and we measured rather than assumed. The unweighted SBAS design matrix has
> κ₂ between 11 and 55 on all five scenes; even the worst weighted pixel we sampled
> is 721, while float32 Cholesky only breaks down near 4,000. Against the CPU
> reference on the large scene, the per-pixel RMS difference is 0.06 µm for the
> median pixel and 16 µm for the worst, against millimetre-level InSAR
> precision. (block 6)

- 「速度のために精度を捨てた」ではなく「この問題の条件数では float32 で十分だと
  見積もった上で選んだ」が正しい言い方。
- 将来 κ の大きい網に当たったら fp64 (破綻域が 6.7e7 まで上がる) か QR/SVD 経路に逃がせる設計。

## 1a. "Which pixels are the badly conditioned ones? Does a denser network help?"

> The network itself is benign: unweighted κ is 11 to 55. The tail comes from the
> weights. The worst pixels mix strong interferograms with ones near the
> coherence floor, so their weights differ by roughly a factor of 10⁴. Those
> are low-coherence pixels that the temporal-coherence mask removes anyway.

- 正典: [results.md](results.md) §設計行列の条件数サーベイ (max(w)/min(w) = 6.6e3〜8.6e4)。
  ポスターの表のキャプションに入れかけたが、列 3 の高さの都合で口頭に回した。
- 「網を密にすると κ が下がる」は**経験則**として言うに留める。ポスターの旧概念図はこれを主張していたが
  2026-10-26 に「潰して戻す」の図に差し替えた ([poster_plan.md](poster_plan.md) 判断 24)。
- 専門家から「浮動小数点の丸めは成分ごとの相対誤差なのに、ぼけを全方向同じ幅に描くのはおかしい」と
  来たら: 図はノルムでの後退誤差 (計算結果は $\lVert\delta G\rVert \lesssim u\lVert G\rVert$ だけずれた
  行列の厳密解) のモデル。細い方向が座標軸と斜めなら、短軸の情報は大きな数どうしの差 (桁落ち) に
  しか残らないので、実際に失われるのは長軸の $u$ 倍の大きさ。

## 1b. "What are the weights, exactly? And doesn't MintPy solve for velocities?"

> By default MintPy weights each interferogram by the inverse of the phase
> variance predicted from its coherence and number of looks, so noisy
> interferograms count less: textbook weighted least squares. Block 2 draws the
> equations in displacement form for readability; MintPy actually solves for the
> velocity in each interval between consecutive dates and sums them up, which
> gives the same least-squares solution for a connected network. (block 2)

- 実装 (upstream `cc44148`): `weightFunc = auto → var` ([smallbaselineApp.cfg L175](https://github.com/insarlab/MintPy/blob/cc441486e3ca68212dec5deb5b0adf29abaa04f7/src/mintpy/defaults/smallbaselineApp.cfg#L175))。
  `coherence2weight` が $w = 1/\sigma_\phi^2(\gamma, L)$ を分布散乱体の位相 PDF (Tough et al. 1995) から計算
  ([decorrelation.py L337–376](https://github.com/insarlab/MintPy/blob/cc441486e3ca68212dec5deb5b0adf29abaa04f7/src/mintpy/simulation/decorrelation.py#L337-L376))。
  $\gamma < 0.05$ は 0.05 に床、$L$ は `NCORRLOOKS` か `ALOOKS·RLOOKS/1.94` (`var` では 80 で頭打ち)。
  他の選択肢は `coh` (γ そのもの)、`fim` (Fisher 情報量)、`no` (OLS = Berardino 2002 の古典 SBAS)。
  行に $\sqrt{w}$ を掛けて `lstsq` (gelsd) に渡す。
- **対角重み**: 同じ日付を共有する干渉縞どうしの誤差相関は無視している。「分散の逆数の重みは誤差が独立なら BLUE」
  なので、言うなら「BLUE の対角近似」。
- **重みが画素ごとのループの原因**: 重みなしなら全観測が有効な画素を `lstsq` 1 回でまとめて解き、重みつきなら
  `estimating time-series via WLS pixel-by-pixel` のループ
  ([ifgram_inversion.py L803–870](https://github.com/insarlab/MintPy/blob/cc441486e3ca68212dec5deb5b0adf29abaa04f7/src/mintpy/ifgram_inversion.py#L803-L870))。
  San Francisco (Sentinel-1) の CPU が速いのはこれ ([results.md](results.md))。
- **速度形**: `minNormVelocity = auto → yes`。B = A·T (T = 累積和 × diag(Δt)、可逆) なので full rank なら解は同じ。
  違いが出るのは網が分断して rank が落ちたときの最小ノルム解の意味だけ。フォークの GPU 経路も
  `G = B if min_norm_velocity else A`。
- **block 6 の κ は κ(B)** (速度形)。block 2 の ±1 の方程式 (A) の κ とは別物。突っ込まれたら「図は説明用の
  変位形、計測したのは実際に解いている速度形の行列」。
- **お椀の図 (`least_squares_bowl`) の数字**: $d_{01} = d_{12} = 1.0$, $d_{02} = 2.6$ (食い違い 0.6) の説明用。描いているのは**代表 1 画素**で、
  重みは網図のバーの長さ (0.85 / 0.70 / 0.15、長いペア t₀–t₂ が低い)。解は (1.076, 2.169)、残差は (0.076, 0.092, −0.431) で、
  食い違い 0.6 のうち 0.43 を重みの小さい長いペアに押し付ける。等重みなら解は (1.2, 2.4) で 0.2 ずつ均等 (水準網の網平均と同じ)。
- **なぜ解が左下の角に寄るか** (Syota さんも最初に引っかかった点。立ち話でも聞かれる): 最小二乗はどの式も「正しい」と決めず、
  食い違いを重みで分け合う。解は三角形の頂点の重心座標 $\lambda_i \propto 1/w_i$ で決まる (頂点 $i$ = 直線 $i$ を通らない頂点)。
  t₀–t₂ の重みが小さいと、その直線を通らない頂点 = 短いペア 2 本が交わる角 (1, 2) に重さが集まる (今の図で 0.72)。
  重みなしなら $\lambda = (1/3, 1/3, 1/3)$ で**厳密に重心** (三角形の係数が ±1 なので残差が同じ大きさになる)、t₀–t₂ の重み → 0 で角そのもの。
  図では線の太さ = 重みにして、解が「太い 2 本の交わる角」のそばにあることを見せている。
- **お椀の等高線の縦横比 = κ(G_w)**: $S(x) - S_{\min} = (x-\hat{x})^\top N (x-\hat{x})$ の等高線は半軸 ∝ 1/σᵢ(G_w) の楕円なので、
  縦横比は σ_max/σ_min = κ(G_w)。block 6 の「単位円を G_w で潰した楕円」(半軸 σᵢ) と同じ偏り。数学好きにはこれで
  block 2 と block 6 がつながる (図の画素は κ(N) = 4.75、κ(G_w) ≈ 2.18。重みが均等に近いほど丸くなる)
- LT の `edge_stamp` (「辺がつなぐ 2 頂点の場所だけに値が立つ」) も A 形でしか成り立たない。ポスターに入れるなら注記が要る。
- 「InSAR 時系列解析の数学的核心」とは言わない。言えるのは「SBAS 型 (MintPy `smallbaselineApp`) の中核 step」まで。
  PS-InSAR や phase linking は別の数理。

## 1c. "Shouldn't d01 + d12 = d02 hold exactly? Isn't the closure phase zero by construction?"

> For single-look wrapped phase, yes: the three interferograms come from the same
> three images. What breaks it is what each interferogram goes through on its own.
> Multilooking averages the phase over neighbouring pixels differently in every
> pair, and phase unwrapping can add a whole cycle to one of them. Atmosphere and
> real motion belong to a date, so they cancel around the triangle; that is also
> why the inversion cannot remove the atmosphere. (block 2)

- ポスターは「loop closure / closure phase」という用語を出さず、「3 日の三角形で足し算が合うはず → 実データは合わない →
  最適化」の概念だけを書いた (Syota さんの方針)。専門家には口頭で用語を添える。
- 合わない原因は**干渉縞ごと**のもの: マルチルック後の非相関雑音、アンラップ誤差 (2π の整数倍)、それに土壌水分や植生による
  系統的な closure phase (De Zan et al. 2015, TGRS)。**大気が原因とは言わない** (日付ごとの量なので一周で消える)。
- MintPy 自身も閉合を使う: `unwrap_error_phase_closure.py` (三角形の閉合でアンラップ誤差を補正、Yunjun et al. 2019 = 参考文献 [2])、
  `closure_phase_bias.py` (系統的な閉合のずれの補正)。
- 添字は $d_{ij}$ = $t_i$ から $t_j$ への動き ($x_j - x_i$)。$d_{20}$ と書くと $-d_{02}$ になるので、ポスターは $d_{01} + d_{12} = d_{02}$。
- お椀の図の食い違い 0.6 (1.0 + 1.0 ≠ 2.6) は説明のための誇張。実データの閉合のずれはずっと小さい。

## 1d. "Are neighbouring pixels solved together? Doesn't the batch couple them?"

> No. Every pixel is its own weighted least-squares problem, solved alone. The
> GPU stacks thousands of them into one batch only to run them at the same time;
> each pixel's matrix is factorized separately. Neighbours enter only before the
> inversion: coherence, and hence the weights, is estimated over a small window,
> and all phases are referenced to one reference pixel. (block 2)

- CPU (upstream `cc44148`): 重みありは画素ごとのループで `estimate_timeseries(y=stack_obs[:, idx], weight_sqrt=weight_sqrt[:, idx])`
  ([ifgram_inversion.py L854–870](https://github.com/insarlab/MintPy/blob/cc441486e3ca68212dec5deb5b0adf29abaa04f7/src/mintpy/ifgram_inversion.py#L854-L870))。
  重みなしは複数画素を `lstsq` 1 回にまとめるが、右辺を並べただけで画素ごとに独立。
- GPU: `(n, P, P)` に積んで `cholesky_ex` を 1 回。バッチの要素ごとに独立に分解する (画素間の結合はない)。
- block 2 の図は一時「画素 1 / 画素 2」を並べ、お椀の図に「画素 1 → 画素 2」の矢印まで描いていた。複数画素をまとめて解くように
  見えるので 2026-10-26 に**代表 1 画素だけ**に直し、「every pixel repeats this alone」と本文で言う形にした (poster_plan 判断 28・29)。

## 2. "Why not CholeskyQR2 / a QR-based scheme?"

> CholeskyQR2 needs the same Gram Cholesky to succeed, so it has the same
> applicability domain (κ ≲ u⁻¹ᐟ²) and breaks down on the same pixels. Its benefit
> is orthogonality of Q, which a one-shot least-squares solve never uses. And we
> measured the QR path on the same GPU: 16.5× slower in MintPy's step time.

- 引用 [3,4] から引けるのは「Gram + Cholesky は level-3 BLAS のみで並列向き」と
  「κ² の代償は既知」まで。**「CholeskyQR2 と同じだから安全」とは言わない**。

## 3. "Why do the five scenes spread from 5× to 94×? Does it scale with size?"

> No size dependence: the ranking does not follow pixel count. What varies is the
> CPU baseline. The San Francisco ARIA scene runs unweighted, and MintPy then
> solves all pixels in one call on the CPU, so there is little loop left to
> replace. Kuju has only 24 dates, so each pixel's system is tiny and the GPU
> step is dominated by fixed costs. For the clean size question use the
> controlled Galápagos measurement, 44× on 3.4 million pixels.

- 順位相関 (実際に反転した画素数で再計算): ピクセル数 −0.10、per-pixel 演算密度 +0.00、
  総演算量 +0.20。
- CPU の 1 画素あたり: 重み付きループ 2.3–4.6 ms (Fernandina / Galápagos / SanFranBay)、
  Kuju 0.14 ms、SanFranSen (重みなし) 0.08 ms。[results.md](results.md) §S3。

## 4. "What about the DEM-error step at only 6×?"

> Same core, but the per-pixel work is about 1/1000 of the network inversion
> (P = 4 instead of ~100), so the step is bound by framework overhead, not compute.
> The model predicts a ceiling near 10× and the large scene sits at 6×.

## 5. "Why a single GPU instead of Dask / a cluster?"

> They are orthogonal. Dask spreads the same per-pixel loop across processes; the
> torch solver replaces the loop with one batched call on one device. The point is
> accessibility: a workstation GPU a single group already owns. Combining the two
> is possible but not implemented.

## 6. "Memory limits? What if the scene does not fit in VRAM?"

> Chunks are sized automatically to 40 % of free VRAM; the design matrix is
> uploaded once and reused. Galápagos (3.4 M pixels) ran in chunks of about
> 8,700 pixels with a peak of 7.6 GB on a 16 GB card. There is no hard
> scene-size limit, only more chunks.

- Galápagos (S2): free VRAM 11.2 GiB → chunk 8,726 px、59 chunk/box × 6 box。

## 7. "Is the 44× the whole step, I/O included?"

> Yes. 44× is the step as MintPy itself times it, HDF5 read and write included.
> Only the Python start-up of a stand-alone step is left out; counting it gives
> 36× in that run, but in a full workflow the start-up is paid once for all
> steps.

- 44.4× = internal (6,169.3 / 139.0 s)、36.4× = step wall (6,189 / 170.06 s)。差は起動
  (CPU 19.7 s / GPU 31 s、NAS 上の fork `.venv` から import)。I/O は両方に入っている。
- 旧版の「44× は solver kernel」は誤り ([results.md](results.md) §計測環境の検証)。

## 7a. "Galápagos takes 103 min in the headline but 50 min in the chart?"

> Two different runs of the same scene. The headline inverts all 3.4 million
> pixels; the chart comes from a complete 18-step run, where the standard
> coherence mask leaves 1.3 million. Both show the same order of speedup,
> 44× and 38×.

- 見出し = S2 (internal、6,169 → 139 s)、グラフ = S3 (step wall、2,977 → 79 s、numpy 1.26.4 の環境)。
  ラベルに "1.29 M px" と書いてあるので、そこを指す。

## 7b. "In block 4 Fernandina is 1.43× and 16.5×, but the chart says 94×. Which is it?"

> They come from different benchmark runs, and they should not be chained. The
> 1.43× and 16.5× runs used a Python environment on network storage; the
> five-scene runs used a local environment with an older NumPy, which makes the
> CPU loop about 1.8× slower. Each comparison is fair within itself, because
> both sides ran in the same environment.

- 1.43 × 16.5 ≈ 24× と 93.77× の差は、CPU 基準 (numpy 2.4.4 で 367 s / 1.26.4 で 645 s)、
  起動 (47 s / 1 s)、GPU internal (13.8 s / 5.9 s、原因未解明) の 3 つ。
- **こちらから「numpy を揃えれば ○○×」とは言わない** (系列をまたいだ推定になる)。

## 8. "Does it work with NISAR / FORMOSAT-9 data?"

> MintPy reads NISAR GUNW products already, and the solver is agnostic to the
> sensor: it sees the network, not the wavelength. The five scenes cover C-band
> and L-band and four processors. For one NISAR frame-year, extrapolating
> from the measured throughput gives roughly 4 hours on the CPU against 5 to
> 20 minutes on the GPU; that is an extrapolation, not a measurement.

- 数字はポスターに載せていない (2026-10-26)。[compute_scale.md](compute_scale.md) の conn5 行。

- FORMOSAT-9 (X-band、2028/2030) は**適性を主張しない**。聞かれたら「X-band は時間
  デコリレーションが速いので、都市部・インフラ監視が主戦場になるだろう。ソルバ自体は
  網しか見ないので使える」と答える。分解能の数字は言わない。

## 8a. "How does the cost grow as the archive gets longer?"

> Roughly with the cube of the number of dates. Each pixel costs about K·P² to
> build its normal matrix plus P³/3 to factorize it; with a fixed number of
> connections per date, K grows like D and P like D, so the total grows like D³.
> Going from one year to three years of acquisitions is about 29 times the work.

- 2026-10-26 にポスターの block 3 から移した (Syota さんの判断: 他のブロックに比べて重要度が低く、聞かれたら答えれば十分)。
  block 7 は「アーカイブの長さのおおよそ 3 乗で伸びる」の 1 句だけ残している。
- 数式: per-pixel $O(KP^2 + P^3/3)$、$K \propto D$ (逐次網 conn 一定)、$P = D - 1$ → $D^3$。
- 29× は [compute_scale.md](compute_scale.md) の conn5 の 1 年 (76 TFLOP) → 3 年 (2216 TFLOP)。$3^3 = 27$ との差は $K$ と $P$ の端の項。
- 支配項は Cholesky ではなく **Gram 行列の組み立て $O(KP^2)$** (Galápagos $P = 97$ で約 95%、
  [numerical_method.md](numerical_method.md) §5)。

## 9. "Is it merged upstream? How do I use it today?"

> Submitted as insarlab/MintPy PR #1490, under review; the branch is rebased on the
> current main and the GPU unit tests pass. Today you can install the fork with
> the [gpu] extra and set `mintpy.networkInversion.solver = torch` in the template.
> The CPU path is untouched, so nothing changes unless you opt in.

- 印刷直前に `gh pr view 1490 --repo insarlab/MintPy` で状態を確認し、merge 済みなら
  block 7 を書き換える。

## 10. "AMD / Apple Silicon?"

> Not yet. The implementation is PyTorch, so a ROCm or MPS backend is a matter of
> `torch.device`, but the batched Cholesky path has only been validated on CUDA,
> and the code currently errors out without a CUDA device rather than silently
> falling back.

## 11. "Who are you with?"

> I'm an independent researcher and software engineer; Earthsea Wizard is my
> practice. Earlier I did postdoc work with JAXA-funded satellite imagery for
> disaster response, which is where the InSAR interest comes from.

## 12. "Can this be applied to other packages (LiCSBAS, dolphin, ISCE3)?"

> The same reformulation applies to any per-pixel least-squares inversion with a
> shared design matrix. I have sibling benchmark work on dolphin and ISCE3; the
> MintPy contribution is the one that is complete and under review.

- 具体的な数字は言わない (別プロジェクトで、ポスターの範囲外)。

## 13. "What happens to rank-deficient pixels? How invasive is the change?"

> `cholesky_ex` reports a failed factorization per pixel instead of raising, so
> those pixels are flagged and zero-filled and no NaN leaks downstream. They are
> the low-coherence pixels the temporal-coherence mask removes anyway. The change
> itself is opt-in by one template key, lives in a separate `mintpy.gpu`
> subpackage, and leaves the CPU path byte-for-byte unchanged.

- ポスターの block 4 から外した実装 Tips の受け皿 (2026-10-19)。chunk は Q6、
  欠測 (ゼロ重み = 行削除) は block 4 本文、DEM 誤差への流用は block 5 (2026-10-26 の入れ替え前は 6)。

## 14. "Do the CPU and GPU products agree everywhere?"

> On the final products, yes: all five scenes pass the 10⁻⁵ gate on velocity
> and the geocoded time series. On two scenes some radar-coordinate
> intermediates differ, in near-rank-deficient pixels where the CPU returns a
> minimum-norm solution and the GPU zero-fills. The temporal-coherence mask
> discards exactly those pixels before any product is made.

- Kuju と San Francisco (ARIA)。Kuju の geocoded velocity はマスク後 1.38e-7 で通過。
- ポスターの旧 block 7 の但し書きの受け皿 (2026-10-26)。

## 15. "What is the big grey segment? If this step is 44× faster, how much faster is the whole run?"

> The second segment is loading the interferograms, which is pure I/O, and in
> this run the data sat on a network share, so it is inflated. On a local disk
> the inversion's share would be larger, so 43.5 % is the conservative figure.
> The rest are many steps of a few percent each. For the whole run, the
> inversion alone caps the gain: even at zero seconds the run would be at most
> about 1.8 times faster. The same GPU core also runs the DEM-error
> correction; beyond that, what is left is I/O and many small steps.

- 横棒は [results.md](results.md) §Baseline 18 step の内訳 (Fernandina、CPU、internal)。2 位は load_data 88.6 s (17.7%)、
  CIFS 共有 (1 GbE) 越しの読み込み
- **44× を掛けて全体の短縮を出さない**: 44× は S2 (Galápagos)、横棒は Fernandina の Phase 1 baseline。
  言えるのはこの run の中の Amdahl の上限 1 / (1 − 0.435) ≈ 1.8× だけ (correct_topography も入れて約 1.9×)
- wall で割ると 24.0% になるのは step ごとの起動 (`--dostep` で 18 回) が母数に入るため。
  通常の 1 プロセス実行では起動は 1 回 (→ Q7 と同じ理屈)

## 持って行く数字 (暗記用)

| 数字 | 意味 | 系列 |
| --- | --- | --- |
| 43.5 % | `invert_network` の占有率 (Fernandina baseline、internal)。2 位 load_data 17.7 % (NAS の I/O)。全体の短縮の上限 ≈ 1.8× | — |
| 1.43× | GPU batched QR の CPU 比 (internal、Fernandina) | Phase 1 |
| 16.5× | 同一 GPU の QR→Cholesky、MintPy の step 時間 (起動除く、Fernandina) | S1 |
| 3,841,835 → 57 | kernel launches / chunk (19,403 px) | S1 |
| 6,169 s → 139 s、44.4× | Galápagos 3.4 M px × 475 ifgs、CPU 比 (internal、ポスターの見出し)。step wall だと 6,189 → 170 s、36.4× | S2 |
| 5.3–93.8× | 5 シーン E2E step wall、CPU 比 | S3 |
| 6.15× | `correct_topography` Galápagos | — |
| 1e-5 / 16 µm | 正規化 RMS gate / 絶対 RMS 最大 | S3 / S2 |
| κ₂(G) 11–55、最悪 721、破綻 4.1e3 | 条件数サーベイ | — |
| 4 h → 5–20 min | NISAR 1 frame-year 外挿 (ポスターには載せない) | 外挿 |
