# ポスター説明の原稿と想定問答 (当日用・日英併記)

TASTI 2026 / Paper No. T0043 / 2026-11-10 11:30–14:00, Tayouan D (3F)

- 英語 (引用ブロック) は**読み上げる台本ではなく言い回しの見本**。図を指しながら、相手に合わせて端折る
- 各英文のすぐ下が日本語訳。「補足」は日本語だけのメモ
- 数字の正典は [results.md](results.md)、深掘りの問答は [qa_prep.md](qa_prep.md)。
  このメモはその当日用の抜粋と、InSAR を知らない人向けの追加

---

## 0. 立ち話の入り方

最初の一言で相手を振り分ける。

> Do you work with radar data, or is InSAR new to you?

レーダーのデータを扱ってる? それとも InSAR は初めて?

- **初めて** → §1-3 を「InSAR とは」から (block 2 の上半分)
- **InSAR の人** → block 1 の横棒 → block 4 (手法) → block 6 (精度)
- **GPU / HPC の人** → block 3「小さな最小二乗が数百万」→ block 4 → block 6
- 去り際に QR コード (PR とポスター PDF) を指す

---

## 1. 説明の原稿

### 1-1. 3 文版 (核になる主張)

> On one consumer GPU, the ground-motion inversion runs 44 times faster.

民生 GPU 1 枚で、地面の変動を求める逆解析が 44 倍速くなった。

> Getting there needed the math recast into a GPU-friendly form; a direct port gave only 1.43 times.

そのためには GPU 向けの形に数式を組み直す必要があった。そのまま移植しただけでは 1.43 倍止まり。

> That form costs accuracy in theory, but measured on real data the cost is micrometres, against millimetre signals.

その形は理論上は精度を落とすが、実データで測るとその代償はマイクロメートル。測りたい信号はミリメートル。

### 1-2. 30 秒版 (通りがかりの人に)

> This poster is about measuring how the ground moves from space, and making that computation much faster.

このポスターは、宇宙から地面の動きを測ること、そしてその計算を大幅に速くしたことについて。

> Radar satellites can track ground motion to the millimetre: volcanoes swelling, cities sinking, faults creeping.

レーダー衛星は地面の動きをミリ単位で追える。火山の膨張、都市の沈下、断層のずれ。

> Turning years of radar images into a motion history means solving millions of small least-squares problems, one per pixel, and in MintPy, the standard open-source tool, that is the single biggest step.

何年分ものレーダー画像を変動の履歴にするには、画素ごとに 1 つ、数百万個の小さな最小二乗問題を解く必要がある。標準的なオープンソースのツール MintPy では、それが一番重い処理。

> I moved it to a single consumer graphics card, and it got 44 times faster: from about 100 minutes to just over 2.

それを民生のグラフィックスカード 1 枚に載せたら 44 倍速くなった。約 100 分が 2 分ちょっとに。

> The trick was rewriting the math into a shape the GPU likes, and the accuracy cost of that rewrite is micrometres, far below what InSAR can measure.

コツは数式を GPU の得意な形に書き直したこと。その書き直しの精度の代償はマイクロメートルで、InSAR が測れる精度よりはるかに小さい。

- 補足: 100 分 = Galápagos の 6,169 s、2 分ちょっと = 139 s (S2)。「一番重い処理」は Fernandina の CPU 実行で 43.5 %

### 1-3. 3 分版 (足を止めてくれた人に、ブロック順)

反応を見て途中で切ってよい。InSAR の人には「InSAR とは」と「なぜ最小二乗か」を飛ばす。

#### InSAR とは (block 2 の上の箇条書きと網の図)

宇宙系でもリモートセンシング以外の人にはここから。

> Let me start with what InSAR is. A radar satellite, like Europe's Sentinel-1 or the new NISAR, sends microwaves down and records the echo, day or night, through clouds.

まず InSAR とは何か。欧州の Sentinel-1 や新しい NISAR のようなレーダー衛星は、地上にマイクロ波を送ってその反射を記録する。昼も夜も、雲があっても。

> The echo has a phase: where the wave is in its cycle when it comes back.

反射波には位相がある。戻ってきたとき波が 1 周期のどこにいるか、ということ。

> Image the same place twice; if the ground moved toward the satellite in between, even by millimetres, the phase shifts.

同じ場所を 2 回撮って、その間に地面が衛星の方へ動いていれば、たとえ数ミリでも位相がずれる。

> The phase difference of the two images is an interferogram. That's the "In" in InSAR: interferometric SAR.

2 枚の画像の位相差が干渉画像 (interferogram)。InSAR の "In" はこれ、干渉 SAR。

> Pairs far apart in time stop matching, so we make many short pairs and connect them into a network: dates are the dots, interferograms are the lines.

時間が離れたペアは像が合わなくなる (干渉しなくなる)。だから短いペアをたくさん作って網にする。日付が点、干渉画像が線。

- 補足: Sentinel-1 は波長 5.6 cm。位相 1 周 = 衛星方向に 2.8 cm (往復なので波長の半分)

#### なぜ最小二乗か (block 2 の三角形とお椀の図)

> Around a triangle of dates, the motions should add up: zero to one, plus one to two, equals zero to two.

3 つの日付の三角形では、動きの足し算が合うはず。0 から 1 と 1 から 2 を足せば 0 から 2。

> Real interferograms never add up exactly, because each one carries its own noise.

でも実際の干渉画像はそれぞれに固有の雑音を持つので、ぴったりは合わない。

> So for each pixel we look for the displacement history that fits all of them best: a weighted least-squares fit, where noisier interferograms count less. That's this bowl; we look for its bottom.

だから画素ごとに、全部の干渉画像に一番よく合う変動の履歴を探す。重みつき最小二乗で、雑音の多い干渉画像ほど軽く扱う。このお椀の底を探すということ。

> The weights differ from pixel to pixel, so every pixel is its own small problem. A scene has millions of them.

重みは画素ごとに違うので、画素ひとつひとつが別々の小さな問題になる。1 シーンに数百万個。

#### ボトルネック (block 1 の横棒)

> In MintPy, that inversion is the single biggest step: 43.5 percent of a complete processing run on the CPU.

MintPy ではこの逆解析が一番重い処理で、CPU での全処理の 43.5 % を占める。

#### 手法 (block 4 の図 2 枚): ここが「GPU 向けの定式化」

> Millions of independent small problems sounds perfect for a GPU. But simply moving the CPU method, QR-based least squares, onto the GPU gave only 1.43 times.

独立した小さな問題が数百万、と聞けば GPU にぴったりに思える。でも CPU と同じ QR 分解の最小二乗をそのまま GPU に移しても 1.43 倍にしかならなかった。

> At this matrix size, PyTorch's QR solver goes through the pixels one by one, about a hundred small steps each, so the GPU receives 3.8 million tiny commands per chunk and spends more time launching them than computing. (top figure)

