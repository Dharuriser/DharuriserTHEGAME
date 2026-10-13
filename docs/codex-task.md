# Codex への作業依頼: 主人公スプライトの作り直し（第1弾）

依頼者: Claude Code（オーナーの指示で作成） / 対象ブランチ: `claude/loving-wright-wu1w7r`

## 目的

主人公「ダルライザー」のモーション画像を、画像生成（組み込みの `image_gen`）で作り直す。
今の歩きは**真横向き・4コマ**で、立ち姿や攻撃（斜め前向き）と体の向きが食い違っている。
これを**斜め前向き（3/4ビュー）・右向き・8コマの歩き**にするのが第1弾の目的。

あなた（Codex）の担当は「生成 → 整形 → 確認 → コミット」まで。
**`index.html` への組み込み（inject）とコードの調整は Claude Code が行うので、やらないでください。**

## 手順

### 0. 準備

```bash
git fetch origin
git checkout claude/loving-wright-wu1w7r
git pull origin claude/loving-wright-wu1w7r
python3 -m pip install pillow numpy   # 入っていなければ
```

`AGENTS.md`、`docs/HANDOFF.md`、`docs/sprite-spec.md` を読む。

### 1. 参考画像を見る

`view_image` で次の2枚を読み込み、会話の中で見える状態にする（生成時の参考画像として使う）。

- `sprites/reference/Dharuriser_design_sheet.png`（立ち・パンチ・キック・ガード・今の歩き）
- `sprites/reference/Dharuriser_idle_x3.png`（立ち姿の拡大）

### 2. 「立ち＋歩き」シートを生成する

組み込みの `image_gen` を使う（CLI や API キーは使わない）。上の2枚を**参考画像（reference image）**として渡し、次のプロンプトで生成する。

```
Use the attached images as the exact character design reference (Dharuriser, a Japanese tokusatsu hero):
red full-body suit, gold emblem on the chest, white-and-red helmet with a black visor, black knee pads and belt.
Keep his realistic adult hero proportions (about 7.5 heads tall). NOT chibi, NOT super-deformed.

Create a pixel-art sprite sheet, 3 columns x 3 rows, 9 cells of identical size.
Every cell: the same character at the same scale, 3/4 front view facing RIGHT
(same camera angle as the attached idle pose), feet on the same ground line near the bottom of the cell.
Crisp 1-pixel dark outline, limited palette matching the reference.
Background: solid flat pure green #00FF00 in every cell. No shadow, no floor, no text, no numbers, no grid lines.

Cells in reading order:
1. idle fighting stance (same as the reference)
2. walking: right foot steps forward and touches the ground (contact)
3. walking: weight comes down on the right foot, body slightly lower (down)
4. walking: left foot passes the right leg (passing)
5. walking: body rises onto the right toes (up)
6. walking: left foot steps forward and touches the ground (contact)
7. walking: weight comes down on the left foot, body slightly lower (down)
8. walking: right foot passes the left leg (passing)
9. walking: body rises onto the left toes (up)
Arms swing opposite to the legs. Keep the fists loosely clenched.
```

- **3回まで**生成してよい（1回の生成＝1回の `image_gen` 呼び出し）。
- 生成した画像は `$CODEX_HOME/generated_images/...` から、`sprites/generated/walk_v1.png`、`walk_v2.png`、`walk_v3.png` にコピーする（上書きしない）。

### 3. 整形する（背景を消し、大きさ・足元・腰の位置を揃える）

生成した各版について実行する（`v1` の部分を変えて）。

```bash
python3 tools/sprite_pipeline.py build sprites/generated/walk_v1.png --grid 3x3 --name Dharuriser_walk_v1 --anchor hip
```

出力は `sprites/build/` に作られる。
- `Dharuriser_walk_v1.png` … ゲーム用の横並び画像（9コマ × 400x300）
- `Dharuriser_walk_v1_preview.gif` … 動きの確認
- `Dharuriser_walk_v1_check.png` … 全コマを並べ、1コマ目を薄く重ねたもの（黄線＝足元、水色線＝腰）

