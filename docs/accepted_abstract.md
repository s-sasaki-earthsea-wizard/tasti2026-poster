# 受理された抄録 (凍結) — TASTI 2026, Paper No. T0043

受理メール (2026-10-07 14:20 JST、`no-reply@conf.tw`、件名 "Review result for your
paper (TASTI 2026)") の内容。ポスターのタイトル・著者表記・キーワードはこれに合わせる。
抄録本文 (665 words) と LaTeX ソースは
[tasti2026-abstract](https://github.com/s-sasaki-earthsea-wizard/tasti2026-abstract)。

| 項目 | 値 |
| --- | --- |
| Conference Type | TASTI |
| Paper No. | **T0043** |
| Session Type | **Poster** |
| Topic & Subtopic | 02 Space Applications and Services / 0201 Earth Observation and Remote Sensing |
| All Authors | Syota Sasaki |
| Presenter / Contact | Syota Sasaki |
| Keywords | InSAR, GPU acceleration, PyTorch, time-series analysis, open-source software |

## Paper Title

> Accelerating Open-Source InSAR Time-Series Analysis on Consumer GPUs:
> A PyTorch-Based Network Inversion Solver for MintPy

## Short Abstract (199 words、提出フォーム入力値と完全一致)

> Interferometric SAR (InSAR) time-series analysis is a standard tool for measuring ground deformation, but archives are growing faster than the software that consumes them. In MintPy, a widely used open-source small-baseline package, a single step - the least-squares inversion of the interferogram network, solved pixel by pixel on the CPU - accounts for 43.5% of a complete run. This work removes that bottleneck on a single consumer GPU.
>
> A direct port of the per-pixel routine to a batched QR solver reached only 1.43x over the CPU path: the bottleneck was the shape of the problem, not the hardware. Reformulating around the normal equations reduces each tall-skinny system to a small Gram block, factorized in one batched Cholesky call in single precision using PyTorch.
>
> Measured against the CPU path on an NVIDIA GeForce RTX 5080, a Galapagos scene (3.4 million pixels, 475 retained interferograms) fell from 6,189 s to 170 s, a 36.4x step-level speedup; five public scenes spanning four interferometric processors and two radar wavelengths accelerated by 5.3x to 93.8x, all clearing a numerical agreement gate at normalized RMS differences of order 1e-5. Inversions that took hours now finish in minutes on hardware a single research group can own.

## メールに書かれた実務情報

- "Please refer to the Presenter Guidelines" → リンク先は Call for Papers ページ
  (<https://tasti2026.conf.tw/site/mypage53.aspx?pid=101&lang=en&sid=1691>)
- ポスターは各自印刷して持参
- **ポスターセッション: 2026-11-10 11:30–14:00、Room Tayouan D, 3F**
- **参加登録締切: 2026-10-13**
