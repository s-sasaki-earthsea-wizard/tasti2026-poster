# プロジェクト概要 — TASTI 2026 ポスター (T0043)

## 何をするか

[insarlab/MintPy#1490](https://github.com/insarlab/MintPy/pull/1490) (MintPy の
PyTorch GPU solver) の成果を、**TASTI 2026 のポスターセッション**で発表する。
抄録は 2026-08-06 に提出、2026-10-07 に **ポスター発表として受理** (Paper No. T0043)。

| 項目 | 値 |
| --- | --- |
| 学会 | TASTI 2026 — Taiwan International Assembly of Space Science, Technology, and Industry |
| 会場 | International Convention Center, Tainan, Taiwan |
| セッション | **ポスター、2026-11-10 11:30–14:00、Tayouan D (3F)** |
| トピック | 02 Space Applications and Services / **0201 Earth Observation and Remote Sensing** |
| サイズ | **A0 (84.1 cm × 118.9 cm)** |
| 発表者 | Syota Sasaki (Earthsea Wizard Tech Lab, Japan) |

## 聴衆と核心メッセージ

聴衆は宇宙科学・衛星技術・産業応用の国際コミュニティで、数値線形代数の専門家ではない。
抄録と同じく、前面に出すのは:

1. **NISAR 時代のデータ量問題** — 処理スループットが取得速度に追いつかない
2. **コンシューマ GPU 1 枚で 5–94×** — HPC クラスタ不要、防災実務者にも手が届く
3. **正しさの担保** — 速いだけでなく数値一致 gate を 5 シーンで通過

ポスターは抄録より面積があるので、抄録で裏方に回した **条件数の議論** を
block 6 として表に出す (立ち話で「float32 で大丈夫?」は最頻出のため)。
数学の深掘りは姉妹 LT の
[numerical_method.md](https://github.com/s-sasaki-earthsea-wizard/vrc-insar-batched-cholesky-LT/blob/main/docs/numerical_method.md)
が正。

> 核心メッセージ (1 文): InSAR 時系列解析の最重ステップを正規方程式 + batched
> Cholesky で GPU 化し、**コンシューマ GPU 1 枚**で 5–94× の高速化と数値一致 gate
> 通過を両立。NISAR 時代のデータ量に耐える処理を「クラスタなしで」手が届くものにした。

## 関連リポジトリ

| リポジトリ | 役割 |
| --- | --- |
| [s-sasaki-earthsea-wizard/MintPy](https://github.com/s-sasaki-earthsea-wizard/MintPy) | 開発フォーク。実装本体 (`src/mintpy/gpu/`)、`docs/gpu.md` |
| [mintpy-benchmark](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark) | ベンチ harness と report。**ポスターの数字は全部ここ由来** |
| [tasti2026-abstract](https://github.com/s-sasaki-earthsea-wizard/tasti2026-abstract) | 受理された抄録 (2026-08-06 凍結)。`docs/` の大半は本リポジトリにコピー済み |
| [vrc-insar-batched-cholesky-LT](https://github.com/s-sasaki-earthsea-wizard/vrc-insar-batched-cholesky-LT) | 数学談話会 LT (日本語)。図の出典 |
| [insarlab/MintPy](https://github.com/insarlab/MintPy) | upstream。PR #1490 |

全リンクの permalink は [sources.md](sources.md)。

## 抄録との関係

- 抄録は投稿時点 (2026-08-06) のスナップショットとして**凍結**。ポスターは**抄録と
  矛盾しない範囲で新しい結果を足す**。足したものは [HANDOVER.md](../HANDOVER.md) §1 と
  [poster_plan.md](poster_plan.md) に列挙してある。
- 受理された抄録のメタデータ (タイトル・short abstract・keywords) は
  [accepted_abstract.md](accepted_abstract.md)。ポスターのタイトル・著者表記はこれに合わせる。

## ドキュメント構成

| doc | 中身 |
| --- | --- |
| [poster_requirements.md](poster_requirements.md) | 公式要件 (サイズ・必須記載・搬入撤去)、印刷の段取り、チェックリスト |
| [poster_plan.md](poster_plan.md) | ブロック別の内容・図・数字の系列、デザイン判断、未決事項 |
| [results.md](results.md) | ベンチ数値の正典 + 投稿後の新結果 (条件数サーベイ、DEM 5 シーン) |
| [numerical_method.md](numerical_method.md) | 手法の数理と実装の要点 (抄録 repo から) |
| [compute_scale.md](compute_scale.md) | NISAR スケール外挿 (抄録 repo から) |
| [qa_prep.md](qa_prep.md) | ポスターセッションの想定問答 (英語回答例つき) |
| [accepted_abstract.md](accepted_abstract.md) | 受理メールの内容 (凍結) |
| [sources.md](sources.md) | 全リンク集 |
