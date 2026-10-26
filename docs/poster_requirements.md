# ポスター要件 — TASTI 2026

出典: 受理メール (2026-10-07、`no-reply@conf.tw`) と、メール中の "Presenter Guidelines"
リンク先 = Call for Papers ページ
<https://tasti2026.conf.tw/site/mypage53.aspx?pid=101&lang=en&sid=1691> (2026-10-07 閲覧)。

## 公式要件

| 項目 | 要件 | 本リポジトリでの対応 |
| --- | --- | --- |
| **サイズ** | **84.1 cm (width) × 118.9 cm (height)、"straight A0 size"** | `poster.tex`: `beamerposter` の `size=a0, orientation=portrait`。`make check` で 2384 × 3370 pt を確認 |
| 向き | 明記なし。幅 < 高さなので縦 | 縦 |
| 書式 | 自由 ("complete freedom … figures, tables, text, photographs, etc.") | — |
| **上部に必須** | **タイトル・Paper No.・著者名** を prominently | headline にタイトル・著者、右上に "Paper No. T0043" バッジ |
| 記載必須 | 著者名・所属・メールアドレス | headline の institute 行 |
| 印刷 | **各自で印刷して持参**。主催者は印刷しない | → §印刷 |
| 言語 | 英語 (抄録と同じ) | 英語 |

## 日程

| 日時 | 内容 | 場所 |
| --- | --- | --- |
| **2026-10-13** | **参加登録締切** | <https://tasti2026.conf.tw/site/mypage53.aspx?pid=127&lang=en&sid=1691> |
| 2026-11-07 15:00–17:00 | 搬入 (設営) 1 回目 | Tayouan D, 3F |
| 2026-11-08 08:30–12:00 | 搬入 (設営) 2 回目 | Tayouan D, 3F |
| **2026-11-10 11:30–14:00** | **ポスターセッション (在席)** | Tayouan D, 3F |
| 2026-11-11 12:00–14:00 | 撤去。**回収しなかったポスターは処分される** | Tayouan D, 3F |

- CfP ページの会期表記は "November 7–10" だが、撤去は 11/11 なので 11/11 まで会場にある。
  抄録 repo の "8–11 November" と食い違うので、**ポスターの footline には日付の範囲を書かず
  セッション日時だけ**を書いてある。
- 発表者本人がセッション中ポスターの前に立つ (口頭説明は自由)。

## 印刷の段取り (提案)

| 選択肢 | 長所 | 短所 |
| --- | --- | --- |
| **A. 日本で印刷して持参 (推奨)** | 仕上がりを事前に確認できる。入稿〜受取 3–5 営業日 | 筒 (ポスターケース) で機内持ち込み。折り目に注意 |
| B. 台南で印刷 | 荷物が減る | 現地業者の当たりをつける必要。トラブル時のリカバリが効かない |
| C. 布ポスター | 折って持ち運べる | 細い線 (SVG の 1 px 罫線) が潰れやすい。色味も沈む |