### 4. 確認する（`view_image` で `_check.png` を見る）

次の**全部を満たす版**を合格とする。

- [ ] 全9コマで、同じキャラに見える（ヘルメットの形、黒いバイザー、胸の金のエンブレム、黒いひざ当て、赤いスーツ）
- [ ] 全コマ **右向き・斜め前（3/4ビュー）**。真横や正面になっているコマがない
- [ ] デフォルメ（ちびキャラ）になっていない。参考画像と同じくらいの頭身
- [ ] 2コマ目と6コマ目で、**前に出ている足が逆**（右足と左足が交互）
- [ ] 背景の緑が残っていない。体の一部が欠けていない
- [ ] 整形後の身長がコマごとに極端に違わない（歩きの上下動の範囲）

3回生成しても合格する版がない場合は、**そこで止めて**報告する（無理に進めない）。
何が問題だったか（例: 「ヘルメットの形が毎回変わる」「真横向きになる」）を具体的に書く。

### 5. コミットして push する

合格した版があってもなくても、生成した画像と整形結果はコミットする（比較のため）。

```bash
git add sprites/generated sprites/build
git commit -m "歩きシートを画像生成で作成(v1〜v3)。合格: vN / 不合格理由: ..."
git push origin claude/loving-wright-wu1w7r
```

### 6. 報告する（日本語で）

- どの版が合格か（なければ「なし」と理由）
- 使ったプロンプト（変えた場合は最終版）
- 組み込みの `image_gen` を使ったか
- 気づいた問題点

## 第1弾やり直し: 歩きを「半分ずつ」作る（2026-09-28 追加）

### これまでに分かったこと

- 9コマを1枚で作らせると、**何度やっても「右足（カメラに近い方の足）が前」の姿勢しか出ない**（v1〜v3 すべて同じ失敗）。
  オーナーも以前同じ経験をしており、今ゲームに入っている歩きは Photoshop で手直ししたもの。
- 右向き・斜め前（3/4ビュー）では、**右足＝カメラに近い足（手前の足）、左足＝カメラから遠い足（奥の足）**。
  「右／左」は取り違えやすいので、プロンプトでは **near leg（手前）／far leg（奥）** と、見た目の手がかりで指示する。
- デザイン・向き・頭身・背景除去は v1〜v3 とも良好だった。`sprites/generated/walk_v2.png` が一番動きに差がある（配色・縮尺の参考に使ってよい）。

### 手順

**A. 前半（手前の足が前に出る4コマ）を生成する** — 生成は最大2回。保存先 `sprites/generated/walk_a_v1.png`、`walk_a_v2.png`

参考画像: `sprites/reference/Dharuriser_design_sheet.png`、`sprites/reference/Dharuriser_idle_x3.png`（必要なら `sprites/generated/walk_v2.png`）

```
Use the attached images as the exact character design reference (Dharuriser, a Japanese tokusatsu hero):
red full-body suit, gold emblem on the chest, white shoulder armor, white-and-red helmet with a black visor, black knee pads and black belt.
Keep his realistic adult hero proportions (about 7.5 heads tall). NOT chibi, NOT super-deformed.

Create a pixel-art sprite sheet, 3 columns x 2 rows, 6 cells of identical size.
Every cell: the same character at the same scale, 3/4 front view facing RIGHT
(same camera angle as the attached idle pose), feet on the same ground line near the bottom of the cell.
Crisp 1-pixel dark outline, limited palette matching the reference.
Background: solid flat pure green #00FF00 in every cell. No shadow, no floor, no text, no numbers, no grid lines.

This is HALF of a slow natural WALK cycle (not running). In every walking cell the NEAR leg (the leg closer to the camera) is the one stepping forward.
Cells in reading order:
1. idle fighting stance (same as the reference)
2. CONTACT: the near leg steps forward, heel touches the ground; the far leg is behind, on its toes. Far arm swings forward, near arm swings back.
3. DOWN: weight comes onto the near (front) leg, knee slightly bent, body visibly lower; the far foot lifts off behind.
4. PASSING: the far leg swings forward and passes right beside the straight near leg; far foot low, just off the ground; arms close to the body. Body highest here.
5. UP: the far leg reaches forward ahead of the body, about to land; the near leg pushes off behind on its toes.
6. leave this cell completely empty (only the green background).
Each of the four walking cells must be a clearly different pose.
```

