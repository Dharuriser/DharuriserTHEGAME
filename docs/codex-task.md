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

## 第2弾以降（第1弾が合格してから）

同じ手順で、`docs/sprite-spec.md` の表の順に進める。

1. 被弾〜ダウン〜起き上がり（`--grid 3x3 --anchor first --air 2,3`、出力名 `Dharuriser_damage_v1`）
2. パンチ（`--grid 3x2 --frames 6 --anchor first`、出力名 `Dharuriser_punch_v1`）

プロンプトは `docs/sprite-spec.md` の「プロンプトの例」の最初の2段落をそのまま使い、「Cells in reading order」以降を表の内容に差し替える。