この行列の大きさだと、PyTorch の QR ソルバは画素を 1 つずつ、それぞれ 100 ほどの小さな手順で処理する。GPU にはチャンクあたり 380 万個の細かい命令が届き、計算より命令を出す時間のほうが長くなる。(上の図)

> So I recast the problem as the normal equations: mathematically the same solution, but the work becomes one big matrix multiplication and one batched Cholesky factorization, each done for all pixels at once. 57 commands per chunk instead of 3.8 million. (bottom figure)

そこで問題を正規方程式に組み直した。数学的には同じ解だが、仕事が「大きな行列積 1 回」と「まとめて行う Cholesky 分解 1 回」になり、どちらも全画素を一度に処理する。命令はチャンクあたり 380 万個ではなく 57 個。(下の図)

> On the same GPU and the same scene, Fernandina, that change alone cuts the step time MintPy reports from 228 to 14 seconds: 16.5 times.

同じ GPU、同じシーン (Fernandina) で、この変更だけで MintPy が報告する step 時間が 228 秒から 14 秒に。16.5 倍。

- 補足: 16.5× (S1) は 3 条件 (同一 GPU・Fernandina・MintPy の step 時間で起動除く) を落とさない。"solver core" とは言わない

#### 速度 (block 5)

> Against the original CPU path, on one consumer GeForce card, a 3.4-million-pixel scene of the Galápagos went from 6,169 seconds to 139 seconds. That's 44 times.

元の CPU の経路と比べて、民生の GeForce 1 枚で、ガラパゴスの 340 万画素のシーンが 6,169 秒から 139 秒に。44 倍。

> On five public datasets, from two satellites, two radar wavelengths and four processing systems, it's 5 to 94 times faster.

公開データ 5 つ (衛星 2 機、レーダー波長 2 種、処理系 4 種) でも 5〜94 倍速い。

> The spread comes from how much work the CPU path does per pixel in each dataset, not from scene size.

ばらつきはデータごとの CPU 側の画素あたりの仕事量の違いから来ていて、シーンの大きさで決まるわけではない。

#### 精度 (block 6): 「定式化による誤差は実用上問題ない」

> There's a catch, and the textbooks warn about it. The normal equations square the condition number, which is roughly how much rounding error gets amplified. In single precision, that breaks down if a matrix is too badly conditioned. (flatten-and-restore figure)

ただし落とし穴があって、教科書も警告している。正規方程式は条件数 (ざっくり言えば丸め誤差が何倍に増幅されるか) を 2 乗にする。単精度だと、条件の悪すぎる行列では破綻する。(潰して戻す図)

> So I measured real networks: even the worst pixel I sampled stays at least 5.7 times away from the breaking point. (table)

そこで実際の網を測った。サンプルした中で最悪の画素でも、破綻点まで 5.7 倍以上の余裕がある。(表)

> And against the CPU's reference solver, the time series differ by 0.06 micrometres for the median pixel and 16 micrometres for the worst: thinner than a human hair, while InSAR resolves millimetres.

CPU の参照ソルバと比べると、時系列の差は中央値の画素で 0.06 マイクロメートル、最悪でも 16 マイクロメートル。髪の毛より細い。InSAR が見分けるのはミリメートル。

> All five datasets pass the agreement check on the final products.

5 つのデータすべてが、最終成果物で一致の判定に通っている。

#### 意義 (block 7)

> Why it matters: NISAR, launched in 2025, commercial constellations of small SAR satellites, and Taiwan's own FORMOSAT-9 are multiplying SAR data. Every new acquisition means inverting the whole network again.

なぜ大事か。2025 年に打ち上がった NISAR、小型 SAR 衛星の商用コンステレーション、台湾の FORMOSAT-9 で SAR データは増え続ける。新しい画像が 1 枚来るたびに、網全体を解き直すことになる。

> This turns that step from hours on a CPU into minutes on one consumer GPU, with no cluster needed.

この成果で、その処理が CPU で何時間から、民生 GPU 1 枚で数分になる。クラスタは要らない。

> It's open source and under review for MintPy. The QR codes take you to the code and to a PDF of this poster.

オープンソースで、MintPy に取り込んでもらうためのレビュー中。QR コードからコードとこのポスターの PDF に飛べる。

---

## 2. 想定 Q&A: InSAR に詳しくない人向け

### N1. なぜレーダー? 普通の衛星写真ではだめ?

> **Q.** Why radar? Couldn't you just use satellite photos?

なぜレーダー? 衛星写真じゃだめなの?

> Optical cameras need sunlight and clear skies, and comparing photos only catches motion of tens of centimetres or more. Radar brings its own illumination, so it works at night and through clouds, and its phase senses millimetres of motion.

光学カメラは太陽光と晴れた空が必要で、写真を比べて分かるのは数十センチ以上の動きだけ。レーダーは自分で電波を当てるので夜も雲越しでも使えて、位相でミリ単位の動きが分かる。

### N2. 波長が数センチなのに、なぜミリが測れる?

> **Q.** The wave is several centimetres long. How can it measure millimetres?

波長が数センチなのに、どうしてミリが測れるの?

> We don't count waves; we measure where in its cycle the wave comes back. For Sentinel-1, one full cycle of phase is 2.8 centimetres of motion toward the satellite, half the wavelength, because the signal travels down and back. A millimetre is about a twenty-eighth of a cycle. With dozens of images over years, the noise averages down to millimetre-level precision.

波の数を数えるのではなく、戻ってきた波が周期のどこにいるかを測っている。Sentinel-1 なら位相 1 周が衛星方向に 2.8 cm の動き。信号が往復するので波長の半分になる。1 mm は約 1/28 周。何年分もの数十枚の画像を使えば、雑音が平均されてミリ単位の精度になる。

### N3. 何が見えるの?

> **Q.** What can you see with it?

それで何が見えるの?

> Anything that moves slowly: volcanoes inflating as magma accumulates, faults creeping between earthquakes and the slow motion after them, cities and farmland sinking from groundwater pumping, landslides, even buildings and bridges settling. Here in Taiwan, the subsidence in the Changhua–Yunlin plain and the creeping faults in the east are classic InSAR targets.

ゆっくり動くものなら何でも。マグマがたまって膨らむ火山、地震と地震の間にずれ続ける断層や地震後のゆっくりした動き、地下水の汲み上げで沈む都市や農地、地すべり、建物や橋の沈下まで。台湾なら、彰化・雲林の平野の地盤沈下や東部のクリープする断層は InSAR の定番の対象。

- 補足: 雲林 (Yúnlín)・彰化 (Zhānghuà) の地盤沈下、台東の池上断層 (Chíshàng) のクリープを想定。数字は言わない

### N4. どの方向の動きでも測れる?

> **Q.** Does it measure motion in every direction?

どの方向の動きでも測れるの?