整形: `python3 tools/sprite_pipeline.py build sprites/generated/walk_a_vN.png --grid 3x2 --frames 5 --name Dharuriser_walk_a_vN --anchor hip`

合格条件: デザインが揃っている／2〜5コマ目がはっきり違う姿勢／2コマ目で手前の足が前／走りの姿勢になっていない。
合格した版を B の元にする。

**B. 後半（奥の足が前に出る4コマ）を、A の画像を編集して作る** — 生成（編集）は最大3回。保存先 `sprites/generated/walk_b_v1.png`〜`walk_b_v3.png`

新しく描かせず、**合格した A の元画像（緑背景のシート）を入力画像にして編集**する（`image_gen` に A の画像を渡す）。

```
Edit the attached sprite sheet (the first image). Keep EVERYTHING the same: same character design, colors, pixel style,
3/4 front view facing RIGHT, same scale, same cell layout, same ground line, same pure green #00FF00 background, cell 1 and the empty cell 6 unchanged.

Change ONLY the legs and arms of cells 2 to 5 so that they show the OTHER half of the walk cycle:
swap which leg is forward. In every walking cell the FAR leg (the leg farther from the camera) now does what the near leg did, and vice versa.
2. CONTACT: the FAR leg steps forward, heel touches the ground; the NEAR leg is behind, on its toes. Near arm swings forward, far arm swings back.
3. DOWN: weight on the far (front) leg, body visibly lower; the near foot lifts off behind.
4. PASSING: the NEAR leg swings forward and passes beside the straight far leg.
5. UP: the NEAR leg reaches forward ahead of the body; the far leg pushes off behind on its toes.
Visual cues: the near leg is always drawn in front of (overlapping) the far leg. When the far leg is forward, the forward foot is partly
behind the near leg's shin and its knee pad is partly hidden; the near leg's full knee pad is visible on the BACK leg.
Do not mirror or flip the character. The head, helmet, chest and face still point to the RIGHT.
```

整形: `python3 tools/sprite_pipeline.py build sprites/generated/walk_b_vN.png --grid 3x2 --frames 5 --name Dharuriser_walk_b_vN --anchor hip`

合格条件: A の同じ番号のコマと比べて、**前に出ている足が逆**（B の2コマ目は奥の足が前、手前の足が後ろ）／デザイン・大きさが A と同じ。
A と B の `_check.png` を**並べて見比べて**判定する。1回目で逆にならなければ、2・3回目はプロンプトの言い方を変える
（例: 「the back leg is the near leg, fully visible, overlapping the front leg」など、見た目の重なり方で指示する）。

**C. 合わせる**（合格した A と B がそろったときだけ）

`sprites/build/Dharuriser_walk_a_vN.png` の 0〜4コマ目と、`Dharuriser_walk_b_vN.png` の 1〜4コマ目をこの順に横に並べ、
9コマ（3600x300）の `sprites/build/Dharuriser_walk_v4.png` を作る（Pillow で貼り合わせるだけ）。確認用 GIF（1〜8コマ目のループ、1コマ100ms）も `Dharuriser_walk_v4_preview.gif` として作る。

B が3回とも不合格なら C はやらずに止めて報告する。

**報告**: A・B それぞれの合否とコマごとの問題点、最終プロンプト、`image_gen` を使ったか（編集として画像を渡せたか）、作ったファイルのパス。
`index.html` の組み込みと、git のコミット・push は Claude Code が行う。

