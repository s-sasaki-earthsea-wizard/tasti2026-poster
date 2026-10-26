# NISAR スケール見積もり — abstract の "significance" の定量的裏付け

宇宙関連の学会だから、**NISAR を名指しで定量に踏み込める**のがこのネタの強み。
再現スクリプトは本リポジトリの [scripts/estimate_scale.py](../scripts/estimate_scale.py)
(原本は sibling repo [vrc-insar-batched-cholesky-LT](https://github.com/s-sasaki-earthsea-wizard/vrc-insar-batched-cholesky-LT/blob/main/scripts/estimate_scale.py))。

```bash
python3 scripts/estimate_scale.py --pixels 305360000 --dates 30 --conn 5
```

## 記法 (混ぜると桁を外す)

- $K$: 干渉ペア数 (観測数 = $G$ の行数)
- $P = D-1$: 未知数 ($D$ = 取得枚数)
- $n$: ピクセル数 (solve を回す回数の外側係数)

総コスト $\;n \times \big(O(KP^2)\,\text{[Gram 組み立て]} + O(P^3/3)\,\text{[Cholesky]}\big)$

## NISAR 1 フレームの規模

- 実データ 1 シーン ≈ 17,350 × 17,600 px = **3.05 億 px** (Galapagos の ~90 倍)
- 12 日回帰 → 1 年で $D \approx 30$、$P = 29$
- 逐次網 conn=5 で $K = \text{conn} \cdot D - \text{conn}(\text{conn}+1)/2 = 135$
  (この網モデルは Galapagos の「475 kept」を conn=5, D=98 で再現できることで検証済み)

| シナリオ | $n$ | $K$ | $P$ | per-px | 総演算量 | 入力量 | CPU 外挿 | GPU 外挿 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 frame × 1 yr (conn4) | 305 M | 110 | 29 | 204 kFLOP | 62 TFLOP | 269 GB | 3.3 h | 4.5 min |
| **1 frame × 1 yr (conn5)** | **305 M** | **135** | **29** | **249 kFLOP** | **76 TFLOP** | **330 GB** | **4.1 h** | **5.5 min** |
| 1 frame × 1 yr (full 網) | 305 M | 435 | 29 | 779 kFLOP | 238 TFLOP | 1063 GB | 12.8 h | 17.3 min |
| 1 frame × 3 yr (conn5) | 305 M | 435 | 89 | 7.3 MFLOP | 2216 TFLOP | 1063 GB | 119 h | 2.7 h |

(2026-10-26 再計算: 校正を S2 の internal (起動除く) と使用 ifgs 475 本に修正。旧値は step wall と
490 本で校正していて、GPU 側が約 2 割遅めに出ていた)

- 一番刺さる言い方: **「29×29 の Cholesky を 3.05 億回」**。
- $D$ が増えると $K \propto D$, $P^2 \propto D^2$ → 総演算量は **$D^3$** で伸びる
  (1 年→3 年で 29 倍)。「アーカイブが伸びるほど GPU が必須になる」の根拠。

## 外挿の但し書き (誠実さ担保 — 査読/Q&A 用)

1. **壁時計は実測スループットからの外挿**: Galapagos 実測 (S2、32.0 TFLOP /
   CPU 6,169.3 s / GPU 139.0 s、MintPy の internal) から実効 CPU 5.2 GFLOPS /
   GPU 230 GFLOPS を逆算して割っただけ。ピーク FLOPS の主張ではない。
2. **モデルの答え合わせ**: Fernandina 予測 6.8 s vs 実測 6.9 s (S3、良好)。ただし
   Kuju は 20 倍外す (per-pixel 密度が低く固定 overhead 律速のため)。
3. **NISAR 1 年網の per-pixel 密度 (249 kFLOP) は Kuju 帯** (193 kFLOP,
   6.85×) であって Galapagos 帯 (9.4 MFLOP, 44×) ではない。ただし NISAR は
   $n$ が Kuju の 1,350 倍あり、チャンク 342 kpx × 893 回で per-chunk overhead
   が完全償却されるため、Galapagos 寄りの効率が出る見込み。**実測がないので
   公の場では「GPU で 5〜20 分」のレンジ表現が安全** (conn5 の 5.5 min 〜 full 網の 17 min)。
4. **NISAR 規模では I/O が計算と同桁に**: 入力 330 GB は 3 GB/s NVMe でも
   110 s。internal と step wall の乖離が実運用で効いてくる領域。
   ストレージ帯域の議論とセットで話すこと。

## abstract / ポスターでの使い方

- Abstract 本文 (800 words 制約) では数表は出さず、「processing scales to
  NISAR-era archives」レベルの定性表現 + 代表値 1 つに留めるのが現実的。
  現ドラフトは定性表現のみ。**もし 1 数字入れるなら「a single NISAR frame-year
  (~0.3 billion pixels) maps to minutes rather than hours on one consumer GPU」**
  のような but 外挿である旨を添えた形。
- **ポスターには外挿の数字を載せない** (2026-10-26、block 7 を「データが増える → 民生 GPU の意義」に
  絞ったため)。$D^3$ の話も 2026-10-26 に block 3 から Q&A ([qa_prep.md](qa_prep.md) Q8a) へ移した。Q&A で聞かれたら 1 frame-year (conn5) の行を使い、
  **"extrapolated from the measured throughput (not measured)"** を添えて「CPU 約 4 h、GPU 5〜20 min」。
  表のフル版はスライドで。全球外挿 (0.44 EFLOP/yr) は仮定が
  粗いので**本編では使わない** (元 doc の判断を踏襲)。