> Only along the line of sight, toward or away from the satellite. Combining northbound and southbound passes separates vertical from east–west motion. North–south motion is hard to see, because the orbits themselves run nearly north–south.

衛星の視線方向、つまり衛星に近づくか遠ざかるかだけ。北行きと南行きの軌道を組み合わせれば上下と東西を分けられる。南北の動きは見えにくい。軌道自体がほぼ南北に走っているから。

### N5. 地震の速報や災害対応に使えるの?

> **Q.** Is this for earthquake early warning or real-time disaster response?

地震の速報とかリアルタイムの災害対応に使うもの?

> Not directly. The sudden offset of an earthquake shows up in a single interferogram, and that's already quick to make. This work speeds up the time-series part: motion over months to years, like the strain building up on faults, the slow slip after an earthquake, or volcanic unrest. Faster processing means you can redo the whole history every time a new image arrives, which is what continuous monitoring needs.

直接にはそうではない。地震の一瞬のずれは干渉画像 1 枚に出るし、それはもう速く作れる。この成果が速くするのは時系列のほう。断層にひずみがたまっていく動き、地震後のゆっくりしたすべり、火山の活発化のような、数か月から数年の動き。処理が速くなれば、新しい画像が来るたびに履歴全体を解き直せる。継続的な監視にはそれが必要。

### N6. GPU って画像や AI 用じゃないの?

> **Q.** What does a GPU have to do with this? Isn't that for graphics and AI?

GPU がなんで関係あるの? グラフィックスや AI 用じゃないの?

> A GPU has thousands of simple cores that do the same operation on different data at once. That's what graphics and AI need, and it's what we have here too: the same small calculation repeated for millions of pixels. The catch is that the work has to come in big, uniform batches.

GPU には単純なコアが何千個もあって、同じ演算を別々のデータに一斉にかける。グラフィックスや AI に要るのはそれで、ここでも同じ。同じ小さな計算を数百万画素ぶん繰り返す。ただし、仕事が大きくて形のそろった塊で来ないといけない。

### N7. そのまま GPU に載せたら速くならなかったのはなぜ?

> **Q.** Why didn't just putting it on the GPU work?

そのまま GPU に載せてうまくいかなかったのはなぜ?

> Think of the GPU as an office with thousands of clerks and one manager handing out orders. The original method has about a hundred small steps per pixel, and the software handed out each step of each pixel as a separate order: 3.8 million orders per chunk. The clerks spent more time waiting for orders than working. The rewrite turns the job into a few dozen big orders, like "everyone, multiply your matrices now", so all the clerks work at once.

GPU を、何千人もの事務員と、指示を出すマネージャー 1 人の事務所だと思って。元の方法は 1 画素あたり 100 ほどの小さな手順があって、ソフトウェアは各画素の各手順を別々の指示として出していた。チャンクあたり 380 万件。事務員は働くより指示を待つ時間のほうが長かった。書き直したあとは、「全員、自分の行列の積を今やって」のような大きな指示数十件になったので、全員が一斉に働ける。

- 補足: マネージャー = CPU が出す kernel launch。QR 側の 1 チャンクは launch のホスト時間 18 s に対して kernel の実行 10 s

### N8. GPU だと答えが変わる? 精度は落ちる?

> **Q.** Does the GPU give a different answer? Is it less accurate?

GPU だと答えが変わるの? 精度は落ちる?

> Slightly different, yes, and in theory the GPU-friendly formula is less accurate; textbooks warn about it. So I measured it. Compared with the standard CPU solver, the difference is 0.06 micrometres for a typical pixel and 16 micrometres at worst. That's thinner than a human hair, and InSAR itself resolves millimetres.

少しは変わる。理論的にも GPU 向けの式のほうが精度は落ちるし、教科書も警告している。だから測った。標準の CPU ソルバと比べて、典型的な画素で 0.06 マイクロメートル、最悪で 16 マイクロメートルの差。髪の毛より細いし、InSAR 自体が見分けるのはミリメートル。

### N9. じゃあ解析全体が 44 倍速くなる?

> **Q.** So the whole analysis is 44 times faster?

じゃあ解析全体が 44 倍速くなるの?

> No, only this step. In a complete run it was 43.5 percent of the time, so even if it took zero seconds, the whole run would be at most about 1.8 times faster. But it's the largest single step, and the one whose cost grows fastest as archives get longer.

いや、この処理だけ。全体の 43.5 % だったので、仮にこれが 0 秒になっても全体は最大で約 1.8 倍。ただ、これは一番大きな処理で、アーカイブが長くなるほど一番速くコストが伸びる処理でもある。

- 補足: 44× (S2、Galápagos) と 43.5 % (Fernandina の baseline) は別シーン・別系列。**掛け算して全体の短縮を出さない** (qa_prep Q15)。コストの伸びは日付数の約 3 乗 (→ E8 の補足)

### N10. スパコンやクラウドではなく民生 GPU なのはなぜ?

> **Q.** Why a consumer GPU, not a supercomputer or the cloud?

なんでスパコンやクラウドじゃなくて民生 GPU なの?

> Because that's what a small research group, a local agency or a consultancy already has, or can buy for the price of a workstation. No cluster, no queue, no administrator. It's plain PyTorch, so it runs on a cloud GPU too, but the point is that you don't need one.

小さな研究グループや自治体、コンサル会社がもう持っているか、ワークステーション程度の値段で買えるものだから。クラスタも、ジョブの順番待ちも、管理者も要らない。素の PyTorch なのでクラウドの GPU でも動くけど、要点は「なくてもいい」こと。

### N11. MintPy って何?

> **Q.** What's MintPy?

MintPy って何?

> One of the most widely used open-source Python packages for InSAR time-series analysis, by Zhang Yunjun and colleagues, published in 2019 (reference 2). It takes interferograms from radar processing software and turns them into velocity maps and displacement histories.

InSAR の時系列解析で最も広く使われているオープンソースの Python パッケージのひとつ。Zhang Yunjun らが作り、2019 年に論文が出ている (参考文献 2)。レーダー処理ソフトが作った干渉画像を受け取って、速度の地図と変動の履歴にする。

### N12. 台湾の FORMOSAT-9 でも使える?

> **Q.** Will it work with Taiwan's FORMOSAT-9?

台湾の FORMOSAT-9 でも使える?

> The solver only sees the network of dates and interferograms, not the sensor, so any SAR stack that MintPy can read will work. The five test datasets already cover two wavelengths and four processing systems.

ソルバが見ているのは日付と干渉画像の網だけで、センサーは見ていない。MintPy が読める SAR データなら何でも使える。5 つのテストデータですでに波長 2 種、処理系 4 種をカバーしている。

- 補足: 分解能・バンド・打ち上げ年の数字は言わない。聞かれても「センサーは関係ない」に戻す

---

## 3. 想定 Q&A: ガチ勢向け

