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

## ベンチマーク report (commit 固定、2026-10-07 時点の最新)

| 内容 | ポスターでの使用 | permalink |
| --- | --- | --- |
| 18 step baseline、`invert_network` 43.5% と 18 step の internal 内訳 (横棒) | block 1 | [report_baseline.md @ 0a60cd4](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/0a60cd4/reports/report_baseline.md) |
| GPU batched QR 1.43× | block 4 | [report_torch.md @ 039d176](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/039d176/reports/report_torch.md) |
| プロファイル (82% が QR、384 万 launches) | block 4 | [report_profile.md @ 039d176](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/039d176/reports/report_profile.md) |
| **S1** QR vs Cholesky 同一 GPU、16.5× | block 4 | [report_solver_comparison.md @ 039d176](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/039d176/reports/report_solver_comparison.md) |
| **S2** Galápagos 大シーン、36.4× / 44.4× | block 5 | [report_large_scene.md @ 8bd51d0](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/8bd51d0/reports/report_large_scene.md) |
| **S3** 5 シーン E2E、5.3–93.8×、数値 gate | block 5, 6 | [report_end_to_end_bench.md @ 0fbf71b](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/0fbf71b/reports/report_end_to_end_bench.md) |
| `correct_topography` 5 シーン、6.15× | block 5 | [dem_error/report_bench_survey.md @ 3f4b8ea](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/3f4b8ea/reports/dem_error/report_bench_survey.md) |
| **条件数サーベイ** κ₂(G) 11–55 | block 6 | [report_condition_number.md @ d74df50](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/d74df50/reports/report_condition_number.md) |
| 条件数の計測ツール | — | [tools/measure_design_matrix_cond.py](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark/blob/d74df50/tools/measure_design_matrix_cond.py) |

## 実装 (フォーク)

| ファイル | 中身 |
| --- | --- |
| `src/mintpy/gpu/ifgram_inversion.py` | `estimate_timeseries_batch`, `_solve_cholesky` |
| `src/mintpy/gpu/_common.py` | `solve_normal_equations_batched`, `auto_chunk_size` |
| `src/mintpy/gpu/dem_error.py` | `correct_topography` の GPU 経路 |
| `docs/gpu.md` | ユーザー向け設定方法 (block 7 "Try it" の出典) |

## データ (Zenodo、5 シーン)

| シーン | 処理系 / バンド | Zenodo |
| --- | --- | --- |
| FernandinaSenDT128 | ISCE-2 / C | <https://zenodo.org/records/3952953> |
| GalapagosSenDT128 | ISCE-2 / C | <https://zenodo.org/records/4743058> |
| SanFranBaySenD42 | GMTSAR / C | <https://zenodo.org/records/15814132> |
| KujuAlosAT422F650 | ROI_PAC / L | <https://zenodo.org/records/3952917> |
| SanFranSenDT42 | ARIA / C | <https://zenodo.org/records/4265413> |

## 学会

| 内容 | URL |
| --- | --- |
| TASTI 2026 トップ | <https://tasti2026.conf.tw/> |
| Call for Papers = Presenter Guidelines (ポスター要件) | <https://tasti2026.conf.tw/site/mypage53.aspx?pid=101&lang=en&sid=1691> |
| 参加登録 (締切 2026-10-13) | <https://tasti2026.conf.tw/site/mypage53.aspx?pid=127&lang=en&sid=1691> |
| Agenda | <https://tasti2026.conf.tw/site/order/1691/sp_agenda.aspx?pid=901&sid=1691&lang=en> |
| FAQ | <https://tasti2026.conf.tw/site/mypage53.aspx?pid=23&lang=en&sid=1691> |

## References (ポスター末尾、抄録と同じ番号)

1. NASA-ISRO SAR (NISAR) Mission Science Users' Handbook, NASA JPL, 2018.
2. Z. Yunjun, H. Fattahi, F. Amelung, "Small baseline InSAR time series analysis: Unwrapping error correction and noise reduction," *Computers & Geosciences*, 133, 104331, 2019. <https://doi.org/10.1016/j.cageo.2019.104331>
3. Y. Yamamoto, Y. Nakatsukasa, Y. Yanagisawa, T. Fukaya, "Roundoff error analysis of the CholeskyQR2 algorithm," *ETNA*, 44, 306–326, 2015.
4. T. Fukaya, Y. Nakatsukasa, Y. Yanagisawa, Y. Yamamoto, "CholeskyQR2: A simple and communication-avoiding algorithm for computing a tall-skinny QR factorization on a large-scale parallel system," METR 2014-37, The University of Tokyo, 2014.
5. A. Paszke et al., "PyTorch: An imperative style, high-performance deep learning library," *NeurIPS*, 32, 2019.
6. Taiwan Space Agency (TASA), FORMOSAT-9 mission. <https://www.tasa.org.tw/en-US/missions/detail/FORMOSAT-9>
7. S. Sasaki, "Add opt-in torch GPU solver for invert_network," insarlab/MintPy, Pull Request #1490, 2026 (under review). <https://github.com/insarlab/MintPy/pull/1490>

文献 3, 4 の PDF は抄録 repo の `docs/` にあった (git 管理外)。必要なら再取得:
ETNA 44 は <https://etna.math.kent.edu/>、METR 2014-37 は東大 数理情報学専攻の
Technical Report ページ。