## 第1弾その3: ダブルドラゴン（ビリー）の歩きを見本にして作る（2026-09-28 追加）

### これまでの結果とオーナーの感想

- 「半分ずつ」方式の9コマ（`Dharuriser_walk_v4`）を組み込んだが、オーナーの評価は「足がスムーズに動いていない」「腕の振りも必要」。
- 原因: ①足の開き具合が「大股→中→そろう→**大股→大股**→中→そろう→大股」と、大股が2回続く所がある。②普通の散歩の歩き方で、後半は腕の振りが入れ替わっていない。
- オーナーが自然だと考えているのはダブルドラゴンの歩き。見本: `sprites/reference/DD_Billy_walk_pose_ref.png`
  （スーパーダブルドラゴンのビリー。左上が立ち、続けて歩き6コマ: **大股 → 中 → そろう → 大股（逆の足） → 中 → そろう**。上半身はほぼ動かず、手前の腕が前後に振れる）
- 画像生成は文章で「左足を前に」と指示すると失敗するが、**見本の絵のポーズを写す**方が得意なはず。今回はこれを試す。

### 手順 — 生成は最大3回。保存先 `sprites/generated/walk_dd_v1.png`〜`walk_dd_v3.png`

参考画像（すべて `image_gen` に渡す）:
1. `sprites/reference/DD_Billy_walk_pose_ref.png` … **ポーズの見本**（足と腕の位置だけを写す。絵柄・服・顔は写さない）
2. `sprites/reference/Dharuriser_design_sheet.png`、`sprites/reference/Dharuriser_idle_x3.png` … キャラのデザイン
3. `sprites/generated/walk_a_v2.png` … 前回合格した絵（配色・縮尺・3/4ビューの参考）

```
Image 1 is a POSE reference only: a 4x2 sheet of a classic beat-'em-up walk (idle + 6 walking frames).
Images 2-4 are the exact character design reference (Dharuriser, a Japanese tokusatsu hero):
red full-body suit, gold emblem on the chest, white shoulder armor, white-and-red helmet with a black visor, black knee pads and black belt.
Keep his realistic adult hero proportions (about 7.5 heads tall). NOT chibi. Do NOT copy the pose reference's clothes, hair, face or colors.

Create a pixel-art sprite sheet with EXACTLY the same layout as Image 1: 4 columns x 2 rows, 8 cells of identical size.
In every cell draw Dharuriser in EXACTLY the same leg and arm positions as the same cell of Image 1
(same stride width, same which-leg-is-forward, same arm position), but in a 3/4 front view facing RIGHT like Image 4.
Same scale in every cell, feet on the same ground line near the bottom of the cell.
Crisp 1-pixel dark outline, limited palette matching Image 4.
Background: solid flat pure green #00FF00 in every cell. No shadow, no floor, no text, no numbers, no grid lines.

Cell 1: idle fighting stance (as Image 4).
Cells 2-7: a calm fighter's walk, upper body upright and steady, fists loosely clenched, arms swinging opposite to the legs:
 2. wide stride, NEAR leg forward, near arm back
 3. legs closing, medium stride
 4. legs together, passing
 5. wide stride, FAR leg forward, NEAR leg back, near arm forward
 6. legs closing, medium stride
 7. legs together, passing
Cell 8: empty (only green).
```

整形: `python3 tools/sprite_pipeline.py build sprites/generated/walk_dd_vN.png --grid 4x2 --frames 7 --name Dharuriser_walk_dd_vN --anchor hip`

合格条件（`_check.png` と見本を並べて判定）:
- 2〜7コマ目の足の開き具合が「大股→中→そろう→大股→中→そろう」の順になっている（見本と同じ）
- 2コマ目と5コマ目で**前に出ている足が逆**、**腕の振りも逆**（見本の2コマ目・5コマ目と同じ関係）
- 上半身の傾き・高さがコマごとに大きく変わらない／デザイン・大きさが揃っている／右向き3/4ビュー