### 3-1. InSAR の専門家

#### E1. 重みは何? 干渉画像間の相関は無視?

> **Q.** What exactly are the weights? Are you ignoring the covariance between interferograms?

重みは正確には何? 干渉画像どうしの共分散は無視してる?

> MintPy's default: the inverse of the phase variance predicted from coherence and the number of looks, so it's weighted least squares with a diagonal weight matrix. Yes, the correlation between interferograms that share a date is ignored, as in MintPy's CPU path. I didn't change the estimator, only how it's solved.

MintPy の既定。コヒーレンスとルック数から予測した位相分散の逆数で、対角の重み行列による重みつき最小二乗。そう、同じ日付を共有する干渉画像どうしの相関は無視している。MintPy の CPU 経路と同じ。推定量は変えておらず、解き方だけを変えた。

- 補足: `weightFunc = var` (Tough et al. 1995)。言うなら「BLUE の対角近似」。重みが画素ごとに違うのが、CPU が画素ループになる原因 (qa_prep Q1b)

#### E2. MintPy は変位じゃなくて速度で解いてるよね?

> **Q.** MintPy solves for velocities, not displacements, doesn't it?

MintPy は変位じゃなくて速度を解いてるよね?

> Right. Block 2 draws the displacement form because it's easier to read. By default MintPy solves for the velocity in each interval between dates and sums them up; for a connected network that's the same least-squares solution. The condition numbers in block 6 are measured on the velocity-form matrix that is actually solved.

その通り。block 2 は読みやすさのために変位形で描いた。MintPy は既定で日付間の区間ごとの速度を解いて足し合わせる。網がつながっていれば最小二乗解は同じ。block 6 の条件数は、実際に解いている速度形の行列で測っている。

#### E3. 閉合は構成上ゼロのはずでは?

> **Q.** Shouldn't the triangle close exactly? Isn't the closure phase zero by construction?

三角形はぴったり閉じるはずでは? closure phase は構成上ゼロでは?

> For single-look wrapped phase, yes. What breaks it is the processing each interferogram goes through on its own: multilooking averages differently in every pair, and unwrapping can add a whole cycle to one of them; soil moisture and vegetation add a systematic part. Atmosphere and real motion belong to a date, so they cancel around the loop. That's also why the inversion can't remove the atmosphere.

シングルルックの wrap した位相なら、そう。崩すのは干渉画像ごとの処理。マルチルックはペアごとに平均のかかり方が違うし、アンラップは 1 枚にだけ 1 周ぶん足してしまうことがある。土壌水分や植生が系統的なずれも足す。大気と本物の動きは日付に属する量なので、三角形を一周すると消える。だから逆解析では大気は取り除けない。

- 補足: ポスターは "closure phase" という語を避けた。専門家には口頭で添える。De Zan et al. 2015 (TGRS)

#### E4. 網の分断・欠測・rank 落ちは?

> **Q.** What about missing data, disconnected networks, rank deficiency?

欠測、網の分断、rank 落ちはどうしてる?

> Missing interferograms enter as zero weights, which is the same as deleting the row, so every pixel keeps the same matrix shape and the chunk stays one batch. If a pixel's network falls apart, the batched Cholesky reports that pixel as failed instead of raising; it's flagged and zero-filled, so no NaN leaks downstream. The CPU returns a minimum-norm solution there, so some radar-coordinate intermediates differ on two scenes, but those are low-coherence pixels that the temporal-coherence mask removes before any product.

欠けた干渉画像は重みゼロで入れる。行を消すのと同じなので、どの画素も行列の形が同じままで、チャンクは 1 つのバッチのまま。網が分断した画素は、バッチ Cholesky が例外を投げずに「その画素は失敗」と報告するので、フラグを立ててゼロで埋める。NaN は下流に漏れない。そこでは CPU は最小ノルム解を返すので、2 つのシーンでレーダー座標の中間生成物に差が出るが、それは時間コヒーレンスのマスクが成果物を作る前に捨てる低コヒーレンスの画素。

- 補足: 2 シーン = Kuju と San Francisco (ARIA)。Kuju の geocoded velocity はマスク後 1.38e-7 で通過 (qa_prep Q13・Q14)

#### E5. ロバスト推定 (L1)、phase linking、PS は?

> **Q.** What about robust (L1) inversion, phase linking, or PS-InSAR?

ロバスト (L1) の逆解析や phase linking、PS-InSAR は?

> Out of scope: the GPU path implements MintPy's default weighted L2 network inversion. An iteratively reweighted scheme would reuse the same batched solve at every iteration, but I haven't built it. Phase linking and PS are different math. The batching idea carries over in spirit, and I have sibling benchmarks on dolphin and ISCE3, but nothing on this poster.

範囲外。GPU 経路が実装しているのは MintPy 既定の重みつき L2 の網逆解析。反復重みつき (IRLS) なら毎回の反復で同じバッチ解法を使い回せるが、作ってはいない。phase linking や PS は別の数理。バッチ化の発想は持ち込めるし、dolphin や ISCE3 での関連ベンチもあるが、このポスターには載せていない。

- 補足: dolphin・ISCE3 の具体的な数字は言わない (qa_prep Q12)

#### E6. 5 シーンで 5〜94 倍とばらつくのはなぜ? 規模で伸びる?

> **Q.** Why do the five scenes spread from 5 to 94 times? Does it scale with size?

5 シーンで 5〜94 倍とばらつくのはなぜ? 規模に比例するの?

> No size dependence; the ranking doesn't follow pixel count. What varies is the CPU baseline. The San Francisco ARIA stack runs unweighted, and then MintPy's CPU path solves all pixels in one call, so there's little loop left to replace. Kuju has only 24 dates, so each pixel's system is tiny and the GPU step is dominated by fixed costs. For a controlled large-scene number, use Galápagos: 44 times on 3.4 million pixels.

規模依存はない。順位は画素数に従っていない。違うのは CPU 側の基準。San Francisco の ARIA のデータは重みなしで走らせていて、そのとき MintPy の CPU 経路は全画素を 1 回の呼び出しでまとめて解くので、置き換えるループがほとんど残っていない。Kuju は日付が 24 しかないので、1 画素の系が小さく、GPU 側は固定費が支配的になる。条件をそろえた大規模シーンの数字なら Galápagos を見てほしい。340 万画素で 44 倍。

- 補足: 順位相関は画素数 −0.10、画素あたり演算量 +0.00、総演算量 +0.20 ([results.md](results.md) §S3)。「大きいほど速い」とは**言わない**

#### E7. 数字が合わない (44× と 38×、1.43× と 16.5× と 94×)

> **Q.** Galápagos is 44 times in the headline but 38 in the chart, and Fernandina is 1.43 and 16.5 in block 4 but 94 in the chart. Which is it?

Galápagos は見出しで 44 倍、グラフで 38 倍。Fernandina は block 4 で 1.43 倍と 16.5 倍、グラフで 94 倍。どれが本当?

