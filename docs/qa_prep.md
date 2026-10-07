# ポスターセッション想定問答

立ち話で聞かれそうな順。英語の答えは**短く言い切り、詳細は図を指す**。
数字は [results.md](results.md)、数理は [numerical_method.md](numerical_method.md) が正。

## 1. "Is float32 really enough? Normal equations square the condition number."

> Yes, and we measured rather than assumed. The unweighted SBAS design matrix has
> κ₂ between 11 and 55 on all five scenes; even the worst weighted pixel we sampled
> is 721, while float32 Cholesky only breaks down near 4,000. The observed
> differences against the CPU reference are about 10⁻⁵ normalized, roughly 16 µm
> absolute on the large scene, which is two orders of magnitude below the
> millimetre-scale signal. (block 5)

- 「速度のために精度を捨てた」ではなく「この問題の条件数では float32 で十分だと
  見積もった上で選んだ」が正しい言い方。
- 将来 κ の大きい網に当たったら fp64 (破綻域が 6.7e7 まで上がる) か QR/SVD 経路に逃がせる設計。

## 2. "Why not CholeskyQR2 / a QR-based scheme?"

> CholeskyQR2 needs the same Gram Cholesky to succeed, so it has the same
> applicability domain (κ ≲ u⁻¹ᐟ²) and breaks down on the same pixels. Its benefit
> is orthogonality of Q, which a one-shot least-squares solve never uses. And we
> measured the QR path end to end: 16.5× slower on the same GPU.

- 引用 [3,4] から引けるのは「Gram + Cholesky は level-3 BLAS のみで並列向き」と
  「κ² の代償は既知」まで。**「CholeskyQR2 と同じだから安全」とは言わない**。

## 3. "Why do the five scenes spread from 5× to 94×? Does it scale with size?"

> No size dependence: the ranking does not follow pixel count. GPU time is nearly
> monotonic in total work; what varies is the CPU-side baseline across processors
> and data layouts. For the clean size question use the controlled Galápagos
> measurement, 36× on 3.4 million pixels.

- 順位相関: ピクセル数 −0.20、per-pixel 演算密度 +0.00。
- CPU 側のばらつきの原因 (マスク後の有効画素数、データレイアウト) は**未検証**と正直に言う。

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
> uploaded once and reused. Galápagos (3.4 M pixels) ran in three chunks with a
> peak of 7.6 GB on a 16 GB card. There is no hard scene-size limit, only more chunks.

## 7. "I/O: is the step really 36× faster end to end?"

> Two numbers, deliberately: 44× for the solver kernel, 36× for the whole step
> including HDF5 read/write on local SSD. On a network mount the I/O share grows
> and dilutes the ratio, which is why every benchmark here states its storage.

## 8. "Does it work with NISAR / FORMOSAT-9 data?"

> MintPy reads NISAR GUNW products already, and the solver is agnostic to the
> sensor: it sees the network, not the wavelength. The five scenes cover C-band
> and L-band and four processors. For NISAR-scale frames the numbers on the
> poster are extrapolated from measured throughput, so treat them as order of
> magnitude.

- FORMOSAT-9 (X-band、2028/2030) は**適性を主張しない**。聞かれたら「X-band は時間
  デコリレーションが速いので、都市部・インフラ監視が主戦場になるだろう。ソルバ自体は
  網しか見ないので使える」と答える。分解能の数字は言わない。

## 9. "Is it merged upstream? How do I use it today?"

> Submitted as insarlab/MintPy PR #1490, under review; the branch is rebased on the
> current main and the GPU unit tests pass. Today you can install the fork with
> the [gpu] extra and set `mintpy.networkInversion.solver = torch` in the template.
> The CPU path is untouched, so nothing changes unless you opt in.

- 印刷直前に `gh pr view 1490 --repo insarlab/MintPy` で状態を確認し、merge 済みなら
  block 8 を書き換える。

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

## 持って行く数字 (暗記用)

| 数字 | 意味 | 系列 |
| --- | --- | --- |
| 43.5 % | `invert_network` の占有率 (Fernandina baseline) | — |
| 1.43× | GPU batched QR の CPU 比 | — |
| 16.5× / 4.49× | 同一 GPU の QR→Cholesky、solver core / step wall (Fernandina) | S1 |
| 3,841,835 → 57 | kernel launches / chunk | S1 |
| 6,189 s → 170 s、36.4× / 44.4× | Galápagos 3.4 M px × 475 ifgs、CPU 比 | S2 |
| 5.3–93.8× | 5 シーン E2E step wall、CPU 比 | S3 |
| 6.15× | `correct_topography` Galápagos | — |
| 1e-5 / 16 µm | 正規化 RMS gate / 絶対 RMS 最大 | S3 / S2 |
| κ₂(G) 11–55、最悪 721、破綻 4.1e3 | 条件数サーベイ | — |
| 4 h → 7–20 min | NISAR 1 frame-year 外挿 | 外挿 |