報告: 合否とコマごとの問題点、最終プロンプト、作ったファイルのパス。`index.html` の組み込みと git 操作は Claude Code が行う。

## 敵の歩きの作り直し（2026-10-13 追加）

主人公の歩き（`walk_dd_v3`、ビリーの歩きをポーズ見本にした6コマ）はオーナーの合格が出た。**同じ方法で敵4体の歩きを作り直す。**
今の敵の歩きは真横向きのコマを往復再生していて、主人公と同じ問題（同じ足が続く・立ちや攻撃と体の向きが違う）がある。
enemyC（小柄な軽業師）は歩きではなくアクロバット移動なので対象外。

| 敵 | 画像名 | デザイン見本 | build の追加オプション |
|---|---|---|---|
| enemyA（紫ポンチョ・標準） | `enemyA_walk` | `sprites/reference/enemyA_design_ref.png` | `--ref-height 240 --anchor-x 165 --baseline 299` |
| enemyB（紫ポンチョ・長身） | `enemyB_walk` | `sprites/reference/enemyB_design_ref.png` | `--ref-height 248 --anchor-x 177 --baseline 298` |
| DICE（黒スーツ・赤い一つ目の仮面） | `DICE_walk` | `sprites/reference/DICE_design_ref.png` | `--ref-height 246 --anchor-x 185 --baseline 299` |
| Bajioh（コート・仮面） | `Bajioh_walk` | `sprites/reference/Bajioh_design_ref.png` | `--ref-height 237 --anchor-x 170 --baseline 299` |

デザイン見本は、左に立ち姿（2倍）、右に今のパンチ・キックのコマを並べたもの（ゲームに入っている絵そのもの）。
追加オプションは、今の立ちコマと同じ身長・立ち位置に揃えるための値（攻撃の絵に切り替わったときに位置がずれないように）。

### 手順（敵1体につき）— 生成は最大3回。保存先 `sprites/generated/<敵>_walk_dd_v1.png`〜`_v3.png`

参考画像（すべて `image_gen` に渡す）:
1. `sprites/reference/DD_Billy_walk_pose_ref.png` … **ポーズの見本**（足と腕の位置だけを写す）
2. その敵のデザイン見本 … キャラのデザイン・絵柄・頭身・カメラの角度
3. `sprites/generated/walk_dd_v3.png` … 主人公で合格した出力。**レイアウト・足の開き方・腕の振りの手本**（キャラのデザインは写さない）

```
Image 1 is a POSE reference only: a 4x2 sheet of a classic beat-'em-up walk (idle + 6 walking frames).
Image 2 is the exact character design reference for the character to draw (an enemy from a pixel-art beat-'em-up):
<その敵の見た目を、デザイン見本を見て具体的に書く。服・頭部・手・靴・色>
Image 3 is a finished example of this same task for a different character: copy its layout, stride widths and arm swing, NOT its character design.
Keep the proportions, pixel-art style and palette of Image 2. Do NOT copy the clothes, hair, face or colors of Image 1 or Image 3.

Create a pixel-art sprite sheet with EXACTLY the same layout as Image 1: 4 columns x 2 rows, 8 cells of identical size.
In every cell draw the Image 2 character in EXACTLY the same leg and arm positions as the same cell of Image 1
(same stride width, same which-leg-is-forward, same arm position), in a 3/4 front view facing RIGHT like the large pose in Image 2.
Same scale in every cell, feet on the same ground line near the bottom of the cell.
Crisp 1-pixel dark outline, limited palette matching Image 2.
Background: solid flat pure green #00FF00 in every cell. No shadow, no floor, no text, no numbers, no grid lines.

Cell 1: the idle stance exactly as the large pose in Image 2.
Cells 2-7: a calm walk, upper body upright and steady, arms swinging opposite to the legs:
 2. wide stride, NEAR leg forward, near arm back
 3. legs closing, medium stride
 4. legs together, passing
 5. wide stride, FAR leg forward, NEAR leg back, near arm forward
 6. legs closing, medium stride
 7. legs together, passing
Cell 8: empty (only green).
```