> They come from different benchmark runs, and they shouldn't be chained. The headline inverts all 3.4 million pixels; the chart comes from complete 18-step runs, where the coherence mask leaves 1.3 million. The block 4 runs used a Python environment on network storage with a newer NumPy; the five-scene runs used a local environment with an older NumPy, whose CPU loop is slower. Each comparison is fair within itself, because both sides ran in the same environment.

別々のベンチマークの数字で、つなげて読むものではない。見出しは 340 万画素すべてを解いた run、グラフは 18 step 全部を流した run で、コヒーレンスのマスクで 130 万画素が残ったもの。block 4 の run はネットワークストレージ上の Python 環境で新しい NumPy、5 シーンの run はローカル環境で古い NumPy で、こちらは CPU のループが遅い。それぞれの比較は、両側を同じ環境で走らせているので、その中ではフェア。

- 補足: 「NumPy をそろえれば ○○ 倍」とは**こちらから言わない** (系列をまたいだ推定になる)

#### E8. NISAR の規模では?

> **Q.** What about NISAR-scale data?

NISAR の規模だとどうなる?

> MintPy already reads NISAR GUNW products, and the solver doesn't care about the sensor. For one NISAR frame over one year, about 300 million pixels with a 29-by-29 system each, extrapolating from the measured throughput gives roughly 4 hours on the CPU against 5 to 20 minutes on the GPU. That's an extrapolation, not a measurement. At that scale, reading the input, hundreds of gigabytes, matters as much as the arithmetic.

MintPy はもう NISAR の GUNW プロダクトを読めるし、ソルバはセンサーを気にしない。NISAR の 1 フレーム 1 年分 (約 3 億画素、それぞれ 29 × 29 の系) なら、実測のスループットから外挿して CPU で約 4 時間、GPU で 5〜20 分。外挿であって実測ではない。この規模では、数百 GB の入力を読むことが計算と同じくらい効いてくる。

- 補足: [compute_scale.md](compute_scale.md) の conn5 の行。入力は約 330 GB。**"extrapolated, not measured" を必ず添える**
- 補足: 日付数 D に対して K ∝ D、P ∝ D なので総コストは約 D³。1 年 → 3 年で約 29 倍の仕事 (qa_prep Q8a)

#### E9. データは何? 手に入る?

> **Q.** Which datasets are these, and can I get them?

このデータは何? 入手できる?

> Public InSAR stacks on Zenodo by Zhang Yunjun and co-authors, under CC BY 4.0. Four are MintPy's own example datasets; Galápagos is the data published with the MintPy paper. The DOIs are in the "Benchmark data" line at the bottom of the poster.

Zhang Yunjun らが Zenodo に CC BY 4.0 で公開している InSAR のデータ。4 つは MintPy 自身のサンプルデータで、Galápagos は MintPy の論文と一緒に公開されたデータ。DOI はポスター下の "Benchmark data" の行にある。

### 3-2. 数値計算 (条件数と精度)

#### M1. 正規方程式は κ を 2 乗する。float32 で本当に足りる?

> **Q.** The normal equations square the condition number. Is float32 really enough?

正規方程式は条件数を 2 乗する。float32 で本当に足りるの?

> Yes, and I measured rather than assumed. Single-precision Cholesky on the Gram matrix breaks down when the condition number of the weighted matrix approaches about 4,100, the square root of one over the unit roundoff. On the five scenes, the unweighted condition number is 11 to 55, and the worst weighted pixel I sampled is 721, so the margin is at least 5.7 times. The measured error against the CPU reference is 0.06 micrometres for the median pixel and 16 for the worst, over 3.4 million pixels, and all five scenes pass a 10^-5 relative gate on the final products.

足りる。仮定ではなく測った。Gram 行列の単精度 Cholesky は、重みつき行列の条件数が約 4,100 (単位丸め誤差の逆数の平方根) に近づくと破綻する。5 シーンで、重みなしの条件数は 11〜55、サンプルした中で最悪の重みつき画素でも 721 なので、余裕は 5.7 倍以上。CPU の参照と比べた実測の誤差は、340 万画素で中央値 0.06 マイクロメートル、最悪 16 マイクロメートル。5 シーンとも最終成果物で相対 10^-5 の判定を通る。

- 補足: 「速度のために精度を捨てた」ではなく「この問題の κ なら fp32 で足りると測ってから選んだ」が正しい言い方

#### M2. 数百万画素のうち 2,100 画素のサンプルでしょ?

> **Q.** You sampled 2,100 pixels out of millions. The real worst pixel could be worse.

数百万画素のうち 2,100 画素のサンプルでしょ。本当の最悪はもっと悪いかもしれない。

> Yes, it's a sample: 2,000 uniform plus 100 chosen for the widest range of weights, because the tail comes from the weights, not the network geometry. Two things cover the rest. The error comparison is over every pixel, and any pixel whose factorization fails is flagged individually by cholesky_ex, not silently wrong. Those are low-coherence pixels the standard mask discards anyway.

そう、サンプル。一様に 2,000 画素と、重みの幅が最も広い 100 画素。条件数の裾を作るのは網の形ではなく重みだから。残りは 2 つで押さえている。誤差の比較は全画素で取っていること。それから、分解に失敗した画素は cholesky_ex が 1 画素ずつフラグを立てるので、黙って間違うことはないこと。そういう画素はどうせ標準のマスクで捨てられる低コヒーレンスの画素。

#### M3. 条件の悪い画素はどれ? 網を密にすれば良くなる?

> **Q.** Which pixels are badly conditioned? Does a denser network help?

条件の悪い画素ってどれ? 網を密にすれば良くなる?

> The network itself is benign: the unweighted condition number is of order ten. The tail comes from the weights. The worst pixels mix strong interferograms with ones near the coherence floor, with weights differing by a factor of ten thousand or more. A denser network may help as a rule of thumb, but I don't claim it.

網自体はおとなしい。重みなしの条件数は 10 程度。裾を作るのは重み。最悪の画素は強い干渉画像とコヒーレンスの下限近くの干渉画像が混ざっていて、重みが 1 万倍以上違う。網を密にすると良くなるのは経験則としてはありうるが、主張はしない。

- 補足: max(w)/min(w) は 6.6e3〜8.6e4 ([results.md](results.md) §設計行列の条件数サーベイ)

#### M4. CholeskyQR2 や QR にしないのはなぜ?

> **Q.** Why not CholeskyQR2, or just QR?

CholeskyQR2 か、素直に QR にしないのはなぜ?

> CholeskyQR2 needs the same Gram Cholesky to succeed first, so it breaks down on the same pixels. Its benefit is an orthogonal Q, which a one-shot least-squares solve never uses. If the tail ever matters, re-solving only the flagged pixels in float64 is cheaper. And QR on the same GPU is what I measured: 16.5 times slower in MintPy's step time, on Fernandina.

