# 手法の数理 — WLS / 正規方程式 / batched Cholesky / 条件数

> 抄録 repo `tasti2026-abstract/docs/numerical_method.md` のコピー (2026-08-06 版)。
> ポスター block 4–5 の裏付けと、当日 Q&A ([qa_prep.md](qa_prep.md)) への備え。
> 5 シーンの**実測 κ** は [results.md](results.md) §投稿後の追加結果 を参照。

Abstract の methodology 段落の裏付けと、査読・当日 Q&A への備え。
数学的な完全版は sibling の
[vrc-insar-batched-cholesky-LT/docs/numerical_method.md](https://github.com/s-sasaki-earthsea-wizard/vrc-insar-batched-cholesky-LT/blob/main/docs/numerical_method.md)
が正。ここでは abstract の主張を守るのに必要な範囲で自己完結させる。

実装対応:

- `src/mintpy/gpu/ifgram_inversion.py` — `estimate_timeseries_batch`, `_solve_cholesky`
- `src/mintpy/gpu/_common.py` — `solve_normal_equations_batched`, `auto_chunk_size`

---

## §1. 問題設定 — SBAS 網逆解析は per-pixel の WLS

$N_d$ 枚の SAR 取得から $N_p$ 本の干渉ペアを作ると、各ピクセル $k$ で

$$ d_k = G\, x_k + \varepsilon_k $$

- $d_k \in \mathbb{R}^{N_p}$ : アンラップ位相 (観測)
- $x_k \in \mathbb{R}^{N_d-1}$ : 復元したい時系列 (基準日固定で自由度 $N_d-1$)
- $G \in \mathbb{R}^{N_p \times (N_d-1)}$ : 網の接続を表す設計行列。**全ピクセル共通**
- 通常 $N_p > N_d-1$ (冗長網) の優決定最小二乗

ペアごとのコヒーレンスで対角重み $W_k$ を入れた WLS:

$$ \hat{x}_k = \arg\min_x \big\lVert W_k^{1/2}(G x - d_k) \big\rVert_2^2 $$

$G$ は共通だが $d_k, W_k$ はピクセルごとに違う。**「同じ形・違う中身の小さな
WLS」を全ピクセル分** (Galapagos で 3.4M 回) 解くのが計算の本体で、これが
GPU バッチ化の的。

## §2. なぜ `lstsq` (QR/SVD) を捨てたか

CPU 参照実装はピクセルごとに `scipy.linalg.lstsq` を呼ぶ。QR/SVD は $G$ を
直接分解するので条件数は $\kappa(G)$ のまま — 数値的には最も安全。しかし:

- per-pixel の薄い QR は逐次 Householder 反復で、GPU バッチと相性が悪い。
  実測: cuSolver `gels` 経由の GPU batched QR は**チャンクあたり ~3.8M kernel
  launches** を発行 (Fernandina)、internal speedup は CPU 比 1.43× 止まり。
- ベースライン計測で `invert_network` は end-to-end の **43.5%** を占有。

→ 解法を対称正定値系に落として **batched Cholesky** で叩く方針に転換。

## §3. 正規方程式 + batched Cholesky

$G_w := W_k^{1/2} G$ とおくと WLS の正規方程式は

$$ \underbrace{G_w^\top G_w}_{=:N_k}\, x_k = G_w^\top d_w $$

$N_k$ は $(N_d-1)\times(N_d-1)$ の小さな密行列で、冗長網が full column rank なら
**SPD** → Cholesky $N_k = L_k L_k^\top$ + 前進後退代入で解ける。ピクセル $n$ 個を
`(n, c, c)` テンソルに積み、cuSolver の**バッチ Cholesky を 1 回**呼ぶ:

```python
G_T = G_batch.transpose(-1, -2)
N   = G_T @ G_batch                    # batched Gram matrices
r   = G_T @ y_batch.unsqueeze(-1)      # batched RHS
L, info = torch.linalg.cholesky_ex(N)  # batched Cholesky, rank check via info
X = torch.cholesky_solve(r, L)
```

チャンクあたりのカーネル起動は **~57 回** (QR 経路の 3.8M 回から 67,400×
の削減)。これが 16.5× の kernel speedup の正体 → [results.md](results.md)。

### 条件数の但し書き (Q&A 最頻出想定)

教科書 (Golub & Van Loan 等) は「正規方程式を作るな、$\kappa(G^\top G) =
\kappa(G)^2$」と警告する。本問題でそれが許される理由:

1. **$G$ が良条件**: 網設計行列は $\pm 1$ 構造 (位相定式化) か時間 baseline
   スケール (速度定式化) で、列数も数十〜数百。冗長網 (`min_redundancy`) で
   接続が担保される。
2. よって $\kappa(G)^2 \cdot \epsilon_{\text{float32}}$ が要求精度に収まる。
3. **要求精度が緩い**: 欲しい変位はミリ〜サブミリ。実測の正規化 RMS は
   最大 **1.19e-5** で upstream gate < 1e-4 を約 1 桁の余裕で通過。しかもこの
   値は**同一 GPU・同一 float32 の QR 解との差**なので、「正規方程式化の代償
   だけ」を分離して測った最も直接的な裏付けになっている。

> 想定問答: 「float32 で精度は大丈夫か?」→「速度のために精度を捨てたのでは
> なく、この問題の条件数では float32 で十分だと**見積もった上で**選んだ。
> 5 シーンの最終成果物 (velocity.h5) で gate 5/5 通過が実測の裏付け」。

## §4. 実装の要点 (abstract の "minimally invasive" の中身)

- **opt-in 設計**: cfg key `mintpy.networkInversion.solver = torch` (CLI
  `--solver`)。既定は cpu で、**CPU 経路は byte-for-byte 不変**。
- **分離 subpackage**: `src/mintpy/gpu/`。dispatch は 1 箇所のみ。
- **NaN 観測は重み 0 で除外**: $G^\top W G = \sum_i w_i^2 g_i g_i^\top$ から
  該当項が消えるので、行削除と数学的に等価。行数固定のままバッチ化できる。
  temporal coherence 計算では masked 行の $\cos(0)=1$ を引き戻す補正が必要
  (CPU 経路との一致のため)。
- **rank 落ちの安全弁**: `cholesky_ex` の info コードで失敗ピクセルを検出し、
  因子を単位行列・右辺を 0 に差し替えて解 0 にフォールバック。例外を投げる
  `cholesky` だと 1 ピクセルの失敗がバッチ全体を落とすため `_ex` 版が必須。
- **VRAM-aware チャンク**: `auto_chunk_size` が free VRAM の 40% を上限に
  チャンク幅を自動決定。$G$ と時間 baseline は 1 度だけ GPU 転送して再利用。
  Galapagos (3.4M px) で 3 チャンク、VRAM peak 7.6/16 GiB。
- **速度定式化** (`min_norm_velocity=True`, 既定): 区間速度を解いてから
  `cumsum` で時系列に積む。rank が際どい網で最小ノルム速度解として安定。

## §5. speedup の天井は per-pixel flops 密度で決まる

同じコアを 2 つのステップに適用した結果の差の説明 (abstract の 44× vs 6× の差):

- per-pixel コスト $\approx \underbrace{O(K P^2)}_{\text{Gram 組み立て}} + \underbrace{O(P^3/3)}_{\text{Cholesky}}$
  ($K$ = 干渉ペア数, $P = N_d - 1$)。支配項は Cholesky ではなく **Gram 行列の
  組み立て** (Galapagos $P=97$ で ~95%)。
- `invert_network` (Galapagos): per-pixel **~9.7 MFLOP** (積和 2 FLOP 換算) →
  演算スループット律速で **internal 44.4×**。
- `correct_topography` (DEM 残差, $P=4$): per-pixel **~3,600 FLOP** (~1/1000) →
  framework overhead 律速で **6.15×**、天井 ~10×。

> flops の絶対値を出すときは積和の数え方 (1 FLOP / 2 FLOP) を明示すること。
> 系列間の**比**はどちらの convention でも不変。