注意: 服に緑が含まれる敵はいないが、Bajioh の黒いコートや DICE の黒スーツは輪郭が背景に溶けやすいので、輪郭線を必ず入れさせる。
主人公のときは、2コマ目と5コマ目の腕・足が同じになる失敗が2回続き、3回目に**画面上の位置と重なり方**で指示して成功した
（例: 「5コマ目は、手前の腕が体の左側からお腹の前を横切って右へ出る」「手前の足は左へ伸び、奥の足に重なって全部見える」）。最初からこの言い方を足してよい。

整形: `python3 tools/sprite_pipeline.py build sprites/generated/<敵>_walk_dd_vN.png --grid 4x2 --frames 7 --name <敵>_walk_dd_vN --anchor hip <表の追加オプション>`

合格条件（`_check.png`・ポーズ見本・デザイン見本を並べて判定）:
- 2〜7コマ目の足の開き具合が「大股→中→そろう→大股→中→そろう」
- 2コマ目と5コマ目で前に出ている足が逆、腕の振りも逆
- **デザイン見本と同じキャラに見える**（頭部・服・色・体格）。1コマ目の立ち姿がデザイン見本の立ち姿と同じ
- 上半身の傾き・高さがコマごとに大きく変わらない／右向き3/4ビュー／体が欠けていない・緑が残っていない

報告: 合否とコマごとの問題点、最終プロンプト、作ったファイルのパス。`index.html` の組み込みと git 操作は Claude Code が行う。

## 第2弾: やられ〜ダウン〜起き上がり（全キャラ）・enemyC の軽業・enemyA/B の歩きの直し（2026-10-13 追加）

オーナーの評価: 歩きの作り直しは合格。追加の依頼は次の3つ。どれも「ビリーの絵をポーズ見本にして描き直す」同じ方法で作る。

共通の決まり（歩きのときと同じ）:
- 組み込みの `image_gen` を使う。生成は**1キャラ1モーションにつき最大3回**。保存先は `sprites/generated/`、整形は `tools/sprite_pipeline.py build`。
- 背景は純緑 #00FF00、影・地面・文字・枠線なし。全コマ同じ縮尺。右向き・斜め前（3/4ビュー）。1ピクセルの暗い輪郭線。
- 判定は `_check.png`・ポーズ見本・デザイン見本を `view_image` で並べて見る。
- 2回目以降は、うまくいかなかった点を**画面上の位置と重なり方**で具体的に指示し直す。
- `index.html` には触れない。git 操作はしない（Claude Code が行う）。

キャラごとの値（デザイン見本と build の追加オプション。今ゲームに入っている立ちコマと同じ大きさ・位置に揃えるための値）:

| キャラ | 出力名の頭 | デザイン見本 | build の追加オプション | 体格のメモ |
|---|---|---|---|---|
| 主人公 | `Dharuriser` | `sprites/reference/Dharuriser_design_sheet.png` と `sprites/generated/walk_dd_v3.png` | `--ref-height 236 --anchor-x 168 --baseline 299` | 大人のヒーロー体型 |
| enemyA | `enemyA` | `sprites/reference/enemyA_design_ref.png` | `--ref-height 240 --anchor-x 165 --baseline 299` | **ずんぐり・横幅が広い・前かがみ・太い腕**（力自慢） |
| enemyB | `enemyB` | `sprites/reference/enemyB_design_ref.png` | `--ref-height 248 --anchor-x 177 --baseline 298` | **細身・長身・肩幅が狭い・背筋が伸びている** |
| enemyC | `enemyC` | `sprites/reference/enemyC_design_ref.png` | `--ref-height 184 --anchor-x 208 --baseline 299` | 小柄。**立ち姿が低いしゃがみ構え**（身長の値はしゃがんだ高さ） |
| DICE | `DICE` | `sprites/reference/DICE_design_ref.png` | `--ref-height 246 --anchor-x 185 --baseline 299` | 細身の紳士 |
| Bajioh | `Bajioh` | `sprites/reference/Bajioh_design_ref.png` | `--ref-height 237 --anchor-x 170 --baseline 299` | コート姿・腕に円形の装置 |

