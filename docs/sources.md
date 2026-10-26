# リンク集 — ポスターの全出典 (permalink)

mintpy-benchmark の report は**将来 private 化の可能性**があるため commit SHA を固定して引く。
upstream (insarlab/MintPy) と Zenodo は消えない前提。

## リポジトリ

| 役割 | URL |
| --- | --- |
| upstream PR | <https://github.com/insarlab/MintPy/pull/1490> |
| 開発フォーク | <https://github.com/s-sasaki-earthsea-wizard/MintPy> |
| フォークの GPU ドキュメント | <https://github.com/s-sasaki-earthsea-wizard/MintPy/blob/main/docs/gpu.md> |
| ベンチ harness / report | <https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark> |
| 抄録 (受理版) | <https://github.com/s-sasaki-earthsea-wizard/tasti2026-abstract> |
| LT スライド (図の出典) | <https://github.com/s-sasaki-earthsea-wizard/vrc-insar-batched-cholesky-LT> |
| 本リポジトリ | <https://github.com/s-sasaki-earthsea-wizard/tasti2026-poster> |
| ポスター PDF (Zenodo、concept DOI = block 7 の QR) | <https://doi.org/10.5281/zenodo.23669874> (常に最新版、CC BY 4.0。v1 <https://doi.org/10.5281/zenodo.23669875> = 旧所属、v2 <https://doi.org/10.5281/zenodo.23673961> = 印刷版。2026-10-27 公開) |

## ベンチマーク report (commit 固定、2026-10-07 時点の最新)