CholeskyQR2 も最初に同じ Gram 行列の Cholesky が通る必要があるので、同じ画素で破綻する。利点は Q の直交性だが、1 回きりの最小二乗では Q を使わない。裾が問題になるなら、フラグの立った画素だけ float64 で解き直すほうが安い。それに QR は同じ GPU で実際に測った。Fernandina で MintPy の step 時間が 16.5 倍遅い。

- 補足: 引用 [4,5] から言えるのは「Gram + Cholesky は並列向きで、κ² の代償は既知」まで。「CholeskyQR2 と同じだから安全」とは**言わない**

#### M5. float64 や混合精度 (反復改良) にしないのは?

> **Q.** Why not float64, or mixed precision with iterative refinement?

float64 にしたり、混合精度で反復改良したりしないのは?

> On GeForce cards FP64 runs at 1/64 of the FP32 rate, so doing everything in float64 would give back most of the gain, and the measured error says it isn't needed. The sensible extension is selective: re-solve only the flagged pixels in float64, where the breakdown moves out to a condition number of about 10^8. Today those pixels are flagged and zero-filled. Iterative refinement would also work, but it isn't implemented.

GeForce では FP64 は FP32 の 1/64 の速さなので、全部 float64 にすると利得のほとんどを返すことになる。実測の誤差からも必要ない。拡張するなら選択的に、フラグの立った画素だけ float64 で解き直す。そうすれば破綻点は条件数 10^8 程度まで遠のく。今はそれらの画素はフラグを立ててゼロ埋め。反復改良も使えるが、実装していない。

- 補足: fp64 の破綻点は [results.md](results.md) では 6.7e7 (2^-52 基準)。口頭では「約 10^8」で十分

#### M6. TF32 や tensor core は?

> **Q.** Do you use TF32 or tensor cores?

TF32 や tensor core は使ってる?

> No, and it shouldn't. TF32 keeps only 10 mantissa bits; forming the Gram matrix with that would bring the breakdown down to a condition number of about 45, inside the measured range. PyTorch keeps FP32 matrix products in full FP32 by default, and the measured GEMM rate fits plain FP32 cores, not tensor cores.

使っていないし、使うべきでもない。TF32 は仮数部が 10 ビットしかなく、それで Gram 行列を作ると破綻点が条件数 45 程度まで下がって、実測の範囲に入ってしまう。PyTorch は既定で FP32 の行列積を完全な FP32 で計算するし、実測の GEMM の速度も tensor core ではなく通常の FP32 コアの値に合う。

- 補足: TF32 の u = 2^-11 → u^-1/2 ≈ 45 は概算で、TF32 での実測はない

#### M7. 図のぼけを等方に描くのはおかしい (丸めは成分ごとの相対誤差)

> **Q.** Rounding error is componentwise and relative. Why is the blur in your figure the same size in every direction?

丸め誤差は成分ごとの相対誤差なのに、図のぼけが全方向で同じ大きさなのはなぜ?

> The figure is a normwise backward-error model: the computed result is the exact solution for a matrix perturbed by about u times its norm. If the thin direction is oblique to the axes, its information survives only as differences of large numbers, so what you actually lose is of size u times the long axis.

図はノルムでの後退誤差のモデル。計算結果は、ノルムの u 倍くらいずらした行列の厳密解になっている。細い方向が座標軸に対して斜めなら、その情報は大きな数どうしの差 (桁落ち) にしか残らないので、実際に失われるのは長軸の u 倍の大きさになる。

### 3-3. GPU / HPC の専門家

#### H1. GPU で QR が遅いのはなぜ? ちゃんとバッチ化した QR なら?

> **Q.** Why is QR so slow on a GPU? Wouldn't a properly batched QR do as well?

GPU で QR が遅いのはなぜ? ちゃんとバッチ化された QR なら同じくらい速いのでは?

> What I measured was the direct port. PyTorch's least-squares solver uses cuBLAS's batched QR only up to 256 rows; at 288 rows it loops over the pixels on the host: one factorization plus 97 reflector applications, two small kernels each, 198 kernels per pixel, 3.8 million per chunk. Launching took 18 seconds per chunk against 10 seconds of kernel time. A truly batched QR would remove the per-pixel loop, but it still sweeps the tall matrix column by column with memory-bound work. I haven't measured that, so I don't claim QR can't work on GPUs.

測ったのはそのままの移植。PyTorch の最小二乗ソルバは cuBLAS のバッチ QR を 256 行までしか使わず、288 行ではホスト側で画素ごとにループする。分解 1 回と、97 個の反射の適用 (それぞれ小さな kernel 2 本) で 1 画素 198 kernel、チャンクあたり 380 万。起動にチャンクあたり 18 秒、kernel の実行は 10 秒。本当にバッチ化された QR なら画素ごとのループは消えるが、縦長の行列を列ごとにメモリ律速の処理でなめていくのは残る。そちらは測っていないので、「QR は GPU で使えない」とは言わない。

- 補足: 条件は K ≤ 256 かつ batch ≥ max(2, K/16)。NISAR 1 年 (K ≈ 135) なら cuBLAS の `gelsBatched` 側に入るはず (未計測)

#### H2. CUDA Graphs で起動のオーバーヘッドは消せるのでは?

> **Q.** Wouldn't CUDA Graphs remove the launch overhead?

CUDA Graphs を使えば起動のオーバーヘッドは消せるのでは?

> It would hide the launch cost, but not the kernel time. Per chunk, the QR kernels alone took 10.4 seconds, against 24 milliseconds for the whole normal-equation path: 430 times. The launches were the visible symptom; the shape of the work is the real cause.

起動のコストは隠せるが、kernel の実行時間は消えない。チャンクあたり QR の kernel だけで 10.4 秒、正規方程式の経路は全部で 24 ミリ秒。430 倍。起動の多さは目に見える症状で、本当の原因は仕事の形。

#### H3. 正規方程式のほうが演算量は少ないの?

> **Q.** Do the normal equations do less arithmetic?

正規方程式のほうが演算量が少ないの?

> No, slightly more: about 5.8 megaflops per pixel against 4.9 for Householder QR, by textbook counts. The gain is the shape. 93 percent of it is one batched GEMM, which runs at about 14.6 teraflops per second on this card, around a quarter of its nominal FP32 peak, while the QR factorization kernel ran at about 25 gigaflops per second.

いや、少し多い。教科書の数え方で 1 画素あたり約 5.8 Mflop、Householder QR は 4.9。得をしているのは形。その 93 % がバッチ GEMM 1 本で、このカードで約 14.6 TFLOP/s、公称の FP32 ピークの 4 分の 1 くらい。一方 QR の分解 kernel は約 25 GFLOP/s。

