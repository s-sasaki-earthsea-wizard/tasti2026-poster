#!/usr/bin/env python3
"""SBAS 網逆解析 (per-pixel WLS) の計算規模を見積もる.

LT スライド (`slides-jp/index.html` の「計算規模」スライド) と
`docs/compute_scale.md` に焼き込んだ数字の出典。

やっていること:

1. per-pixel の FLOP を「正規方程式 + Cholesky」の各段で数える
2. ピクセル数を掛けて 1 シーンぶんの総演算量・入力データ量を出す
3. `docs/results.md` の Galapagos 実測 (CPU 6189 s / GPU 170.06 s) から
   逆算した**実効**スループットで壁時計時間に換算する

3. はベンチ機 1 台の実測から外挿しているだけで、ピーク FLOPS の主張ではない。
per-pixel の flops 密度が変わると speedup も変わる (docs/numerical_method.md §4)
ので、あくまでオーダー感の目安として使うこと。

使い方::

    python3 scripts/estimate_scale.py                     # プリセット一覧
    python3 scripts/estimate_scale.py --pixels 305360000 --dates 30 --conn 5
    python3 scripts/estimate_scale.py --repeat-days 12 --years 3 --conn 5
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field

# --- 実測キャリブレーション (docs/results.md 冒頭の表) -----------------------
# GalapagosSenDT128: 3.4M px x 490 pair (98 date), internal 時間
CAL_PIXELS = 3_400_000
CAL_PAIRS = 490
CAL_DATES = 98
CAL_CPU_SEC = 6189.0
CAL_GPU_SEC = 170.06

# 入力スタックは unwrapPhase と coherence の 2 本を float32 で読む
BYTES_PER_SAMPLE = 4
STACKS_READ = 2

# VRAM 16 GiB のうち auto_chunk_size が使う上限 (mintpy/gpu/_common.py の既定 40%)
VRAM_BYTES = 16 * 1024**3
VRAM_FRACTION = 0.40


@dataclass
class Scenario:
    """計算規模を見積もる 1 ケース.

    Attributes:
        name: 表示名。
        pixels: ピクセル数 n。
        dates: 取得 (SAR 画像) 枚数 D。未知数は P = D - 1。
        pairs: 干渉ペア数 K。None なら ``conn`` から推定する。
        conn: 逐次網の接続数。``pairs`` が None のときだけ使う。
    """

    name: str
    pixels: int
    dates: int
    pairs: int | None = None
    conn: int = 5
    note: str = field(default="")

    @property
    def num_params(self) -> int:
        """未知数 P。基準日を 0 に固定するので D - 1。"""
        return self.dates - 1

    @property
    def num_pairs(self) -> int:
        """干渉ペア数 K。"""
        if self.pairs is not None:
            return self.pairs
        return sequential_network_pairs(self.dates, self.conn)


def sequential_network_pairs(num_dates: int, conn: int) -> int:
    """逐次 (sequential) 網の干渉ペア数を返す.

    各取得を後続 ``conn`` 枚と結ぶ網。末尾は結び先が足りないので詰まる::

        K = sum_i min(conn, D - 1 - i) = conn * D - conn * (conn + 1) / 2

    Galapagos (D=98, conn=5) で K=475 となり、docs/results.md の
    「475 kept」と一致する。

    Args:
        num_dates: 取得枚数 D。
        conn: 各取得が張る接続数。

    Returns:
        干渉ペア数 K。
    """
    if conn >= num_dates:
        return num_dates * (num_dates - 1) // 2
    return conn * num_dates - conn * (conn + 1) // 2


def count_flops(num_pairs: int, num_params: int) -> dict[str, float]:
    """per-pixel の FLOP を段ごとに数える.

    正規方程式 + Cholesky 経路 (mintpy/gpu/_common.solve_normal_equations_batched)
    の各段。積和は 2 FLOP として数える。行スケールだけは乗算のみ。

    Args:
        num_pairs: 干渉ペア数 K (= 観測数)。
        num_params: 未知数 P。

    Returns:
        段名 -> FLOP の dict。``total`` キーに合計を入れる。
    """
    k, p = num_pairs, num_params
    stages = {
        "row_scale": k * p,          # W^(1/2) G の行スケール (乗算のみ)
        "gram": 2 * k * p * p,       # G^T W G  … 支配項
        "rhs": 2 * k * p,            # G^T W d
        "cholesky": p**3 / 3.0,      # N = L L^T
        "triangular": 2 * p * p,     # 前進・後退代入
    }
    stages["total"] = sum(stages.values())
    return stages


def working_set_bytes(num_pairs: int, num_params: int) -> int:
    """per-pixel の GPU 側ワーキングセット (byte).

    行スケール済みの G はピクセルごとに実体化されるので (K x P) が効く。
    ここが auto_chunk_size のチャンク幅を決める。

    Args:
        num_pairs: 干渉ペア数 K。
        num_params: 未知数 P。

    Returns:
        1 ピクセルあたりのバイト数。
    """
    k, p = num_pairs, num_params
    return (k * p + k * STACKS_READ + p * p) * BYTES_PER_SAMPLE


def summarize(sc: Scenario) -> dict[str, float]:
    """1 シナリオの計算規模をまとめる.

    Args:
        sc: 対象シナリオ。

    Returns:
        見積もり値の dict。
    """
    k, p = sc.num_pairs, sc.num_params
    stages = count_flops(k, p)
    per_pixel = stages["total"]
    total_flops = sc.pixels * per_pixel
    input_bytes = sc.pixels * k * BYTES_PER_SAMPLE * STACKS_READ

    cal_flops = CAL_PIXELS * count_flops(CAL_PAIRS, CAL_DATES - 1)["total"]
    gpu_flops_per_sec = cal_flops / CAL_GPU_SEC
    cpu_flops_per_sec = cal_flops / CAL_CPU_SEC

    ws = working_set_bytes(k, p)
    chunk_pixels = int(VRAM_BYTES * VRAM_FRACTION / ws)

    return {
        "pairs": k,
        "params": p,
        "per_pixel_flops": per_pixel,
        "gram_share": stages["gram"] / per_pixel,
        "cholesky_share": stages["cholesky"] / per_pixel,
        "total_flops": total_flops,
        "num_cholesky": sc.pixels,
        "input_bytes": input_bytes,
        "arithmetic_intensity": total_flops / input_bytes,
        "cpu_sec": total_flops / cpu_flops_per_sec,
        "gpu_sec": total_flops / gpu_flops_per_sec,
        "chunk_pixels": chunk_pixels,
        "num_chunks": sc.pixels / chunk_pixels,
    }


def build_presets() -> list[Scenario]:
    """スライドで使うプリセット一式を返す.

    Returns:
        シナリオのリスト。
    """
    # NISAR: 約 17,350 x 17,600 px、12 日回帰 -> 1 年で約 30 枚
    nisar_px = 17_350 * 17_600
    return [
        Scenario("Kuju (実測)", 226_000, 24, pairs=167, note="ALOS-1, speedup 6.85x"),
        Scenario("Fernandina (実測)", 270_000, 98, pairs=288, note="S1, speedup 93.8x"),
        Scenario("Galapagos (実測/校正元)", CAL_PIXELS, CAL_DATES, pairs=CAL_PAIRS,
                 note="S1, speedup 44.4x (internal)"),
        Scenario("NISAR 1frame x 1yr (conn4)", nisar_px, 30, conn=4),
        Scenario("NISAR 1frame x 1yr (conn5)", nisar_px, 30, conn=5, note="主線"),
        Scenario("NISAR 1frame x 1yr (full網)", nisar_px, 30, pairs=30 * 29 // 2),
        Scenario("NISAR 1frame x 3yr (conn5)", nisar_px, 90, conn=5),
    ]


def format_seconds(sec: float) -> str:
    """秒を読みやすい単位に整形する.

    Args:
        sec: 秒数。

    Returns:
        整形済み文字列。
    """
    if sec < 90:
        return f"{sec:.1f} s"
    if sec < 5400:
        return f"{sec / 60:.1f} min"
    return f"{sec / 3600:.1f} h"


def print_table(scenarios: list[Scenario]) -> None:
    """シナリオ一覧を表で出力する.

    Args:
        scenarios: 対象シナリオ。
    """
    header = (
        f"{'scenario':30s} {'n[Mpx]':>8s} {'K':>5s} {'P':>4s} "
        f"{'per-px[kF]':>11s} {'total[TFLOP]':>13s} {'in[GB]':>8s} "
        f"{'CPU':>8s} {'GPU':>8s}"
    )
    print(header)
    print("-" * len(header))
    for sc in scenarios:
        r = summarize(sc)
        print(
            f"{sc.name:30s} {sc.pixels / 1e6:8.1f} {r['pairs']:5d} {r['params']:4d} "
            f"{r['per_pixel_flops'] / 1e3:11.1f} {r['total_flops'] / 1e12:13.2f} "
            f"{r['input_bytes'] / 1e9:8.1f} "
            f"{format_seconds(r['cpu_sec']):>8s} {format_seconds(r['gpu_sec']):>8s}"
        )


def print_detail(sc: Scenario) -> None:
    """1 シナリオの内訳を出力する.

    Args:
        sc: 対象シナリオ。
    """
    r = summarize(sc)
    stages = count_flops(r["pairs"], r["params"])
    print(f"\n=== {sc.name} ===")
    print(f"  n = {sc.pixels:,} px, D = {sc.dates}, K = {r['pairs']}, P = {r['params']}")
    print("  per-pixel FLOP:")
    for key in ("row_scale", "gram", "rhs", "cholesky", "triangular"):
        print(f"    {key:12s} {stages[key]:12,.0f}  ({stages[key] / stages['total'] * 100:4.1f}%)")
    print(f"    {'total':12s} {stages['total']:12,.0f}")
    print(f"  総演算量        : {r['total_flops'] / 1e12:.2f} TFLOP")
    print(f"  Cholesky 実行回数: {r['num_cholesky']:,} 回 ({r['params']}x{r['params']})")
    print(f"  入力データ量    : {r['input_bytes'] / 1e9:.1f} GB (fp32 x {STACKS_READ} stack)")
    print(f"  算術強度        : {r['arithmetic_intensity']:.0f} FLOP/byte")
    print(f"  チャンク        : {r['chunk_pixels'] / 1e3:.0f} kpx/chunk, {r['num_chunks']:.0f} chunk")
    print(f"  壁時計 (外挿)   : CPU {format_seconds(r['cpu_sec'])} / GPU {format_seconds(r['gpu_sec'])}")


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解釈する.

    Returns:
        パース済み引数。
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pixels", type=int, help="ピクセル数 n")
    parser.add_argument("--dates", type=int, help="取得枚数 D")
    parser.add_argument("--pairs", type=int, help="干渉ペア数 K (省略時は --conn から推定)")
    parser.add_argument("--conn", type=int, default=5, help="逐次網の接続数 (既定: 5)")
    parser.add_argument("--repeat-days", type=float, help="回帰日数。--years と併用して D を出す")
    parser.add_argument("--years", type=float, help="観測年数。--repeat-days と併用")
    return parser.parse_args()


def main() -> None:
    """エントリポイント。"""
    args = parse_args()

    dates = args.dates
    if dates is None and args.repeat_days and args.years:
        dates = int(round(args.years * 365.25 / args.repeat_days))

    if args.pixels or dates:
        pixels = args.pixels or 17_350 * 17_600
        sc = Scenario("custom", pixels, dates or 30, pairs=args.pairs, conn=args.conn)
        print_detail(sc)
        return

    presets = build_presets()
    print_table(presets)
    print("\n実測 3 件は校正・答え合わせ用 (docs/results.md)。NISAR 4 件が外挿。")
    for sc in presets:
        if sc.name.startswith("NISAR") and sc.note == "主線":
            print_detail(sc)
    cal_flops = CAL_PIXELS * count_flops(CAL_PAIRS, CAL_DATES - 1)["total"]
    print(
        f"\n校正: Galapagos {cal_flops / 1e12:.1f} TFLOP から逆算した実効スループット "
        f"CPU {cal_flops / CAL_CPU_SEC / 1e9:.1f} GFLOPS / "
        f"GPU {cal_flops / CAL_GPU_SEC / 1e9:.0f} GFLOPS"
    )


if __name__ == "__main__":
    main()