- 紙: マット合成紙 (耐水・耐折) か、通常のマットコート紙。光沢紙は会場照明で反射する。テカリは紙の仕上げで決まる (白地はインクの乗らない紙そのもの)
- 地色: 2026-10-27 から地が暖色 `#F6F1E7` で、左右の端まで届く (上下の紺の帯も同じ)。業者に**フチなし印刷か、塗り足しが要るか**を確認する。白いフチが出ると白地のときより目立つ。淡いベタ面は大判インクジェットでムラや CMYK 変換での黄み寄りが出やすいので、校正 PDF か出力見本が出せるなら確認
- 色: `beamerthemetasti2026.sty` の青 (#1A6FB5) / 橙 (#C8641E) は RGB。業者が CMYK 変換するので
  校正 PDF を出してもらえるなら確認
- **入稿目安: 2026-11-01 まで** (`make print` → `print/poster_YYYY-MM-DD.pdf`)
- 予備: A4 縮刷版を 20 部ほど持参して立ち話で配る (`pdftoppm` or `pdfjam` で縮小)

## Zenodo (ポスター PDF の公開)

block 7 の 2 つ目の QR は、ポスター PDF の Zenodo の記録の **concept DOI**
(`https://doi.org/10.5281/zenodo.23669874`、常に最新版に解決する) を指す。

| 版 | version DOI | ファイル | 中身 |
| --- | --- | --- | --- |
| v1 | 10.5281/zenodo.23669875 | `poster.pdf` (md5 `b5dcb701…`) | 旧所属 "Earthsea Wizard, Japan"、QR → v1 |
| **v2 (最新)** | 10.5281/zenodo.23673961 | `print/poster_2026-10-27.pdf` (md5 `d14b0f218892b24c91b63993020c8ac5`) に差し替える | 所属 "Earthsea Wizard Tech Lab, Japan"、QR → concept DOI |

- 経緯 (2026-10-27): v1 の DOI を下書きで予約し、QR をその version DOI にして publish した。
  所属を直したあと、ファイルの差し替えのつもりが New version (v2) になり、QR (v1) と印刷する PDF (v2) が
  ずれた。concept DOI はもう決まっていたので、QR を concept DOI にした PDF を作り直し、v2 のファイルを
  Edit published files で差し替える ([poster_plan.md](poster_plan.md) 判断 36・37)
- 予約で取れるのは version DOI で、concept DOI は初版の publish で決まる。予約した DOI は
  **publish するまで解決しない** (QR を読むと 404) し、保証もされない。**下書きを消すと DOI は戻らない**
- これから: QR は concept DOI なので、New version を出しても QR は最新版に着く。
  ファイルだけ直すなら Edit published files (v2 は 2026-11-25 頃まで)。
  Description・Keywords and subjects・Conference は空欄で公開したので、あとで足す
  (メタデータの編集では新しい版はできない)
- 順番 (推奨): `make print` → 同じ `print/poster_YYYY-MM-DD.pdf` を下書きに上げて publish →
  画面に出した PDF の QR を実機で読み、Zenodo に着くことを確かめる → 入稿。
  こうすると、印刷前に QR の先まで確かめられる
- publish 後の修正: **30 日以内**なら DOI を変えずにファイルを差し替えられる (小さな修正だけ)。
  それより後や大きな変更は **New version** (新しい version DOI。旧版のページに新しい版の案内が出る)。
  publish した記録は消せない
- メタデータ (案):
  - Resource type: Poster。Title は受理されたタイトル、Creator は Syota Sasaki (Earthsea Wizard Tech Lab、ORCID つき)
  - Related works (Relation / Scheme / Resource type)。DataCite に「リポジトリ」「PR」の型はないので近いものを使う:
    - 本リポジトリ: Is supplemented by / URL / Software (LaTeX と build スクリプト、MIT。GitHub 連携の取り込みも Software)
    - PR #1490: Cites / URL / Software (ポスターの [7])
    - 5 シーンのデータ: Cites / DOI / Dataset (References 帯の "Benchmark data"。`10.5281/zenodo.3952953` の形で入れる、番号は [sources.md](sources.md) §データ)
    - mintpy-benchmark は入れない (将来 private 化の可能性、[sources.md](sources.md) 冒頭)
  - Subjects: Zenodo に OECD の FOS そのものはなく ("FOS" で検索すると MeSH の遺伝子 fos が出る)、
    FOS を土台にした **EuroSciVoc** から選ぶ: Remote sensing / Geophysics / Numerical analysis /
    Linear algebra / Software (2026-10-27 に `https://zenodo.org/api/subjects` で存在を確認)。
    GPU・並列計算にあたる語はどの語彙にもないので Keywords に任せる
  - Conference: TASTI 2026, Tainan, Taiwan。日付はセッション日 (2026-11-10) だけにする
    (会期の範囲は抄録 repo と CfP で食い違う → §日程)
  - License: **CC BY 4.0** (2026-10-27 に Syota さんが決定。ベンチマークのデータも 5 件とも CC BY 4.0)
- publish 後に README と [sources.md](sources.md) へ DOI を書いた (2026-10-27)

参考: [Reserve DOI](https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/)、
[Manage versions](https://help.zenodo.org/docs/deposit/manage-versions/)、
[Manage files (30 日)](https://help.zenodo.org/docs/deposit/manage-files/)

## 持ち物

- ポスター本体 (筒)
- 画鋲・テープは会場支給が普通だが、念のためマスキングテープ少量
- A4 縮刷版 + 名刺
- 抄録 PDF・ポスター PDF をスマホ/タブレットにも入れておく (QR の先が開けないときの保険)

## 提出前 (印刷前) チェックリスト

- [ ] `make check` が OK (A0、1 ページ、全フォント埋め込み)
- [ ] 業者にフチなし印刷 / 塗り足しの要否を確認した (地色と紺の帯が端まで届く)
- [ ] `make preview` で全ブロックが切れていない (下端の References まで入っている)
- [ ] タイトル・Paper No. T0043・著者名が上部に大きくある
- [ ] 所属 "Earthsea Wizard Tech Lab, Japan" (Zenodo の所属と同じ) とメールアドレスがある
- [ ] 数値の系列が [results.md](results.md) と一致 (S1 の 3 条件、規模依存なし)
- [ ] block 7 の PR #1490 の記述が現状と一致 (`gh pr view 1490 --repo insarlab/MintPy`)
- [ ] 印刷する PDF が Zenodo の最新版 (concept DOI 10.5281/zenodo.23669874 → v2) のファイルと md5 で一致する (→ §Zenodo)
- [ ] QR コード 2 つが実機で読める (PR / Zenodo のポスター PDF)。Zenodo 側は publish 前だと 404
- [ ] 1 m 離れて本文が読める (目安: 本文 ≥ 24 pt、キャプション ≥ 18 pt)
- [ ] 参加登録済み (2026-10-13 まで)