- 補足: スループットは実測の kernel 時間 ÷ 教科書の flop 数で出した**概算**
- 補足: 「ピークの 4 分の 1」は RTX 5080 デスクトップ版の公称 56 TFLOP/s が前提。計測機の GPU がノート版なら比が変わるので、聞かれる前に確認しておく

#### H4. Cholesky も逐次的では?

> **Q.** Isn't Cholesky sequential too?

Cholesky も逐次的じゃないの?

> Yes. cuSOLVER's batched Cholesky goes through 16-column panels in 7 stages. The difference is that each stage is one launch over all 19,403 pixels in the chunk. Those stages are part of the 57 launches.

そう。cuSOLVER のバッチ Cholesky は 16 列幅のパネルで 7 段進む。違いは、1 段が 1 回の起動でチャンクの 19,403 画素全部を処理すること。その 7 段も 57 回の起動に含まれている。

#### H5. CPU の基準はシングルスレッド? それはフェアじゃない

一番突っ込まれる質問。正直に答える。

> **Q.** Is your CPU baseline single-threaded? That's not a fair comparison.

CPU の基準はシングルスレッド? それはフェアな比較じゃない。

> It's MintPy's default configuration, which is what users get: the per-pixel loop runs on one Python thread, at 99 percent CPU utilisation, on a 16-core Intel Core Ultra 9 285H. MintPy can spread the loop over cores with Dask; I didn't benchmark that. Even with perfect 16-core scaling, the GPU would still be about 3 times ahead, so the conclusion holds, but against a fully parallel CPU the margin is much smaller than 44. A batched, multi-core CPU solver would be the fairest next comparison. What block 4 does show is that the reformulation itself is worth 16.5 times on the same GPU, so it's not just about removing a Python loop.

MintPy の既定の設定で、ユーザーが普通に使う形。画素ごとのループは Python の 1 スレッドで、CPU 使用率 99 %、マシンは 16 コアの Intel Core Ultra 9 285H。MintPy は Dask でループを複数コアに分けられるが、それはベンチしていない。16 コアで完全にスケールしたとしても GPU はまだ約 3 倍速いので結論は変わらないが、完全に並列化した CPU と比べれば差は 44 倍よりずっと小さい。バッチ化したマルチコアの CPU ソルバが、次にやるべき一番フェアな比較。block 4 が示しているのは、同じ GPU の上で定式化だけで 16.5 倍の価値があるということで、Python のループを消しただけの話ではない。

- 補足: 「約 3 倍」は 44.4 / 16 の推論で、**実測ではない**と必ず言う。285H は P / E / LP-E コアの混成なので、16 倍の理想スケーリングは CPU にかなり甘い上限
- 補足: 出典は mintpy-benchmark `report_large_scene.md` (`/usr/bin/time` で User 6,112.58 s、CPU 99 %)

#### H6. いまのボトルネックはどこ? 計算律速? I/O 律速?

> **Q.** Where does the time go now? Is it compute-bound or I/O-bound?

いま時間はどこにかかってる? 計算律速? I/O 律速?

> Across the five scenes, the GPU step time follows the amount of stack read from disk more than the arithmetic, so it's moving toward I/O. On Galápagos the whole step, HDF5 reads and writes included, is 139 seconds. At NISAR scale, with hundreds of gigabytes of input, storage bandwidth matters as much as the GPU.

5 シーンを通して、GPU の step 時間は演算量よりもディスクから読むスタックの量に沿っているので、I/O 寄りになってきている。Galápagos では HDF5 の読み書きを含めた step 全体で 139 秒。NISAR 規模で入力が数百 GB になると、ストレージの帯域が GPU と同じくらい効く。

#### H7. メモリは? VRAM に乗らないシーンは?

> **Q.** What about memory? What if the scene doesn't fit in VRAM?

メモリは? シーンが VRAM に乗らなかったら?

> Chunks are sized automatically to 40 percent of free VRAM, and the design matrix goes up once and is reused. Galápagos ran in chunks of about 8,700 pixels with a 7.6 GB peak on a 16 GB card. There's no hard size limit, only more chunks.

チャンクは空き VRAM の 40 % に収まるよう自動で決まり、設計行列は 1 回だけ転送して使い回す。Galápagos は約 8,700 画素のチャンクで、16 GB のカードでピーク 7.6 GB。シーンの大きさに上限はなく、チャンクが増えるだけ。

#### H8. マルチ GPU、Dask、クラスタは?

> **Q.** What about multiple GPUs, Dask, or a cluster?

マルチ GPU や Dask、クラスタは?

> They're orthogonal. Dask spreads the per-pixel loop over processes; this replaces the loop with batched calls on one device. Chunks are independent, so splitting them across several GPUs is straightforward, but it isn't implemented. The point here is one card a group already owns.

直交する話。Dask は画素ごとのループを複数プロセスに分ける。こちらはそのループを 1 台のデバイス上のバッチ呼び出しに置き換える。チャンクは互いに独立なので複数 GPU に分けるのは素直にできるが、実装はしていない。ここでの要点は、グループがもう持っているカード 1 枚。

#### H9. なぜ PyTorch? 自前の CUDA、CuPy、JAX ではなく?

> **Q.** Why PyTorch? Why not custom CUDA kernels, CuPy or JAX?

なぜ PyTorch? 自前の CUDA kernel や CuPy、JAX ではなく?

> MintPy is a community-maintained Python package, so I wanted no custom kernels. PyTorch gives batched GEMM and batched Cholesky through cuBLAS and cuSOLVER, and cholesky_ex reports failures per matrix instead of raising, which is exactly what millions of pixels need. It's an optional dependency, and the CPU path is untouched.

MintPy はコミュニティで保守されている Python パッケージなので、自前の kernel は入れたくなかった。PyTorch なら cuBLAS と cuSOLVER 経由でバッチ GEMM とバッチ Cholesky が使えて、cholesky_ex は例外を投げずに行列ごとに失敗を報告してくれる。数百万画素にはまさにそれが要る。依存は任意 (optional) で、CPU 経路には手を入れていない。

#### H10. AMD や Apple Silicon は?

> **Q.** Does it run on AMD or Apple Silicon?

AMD や Apple Silicon で動く?

> Not yet. It's PyTorch, so ROCm or MPS is a matter of the device setting, but the batched Cholesky path has only been validated on CUDA, and the code currently stops with an error without a CUDA device rather than silently falling back.

まだ。PyTorch なので ROCm や MPS はデバイスの指定次第だが、バッチ Cholesky の経路は CUDA でしか検証していない。今のコードは CUDA デバイスがなければ、黙って CPU に切り替えるのではなくエラーで止まる。

#### H11. 分解を 1 回して全画素で使い回せないの?

> **Q.** Why not factorize once and reuse it for every pixel?

1 回分解して、全画素で使い回せないの?