| 内容 | ポスターでの使用 | permalink |
| --- | --- | --- |
| 18 step baseline、`invert_network` 43.5% と 18 step の internal 内訳 (横棒) | block 1 | [report_baseline.md @ 0a60cd4](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/0a60cd4/reports/report_baseline.md) |
| GPU QR (`torch.linalg.lstsq`) 1.43× | block 4 | [report_torch.md @ 039d176](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/039d176/reports/report_torch.md) |
| プロファイル (82% が QR、384 万 launches) | block 4 | [report_profile.md @ 039d176](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/039d176/reports/report_profile.md) |
| **S1** QR vs Cholesky 同一 GPU、16.5× | block 4 | [report_solver_comparison.md @ 039d176](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/039d176/reports/report_solver_comparison.md) |
| S1 の kernel 内訳 (QR 1 画素 198 本、Cholesky 57 本、launch 18.2 s vs kernel 10.4 s) | block 4 の図 2 枚 | [report_solver_comparison.md §4 @ 039d176](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/039d176/reports/report_solver_comparison.md#4-gpu-kernel-breakdown-per-chunk) |
| **S2** Galápagos 大シーン、36.4× / 44.4× | block 5 | [report_large_scene.md @ 8bd51d0](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/8bd51d0/reports/report_large_scene.md) |
| **S3** 5 シーン E2E、5.3–93.8×、数値 gate | block 5, 6 | [report_end_to_end_bench.md @ 0fbf71b](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/0fbf71b/reports/report_end_to_end_bench.md) |
| `correct_topography` 5 シーン、6.15× | block 5 | [dem_error/report_bench_survey.md @ 3f4b8ea](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/3f4b8ea/reports/dem_error/report_bench_survey.md) |
| **条件数サーベイ** κ₂(G) 11–55 | block 6 | [report_condition_number.md @ d74df50](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/d74df50/reports/report_condition_number.md) |
| 条件数の計測ツール | — | [tools/measure_design_matrix_cond.py](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/d74df50/tools/measure_design_matrix_cond.py) |

## 実装 (フォーク)

フォーク `main` は `src/mintpy/gpu/` に分離。upstream PR #1490 (`gpu_torch_solver`) は同じ計算を単一モジュールに置いている。

| ファイル | 中身 |
| --- | --- |
| [PR #1490 `src/mintpy/ifgram_inversion_gpu.py` L111–127 @ 086d162](https://github.com/s-sasaki-earthsea-wizard/MintPy/blob/086d16217ef7052766f80f62e8bc7b88c80fa262/src/mintpy/ifgram_inversion_gpu.py#L111-L127) | `_solve_cholesky`: `Gw_T @ Gw` (バッチ GEMM) → `cholesky_ex` → `cholesky_solve`。block 4 の `normal_equations_batched` の根拠 |
| `src/mintpy/gpu/ifgram_inversion.py` | `estimate_timeseries_batch`, `_solve_cholesky` |
| `src/mintpy/gpu/_common.py` | `solve_normal_equations_batched`, `auto_chunk_size` |
| `src/mintpy/gpu/dem_error.py` | `correct_topography` の GPU 経路 |
| `docs/gpu.md` | ユーザー向け設定方法 (block 7 "Try it" の出典) |

## PyTorch (QR 経路のディスパッチ、計測環境の torch 2.11.0)

| 箇所 | 中身 |
| --- | --- |
| [`lstsq_kernel` @ v2.11.0](https://github.com/pytorch/pytorch/blob/v2.11.0/aten/src/ATen/native/cuda/linalg/BatchLinearAlgebra.cpp#L2098-L2117) | cuBLAS `gelsBatched` は K ≤ 256 かつ batch ≥ max(2, K/16) のときだけ。それ以外は `linalg_lstsq_gels` (geqrf + ormqr + 三角ソルブ) |
| [`apply_geqrf` のループ @ v2.11.0](https://github.com/pytorch/pytorch/blob/v2.11.0/aten/src/ATen/native/cuda/linalg/BatchLinearAlgebraLib.cpp#L1002) | cuSOLVER `geqrf` を画素ごとに呼ぶ |
| [`apply_ormqr` のループ @ v2.11.0](https://github.com/pytorch/pytorch/blob/v2.11.0/aten/src/ATen/native/cuda/linalg/BatchLinearAlgebraLib.cpp#L1098) | cuSOLVER `ormqr` を画素ごとに呼ぶ |
| [`cholesky_helper_cusolver` @ v2.11.0](https://github.com/pytorch/pytorch/blob/v2.11.0/aten/src/ATen/native/cuda/linalg/BatchLinearAlgebraLib.cpp#L800-L814) | batch > 1 なら cuSOLVER `potrfBatched` (1 回の呼び出しで全画素) |

## データ (Zenodo、5 シーン)

ポスターでは References 帯の "Benchmark data:" に、シーン名と version DOI の番号だけを載せている
([poster_plan.md](poster_plan.md) 判断 35)。5 件とも CC BY 4.0。version DOI は使った版を指す
(concept DOI は最新版に解決されるので使わない)。

| ポスターの呼び名 | データ名 | 処理系 / バンド | 出所 | Zenodo (version DOI) | 版 |
| --- | --- | --- | --- | --- | --- |
| Fernandina | FernandinaSenDT128 | ISCE-2 / C | MintPy example | [10.5281/zenodo.3952953](https://doi.org/10.5281/zenodo.3952953) | 1.6 |
| Galápagos | GalapagosSenDT128 | ISCE-2 / C | [2] のデータ | [10.5281/zenodo.4743058](https://doi.org/10.5281/zenodo.4743058) | 1.1 |
| San Francisco Bay | SanFranBaySenD42 | GMTSAR / C | MintPy example | [10.5281/zenodo.15814132](https://doi.org/10.5281/zenodo.15814132) | 1.1 |
| Kuju | KujuAlosAT422F650 | ROI_PAC / L | MintPy example | [10.5281/zenodo.3952917](https://doi.org/10.5281/zenodo.3952917) | 1.4 |
| San Francisco | SanFranSenDT42 | ARIA / C | MintPy example | [10.5281/zenodo.4265413](https://doi.org/10.5281/zenodo.4265413) | 1.0 |

「MintPy example」は upstream の
[`docs/demo_dataset.md`](https://github.com/insarlab/MintPy/blob/main/docs/demo_dataset.md) に載っているもの。
Galápagos はそこになく、[2] (Yunjun et al., 2019) のデータとして公開されたレコード (ALOS と Sentinel-1 の
2 stack を含む。使ったのは Sentinel-1)。MintPy の README や CLI のヘルプでは使用例の名前として出てくる。

正式なデータ引用 (DataCite の形、Zenodo API で 2026-10-27 に確認):

- Z. Yunjun, F. Amelung (2019). *InSAR stack of Fernandina volcano in Galápagos, Ecuador from Sentinel-1 descending track 128* (Version 1.6) [Data set]. Zenodo. <https://doi.org/10.5281/zenodo.3952953>
- Z. Yunjun, F. Amelung (2019). *InSAR time-series for Galápagos volcanoes, Ecuador from ALOS and Sentinel-1* (Version 1.1) [Data set]. Zenodo. <https://doi.org/10.5281/zenodo.4743058>
- Z. Yunjun, F. Amelung, Y. Aoki (2017). *InSAR stack of Kuju volcano in Kyushu, Japan from ALOS ascending track 422 processed with ROI_PAC* (Version 1.4) [Data set]. Zenodo. <https://doi.org/10.5281/zenodo.3952917>
- H. Fattahi, Z. Yunjun (2020). *InSAR Stack of San Francisco Bay in California from Sentinel-1* (Version 1.0) [Data set]. Zenodo. <https://doi.org/10.5281/zenodo.4265413>
- X. Xu, Z. Yunjun (2024). *InSAR stack of San Francisco Bay, California from Sentinel-1 descending track 42 processed with GMTSAR* (Version 1.1) [Data set]. Zenodo. <https://doi.org/10.5281/zenodo.15814132>

ARIA の San Francisco (4265413) は Zenodo 上のタイトルが "San Francisco Bay" なので、GMTSAR の
San Francisco Bay (15814132) と取り違えないこと。

## 学会

| 内容 | URL |
| --- | --- |
| TASTI 2026 トップ | <https://tasti2026.conf.tw/> |
| Call for Papers = Presenter Guidelines (ポスター要件) | <https://tasti2026.conf.tw/site/mypage53.aspx?pid=101&lang=en&sid=1691> |
| 参加登録 (締切 2026-10-13) | <https://tasti2026.conf.tw/site/mypage53.aspx?pid=127&lang=en&sid=1691> |
| Agenda | <https://tasti2026.conf.tw/site/order/1691/sp_agenda.aspx?pid=901&sid=1691&lang=en> |
| FAQ | <https://tasti2026.conf.tw/site/mypage53.aspx?pid=23&lang=en&sid=1691> |

## References (ポスター末尾、ポスターでの登場順)

抄録と同じ 7 件を、ポスターに出てくる順に振り直した ([poster_plan.md](poster_plan.md) 判断 35)。
抄録の番号との対応: 抄録 [3] → ポスター [4]、抄録 [4] → [5]、抄録 [5] → [3]。1・2・6・7 は同じ。

1. NASA-ISRO SAR (NISAR) Mission Science Users' Handbook, NASA JPL, 2018.
2. Z. Yunjun, H. Fattahi, F. Amelung, "Small baseline InSAR time series analysis: Unwrapping error correction and noise reduction," *Computers & Geosciences*, 133, 104331, 2019. <https://doi.org/10.1016/j.cageo.2019.104331>
3. A. Paszke et al., "PyTorch: An imperative style, high-performance deep learning library," *NeurIPS*, 32, 2019.
4. Y. Yamamoto, Y. Nakatsukasa, Y. Yanagisawa, T. Fukaya, "Roundoff error analysis of the CholeskyQR2 algorithm," *ETNA*, 44, 306–326, 2015.
5. T. Fukaya, Y. Nakatsukasa, Y. Yanagisawa, Y. Yamamoto, "CholeskyQR2: A simple and communication-avoiding algorithm for computing a tall-skinny QR factorization on a large-scale parallel system," METR 2014-37, The University of Tokyo, 2014.
6. Taiwan Space Agency, FORMOSAT-9. <https://www.tasa.org.tw/en-US/missions/detail/FORMOSAT-9>
7. S. Sasaki, "Add opt-in torch GPU solver for invert_network," insarlab/MintPy, Pull Request #1490, 2026 (under review). <https://github.com/insarlab/MintPy/pull/1490>

その後に番号なしで **Benchmark data:** InSAR stacks on Zenodo by Z. Yunjun and co-authors,
DOI 10.5281/zenodo.⟨n⟩: Fernandina 3952953, Galápagos 4743058 (data of [2]), Kuju 3952917,
San Francisco 4265413, San Francisco Bay 15814132. (正式な引用は §データ)

文献 4, 5 の PDF は抄録 repo の `docs/` にあった (git 管理外)。必要なら再取得:
ETNA 44 は <https://etna.math.kent.edu/>、METR 2014-37 は東大 数理情報学専攻の
Technical Report ページ。
