# ポスターセッション想定問答

立ち話で聞かれそうな順。英語の答えは**短く言い切り、詳細は図を指す**。
数字は [results.md](results.md)、数理は [numerical_method.md](numerical_method.md) が正。

## 1. "Is float32 really enough? Normal equations square the condition number."

> Yes, and we measured rather than assumed. The unweighted SBAS design matrix has
> κ₂ between 11 and 55 on all five scenes; even the worst weighted pixel we sampled
> is 721, while float32 Cholesky only breaks down near 4,000. Against the CPU
> reference on the large scene, the per-pixel RMS difference is 0.06 µm for the
> median pixel and 16 µm for the worst, against millimetre-level InSAR
> precision. (block 5)

- 「速度のために精度を捨てた」ではなく「この問題の条件数では float32 で十分だと
  見積もった上で選んだ」が正しい言い方。
- 将来 κ の大きい網に当たったら fp64 (破綻域が 6.7e7 まで上がる) か QR/SVD 経路に逃がせる設計。

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
  欠測 (ゼロ重み = 行削除) は block 4 本文、DEM 誤差への流用は block 6。

## 14. "Do the CPU and GPU products agree everywhere?"

> On the final products, yes: all five scenes pass the 10⁻⁵ gate on velocity
> and the geocoded time series. On two scenes some radar-coordinate
> intermediates differ, in near-rank-deficient pixels where the CPU returns a
> minimum-norm solution and the GPU zero-fills. The temporal-coherence mask
> discards exactly those pixels before any product is made.

- Kuju と San Francisco (ARIA)。Kuju の geocoded velocity はマスク後 1.38e-7 で通過。
- ポスターの旧 block 7 の但し書きの受け皿 (2026-10-26)。

## 持って行く数字 (暗記用)

| 数字 | 意味 | 系列 |
| --- | --- | --- |
| 43.5 % | `invert_network` の占有率 (Fernandina baseline) | — |
| 1.43× | GPU batched QR の CPU 比 (internal、Fernandina) | Phase 1 |
| 16.5× | 同一 GPU の QR→Cholesky、MintPy の step 時間 (起動除く、Fernandina) | S1 |
| 3,841,835 → 57 | kernel launches / chunk (19,403 px) | S1 |
| 6,169 s → 139 s、44.4× | Galápagos 3.4 M px × 475 ifgs、CPU 比 (internal、ポスターの見出し)。step wall だと 6,189 → 170 s、36.4× | S2 |
| 5.3–93.8× | 5 シーン E2E step wall、CPU 比 | S3 |
| 6.15× | `correct_topography` Galápagos | — |
| 1e-5 / 16 µm | 正規化 RMS gate / 絶対 RMS 最大 | S3 / S2 |
| κ₂(G) 11–55、最悪 721、破綻 4.1e3 | 条件数サーベイ | — |
| 4 h → 5–20 min | NISAR 1 frame-year 外挿 (ポスターには載せない) | 外挿 |
