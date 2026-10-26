# tasti2026-poster

## プロジェクト概要

**TASTI 2026 (Paper No. T0043, ポスター発表) のポスター**を作るリポジトリ。
[insarlab/MintPy#1490](https://github.com/insarlab/MintPy/pull/1490) (MintPy の
PyTorch GPU solver) の成果を、宇宙科学・衛星技術・産業の国際的な聴衆に向けて
A0 ポスター 1 枚にまとめる。

- 抄録は [tasti2026-abstract](https://github.com/s-sasaki-earthsea-wizard/tasti2026-abstract)
  で **2026-08-06 に提出・凍結、2026-10-07 に受理**。抄録の文言は追わない。
  **投稿後の進展 (PR の rebase、条件数サーベイなど) はこちらに載せる**。
- 図の大半は姉妹 repo
  [vrc-insar-batched-cholesky-LT](https://github.com/s-sasaki-earthsea-wizard/vrc-insar-batched-cholesky-LT)
  の日本語 SVG を英語化したもの。
- 発表当日: **2026-11-10 11:30–14:00、Tayouan D (3F)**。要件は
  [docs/poster_requirements.md](docs/poster_requirements.md)。

## 最初に読むもの

1. [HANDOVER.md](HANDOVER.md) — 現状と次の作業
2. [docs/poster_plan.md](docs/poster_plan.md) — ブロックごとの内容と判断の記録
3. [docs/results.md](docs/results.md) — **数字の正典。系列 (S1/S2/S3) を混ぜない、
   規模依存を主張しない**。数字を触る前に必ず読む
4. [docs/sources.md](docs/sources.md) — 全リンク (commit 固定 permalink)

## 言語設定

- ユーザへの応答は **日本語**
- `docs/`・`HANDOVER.md`・`.claude-notes/` は日本語
- `poster.tex`・`*.sty`・`scripts/`・`Makefile`・`README.md` と、その中の
  コメント/docstring は **英語**
- ポスター本文は英語

## 開発ルール

### ビルド

```bash
make            # poster.pdf (figures/src/*.svg → figures/*.pdf, fig2 は python)
make preview    # preview/poster.png
make check      # A0 / 1 ページ / フォント埋め込み
make print      # print/poster_<date>.pdf
```

- `rsvg-convert` (librsvg) と `pdftoppm` (poppler) が必要。`brew install librsvg poppler`
- `*.pdf` は `.gitignore` で無視。例外は `print/*.pdf` (実際に印刷した版)
- `figures/src/ja/` の日本語 SVG はビルド対象外。英語化したら `figures/src/` に置く

### 数字の扱い (最重要)

- [docs/results.md](docs/results.md) の表と系列名で照合してから書く
- **S1 (同一 GPU で QR→Cholesky、16.5×) を載せるときは 3 条件を必ず添える**:
  比較の両側 (GPU QR vs GPU Cholesky) / シーン (Fernandina) / MintPy が報告する
  step 時間 (起動除く)。"solver core" とは書かない (読み込み・重み計算も含む)
- **S1 の step wall 4.49× は載せない**。両側に約 47 s の起動コスト (NAS 上の venv
  からの torch import) が乗った値で、solver の比較として正当でない
- 系列ごとに Python 環境が違う (Phase 1〜S2 は numpy 2.4.4、S3 は numpy 1.26.4 で
  CPU ループが遅い)。詳細は [docs/results.md](docs/results.md) §計測環境の検証
- **規模依存 (「大きいほど速い」) は主張しない**。S3 の実データで成立しない
- NISAR の数字は**外挿**。"extrapolated from measured throughput" を必ず添える
- FORMOSAT-9 は地域文脈のみ。分解能の数字は書かない
- PR #1490 の状態は `gh pr view 1490 --repo insarlab/MintPy` で**印刷直前に再確認**

### コーディング規約

- Python: PEP 8、関数名 snake_case、Docstring は Google Style
- LaTeX: 1 文 1 行 (semantic line breaks)。ブロックの先頭にコメントで意図を書く
- SVG: `<text>` 要素に英語を直書き。パレットは `#1a6fb5` (青) / `#c8641e` (橙)

### Git 運用

- ブランチ戦略: `feature/*`, `fix/*`, `refactor/*`。PR は main へ
- コミットメッセージ: 英文、動詞始まり、絵文字プレフィックス
  (✨ feat / 🐞 fix / 📚 docs / 🎨 style / 🛠️ refactor / ⚡ perf / ✅ test /
  🏗️ chore / 🚀 deploy / 🔒 security / 📝 update / 🗑️ remove)
- 1 コミット = 1 つの主要な変更

**重要**: Claude Code を使用してコミットする場合は、必ず以下の署名を含める:

```text
🤖 Assisted by [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### セッション記録

- セッションの記録は `.claude-notes/` に残す (git 管理外)
- 申し送りは [HANDOVER.md](HANDOVER.md) を更新する (git 管理)

## ディレクトリ構成

```text
.
├── CLAUDE.md                     # 本ファイル
├── README.md                     # 英語の概要・ビルド手順・日程
├── HANDOVER.md                   # 申し送り (日本語)
├── LICENSE                       # MIT
├── Makefile                      # make / figures / preview / check / print / clean
├── poster.tex                    # ポスター本体 (beamerposter, A0 縦, 3 カラム)
├── beamerthemetasti2026.sty      # テーマ (紺のマストヘッド + ロゴ、罫線のブロック、References 帯。図と同じパレット)
├── figures/
│   ├── images/                   # ロゴ (earthsea-wizard-logo.png、マストヘッドで使用)
│   ├── src/*.svg                 # 英語化済み図 (make が PDF 化)
│   └── src/ja/*.ja.svg           # 未英語化の候補 (ビルド対象外)
├── scripts/
│   ├── plot_speedup.py           # Fig. 2 (5 シーン speedup、S3 系列)
│   └── estimate_scale.py         # NISAR 規模の見積もり (Q&A 用、ポスターには載せない)
├── docs/
│   ├── project_overview.md       # 何を・誰に・どこで
│   ├── poster_requirements.md    # A0、搬入/撤去、必須記載、印刷の段取り
│   ├── poster_plan.md            # ブロック別の内容・図・数字の系列・判断の記録
│   ├── results.md                # ベンチ数値の正典 (+ 投稿後の新結果)
│   ├── numerical_method.md       # 手法の数理 (WLS / 正規方程式 / Cholesky / 条件数)
│   ├── compute_scale.md          # NISAR スケール外挿
│   ├── qa_prep.md                # ポスターセッションの想定問答
│   ├── accepted_abstract.md      # 受理された抄録のメタデータ (凍結)
│   └── sources.md                # 全リンク集 (permalink)
└── print/                        # 実際に印刷した PDF (日付つき)
```