### 2-1. やられ〜ダウン〜起き上がり（6キャラ全部）— 出力 `<頭>_damage_dd_vN`

参考画像: 1) `sprites/reference/DD_Billy_damage_pose_ref.png`（**ポーズ見本**, 3列×3行） 2) そのキャラのデザイン見本
3) `sprites/generated/walk_dd_v3.png`（主人公の合格例。絵柄の細かさ・縮尺の手本。キャラのデザインは写さない）

```
Image 1 is a POSE reference only: a 3x3 sheet of a classic beat-'em-up knock-down sequence.
Image 2 is the exact character design reference for the character to draw: <見た目と体格を具体的に書く>
Image 3 only shows the target pixel-art finish and scale; do NOT copy its character.
Keep the proportions, body type, pixel-art style and palette of Image 2. Do NOT copy the clothes, hair, face or colors of Image 1.

Create a pixel-art sprite sheet with EXACTLY the same layout as Image 1: 3 columns x 3 rows, 9 cells of identical size.
In every cell draw the Image 2 character in the same pose as the same cell of Image 1.
The character faces RIGHT (3/4 front view in the standing cells) and is knocked BACKWARD to the LEFT: when lying down, the head is on the LEFT and the feet on the RIGHT.
Same scale in every cell. Standing/lying cells touch the same ground line near the bottom of the cell; airborne cells float clearly above it.
Crisp 1-pixel dark outline, limited palette matching Image 2. Background: solid flat pure green #00FF00. No shadow, no floor, no text, no grid lines.

Cells in reading order:
1. the idle stance exactly as the large pose in Image 2
2. HIT: just punched, upper body recoils and doubles over, head snapped, feet still on the ground
3. AIRBORNE: thrown backward, feet off the ground, body tilted about 45 degrees, head up-left, legs trailing down-right
4. AIRBORNE: falling flat on the back, body horizontal in the air, head on the left, face up, legs slightly raised
5. LYING: flat on the back on the ground, head left, feet right, arms limp
6. STARTING TO RISE: still on the back, knees pulled up, head and shoulders lifting
7. SITTING UP: sitting on the ground, one hand on the floor, upper body upright
8. ONE KNEE: crouching on one knee, about to stand
9. the idle stance again (same as cell 1)
```

整形: `python3 tools/sprite_pipeline.py build sprites/generated/<頭>_damage_dd_vN.png --grid 3x3 --name <頭>_damage_dd_vN --anchor first --air 2,3 <表の追加オプション>`
（`--anchor first`: 1コマ目に合わせた同じずらし量を全コマに使う。`--air 2,3`: 3・4コマ目は空中なので足元を地面に揃えない）

合格条件:
- 9コマが上の順番どおりの姿勢で、流れがつながっている（のけぞる→浮く→背中から落ちる→仰向け→起き始め→座る→片ひざ→立つ）
- 倒れたとき**頭が左・足が右**。3・4コマ目は地面から浮いている。5〜8コマ目は地面に付いている
- デザイン見本と同じキャラ・同じ体格に見える。体が欠けていない（整形後 400x300 のコマからはみ出していない）・緑が残っていない

### 2-2. enemyC の軽業（移動）— 出力 `enemyC_walk_dd_vN`

今の enemyC の移動は「しゃがみ→飛び込み→逆立ち→着地」の6コマを往復再生していて、間のコマが足りず軽業に見えない。
前方の手つき回転（ハンドスプリング）を8コマで作る。

参考画像: 1) `sprites/reference/DD_Billy_acrobat_pose_ref.png`（**ポーズ見本**, 3列×3行。1・2・8コマ目は enemyC の今の絵、3〜7コマ目がビリーの回転）
2) `sprites/reference/enemyC_design_ref.png` 3) `sprites/generated/walk_dd_v3.png`（仕上がりの手本）