> That works only when every pixel shares the same matrix, which is the unweighted case, and MintPy's CPU path already does it. That's why the unweighted San Francisco scene has the fastest CPU baseline. With per-pixel weights every row is scaled differently, so each pixel needs its own factorization.

それができるのは全画素が同じ行列を共有するとき、つまり重みなしの場合だけで、MintPy の CPU 経路はすでにそうしている。重みなしの San Francisco のシーンで CPU の基準が一番速いのはそのため。画素ごとに重みがあると各行のスケールが画素ごとに違うので、画素ごとに分解が要る。

#### H12. 反復解法 (CG、LSQR) は?

> **Q.** Why not an iterative solver, like CG or LSQR?

CG や LSQR みたいな反復解法は?

> Each system is small and dense, 97 by 97 once the normal matrix is formed, so a direct factorization is cheap and has a fixed, uniform cost, which batches well. Iterative methods would converge at different rates for different pixels, which breaks the uniform batch.

1 つ 1 つの系は小さくて密 (正規行列にすると 97 × 97) なので、直接分解が安く、コストが一定でそろっていてバッチに向く。反復解法だと画素ごとに収束の速さが違うので、そろったバッチが崩れる。

### 3-4. 計測の作法

#### B1. 44 倍は solver の kernel だけ? I/O は入ってる?

> **Q.** Is the 44 times just the solver kernel? Is I/O included?

44 倍は solver の kernel だけ? I/O は入ってる?

> It's the whole step as MintPy itself times it: reading the stack, computing the weights, solving, writing HDF5. Only Python start-up is left out. Counting it gives 36 times for that run, but in a normal workflow start-up is paid once for all steps.

MintPy 自身が計る step 全体。スタックの読み込み、重みの計算、解く処理、HDF5 の書き出しまで。外しているのは Python の起動だけ。それを含めるとこの run では 36 倍だが、普通の流れでは起動は全 step で 1 回しか払わない。

- 補足: S1 の step wall 4.49× (両側に起動 約 47 s) は**出さない**

#### B2. 何回測った? ばらつきは? キャッシュは?

> **Q.** How many runs? What about variance and caching?

何回測った? ばらつきやキャッシュは?

> The same-GPU QR versus Cholesky comparison is a mean of three runs. The large-scene CPU run takes an hour and 43 minutes, so it's one run per side; at 44 times, run-to-run variance doesn't change the conclusion. Both read from a local NVMe drive, and the GPU run went second, with a warm page cache.

同じ GPU での QR 対 Cholesky は 3 回の平均。大規模シーンの CPU の run は 1 時間 43 分かかるので、両側 1 回ずつ。44 倍もあれば、run ごとのばらつきで結論は変わらない。どちらもローカルの NVMe から読んでいて、GPU の run は 2 番目で、ページキャッシュが温まった状態だった。

- 補足: ウォームキャッシュは聞かれたら認める。コールドキャッシュでの計測はない

#### B3. 計測環境は?

> **Q.** What hardware and software?

ハードとソフトは?

> An Intel Core Ultra 9 285H with 16 cores, and an NVIDIA GeForce RTX 5080 with 16 GB, running PyTorch 2.11 with CUDA 12.8.

16 コアの Intel Core Ultra 9 285H と、16 GB の NVIDIA GeForce RTX 5080。PyTorch 2.11、CUDA 12.8。

---

## 4. 共通の質問

### C1. マージされた? 今すぐ使える?

> **Q.** Is it merged? Can I use it today?

マージされた? 今すぐ使える?

> It's pull request 1490 on MintPy, open and waiting for the maintainers' review; the branch is rebased on main and the GPU tests pass. Today you can install my fork with the GPU extra and set one template option, mintpy.networkInversion.solver = torch. Without that option nothing changes; the CPU path is untouched.

MintPy の pull request 1490 で、オープンのままメンテナのレビュー待ち。ブランチは main に rebase 済みで GPU のテストも通っている。今なら、わたしのフォークを GPU 用の extra つきで入れて、テンプレートに mintpy.networkInversion.solver = torch を 1 行足せば使える。その設定がなければ何も変わらない。CPU 経路には手を入れていない。

- 補足: 2026-11-09 時点で OPEN / REVIEW_REQUIRED。11/07 にフォローアップのコメント済み。当日の朝に `gh pr view 1490 --repo insarlab/MintPy` で再確認

### C2. どちらの所属?

> **Q.** Who are you with?

どちらの所属ですか?

> I'm an independent researcher and software engineer; Earthsea Wizard Tech Lab is my practice. Before that I was a postdoc on a JAXA-funded project using satellite imagery for disaster management, which is where my interest in InSAR started.

独立の研究者・ソフトウェアエンジニアで、Earthsea Wizard Tech Lab はわたしの事業。その前は、衛星画像を防災に役立てる JAXA の資金のプロジェクトでポスドクをしていて、InSAR への興味はそこから。

---

## 5. 言わないこと (チェックリスト)

- 44× も 16.5× も "solver core" / "kernel speedup" とは言わない (読み込み・重み計算込みの step 時間)
- S1 の step wall 4.49× (起動込み) は出さない
- 「大きいシーンほど速い」とは言わない
- 系列をまたいで掛けない: 1.43 × 16.5 ≈ 24、44× と 43.5 % から全体の短縮を出す、など
- NISAR の数字には必ず "extrapolated, not measured"
- FORMOSAT-9 の分解能・性能の数字は言わない
- 「CholeskyQR2 と同じだから安全」と言わない
- 「QR は原理的に GPU に向かない」と言わない
- 閉合のずれの原因に大気を挙げない
- 「網を密にすると κ が下がる」を主張しない
- 「InSAR 時系列解析を速くした」と広げない。速くしたのは SBAS 型の網逆解析の step (と同じコアの DEM 誤差補正)

---

## 6. 数字カンペ

| 数字 | 中身 |
| --- | --- |
| 43.5 % | CPU の全処理に占める網逆解析 (Fernandina) |
| 1.43× | そのままの移植 (GPU の QR) の CPU 比 |
| 3.8 M → 57 | チャンク (19,403 px) あたりの kernel 起動 |
| 16.5× | 同一 GPU・Fernandina の QR → Cholesky (MintPy の step 時間、起動除く) |
| 6,169 → 139 s | Galápagos 3.4 M px × 475 ifgs、44.4× |
| 5–94× | 5 シーンの 18 step 実行 |
| 6.2× | DEM 誤差補正 (Galápagos) |
| 11–55 | κ、重みなし |
| 721 | κ、重みつきの最悪 (San Francisco Bay) |
| 4,100 | fp32 Cholesky の破綻点 |
| 0.06 / 16 µm | CPU との差 (中央値 / 最悪) |
| 10^-5 | 一致の判定 (5/5 通過) |
| 7.6 / 16 GB | VRAM のピーク / 搭載量 |
| 4 h → 5–20 min | NISAR 1 フレーム 1 年 (外挿) |