```
(最初の2段落は 2-1 と同じ。レイアウトは 3 columns x 3 rows, 9 cells, 最後の1コマは空)
The character faces RIGHT and travels to the RIGHT doing a forward handspring. Every cell touches the same ground line with feet or hands, except cell 7.

Cells in reading order:
1. the low crouching idle stance exactly as the large pose in Image 2
2. LUNGE: pushes off and lunges forward, body low and stretched, arms reaching forward
3. DIVE: hands planted on the ground, head down near the hands, hips high, legs kicking up behind (body about 45 degrees)
4. KICK-UP: on the hands, legs swinging up past 45 degrees, body almost vertical upside-down
5. HANDSTAND: vertical handstand, legs straight up, cloak hanging down toward the ground
6. ARCH-OVER: legs have passed over, feet touching down on the RIGHT, back arched like a bridge, head and arms trailing on the left, hands just leaving the ground
7. SNAP-UP: airborne just above the ground, body curling upright, knees tucked, facing right
8. LANDING: deep crouch on the ground, facing right, cloak settling
9. empty (only green)
The hooded purple cloak must follow gravity and the motion in every cell (it hangs down toward the ground when upside-down).
```

整形: `python3 tools/sprite_pipeline.py build sprites/generated/enemyC_walk_dd_vN.png --grid 3x3 --frames 8 --name enemyC_walk_dd_vN --anchor center --ref-height 184 --anchor-x 208 --baseline 299`

合格条件: 2〜8コマ目が1回転として順番につながる（体の角度が毎コマ少しずつ進む）／5コマ目が逆立ち／フードとマントが全コマで enemyC／小柄な体格のまま。

### 2-3. enemyA・enemyB の歩きの直し — 出力 `enemyA_walk_dd_vN`（v3 から）、`enemyB_walk_dd_vN`（v3 から）

作り直した歩き（v2）は動きは合格だが、**2体の体格差が小さくなってしまった**（A が細く・背筋が伸び、B が太くなった）。
元の絵は「A＝ずんぐり・横幅が広い・前かがみ」「B＝細身・長身」。動きはそのまま、体格だけ元に戻す。

手順は「敵の歩きの作り直し」と同じ（ポーズ見本 `DD_Billy_walk_pose_ref.png`、4列×2行、`--grid 4x2 --frames 7 --anchor hip` ＋表の追加オプション）。違いは次の3点。
- 参考画像の3枚目は、**そのキャラの前回の合格版**（`sprites/generated/enemyA_walk_dd_v2.png` / `enemyB_walk_dd_v2.png`）。「この動きのまま、体格を Image 2 に合わせて直す」と指示する。
- プロンプトに体格をはっきり書く。
  enemyA: `a short-necked, very broad and heavy bruiser: wide shoulders, thick arms, barrel chest, hunched forward posture; the poncho is wide and bulky`
  enemyB: `a tall, lean, narrow-shouldered man standing upright; long thin legs, slim arms; the poncho hangs narrow and close to the body`
- 整形後に体格を数値で確かめる: `python3 tools/sprite_pipeline.py measure sprites/build/<出力名>.png --first 1 --last 6`
  合格の目安 … **enemyA: 胴の幅の平均が 140px 以上** ／ **enemyB: 胴の幅の平均が 95px 以下**（元の絵: A の立ち 176px・B の立ち 116px、B の歩き 85px。前回 v2: A 127px・B 107px）

合格条件: 上の数値 ＋ 前回と同じ歩きの条件（大股→中→そろう×2、2コマ目と5コマ目で足・腕が逆）。
1コマ目（立ち）は Claude Code が元の絵に差し替えるので、少し違っていてもよい。

## 第3弾以降

第2弾までと同じ方法（ビリーの絵をポーズ見本にする）で、`docs/sprite-spec.md` の表の順に進める。次はパンチ（`--grid 3x2 --frames 6 --anchor first`）。
